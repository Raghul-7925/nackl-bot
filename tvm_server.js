/**
 * tvm_server.js — Acki Nacki TVM SDK HTTP bridge
 *
 * Boots worker_compat.js (which shims Web Worker globals and loads worker.js + tvmsdk.wasm),
 * creates an SDK context, then serves POST /call for Python to call abi.encode_message etc.
 *
 * Files needed in same dir:
 *   worker_compat.js   (shim — provided)
 *   worker.js          (from acki.live zip)
 *   tvmsdk.wasm        (from acki.live / your upload)
 *
 * Usage:
 *   node tvm_server.js
 *   TVM_PORT=7799 node tvm_server.js
 */

'use strict';

const http               = require('http');
const path               = require('path');
const fs                 = require('fs');
const { Worker }         = require('worker_threads');

const PORT   = parseInt(process.env.TVM_PORT || '7799', 10);
const DIR    = __dirname;

// ── State ─────────────────────────────────────────────────────────────────────
let worker      = null;
let ready       = false;
let fatalError  = null;
let sdkCtx      = null;   // integer context handle from SDK

const pendingCtx = new Map();  // reqId → {resolve, reject}
const pendingReq = new Map();  // reqId → {resolve, reject}
let ctxCounter   = 1;
let reqCounter   = 1;

// ── Boot ──────────────────────────────────────────────────────────────────────
async function boot() {
  // Compile WASM upfront in the main thread (transferable to worker)
  const wasmBytes  = fs.readFileSync(path.join(DIR, 'tvmsdk.wasm'));
  const wasmModule = await WebAssembly.compile(
    wasmBytes.buffer
      ? wasmBytes.buffer.slice(wasmBytes.byteOffset, wasmBytes.byteOffset + wasmBytes.byteLength)
      : wasmBytes
  );

  worker = new Worker(path.join(DIR, 'worker_compat.js'));

  return new Promise((resolve, reject) => {
    worker.on('error', (err) => {
      fatalError = err;
      console.error('[tvm] worker crashed:', err.message);
      for (const c of pendingCtx.values()) c.reject(err);
      for (const r of pendingReq.values()) r.reject(err);
      pendingCtx.clear(); pendingReq.clear();
      if (!ready) reject(err);
    });

    worker.on('message', (msg) => {
      switch (msg.type) {

        case 'init':
          console.log('[tvm] WASM initialised');
          ready = true;
          resolve();
          break;

        case 'initError':
          fatalError = new Error('init failed: ' + JSON.stringify(msg.error));
          reject(fatalError);
          break;

        case 'createContext': {
          const cb = pendingCtx.get(msg.requestId);
          if (!cb) break;
          pendingCtx.delete(msg.requestId);
          try {
            const parsed = typeof msg.result === 'string' ? JSON.parse(msg.result) : msg.result;
            const ctx    = (parsed && parsed.result !== undefined) ? parsed.result : parsed;
            cb.resolve(ctx);
          } catch(e) { cb.resolve(msg.result); }
          break;
        }

        case 'createContextError': {
          const cb = pendingCtx.get(msg.requestId);
          if (!cb) break;
          pendingCtx.delete(msg.requestId);
          cb.reject(new Error(JSON.stringify(msg.error)));
          break;
        }

        case 'response': {
          const cb = pendingReq.get(msg.requestId);
          if (!cb) break;
          if (!msg.finished) break;   // wait for finished=true
          pendingReq.delete(msg.requestId);
          const params = typeof msg.params === 'string' ? JSON.parse(msg.params) : msg.params;
          // responseType: 0=Success, 1=Error
          if (msg.responseType === 1) {
            cb.reject(new Error(JSON.stringify(params)));
          } else {
            cb.resolve(params);
          }
          break;
        }

        case 'requestError': {
          const cb = pendingReq.get(msg.requestId);
          if (!cb) break;
          pendingReq.delete(msg.requestId);
          cb.reject(new Error(JSON.stringify(msg.error)));
          break;
        }

        default: break;
      }
    });

    // Exactly what Dn() does: postMessage({ type:'init', wasmModule })
    worker.postMessage({ type: 'init', wasmModule }, [wasmModule]);
  });
}

// ── Create context ────────────────────────────────────────────────────────────
function createCtx(configJson) {
  return new Promise((resolve, reject) => {
    const id = ctxCounter++;
    pendingCtx.set(id, { resolve, reject });
    worker.postMessage({ type: 'createContext', requestId: id, configJson });
  });
}

// ── SDK call ──────────────────────────────────────────────────────────────────
function sdkCall(functionName, params) {
  return new Promise((resolve, reject) => {
    const id = reqCounter++;
    const timer = setTimeout(() => {
      pendingReq.delete(id);
      reject(new Error(`Timeout: ${functionName}`));
    }, 15000);

    pendingReq.set(id, {
      resolve: (v) => { clearTimeout(timer); resolve(v); },
      reject:  (e) => { clearTimeout(timer); reject(e);  },
    });

    worker.postMessage({
      type:           'request',
      context:        sdkCtx,
      requestId:      id,
      functionName,
      functionParams: typeof params === 'string' ? params : JSON.stringify(params),
    });
  });
}

// ── HTTP server ───────────────────────────────────────────────────────────────
http.createServer(async (req, res) => {
  const send = (obj) => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(obj));
  };

  if (req.method === 'GET' && req.url === '/health') {
    return send({ ok: true, ready: ready && sdkCtx !== null });
  }

  if (req.method !== 'POST' || req.url !== '/call') {
    res.writeHead(404); return res.end('not found');
  }

  let body = '';
  req.on('data', d => body += d);
  req.on('end', async () => {
    try {
      if (!ready || sdkCtx === null) throw new Error('TVM not ready');
      const { function: fn, params } = JSON.parse(body);
      const result = await sdkCall(fn, params);
      send({ result });
    } catch (e) {
      send({ error: e.message });
    }
  });

}).listen(PORT, '127.0.0.1', () => {
  console.log(`[tvm] listening on http://127.0.0.1:${PORT}`);
});

// ── Init ──────────────────────────────────────────────────────────────────────
(async () => {
  try {
    console.log('[tvm] loading WASM + starting worker…');
    await boot();

    const cfg = JSON.stringify({
      network: { endpoints: ['https://mainnet.ackinacki.org/graphql'] },
    });
    console.log('[tvm] creating SDK context…');
    sdkCtx = await createCtx(cfg);
    console.log('[tvm] ready. context =', sdkCtx);
  } catch (e) {
    console.error('[tvm] fatal:', e.message);
    process.exit(1);
  }
})();
