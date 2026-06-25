#!/usr/bin/env python3
"""
Acki Nacki Wallet Bot — Telegram bot to look up NACKL wallet info.

Usage:
  python acki_bot.py bot <TOKEN>   # run the bot
  python acki_bot.py test <name>   # test lookup in terminal
"""

import asyncio
import base64
import json
import logging
import os
import re
import struct
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

import httpx

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
GRAPHQL   = "https://mainnet.ackinacki.org/graphql"
API_BASE  = "https://acki.live"

# Contract code hashes (from chunk-VZWIGR4W.js / chunk-F5RX2E5J.js)
HASH_MV_MULTIFACTOR = "6cc8128da9cda444e4ad83fc7064ea51c6a0bbf0e2aa4777d0807e8ed7283cdb"
HASH_POPIT_GAME     = "18e57fc187e8ac1cc2a9b1e8907e291cd925c840c1f93d2f30fe12747dd90126"
HASH_INDEXER        = "f5580a523a708377e8fadc17265def99bed081988d9b9f37e153b938390e3245"

# Known currency IDs on Acki Nacki
CURRENCY_NACKL = 1   # NACKL token
CURRENCY_USDC  = 2   # USDC (ECC)

# ── GraphQL helper ─────────────────────────────────────────────────────────────

HEADERS = {
    "Content-Type": "text/plain",   # MUST be text/plain, not application/json
    "Origin": "https://acki.live",
    "Referer": "https://acki.live/",
}

async def gql(client: httpx.AsyncClient, query: str, variables: dict) -> dict:
    """POST a GraphQL query; returns data dict or raises."""
    resp = await client.post(
        GRAPHQL,
        content=json.dumps({"query": query, "variables": variables}),
        headers=HEADERS,
        timeout=20,
    )
    resp.raise_for_status()
    body = resp.json()
    if "errors" in body:
        raise ValueError(body["errors"][0]["message"])
    return body.get("data", {})

# ── Address helpers ────────────────────────────────────────────────────────────

def is_address(s: str) -> bool:
    """Return True if s looks like a blockchain address (0:hex64 or bare hex64)."""
    s = s.strip()
    return bool(
        re.match(r'^-?\d+:[a-fA-F0-9]{64}$', s)
        or re.match(r'^[a-fA-F0-9]{64}$', s)
    )

def to_account_id(addr: str) -> str:
    """Strip workchain prefix; return bare 64-char hex."""
    addr = addr.strip()
    m = re.match(r'^-?\d+:([a-fA-F0-9]{64})$', addr)
    return m.group(1).lower() if m else addr.lower()

# ── GraphQL queries ────────────────────────────────────────────────────────────

# Full account info (balances + meta)
Q_ACCOUNT = """
query GetAccount($accountId: String!, $dappId: String!) {
  blockchain {
    account(account_id: $accountId, dapp_id: $dappId) {
      info {
        balance(format: DEC)
        balance_other { currency  value(format: DEC) }
        acc_type_name
        last_paid
        code_hash
        init_code_hash
        last_trans_lt(format: DEC)
        data
        dapp_id
      }
    }
  }
}
"""

# Indexer contract — contains _wallet (MvMultifactor address) in its data BOC
Q_INDEXER = """
query GetIndexerData($accountId: String!, $dappId: String!) {
  blockchain {
    account(account_id: $accountId, dapp_id: $dappId) {
      info { data  code_hash }
    }
  }
}
"""

# Transactions (for speed & tap count)
Q_TRANSACTIONS = """
query GetTransactions($accountId: String!, $dappId: String!, $limit: Int!) {
  blockchain {
    account(account_id: $accountId, dapp_id: $dappId) {
      transactions(last: $limit, allow_latest_inconsistent_data: true) {
        nodes {
          id
          now
          balance_delta_other { currency  value(format: DEC) }
        }
      }
    }
  }
}
"""

# ── Account fetch ──────────────────────────────────────────────────────────────

async def fetch_account(client: httpx.AsyncClient, account_id: str) -> Optional[dict]:
    """Return the info dict for an account_id, or None if not found."""
    try:
        data = await gql(client, Q_ACCOUNT, {
            "accountId": account_id,
            "dappId":    account_id,
        })
        return data.get("blockchain", {}).get("account", {}).get("info")
    except Exception as e:
        log.warning("fetch_account(%s) failed: %s", account_id, e)
        return None

# ── Name → address resolution ──────────────────────────────────────────────────
#
# How the explorer does it (from chunk-F5RX2E5J.js):
#   1. TVM SDK: encode_message(IndexerABI, initial_data={_pubkey:0, _name:name})
#      → deterministic Indexer contract address
#   2. Query that Indexer's data BOC → decode → _wallet field = MvMultifactor addr
#
# We replicate step 1 by calling the acki.live /api/indexer-address endpoint
# (which runs TVM on the server), then step 2 via GraphQL.
# If that API doesn't exist we fall back to querying the name directly as
# account_id — the GraphQL server also accepts names for some queries.

async def resolve_name(client: httpx.AsyncClient, name: str) -> Optional[str]:
    """
    Resolve a wallet name to its MvMultifactor account_id (64-char hex).
    Returns None if not found.
    """
    name_lower = name.strip().lower()

    # ── Strategy 1: acki.live REST API (if it exists) ──────────────────────
    for url in [
        f"{API_BASE}/api/resolve/{name_lower}",
        f"{API_BASE}/api/account/{name_lower}",
        f"{API_BASE}/api/wallet/{name_lower}",
    ]:
        try:
            r = await client.get(url, timeout=8, headers={"Origin": "https://acki.live"})
            if r.status_code == 200:
                d = r.json()
                addr = d.get("address") or d.get("id") or d.get("accountId")
                if addr:
                    return to_account_id(addr)
        except Exception:
            pass

    # ── Strategy 2: query name directly as account_id ──────────────────────
    # The GraphQL server resolves wallet names via the Indexer contract internally
    # when you pass the name as account_id.
    info = await fetch_account(client, name_lower)
    if info and info.get("code_hash"):
        return name_lower   # server accepted the name — return it as-is

    # ── Strategy 3: try the Indexer data approach via known dapp pattern ────
    # Query GetIndexerData with name as account_id — if the server resolves names
    # in that query context we'll get the _wallet inside the data BOC.
    try:
        data = await gql(client, Q_INDEXER, {
            "accountId": name_lower,
            "dappId":    name_lower,
        })
        info2 = data.get("blockchain", {}).get("account", {}).get("info")
        if info2 and info2.get("data"):
            wallet_addr = extract_wallet_from_indexer_boc(info2["data"])
            if wallet_addr:
                return wallet_addr
    except Exception:
        pass

    return None

# ── BOC data extraction ────────────────────────────────────────────────────────

def extract_wallet_from_indexer_boc(boc_b64: str) -> Optional[str]:
    """
    Extract the _wallet address from an Indexer contract data BOC.
    The Indexer stores: _name (string) and _wallet (address).
    We look for a 32-byte sequence that looks like a valid address.
    """
    try:
        raw = base64.b64decode(boc_b64)
        # TVM std address = 267 bits embedded in cell.
        # Heuristic: scan for 32-byte non-zero, non-all-F sequences.
        for i in range(len(raw) - 32):
            chunk = raw[i:i+32]
            h = chunk.hex()
            if h not in ("0" * 64, "f" * 64) and sum(chunk) > 100:
                return h
    except Exception:
        pass
    return None


def extract_mbi_from_boc(boc_b64: str) -> int:
    """
    Extract _mbiCur (MBI Level, uint64) from PopitGame contract data BOC.
    Looks for uint64 big-endian values in the range 1–1000.
    """
    try:
        raw = base64.b64decode(boc_b64)
        # Scan every 8-byte aligned position
        for i in range(0, len(raw) - 8, 1):
            val = struct.unpack(">Q", raw[i:i+8])[0]
            if 1 <= val <= 1000:
                return int(val)
    except Exception:
        pass
    return 0


def extract_name_from_boc(boc_b64: str) -> Optional[str]:
    """Extract _name string from MvMultifactor / Indexer contract data BOC."""
    try:
        raw = base64.b64decode(boc_b64)
        # Names are ASCII, 3–24 chars, alphanumeric + underscore/hyphen
        matches = re.findall(rb'[a-zA-Z][a-zA-Z0-9_\-]{2,23}', raw)
        for m in matches:
            decoded = m.decode("ascii")
            # Avoid obvious false positives
            if decoded.lower() not in ("none", "null", "true", "false", "data"):
                return decoded
    except Exception:
        pass
    return None

# ── Balance formatting ─────────────────────────────────────────────────────────

def fmt(raw: str, decimals: int = 9, show: int = 2) -> str:
    """Format a raw integer string to human-readable decimal."""
    if not raw or raw == "0":
        return "0.00"
    try:
        n = int(raw)
        whole = n // (10 ** decimals)
        frac  = n %  (10 ** decimals)
        frac_s = str(frac).zfill(decimals)[:show]
        return f"{whole:,}.{frac_s}"
    except (ValueError, TypeError):
        return "0.00"

# ── Transaction analysis ───────────────────────────────────────────────────────

async def fetch_transactions(client: httpx.AsyncClient, account_id: str, limit: int = 100) -> list:
    try:
        data = await gql(client, Q_TRANSACTIONS, {
            "accountId": account_id,
            "dappId":    account_id,
            "limit":     limit,
        })
        return (
            data.get("blockchain", {})
                .get("account", {})
                .get("transactions", {})
                .get("nodes", [])
        ) or []
    except Exception as e:
        log.warning("fetch_transactions failed: %s", e)
        return []


def calc_speed(txns: list) -> float:
    """NACKL earned per 24 hours based on recent transactions."""
    if not txns:
        return 0.0
    now_ts = max((t.get("now", 0) for t in txns), default=0)
    cutoff = now_ts - 86400
    earned = 0
    for tx in txns:
        if tx.get("now", 0) < cutoff:
            continue
        for d in tx.get("balance_delta_other") or []:
            if d.get("currency") == CURRENCY_NACKL:
                try:
                    v = int(d.get("value", "0"))
                    if v > 0:
                        earned += v
                except (ValueError, TypeError):
                    pass
    window_h = (now_ts - cutoff) / 3600 if now_ts > cutoff else 24
    return (earned / 1e9) * (24 / max(window_h, 0.1))


def calc_taps(txns: list) -> int:
    """Count reward transactions (each NACKL credit = one tap)."""
    count = 0
    for tx in txns:
        for d in tx.get("balance_delta_other") or []:
            if d.get("currency") == CURRENCY_NACKL:
                try:
                    if int(d.get("value", "0")) > 0:
                        count += 1
                        break
                except (ValueError, TypeError):
                    pass
    return count

# ── Main lookup ────────────────────────────────────────────────────────────────

async def lookup_wallet(identifier: str) -> dict:
    """
    Given a wallet name or address, return a dict with all wallet fields.
    Raises ValueError with a user-friendly message on failure.
    """
    identifier = identifier.strip()

    async with httpx.AsyncClient() as client:

        # ── 1. Resolve to account_id ───────────────────────────────────────
        if is_address(identifier):
            account_id = to_account_id(identifier)
        else:
            account_id = await resolve_name(client, identifier)
            if not account_id:
                raise ValueError(
                    f"Wallet *'{identifier}'* not found.\n\n"
                    f"Try using the full address instead:\n"
                    f"`/wallet 0:8c478bedb9...`"
                )

        # ── 2. Fetch MvMultifactor account ─────────────────────────────────
        info = await fetch_account(client, account_id)
        if not info:
            raise ValueError(f"Account `0:{account_id}` not found on chain.")

        code_hash = info.get("code_hash", "")
        dapp_id   = info.get("dapp_id", "")

        # Extract name from BOC if we only have an address
        wallet_name = identifier if not is_address(identifier) else None
        if not wallet_name and info.get("data"):
            wallet_name = extract_name_from_boc(info["data"])

        # ── 3. Parse balances ──────────────────────────────────────────────
        nackl_bal  = "0"
        usdc_bal   = "0"
        shell_bal  = info.get("balance", "0") or "0"

        for b in info.get("balance_other") or []:
            cid = b.get("currency", -1)
            val = b.get("value", "0") or "0"
            if cid == CURRENCY_NACKL:
                nackl_bal = val
            elif cid == CURRENCY_USDC:
                usdc_bal = val

        # ── 4. Find PopitGame contract ─────────────────────────────────────
        # PopitGame address == dapp_id of the MvMultifactor when set,
        # OR we try querying with the same account_id as dapp_id owner.
        nackl_locked = "0"
        mbi_level    = 0
        popit_id     = None

        # Try dapp_id as the popit address
        if dapp_id:
            dpid = to_account_id(dapp_id)
            if dpid != account_id:
                popit_id = dpid

        # If dapp_id == account_id (self), try known derivation patterns
        # (Without TVM SDK we can't compute the exact PopitGame address,
        #  but we try the Indexer dapp_id chain)
        if not popit_id:
            # Ask the indexer for the linked popit address via Indexer data
            try:
                idata = await gql(client, Q_INDEXER, {
                    "accountId": account_id,
                    "dappId":    account_id,
                })
                iinfo = idata.get("blockchain",{}).get("account",{}).get("info",{})
                if iinfo and iinfo.get("code_hash") == HASH_POPIT_GAME:
                    popit_id = account_id  # rare: queried account IS the popit
            except Exception:
                pass

        if popit_id:
            pinfo = await fetch_account(client, popit_id)
            if pinfo and pinfo.get("code_hash") == HASH_POPIT_GAME:
                for b in pinfo.get("balance_other") or []:
                    if b.get("currency") == CURRENCY_NACKL:
                        nackl_locked = b.get("value", "0") or "0"
                if pinfo.get("data"):
                    mbi_level = extract_mbi_from_boc(pinfo["data"])

        # ── 5. Recent transactions for speed + taps ────────────────────────
        txns  = await fetch_transactions(client, account_id)
        speed = calc_speed(txns)
        taps  = calc_taps(txns)

        return {
            "name":         wallet_name or "—",
            "address":      f"0:{account_id}",
            "nackl":        nackl_bal,
            "nackl_locked": nackl_locked,
            "usdc":         usdc_bal,
            "shell":        shell_bal,
            "speed":        speed,
            "taps":         taps,
            "mbi_level":    mbi_level,
        }

# ── Message formatter ──────────────────────────────────────────────────────────

def format_message(w: dict) -> str:
    return (
        "📊 *Wallet Info*\n\n"
        f"👤 {w['name']}\n"
        f"🪙 NACKL: `{fmt(w['nackl'])}`\n"
        f"🔒 Locked: `{fmt(w['nackl_locked'])}`\n"
        f"💵 USDC: `{fmt(w['usdc'])}`\n"
        f"🐚 SHELL: `{fmt(w['shell'], show=4)}`\n"
        f"⚡ Speed: `{w['speed']:,.2f} NACKL/24h`\n"
        f"👆 Total taps: `{w['taps']}`\n"
        f"🎮 MBI Level: `{w['mbi_level']}`\n\n"
        f"📍 `{w['address']}`"
    )

# ── Telegram bot ───────────────────────────────────────────────────────────────

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Acki Nacki Wallet Bot*\n\n"
        "Commands:\n"
        "`/wallet <name or address>` — look up any wallet\n\n"
        "Examples:\n"
        "`/wallet raghul`\n"
        "`/wallet 0:8c478bed...`",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_wallet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    args = ctx.args
    if not args:
        await update.message.reply_text(
            "Usage: `/wallet <name or address>`\nExample: `/wallet raghul`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    identifier = " ".join(args).strip()
    msg = await update.message.reply_text(
        f"🔍 Looking up `{identifier}`…", parse_mode=ParseMode.MARKDOWN
    )
    try:
        w    = await lookup_wallet(identifier)
        text = format_message(w)
        await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    except ValueError as e:
        await msg.edit_text(f"❌ {e}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        log.exception("Wallet lookup error")
        await msg.edit_text(f"❌ Error: {e}")


# ── HTTP health server (keeps Render Web Service alive) ───────────────────────

class _Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - Acki Bot running")
    def log_message(self, *a):
        pass   # silence nginx-style access log noise


def _start_health_server():
    port = int(os.environ.get("PORT", 8080))
    srv  = HTTPServer(("0.0.0.0", port), _Health)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    log.info("Health server on port %d", port)


# ── Entry point ────────────────────────────────────────────────────────────────

def run_bot(token: str):
    _start_health_server()
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("wallet", cmd_wallet))
    app.add_handler(CommandHandler("w",      cmd_wallet))
    log.info("Bot polling…")
    app.run_polling(drop_pending_updates=True)


async def _test(identifier: str):
    print(f"Looking up: {identifier}\n")
    try:
        w = await lookup_wallet(identifier)
        print(format_message(w).replace("*", "").replace("`", ""))
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        import traceback; traceback.print_exc()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage:\n  python acki_bot.py bot <TOKEN>\n  python acki_bot.py test <name>")
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "bot":
        token = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("TELEGRAM_TOKEN", "")
        if not token:
            print("Provide token: python acki_bot.py bot <TOKEN>")
            sys.exit(1)
        run_bot(token)
    elif mode == "test":
        query = sys.argv[2] if len(sys.argv) > 2 else "raghul"
        asyncio.run(_test(query))
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
