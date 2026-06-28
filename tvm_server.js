/**
 * tvm_server.js
 * Uses bee_sdk.js + bee_sdk_bg.wasm from the Acki Nacki miner app.
 * Exposes HTTP API for Python to resolve wallet names → addresses.
 *
 * Files needed in same dir:
 *   bee_sdk.js        (from miner app assets)
 *   bee_sdk_bg.wasm   (from miner app assets)
 *
 * Usage: node tvm_server.js
 */

'use strict';

const http = require('http');
const fs   = require('fs');
const path = require('path');

const PORT     = parseInt(process.env.TVM_PORT || '7799', 10);
const ENDPOINT = 'https://mainnet.ackinacki.org/graphql';
const DIR      = __dirname;

// ── bee_sdk.js is an ES module — convert it for CommonJS use ─────────────────
// It uses `export function` syntax. We load it via dynamic import().

let sdk = null;

async function loadSdk() {
  // bee_sdk.js uses `export` — needs to be loaded as ESM
  // Node.js supports dynamic import() for ESM files
  const wasmPath = path.join(DIR, 'bee_sdk_bg.wasm');
  const sdkPath  = path.join(DIR, 'bee_sdk.js');

  // Verify files exist
  if (!fs.existsSync(wasmPath)) throw new Error('bee_sdk_bg.wasm not found in ' + DIR);
  if (!fs.existsSync(sdkPath))  throw new Error('bee_sdk.js not found in ' + DIR);

  // Load the WASM bytes
  const wasmBytes = fs.readFileSync(wasmPath);

  // bee_sdk.js expects to be loaded as ESM — use pathToFileURL
  const { pathToFileURL } = require('url');
  const sdkModule = await import(pathToFileURL(sdkPath).href);

  // Initialize with WASM bytes
  // bee_sdk's __wbg_init accepts: ArrayBuffer, WebAssembly.Module, or path
  const wasmBuffer = wasmBytes.buffer.slice(
    wasmBytes.byteOffset,
    wasmBytes.byteOffset + wasmBytes.byteLength
  );
  
  // Call the default export or the initSync function
  if (sdkModule.default) {
    await sdkModule.default({ module_or_path: wasmBuffer });
  } else if (sdkModule.initSync) {
    sdkModule.initSync({ module: wasmBuffer });
  } else {
    // Try calling __wbg_init directly if exported
    const initFn = sdkModule.__wbg_init || sdkModule.init;
    if (initFn) await initFn(wasmBuffer);
  }

  return sdkModule;
}

// ── Resolve wallet name → addresses ──────────────────────────────────────────

async function getWalletAddress(walletName) {
  // TParamsOfGetWalletAddressByWalletName = { name: string, ...network params }
  // From WASM binary strings: it needs "name" and network endpoint
  const result = await sdk.get_wallet_address_by_wallet_name({
    name: walletName,
    endpoints: [ENDPOINT],
  });
  return result;
}

async function getPopitAddress(walletName) {
  const result = await sdk.get_popitgame_address_by_wallet_name({
    name: walletName,
    endpoints: [ENDPOINT],
  });
  return result;
}

async function getMinerAddress(walletName) {
  const result = await sdk.get_miner_address_by_wallet_name({
    name: walletName,
    endpoints: [ENDPOINT],
  });
  return result;
}

// ── HTTP server ───────────────────────────────────────────────────────────────

const server = http.createServer(async (req, res) => {
  const send = (obj, status = 200) => {
    res.writeHead(status, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(obj));
  };

  if (req.method === 'GET' && req.url === '/health') {
    return send({ ok: true, ready: sdk !== null });
  }

  if (req.method !== 'POST') {
    return send({ error: 'POST only' }, 405);
  }

  let body = '';
  req.on('data', d => body += d);
  req.on('end', async () => {
    try {
      if (!sdk) throw new Error('SDK not ready');
      const { action, name } = JSON.parse(body);

      let result;
      switch (action) {
        case 'wallet_address':
          result = await getWalletAddress(name);
          break;
        case 'popit_address':
          result = await getPopitAddress(name);
          break;
        case 'miner_address':
          result = await getMinerAddress(name);
          break;
        default:
          throw new Error(`Unknown action: ${action}`);
      }

      send({ result: String(result) });
    } catch (e) {
      console.error('[tvm] error:', e.message);
      send({ error: e.message });
    }
  });
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[tvm] HTTP server on http://127.0.0.1:${PORT}`);
});

// ── Init ──────────────────────────────────────────────────────────────────────
(async () => {
  try {
    console.log('[tvm] Loading bee_sdk WASM...');
    sdk = await loadSdk();
    console.log('[tvm] bee_sdk ready. Exported functions:', 
      Object.keys(sdk).filter(k => k.startsWith('get_')));
  } catch (e) {
    console.error('[tvm] Fatal init error:', e.message);
    process.exit(1);
  }
})();
