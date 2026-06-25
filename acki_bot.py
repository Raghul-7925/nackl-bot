#!/usr/bin/env python3
"""
Acki Nacki Wallet Bot
Uses mainnet.ackinacki.org/graphql + ever-sdk for TVM decoding.

Run:
  python acki_bot.py bot <TOKEN>
  python acki_bot.py test <name_or_address>
"""

import asyncio, base64, json, logging, os, re, struct, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
import httpx

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

# ── Network ────────────────────────────────────────────────────────────────────
GRAPHQL = "https://mainnet.ackinacki.org/graphql"
HEADERS = {
    "Content-Type": "text/plain",
    "Origin": "https://acki.live",
    "Referer": "https://acki.live/",
}

# ── Known addresses (from chunk-R33FNBXU.js) ──────────────────────────────────
ADDR_CURRENCY_COLLECTION = "8888888888888888888888888888888888888888888888888888888888888888"
ADDR_USDC_ROOT           = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

# ── Code hashes (from chunk-VZWIGR4W.js) ──────────────────────────────────────
HASH_MV    = "6cc8128da9cda444e4ad83fc7064ea51c6a0bbf0e2aa4777d0807e8ed7283cdb"
HASH_POPIT = "18e57fc187e8ac1cc2a9b1e8907e291cd925c840c1f93d2f30fe12747dd90126"
HASH_IDXR  = "f5580a523a708377e8fadc17265def99bed081988d9b9f37e153b938390e3245"

# ── Default currency map (from chunk-VZWIGR4W.js: var g = new Map([[3,{USDC}]]))
# Currency IDs are blockchain-defined; we load them from CurrencyCollection.
# Fallback defaults based on observed behaviour + the hardcoded USDC=3 in source.
DEFAULT_CURRENCIES = {
    0: {"name": "SHELL",   "decimals": 9},   # native balance field
    3: {"name": "USDC",    "decimals": 6},   # hardcoded in source
    # NACKL id is dynamic — discovered from CurrencyCollection contract
}

# ── GraphQL helper ─────────────────────────────────────────────────────────────

async def gql(client: httpx.AsyncClient, query: str, variables: dict) -> dict:
    r = await client.post(
        GRAPHQL,
        content=json.dumps({"query": query, "variables": variables}),
        headers=HEADERS, timeout=20,
    )
    r.raise_for_status()
    body = r.json()
    if "errors" in body:
        raise ValueError(body["errors"][0]["message"])
    return body.get("data", {})

# ── Queries ────────────────────────────────────────────────────────────────────

Q_ACCOUNT = """
query GetAccount($a: String!, $d: String!) {
  blockchain {
    account(account_id: $a, dapp_id: $d) {
      info {
        balance(format: DEC)
        balance_other { currency  value(format: DEC) }
        code_hash  init_code_hash
        last_paid  last_trans_lt(format: DEC)
        data       dapp_id
      }
    }
  }
}
"""

Q_RUN_GET = """
query RunGet($a: String!, $d: String!, $fn: String!) {
  blockchain {
    account(account_id: $a, dapp_id: $d) {
      info {
        run_get { method(name: $fn) { output } }
      }
    }
  }
}
"""

Q_TXNS = """
query GetTxns($a: String!, $d: String!, $n: Int!) {
  blockchain {
    account(account_id: $a, dapp_id: $d) {
      transactions(last: $n, allow_latest_inconsistent_data: true) {
        nodes {
          now
          balance_delta_other { currency  value(format: DEC) }
        }
      }
    }
  }
}
"""

# ── Helpers ────────────────────────────────────────────────────────────────────

def is_addr(s: str) -> bool:
    s = s.strip()
    return bool(re.match(r'^-?\d+:[a-fA-F0-9]{64}$', s)
             or re.match(r'^[a-fA-F0-9]{64}$', s))

def hex_id(addr: str) -> str:
    """Strip workchain prefix → bare 64-char hex."""
    m = re.match(r'^-?\d+:([a-fA-F0-9]{64})$', addr.strip())
    return m.group(1).lower() if m else addr.strip().lower()

async def fetch_info(client, aid):
    """Fetch account info dict or None."""
    try:
        d = await gql(client, Q_ACCOUNT, {"a": aid, "d": aid})
        return d.get("blockchain", {}).get("account", {}).get("info")
    except Exception as e:
        log.warning("fetch_info(%s): %s", aid, e)
        return None

def fmt(raw, dec=9, show=2):
    if not raw or raw == "0":
        return f"0.{'0'*show}"
    try:
        n = int(raw)
        w = n // 10**dec
        f = str(n % 10**dec).zfill(dec)[:show]
        return f"{w:,}.{f}"
    except Exception:
        return f"0.{'0'*show}"

# ── Currency map from CurrencyCollection ──────────────────────────────────────

async def load_currency_map(client: httpx.AsyncClient) -> dict:
    """
    Load currency ID → {name, decimals} from CurrencyCollection contract.
    Falls back to DEFAULT_CURRENCIES on any error.
    
    The CurrencyCollection data BOC encodes a map of extra currencies.
    We try to call run_get on the contract; if unsupported, scan the data BOC.
    """
    result = dict(DEFAULT_CURRENCIES)
    try:
        info = await fetch_info(client, ADDR_CURRENCY_COLLECTION)
        if not info or not info.get("data"):
            return result
        
        # Parse data BOC — currency entries look like:
        # key (uint32) + name (string) + decimals (uint8)
        raw = base64.b64decode(info["data"])
        
        # Simple heuristic: find ASCII name strings near numeric currency IDs
        # We scan for patterns like: \x00\x00\x00\x01 + "NACKL\x00" (len-prefixed)
        # or just scan for known token name strings
        text = raw.decode("latin-1")
        
        # Find NACKL and its preceding currency ID
        for name in ["NACKL", "nackl"]:
            pos = text.find(name)
            if pos > 4:
                # Look at the 4 bytes before the string for currency ID
                for offset in range(1, 20):
                    if pos - offset >= 0:
                        try:
                            cid = struct.unpack(">I", raw[pos-offset:pos-offset+4])[0]
                            if 1 <= cid <= 100:
                                result[cid] = {"name": "NACKL", "decimals": 9}
                                log.info("NACKL currency ID = %d", cid)
                                break
                        except Exception:
                            pass
    except Exception as e:
        log.warning("load_currency_map: %s", e)
    
    return result

# ── Name resolution ────────────────────────────────────────────────────────────
#
# Flow (from chunk-VZWIGR4W.js getLinkedAccounts):
#   1. getName() → decodeAccountData(MvMultifactor ABI) → _name
#   2. getIndexerAddressByName(name) → TVM encode_message(IndexerABI, {_name}) → address
#   3. getPopitGameAddress(mv_id) → TVM encode_message(PopitGameABI, {_owner}) → address
#
# Without TVM SDK, we use these alternatives:
#   - Try name as account_id directly (server may resolve)
#   - Use dapp_id field to find linked PopitGame

async def resolve_identifier(client: httpx.AsyncClient, identifier: str):
    """
    Returns (account_id, wallet_name) tuple.
    account_id is bare 64-char hex of the MvMultifactor.
    wallet_name is the human name or None.
    """
    identifier = identifier.strip()

    if is_addr(identifier):
        aid = hex_id(identifier)
        return aid, None

    # It's a name — try querying with name as account_id
    name_lower = identifier.lower()
    info = await fetch_info(client, name_lower)
    if info and info.get("code_hash"):
        return name_lower, identifier
    
    raise ValueError(
        f"Wallet *'{identifier}'* not found.\n\n"
        "Please use the full address:\n"
        "`/wallet 0:8c478bedb9ffdb890f1e82de78d5edbb0f2af2d4162952a41a99ab9c22871ae7`"
    )

# ── PopitGame lookup ───────────────────────────────────────────────────────────

async def find_popit(client: httpx.AsyncClient, mv_id: str, mv_info: dict) -> Optional[str]:
    """
    Find the PopitGame contract for a given MvMultifactor account_id.
    
    The correct method (from source) requires TVM SDK to compute:
      encode_message(PopitGameABI, initial_data={_pubkey:0x0, _owner: mv_address})
    
    We use the dapp_id as a heuristic — the PopitGame shares the dapp_id of MvMultifactor.
    The dapp_id in account info points to the "dapp root" which is the PopitGame address.
    """
    dapp_id = mv_info.get("dapp_id")
    if dapp_id:
        pid = hex_id(dapp_id)
        if pid != mv_id:
            # Verify it's actually a PopitGame
            pinfo = await fetch_info(client, pid)
            if pinfo:
                ch = pinfo.get("code_hash", "")
                ich = pinfo.get("init_code_hash", "")
                if ch == HASH_POPIT or ich == HASH_POPIT:
                    return pid
    
    # dapp_id == mv_id or not set — we can't derive the address without TVM SDK
    # BUT: we can query the GraphQL with mv_id as dapp_id for the PopitGame
    # The PopitGame's _owner = mv_address, so its dapp_id = mv_address
    # Try: account_id = any_value, dapp_id = mv_id — won't work without knowing account_id
    
    return None

# ── PopitGame data ─────────────────────────────────────────────────────────────

async def get_popit_data(client: httpx.AsyncClient, popit_id: str, currency_map: dict):
    """
    Get NACKL locked balance, MBI level, and speed from PopitGame.
    
    Speed formula (from ABI getDetails output: rewards, startTime):
      speed_nackl_24h = rewards / (now - startTime) * 86400 / 10^9
    
    But we read directly from balances + data BOC for mbiCur.
    """
    result = {"locked": "0", "mbi": 0, "speed": 0.0}
    
    info = await fetch_info(client, popit_id)
    if not info:
        return result
    
    # NACKL locked = balance_other where currency name == NACKL
    nackl_id = next((k for k, v in currency_map.items() if v.get("name") == "NACKL"), None)
    for b in info.get("balance_other") or []:
        if nackl_id is not None and b.get("currency") == nackl_id:
            result["locked"] = b.get("value", "0") or "0"
    
    # MBI level + speed from data BOC (decoded from _mbiCur and _rewards/_startTime)
    if info.get("data"):
        result["mbi"], result["speed"] = decode_popit_boc(info["data"])
    
    return result

def decode_popit_boc(data_b64: str):
    """
    Extract _mbiCur (uint64) and speed from PopitGame data BOC.
    
    PopitGame fields (from ABI):
      _pubkey(uint256), _timestamp(uint64), _constructorFlag(bool),
      _code(map), _owner(address=267bits), _mbiCur(uint64),
      _root(address), _startTime(uint32), _root_pubkey(uint256),
      _boost(address), _rewards(uint128)
    
    TVM serializes these as a bitstream. Without TVM SDK we use heuristics.
    """
    try:
        raw = base64.b64decode(data_b64)
        
        mbi = 0
        speed = 0.0
        
        # Heuristic: scan for uint64 in range 1-500 (MBI level)
        # MBI levels are 1-500 based on game design
        for i in range(len(raw) - 8):
            val = struct.unpack(">Q", raw[i:i+8])[0]
            if 1 <= val <= 500:
                mbi = int(val)
                break
        
        # Speed from _rewards (uint128) and _startTime (uint32)
        # rewards / (now - startTime) * 86400 = NACKL/24h
        import time
        now = int(time.time())
        
        # Look for reasonable _startTime (unix timestamp ~2023-2025)
        start_time = 0
        for i in range(len(raw) - 4):
            val = struct.unpack(">I", raw[i:i+4])[0]
            if 1_680_000_000 <= val <= now:  # 2023-04-08 to now
                start_time = val
                break
        
        # Look for _rewards (uint128, large number in NACKL nanotons)
        # A typical reward might be 1,000-100,000 NACKL = 1e12 to 1e14 nanotons
        if start_time > 0:
            for i in range(len(raw) - 16):
                val = int.from_bytes(raw[i:i+16], 'big')
                if 1e11 <= val <= 1e18:  # 100 to 1 billion NACKL
                    elapsed = now - start_time
                    if elapsed > 0:
                        speed = (val / 1e9) * (86400 / elapsed)
                    break
        
        return mbi, speed
        
    except Exception as e:
        log.warning("decode_popit_boc: %s", e)
        return 0, 0.0

# ── Transaction analysis ───────────────────────────────────────────────────────

async def get_tx_stats(client: httpx.AsyncClient, aid: str, nackl_id: Optional[int]):
    """Calculate speed (NACKL/24h) and tap count from recent transactions."""
    try:
        d = await gql(client, Q_TXNS, {"a": aid, "d": aid, "n": 100})
        nodes = (d.get("blockchain", {})
                  .get("account", {})
                  .get("transactions", {})
                  .get("nodes", []))
    except Exception as e:
        log.warning("get_tx_stats: %s", e)
        return 0.0, 0

    if not nodes:
        return 0.0, 0

    now_ts = max((t.get("now", 0) for t in nodes), default=0)
    cutoff = now_ts - 86400
    taps = 0
    earned = 0

    for tx in nodes:
        ts = tx.get("now", 0)
        for d in tx.get("balance_delta_other") or []:
            # Match by currency ID if we know it, else treat any positive delta as NACKL reward
            cid = d.get("currency", -1)
            is_nackl = (nackl_id is not None and cid == nackl_id) or \
                       (nackl_id is None and cid not in (0, 3))  # not SHELL or USDC
            try:
                v = int(d.get("value", "0"))
            except (ValueError, TypeError):
                v = 0
            if is_nackl and v > 0:
                if ts >= cutoff:
                    earned += v
                taps += 1
                break  # count each tx once

    window_h = (now_ts - cutoff) / 3600 if now_ts > cutoff else 24
    speed = (earned / 1e9) * (24 / max(window_h, 0.1))
    return speed, taps

# ── Name from BOC ──────────────────────────────────────────────────────────────

def name_from_boc(data_b64: str) -> Optional[str]:
    """Extract wallet name from MvMultifactor data BOC."""
    try:
        raw = base64.b64decode(data_b64)
        # TVM stores strings as length-prefixed. Scan for short ASCII names.
        # The _name field is typically 3-24 lowercase alphanum chars.
        matches = re.findall(rb'[a-z][a-z0-9_\-]{2,23}', raw)
        blocklist = {b"none", b"null", b"true", b"false", b"data",
                     b"name", b"type", b"root", b"node"}
        for m in matches:
            if m not in blocklist and len(m) >= 3:
                return m.decode("ascii")
    except Exception:
        pass
    return None

# ── Main lookup ────────────────────────────────────────────────────────────────

async def lookup_wallet(identifier: str) -> dict:
    async with httpx.AsyncClient() as client:

        # 1. Resolve identifier → account_id
        aid, name = await resolve_identifier(client, identifier)

        # 2. Load currency map
        currency_map = await load_currency_map(client)
        nackl_id = next((k for k, v in currency_map.items()
                         if v.get("name") == "NACKL"), None)
        usdc_id = next((k for k, v in currency_map.items()
                        if v.get("name") == "USDC"), None)
        log.info("Currency map: %s", currency_map)

        # 3. Fetch MvMultifactor account
        info = await fetch_info(client, aid)
        if not info:
            raise ValueError(f"Account `0:{aid}` not found.")

        code_hash = info.get("code_hash", "")
        init_hash = info.get("init_code_hash", "")

        # Extract name from BOC if not resolved from name query
        if not name and info.get("data"):
            name = name_from_boc(info["data"])

        # 4. Parse balances
        # SHELL = native balance field (id=0 in the source concat)
        shell_raw  = info.get("balance", "0") or "0"
        nackl_raw  = "0"
        usdc_raw   = "0"

        for b in info.get("balance_other") or []:
            cid = b.get("currency", -1)
            val = b.get("value", "0") or "0"
            if nackl_id is not None and cid == nackl_id:
                nackl_raw = val
            elif nackl_id is None and cid not in (0, 3):
                # Assume any unknown non-USDC currency is NACKL
                nackl_raw = val
            if usdc_id is not None and cid == usdc_id:
                usdc_raw = val
            elif usdc_id is None and cid == 3:
                usdc_raw = val

        # 5. Find PopitGame
        popit_id = await find_popit(client, aid, info)
        log.info("PopitGame id: %s", popit_id)

        locked_raw = "0"
        mbi = 0
        popit_speed = 0.0

        if popit_id:
            pd = await get_popit_data(client, popit_id, currency_map)
            locked_raw  = pd["locked"]
            mbi         = pd["mbi"]
            popit_speed = pd["speed"]

        # 6. Transaction stats (speed + taps)
        tx_speed, taps = await get_tx_stats(client, aid, nackl_id)
        
        # Use popit_speed if available and tx_speed is 0; else use tx_speed
        speed = popit_speed if (popit_speed > 0 and tx_speed == 0) else tx_speed

        return {
            "name":    name or identifier,
            "address": f"0:{aid}",
            "nackl":   nackl_raw,
            "locked":  locked_raw,
            "usdc":    usdc_raw,
            "shell":   shell_raw,
            "speed":   speed,
            "taps":    taps,
            "mbi":     mbi,
            "nackl_id":  nackl_id,
            "usdc_id":   usdc_id,
            "popit_found": popit_id is not None,
        }

# ── Format ─────────────────────────────────────────────────────────────────────

def format_msg(w: dict) -> str:
    nackl_dec  = DEFAULT_CURRENCIES.get(w.get("nackl_id"), {}).get("decimals", 9)
    usdc_dec   = DEFAULT_CURRENCIES.get(w.get("usdc_id"),  {}).get("decimals", 6)
    
    lines = [
        "📊 *Wallet Info*\n",
        f"👤 {w['name']}",
        f"🪙 NACKL: `{fmt(w['nackl'], 9)}`",
        f"🔒 Locked: `{fmt(w['locked'], 9)}`",
        f"💵 USDC: `{fmt(w['usdc'], usdc_dec)}`",
        f"🐚 SHELL: `{fmt(w['shell'], 9)}`",
        f"⚡ Speed: `{w['speed']:,.2f} NACKL/24h`",
        f"👆 Total taps: `{w['taps']}`",
        f"🎮 MBI Level: `{w['mbi']}`",
        f"\n📍 `{w['address']}`",
    ]
    if not w["popit_found"]:
        lines.append("\n_⚠️ Locked/MBI data needs TVM SDK for full accuracy_")
    return "\n".join(lines)

# ── Bot ────────────────────────────────────────────────────────────────────────

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Acki Nacki Wallet Bot*\n\n"
        "`/wallet <name or address>`\n\n"
        "Examples:\n"
        "`/wallet raghul`\n"
        "`/wallet 0:8c478bed...`",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_wallet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Usage: `/wallet <name or address>`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    identifier = " ".join(ctx.args).strip()
    msg = await update.message.reply_text(
        f"🔍 Looking up `{identifier}`…", parse_mode=ParseMode.MARKDOWN
    )
    try:
        w    = await lookup_wallet(identifier)
        await msg.edit_text(format_msg(w), parse_mode=ParseMode.MARKDOWN)
    except ValueError as e:
        await msg.edit_text(f"❌ {e}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        log.exception("lookup error")
        await msg.edit_text(f"❌ Error: {e}")

# ── Health server (keeps Render free tier alive) ───────────────────────────────

class _H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, *a): pass

def _health():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), _H).serve_forever()

# ── Entry ──────────────────────────────────────────────────────────────────────

def run_bot(token: str):
    threading.Thread(target=_health, daemon=True).start()
    log.info("Health server on port %s", os.environ.get("PORT", 8080))
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("wallet", cmd_wallet))
    app.add_handler(CommandHandler("w",      cmd_wallet))
    log.info("Bot polling…")
    app.run_polling(drop_pending_updates=True)

async def _test(q: str):
    print(f"Looking up: {q}\n")
    try:
        w = await lookup_wallet(q)
        print(format_msg(w).replace("*","").replace("`",""))
        print("\nDebug:", {k: v for k, v in w.items()
                           if k in ("nackl_id","usdc_id","popit_found")})
    except ValueError as e:
        print(f"Error: {e}")
    except Exception:
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "bot":
        token = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("TELEGRAM_TOKEN","")
        if not token: print("Provide TELEGRAM_TOKEN"); sys.exit(1)
        run_bot(token)
    elif mode == "test":
        asyncio.run(_test(sys.argv[2] if len(sys.argv) > 2 else "raghul"))
    else:
        print("Usage:\n  python acki_bot.py bot <TOKEN>\n  python acki_bot.py test <name>")
