#!/usr/bin/env python3
"""
Acki Nacki Wallet Bot
Uses bee_sdk.js (from miner app) via Node.js for address resolution.
GraphQL queries mirror index.html exactly.
"""
import asyncio, json, logging, os, re, subprocess, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
import httpx

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

# ── Endpoints (from index.html CFG) ───────────────────────────────────────────
GQL_ENDPOINTS = [
    "https://mainnet.ackinacki.org/graphql",
    "https://mainnet-cf.ackinacki.org/graphql",
]
GQL_HDR = {"Content-Type": "application/json", "Origin": "https://acki.live"}

# Currency IDs confirmed from index.html (cur1 = currency 1 = NACKL locked)
NACKL_ID  = 1
USDC_ID   = 3
NACKL_DEC = 9
USDC_DEC  = 6
SHELL_DEC = 9

# dapp_id used for PopitGame locked balance query (from index.html queryCurrency1Balance)
POPIT_DAPP_ID = "0000000000000000000000000000000000000000000000000000000000000001"

# ── TVM server ─────────────────────────────────────────────────────────────────
TVM_PORT  = int(os.environ.get("TVM_PORT", "7799"))
TVM_BASE  = f"http://127.0.0.1:{TVM_PORT}"
_tvm_proc = None

def start_tvm_server():
    global _tvm_proc
    script = os.path.join(os.path.dirname(__file__), "tvm_server.js")
    if not os.path.exists(script):
        log.warning("tvm_server.js not found")
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
        log.warning("node not found — TVM features disabled")

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
    log.warning("TVM server not ready after %ds", timeout)
    return False

async def tvm_call(action: str, name: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{TVM_BASE}/",
                content=json.dumps({"action": action, "name": name}),
                headers={"Content-Type": "application/json"},
                timeout=20,
            )
        body = r.json()
        if "error" in body:
            log.warning("tvm_call %s(%s): %s", action, name, body["error"])
            return None
        return body.get("result")
    except Exception as e:
        log.warning("tvm_call %s(%s) failed: %s", action, name, e)
        return None

# ── GraphQL ────────────────────────────────────────────────────────────────────

async def gql(client: httpx.AsyncClient, query: str) -> dict:
    """Try each endpoint until one succeeds."""
    for url in GQL_ENDPOINTS:
        try:
            r = await client.post(
                url,
                content=json.dumps({"query": query}),
                headers=GQL_HDR, timeout=15,
            )
            body = r.json()
            if "errors" not in body and body.get("data"):
                return body["data"]
        except Exception:
            continue
    return {}

async def fetch_account(client: httpx.AsyncClient, account_id: str, dapp_id: str = None) -> Optional[dict]:
    """Fetch account info. dapp_id defaults to account_id."""
    did = dapp_id or account_id
    q = f"""{{blockchain{{account(account_id:"{account_id}" dapp_id:"{did}"){{
      info{{
        balance
        balance_other{{currency value}}
        code_hash last_trans_lt last_paid
      }}
    }}}}}}"""
    data = await gql(client, q)
    return data.get("blockchain", {}).get("account", {}).get("info")

async def fetch_transactions(client: httpx.AsyncClient, account_id: str, limit=100) -> list:
    q = f"""{{blockchain{{account(account_id:"{account_id}" dapp_id:"{account_id}"){{
      transactions(last:{limit} allow_latest_inconsistent_data:true){{
        nodes{{now balance_delta_other{{currency value}}}}
      }}
    }}}}}}"""
    data = await gql(client, q)
    return (data.get("blockchain",{}).get("account",{})
                .get("transactions",{}).get("nodes",[])) or []

# ── Helpers ────────────────────────────────────────────────────────────────────

def is_addr(s: str) -> bool:
    return bool(re.match(r'^-?\d+:[a-fA-F0-9]{64}$', s.strip())
             or re.match(r'^[a-fA-F0-9]{64}$', s.strip()))

def hex_id(addr: str) -> str:
    m = re.match(r'^-?\d+:([a-fA-F0-9]{64})$', addr.strip())
    return m.group(1).lower() if m else addr.strip().lower()

def parse_balance_hex(val: str, decimals: int = 9) -> float:
    """Parse hex OR decimal balance string → float. Mirrors index.html exactly."""
    if not val or val == "0":
        return 0.0
    try:
        if isinstance(val, str) and val.startswith("0x"):
            raw = int(val, 16)
        elif isinstance(val, str) and re.match(r'^[0-9a-fA-F]+$', val) and not val.isdigit():
            raw = int(val, 16)  # hex without 0x prefix
        else:
            raw = int(val)      # decimal
        return raw / (10 ** decimals)
    except Exception:
        return 0.0

def fmt(val: float, decimals: int = 2) -> str:
    if val == 0:
        return "0.00"
    if val >= 1000:
        return f"{val:,.{decimals}f}"
    return f"{val:.{decimals}f}"

# ── Wallet lookup ──────────────────────────────────────────────────────────────

async def lookup_wallet(identifier: str) -> dict:
    identifier = identifier.strip()

    async with httpx.AsyncClient() as http:

        # ── 1. Resolve name → MvMultifactor address ───────────────────────────
        wallet_name: Optional[str] = None
        mv_id: Optional[str]       = None

        if is_addr(identifier):
            mv_id = hex_id(identifier)
        else:
            wallet_name = identifier.lower()
            # Use bee_sdk to get wallet address (mirrors index.html connectWallet)
            addr_str = await tvm_call("wallet_address", wallet_name)
            log.info("bee_sdk wallet_address(%s) = %s", wallet_name, addr_str)

            if addr_str and addr_str != "None":
                mv_id = hex_id(addr_str)
            else:
                raise ValueError(
                    f"Wallet *'{identifier}'* not found.\n"
                    "Try the full address:\n`/wallet 0:8c478bed...`"
                )

        # ── 2. Fetch MvMultifactor account ────────────────────────────────────
        mv_info = await fetch_account(http, mv_id)
        if not mv_info:
            raise ValueError(f"Account `0:{mv_id}` not found on chain.")

        # ── 3. Parse balances exactly as index.html does ──────────────────────
        # SHELL = native balance (hex string)
        shell_val = parse_balance_hex(mv_info.get("balance", "0") or "0", SHELL_DEC)

        # balance_other: currency=1 is NACKL, currency=3 is USDC
        nackl_val = 0.0
        usdc_val  = 0.0
        for b in mv_info.get("balance_other") or []:
            cid = b.get("currency", -1)
            v   = parse_balance_hex(b.get("value", "0") or "0", NACKL_DEC)
            if cid == NACKL_ID:   nackl_val = v
            elif cid == USDC_ID:  usdc_val  = v

        # ── 4. Get PopitGame address via bee_sdk ──────────────────────────────
        locked_val  = 0.0
        mbi_level   = 0
        popit_speed = 0.0
        popit_found = False

        if wallet_name:
            popit_str = await tvm_call("popit_address", wallet_name)
            log.info("bee_sdk popit_address(%s) = %s", wallet_name, popit_str)
        else:
            popit_str = None

        if popit_str and popit_str != "None":
            popit_hex = hex_id(popit_str)
            popit_found = True

            # Query locked NACKL exactly as index.html queryCurrency1Balance does:
            # Uses dapp_id = "0000...0001" NOT the popit address itself
            popit_info = await fetch_account(http, popit_hex, POPIT_DAPP_ID)
            if popit_info:
                for b in popit_info.get("balance_other") or []:
                    if b.get("currency") == NACKL_ID:
                        locked_val = parse_balance_hex(b.get("value","0") or "0", NACKL_DEC)

        # ── 5. Transactions: speed + taps ─────────────────────────────────────
        tx_speed = 0.0
        taps     = 0
        try:
            txns = await fetch_transactions(http, mv_id, limit=100)
            if txns:
                now_ts  = max((t.get("now", 0) for t in txns), default=0)
                cutoff  = now_ts - 86400
                earned  = 0.0
                for tx in txns:
                    ts = tx.get("now", 0)
                    for d in tx.get("balance_delta_other") or []:
                        if d.get("currency") == NACKL_ID:
                            v = parse_balance_hex(d.get("value","0") or "0", NACKL_DEC)
                            if v > 0:
                                if ts >= cutoff:
                                    earned += v
                                taps += 1
                                break
                window_h = (now_ts - cutoff) / 3600 if now_ts > cutoff else 24
                tx_speed = earned * (24 / max(window_h, 0.1))
        except Exception as e:
            log.warning("tx stats: %s", e)

        return {
            "name":    wallet_name or f"0:{mv_id[:8]}...",
            "address": f"0:{mv_id}",
            "nackl":   nackl_val,
            "locked":  locked_val,
            "usdc":    usdc_val,
            "shell":   shell_val,
            "speed":   tx_speed,
            "taps":    taps,
            "mbi":     mbi_level,
        }

# ── Format ─────────────────────────────────────────────────────────────────────

def format_msg(w: dict) -> str:
    return "\n".join([
        "📊 *Wallet Info*\n",
        f"👤 {w['name']}",
        f"🪙 NACKL: `{fmt(w['nackl'])}`",
        f"🔒 Locked: `{fmt(w['locked'])}`",
        f"💵 USDC: `{fmt(w['usdc'])}`",
        f"🐚 SHELL: `{fmt(w['shell'], 4)}`",
        f"⚡ Speed: `{fmt(w['speed'])} NACKL/24h`",
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

# ── Health server ──────────────────────────────────────────────────────────────
class _H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def log_message(self, *a): pass

def _health():
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), _H).serve_forever()

# ── Entry ──────────────────────────────────────────────────────────────────────

def run_bot(token: str):
    threading.Thread(target=_health, daemon=True).start()
    start_tvm_server()
    # Wait for Node.js TVM server to be ready
    asyncio.get_event_loop().run_until_complete(wait_tvm_ready(30))
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
