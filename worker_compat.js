/**
 * worker_compat.js
 * Shims Web Worker globals so worker.js runs inside Node.js worker_threads.
 *
 * worker.js uses:
 *   - `self.onmessage = handler`
 *   - `postMessage(msg)`
 *   - `self.self`
 *   - `self.indexedDB` (null is fine)
 *   - `self.WorkerGlobalScope`
 *   - `TextDecoder` / `TextEncoder` (built-in Node.js)
 *   - `WebAssembly` (built-in Node.js)
 *   - `fetch` (NOT needed — we pass wasmModule directly)
 */

'use strict';

const { parentPort, workerData } = require('worker_threads');

// ── Shim `self` ───────────────────────────────────────────────────────────────
global.self = {
  get self()             { return global.self; },
  WorkerGlobalScope:     {},
  indexedDB:             null,   // not needed for abi/boc ops
  get onmessage()        { return global._onmessage; },
  set onmessage(fn)      { global._onmessage = fn; },
};

// ── Shim `postMessage` (sends to parent thread) ───────────────────────────────
global.postMessage = (msg, transfer) => {
  parentPort.postMessage(msg, transfer);
};

// ── Forward messages from parent → worker.js handler ─────────────────────────
parentPort.on('message', (msg) => {
  if (typeof global._onmessage === 'function') {
    global._onmessage({ data: msg });
  }
});

// ── Load worker.js ────────────────────────────────────────────────────────────
require('./worker.js');
