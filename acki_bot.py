#!/usr/bin/env python3
"""
Acki Nacki Wallet Bot — with TVM SDK for accurate address derivation & BOC decoding.

Requirements:
  pip install httpx python-telegram-bot ton-client-py

Run:
  python acki_bot.py bot <TOKEN>
  python acki_bot.py test <name_or_address>
"""

import asyncio, base64, json, logging, os, re, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
import httpx

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════
# CONSTANTS  (extracted from acki.live source)
# ══════════════════════════════════════════════════════════════════════

GRAPHQL   = "https://mainnet.ackinacki.org/graphql"
GQL_HDR   = {"Content-Type": "text/plain", "Origin": "https://acki.live"}

# Currency IDs confirmed from chunk-F5RX2E5J.js: Hn = {nackl:"1", shell:"2", usdc:"3"}
# In balance_other: NACKL=1, USDC=3
# Native `balance` field = SHELL (9 decimals)
NACKL_ID  = 1
USDC_ID   = 3
NACKL_DEC = 9
USDC_DEC  = 6
SHELL_DEC = 9

# Contract code hashes
HASH_MV    = "6cc8128da9cda444e4ad83fc7064ea51c6a0bbf0e2aa4777d0807e8ed7283cdb"
HASH_POPIT = "18e57fc187e8ac1cc2a9b1e8907e291cd925c840c1f93d2f30fe12747dd90126"
HASH_IDXR  = "f5580a523a708377e8fadc17265def99bed081988d9b9f37e153b938390e3245"

# ── ABIs extracted from chunk-F5RX2E5J.js ─────────────────────────────────────

INDEXER_ABI = {"ABI version":2,"version":"2.4","header":["pubkey","time","expire"],"functions":[{"name":"constructor","inputs":[{"name":"wallet","type":"address"},{"name":"rootPubkey","type":"uint256"},{"name":"index","type":"uint128"},{"name":"root","type":"address"}],"outputs":[]},{"name":"getDetails","inputs":[],"outputs":[{"name":"name","type":"string"},{"name":"wallet","type":"address"}]},{"name":"getVersion","inputs":[],"outputs":[{"name":"value0","type":"string"},{"name":"value1","type":"string"}]}],"events":[],"fields":[{"init":True,"name":"_pubkey","type":"uint256"},{"init":False,"name":"_timestamp","type":"uint64"},{"init":False,"name":"_constructorFlag","type":"bool"},{"init":True,"name":"_name","type":"string"},{"init":False,"name":"_wallet","type":"address"},{"init":False,"name":"_root","type":"address"},{"init":False,"name":"_rootPubkey","type":"uint256"}]}

POPIT_ABI = {"ABI version":2,"version":"2.4","header":["pubkey","time","expire"],"functions":[{"name":"constructor","inputs":[{"name":"code","type":"map(uint8,cell)"},{"name":"root_pubkey","type":"uint256"},{"name":"index","type":"uint128"}],"outputs":[]},{"name":"setMbiCur","inputs":[{"name":"mbiCur","type":"uint64"}],"outputs":[]},{"name":"getDetails","inputs":[],"outputs":[{"name":"owner","type":"address"},{"name":"root","type":"address"},{"name":"startTime","type":"uint32"},{"name":"mbiCur","type":"uint64"},{"name":"boost","type":"address"},{"name":"rewards","type":"uint128"},{"name":"minstake","type":"uint128"}]},{"name":"getVersion","inputs":[],"outputs":[{"name":"value0","type":"string"},{"name":"value1","type":"string"}]}],"events":[],"fields":[{"init":True,"name":"_pubkey","type":"uint256"},{"init":False,"name":"_timestamp","type":"uint64"},{"init":False,"name":"_constructorFlag","type":"bool"},{"init":False,"name":"_code","type":"map(uint8,cell)"},{"init":True,"name":"_owner","type":"address"},{"init":False,"name":"_mbiCur","type":"uint64"},{"init":False,"name":"_root","type":"address"},{"init":False,"name":"_startTime","type":"uint32"},{"init":False,"name":"_root_pubkey","type":"uint256"},{"init":False,"name":"_boost","type":"address"},{"init":False,"name":"_rewards","type":"uint128"}]}

# TVC codes (base64 BOC) extracted from chunk-F5RX2E5J.js
INDEXER_CODE = "te6ccgECIwEABTUABCSK7VMg4wMgwP/jAiDA/uMC8gseAwEiArSNCGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAT4aSHbPNMAAY4igwjXGCD4KMjOzsn5AAHTAAGU0/9QM5MC+ELiIPhl+RDyqJXTAAHyeuLTPwEcAgFO+EMhufK0IPgjgQPoqIIg94rA3o6A3vgAkvAOlIAg94pA3rOl99CTVM52+A/SaG1g+kAx0NMDAcchkl8E4AHTPwHtRNDXCx+DFv79wT/4PfpA1NHQ0wfU0dDTB9Mf0//TD9P/0wf0BPQF+Gj4Z/hm+GP4Yo6A2CL4SfhKxwXy4+j4ACT4SoBA9A6OgN/4RvJzcfhm4tMAAY4SgQIA1xgg+QFY+EIg2zxY2zHikvIz4tMAAY4SgQIA1xgg+QFY+EIg2zxY2zHikvIz4uIw0x8B+CO88rki+E/A/5Jt"

POPIT_CODE = "te6ccgECPAEACZQABCSK7VMg4wMgwP/jAiDA/uMC8gs3AwE7ArSNCGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAT4aSHbPNMAAY4igwjXGCD4KMjOzsn5AAHTAAGU0/9QM5MC+ELiIPhl+RDyqJXTAAHyeuLTPwE2AgFO+EMhufK0IPgjgQPoqIIg94rA3o6A3vgAkvAOlIAg94pA3rOl99CTVM52+A/SaG1g+kAx0NMDAcchkl8E4AHTPwHtRNDXCx+DFv79wT/4PfpA1NHQ0wfU0dDTB9Mf0//TD9P/0wf0BPQF+Gj4Z/hm+GP4Yo6A2CL4SfhKxwXy4+j4ACT4SoBA9A6OgN/4RvJzcfhm4tMAAY4SgQIA1xgg+QFY+EIg2zxY2zHikvIz4tMAAY4SgQIA1xgg+QFY+EIg2zxY2zHikvIz4uIw0x8B+CO88rki+E/A/5JtXw3xwAKSbV8N4iCUMCDTHwHbMeBb2zxb"

# ══════════════════════════════════════════════════════════════════════
# TVM SDK  (ton-client-py)
# ══════════════════════════════════════════════════════════════════════

_tvm_client = None

def get_tvm_client():
    """Return a singleton TonClient connected to mainnet.ackinacki.org."""
    global _tvm_client
    if _tvm_client is not None:
        return _tvm_client
    try:
        from tonclient.client import TonClient
        from tonclient.types import ClientConfig, NetworkConfig
        cfg = ClientConfig()
        cfg.network = NetworkConfig(
            endpoints=["https://mainnet.ackinacki.org/graphql"],
        )
        _tvm_client = TonClient(config=cfg, is_async=True)
        log.info("TVM client initialised")
    except ImportError:
        log.warning("ton-client-py not installed — TVM features disabled")
        _tvm_client = None
    except Exception as e:
        log.warning("TVM client init failed: %s", e)
        _tvm_client = None
    return _tvm_client


async def tvm_get_indexer_address(name: str) -> Optional[str]:
    """
    Derive the Indexer contract address from a wallet name.
    Replicates: tvmClientService.getIndexerAddressByName(name)
      → encode_message(IndexerABI, initial_data={_pubkey:"0x0", _name:name})
    """
    client = get_tvm_client()
    if not client:
        return None
    try:
        from tonclient.types import (
            ParamsOfEncodeMessage, Abi, AbiType,
            DeploySet, Signer, SignerType,
        )
        abi = Abi(type=AbiType.JSON, value=json.dumps(INDEXER_ABI))
        deploy = DeploySet(
            tvc=INDEXER_CODE,
            initial_data={"_pubkey": "0x0", "_name": name.lower()},
        )
        signer = Signer(type=SignerType.NONE)
        params = ParamsOfEncodeMessage(abi=abi, deploy_set=deploy, signer=signer)
        result = await client.abi.encode_message(params=params)
        addr = result.address  # "0:hex64"
        return addr.split(":")[-1].lower()
    except Exception as e:
        log.warning("tvm_get_indexer_address(%s): %s", name, e)
        return None


async def tvm_get_popit_address(mv_hex_id: str) -> Optional[str]:
    """
    Derive the PopitGame contract address from the MvMultifactor address.
    Replicates: tvmClientService.getPopitGameAddress(mv_id)
      → encode_message(PopitGameABI, initial_data={_pubkey:"0x0", _owner:"0:mv_hex"})
    """
    client = get_tvm_client()
    if not client:
        return None
    try:
        from tonclient.types import (
            ParamsOfEncodeMessage, Abi, AbiType,
            DeploySet, Signer, SignerType,
        )
        abi    = Abi(type=AbiType.JSON, value=json.dumps(POPIT_ABI))
        deploy = DeploySet(
            tvc=POPIT_CODE,
            initial_data={"_pubkey": "0x0", "_owner": f"0:{mv_hex_id}"},
        )
        signer = Signer(type=SignerType.NONE)
        params = ParamsOfEncodeMessage(abi=abi, deploy_set=deploy, signer=signer)
        result = await client.abi.encode_message(params=params)
        addr = result.address
        return addr.split(":")[-1].lower()
    except Exception as e:
        log.warning("tvm_get_popit_address(%s): %s", mv_hex_id, e)
        return None


async def tvm_decode_indexer_data(data_boc: str) -> Optional[dict]:
    """
    Decode Indexer contract data BOC → {_name, _wallet}.
    Replicates: tvmClientService.decodeAccountData(data, IndexerABI)
    """
    client = get_tvm_client()
    if not client:
        return None
    try:
        from tonclient.types import ParamsOfDecodeAccountData, Abi, AbiType
        abi    = Abi(type=AbiType.JSON, value=json.dumps(INDEXER_ABI))
        params = ParamsOfDecodeAccountData(abi=abi, data=data_boc)
        result = await client.abi.decode_account_data(params=params)
        return result.data  # {"_name": "raghul", "_wallet": "0:8c47...", ...}
    except Exception as e:
        log.warning("tvm_decode_indexer_data: %s", e)
        return None


async def tvm_decode_popit_data(data_boc: str) -> Optional[dict]:
    """
    Decode PopitGame contract data BOC → {_mbiCur, _rewards, _startTime, ...}.
    Replicates: tvmClientService.decodeAccountData(data, PopitGameABI)
    """
    client = get_tvm_client()
    if not client:
        return None
    try:
        from tonclient.types import ParamsOfDecodeAccountData, Abi, AbiType
        abi    = Abi(type=AbiType.JSON, value=json.dumps(POPIT_ABI))
        params = ParamsOfDecodeAccountData(abi=abi, data=data_boc)
        result = await client.abi.decode_account_data(params=params)
        return result.data  # {"_mbiCur": "64", "_rewards": "...", "_startTime": "..."}
    except Exception as e:
        log.warning("tvm_decode_popit_data: %s", e)
        return None

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
# Main wallet lookup
# ══════════════════════════════════════════════════════════════════════

async def lookup_wallet(identifier: str) -> dict:
    identifier = identifier.strip()

    async with httpx.AsyncClient() as http:

        # ── Step 1: Resolve name → MvMultifactor address ─────────────────────
        wallet_name: Optional[str] = None
        mv_id: Optional[str]       = None

        if is_addr(identifier):
            mv_id = hex_id(identifier)
        else:
            wallet_name = identifier
            name_lower  = identifier.lower()

            # TVM SDK: derive Indexer address from name
            indexer_id = await tvm_get_indexer_address(name_lower)
            log.info("Indexer addr for '%s': %s", name_lower, indexer_id)

            if indexer_id:
                # Query Indexer contract data to get _wallet (MvMultifactor addr)
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
                # Fallback: try name directly as account_id
                info_direct = await fetch_info(http, name_lower)
                if info_direct and info_direct.get("code_hash"):
                    mv_id = name_lower
                else:
                    raise ValueError(
                        f"Wallet *'{identifier}'* not found.\n\n"
                        "Try the full address:\n"
                        "`/wallet 0:8c478bed...`"
                    )

        # ── Step 2: Fetch MvMultifactor account info ──────────────────────────
        mv_info = await fetch_info(http, mv_id)
        if not mv_info:
            raise ValueError(f"Account `0:{mv_id}` not found on chain.")

        # ── Step 3: Parse NACKL + USDC + SHELL balances ───────────────────────
        # SHELL = native balance field
        # NACKL = balance_other[currency==1]
        # USDC  = balance_other[currency==3]
        shell_raw = mv_info.get("balance", "0") or "0"
        nackl_raw = "0"
        usdc_raw  = "0"

        for b in mv_info.get("balance_other") or []:
            cid = b.get("currency", -1)
            val = b.get("value", "0") or "0"
            if cid == NACKL_ID:
                nackl_raw = val
            elif cid == USDC_ID:
                usdc_raw = val

        # ── Step 4: Find & query PopitGame contract ───────────────────────────
        popit_id = await tvm_get_popit_address(mv_id)
        log.info("PopitGame addr: %s", popit_id)

        locked_raw  = "0"
        mbi_level   = 0
        popit_speed = 0.0
        popit_found = False

        if popit_id:
            popit_info = await fetch_info(http, popit_id)
            if popit_info:
                popit_found = True

                # NACKL locked = balance_other[currency==1] on PopitGame
                for b in popit_info.get("balance_other") or []:
                    if b.get("currency") == NACKL_ID:
                        locked_raw = b.get("value", "0") or "0"

                # Decode data BOC for _mbiCur + _rewards + _startTime
                if popit_info.get("data"):
                    decoded_p = await tvm_decode_popit_data(popit_info["data"])
                    log.info("PopitGame decoded: %s", decoded_p)
                    if decoded_p:
                        mbi_level = int(decoded_p.get("_mbiCur", 0) or 0)

                        # Speed = rewards / elapsed * 86400 (NACKL per 24h)
                        rewards_raw  = decoded_p.get("_rewards", "0") or "0"
                        start_time   = decoded_p.get("_startTime", "0") or "0"
                        try:
                            rewards  = int(rewards_raw)
                            start_ts = int(start_time)
                            now_ts   = int(time.time())
                            elapsed  = now_ts - start_ts
                            if elapsed > 0 and rewards > 0:
                                popit_speed = (rewards / 10**NACKL_DEC) * (86400 / elapsed)
                        except (ValueError, TypeError):
                            pass

        # ── Step 5: Transactions → speed + taps ──────────────────────────────
        tx_speed = 0.0
        taps     = 0
        try:
            d = await gql(http, Q_TXNS, {"a": mv_id, "d": mv_id, "n": 100})
            nodes = (d.get("blockchain", {})
                      .get("account", {})
                      .get("transactions", {})
                      .get("nodes", []))
            if nodes:
                now_ts  = max(t.get("now", 0) for t in nodes)
                cutoff  = now_ts - 86400
                earned  = 0
                for tx in nodes:
                    ts = tx.get("now", 0)
                    for delta in tx.get("balance_delta_other") or []:
                        if delta.get("currency") == NACKL_ID:
                            try:
                                v = int(delta.get("value", "0"))
                                if v > 0:
                                    if ts >= cutoff:
                                        earned += v
                                    taps += 1
                                    break
                            except (ValueError, TypeError):
                                pass
                window_h = (now_ts - cutoff) / 3600 if now_ts > cutoff else 24
                tx_speed = (earned / 10**NACKL_DEC) * (24 / max(window_h, 0.1))
        except Exception as e:
            log.warning("tx stats: %s", e)

        # Prefer PopitGame speed (more accurate); fall back to tx-derived speed
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
            "tvm_ok":      get_tvm_client() is not None,
        }

# ══════════════════════════════════════════════════════════════════════
# Message formatter
# ══════════════════════════════════════════════════════════════════════

def format_msg(w: dict) -> str:
    lines = [
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
    ]
    return "\n".join(lines)

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
        "Examples:\n"
        "`/wallet raghul`\n"
        "`/wallet 0:8c478bed...`",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_wallet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Usage: `/wallet <name or address>`\nExample: `/wallet raghul`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    identifier = " ".join(ctx.args).strip()
    msg = await update.message.reply_text(
        f"🔍 Looking up `{identifier}`…", parse_mode=ParseMode.MARKDOWN
    )
    try:
        w = await lookup_wallet(identifier)
        await msg.edit_text(format_msg(w), parse_mode=ParseMode.MARKDOWN)
    except ValueError as e:
        await msg.edit_text(f"❌ {e}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        log.exception("lookup_wallet error")
        await msg.edit_text(f"❌ Error: {e}")

# ── Health server keeps Render Web Service alive ───────────────────────────────
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
    # Pre-warm TVM client
    get_tvm_client()
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("wallet", cmd_wallet))
    app.add_handler(CommandHandler("w",      cmd_wallet))
    log.info("Bot polling…")
    app.run_polling(drop_pending_updates=True)

async def _test(q: str):
    get_tvm_client()  # init
    print(f"\nLooking up: {q}\n")
    try:
        w = await lookup_wallet(q)
        print(format_msg(w).replace("*","").replace("`",""))
        print("\nDebug:", {k: w[k] for k in ("popit_found","tvm_ok","speed")})
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
