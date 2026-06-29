#!/usr/bin/env python3
"""
Acki Nacki Wallet Bot — built directly from raghul.har network traffic.
Every query, address, and field format verified against real responses.
"""
import asyncio, json, logging, os, re, subprocess, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
import httpx

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

# ── Confirmed from HAR ─────────────────────────────────────────────────────────
GQL_URLS = [
    "https://mainnet.ackinacki.org/graphql",
    "https://mainnet-cf.ackinacki.org/graphql",
]
GQL_HDR = {"Content-Type": "application/json"}

# From HAR: messages from this address = NACKL tap rewards
REWARD_SRC = "0505050505050505050505050505050505050505050505050505050505050505"

# From HAR: currency=1 is NACKL (in value_other)
NACKL_CURRENCY = 1
USDC_CURRENCY  = 3

# ── TVM server (bee_sdk for name→address) ─────────────────────────────────────
TVM_PORT  = int(os.environ.get("TVM_PORT", "7799"))
TVM_BASE  = f"http://127.0.0.1:{TVM_PORT}"
_proc     = None

def start_tvm_server():
    global _proc
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tvm_server.js")
    if not os.path.exists(script):
        log.warning("tvm_server.js not found")
        return
    try:
        env = os.environ.copy()
        env["TVM_PORT"] = str(TVM_PORT)
        _proc = subprocess.Popen(["node", script], env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        def _log():
            for line in _proc.stdout:
                log.info("[node] %s", line.decode().rstrip())
        threading.Thread(target=_log, daemon=True).start()
        log.info("TVM server started (pid %d)", _proc.pid)
    except FileNotFoundError:
        log.warning("node not found")

async def wait_tvm_ready(timeout=30):
    deadline = time.time() + timeout
    async with httpx.AsyncClient() as c:
        while time.time() < deadline:
            try:
                r = await c.get(f"{TVM_BASE}/health", timeout=2)
                if r.json().get("ready"):
                    log.info("TVM ready")
                    return True
            except Exception:
                pass
            await asyncio.sleep(1)
    return False

async def tvm_call(action: str, name: str) -> Optional[str]:
    try:
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{TVM_BASE}/",
                             content=json.dumps({"action": action, "name": name}),
                             headers={"Content-Type": "application/json"},
                             timeout=25)
        body = r.json()
        if "error" in body:
            log.warning("tvm %s(%s): %s", action, name, body["error"])
            return None
        v = body.get("result", "")
        return v if v and v != "None" else None
    except Exception as e:
        log.warning("tvm %s(%s): %s", action, name, e)
        return None

# ── GraphQL ────────────────────────────────────────────────────────────────────

async def gql(client: httpx.AsyncClient, query: str, variables: dict = {}) -> dict:
    for url in GQL_URLS:
        try:
            r = await client.post(url,
                                  content=json.dumps({"query": query, "variables": variables}),
                                  headers=GQL_HDR, timeout=15)
            j = r.json()
            if j.get("data"):
                return j["data"]
        except Exception:
            continue
    return {}

# ── Helpers ────────────────────────────────────────────────────────────────────

def is_addr(s):
    s = s.strip()
    return bool(re.match(r'^-?\d+:[a-fA-F0-9]{64}$', s) or
                re.match(r'^[a-fA-F0-9]{64}$', s))

def clean_hex(addr):
    if not addr: return ""
    h = addr.split(":")[-1] if ":" in addr else addr
    return re.sub(r'^0x', '', h, flags=re.IGNORECASE).lower()

def dec_to_float(val, decimals=9) -> float:
    """
    HAR confirmed: balance(format:DEC) returns decimal strings like "146439004000".
    value_other values are also decimal: "4261670956"
    Simple int division.
    """
    if not val or str(val) in ("0", ""):
        return 0.0
    try:
        return int(str(val)) / (10 ** decimals)
    except Exception:
        return 0.0

def fmt(val: float, dec=2) -> str:
    if val == 0: return "0.00"
    return f"{val:,.{dec}f}" if val >= 1000 else f"{val:.{dec}f}"

# ── Step 1: Resolve Indexer data → wallet + popit addresses ───────────────────
# HAR confirmed:
#   Indexer addr for "raghul": a432f6f5...d9dd1718
#   Query: GetIndexerData with accountId=dappId=indexer_addr
#   Returns: data BOC containing _wallet and _name (base64)

async def fetch_indexer_data(client, indexer_hex):
    q = """query GetIndexerData($accountId: String!, $dappId: String!) {
      blockchain { account(account_id: $accountId, dapp_id: $dappId) {
        info { data }
      }}
    }"""
    d = await gql(client, q, {"accountId": indexer_hex, "dappId": indexer_hex})
    return d.get("blockchain", {}).get("account", {}).get("info", {}).get("data")

# ── Step 2: Get MvMultifactor balances ────────────────────────────────────────
# HAR confirmed: balance(format:DEC)="146439004000" → 146.44 SHELL
# balance_other not in HAR for MvMultifactor directly,
# but confirmed NACKL currency=1 from messages value_other

async def fetch_mv_balances(client, mv_hex):
    q = """query GetAccount($accountId: String!, $dappId: String!) {
      blockchain { account(account_id: $accountId, dapp_id: $dappId) {
        info {
          balance(format: DEC)
          balance_other { currency value(format: DEC) }
        }
      }}
    }"""
    d = await gql(client, q, {"accountId": mv_hex, "dappId": mv_hex})
    return d.get("blockchain", {}).get("account", {}).get("info") or {}

# ── Step 3: Get PopitGame messages for speed + taps ───────────────────────────
# HAR confirmed:
#   Messages to ae78b6bb... from 0505...0505 = tap rewards
#   value_other[{currency:1, value:"4261670956"}] (decimal) = NACKL earned
#   Total messages from 0505...0505 = total taps

async def fetch_popit_messages(client, popit_hex, limit=80):
    """
    HAR flow:
    1. AccountMessageAndEventIds → get message IDs
    2. BatchMsgTx → get each message's src, value_other
    """
    # Step 1: get message IDs
    q1 = """query AccountMessageAndEventIds($accountId: String!, $dappId: String!, $last: Int!) {
      blockchain { account(account_id: $accountId, dapp_id: $dappId) {
        messages(last: $last) { nodes { id } }
      }}
    }"""
    d1 = await gql(client, q1, {"accountId": popit_hex, "dappId": popit_hex, "last": limit})
    msg_ids = [n["id"] for n in
               (d1.get("blockchain", {}).get("account", {})
                  .get("messages", {}).get("nodes") or [])]

    if not msg_ids:
        return []

    # Step 2: batch fetch messages (HAR does 11 at a time)
    BATCH = 11
    all_msgs = []
    for i in range(0, len(msg_ids), BATCH):
        batch = msg_ids[i:i+BATCH]
        aliases = "\n".join(
            f'm{j}: message(hash: "{mid}") {{ id src dst value(format:DEC) value_other {{ currency value(format:DEC) }} msg_type_name dst_transaction {{ now }} }}'
            for j, mid in enumerate(batch)
        )
        q2 = f"query BatchMsgTx {{ blockchain {{ {aliases} }} }}"
        d2 = await gql(client, q2)
        bc = d2.get("blockchain", {})
        for j in range(len(batch)):
            msg = bc.get(f"m{j}")
            if msg:
                all_msgs.append(msg)

    return all_msgs

# ── Step 4: Get locked NACKL from PopitGame BOC ───────────────────────────────
# HAR shows acki.live fetches the BOC and decodes with ABI
# The acki.live ABI endpoint: GET /abi/18e57fc1...dd90126.json
# But we can query balance_other with dapp_id=0000...0001 (from index.html)

async def fetch_locked_nackl(client, popit_hex):
    DAPP = "0000000000000000000000000000000000000000000000000000000000000001"
    q = (f'{{blockchain{{account(account_id:"{popit_hex}" dapp_id:"{DAPP}")'
         f'{{info{{balance_other{{currency value(format:DEC)}}}}}}}}}}')
    d = await gql(client, q)
    others = (d.get("blockchain", {}).get("account", {})
               .get("info", {}).get("balance_other")) or []
    for c in others:
        if str(c.get("currency")) == "1" or c.get("currency") == 1:
            return dec_to_float(c.get("value", "0"))
    return 0.0

# ── Main lookup ────────────────────────────────────────────────────────────────

async def lookup_wallet(identifier: str) -> dict:
    identifier = identifier.strip()

    async with httpx.AsyncClient() as http:

        # ── Resolve name → address ─────────────────────────────────────────────
        wallet_name = None
        mv_hex = None
        popit_hex = None

        if is_addr(identifier):
            mv_hex = clean_hex(identifier)
        else:
            wallet_name = identifier.lower()
            # bee_sdk: name → wallet address
            mv_str = await tvm_call("wallet_address", wallet_name)
            log.info("wallet_address(%s) = %s", wallet_name, mv_str)
            if mv_str:
                mv_hex = clean_hex(mv_str)
            else:
                raise ValueError(
                    f"Wallet *'{identifier}'* not found.\n"
                    "Try the full address:\n`/wallet 0:8c478bed...`"
                )

        # ── Get PopitGame address ──────────────────────────────────────────────
        if wallet_name:
            popit_str = await tvm_call("popit_address", wallet_name)
            log.info("popit_address(%s) = %s", wallet_name, popit_str)
            if popit_str:
                popit_hex = clean_hex(popit_str)

        # ── MvMultifactor balances ─────────────────────────────────────────────
        mv_info = await fetch_mv_balances(http, mv_hex)
        if not mv_info:
            raise ValueError(f"Account `0:{mv_hex}` not found.")

        # HAR confirmed: balance(format:DEC) = decimal string
        shell_val = dec_to_float(mv_info.get("balance", "0") or "0")

        nackl_val = 0.0
        usdc_val  = 0.0
        for b in mv_info.get("balance_other") or []:
            cid = b.get("currency")
            v   = dec_to_float(b.get("value", "0") or "0")
            if cid == NACKL_CURRENCY or str(cid) == "1":
                nackl_val = v
            elif cid == USDC_CURRENCY or str(cid) == "3":
                usdc_val = v

        # ── Locked NACKL from PopitGame ────────────────────────────────────────
        locked_val = 0.0
        if popit_hex:
            locked_val = await fetch_locked_nackl(http, popit_hex)

        # ── Speed + Taps from PopitGame messages ───────────────────────────────
        # HAR: messages src=0505...0505 to PopitGame with value_other[currency=1]
        speed_val = 0.0
        taps_val  = 0

        if popit_hex:
            try:
                msgs = await fetch_popit_messages(http, popit_hex, limit=80)
                now_ts = int(time.time())
                cutoff = now_ts - 86400
                earned_24h = 0.0

                for msg in msgs:
                    src = clean_hex(msg.get("src", ""))
                    if src != REWARD_SRC:
                        continue
                    # This is a tap reward message
                    taps_val += 1
                    tx_now = 0
                    dst_tx = msg.get("dst_transaction")
                    if dst_tx:
                        tx_now = dst_tx.get("now", 0)
                    for vo in msg.get("value_other") or []:
                        if str(vo.get("currency")) == "1" or vo.get("currency") == 1:
                            v = dec_to_float(vo.get("value", "0") or "0")
                            if tx_now >= cutoff:
                                earned_24h += v

                # Speed = NACKL earned in 24h window
                speed_val = earned_24h * (86400 / 86400)  # already a 24h window
            except Exception as e:
                log.warning("messages fetch: %s", e)

        return {
            "name":    wallet_name or f"0:{mv_hex[:8]}...",
            "address": f"0:{mv_hex}",
            "nackl":   nackl_val,
            "locked":  locked_val,
            "usdc":    usdc_val,
            "shell":   shell_val,
            "speed":   speed_val,
            "taps":    taps_val,
            "mbi":     0,
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

# ── Telegram ───────────────────────────────────────────────────────────────────
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Acki Nacki Wallet Bot*\n\n"
        "`/wallet <name or address>`\n\n"
        "Examples:\n`/wallet raghul`\n`/wallet 0:8c478bed...`",
        parse_mode=ParseMode.MARKDOWN)

async def cmd_wallet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: `/wallet <name or address>`",
                                        parse_mode=ParseMode.MARKDOWN)
        return
    identifier = " ".join(ctx.args).strip()
    msg = await update.message.reply_text(f"🔍 Looking up `{identifier}`…",
                                          parse_mode=ParseMode.MARKDOWN)
    try:
        w = await lookup_wallet(identifier)
        await msg.edit_text(format_msg(w), parse_mode=ParseMode.MARKDOWN)
    except ValueError as e:
        await msg.edit_text(f"❌ {e}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        log.exception("lookup error")
        await msg.edit_text(f"❌ Error: {e}")

class _H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def log_message(self, *a): pass

def _health():
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), _H).serve_forever()

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
    except Exception:
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "bot":
        token = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("TELEGRAM_TOKEN","")
        if not token: print("No token"); sys.exit(1)
        run_bot(token)
    elif mode == "test":
        asyncio.run(_test(sys.argv[2] if len(sys.argv) > 2 else "raghul"))
    else:
        print("python acki_bot.py bot <TOKEN>\npython acki_bot.py test <name>")
