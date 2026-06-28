/**
 * tvm_server.js — Acki Nacki address resolver using bee_sdk
 *
 * Exact param format from index.html:
 *   bee.get_wallet_address_by_wallet_name({
 *     client_config: { network: { endpoints: [...] } },
 *     wallet_name: name
 *   })
 *
 * Files needed: bee_sdk.js, bee_sdk_bg.wasm (+ package.json with "type":"module")
 */

import { readFileSync } from 'fs';
import { createServer }  from 'http';
import { fileURLToPath } from 'url';
import { dirname, join }  from 'path';

import beeSdkInit, {
  get_wallet_address_by_wallet_name,
  get_popitgame_address_by_wallet_name,
  get_miner_address_by_wallet_name,
} from './bee_sdk.js';

const __dir = dirname(fileURLToPath(import.meta.url));
const PORT  = parseInt(process.env.TVM_PORT || '7799', 10);

// Endpoints WITHOUT /graphql (as used in index.html goshEndpoints)
const ENDPOINTS = [
  'https://mainnet.ackinacki.org',
  'https://mainnet-cf.ackinacki.org',
];

const CLIENT_CONFIG = { network: { endpoints: ENDPOINTS } };

// ── Init WASM ─────────────────────────────────────────────────────────────────
let ready = false;

async function initWasm() {
  const wasmBytes = readFileSync(join(__dir, 'bee_sdk_bg.wasm'));
  const wasmBuf   = wasmBytes.buffer.slice(
    wasmBytes.byteOffset,
    wasmBytes.byteOffset + wasmBytes.byteLength
  );
  await beeSdkInit({ module_or_path: wasmBuf });
  console.log('[tvm] bee_sdk WASM ready');
  ready = true;
}

// ── HTTP server ───────────────────────────────────────────────────────────────
createServer(async (req, res) => {
  const send = obj => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(obj));
  };

  if (req.method === 'GET' && req.url === '/health') {
    return send({ ok: true, ready });
  }

  if (req.method !== 'POST') {
    res.writeHead(405); return res.end();
  }

  let body = '';
  req.on('data', d => body += d);
  req.on('end', async () => {
    try {
      if (!ready) throw new Error('WASM not ready');
      const { action, name } = JSON.parse(body);
      const params = { client_config: CLIENT_CONFIG, wallet_name: name };
      let result;

      switch (action) {
        case 'wallet_address':
          result = await get_wallet_address_by_wallet_name(params);
          break;
        case 'popit_address':
          result = await get_popitgame_address_by_wallet_name(params);
          break;
        case 'miner_address':
          result = await get_miner_address_by_wallet_name(params);
          break;
        default:
          throw new Error('Unknown action: ' + action);
      }

      console.log(`[tvm] ${action}(${name}) =`, result);
      send({ result: String(result) });
    } catch (e) {
      console.error(`[tvm] error:`, e.message);
      send({ error: e.message });
    }
  });
}).listen(PORT, '127.0.0.1', () => {
  console.log(`[tvm] listening on http://127.0.0.1:${PORT}`);
});

await initWasm();
