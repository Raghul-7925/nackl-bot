/**
 * test_tvm.js — verify bee_sdk works with correct params
 * node test_tvm.js
 */
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join }  from 'path';

import beeSdkInit, {
  get_wallet_address_by_wallet_name,
  get_popitgame_address_by_wallet_name,
} from './bee_sdk.js';

const __dir     = dirname(fileURLToPath(import.meta.url));
const wasmBytes = readFileSync(join(__dir, 'bee_sdk_bg.wasm'));
const wasmBuf   = wasmBytes.buffer.slice(wasmBytes.byteOffset, wasmBytes.byteOffset + wasmBytes.byteLength);

const CLIENT_CONFIG = {
  network: {
    endpoints: ['https://mainnet.ackinacki.org', 'https://mainnet-cf.ackinacki.org']
  }
};

console.log('Initialising WASM...');
await beeSdkInit({ module_or_path: wasmBuf });
console.log('WASM ready\n');

console.log('Resolving wallet address for "raghul"...');
const walletAddr = await get_wallet_address_by_wallet_name({
  client_config: CLIENT_CONFIG,
  wallet_name: 'raghul',
});
console.log('✅ Wallet address:', walletAddr);

console.log('\nResolving PopitGame address for "raghul"...');
const popitAddr = await get_popitgame_address_by_wallet_name({
  client_config: CLIENT_CONFIG,
  wallet_name: 'raghul',
});
console.log('✅ PopitGame address:', popitAddr);
