#!/usr/bin/env python3
"""
Acki Nacki Wallet Bot — mirrors NJDminers index.html exactly.

Data sources:
  - bee_sdk (via tvm_server.js Node.js):
      get_wallet_address_by_wallet_name   → MvMultifactor address
      get_popitgame_address_by_wallet_name → PopitGame address
  - GraphQL (mainnet.ackinacki.org/graphql):
      MvMultifactor: balance (SHELL), balance_other (NACKL id=1, USDC id=3)
      PopitGame:     balance_other with dapp_id=0000...0001 → locked NACKL
      Transactions:  balance_delta_other → speed + taps
"""

import asyncio, json, logging, os, re, subprocess, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
import httpx

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

# ── Config (mirrors index.html CFG) ───────────────────────────────────────────
GQL_ENDPOINTS = [
    "https://mainnet.ackinacki.org/graphql",
    "https://mainnet-cf.ackinacki.org/graphql",
]
GQL_HDR = {"Content-Type": "application/json"}

# Currency IDs (from index.html: cur.currency == 1 is NACKL locked)
NACKL_ID  = 1
USDC_ID   = 3

# dapp_id for PopitGame locked balance query (from index.html queryCurrency1Balance)
POPIT_DAPP_ID = "0000000000000000000000000000000000000000000000000000000000000001"

# ── TVM server (Node.js subprocess) ───────────────────────────────────────────
TVM_PORT  = int(os.environ.get("TVM_PORT", "7799"))
TVM_BASE  = f"http://127.0.0.1:{TVM_PORT}"
_tvm_proc = None

def start_tvm_server():
    global _tvm_proc
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tvm_server.js")
    if not os.path.exists(script):
        log.warning("tvm_server.js not found — name lookups disabled")
        return
    try:
        env = os.environ.copy()
        env["TVM_PORT"] = str(TVM_PORT)
        _tvm_proc = subprocess.Popen(
            ["node", script], env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        def _pipe():
            for line in _tvm_proc.stdout:
                log.info("[node] %s", line.decode().rstrip())
        threading.Thread(target=_pipe, daemon=True).start()
        log.info("TVM server started (pid %d)", _tvm_proc.pid)
    except FileNotFoundError:
        log.warning("node not found — name lookups disabled")

async def wait_tvm_ready(timeout=30):
    deadline = time.time() + timeout
    async with httpx.AsyncClient() as c:
        while time.time() < deadline:
            try:
                r = await c.get(f"{TVM_BASE}/health", timeout=2)
                if r.json().get("ready"):
                    log.info("TVM server ready")
                    return True
            except Exception:
                pass
            await asyncio.sleep(1)
    log.warning("TVM server not ready after %ds — name lookups may fail", timeout)
    return False

async def tvm_call(action: str, name: str) -> Optional[str]:
    """Call bee_sdk via Node.js TVM server."""
    try:
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{TVM_BASE}/",
                content=json.dumps({"action": action, "name": name}),
                headers={"Content-Type": "application/json"},
                timeout=25,
            )
        body = r.json()
        if "error" in body:
            log.warning("tvm %s(%s): %s", action, name, body["error"])
            return None
        result = body.get("result", "")
        return result if result and result != "None" else None
    except Exception as e:
        log.warning("tvm %s(%s) failed: %s", action, name, e)
        return None

# ── GraphQL helper (mirrors index.html gql()) ─────────────────────────────────
async def gql(client: httpx.AsyncClient, query: str) -> dict:
    """Try each endpoint until one returns data."""
    for url in GQL_ENDPOINTS:
        try:
            r = await client.post(
                url,
                content=json.dumps({"query": query}),
                headers=GQL_HDR, timeout=12,
            )
            j = r.json()
            if j.get("data"):
                return j["data"]
        except Exception:
            continue
    return {}

# ── Balance parsing (mirrors index.html queryCurrency1Balance) ─────────────────
def parse_hex_balance(val, decimals=9) -> float:
    """
    Parse hex or decimal balance string.
    Mirrors: BigInt(valHex.startsWith('0x') ? valHex : '0x'+valHex) / 1e9
    """
    if not val or val in ("0", "", "0x0"):
        return 0.0
    try:
        s = str(val)
        if s.startswith("0x") or s.startswith("0X"):
            raw = int(s, 16)
        elif re.match(r'^[0-9a-fA-F]+$', s) and not s.isdigit():
            raw = int("0x" + s, 16)  # hex without prefix
        else:
            raw = int(s)
        return raw / (10 ** decimals)
    except Exception:
        return 0.0

def fmt_num(val: float, decimals=2) -> str:
    if val == 0:
        return "0.00"
    if val >= 1000:
        return f"{val:,.{decimals}f}"
    return f"{val:.{decimals}f}"

# ── Address helpers ────────────────────────────────────────────────────────────
def is_addr(s: str) -> bool:
    s = s.strip()
    return bool(re.match(r'^-?\d+:[a-fA-F0-9]{64}$', s)
             or re.match(r'^[a-fA-F0-9]{64}$', s))

def clean_hex(addr: str) -> str:
    """Strip workchain prefix and 0x → bare 64-char hex. Mirrors index.html cleanHex()."""
    if not addr:
        return ""
    h = addr.split(":")[-1] if ":" in addr else addr
    h = re.sub(r'^0x', '', h, flags=re.IGNORECASE)
    return h.lower()

# ── GraphQL queries ────────────────────────────────────────────────────────────

async def fetch_account_balances(client: httpx.AsyncClient, hex_id: str) -> dict:
    """Fetch NACKL + USDC + SHELL balances for a wallet address."""
    q = (f'{{blockchain{{account(account_id:"{hex_id}" dapp_id:"{hex_id}")'
         f'{{info{{balance balance_other{{currency value}}}}}}}}}}')
    data = await gql(client, q)
    return data.get("blockchain", {}).get("account", {}).get("info") or {}

async def fetch_locked_nackl(client: httpx.AsyncClient, popit_hex: str) -> float:
    """
    Mirrors index.html queryCurrency1Balance() exactly:
      dappId = '0000...0001'  (NOT the popit address)
      currency == 1  → NACKL locked
      value is hex   → BigInt('0x'+val) / 1e9
    """
    q = (f'{{blockchain{{account(account_id:"{popit_hex}" dapp_id:"{POPIT_DAPP_ID}")'
         f'{{info{{balance_other{{currency value}}}}}}}}}}')
    data = await gql(client, q)
    others = (data.get("blockchain", {}).get("account", {})
                  .get("info", {}).get("balance_other")) or []
    for c in others:
        if str(c.get("currency")) == "1" or c.get("currency") == 1:
            return parse_hex_balance(c.get("value", "0"))
    return 0.0

async def fetch_transactions(client: httpx.AsyncClient, hex_id: str, limit=100) -> list:
    q = (f'{{blockchain{{account(account_id:"{hex_id}" dapp_id:"{hex_id}")'
         f'{{transactions(last:{limit} allow_latest_inconsistent_data:true)'
         f'{{nodes{{now balance_delta_other{{currency value}}}}}}}}}}}}')
    data = await gql(client, q)
    return ((data.get("blockchain", {}).get("account", {})
                 .get("transactions", {}).get("nodes")) or [])

# ── Wallet lookup ──────────────────────────────────────────────────────────────

async def lookup_wallet(identifier: str) -> dict:
    identifier = identifier.strip()

    async with httpx.AsyncClient() as http:

        # ── 1. Resolve name → MvMultifactor address ───────────────────────────
        wallet_name: Optional[str] = None
        mv_hex: Optional[str]      = None

        if is_addr(identifier):
            mv_hex = clean_hex(identifier)
        else:
            wallet_name = identifier.lower()
            addr_str = await tvm_call("wallet_address", wallet_name)
            log.info("wallet_address(%s) = %s", wallet_name, addr_str)

            if addr_str:
                mv_hex = clean_hex(addr_str)
            else:
                raise ValueError(
                    f"Wallet *'{identifier}'* not found.\n"
                    "Try the full address:\n`/wallet 0:8c478bed...`"
                )

        # ── 2. MvMultifactor balances ──────────────────────────────────────────
        mv_info = await fetch_account_balances(http, mv_hex)
        if not mv_info:
            raise ValueError(f"Account `0:{mv_hex}` not found on chain.")

        # SHELL = native balance (hex)
        shell_val = parse_hex_balance(mv_info.get("balance", "0") or "0")

        # balance_other: NACKL (id=1), USDC (id=3)
        nackl_val = 0.0
        usdc_val  = 0.0
        for b in mv_info.get("balance_other") or []:
            cid = b.get("currency")
            v   = parse_hex_balance(b.get("value", "0") or "0")
            if cid == NACKL_ID or str(cid) == str(NACKL_ID):
                nackl_val = v
            elif cid == USDC_ID or str(cid) == str(USDC_ID):
                usdc_val = v

        # ── 3. PopitGame → locked NACKL ────────────────────────────────────────
        locked_val = 0.0
        if wallet_name:
            popit_str = await tvm_call("popit_address", wallet_name)
            log.info("popit_address(%s) = %s", wallet_name, popit_str)
            if popit_str:
                popit_hex  = clean_hex(popit_str)
                locked_val = await fetch_locked_nackl(http, popit_hex)

        # ── 4. Transactions → speed (NACKL/24h) + total taps ──────────────────
        speed_val = 0.0
        taps_val  = 0
        try:
            txns = await fetch_transactions(http, mv_hex)
            if txns:
                now_ts = max((t.get("now", 0) for t in txns), default=0)
                cutoff = now_ts - 86400
                earned = 0.0
                for tx in txns:
                    ts = tx.get("now", 0)
                    for d in tx.get("balance_delta_other") or []:
                        cid = d.get("currency")
                        if cid == NACKL_ID or str(cid) == str(NACKL_ID):
                            v = parse_hex_balance(d.get("value", "0") or "0")
                            if v > 0:
                                if ts >= cutoff:
                                    earned += v
                                taps_val += 1
                                break
                window_h = (now_ts - cutoff) / 3600 if now_ts > cutoff else 24
                speed_val = earned * (24 / max(window_h, 0.1))
        except Exception as e:
            log.warning("tx stats: %s", e)

        return {
            "name":    wallet_name or f"0:{mv_hex[:8]}...",
            "address": f"0:{mv_hex}",
            "nackl":   nackl_val,
            "locked":  locked_val,
            "usdc":    usdc_val,
            "shell":   shell_val,
            "speed":   speed_val,
            "taps":    taps_val,
            "mbi":     0,   # requires TVM decode — not available without keys
        }

# ── Message formatter ──────────────────────────────────────────────────────────

def format_msg(w: dict) -> str:
    return "\n".join([
        "📊 *Wallet Info*\n",
        f"👤 {w['name']}",
        f"🪙 NACKL: `{fmt_num(w['nackl'])}`",
        f"🔒 Locked: `{fmt_num(w['locked'])}`",
        f"💵 USDC: `{fmt_num(w['usdc'])}`",
        f"🐚 SHELL: `{fmt_num(w['shell'], 4)}`",
        f"⚡ Speed: `{fmt_num(w['speed'])} NACKL/24h`",
        f"👆 Total taps: `{w['taps']}`",
        f"🎮 MBI Level: `{w['mbi']}`",
        f"\n📍 `{w['address']}`",
    ])

# ── Telegram bot ───────────────────────────────────────────────────────────────
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Acki Nacki Wallet Bot*\n\n"
        "`/wallet <name or address>`\n\n"
        "Examples:\n`/wallet raghul`\n`/wallet 0:8c478bed...`",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_wallet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Usage: `/wallet <name or address>`", parse_mode=ParseMode.MARKDOWN)
        return
    identifier = " ".join(ctx.args).strip()
    msg = await update.message.reply_text(
        f"🔍 Looking up `{identifier}`…", parse_mode=ParseMode.MARKDOWN)
    try:
        w = await lookup_wallet(identifier)
        await msg.edit_text(format_msg(w), parse_mode=ParseMode.MARKDOWN)
    except ValueError as e:
        await msg.edit_text(f"❌ {e}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        log.exception("lookup error")
        await msg.edit_text(f"❌ Error: {e}")

# ── Health server (keeps Render alive) ────────────────────────────────────────
class _H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def log_message(self, *a): pass

def _health():
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), _H).serve_forever()

# ── Entry point ────────────────────────────────────────────────────────────────

def run_bot(token: str):
    threading.Thread(target=_health, daemon=True).start()
    start_tvm_server()
    asyncio.run(wait_tvm_ready(30))

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("wallet", cmd_wallet))
    app.add_handler(CommandHandler("w",      cmd_wallet))
    log.info("Bot polling…")
    app.run_polling(drop_pending_updates=True)

async def _test(q: str):
    start_tvm_server()
    await wait_tvm_ready(30)
    print(f"\nLooking up: {q}\n")
    try:
        w = await lookup_wallet(q)
        print(format_msg(w).replace("*","").replace("`",""))
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
