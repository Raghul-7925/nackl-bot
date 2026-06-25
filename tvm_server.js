/**
 * tvm_server.js
 * Tiny HTTP server that wraps tvmsdk.wasm + worker.js for Python to call.
 * 
 * Exposes POST /call  { function: "abi.encode_message", params: {...} }
 * Returns           { result: {...} } or { error: "..." }
 * 
 * Usage:
 *   node tvm_server.js          # listens on port 7799
 *   TVM_PORT=7799 node tvm_server.js
 */

const http   = require('http');
const fs     = require('fs');
const path   = require('path');

// ── Load the WASM + worker glue ─────────────────────────────────────────────
// worker.js uses `self.onmessage` pattern (Web Worker style).
// We shim the Worker globals so it runs in plain Node.js.

const WASM_PATH   = path.join(__dirname, 'tvmsdk.wasm');
const WORKER_PATH = path.join(__dirname, 'worker.js');
const PORT        = parseInt(process.env.TVM_PORT || '7799', 10);

// Pending callbacks: requestId → {resolve, reject}
const pending = new Map();
let   requestIdCounter = 1;

// ── Shim Web Worker globals ──────────────────────────────────────────────────
// The worker.js uses `self`, `postMessage`, and `self.onmessage`.
// We replace these so it runs synchronously in Node.

let workerOnMessage = null;   // set by worker.js via `self.onmessage = ...`

global.self = {
  onmessage: null,
  get onmessage() { return workerOnMessage; },
  set onmessage(fn) { workerOnMessage = fn; },
  self: global.self,   // self.self (used in worker.js)
  WorkerGlobalScope: {},
  indexedDB: null,     // not needed for abi/boc operations
};

// Messages the worker posts back to us
global.postMessage = (msg) => {
  if (msg.type === 'init') {
    console.log('[tvm] WASM initialised OK');
    return;
  }

  if (msg.type === 'createContext') {
    const cb = pending.get('ctx:' + msg.requestId);
    if (cb) { pending.delete('ctx:' + msg.requestId); cb.resolve(msg.result); }
    return;
  }

  // SDK responses come via core_response_handler (already handled in worker.js)
  // but we also receive them here wrapped in postMessage for some paths
  const cb = pending.get(msg.requestId);
  if (cb) {
    pending.delete(msg.requestId);
    if (msg.type && msg.type.includes('Error')) {
      cb.reject(new Error(JSON.stringify(msg.error)));
    } else {
      cb.resolve(msg.result);
    }
  }
};

// ── Intercept core_response_handler calls ───────────────────────────────────
// worker.js calls `core_response_handler(requestId, params, responseType, finished)`
// We need to capture these as our actual SDK results.
// Inject a global that worker.js will call:
let _origCoreResponseHandler = null;
global.__captureResponseHandler = (handler) => {
  _origCoreResponseHandler = handler;
};

// ── Load and init worker.js ──────────────────────────────────────────────────
let wasmReady = false;

async function initWorker() {
  // Read WASM as ArrayBuffer
  const wasmBytes = fs.readFileSync(WASM_PATH);
  const wasmModule = await WebAssembly.compile(wasmBytes.buffer || wasmBytes);

  // Patch worker.js: replace `self.onmessage = ...` handler dispatch
  // so we can call it directly from Node without postMessage roundtrip
  let workerSrc = fs.readFileSync(WORKER_PATH, 'utf8');

  // Replace the indexed DB calls with no-ops (we don't need caching)
  // The WASM itself doesn't require IndexedDB for abi/boc operations

  // Execute worker.js in this context
  const vm = require('vm');
  const ctx = vm.createContext(global);
  vm.runInContext(workerSrc, ctx);

  // Send the init message with the compiled WASM module
  await new Promise((resolve, reject) => {
    const tmpId = 'init:' + (requestIdCounter++);
    // Override postMessage temporarily to catch init response
    const orig = global.postMessage;
    global.postMessage = (msg) => {
      if (msg.type === 'init') { global.postMessage = orig; resolve(); }
      else if (msg.type === 'initError') { global.postMessage = orig; reject(new Error(msg.error)); }
      else orig(msg);
    };
    workerOnMessage({ data: { type: 'init', wasmModule } });
  });

  wasmReady = true;
  console.log('[tvm] Worker ready on port', PORT);
}

// ── Create SDK context ───────────────────────────────────────────────────────
let sdkContext = null;

async function getContext() {
  if (sdkContext !== null) return sdkContext;

  const reqId = requestIdCounter++;
  const result = await new Promise((resolve, reject) => {
    pending.set('ctx:' + reqId, { resolve, reject });
    workerOnMessage({
      data: {
        type: 'createContext',
        configJson: JSON.stringify({
          network: { endpoints: ['https://mainnet.ackinacki.org/graphql'] },
        }),
        requestId: reqId,
      }
    });
  });

  const parsed = JSON.parse(result);
  if (parsed.error) throw new Error(parsed.error);
  sdkContext = parsed.result;
  console.log('[tvm] Context created:', sdkContext);
  return sdkContext;
}

// ── Call SDK function ────────────────────────────────────────────────────────
function callSdk(functionName, params) {
  return new Promise(async (resolve, reject) => {
    const ctx = await getContext();
    const reqId = requestIdCounter++;

    // The worker calls core_response_handler which calls postMessage
    // We intercept via the pending map keyed by reqId
    const timeout = setTimeout(() => {
      pending.delete(reqId);
      reject(new Error('SDK timeout: ' + functionName));
    }, 15000);

    // Set up response capture — core_response_handler posts back to us
    // The worker.js has this path: core_response_handler → postMessage({requestId, ...})
    pending.set(reqId, {
      resolve: (r) => { clearTimeout(timeout); resolve(r); },
      reject:  (e) => { clearTimeout(timeout); reject(e); },
    });

    workerOnMessage({
      data: {
        type: 'request',
        context: ctx,
        functionName,
        functionParams: params,
        requestId: reqId,
      }
    });
  });
}

// ── HTTP server ──────────────────────────────────────────────────────────────
const server = http.createServer(async (req, res) => {
  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200); res.end(JSON.stringify({ ok: true, ready: wasmReady }));
    return;
  }

  if (req.method !== 'POST' || req.url !== '/call') {
    res.writeHead(404); res.end('Not found');
    return;
  }

  let body = '';
  req.on('data', d => body += d);
  req.on('end', async () => {
    try {
      const { function: fn, params } = JSON.parse(body);
      if (!wasmReady) throw new Error('WASM not ready yet');
      const result = await callSdk(fn, params);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ result }));
    } catch (e) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: e.message }));
    }
  });
});

server.listen(PORT, '127.0.0.1', () => {
  console.log('[tvm] HTTP server on http://127.0.0.1:' + PORT);
  initWorker().catch(e => { console.error('[tvm] Init failed:', e); process.exit(1); });
});
