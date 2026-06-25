#!/usr/bin/env python3
"""
Acki Nacki Telegram Wallet Bot
Fetches wallet data from https://mainnet.ackinacki.org/graphql
"""

import asyncio
import httpx
import json
import base64
import struct
import re
import logging
from typing import Optional

# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ─── Constants ─────────────────────────────────────────────────────────────────
GRAPHQL = "https://mainnet.ackinacki.org/graphql"
API_BASE = "https://acki.live"

# Code hashes for contract type detection (from chunk-VZWIGR4W.js)
CODE_HASH_TYPES = {
    "6cc8128da9cda444e4ad83fc7064ea51c6a0bbf0e2aa4777d0807e8ed7283cdb": "MvMultifactor",
    "18e57fc187e8ac1cc2a9b1e8907e291cd925c840c1f93d2f30fe12747dd90126": "PopitGame",
    "f5580a523a708377e8fadc17265def99bed081988d9b9f37e153b938390e3245": "Indexer",
}

# PopitGame code (for address derivation) - init code hash
POPIT_INIT_HASH = "18e57fc187e8ac1cc2a9b1e8907e291cd925c840c1f93d2f30fe12747dd90126"

# ─── GraphQL helpers ────────────────────────────────────────────────────────────

async def gql(client: httpx.AsyncClient, query: str, variables: dict) -> dict:
    """Execute a GraphQL query against the Acki Nacki endpoint."""
    resp = await client.post(
        GRAPHQL,
        content=json.dumps({"query": query, "variables": variables}),
        headers={"Content-Type": "text/plain"},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise ValueError(data["errors"][0]["message"])
    return data.get("data", {})


def normalize_address(addr: str) -> str:
    """Normalize address to lowercase, strip workchain prefix for account_id."""
    addr = addr.strip()
    # Extract just the hex part (after the colon)
    m = re.match(r'^(-?\d+):([a-fA-F0-9]{64})$', addr)
    if m:
        return m.group(2).lower()
    return addr.lower()


# ─── Step 1: Resolve wallet name → MvMultifactor address ───────────────────────

async def resolve_name_to_address(client: httpx.AsyncClient, name: str) -> Optional[str]:
    """
    The explorer resolves a wallet name by calling the Indexer contract's
    getIndexerAddressByName which derives an address from the name.
    We replicate by calling the acki.live API endpoint.
    """
    # The explorer uses TVM SDK to compute: encode_message with Indexer ABI +
    # initial_data={_pubkey:"0x0", _name: name.toLowerCase()}
    # We call the acki.live API to resolve (it exposes a REST-like endpoint)
    try:
        resp = await client.get(
            f"{API_BASE}/api/account/by-name/{name.strip().lower()}",
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("address") or data.get("id")
    except Exception:
        pass

    # Fallback: query GraphQL for indexer data by searching for the name
    # The indexer address IS the GraphQL account_id for the indexer contract
    # We query with account_id = name (the explorer normalises it)
    query = """
    query GetIndexerData($accountId: String!, $dappId: String!) {
      blockchain {
        account(account_id: $accountId, dapp_id: $dappId) {
          info {
            data
          }
        }
      }
    }
    """
    name_lower = name.strip().lower()
    try:
        data = await gql(client, query, {"accountId": name_lower, "dappId": name_lower})
        # If this returns data, the name itself IS a valid account_id (hash form)
        if data.get("blockchain", {}).get("account", {}).get("info"):
            return name_lower
    except Exception:
        pass

    return None


async def resolve_account(client: httpx.AsyncClient, identifier: str) -> Optional[str]:
    """
    Resolve a wallet name or address to a full 0:hex address.
    Returns the account_id (hex without workchain prefix).
    """
    identifier = identifier.strip()

    # Already a hex address?
    m = re.match(r'^(-?\d+):([a-fA-F0-9]{64})$', identifier)
    if m:
        return m.group(2).lower()

    # Pure 64-char hex?
    if re.match(r'^[a-fA-F0-9]{64}$', identifier):
        return identifier.lower()

    # It's a name — query the Indexer contract
    # The explorer uses TVM SDK to derive the Indexer address from the name.
    # We query the GraphQL with account_id = indexer_hash_derived_from_name.
    # Since we don't have TVM SDK in Python, we query with a special API call.
    return await resolve_name_via_graphql(client, identifier)


async def resolve_name_via_graphql(client: httpx.AsyncClient, name: str) -> Optional[str]:
    """
    The acki.live frontend resolves names by:
    1. Computing Indexer contract address from name using TVM SDK
    2. Querying that indexer to get the MvMultifactor wallet address

    We replicate by querying the code schema API + using known Indexer code hash.
    As a simpler approach: search transactions/accounts by name metadata.
    """
    # Direct GraphQL search — account name is stored as _name in Indexer contract data
    # The explorer searches by encoding the address from the name
    # Without TVM SDK we query account info endpoint
    query = """
    query GetAccountByName($accountId: String!, $dappId: String!) {
      blockchain {
        account(account_id: $accountId, dapp_id: $dappId) {
          info {
            data
            code_hash
          }
        }
      }
    }
    """
    name_lower = name.strip().lower()
    try:
        data = await gql(client, query, {"accountId": name_lower, "dappId": name_lower})
        info = data.get("blockchain", {}).get("account", {}).get("info")
        if info and info.get("code_hash"):
            return name_lower
    except Exception:
        pass
    return None


# ─── Step 2: Get account full info ─────────────────────────────────────────────

ACCOUNT_INFO_QUERY = """
query GetAccountInfo($accountId: String!, $dappId: String!) {
  blockchain {
    account(account_id: $accountId, dapp_id: $dappId) {
      info {
        balance(format: DEC)
        balance_other {
          currency
          value(format: DEC)
        }
        acc_type
        acc_type_name
        last_paid
        code_hash
        init_code_hash
        last_trans_lt(format: DEC)
        boc
        data
        dapp_id
      }
    }
  }
}
"""

ACCOUNT_BOC_QUERY = """
query GetAccountBocDapp($accountId: String!, $dappId: String!) {
  blockchain {
    account(account_id: $accountId, dapp_id: $dappId) {
      info {
        boc
        dapp_id
      }
    }
  }
}
"""


async def get_account_info(client: httpx.AsyncClient, account_id: str) -> Optional[dict]:
    """Fetch full account info from GraphQL."""
    try:
        data = await gql(client, ACCOUNT_INFO_QUERY, {
            "accountId": account_id,
            "dappId": account_id,
        })
        return data.get("blockchain", {}).get("account", {}).get("info")
    except Exception as e:
        log.warning(f"get_account_info failed for {account_id}: {e}")
        return None


# ─── Step 3: Decode BOC data to get wallet name ─────────────────────────────────

def decode_name_from_boc_data(boc_data_b64: str) -> Optional[str]:
    """
    Extract _name string from base64-encoded BOC data field.
    The data field in BOC for an MvMultifactor / Indexer contract stores
    _name as a TVM cell. We do a simple heuristic extraction.
    
    The explorer uses @eversdk/core decodeAccountData for proper TVM decoding.
    We do a simplified extraction: look for printable ASCII strings in the raw bytes.
    """
    try:
        raw = base64.b64decode(boc_data_b64)
        # Find ASCII strings of length 3–32 (typical wallet names)
        strings = re.findall(rb'[\x20-\x7E]{3,32}', raw)
        for s in strings:
            decoded = s.decode('ascii', errors='ignore').strip()
            # Wallet names are typically alphanumeric, 3-20 chars
            if re.match(r'^[a-zA-Z][a-zA-Z0-9_-]{1,19}$', decoded):
                return decoded
    except Exception:
        pass
    return None


# ─── Step 4: Fetch indexer data and get MvMultifactor (wallet) address ──────────

INDEXER_QUERY = """
query GetIndexerData($accountId: String!, $dappId: String!) {
  blockchain {
    account(account_id: $accountId, dapp_id: $dappId) {
      info {
        data
        code_hash
      }
    }
  }
}
"""


async def get_mv_from_indexer(client: httpx.AsyncClient, indexer_id: str) -> Optional[str]:
    """Get MvMultifactor wallet address from Indexer contract data."""
    try:
        data = await gql(client, INDEXER_QUERY, {
            "accountId": indexer_id,
            "dappId": indexer_id,
        })
        info = data.get("blockchain", {}).get("account", {}).get("info")
        if not info or not info.get("data"):
            return None
        # _wallet is stored at a known position; do simple extraction
        raw = base64.b64decode(info["data"])
        # Look for 64-char hex pattern or address-like patterns
        # In TVM cell encoding, addresses are stored as bit strings
        # Simple heuristic: the data field contains _wallet address bytes
        return extract_address_from_cell(raw)
    except Exception as e:
        log.warning(f"get_mv_from_indexer failed: {e}")
        return None


def extract_address_from_cell(raw: bytes) -> Optional[str]:
    """
    Simple heuristic to extract an address from a TVM cell.
    A TVM std address is 267 bits: 2 bits type + 1 bit anycast + 8 bits workchain + 256 bits address.
    """
    # Look for 32-byte sequences that look like valid addresses (not all zeros)
    for i in range(len(raw) - 32):
        chunk = raw[i:i+32]
        hex_str = chunk.hex()
        if hex_str not in ('0' * 64, 'f' * 64) and sum(chunk) > 0:
            return hex_str
    return None


# ─── Step 5: Get PopitGame address (derived from MvMultifactor address) ─────────

async def get_popit_game_address(client: httpx.AsyncClient, mv_address: str) -> Optional[str]:
    """
    The PopitGame address is derived from the MvMultifactor (owner) address
    via TVM SDK encode_message. We query the acki.live code schema API.
    Since we can't run TVM SDK, we try the code schema API to find it.
    """
    # Try: query GraphQL for accounts whose dapp_id matches and type is PopitGame
    query = """
    query GetPopitGame($accountId: String!, $dappId: String!) {
      blockchain {
        account(account_id: $accountId, dapp_id: $dappId) {
          info {
            code_hash
            data
            balance(format: DEC)
            balance_other {
              currency
              value(format: DEC)
            }
          }
        }
      }
    }
    """
    # PopitGame address is computed as: encode_message(PopitGameABI, code=UN, initial_data={_pubkey:0, _owner: mv_address})
    # We can't compute this without TVM SDK. Instead, query by dapp_id pattern.
    # The dapp_id for PopitGame would be the MvMultifactor address.
    try:
        data = await gql(client, query, {
            "accountId": mv_address,
            "dappId": mv_address,
        })
        info = data.get("blockchain", {}).get("account", {}).get("info")
        if info and info.get("code_hash") == POPIT_INIT_HASH:
            return mv_address
    except Exception:
        pass
    return None


# ─── Step 6: Parse balances ─────────────────────────────────────────────────────

# Currency IDs from the blockchain (from observed responses)
# NACKL = currency ID 1 (from chunk-VZWIGR4W: mainCurrencyName = map.get(1)?.name || "SHELL")
KNOWN_CURRENCIES = {
    # These are populated from CurrencyCollection contract
    # Defaults based on what's shown in the explorer
    0: {"name": "SHELL", "decimals": 9},
    1: {"name": "NACKL", "decimals": 9},
}


def format_balance(value_str: str, decimals: int = 9, display_decimals: int = 2) -> str:
    """Format a raw integer balance string to human-readable."""
    if not value_str or value_str == "0":
        return "0"
    try:
        raw = int(value_str)
        divisor = 10 ** decimals
        whole = raw // divisor
        frac = raw % divisor
        frac_str = str(frac).zfill(decimals)[:display_decimals]
        result = f"{whole:,}.{frac_str}"
        return result
    except (ValueError, TypeError):
        return "0"


async def get_currency_map(client: httpx.AsyncClient) -> dict:
    """
    Fetch the currency collection to get NACKL/SHELL/USDC currency IDs and decimals.
    This queries the CurrencyCollectionConfig contract.
    """
    query = """
    query GetCurrencyCollection($accountId: String!, $dappId: String!) {
      blockchain {
        account(account_id: $accountId, dapp_id: $dappId) {
          info {
            data
            code_hash
            init_code_hash
          }
        }
      }
    }
    """
    # CurrencyCollectionConfig address = 0:8888...8888
    CURRENCY_CONFIG = "8" * 64
    try:
        data = await gql(client, query, {
            "accountId": CURRENCY_CONFIG,
            "dappId": CURRENCY_CONFIG,
        })
        # Even if we can't decode the BOC, return defaults
    except Exception:
        pass
    return KNOWN_CURRENCIES


# ─── Step 7: Get transactions for speed calculation ─────────────────────────────

TRANSACTIONS_QUERY = """
query GetAccountTransactions($accountId: String!, $dappId: String!, $limit: Int!) {
  blockchain {
    account(account_id: $accountId, dapp_id: $dappId) {
      transactions(
        last: $limit
        allow_latest_inconsistent_data: true
      ) {
        nodes {
          id
          now
          balance_delta(format: DEC)
          balance_delta_other {
            currency
            value(format: DEC)
          }
          tr_type_name
          in_message {
            src
            msg_type_name
            value_other {
              currency
              value(format: DEC)
            }
          }
        }
      }
    }
  }
}
"""


async def get_recent_transactions(
    client: httpx.AsyncClient,
    account_id: str,
    limit: int = 50,
) -> list:
    """Fetch recent transactions for an account."""
    try:
        data = await gql(client, TRANSACTIONS_QUERY, {
            "accountId": account_id,
            "dappId": account_id,
            "limit": limit,
        })
        nodes = (
            data.get("blockchain", {})
            .get("account", {})
            .get("transactions", {})
            .get("nodes", [])
        )
        return nodes or []
    except Exception as e:
        log.warning(f"get_recent_transactions failed: {e}")
        return []


def calculate_speed_nackl_per_24h(transactions: list, nackl_currency_id: int = 1) -> float:
    """
    Calculate NACKL earning speed based on recent reward transactions.
    Speed = total NACKL received in the last N hours / N * 24
    """
    now_ts = None
    nackl_rewards = []

    for tx in transactions:
        ts = tx.get("now", 0)
        if ts:
            now_ts = max(now_ts or ts, ts)

    if not now_ts:
        return 0.0

    # Look at last 24 hours
    cutoff = now_ts - 86400

    for tx in transactions:
        ts = tx.get("now", 0)
        if ts < cutoff:
            continue

        # Check balance_delta_other for NACKL rewards
        for other in tx.get("balance_delta_other") or []:
            if other.get("currency") == nackl_currency_id:
                val_str = other.get("value", "0")
                try:
                    val = int(val_str)
                    if val > 0:
                        nackl_rewards.append(val)
                except (ValueError, TypeError):
                    pass

    if not nackl_rewards:
        return 0.0

    total_nackl = sum(nackl_rewards)
    # These are the rewards in the window; extrapolate to 24h
    window_hours = (now_ts - cutoff) / 3600
    if window_hours < 0.1:
        window_hours = 1.0

    per_24h = (total_nackl / (10 ** 9)) * (24 / window_hours)
    return per_24h


def count_total_taps(transactions: list) -> int:
    """Count reward transactions (each is a 'tap' in the mining context)."""
    return sum(
        1 for tx in transactions
        if any(
            (other.get("value") or "0") != "0" and int(other.get("value", "0")) > 0
            for other in (tx.get("balance_delta_other") or [])
        )
    )


# ─── Main wallet lookup ─────────────────────────────────────────────────────────

class WalletInfo:
    def __init__(self):
        self.name: Optional[str] = None
        self.address: str = ""
        self.nackl_balance: float = 0.0
        self.nackl_locked: float = 0.0
        self.usdc_balance: float = 0.0
        self.shell_balance: float = 0.0
        self.speed_nackl_24h: float = 0.0
        self.total_taps: int = 0
        self.mbi_level: int = 0
        self.last_transaction: Optional[str] = None
        self.last_paid: Optional[str] = None
        self.popit_address: Optional[str] = None


async def lookup_wallet(name_or_address: str) -> WalletInfo:
    """
    Main function: given a wallet name or address, return all wallet data.
    
    Flow (mirrors the acki.live explorer):
    1. Resolve name → MvMultifactor address (via Indexer contract)
    2. Fetch MvMultifactor account info (BOC, balances)
    3. Derive PopitGame address from MvMultifactor address
    4. Fetch PopitGame data (_mbiCur for MBI level, NACKL locked balance)
    5. Calculate speed from recent transactions
    """
    info = WalletInfo()

    async with httpx.AsyncClient(
        headers={
            "User-Agent": "Mozilla/5.0 AckiBot/1.0",
            "Origin": "https://acki.live",
            "Referer": "https://acki.live/",
        }
    ) as client:

        # ── Resolve identifier ─────────────────────────────────────────────────
        identifier = name_or_address.strip()
        account_id: Optional[str] = None
        wallet_name: Optional[str] = None

        # Check if it's a direct address
        m = re.match(r'^(-?\d+):([a-fA-F0-9]{64})$', identifier)
        if m:
            account_id = m.group(2).lower()
        elif re.match(r'^[a-fA-F0-9]{64}$', identifier):
            account_id = identifier.lower()
        else:
            # It's a name — use the Indexer to resolve
            wallet_name = identifier
            account_id = await resolve_name_via_indexer(client, identifier)
            if not account_id:
                raise ValueError(f"Could not find wallet '{identifier}'")

        info.address = f"0:{account_id}"
        info.name = wallet_name

        # ── Fetch main account (MvMultifactor) ────────────────────────────────
        acct = await get_account_info(client, account_id)
        if not acct:
            raise ValueError(f"Account not found: {info.address}")

        # Extract name from BOC data if not already known
        if not info.name and acct.get("data"):
            info.name = decode_name_from_boc_data(acct["data"])

        # ── Parse balances ─────────────────────────────────────────────────────
        # SHELL (native, id=0)
        shell_raw = acct.get("balance", "0") or "0"
        info.shell_balance = float(format_balance(shell_raw, 9, 6).replace(",", ""))

        # Other currencies (NACKL id=1, USDC, etc.)
        for bal in acct.get("balance_other") or []:
            cid = bal.get("currency", -1)
            val = bal.get("value", "0") or "0"
            if cid == 1:  # NACKL
                info.nackl_balance = float(format_balance(val, 9, 6).replace(",", ""))

        code_hash = acct.get("code_hash", "")
        init_code_hash = acct.get("init_code_hash", "")
        contract_type = CODE_HASH_TYPES.get(code_hash) or CODE_HASH_TYPES.get(init_code_hash)

        info.last_transaction = acct.get("last_trans_lt")
        info.last_paid = acct.get("last_paid")

        # ── Find PopitGame address ──────────────────────────────────────────────
        # PopitGame is a linked contract whose _owner = account_id
        # Its address is derived by TVM from: {_pubkey: 0, _owner: account_id}
        # We try to fetch it via the API
        popit_address = await find_popit_game(client, account_id, acct)

        if popit_address:
            info.popit_address = f"0:{popit_address}"
            popit_info = await get_account_info(client, popit_address)
            if popit_info:
                # Get NACKL locked balance from PopitGame
                for bal in popit_info.get("balance_other") or []:
                    if bal.get("currency") == 1:
                        val = bal.get("value", "0") or "0"
                        info.nackl_locked = float(format_balance(val, 9, 6).replace(",", ""))

                # MBI level from dataParsed._mbiCur
                # We can try to decode from the data field
                if popit_info.get("data"):
                    mbi = extract_mbi_from_data(popit_info["data"])
                    if mbi is not None:
                        info.mbi_level = mbi

        # ── Recent transactions for speed / taps ────────────────────────────────
        txns = await get_recent_transactions(client, account_id, limit=100)
        if txns:
            info.speed_nackl_24h = calculate_speed_nackl_per_24h(txns)
            info.total_taps = count_total_taps(txns)

    return info


async def resolve_name_via_indexer(client: httpx.AsyncClient, name: str) -> Optional[str]:
    """
    Resolve a wallet name to its MvMultifactor account_id.
    
    The explorer does:
    1. TVM SDK → compute Indexer address from name (encode_message with Indexer ABI)
    2. Query Indexer data → _wallet field = MvMultifactor address
    
    Since we don't have TVM SDK, we use the acki.live /api endpoint.
    """
    # Try acki.live API first (if it exists)
    endpoints = [
        f"{API_BASE}/api/resolve/{name.lower()}",
        f"{API_BASE}/api/account/{name.lower()}",
    ]
    for url in endpoints:
        try:
            r = await client.get(url, timeout=8)
            if r.status_code == 200:
                d = r.json()
                addr = d.get("address") or d.get("id") or d.get("accountId")
                if addr:
                    m = re.match(r'^(-?\d+):([a-fA-F0-9]{64})$', addr)
                    return m.group(2).lower() if m else addr.lower()
        except Exception:
            pass

    # The key insight from the source code:
    # getIndexerAddressByName() uses ABI.encode_message with Indexer ABI code
    # to derive a deterministic address from the name.
    # Without TVM SDK we can't replicate this in pure Python.
    # 
    # However, the response.txt shows the actual curl request format:
    # POST /graphql with query GetIndexerData and variables:
    #   accountId = "a432f6f5..." (the Indexer address)
    #   dappId = "a432f6f5..."
    #
    # The Indexer address for a name is NOT the name itself—it's derived.
    # We fall back to: try the name directly as an account identifier.
    
    query = """
    query GetAccountBocDapp($accountId: String!, $dappId: String!) {
      blockchain {
        account(account_id: $accountId, dapp_id: $dappId) {
          info {
            boc
            dapp_id
            code_hash
          }
        }
      }
    }
    """
    name_lower = name.strip().lower()
    try:
        data = await gql(client, query, {"accountId": name_lower, "dappId": name_lower})
        info = data.get("blockchain", {}).get("account", {}).get("info")
        if info and info.get("code_hash"):
            return name_lower
    except Exception:
        pass

    return None


async def find_popit_game(
    client: httpx.AsyncClient,
    mv_address: str,
    mv_info: dict,
) -> Optional[str]:
    """
    Find the PopitGame contract address for a given MvMultifactor address.
    
    From the source: getPopitGameAddress uses TVM ABI encode_message with
    PopitGame ABI + initial_data={_pubkey:0, _owner: mv_address}
    
    We try the dapp_id field (which links contracts together).
    """
    dapp_id = mv_info.get("dapp_id")
    if dapp_id:
        # Try querying with dapp_id as both accountId and dappId
        # PopitGame and MvMultifactor share the same dapp_id
        query = """
        query FindPopitGame($accountId: String!, $dappId: String!) {
          blockchain {
            account(account_id: $accountId, dapp_id: $dappId) {
              info {
                code_hash
                balance_other { currency value(format: DEC) }
                data
              }
            }
          }
        }
        """
        # Clean up dapp_id
        dapp_clean = dapp_id.strip().lower()
        m = re.match(r'^(-?\d+):([a-fA-F0-9]{64})$', dapp_clean)
        dapp_hex = m.group(2) if m else dapp_clean

        # From the response.txt, the Indexer data query uses:
        # accountId = "a432f6f5..." (Indexer address)
        # dappId = "a432f6f5..."   (same)
        # The POPIT GAME is linked via the dapp_id shown in the account details screen
        
        # From screenshot: POPIT GAME 0:ae78b6bb...add4618509
        # This is a different address from the MvMultifactor address
        # It's stored in the Indexer's linkedAccounts under type "Popit Game"
        
        # Try: the popit game address is the dapp_id of the MvMultifactor
        try:
            data = await gql(client, query, {"accountId": dapp_hex, "dappId": dapp_hex})
            info = data.get("blockchain", {}).get("account", {}).get("info")
            if info:
                code_hash = info.get("code_hash", "")
                if CODE_HASH_TYPES.get(code_hash) == "PopitGame":
                    return dapp_hex
        except Exception:
            pass

    return None


def extract_mbi_from_data(data_b64: str) -> Optional[int]:
    """
    Extract _mbiCur (MBI level) from PopitGame contract data (base64 BOC).
    _mbiCur is a uint64. We look for small integer values in the expected range.
    """
    try:
        raw = base64.b64decode(data_b64)
        # In TVM cell serialization, uint64 values are stored as big-endian 8 bytes
        # We look for uint64 values in range 1-500 (reasonable MBI level range)
        for i in range(len(raw) - 8):
            val = struct.unpack(">Q", raw[i:i+8])[0]
            if 1 <= val <= 500:
                return int(val)
    except Exception:
        pass
    return None


# ─── Format output ──────────────────────────────────────────────────────────────

def format_wallet_message(info: WalletInfo) -> str:
    """Format wallet info as a Telegram message."""
    name = info.name or "Unknown"
    lines = [
        "📊 *Wallet Info*",
        "",
        f"👤 {name}",
        f"🪙 NACKL: `{info.nackl_balance:,.2f}`",
        f"🔒 Locked: `{info.nackl_locked:,.2f}`",
        f"💵 USDC: `{info.usdc_balance:,.2f}`",
        f"🐚 SHELL: `{info.shell_balance:,.4f}`",
        f"⚡ Speed: `{info.speed_nackl_24h:,.2f} NACKL/24h`",
        f"👆 Total taps: `{info.total_taps}`",
        f"🎮 MBI Level: `{info.mbi_level}`",
    ]
    if info.address:
        lines.append(f"\n📍 `{info.address}`")
    return "\n".join(lines)


# ─── Telegram Bot ───────────────────────────────────────────────────────────────

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    from telegram.constants import ParseMode
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("python-telegram-bot not installed. Install with: pip install python-telegram-bot")


async def cmd_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /wallet <name_or_address> command."""
    args = context.args
    if not args:
        await update.message.reply_text(
            "Usage: `/wallet <name_or_address>`\n"
            "Example: `/wallet raghul`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    identifier = " ".join(args).strip()
    msg = await update.message.reply_text(f"🔍 Looking up `{identifier}`…", parse_mode=ParseMode.MARKDOWN)

    try:
        info = await lookup_wallet(identifier)
        text = format_wallet_message(info)
        await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    except ValueError as e:
        await msg.edit_text(f"❌ {e}")
    except Exception as e:
        log.exception("Wallet lookup failed")
        await msg.edit_text(f"❌ Error fetching wallet data: {e}")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Acki Nacki Wallet Bot*\n\n"
        "Commands:\n"
        "`/wallet <name_or_address>` — Look up a wallet\n\n"
        "Example: `/wallet raghul`",
        parse_mode=ParseMode.MARKDOWN,
    )


def run_bot(token: str):
    """Start the Telegram bot."""
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("wallet", cmd_wallet))
    app.add_handler(CommandHandler("w", cmd_wallet))  # shortcut
    print("Bot started. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


# ─── CLI test (no Telegram needed) ─────────────────────────────────────────────

async def test_lookup(name_or_address: str):
    """Test the lookup without Telegram."""
    print(f"Looking up: {name_or_address}")
    try:
        info = await lookup_wallet(name_or_address)
        print(format_wallet_message(info))
    except Exception as e:
        print(f"Error: {e}")
        import traceback; traceback.print_exc()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python acki_bot.py test <name_or_address>   # test lookup")
        print("  python acki_bot.py bot <TELEGRAM_TOKEN>     # run bot")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "test":
        query = sys.argv[2] if len(sys.argv) > 2 else "raghul"
        asyncio.run(test_lookup(query))

    elif mode == "bot":
        if len(sys.argv) < 3:
            print("Error: provide your Telegram bot token")
            print("  python acki_bot.py bot <TOKEN>")
            sys.exit(1)
        if not TELEGRAM_AVAILABLE:
            print("Install: pip install python-telegram-bot")
            sys.exit(1)
        run_bot(sys.argv[2])

    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
