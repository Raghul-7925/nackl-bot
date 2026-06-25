#!/usr/bin/env python3
"""
Acki Nacki Wallet Bot — uses tvmsdk.wasm via Node.js subprocess for TVM ops.

Files needed in same directory:
  acki_bot.py      ← this file
  tvm_server.js    ← Node.js TVM wrapper
  tvmsdk.wasm      ← Acki Nacki TVM SDK WASM (from acki.live)
  worker.js        ← WASM glue JS (from acki.live)

Install:
  pip install httpx python-telegram-bot

Run:
  python acki_bot.py bot <TOKEN>
  python acki_bot.py test <name_or_address>
"""

import asyncio, json, logging, os, re, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
import httpx

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════
# CONSTANTS (from acki.live source)
# ══════════════════════════════════════════════════════════════════════

GRAPHQL   = "https://mainnet.ackinacki.org/graphql"
GQL_HDR   = {"Content-Type": "text/plain", "Origin": "https://acki.live"}

# Currency IDs — confirmed from chunk-F5RX2E5J.js: Hn={nackl:"1", usdc:"3"}
NACKL_ID  = 1   # in balance_other
USDC_ID   = 3   # in balance_other
NACKL_DEC = 9
USDC_DEC  = 6
SHELL_DEC = 9   # native balance field

# ABIs extracted from chunk-F5RX2E5J.js
INDEXER_ABI = {"ABI version":2,"version":"2.4","header":["pubkey","time","expire"],"functions":[{"name":"getDetails","inputs":[],"outputs":[{"name":"name","type":"string"},{"name":"wallet","type":"address"}]},{"name":"getVersion","inputs":[],"outputs":[{"name":"value0","type":"string"},{"name":"value1","type":"string"}]}],"events":[],"fields":[{"init":True,"name":"_pubkey","type":"uint256"},{"init":False,"name":"_timestamp","type":"uint64"},{"init":False,"name":"_constructorFlag","type":"bool"},{"init":True,"name":"_name","type":"string"},{"init":False,"name":"_wallet","type":"address"},{"init":False,"name":"_root","type":"address"},{"init":False,"name":"_rootPubkey","type":"uint256"}]}

POPIT_ABI = {"ABI version":2,"version":"2.4","header":["pubkey","time","expire"],"functions":[{"name":"getDetails","inputs":[],"outputs":[{"name":"owner","type":"address"},{"name":"root","type":"address"},{"name":"startTime","type":"uint32"},{"name":"mbiCur","type":"uint64"},{"name":"boost","type":"address"},{"name":"rewards","type":"uint128"},{"name":"minstake","type":"uint128"}]},{"name":"getVersion","inputs":[],"outputs":[{"name":"value0","type":"string"},{"name":"value1","type":"string"}]}],"events":[],"fields":[{"init":True,"name":"_pubkey","type":"uint256"},{"init":False,"name":"_timestamp","type":"uint64"},{"init":False,"name":"_constructorFlag","type":"bool"},{"init":False,"name":"_code","type":"map(uint8,cell)"},{"init":True,"name":"_owner","type":"address"},{"init":False,"name":"_mbiCur","type":"uint64"},{"init":False,"name":"_root","type":"address"},{"init":False,"name":"_startTime","type":"uint32"},{"init":False,"name":"_root_pubkey","type":"uint256"},{"init":False,"name":"_boost","type":"address"},{"init":False,"name":"_rewards","type":"uint128"}]}

# TVC codes (base64) from chunk-F5RX2E5J.js (Un = PopitGame, Wn = Indexer)
INDEXER_TVC = "te6ccgECIwEABTUABCSK7VMg4wMgwP/jAiDA/uMC8gseAwEiArSNCGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAT4aSHbPNMAAY4igwjXGCD4KMjOzsn5AAHTAAGU0/9QM5MC+ELiIPhl+RDyqJXTAAHyeuLTPwEcAgFO+EMhufK0IPgjgQPoqIIg94rA3o6A3vgAkvAOlIAg94pA3rOl99CTVM52+A/SaG1g+kAx0NMDAcchkl8E4AHTPwHtRNDXCx+DFv79wT/4PfpA1NHQ0wfU0dDTB9Mf0//TD9P/0wf0BPQF+Gj4Z/hm+GP4Yo6A2CL4SfhKxwXy4+j4ACT4SoBA9A6OgN/4RvJzcfhm4tMAAY4SgQIA1xgg+QFY+EIg2zxY2zHikvIz4tMAAY4SgQIA1xgg+QFY+EIg2zxY2zHikvIz4uIw0x8B+CO88rki+E/A/5Jt"

POPIT_TVC   = "te6ccgECPAEACZQABCSK7VMg4wMgwP/jAiDA/uMC8gs3AwE7ArSNCGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAT4aSHbPNMAAY4igwjXGCD4KMjOzsn5AAHTAAGU0/9QM5MC+ELiIPhl+RDyqJXTAAHyeuLTPwE2AgFO+EMhufK0IPgjgQPoqIIg94rA3o6A3vgAkvAOlIAg94pA3rOl99CTVM52+A/SaG1g+kAx0NMDAcchkl8E4AHTPwHtRNDXCx+DFv79wT/4PfpA1NHQ0wfU0dDTB9Mf0//TD9P/0wf0BPQF+Gj4Z/hm+GP4Yo6A2CL4SfhKxwXy4+j4ACT4SoBA9A6OgN/4RvJzcfhm4tMAAY4SgQIA1xgg+QFY+EIg2zxY2zHikvIz4tMAAY4SgQIA1xgg+QFY+EIg2zxY2zHikvIz4uIw0x8B+CO88rki+E/A/5JtXw3xwAKSbV8N4iCUMCDTHwHbMeBb2zxb"

# ══════════════════════════════════════════════════════════════════════
# TVM server (Node.js subprocess)
# ══════════════════════════════════════════════════════════════════════

TVM_PORT    = int(os.environ.get("TVM_PORT", "7799"))
TVM_BASE    = f"http://127.0.0.1:{TVM_PORT}"
_tvm_proc   = None

def start_tvm_server():
    """Launch tvm_server.js as a subprocess."""
    global _tvm_proc
    script = os.path.join(os.path.dirname(__file__), "tvm_server.js")
    if not os.path.exists(script):
        log.warning("tvm_server.js not found — TVM features disabled")
        return False

    node = "node"
    try:
        env = os.environ.copy()
        env["TVM_PORT"] = str(TVM_PORT)
        _tvm_proc = subprocess.Popen(
            [node, script],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        # Log output in background thread
        def _pipe():
            for line in _tvm_proc.stdout:
                log.info("[node] %s", line.decode().rstrip())
        threading.Thread(target=_pipe, daemon=True).start()
        log.info("TVM server started (pid %d)", _tvm_proc.pid)
        return True
    except FileNotFoundError:
        log.warning("Node.js not found — TVM features disabled")
        return False


async def wait_tvm_ready(timeout: int = 30):
    """Wait until the TVM server responds to /health."""
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
            await asyncio.sleep(0.5)
    log.warning("TVM server did not become ready in %ds", timeout)
    return False


async def tvm_call(function_name: str, params: dict) -> Optional[dict]:
    """Call a function on the TVM SDK server."""
    try:
        async with httpx.AsyncClient() as c:
            r = await c.post(
                f"{TVM_BASE}/call",
                content=json.dumps({"function": function_name, "params": params}),
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
        body = r.json()
        if "error" in body:
            log.warning("tvm_call(%s) error: %s", function_name, body["error"])
            return None
        return body.get("result")
    except Exception as e:
        log.warning("tvm_call(%s) failed: %s", function_name, e)
        return None


async def tvm_get_indexer_address(name: str) -> Optional[str]:
    """
    Derive Indexer contract address from wallet name.
    = encode_message(IndexerABI, tvc=INDEXER_TVC, initial_data={_pubkey:"0x0", _name:name})
    """
    result = await tvm_call("abi.encode_message", {
        "abi": {"type": "Json", "value": json.dumps(INDEXER_ABI)},
        "deploy_set": {
            "tvc": INDEXER_TVC,
            "initial_data": {"_pubkey": "0x0", "_name": name.lower()},
        },
        "signer": {"type": "None"},
    })
    if result and result.get("address"):
        addr = result["address"]
        return addr.split(":")[-1].lower()
    return None


async def tvm_get_popit_address(mv_hex_id: str) -> Optional[str]:
    """
    Derive PopitGame contract address from MvMultifactor address.
    = encode_message(PopitGameABI, tvc=POPIT_TVC, initial_data={_pubkey:"0x0", _owner:"0:mv"})
    """
    result = await tvm_call("abi.encode_message", {
        "abi": {"type": "Json", "value": json.dumps(POPIT_ABI)},
        "deploy_set": {
            "tvc": POPIT_TVC,
            "initial_data": {"_pubkey": "0x0", "_owner": f"0:{mv_hex_id}"},
        },
        "signer": {"type": "None"},
    })
    if result and result.get("address"):
        addr = result["address"]
        return addr.split(":")[-1].lower()
    return None


async def tvm_decode_indexer_data(data_boc: str) -> Optional[dict]:
    """Decode Indexer data BOC → {_name, _wallet, ...}"""
    result = await tvm_call("abi.decode_account_data", {
        "abi": {"type": "Json", "value": json.dumps(INDEXER_ABI)},
        "data": data_boc,
    })
    return result.get("data") if result else None


async def tvm_decode_popit_data(data_boc: str) -> Optional[dict]:
    """Decode PopitGame data BOC → {_mbiCur, _rewards, _startTime, ...}"""
    result = await tvm_call("abi.decode_account_data", {
        "abi": {"type": "Json", "value": json.dumps(POPIT_ABI)},
        "data": data_boc,
    })
    return result.get("data") if result else None

# ══════════════════════════════════════════════════════════════════════
# GraphQL helpers
# ══════════════════════════════════════════════════════════════════════

async def gql(client: httpx.AsyncClient, query: str, variables: dict) -> dict:
    r = await client.post(
        GRAPHQL,
        content=json.dumps({"query": query, "variables": variables}),
        headers=GQL_HDR, timeout=20,
    )
    r.raise_for_status()
    body = r.json()
    if "errors" in body:
        raise ValueError(body["errors"][0]["message"])
    return body.get("data", {})

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
}"""

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
}"""

async def fetch_info(client: httpx.AsyncClient, aid: str) -> Optional[dict]:
    try:
        d = await gql(client, Q_ACCOUNT, {"a": aid, "d": aid})
        return d.get("blockchain", {}).get("account", {}).get("info")
    except Exception as e:
        log.warning("fetch_info(%s): %s", aid, e)
        return None

# ══════════════════════════════════════════════════════════════════════
# Utilities
# ══════════════════════════════════════════════════════════════════════

def is_addr(s: str) -> bool:
    s = s.strip()
    return bool(re.match(r'^-?\d+:[a-fA-F0-9]{64}$', s)
             or re.match(r'^[a-fA-F0-9]{64}$', s))

def hex_id(addr: str) -> str:
    m = re.match(r'^-?\d+:([a-fA-F0-9]{64})$', addr.strip())
    return m.group(1).lower() if m else addr.strip().lower()

def fmt(raw, dec=9, show=2):
    if not raw or str(raw) == "0":
        return f"0.{'0'*show}"
    try:
        n = int(raw)
        w = n // 10**dec
        f = str(n % 10**dec).zfill(dec)[:show]
        return f"{w:,}.{f}"
    except Exception:
        return f"0.{'0'*show}"

# ══════════════════════════════════════════════════════════════════════
# Wallet lookup
# ══════════════════════════════════════════════════════════════════════

async def lookup_wallet(identifier: str) -> dict:
    identifier = identifier.strip()

    async with httpx.AsyncClient() as http:

        # ── 1. Resolve name → MvMultifactor hex ID ───────────────────────────
        wallet_name: Optional[str] = None
        mv_id: Optional[str]       = None

        if is_addr(identifier):
            mv_id = hex_id(identifier)
        else:
            wallet_name = identifier
            name_lower  = identifier.lower()

            # TVM: derive Indexer address from name
            indexer_id = await tvm_get_indexer_address(name_lower)
            log.info("Indexer addr for '%s': %s", name_lower, indexer_id)

            if indexer_id:
                idxr_info = await fetch_info(http, indexer_id)
                if idxr_info and idxr_info.get("data"):
                    decoded = await tvm_decode_indexer_data(idxr_info["data"])
                    log.info("Indexer decoded: %s", decoded)
                    if decoded:
                        wallet_name = decoded.get("_name") or wallet_name
                        w = decoded.get("_wallet", "")
                        if w:
                            mv_id = hex_id(w)

            if not mv_id:
                # Fallback: try name as account_id directly
                info_direct = await fetch_info(http, name_lower)
                if info_direct and info_direct.get("code_hash"):
                    mv_id = name_lower
                else:
                    raise ValueError(
                        f"Wallet *'{identifier}'* not found.\n"
                        "Try the full address:\n"
                        "`/wallet 0:8c478bed...`"
                    )

        # ── 2. Fetch MvMultifactor info ───────────────────────────────────────
        mv_info = await fetch_info(http, mv_id)
        if not mv_info:
            raise ValueError(f"Account `0:{mv_id}` not found on chain.")

        # ── 3. Balances ───────────────────────────────────────────────────────
        shell_raw = mv_info.get("balance", "0") or "0"
        nackl_raw = "0"
        usdc_raw  = "0"
        for b in mv_info.get("balance_other") or []:
            cid = b.get("currency", -1)
            val = b.get("value", "0") or "0"
            if cid == NACKL_ID: nackl_raw = val
            elif cid == USDC_ID: usdc_raw = val

        # ── 4. PopitGame ──────────────────────────────────────────────────────
        popit_id    = await tvm_get_popit_address(mv_id)
        log.info("PopitGame addr: %s", popit_id)

        locked_raw  = "0"
        mbi_level   = 0
        popit_speed = 0.0
        popit_found = False

        if popit_id:
            popit_info = await fetch_info(http, popit_id)
            if popit_info:
                popit_found = True
                for b in popit_info.get("balance_other") or []:
                    if b.get("currency") == NACKL_ID:
                        locked_raw = b.get("value", "0") or "0"

                if popit_info.get("data"):
                    dp = await tvm_decode_popit_data(popit_info["data"])
                    log.info("PopitGame decoded: %s", dp)
                    if dp:
                        mbi_level = int(dp.get("_mbiCur", 0) or 0)
                        try:
                            rewards   = int(dp.get("_rewards", "0") or "0")
                            start_ts  = int(dp.get("_startTime", "0") or "0")
                            elapsed   = int(time.time()) - start_ts
                            if elapsed > 0 and rewards > 0:
                                popit_speed = (rewards / 10**NACKL_DEC) * (86400 / elapsed)
                        except (ValueError, TypeError):
                            pass

        # ── 5. Transactions → speed + tap count ──────────────────────────────
        tx_speed = 0.0
        taps     = 0
        try:
            d = await gql(http, Q_TXNS, {"a": mv_id, "d": mv_id, "n": 100})
            nodes = (d.get("blockchain",{})
                      .get("account",{})
                      .get("transactions",{})
                      .get("nodes",[]))
            if nodes:
                now_ts = max(t.get("now", 0) for t in nodes)
                cutoff = now_ts - 86400
                earned = 0
                for tx in nodes:
                    ts = tx.get("now", 0)
                    for delta in tx.get("balance_delta_other") or []:
                        if delta.get("currency") == NACKL_ID:
                            try:
                                v = int(delta.get("value", "0"))
                                if v > 0:
                                    if ts >= cutoff: earned += v
                                    taps += 1
                                    break
                            except (ValueError, TypeError):
                                pass
                wh = (now_ts - cutoff) / 3600 if now_ts > cutoff else 24
                tx_speed = (earned / 10**NACKL_DEC) * (24 / max(wh, 0.1))
        except Exception as e:
            log.warning("tx stats: %s", e)

        speed = popit_speed if popit_speed > 0 else tx_speed

        return {
            "name":        wallet_name or f"0:{mv_id}",
            "address":     f"0:{mv_id}",
            "nackl":       nackl_raw,
            "locked":      locked_raw,
            "usdc":        usdc_raw,
            "shell":       shell_raw,
            "speed":       speed,
            "taps":        taps,
            "mbi":         mbi_level,
            "popit_found": popit_found,
        }

# ══════════════════════════════════════════════════════════════════════
# Formatter
# ══════════════════════════════════════════════════════════════════════

def format_msg(w: dict) -> str:
    return "\n".join([
        "📊 *Wallet Info*\n",
        f"👤 {w['name']}",
        f"🪙 NACKL: `{fmt(w['nackl'], NACKL_DEC)}`",
        f"🔒 Locked: `{fmt(w['locked'], NACKL_DEC)}`",
        f"💵 USDC: `{fmt(w['usdc'], USDC_DEC)}`",
        f"🐚 SHELL: `{fmt(w['shell'], SHELL_DEC)}`",
        f"⚡ Speed: `{w['speed']:,.2f} NACKL/24h`",
        f"👆 Total taps: `{w['taps']}`",
        f"🎮 MBI Level: `{w['mbi']}`",
        f"\n📍 `{w['address']}`",
    ])

# ══════════════════════════════════════════════════════════════════════
# Telegram bot
# ══════════════════════════════════════════════════════════════════════

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
        log.exception("lookup_wallet error")
        await msg.edit_text(f"❌ Error: {e}")

# ── Health server (Render) ────────────────────────────────────────────────────
class _H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def log_message(self, *a): pass

def _health():
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), _H).serve_forever()

# ══════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════

def run_bot(token: str):
    threading.Thread(target=_health, daemon=True).start()
    start_tvm_server()
    # Give Node.js 10s to start before first request; it'll keep warming in bg
    loop = asyncio.new_event_loop()
    loop.run_until_complete(asyncio.sleep(3))
    loop.close()

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("wallet", cmd_wallet))
    app.add_handler(CommandHandler("w",      cmd_wallet))
    log.info("Bot polling…")
    app.run_polling(drop_pending_updates=True)

async def _test(q: str):
    start_tvm_server()
    await asyncio.sleep(3)   # wait for Node.js
    await wait_tvm_ready(20)
    print(f"\nLooking up: {q}\n")
    try:
        w = await lookup_wallet(q)
        print(format_msg(w).replace("*","").replace("`",""))
        print("\npopit_found:", w["popit_found"])
    except ValueError as e:
        print(f"Error: {e}")
    except Exception:
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "bot":
        token = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("TELEGRAM_TOKEN","")
        if not token: print("Provide TELEGRAM_TOKEN"); sys.exit(1)
        run_bot(token)
    elif mode == "test":
        asyncio.run(_test(sys.argv[2] if len(sys.argv) > 2 else "raghul"))
    else:
        print("Usage:\n  python acki_bot.py bot <TOKEN>\n  python acki_bot.py test <name>")
