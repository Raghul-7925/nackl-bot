/* @ts-self-types="./bee_sdk.d.ts" */

export class ActiveConnectSession {
    static __wrap(ptr) {
        const obj = Object.create(ActiveConnectSession.prototype);
        obj.__wbg_ptr = ptr;
        ActiveConnectSessionFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ActiveConnectSessionFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_activeconnectsession_free(ptr, 0);
    }
    /**
     * @returns {string | undefined}
     */
    get app_id() {
        const ret = wasm.activeconnectsession_app_id(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
    /**
     * @returns {bigint}
     */
    get deployed_at() {
        const ret = wasm.activeconnectsession_deployed_at(this.__wbg_ptr);
        return BigInt.asUintN(64, ret);
    }
    /**
     * @returns {string}
     */
    get deployed_event_id() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.activeconnectsession_deployed_event_id(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get description() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.activeconnectsession_description(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get profile_address() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.activeconnectsession_profile_address(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string | undefined}
     */
    get session_id() {
        const ret = wasm.activeconnectsession_session_id(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
}
if (Symbol.dispose) ActiveConnectSession.prototype[Symbol.dispose] = ActiveConnectSession.prototype.free;

export class BeeConnect {
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        BeeConnectFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_beeconnect_free(ptr, 0);
    }
    /**
     * Creates a `shared_key` session and returns payload + temporary owner
     * keys.
     * @param {string} app_id
     * @param {number | null} [ttl_secs]
     * @param {string | null} [nonce]
     * @returns {ResultOfCreateSharedKeySession}
     */
    create_shared_key_session(app_id, ttl_secs, nonce) {
        const ptr0 = passStringToWasm0(app_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        var ptr1 = isLikeNone(nonce) ? 0 : passStringToWasm0(nonce, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        var len1 = WASM_VECTOR_LEN;
        const ret = wasm.beeconnect_create_shared_key_session(this.__wbg_ptr, ptr0, len0, isLikeNone(ttl_secs) ? Number.MAX_SAFE_INTEGER : (ttl_secs) >>> 0, ptr1, len1);
        if (ret[2]) {
            throw takeFromExternrefTable0(ret[1]);
        }
        return ResultOfCreateSharedKeySession.__wrap(ret[0]);
    }
    /**
     * Decodes and validates base64url connect payload (`payload` query
     * value).
     * @param {string} payload_b64url
     * @returns {ParsedConnectPayload}
     */
    decode_connect_payload_b64url(payload_b64url) {
        const ptr0 = passStringToWasm0(payload_b64url, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.beeconnect_decode_connect_payload_b64url(this.__wbg_ptr, ptr0, len0);
        if (ret[2]) {
            throw takeFromExternrefTable0(ret[1]);
        }
        return ParsedConnectPayload.__wrap(ret[0]);
    }
    /**
     * Sends a `client_disconnect` message (`dir = c2w`) to the connected
     * profile. Performs DH re-key for forward secrecy.
     * @param {string[]} endpoints
     * @param {string} session_id
     * @param {string} description
     * @param {string} session_state_json
     * @param {string | null} [reason]
     * @param {number | null} [max_attempts]
     * @param {number | null} [interval_ms]
     * @returns {Promise<ResultOfDisconnectSession>}
     */
    disconnect_session(endpoints, session_id, description, session_state_json, reason, max_attempts, interval_ms) {
        const ptr0 = passArrayJsValueToWasm0(endpoints, wasm.__wbindgen_malloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(session_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ptr2 = passStringToWasm0(description, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len2 = WASM_VECTOR_LEN;
        const ptr3 = passStringToWasm0(session_state_json, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len3 = WASM_VECTOR_LEN;
        var ptr4 = isLikeNone(reason) ? 0 : passStringToWasm0(reason, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        var len4 = WASM_VECTOR_LEN;
        const ret = wasm.beeconnect_disconnect_session(this.__wbg_ptr, ptr0, len0, ptr1, len1, ptr2, len2, ptr3, len3, ptr4, len4, isLikeNone(max_attempts) ? Number.MAX_SAFE_INTEGER : (max_attempts) >>> 0, isLikeNone(interval_ms) ? Number.MAX_SAFE_INTEGER : (interval_ms) >>> 0);
        return ret;
    }
    /**
     * Returns `true` if session profile is currently deployed.
     * @param {string[]} endpoints
     * @param {string} description
     * @returns {Promise<boolean>}
     */
    is_session_profile_deployed(endpoints, description) {
        const ptr0 = passArrayJsValueToWasm0(endpoints, wasm.__wbindgen_malloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(description, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ret = wasm.beeconnect_is_session_profile_deployed(this.__wbg_ptr, ptr0, len0, ptr1, len1);
        return ret;
    }
    /**
     * Creates a new wasm-facing `bee_connect` client wrapper.
     * @param {number | null} [max_rps]
     */
    constructor(max_rps) {
        const ret = wasm.beeconnect_new(isLikeNone(max_rps) ? Number.MAX_SAFE_INTEGER : (max_rps) >>> 0);
        this.__wbg_ptr = ret;
        BeeConnectFinalization.register(this, this.__wbg_ptr, this);
        return this;
    }
    /**
     * Small health-check helper for smoke tests.
     * @returns {string}
     */
    ping() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.beeconnect_ping(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * Queries one chunk of active connect sessions by multifactor.
     *
     * Returns at most 10 deployed `bee_connect` sessions and a cursor for the
     * next chunk. Optional `app_id` filters to one application.
     * @param {string[]} endpoints
     * @param {string} multifactor_address
     * @param {string | null} [app_id]
     * @param {bigint | null} [created_at_from]
     * @param {string | null} [before]
     * @returns {Promise<ResultOfQueryActiveSessionsByMultifactor>}
     */
    query_active_sessions_by_multifactor(endpoints, multifactor_address, app_id, created_at_from, before) {
        const ptr0 = passArrayJsValueToWasm0(endpoints, wasm.__wbindgen_malloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(multifactor_address, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        var ptr2 = isLikeNone(app_id) ? 0 : passStringToWasm0(app_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        var len2 = WASM_VECTOR_LEN;
        var ptr3 = isLikeNone(before) ? 0 : passStringToWasm0(before, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        var len3 = WASM_VECTOR_LEN;
        const ret = wasm.beeconnect_query_active_sessions_by_multifactor(this.__wbg_ptr, ptr0, len0, ptr1, len1, ptr2, len2, !isLikeNone(created_at_from), isLikeNone(created_at_from) ? BigInt(0) : created_at_from, ptr3, len3);
        return ret;
    }
    /**
     * Sends `set_mining_keys` request (`dir = c2w`) to wallet over connect
     * profile. Performs DH re-key for forward secrecy.
     * @param {string[]} endpoints
     * @param {string} session_id
     * @param {string} description
     * @param {string} session_state_json
     * @param {string} app_id
     * @param {string} owner_public
     * @param {number | null} [max_attempts]
     * @param {number | null} [interval_ms]
     * @returns {Promise<ResultOfRequestSetMiningKeys>}
     */
    request_set_mining_keys(endpoints, session_id, description, session_state_json, app_id, owner_public, max_attempts, interval_ms) {
        const ptr0 = passArrayJsValueToWasm0(endpoints, wasm.__wbindgen_malloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(session_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ptr2 = passStringToWasm0(description, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len2 = WASM_VECTOR_LEN;
        const ptr3 = passStringToWasm0(session_state_json, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len3 = WASM_VECTOR_LEN;
        const ptr4 = passStringToWasm0(app_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len4 = WASM_VECTOR_LEN;
        const ptr5 = passStringToWasm0(owner_public, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len5 = WASM_VECTOR_LEN;
        const ret = wasm.beeconnect_request_set_mining_keys(this.__wbg_ptr, ptr0, len0, ptr1, len1, ptr2, len2, ptr3, len3, ptr4, len4, ptr5, len5, isLikeNone(max_attempts) ? Number.MAX_SAFE_INTEGER : (max_attempts) >>> 0, isLikeNone(interval_ms) ? Number.MAX_SAFE_INTEGER : (interval_ms) >>> 0);
        return ret;
    }
    /**
     * Sends `sign_challenge` (`dir = c2w`) to the wallet. The wallet should
     * sign the nonce and respond with `challenge_response`.
     * @param {string[]} endpoints
     * @param {string} session_id
     * @param {string} description
     * @param {string} session_state_json
     * @param {string} nonce
     * @param {number | null} [max_attempts]
     * @param {number | null} [interval_ms]
     * @returns {Promise<ResultOfRequestSignChallenge>}
     */
    request_sign_challenge(endpoints, session_id, description, session_state_json, nonce, max_attempts, interval_ms) {
        const ptr0 = passArrayJsValueToWasm0(endpoints, wasm.__wbindgen_malloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(session_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ptr2 = passStringToWasm0(description, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len2 = WASM_VECTOR_LEN;
        const ptr3 = passStringToWasm0(session_state_json, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len3 = WASM_VECTOR_LEN;
        const ptr4 = passStringToWasm0(nonce, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len4 = WASM_VECTOR_LEN;
        const ret = wasm.beeconnect_request_sign_challenge(this.__wbg_ptr, ptr0, len0, ptr1, len1, ptr2, len2, ptr3, len3, ptr4, len4, isLikeNone(max_attempts) ? Number.MAX_SAFE_INTEGER : (max_attempts) >>> 0, isLikeNone(interval_ms) ? Number.MAX_SAFE_INTEGER : (interval_ms) >>> 0);
        return ret;
    }
    /**
     * Resolves deterministic `AuthProfile` address by `description`.
     * @param {string[]} endpoints
     * @param {string} description
     * @returns {Promise<string>}
     */
    resolve_profile_address(endpoints, description) {
        const ptr0 = passArrayJsValueToWasm0(endpoints, wasm.__wbindgen_malloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(description, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ret = wasm.beeconnect_resolve_profile_address(this.__wbg_ptr, ptr0, len0, ptr1, len1);
        return ret;
    }
    /**
     * Waits for `challenge_response` (`dir = w2c`) from the wallet.
     * @param {string[]} endpoints
     * @param {string} session_id
     * @param {string} description
     * @param {string | null} [session_state_json]
     * @param {bigint | null} [created_at_from]
     * @param {number | null} [max_attempts]
     * @param {number | null} [interval_ms]
     * @returns {Promise<ResultOfWaitChallengeResponse>}
     */
    wait_challenge_response(endpoints, session_id, description, session_state_json, created_at_from, max_attempts, interval_ms) {
        const ptr0 = passArrayJsValueToWasm0(endpoints, wasm.__wbindgen_malloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(session_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ptr2 = passStringToWasm0(description, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len2 = WASM_VECTOR_LEN;
        var ptr3 = isLikeNone(session_state_json) ? 0 : passStringToWasm0(session_state_json, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        var len3 = WASM_VECTOR_LEN;
        const ret = wasm.beeconnect_wait_challenge_response(this.__wbg_ptr, ptr0, len0, ptr1, len1, ptr2, len2, ptr3, len3, !isLikeNone(created_at_from), isLikeNone(created_at_from) ? BigInt(0) : created_at_from, isLikeNone(max_attempts) ? Number.MAX_SAFE_INTEGER : (max_attempts) >>> 0, isLikeNone(interval_ms) ? Number.MAX_SAFE_INTEGER : (interval_ms) >>> 0);
        return ret;
    }
    /**
     * Waits for `set_mining_keys` request (`dir = c2w`) in session profile.
     * @param {string[]} endpoints
     * @param {string} session_id
     * @param {string} description
     * @param {bigint | null} [created_at_from]
     * @param {number | null} [max_attempts]
     * @param {number | null} [interval_ms]
     * @param {string | null} [session_state_json]
     * @returns {Promise<ResultOfWaitSetMiningKeysRequest>}
     */
    wait_set_mining_keys_request(endpoints, session_id, description, created_at_from, max_attempts, interval_ms, session_state_json) {
        const ptr0 = passArrayJsValueToWasm0(endpoints, wasm.__wbindgen_malloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(session_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ptr2 = passStringToWasm0(description, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len2 = WASM_VECTOR_LEN;
        var ptr3 = isLikeNone(session_state_json) ? 0 : passStringToWasm0(session_state_json, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        var len3 = WASM_VECTOR_LEN;
        const ret = wasm.beeconnect_wait_set_mining_keys_request(this.__wbg_ptr, ptr0, len0, ptr1, len1, ptr2, len2, !isLikeNone(created_at_from), isLikeNone(created_at_from) ? BigInt(0) : created_at_from, isLikeNone(max_attempts) ? Number.MAX_SAFE_INTEGER : (max_attempts) >>> 0, isLikeNone(interval_ms) ? Number.MAX_SAFE_INTEGER : (interval_ms) >>> 0, ptr3, len3);
        return ret;
    }
    /**
     * Waits for the wallet's first `wallet_hello` message on the profile.
     * @param {string[]} endpoints
     * @param {string} session_id
     * @param {string} description
     * @param {string} client_dh_secret
     * @param {bigint | null} [created_at_from]
     * @param {number | null} [max_attempts]
     * @param {number | null} [interval_ms]
     * @returns {Promise<ResultOfWaitWalletHello>}
     */
    wait_wallet_hello(endpoints, session_id, description, client_dh_secret, created_at_from, max_attempts, interval_ms) {
        const ptr0 = passArrayJsValueToWasm0(endpoints, wasm.__wbindgen_malloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(session_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ptr2 = passStringToWasm0(description, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len2 = WASM_VECTOR_LEN;
        const ptr3 = passStringToWasm0(client_dh_secret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len3 = WASM_VECTOR_LEN;
        const ret = wasm.beeconnect_wait_wallet_hello(this.__wbg_ptr, ptr0, len0, ptr1, len1, ptr2, len2, ptr3, len3, !isLikeNone(created_at_from), isLikeNone(created_at_from) ? BigInt(0) : created_at_from, isLikeNone(max_attempts) ? Number.MAX_SAFE_INTEGER : (max_attempts) >>> 0, isLikeNone(interval_ms) ? Number.MAX_SAFE_INTEGER : (interval_ms) >>> 0);
        return ret;
    }
}
if (Symbol.dispose) BeeConnect.prototype[Symbol.dispose] = BeeConnect.prototype.free;

/**
 * High-level wasm API for crypto operations.
 */
export class Crypto {
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        CryptoFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_crypto_free(ptr, 0);
    }
    /**
     * Decrypts data previously encrypted with `encrypt`.
     * @param {string} encrypted
     * @param {string} password
     * @returns {Promise<string>}
     */
    decrypt(encrypted, password) {
        const ptr0 = passStringToWasm0(encrypted, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(password, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ret = wasm.crypto_decrypt(this.__wbg_ptr, ptr0, len0, ptr1, len1);
        return ret;
    }
    /**
     * Encrypts plaintext with a password.
     * @param {string} plaintext
     * @param {string} password
     * @returns {Promise<CryptoResultOfEncrypt>}
     */
    encrypt(plaintext, password) {
        const ptr0 = passStringToWasm0(plaintext, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(password, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ret = wasm.crypto_encrypt(this.__wbg_ptr, ptr0, len0, ptr1, len1);
        return ret;
    }
    /**
     * Generates a short-lived mining keypair.
     * @returns {Promise<CryptoResultOfGetKeys>}
     */
    gen_mining_keys() {
        const ret = wasm.crypto_gen_mining_keys(this.__wbg_ptr);
        return ret;
    }
    /**
     * Generates 24-word mnemonic and derives keys from it.
     * @returns {Promise<CryptoResultOfGenSeedAndKeys>}
     */
    gen_mnemonic_and_derive_keys() {
        const ret = wasm.crypto_gen_mnemonic_and_derive_keys(this.__wbg_ptr);
        return ret;
    }
    /**
     * Derives keys from a mnemonic phrase.
     * @param {string} phrase
     * @returns {Promise<CryptoResultOfGetKeys>}
     */
    get_keys_from_mnemonic(phrase) {
        const ptr0 = passStringToWasm0(phrase, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.crypto_get_keys_from_mnemonic(this.__wbg_ptr, ptr0, len0);
        return ret;
    }
    /**
     * Derives keys from a mnemonic phrase using a specific HD derivation path.
     * @param {string} phrase
     * @param {string} path
     * @returns {Promise<CryptoResultOfGetKeys>}
     */
    get_keys_from_mnemonic_with_path(phrase, path) {
        const ptr0 = passStringToWasm0(phrase, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(path, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ret = wasm.crypto_get_keys_from_mnemonic_with_path(this.__wbg_ptr, ptr0, len0, ptr1, len1);
        return ret;
    }
    /**
     * Computes a salted password hash in `v3:<salt_hex>:<dk_hex>` format.
     * @param {string} data
     * @returns {Promise<string>}
     */
    hash_password(data) {
        const ptr0 = passStringToWasm0(data, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.crypto_hash_password(this.__wbg_ptr, ptr0, len0);
        return ret;
    }
    /**
     * Creates a crypto client bound to network endpoints.
     * @param {string[]} endpoints
     */
    constructor(endpoints) {
        const ptr0 = passArrayJsValueToWasm0(endpoints, wasm.__wbindgen_malloc);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.crypto_new(ptr0, len0);
        if (ret[2]) {
            throw takeFromExternrefTable0(ret[1]);
        }
        this.__wbg_ptr = ret[0];
        CryptoFinalization.register(this, this.__wbg_ptr, this);
        return this;
    }
    /**
     * Signs base64-encoded payload with an Ed25519 keypair.
     * @param {TParamsOfSign} params_js
     * @returns {Promise<CryptoResultOfSign>}
     */
    sign(params_js) {
        const ret = wasm.crypto_sign(this.__wbg_ptr, params_js);
        return ret;
    }
    /**
     * Verifies mnemonic checksum and format.
     * @param {string} phrase
     * @returns {Promise<boolean>}
     */
    verify_mnemonic(phrase) {
        const ptr0 = passStringToWasm0(phrase, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.crypto_verify_mnemonic(this.__wbg_ptr, ptr0, len0);
        return ret;
    }
    /**
     * Verifies a plain password against a `v2` or `v3` hash.
     * @param {string} password
     * @param {string} expected
     * @returns {Promise<boolean>}
     */
    verify_password_hash(password, expected) {
        const ptr0 = passStringToWasm0(password, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(expected, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ret = wasm.crypto_verify_password_hash(this.__wbg_ptr, ptr0, len0, ptr1, len1);
        return ret;
    }
}
if (Symbol.dispose) Crypto.prototype[Symbol.dispose] = Crypto.prototype.free;

export class CryptoResultOfEncrypt {
    static __wrap(ptr) {
        const obj = Object.create(CryptoResultOfEncrypt.prototype);
        obj.__wbg_ptr = ptr;
        CryptoResultOfEncryptFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        CryptoResultOfEncryptFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_cryptoresultofencrypt_free(ptr, 0);
    }
    /**
     * @returns {string}
     */
    get encrypted() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.cryptoresultofencrypt_encrypted(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
}
if (Symbol.dispose) CryptoResultOfEncrypt.prototype[Symbol.dispose] = CryptoResultOfEncrypt.prototype.free;

export class CryptoResultOfGenSeedAndKeys {
    static __wrap(ptr) {
        const obj = Object.create(CryptoResultOfGenSeedAndKeys.prototype);
        obj.__wbg_ptr = ptr;
        CryptoResultOfGenSeedAndKeysFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        CryptoResultOfGenSeedAndKeysFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_cryptoresultofgenseedandkeys_free(ptr, 0);
    }
    /**
     * @returns {CryptoResultOfGetKeys}
     */
    get keys() {
        const ret = wasm.cryptoresultofgenseedandkeys_keys(this.__wbg_ptr);
        return CryptoResultOfGetKeys.__wrap(ret);
    }
    /**
     * @returns {string}
     */
    get phrase() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.cryptoresultofgenseedandkeys_phrase(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
}
if (Symbol.dispose) CryptoResultOfGenSeedAndKeys.prototype[Symbol.dispose] = CryptoResultOfGenSeedAndKeys.prototype.free;

export class CryptoResultOfGetKeys {
    static __wrap(ptr) {
        const obj = Object.create(CryptoResultOfGetKeys.prototype);
        obj.__wbg_ptr = ptr;
        CryptoResultOfGetKeysFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        CryptoResultOfGetKeysFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_cryptoresultofgetkeys_free(ptr, 0);
    }
    /**
     * @returns {string}
     */
    get public() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.cryptoresultofgetkeys_public(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get secret() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.cryptoresultofgetkeys_secret(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
}
if (Symbol.dispose) CryptoResultOfGetKeys.prototype[Symbol.dispose] = CryptoResultOfGetKeys.prototype.free;

export class CryptoResultOfSign {
    static __wrap(ptr) {
        const obj = Object.create(CryptoResultOfSign.prototype);
        obj.__wbg_ptr = ptr;
        CryptoResultOfSignFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        CryptoResultOfSignFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_cryptoresultofsign_free(ptr, 0);
    }
    /**
     * @returns {string}
     */
    get signature() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.cryptoresultofsign_signature(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get signed() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.cryptoresultofsign_signed(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
}
if (Symbol.dispose) CryptoResultOfSign.prototype[Symbol.dispose] = CryptoResultOfSign.prototype.free;

export class GraphqlBlockData {
    static __wrap(ptr) {
        const obj = Object.create(GraphqlBlockData.prototype);
        obj.__wbg_ptr = ptr;
        GraphqlBlockDataFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        GraphqlBlockDataFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_graphqlblockdata_free(ptr, 0);
    }
    /**
     * @returns {bigint}
     */
    get seq_no() {
        const ret = wasm.__wbg_get_graphqlblockdata_seq_no(this.__wbg_ptr);
        return BigInt.asUintN(64, ret);
    }
    /**
     * @param {bigint} arg0
     */
    set seq_no(arg0) {
        wasm.__wbg_set_graphqlblockdata_seq_no(this.__wbg_ptr, arg0);
    }
}
if (Symbol.dispose) GraphqlBlockData.prototype[Symbol.dispose] = GraphqlBlockData.prototype.free;

export class Miner {
    static __wrap(ptr) {
        const obj = Object.create(Miner.prototype);
        obj.__wbg_ptr = ptr;
        MinerFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        MinerFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_miner_free(ptr, 0);
    }
    /**
     * @param {number} x
     * @param {number} y
     */
    add_tap(x, y) {
        const ret = wasm.miner_add_tap(this.__wbg_ptr, x, y);
        if (ret[1]) {
            throw takeFromExternrefTable0(ret[0]);
        }
    }
    /**
     * @returns {boolean}
     */
    can_start() {
        const ret = wasm.miner_can_start(this.__wbg_ptr);
        return ret !== 0;
    }
    /**
     * @returns {Promise<GraphqlBlockData>}
     */
    get_current_block() {
        const ret = wasm.miner_get_current_block(this.__wbg_ptr);
        return ret;
    }
    /**
     * @returns {Promise<MinerAccountData>}
     */
    get_miner_data() {
        const ret = wasm.miner_get_miner_data(this.__wbg_ptr);
        return ret;
    }
    /**
     * @returns {Promise<void>}
     */
    get_reward() {
        const ret = wasm.miner_get_reward(this.__wbg_ptr);
        return ret;
    }
    /**
     * @param {string[]} endpoints
     * @param {string} app_id
     * @param {string} address
     * @param {string} public_key
     * @param {string} secret_key
     * @returns {Promise<Miner>}
     */
    static new(endpoints, app_id, address, public_key, secret_key) {
        const ptr0 = passArrayJsValueToWasm0(endpoints, wasm.__wbindgen_malloc);
        const len0 = WASM_VECTOR_LEN;
        const ptr1 = passStringToWasm0(app_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len1 = WASM_VECTOR_LEN;
        const ptr2 = passStringToWasm0(address, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len2 = WASM_VECTOR_LEN;
        const ptr3 = passStringToWasm0(public_key, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len3 = WASM_VECTOR_LEN;
        const ptr4 = passStringToWasm0(secret_key, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len4 = WASM_VECTOR_LEN;
        const ret = wasm.miner_new(ptr0, len0, ptr1, len1, ptr2, len2, ptr3, len3, ptr4, len4);
        return ret;
    }
    /**
     * @param {string} seed
     */
    remove_seed(seed) {
        const ptr0 = passStringToWasm0(seed, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
        const len0 = WASM_VECTOR_LEN;
        wasm.miner_remove_seed(this.__wbg_ptr, ptr0, len0);
    }
    /**
     * @param {number} duration_ms
     * @param {Function} callback
     */
    start(duration_ms, callback) {
        const ret = wasm.miner_start(this.__wbg_ptr, duration_ms, callback);
        if (ret[1]) {
            throw takeFromExternrefTable0(ret[0]);
        }
    }
    stop() {
        wasm.miner_stop(this.__wbg_ptr);
    }
}
if (Symbol.dispose) Miner.prototype[Symbol.dispose] = Miner.prototype.free;

export class MinerAccountData {
    static __wrap(ptr) {
        const obj = Object.create(MinerAccountData.prototype);
        obj.__wbg_ptr = ptr;
        MinerAccountDataFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        MinerAccountDataFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_mineraccountdata_free(ptr, 0);
    }
    /**
     * @returns {bigint}
     */
    get epoch_5m_start() {
        const ret = wasm.__wbg_get_mineraccountdata_epoch_5m_start(this.__wbg_ptr);
        return BigInt.asUintN(64, ret);
    }
    /**
     * @returns {bigint}
     */
    get epoch_start() {
        const ret = wasm.__wbg_get_mineraccountdata_epoch_start(this.__wbg_ptr);
        return BigInt.asUintN(64, ret);
    }
    /**
     * @returns {bigint}
     */
    get tap_sum_5m() {
        const ret = wasm.__wbg_get_mineraccountdata_tap_sum_5m(this.__wbg_ptr);
        return (BigInt.asUintN(64, ret[0]) | (BigInt.asUintN(64, ret[1]) << BigInt(64)));
    }
    /**
     * @returns {bigint}
     */
    get tap_sum() {
        const ret = wasm.__wbg_get_mineraccountdata_tap_sum(this.__wbg_ptr);
        return (BigInt.asUintN(64, ret[0]) | (BigInt.asUintN(64, ret[1]) << BigInt(64)));
    }
    /**
     * @param {bigint} arg0
     */
    set epoch_5m_start(arg0) {
        wasm.__wbg_set_mineraccountdata_epoch_5m_start(this.__wbg_ptr, arg0);
    }
    /**
     * @param {bigint} arg0
     */
    set epoch_start(arg0) {
        wasm.__wbg_set_mineraccountdata_epoch_start(this.__wbg_ptr, arg0);
    }
    /**
     * @param {bigint} arg0
     */
    set tap_sum_5m(arg0) {
        wasm.__wbg_set_mineraccountdata_tap_sum_5m(this.__wbg_ptr, arg0, arg0 >> BigInt(64));
    }
    /**
     * @param {bigint} arg0
     */
    set tap_sum(arg0) {
        wasm.__wbg_set_mineraccountdata_tap_sum(this.__wbg_ptr, arg0, arg0 >> BigInt(64));
    }
}
if (Symbol.dispose) MinerAccountData.prototype[Symbol.dispose] = MinerAccountData.prototype.free;

export class ParsedConnectPayload {
    static __wrap(ptr) {
        const obj = Object.create(ParsedConnectPayload.prototype);
        obj.__wbg_ptr = ptr;
        ParsedConnectPayloadFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ParsedConnectPayloadFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_parsedconnectpayload_free(ptr, 0);
    }
    /**
     * @returns {string}
     */
    get app_id() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.parsedconnectpayload_app_id(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get description() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.parsedconnectpayload_description(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {bigint}
     */
    get expires_at() {
        const ret = wasm.parsedconnectpayload_expires_at(this.__wbg_ptr);
        return BigInt.asUintN(64, ret);
    }
    /**
     * @returns {string | undefined}
     */
    get nonce() {
        const ret = wasm.parsedconnectpayload_nonce(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
    /**
     * @returns {string}
     */
    get session_id() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.parsedconnectpayload_session_id(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get v() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.parsedconnectpayload_v(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
}
if (Symbol.dispose) ParsedConnectPayload.prototype[Symbol.dispose] = ParsedConnectPayload.prototype.free;

export class ResultOfCreateSharedKeySession {
    static __wrap(ptr) {
        const obj = Object.create(ResultOfCreateSharedKeySession.prototype);
        obj.__wbg_ptr = ptr;
        ResultOfCreateSharedKeySessionFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ResultOfCreateSharedKeySessionFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_resultofcreatesharedkeysession_free(ptr, 0);
    }
    /**
     * @returns {string}
     */
    get app_id() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofcreatesharedkeysession_app_id(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get client_dh_public() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofcreatesharedkeysession_client_dh_public(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get client_dh_secret() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofcreatesharedkeysession_client_dh_secret(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {bigint}
     */
    get created_at() {
        const ret = wasm.resultofcreatesharedkeysession_created_at(this.__wbg_ptr);
        return BigInt.asUintN(64, ret);
    }
    /**
     * @returns {string}
     */
    get deep_link() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofcreatesharedkeysession_deep_link(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get description() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofcreatesharedkeysession_description(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {bigint}
     */
    get expires_at() {
        const ret = wasm.resultofcreatesharedkeysession_expires_at(this.__wbg_ptr);
        return BigInt.asUintN(64, ret);
    }
    /**
     * @returns {string}
     */
    get payload_b64url() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofcreatesharedkeysession_payload_b64url(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get payload_json() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofcreatesharedkeysession_payload_json(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get session_id() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofcreatesharedkeysession_session_id(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
}
if (Symbol.dispose) ResultOfCreateSharedKeySession.prototype[Symbol.dispose] = ResultOfCreateSharedKeySession.prototype.free;

export class ResultOfDisconnectSession {
    static __wrap(ptr) {
        const obj = Object.create(ResultOfDisconnectSession.prototype);
        obj.__wbg_ptr = ptr;
        ResultOfDisconnectSessionFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ResultOfDisconnectSessionFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_resultofdisconnectsession_free(ptr, 0);
    }
    /**
     * @returns {string | undefined}
     */
    get message_id() {
        const ret = wasm.resultofdisconnectsession_message_id(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
    /**
     * @returns {string}
     */
    get profile_address() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofdisconnectsession_profile_address(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get raw_message_json() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofdisconnectsession_raw_message_json(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get updated_session_state_json() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofdisconnectsession_updated_session_state_json(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
}
if (Symbol.dispose) ResultOfDisconnectSession.prototype[Symbol.dispose] = ResultOfDisconnectSession.prototype.free;

export class ResultOfGenMiningKeys {
    static __wrap(ptr) {
        const obj = Object.create(ResultOfGenMiningKeys.prototype);
        obj.__wbg_ptr = ptr;
        ResultOfGenMiningKeysFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ResultOfGenMiningKeysFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_resultofgenminingkeys_free(ptr, 0);
    }
    /**
     * @returns {string}
     */
    get deep_link() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofgenminingkeys_deep_link(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get public() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofgenminingkeys_public(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get secret() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofgenminingkeys_secret(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
}
if (Symbol.dispose) ResultOfGenMiningKeys.prototype[Symbol.dispose] = ResultOfGenMiningKeys.prototype.free;

export class ResultOfQueryActiveSessionsByMultifactor {
    static __wrap(ptr) {
        const obj = Object.create(ResultOfQueryActiveSessionsByMultifactor.prototype);
        obj.__wbg_ptr = ptr;
        ResultOfQueryActiveSessionsByMultifactorFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ResultOfQueryActiveSessionsByMultifactorFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_resultofqueryactivesessionsbymultifactor_free(ptr, 0);
    }
    /**
     * @returns {boolean}
     */
    get exhausted_active() {
        const ret = wasm.resultofqueryactivesessionsbymultifactor_exhausted_active(this.__wbg_ptr);
        return ret !== 0;
    }
    /**
     * @returns {string | undefined}
     */
    get next_before() {
        const ret = wasm.resultofqueryactivesessionsbymultifactor_next_before(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
    /**
     * @returns {Array<any>}
     */
    get sessions() {
        const ret = wasm.resultofqueryactivesessionsbymultifactor_sessions(this.__wbg_ptr);
        return ret;
    }
}
if (Symbol.dispose) ResultOfQueryActiveSessionsByMultifactor.prototype[Symbol.dispose] = ResultOfQueryActiveSessionsByMultifactor.prototype.free;

export class ResultOfRequestSetMiningKeys {
    static __wrap(ptr) {
        const obj = Object.create(ResultOfRequestSetMiningKeys.prototype);
        obj.__wbg_ptr = ptr;
        ResultOfRequestSetMiningKeysFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ResultOfRequestSetMiningKeysFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_resultofrequestsetminingkeys_free(ptr, 0);
    }
    /**
     * @returns {string}
     */
    get app_id() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofrequestsetminingkeys_app_id(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string | undefined}
     */
    get message_id() {
        const ret = wasm.resultofrequestsetminingkeys_message_id(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
    /**
     * @returns {string}
     */
    get owner_public() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofrequestsetminingkeys_owner_public(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get profile_address() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofrequestsetminingkeys_profile_address(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get raw_message_json() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofrequestsetminingkeys_raw_message_json(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get updated_session_state_json() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofrequestsetminingkeys_updated_session_state_json(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
}
if (Symbol.dispose) ResultOfRequestSetMiningKeys.prototype[Symbol.dispose] = ResultOfRequestSetMiningKeys.prototype.free;

export class ResultOfRequestSignChallenge {
    static __wrap(ptr) {
        const obj = Object.create(ResultOfRequestSignChallenge.prototype);
        obj.__wbg_ptr = ptr;
        ResultOfRequestSignChallengeFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ResultOfRequestSignChallengeFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_resultofrequestsignchallenge_free(ptr, 0);
    }
    /**
     * @returns {string | undefined}
     */
    get message_id() {
        const ret = wasm.resultofrequestsignchallenge_message_id(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
    /**
     * @returns {string}
     */
    get nonce() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofrequestsignchallenge_nonce(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get profile_address() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofrequestsignchallenge_profile_address(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get raw_message_json() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofrequestsignchallenge_raw_message_json(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {bigint}
     */
    get sent_at() {
        const ret = wasm.resultofrequestsignchallenge_sent_at(this.__wbg_ptr);
        return BigInt.asUintN(64, ret);
    }
    /**
     * @returns {string}
     */
    get updated_session_state_json() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofrequestsignchallenge_updated_session_state_json(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
}
if (Symbol.dispose) ResultOfRequestSignChallenge.prototype[Symbol.dispose] = ResultOfRequestSignChallenge.prototype.free;

export class ResultOfWaitChallengeResponse {
    static __wrap(ptr) {
        const obj = Object.create(ResultOfWaitChallengeResponse.prototype);
        obj.__wbg_ptr = ptr;
        ResultOfWaitChallengeResponseFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ResultOfWaitChallengeResponseFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_resultofwaitchallengeresponse_free(ptr, 0);
    }
    /**
     * @returns {string | undefined}
     */
    get epk_public() {
        const ret = wasm.resultofwaitchallengeresponse_epk_public(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
    /**
     * @returns {bigint}
     */
    get event_created_at() {
        const ret = wasm.resultofwaitchallengeresponse_event_created_at(this.__wbg_ptr);
        return BigInt.asUintN(64, ret);
    }
    /**
     * @returns {string}
     */
    get event_id() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitchallengeresponse_event_id(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get nonce() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitchallengeresponse_nonce(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get profile_address() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitchallengeresponse_profile_address(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get raw_message_json() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitchallengeresponse_raw_message_json(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get signature() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitchallengeresponse_signature(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string | undefined}
     */
    get updated_session_state_json() {
        const ret = wasm.resultofwaitchallengeresponse_updated_session_state_json(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
    /**
     * @returns {string}
     */
    get wallet_address() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitchallengeresponse_wallet_address(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
}
if (Symbol.dispose) ResultOfWaitChallengeResponse.prototype[Symbol.dispose] = ResultOfWaitChallengeResponse.prototype.free;

export class ResultOfWaitSetMiningKeysRequest {
    static __wrap(ptr) {
        const obj = Object.create(ResultOfWaitSetMiningKeysRequest.prototype);
        obj.__wbg_ptr = ptr;
        ResultOfWaitSetMiningKeysRequestFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ResultOfWaitSetMiningKeysRequestFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_resultofwaitsetminingkeysrequest_free(ptr, 0);
    }
    /**
     * @returns {string}
     */
    get app_id() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitsetminingkeysrequest_app_id(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {bigint}
     */
    get event_created_at() {
        const ret = wasm.resultofwaitsetminingkeysrequest_event_created_at(this.__wbg_ptr);
        return BigInt.asUintN(64, ret);
    }
    /**
     * @returns {string}
     */
    get event_id() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitsetminingkeysrequest_event_id(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get owner_public() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitsetminingkeysrequest_owner_public(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get profile_address() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitsetminingkeysrequest_profile_address(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get raw_message_json() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitsetminingkeysrequest_raw_message_json(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string | undefined}
     */
    get updated_session_state_json() {
        const ret = wasm.resultofwaitsetminingkeysrequest_updated_session_state_json(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
}
if (Symbol.dispose) ResultOfWaitSetMiningKeysRequest.prototype[Symbol.dispose] = ResultOfWaitSetMiningKeysRequest.prototype.free;

export class ResultOfWaitWalletHello {
    static __wrap(ptr) {
        const obj = Object.create(ResultOfWaitWalletHello.prototype);
        obj.__wbg_ptr = ptr;
        ResultOfWaitWalletHelloFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }
    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ResultOfWaitWalletHelloFinalization.unregister(this);
        return ptr;
    }
    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_resultofwaitwallethello_free(ptr, 0);
    }
    /**
     * @returns {string | undefined}
     */
    get epk_public() {
        const ret = wasm.resultofwaitwallethello_epk_public(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
    /**
     * @returns {bigint}
     */
    get event_created_at() {
        const ret = wasm.resultofwaitwallethello_event_created_at(this.__wbg_ptr);
        return BigInt.asUintN(64, ret);
    }
    /**
     * @returns {string}
     */
    get event_id() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitwallethello_event_id(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string | undefined}
     */
    get nonce() {
        const ret = wasm.resultofwaitwallethello_nonce(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
    /**
     * @returns {string}
     */
    get profile_address() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitwallethello_profile_address(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get raw_message_json() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitwallethello_raw_message_json(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get session_state_json() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitwallethello_session_state_json(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string | undefined}
     */
    get signature() {
        const ret = wasm.resultofwaitwallethello_signature(this.__wbg_ptr);
        let v1;
        if (ret[0] !== 0) {
            v1 = getStringFromWasm0(ret[0], ret[1]).slice();
            wasm.__wbindgen_free(ret[0], ret[1] * 1, 1);
        }
        return v1;
    }
    /**
     * @returns {string}
     */
    get wallet_address() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitwallethello_wallet_address(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get wallet_name() {
        let deferred1_0;
        let deferred1_1;
        try {
            const ret = wasm.resultofwaitwallethello_wallet_name(this.__wbg_ptr);
            deferred1_0 = ret[0];
            deferred1_1 = ret[1];
            return getStringFromWasm0(ret[0], ret[1]);
        } finally {
            wasm.__wbindgen_free(deferred1_0, deferred1_1, 1);
        }
    }
}
if (Symbol.dispose) ResultOfWaitWalletHello.prototype[Symbol.dispose] = ResultOfWaitWalletHello.prototype.free;

/**
 * @param {TParamsOfEnsureMiningKeysPropagated} params
 * @returns {Promise<void>}
 */
export function ensure_mining_keys_propagated(params) {
    const ret = wasm.ensure_mining_keys_propagated(params);
    return ret;
}

/**
 * @param {string} app_id
 * @returns {Promise<ResultOfGenMiningKeys>}
 */
export function gen_mining_keys(app_id) {
    const ptr0 = passStringToWasm0(app_id, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
    const len0 = WASM_VECTOR_LEN;
    const ret = wasm.gen_mining_keys(ptr0, len0);
    return ret;
}

/**
 * @param {TParamsOfGetMinerAddressByWalletName} params
 * @returns {Promise<string>}
 */
export function get_miner_address_by_wallet_name(params) {
    const ret = wasm.get_miner_address_by_wallet_name(params);
    return ret;
}

/**
 * @param {TParamsOfGetPopitgameAddressByWalletName} params
 * @returns {Promise<string>}
 */
export function get_popitgame_address_by_wallet_name(params) {
    const ret = wasm.get_popitgame_address_by_wallet_name(params);
    return ret;
}

/**
 * @param {TParamsOfGetWalletAddressByWalletName} params
 * @returns {Promise<string>}
 */
export function get_wallet_address_by_wallet_name(params) {
    const ret = wasm.get_wallet_address_by_wallet_name(params);
    return ret;
}
function __wbg_get_imports() {
    const import0 = {
        __proto__: null,
        __wbg_Error_fdd633d4bb5dd76a: function(arg0, arg1) {
            const ret = Error(getStringFromWasm0(arg0, arg1));
            return ret;
        },
        __wbg_Number_c4bdf66bb78f7977: function(arg0) {
            const ret = Number(arg0);
            return ret;
        },
        __wbg_String_8564e559799eccda: function(arg0, arg1) {
            const ret = String(arg1);
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg_Window_6b1e5e30561398b0: function(arg0) {
            const ret = arg0.Window;
            return ret;
        },
        __wbg_WorkerGlobalScope_c2be21ef9cc5eb0e: function(arg0) {
            const ret = arg0.WorkerGlobalScope;
            return ret;
        },
        __wbg___wbindgen_bigint_get_as_i64_d9e915702856f831: function(arg0, arg1) {
            const v = arg1;
            const ret = typeof(v) === 'bigint' ? v : undefined;
            getDataViewMemory0().setBigInt64(arg0 + 8 * 1, isLikeNone(ret) ? BigInt(0) : ret, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, !isLikeNone(ret), true);
        },
        __wbg___wbindgen_boolean_get_edaed31a367ce1bd: function(arg0) {
            const v = arg0;
            const ret = typeof(v) === 'boolean' ? v : undefined;
            return isLikeNone(ret) ? 0xFFFFFF : ret ? 1 : 0;
        },
        __wbg___wbindgen_debug_string_8a447059637473e2: function(arg0, arg1) {
            const ret = debugString(arg1);
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg___wbindgen_in_4990f46af709e33c: function(arg0, arg1) {
            const ret = arg0 in arg1;
            return ret;
        },
        __wbg___wbindgen_is_bigint_90b5ccfe67c78460: function(arg0) {
            const ret = typeof(arg0) === 'bigint';
            return ret;
        },
        __wbg___wbindgen_is_function_acc5528be2b923f2: function(arg0) {
            const ret = typeof(arg0) === 'function';
            return ret;
        },
        __wbg___wbindgen_is_object_0beba4a1980d3eea: function(arg0) {
            const val = arg0;
            const ret = typeof(val) === 'object' && val !== null;
            return ret;
        },
        __wbg___wbindgen_is_string_1fca8072260dd261: function(arg0) {
            const ret = typeof(arg0) === 'string';
            return ret;
        },
        __wbg___wbindgen_is_undefined_721f8decd50c87a3: function(arg0) {
            const ret = arg0 === undefined;
            return ret;
        },
        __wbg___wbindgen_jsval_eq_4e8c38722cb8ff51: function(arg0, arg1) {
            const ret = arg0 === arg1;
            return ret;
        },
        __wbg___wbindgen_jsval_loose_eq_4b9aba9e5b3c4582: function(arg0, arg1) {
            const ret = arg0 == arg1;
            return ret;
        },
        __wbg___wbindgen_number_get_1cc01dd708740256: function(arg0, arg1) {
            const obj = arg1;
            const ret = typeof(obj) === 'number' ? obj : undefined;
            getDataViewMemory0().setFloat64(arg0 + 8 * 1, isLikeNone(ret) ? 0 : ret, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, !isLikeNone(ret), true);
        },
        __wbg___wbindgen_string_get_71bb4348194e31f0: function(arg0, arg1) {
            const obj = arg1;
            const ret = typeof(obj) === 'string' ? obj : undefined;
            var ptr1 = isLikeNone(ret) ? 0 : passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            var len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg___wbindgen_throw_ea4887a5f8f9a9db: function(arg0, arg1) {
            throw new Error(getStringFromWasm0(arg0, arg1));
        },
        __wbg__wbg_cb_unref_33c39e13d73b25f6: function(arg0) {
            arg0._wbg_cb_unref();
        },
        __wbg_activeconnectsession_new: function(arg0) {
            const ret = ActiveConnectSession.__wrap(arg0);
            return ret;
        },
        __wbg_buffer_9e4d98d0766fb908: function(arg0) {
            const ret = arg0.buffer;
            return ret;
        },
        __wbg_call_5575218572ead796: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.call(arg1, arg2);
            return ret;
        }, arguments); },
        __wbg_call_8e98ed2f3c86c4b5: function() { return handleError(function (arg0, arg1) {
            const ret = arg0.call(arg1);
            return ret;
        }, arguments); },
        __wbg_clearTimeout_113b1cde814ec762: function(arg0) {
            const ret = clearTimeout(arg0);
            return ret;
        },
        __wbg_clearTimeout_ef73c3ecbb0ece69: function(arg0, arg1) {
            arg0.clearTimeout(arg1);
        },
        __wbg_close_26aa343c0d729303: function() { return handleError(function (arg0) {
            arg0.close();
        }, arguments); },
        __wbg_createObjectStore_6c2399b0dc59f473: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.createObjectStore(getStringFromWasm0(arg1, arg2));
            return ret;
        }, arguments); },
        __wbg_crypto_38df2bab126b63dc: function(arg0) {
            const ret = arg0.crypto;
            return ret;
        },
        __wbg_cryptoresultofencrypt_new: function(arg0) {
            const ret = CryptoResultOfEncrypt.__wrap(arg0);
            return ret;
        },
        __wbg_cryptoresultofgenseedandkeys_new: function(arg0) {
            const ret = CryptoResultOfGenSeedAndKeys.__wrap(arg0);
            return ret;
        },
        __wbg_cryptoresultofgetkeys_new: function(arg0) {
            const ret = CryptoResultOfGetKeys.__wrap(arg0);
            return ret;
        },
        __wbg_cryptoresultofsign_new: function(arg0) {
            const ret = CryptoResultOfSign.__wrap(arg0);
            return ret;
        },
        __wbg_data_4a7f1308dbd33a21: function(arg0) {
            const ret = arg0.data;
            return ret;
        },
        __wbg_debug_efaf8c48cff2394a: function(arg0) {
            console.debug(arg0);
        },
        __wbg_deriveBits_fc504382590b3ccb: function() { return handleError(function (arg0, arg1, arg2, arg3) {
            const ret = arg0.deriveBits(arg1, arg2, arg3 >>> 0);
            return ret;
        }, arguments); },
        __wbg_done_b62d4a7d2286852a: function(arg0) {
            const ret = arg0.done;
            return ret;
        },
        __wbg_entries_c261c3fa1f281256: function(arg0) {
            const ret = Object.entries(arg0);
            return ret;
        },
        __wbg_error_2730901eef46e484: function() { return handleError(function (arg0) {
            const ret = arg0.error;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        }, arguments); },
        __wbg_error_933f449d72fef598: function(arg0) {
            console.error(arg0);
        },
        __wbg_error_a6fa202b58aa1cd3: function(arg0, arg1) {
            let deferred0_0;
            let deferred0_1;
            try {
                deferred0_0 = arg0;
                deferred0_1 = arg1;
                console.error(getStringFromWasm0(arg0, arg1));
            } finally {
                wasm.__wbindgen_free(deferred0_0, deferred0_1, 1);
            }
        },
        __wbg_fetch_e1ba8bc3c3cb9640: function(arg0, arg1) {
            const ret = arg0.fetch(arg1);
            return ret;
        },
        __wbg_getRandomValues_3f44b700395062e5: function() { return handleError(function (arg0, arg1) {
            globalThis.crypto.getRandomValues(getArrayU8FromWasm0(arg0, arg1));
        }, arguments); },
        __wbg_getRandomValues_c44a50d8cfdaebeb: function() { return handleError(function (arg0, arg1) {
            arg0.getRandomValues(arg1);
        }, arguments); },
        __wbg_getTime_7a770f8a2ec8d634: function(arg0) {
            const ret = arg0.getTime();
            return ret;
        },
        __wbg_getTimezoneOffset_d6fba5332f80c3da: function(arg0) {
            const ret = arg0.getTimezoneOffset();
            return ret;
        },
        __wbg_get_197a3fe98f169e38: function(arg0, arg1) {
            const ret = arg0[arg1 >>> 0];
            return ret;
        },
        __wbg_get_9a29be2cb383ed9a: function() { return handleError(function (arg0, arg1) {
            const ret = Reflect.get(arg0, arg1);
            return ret;
        }, arguments); },
        __wbg_get_cc81af70c9fceaea: function() { return handleError(function (arg0, arg1) {
            const ret = arg0.get(arg1);
            return ret;
        }, arguments); },
        __wbg_get_dddb90ff5d27a080: function() { return handleError(function (arg0, arg1) {
            const ret = Reflect.get(arg0, arg1);
            return ret;
        }, arguments); },
        __wbg_get_unchecked_54a4374c38e08460: function(arg0, arg1) {
            const ret = arg0[arg1 >>> 0];
            return ret;
        },
        __wbg_get_with_ref_key_6412cf3094599694: function(arg0, arg1) {
            const ret = arg0[arg1];
            return ret;
        },
        __wbg_global_deb18d05f75c643d: function(arg0) {
            const ret = arg0.global;
            return ret;
        },
        __wbg_graphqlblockdata_new: function(arg0) {
            const ret = GraphqlBlockData.__wrap(arg0);
            return ret;
        },
        __wbg_headers_59a5fd80651dd721: function(arg0) {
            const ret = arg0.headers;
            return ret;
        },
        __wbg_importKey_0713cd74ebe2bf89: function() { return handleError(function (arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7) {
            const ret = arg0.importKey(getStringFromWasm0(arg1, arg2), arg3, getStringFromWasm0(arg4, arg5), arg6 !== 0, arg7);
            return ret;
        }, arguments); },
        __wbg_indexedDB_24a7a59b7e7d76f2: function() { return handleError(function (arg0) {
            const ret = arg0.indexedDB;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        }, arguments); },
        __wbg_indexedDB_66709c81db8a4d72: function() { return handleError(function (arg0) {
            const ret = arg0.indexedDB;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        }, arguments); },
        __wbg_indexedDB_6d53c9cf3d668233: function() { return handleError(function (arg0) {
            const ret = arg0.indexedDB;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        }, arguments); },
        __wbg_instanceof_ArrayBuffer_2a7bb09fee70c2da: function(arg0) {
            let result;
            try {
                result = arg0 instanceof ArrayBuffer;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_Error_77d0cf0b4f31a32f: function(arg0) {
            let result;
            try {
                result = arg0 instanceof Error;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_Response_79948c98d1d2ba75: function(arg0) {
            let result;
            try {
                result = arg0 instanceof Response;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_Uint8Array_f080092dc70f5d58: function(arg0) {
            let result;
            try {
                result = arg0 instanceof Uint8Array;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_instanceof_Window_0d356b88a2f77c42: function(arg0) {
            let result;
            try {
                result = arg0 instanceof Window;
            } catch (_) {
                result = false;
            }
            const ret = result;
            return ret;
        },
        __wbg_isArray_145a34fd0a38d37b: function(arg0) {
            const ret = Array.isArray(arg0);
            return ret;
        },
        __wbg_isSafeInteger_a3389a198582f5f6: function(arg0) {
            const ret = Number.isSafeInteger(arg0);
            return ret;
        },
        __wbg_item_ad4cc2762866f069: function(arg0, arg1, arg2) {
            const ret = arg1.item(arg2 >>> 0);
            var ptr1 = isLikeNone(ret) ? 0 : passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            var len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg_iterator_cc47ba25a2be735a: function() {
            const ret = Symbol.iterator;
            return ret;
        },
        __wbg_length_589238bdcf171f0e: function(arg0) {
            const ret = arg0.length;
            return ret;
        },
        __wbg_length_c6054974c0a6cdb9: function(arg0) {
            const ret = arg0.length;
            return ret;
        },
        __wbg_message_6fc0a1f59fcc247b: function(arg0) {
            const ret = arg0.message;
            return ret;
        },
        __wbg_message_bc855ffd1f7f1de1: function(arg0, arg1) {
            const ret = arg1.message;
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg_miner_new: function(arg0) {
            const ret = Miner.__wrap(arg0);
            return ret;
        },
        __wbg_mineraccountdata_new: function(arg0) {
            const ret = MinerAccountData.__wrap(arg0);
            return ret;
        },
        __wbg_msCrypto_bd5a034af96bcba6: function(arg0) {
            const ret = arg0.msCrypto;
            return ret;
        },
        __wbg_new_0_1b32bedde98fef4b: function() {
            const ret = new Date();
            return ret;
        },
        __wbg_new_227d7c05414eb861: function() {
            const ret = new Error();
            return ret;
        },
        __wbg_new_2e117a478906f062: function() {
            const ret = new Object();
            return ret;
        },
        __wbg_new_36e147a8ced3c6e0: function() {
            const ret = new Array();
            return ret;
        },
        __wbg_new_47ab770c8bd3b6bb: function(arg0) {
            const ret = new Date(arg0);
            return ret;
        },
        __wbg_new_5a19eef57e9178b5: function() { return handleError(function (arg0, arg1) {
            const ret = new WebSocket(getStringFromWasm0(arg0, arg1));
            return ret;
        }, arguments); },
        __wbg_new_81880fb5002cb255: function(arg0) {
            const ret = new Uint8Array(arg0);
            return ret;
        },
        __wbg_new_from_slice_543b875b27789a8f: function(arg0, arg1) {
            const ret = new Uint8Array(getArrayU8FromWasm0(arg0, arg1));
            return ret;
        },
        __wbg_new_typed_00a409eb4ec4f2d9: function(arg0, arg1) {
            try {
                var state0 = {a: arg0, b: arg1};
                var cb0 = (arg0, arg1) => {
                    const a = state0.a;
                    state0.a = 0;
                    try {
                        return wasm_bindgen__convert__closures_____invoke__h3031a3aa7f6324e0(a, state0.b, arg0, arg1);
                    } finally {
                        state0.a = a;
                    }
                };
                const ret = new Promise(cb0);
                return ret;
            } finally {
                state0.a = 0;
            }
        },
        __wbg_new_with_length_9b650f44b5c44a4e: function(arg0) {
            const ret = new Uint8Array(arg0 >>> 0);
            return ret;
        },
        __wbg_new_with_str_and_init_5b299538bdeeec64: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = new Request(getStringFromWasm0(arg0, arg1), arg2);
            return ret;
        }, arguments); },
        __wbg_new_with_str_df5b9855ce14dac6: function() { return handleError(function (arg0, arg1, arg2, arg3) {
            const ret = new WebSocket(getStringFromWasm0(arg0, arg1), getStringFromWasm0(arg2, arg3));
            return ret;
        }, arguments); },
        __wbg_next_0c4066e251d2eff9: function() { return handleError(function (arg0) {
            const ret = arg0.next();
            return ret;
        }, arguments); },
        __wbg_next_402fa10b59ab20c3: function(arg0) {
            const ret = arg0.next;
            return ret;
        },
        __wbg_node_84ea875411254db1: function(arg0) {
            const ret = arg0.node;
            return ret;
        },
        __wbg_now_d2e0afbad4edbe82: function() {
            const ret = Date.now();
            return ret;
        },
        __wbg_objectStoreNames_1b3537217ff11c20: function(arg0) {
            const ret = arg0.objectStoreNames;
            return ret;
        },
        __wbg_objectStore_3468a23e50c7e125: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.objectStore(getStringFromWasm0(arg1, arg2));
            return ret;
        }, arguments); },
        __wbg_of_62183ea089c00bfa: function(arg0) {
            const ret = Array.of(arg0);
            return ret;
        },
        __wbg_open_cd413714bc9879e4: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.open(getStringFromWasm0(arg1, arg2));
            return ret;
        }, arguments); },
        __wbg_process_44c7a14e11e9f69e: function(arg0) {
            const ret = arg0.process;
            return ret;
        },
        __wbg_prototypesetcall_d721637c7ca66eb8: function(arg0, arg1, arg2) {
            Uint8Array.prototype.set.call(getArrayU8FromWasm0(arg0, arg1), arg2);
        },
        __wbg_push_f724b5db8acf89d2: function(arg0, arg1) {
            const ret = arg0.push(arg1);
            return ret;
        },
        __wbg_put_738d34320465aaf3: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.put(arg1, arg2);
            return ret;
        }, arguments); },
        __wbg_queueMicrotask_1c9b3800e321a967: function(arg0) {
            const ret = arg0.queueMicrotask;
            return ret;
        },
        __wbg_queueMicrotask_311744e534a929a3: function(arg0) {
            queueMicrotask(arg0);
        },
        __wbg_randomFillSync_6c25eac9869eb53c: function() { return handleError(function (arg0, arg1) {
            arg0.randomFillSync(arg1);
        }, arguments); },
        __wbg_random_3182549db57fb083: function() {
            const ret = Math.random();
            return ret;
        },
        __wbg_readyState_82f116ed130415ca: function(arg0) {
            const ret = arg0.readyState;
            return (__wbindgen_enum_IdbRequestReadyState.indexOf(ret) + 1 || 3) - 1;
        },
        __wbg_require_b4edbdcf3e2a1ef0: function() { return handleError(function () {
            const ret = module.require;
            return ret;
        }, arguments); },
        __wbg_resolve_d82363d90af6928a: function(arg0) {
            const ret = Promise.resolve(arg0);
            return ret;
        },
        __wbg_result_ad4d0eede558cd6c: function() { return handleError(function (arg0) {
            const ret = arg0.result;
            return ret;
        }, arguments); },
        __wbg_resultofdisconnectsession_new: function(arg0) {
            const ret = ResultOfDisconnectSession.__wrap(arg0);
            return ret;
        },
        __wbg_resultofgenminingkeys_new: function(arg0) {
            const ret = ResultOfGenMiningKeys.__wrap(arg0);
            return ret;
        },
        __wbg_resultofqueryactivesessionsbymultifactor_new: function(arg0) {
            const ret = ResultOfQueryActiveSessionsByMultifactor.__wrap(arg0);
            return ret;
        },
        __wbg_resultofrequestsetminingkeys_new: function(arg0) {
            const ret = ResultOfRequestSetMiningKeys.__wrap(arg0);
            return ret;
        },
        __wbg_resultofrequestsignchallenge_new: function(arg0) {
            const ret = ResultOfRequestSignChallenge.__wrap(arg0);
            return ret;
        },
        __wbg_resultofwaitchallengeresponse_new: function(arg0) {
            const ret = ResultOfWaitChallengeResponse.__wrap(arg0);
            return ret;
        },
        __wbg_resultofwaitsetminingkeysrequest_new: function(arg0) {
            const ret = ResultOfWaitSetMiningKeysRequest.__wrap(arg0);
            return ret;
        },
        __wbg_resultofwaitwallethello_new: function(arg0) {
            const ret = ResultOfWaitWalletHello.__wrap(arg0);
            return ret;
        },
        __wbg_send_d3ba4386db8a6937: function() { return handleError(function (arg0, arg1, arg2) {
            arg0.send(getStringFromWasm0(arg1, arg2));
        }, arguments); },
        __wbg_setTimeout_8afa0b5ed243c77d: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = arg0.setTimeout(arg1, arg2);
            return ret;
        }, arguments); },
        __wbg_setTimeout_ef24d2fc3ad97385: function() { return handleError(function (arg0, arg1) {
            const ret = setTimeout(arg0, arg1);
            return ret;
        }, arguments); },
        __wbg_set_1c87dcfd4a93c514: function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
            arg0.set(getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
        }, arguments); },
        __wbg_set_4564f7dc44fcb0c9: function() { return handleError(function (arg0, arg1, arg2) {
            const ret = Reflect.set(arg0, arg1, arg2);
            return ret;
        }, arguments); },
        __wbg_set_body_97c25d1c0051cb04: function(arg0, arg1) {
            arg0.body = arg1;
        },
        __wbg_set_method_1120482abe0934aa: function(arg0, arg1, arg2) {
            arg0.method = getStringFromWasm0(arg1, arg2);
        },
        __wbg_set_onabort_aa769067996be236: function(arg0, arg1) {
            arg0.onabort = arg1;
        },
        __wbg_set_onblocked_64124040f8494e39: function(arg0, arg1) {
            arg0.onblocked = arg1;
        },
        __wbg_set_oncomplete_56fb9939584534f1: function(arg0, arg1) {
            arg0.oncomplete = arg1;
        },
        __wbg_set_onerror_0803e0826d3abdc4: function(arg0, arg1) {
            arg0.onerror = arg1;
        },
        __wbg_set_onerror_3f68563f77d362f1: function(arg0, arg1) {
            arg0.onerror = arg1;
        },
        __wbg_set_onerror_ba8db3530f46f30a: function(arg0, arg1) {
            arg0.onerror = arg1;
        },
        __wbg_set_onmessage_397a79f643011142: function(arg0, arg1) {
            arg0.onmessage = arg1;
        },
        __wbg_set_onopen_ca8d311fe5282041: function(arg0, arg1) {
            arg0.onopen = arg1;
        },
        __wbg_set_onsuccess_2cdfe0be022e28fa: function(arg0, arg1) {
            arg0.onsuccess = arg1;
        },
        __wbg_set_onupgradeneeded_b840f47064664247: function(arg0, arg1) {
            arg0.onupgradeneeded = arg1;
        },
        __wbg_set_onversionchange_9381fdf7f68c845f: function(arg0, arg1) {
            arg0.onversionchange = arg1;
        },
        __wbg_stack_3b0d974bbf31e44f: function(arg0, arg1) {
            const ret = arg1.stack;
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg_static_accessor_GLOBAL_THIS_2fee5048bcca5938: function() {
            const ret = typeof globalThis === 'undefined' ? null : globalThis;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_static_accessor_GLOBAL_ce44e66a4935da8c: function() {
            const ret = typeof global === 'undefined' ? null : global;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_static_accessor_SELF_44f6e0cb5e67cdad: function() {
            const ret = typeof self === 'undefined' ? null : self;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_static_accessor_WINDOW_168f178805d978fe: function() {
            const ret = typeof window === 'undefined' ? null : window;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_status_0053aa6239760447: function(arg0) {
            const ret = arg0.status;
            return ret;
        },
        __wbg_stringify_747a843de2eb6359: function() { return handleError(function (arg0) {
            const ret = JSON.stringify(arg0);
            return ret;
        }, arguments); },
        __wbg_subarray_b0e8ac4ed313fea8: function(arg0, arg1, arg2) {
            const ret = arg0.subarray(arg1 >>> 0, arg2 >>> 0);
            return ret;
        },
        __wbg_subtle_1287656b3b345d44: function(arg0) {
            const ret = arg0.subtle;
            return ret;
        },
        __wbg_target_4387d5c508f1ecbd: function(arg0) {
            const ret = arg0.target;
            return isLikeNone(ret) ? 0 : addToExternrefTable0(ret);
        },
        __wbg_text_68ea00f7126f2706: function() { return handleError(function (arg0) {
            const ret = arg0.text();
            return ret;
        }, arguments); },
        __wbg_then_05edfc8a4fea5106: function(arg0, arg1, arg2) {
            const ret = arg0.then(arg1, arg2);
            return ret;
        },
        __wbg_then_591b6b3a75ee817a: function(arg0, arg1) {
            const ret = arg0.then(arg1);
            return ret;
        },
        __wbg_transaction_e1fa871de48c3ddf: function() { return handleError(function (arg0, arg1, arg2, arg3) {
            const ret = arg0.transaction(getStringFromWasm0(arg1, arg2), __wbindgen_enum_IdbTransactionMode[arg3]);
            return ret;
        }, arguments); },
        __wbg_url_0e0eeabf01fb5519: function(arg0, arg1) {
            const ret = arg1.url;
            const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_malloc, wasm.__wbindgen_realloc);
            const len1 = WASM_VECTOR_LEN;
            getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
            getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
        },
        __wbg_value_49f783bb59765962: function(arg0) {
            const ret = arg0.value;
            return ret;
        },
        __wbg_versions_276b2795b1c6a219: function(arg0) {
            const ret = arg0.versions;
            return ret;
        },
        __wbindgen_cast_0000000000000001: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [Externref], shim_idx: 144, ret: Result(Unit), inner_ret: Some(Result(Unit)) }, mutable: true }) -> Externref`.
            const ret = makeMutClosure(arg0, arg1, wasm_bindgen__convert__closures_____invoke__hca7b2218525b506f);
            return ret;
        },
        __wbindgen_cast_0000000000000002: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [Externref], shim_idx: 3474, ret: Unit, inner_ret: Some(Unit) }, mutable: true }) -> Externref`.
            const ret = makeMutClosure(arg0, arg1, wasm_bindgen__convert__closures_____invoke__h3b11c9c6f1321b37);
            return ret;
        },
        __wbindgen_cast_0000000000000003: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [NamedExternref("Event")], shim_idx: 2438, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen__convert__closures_____invoke__h56a527e5ba162cbf);
            return ret;
        },
        __wbindgen_cast_0000000000000004: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [NamedExternref("Event")], shim_idx: 3474, ret: Unit, inner_ret: Some(Unit) }, mutable: true }) -> Externref`.
            const ret = makeMutClosure(arg0, arg1, wasm_bindgen__convert__closures_____invoke__h3b11c9c6f1321b37_3);
            return ret;
        },
        __wbindgen_cast_0000000000000005: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [NamedExternref("IDBVersionChangeEvent")], shim_idx: 3475, ret: Result(Unit), inner_ret: Some(Result(Unit)) }, mutable: true }) -> Externref`.
            const ret = makeMutClosure(arg0, arg1, wasm_bindgen__convert__closures_____invoke__hfb521414532ea888);
            return ret;
        },
        __wbindgen_cast_0000000000000006: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [NamedExternref("MessageEvent")], shim_idx: 3474, ret: Unit, inner_ret: Some(Unit) }, mutable: true }) -> Externref`.
            const ret = makeMutClosure(arg0, arg1, wasm_bindgen__convert__closures_____invoke__h3b11c9c6f1321b37_5);
            return ret;
        },
        __wbindgen_cast_0000000000000007: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [], shim_idx: 2437, ret: Unit, inner_ret: Some(Unit) }, mutable: false }) -> Externref`.
            const ret = makeClosure(arg0, arg1, wasm_bindgen__convert__closures_____invoke__h57e6588dd12ae83d);
            return ret;
        },
        __wbindgen_cast_0000000000000008: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [], shim_idx: 3473, ret: Unit, inner_ret: Some(Unit) }, mutable: true }) -> Externref`.
            const ret = makeMutClosure(arg0, arg1, wasm_bindgen__convert__closures_____invoke__h0f0aa98c7a293579);
            return ret;
        },
        __wbindgen_cast_0000000000000009: function(arg0, arg1) {
            // Cast intrinsic for `Closure(Closure { owned: true, function: Function { arguments: [], shim_idx: 4298, ret: Unit, inner_ret: Some(Unit) }, mutable: true }) -> Externref`.
            const ret = makeMutClosure(arg0, arg1, wasm_bindgen__convert__closures_____invoke__h887315a3ba57698c);
            return ret;
        },
        __wbindgen_cast_000000000000000a: function(arg0) {
            // Cast intrinsic for `F64 -> Externref`.
            const ret = arg0;
            return ret;
        },
        __wbindgen_cast_000000000000000b: function(arg0, arg1) {
            // Cast intrinsic for `Ref(Slice(U8)) -> NamedExternref("Uint8Array")`.
            const ret = getArrayU8FromWasm0(arg0, arg1);
            return ret;
        },
        __wbindgen_cast_000000000000000c: function(arg0, arg1) {
            // Cast intrinsic for `Ref(String) -> Externref`.
            const ret = getStringFromWasm0(arg0, arg1);
            return ret;
        },
        __wbindgen_cast_000000000000000d: function(arg0) {
            // Cast intrinsic for `U64 -> Externref`.
            const ret = BigInt.asUintN(64, arg0);
            return ret;
        },
        __wbindgen_init_externref_table: function() {
            const table = wasm.__wbindgen_externrefs;
            const offset = table.grow(4);
            table.set(0, undefined);
            table.set(offset + 0, undefined);
            table.set(offset + 1, null);
            table.set(offset + 2, true);
            table.set(offset + 3, false);
        },
    };
    return {
        __proto__: null,
        "./bee_sdk_bg.js": import0,
    };
}

function wasm_bindgen__convert__closures_____invoke__h57e6588dd12ae83d(arg0, arg1) {
    wasm.wasm_bindgen__convert__closures_____invoke__h57e6588dd12ae83d(arg0, arg1);
}

function wasm_bindgen__convert__closures_____invoke__h0f0aa98c7a293579(arg0, arg1) {
    wasm.wasm_bindgen__convert__closures_____invoke__h0f0aa98c7a293579(arg0, arg1);
}

function wasm_bindgen__convert__closures_____invoke__h887315a3ba57698c(arg0, arg1) {
    wasm.wasm_bindgen__convert__closures_____invoke__h887315a3ba57698c(arg0, arg1);
}

function wasm_bindgen__convert__closures_____invoke__h3b11c9c6f1321b37(arg0, arg1, arg2) {
    wasm.wasm_bindgen__convert__closures_____invoke__h3b11c9c6f1321b37(arg0, arg1, arg2);
}

function wasm_bindgen__convert__closures_____invoke__h56a527e5ba162cbf(arg0, arg1, arg2) {
    wasm.wasm_bindgen__convert__closures_____invoke__h56a527e5ba162cbf(arg0, arg1, arg2);
}

function wasm_bindgen__convert__closures_____invoke__h3b11c9c6f1321b37_3(arg0, arg1, arg2) {
    wasm.wasm_bindgen__convert__closures_____invoke__h3b11c9c6f1321b37_3(arg0, arg1, arg2);
}

function wasm_bindgen__convert__closures_____invoke__h3b11c9c6f1321b37_5(arg0, arg1, arg2) {
    wasm.wasm_bindgen__convert__closures_____invoke__h3b11c9c6f1321b37_5(arg0, arg1, arg2);
}

function wasm_bindgen__convert__closures_____invoke__hca7b2218525b506f(arg0, arg1, arg2) {
    const ret = wasm.wasm_bindgen__convert__closures_____invoke__hca7b2218525b506f(arg0, arg1, arg2);
    if (ret[1]) {
        throw takeFromExternrefTable0(ret[0]);
    }
}

function wasm_bindgen__convert__closures_____invoke__hfb521414532ea888(arg0, arg1, arg2) {
    const ret = wasm.wasm_bindgen__convert__closures_____invoke__hfb521414532ea888(arg0, arg1, arg2);
    if (ret[1]) {
        throw takeFromExternrefTable0(ret[0]);
    }
}

function wasm_bindgen__convert__closures_____invoke__h3031a3aa7f6324e0(arg0, arg1, arg2, arg3) {
    wasm.wasm_bindgen__convert__closures_____invoke__h3031a3aa7f6324e0(arg0, arg1, arg2, arg3);
}


const __wbindgen_enum_IdbRequestReadyState = ["pending", "done"];


const __wbindgen_enum_IdbTransactionMode = ["readonly", "readwrite", "versionchange", "readwriteflush", "cleanup"];
const ActiveConnectSessionFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_activeconnectsession_free(ptr, 1));
const BeeConnectFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_beeconnect_free(ptr, 1));
const CryptoFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_crypto_free(ptr, 1));
const CryptoResultOfEncryptFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_cryptoresultofencrypt_free(ptr, 1));
const CryptoResultOfGenSeedAndKeysFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_cryptoresultofgenseedandkeys_free(ptr, 1));
const CryptoResultOfGetKeysFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_cryptoresultofgetkeys_free(ptr, 1));
const CryptoResultOfSignFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_cryptoresultofsign_free(ptr, 1));
const GraphqlBlockDataFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_graphqlblockdata_free(ptr, 1));
const MinerFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_miner_free(ptr, 1));
const MinerAccountDataFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_mineraccountdata_free(ptr, 1));
const ParsedConnectPayloadFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_parsedconnectpayload_free(ptr, 1));
const ResultOfCreateSharedKeySessionFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_resultofcreatesharedkeysession_free(ptr, 1));
const ResultOfDisconnectSessionFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_resultofdisconnectsession_free(ptr, 1));
const ResultOfGenMiningKeysFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_resultofgenminingkeys_free(ptr, 1));
const ResultOfQueryActiveSessionsByMultifactorFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_resultofqueryactivesessionsbymultifactor_free(ptr, 1));
const ResultOfRequestSetMiningKeysFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_resultofrequestsetminingkeys_free(ptr, 1));
const ResultOfRequestSignChallengeFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_resultofrequestsignchallenge_free(ptr, 1));
const ResultOfWaitChallengeResponseFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_resultofwaitchallengeresponse_free(ptr, 1));
const ResultOfWaitSetMiningKeysRequestFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_resultofwaitsetminingkeysrequest_free(ptr, 1));
const ResultOfWaitWalletHelloFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_resultofwaitwallethello_free(ptr, 1));

function addToExternrefTable0(obj) {
    const idx = wasm.__externref_table_alloc();
    wasm.__wbindgen_externrefs.set(idx, obj);
    return idx;
}

const CLOSURE_DTORS = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(state => wasm.__wbindgen_destroy_closure(state.a, state.b));

function debugString(val) {
    // primitive types
    const type = typeof val;
    if (type == 'number' || type == 'boolean' || val == null) {
        return  `${val}`;
    }
    if (type == 'string') {
        return `"${val}"`;
    }
    if (type == 'symbol') {
        const description = val.description;
        if (description == null) {
            return 'Symbol';
        } else {
            return `Symbol(${description})`;
        }
    }
    if (type == 'function') {
        const name = val.name;
        if (typeof name == 'string' && name.length > 0) {
            return `Function(${name})`;
        } else {
            return 'Function';
        }
    }
    // objects
    if (Array.isArray(val)) {
        const length = val.length;
        let debug = '[';
        if (length > 0) {
            debug += debugString(val[0]);
        }
        for(let i = 1; i < length; i++) {
            debug += ', ' + debugString(val[i]);
        }
        debug += ']';
        return debug;
    }
    // Test for built-in
    const builtInMatches = /\[object ([^\]]+)\]/.exec(toString.call(val));
    let className;
    if (builtInMatches && builtInMatches.length > 1) {
        className = builtInMatches[1];
    } else {
        // Failed to match the standard '[object ClassName]'
        return toString.call(val);
    }
    if (className == 'Object') {
        // we're a user defined class or Object
        // JSON.stringify avoids problems with cycles, and is generally much
        // easier than looping through ownProperties of `val`.
        try {
            return 'Object(' + JSON.stringify(val) + ')';
        } catch (_) {
            return 'Object';
        }
    }
    // errors
    if (val instanceof Error) {
        return `${val.name}: ${val.message}\n${val.stack}`;
    }
    // TODO we could test for more things here, like `Set`s and `Map`s.
    return className;
}

function getArrayU8FromWasm0(ptr, len) {
    ptr = ptr >>> 0;
    return getUint8ArrayMemory0().subarray(ptr / 1, ptr / 1 + len);
}

let cachedDataViewMemory0 = null;
function getDataViewMemory0() {
    if (cachedDataViewMemory0 === null || cachedDataViewMemory0.buffer.detached === true || (cachedDataViewMemory0.buffer.detached === undefined && cachedDataViewMemory0.buffer !== wasm.memory.buffer)) {
        cachedDataViewMemory0 = new DataView(wasm.memory.buffer);
    }
    return cachedDataViewMemory0;
}

function getStringFromWasm0(ptr, len) {
    return decodeText(ptr >>> 0, len);
}

let cachedUint8ArrayMemory0 = null;
function getUint8ArrayMemory0() {
    if (cachedUint8ArrayMemory0 === null || cachedUint8ArrayMemory0.byteLength === 0) {
        cachedUint8ArrayMemory0 = new Uint8Array(wasm.memory.buffer);
    }
    return cachedUint8ArrayMemory0;
}

function handleError(f, args) {
    try {
        return f.apply(this, args);
    } catch (e) {
        const idx = addToExternrefTable0(e);
        wasm.__wbindgen_exn_store(idx);
    }
}

function isLikeNone(x) {
    return x === undefined || x === null;
}

function makeClosure(arg0, arg1, f) {
    const state = { a: arg0, b: arg1, cnt: 1 };
    const real = (...args) => {

        // First up with a closure we increment the internal reference
        // count. This ensures that the Rust closure environment won't
        // be deallocated while we're invoking it.
        state.cnt++;
        try {
            return f(state.a, state.b, ...args);
        } finally {
            real._wbg_cb_unref();
        }
    };
    real._wbg_cb_unref = () => {
        if (--state.cnt === 0) {
            wasm.__wbindgen_destroy_closure(state.a, state.b);
            state.a = 0;
            CLOSURE_DTORS.unregister(state);
        }
    };
    CLOSURE_DTORS.register(real, state, state);
    return real;
}

function makeMutClosure(arg0, arg1, f) {
    const state = { a: arg0, b: arg1, cnt: 1 };
    const real = (...args) => {

        // First up with a closure we increment the internal reference
        // count. This ensures that the Rust closure environment won't
        // be deallocated while we're invoking it.
        state.cnt++;
        const a = state.a;
        state.a = 0;
        try {
            return f(a, state.b, ...args);
        } finally {
            state.a = a;
            real._wbg_cb_unref();
        }
    };
    real._wbg_cb_unref = () => {
        if (--state.cnt === 0) {
            wasm.__wbindgen_destroy_closure(state.a, state.b);
            state.a = 0;
            CLOSURE_DTORS.unregister(state);
        }
    };
    CLOSURE_DTORS.register(real, state, state);
    return real;
}

function passArrayJsValueToWasm0(array, malloc) {
    const ptr = malloc(array.length * 4, 4) >>> 0;
    for (let i = 0; i < array.length; i++) {
        const add = addToExternrefTable0(array[i]);
        getDataViewMemory0().setUint32(ptr + 4 * i, add, true);
    }
    WASM_VECTOR_LEN = array.length;
    return ptr;
}

function passStringToWasm0(arg, malloc, realloc) {
    if (realloc === undefined) {
        const buf = cachedTextEncoder.encode(arg);
        const ptr = malloc(buf.length, 1) >>> 0;
        getUint8ArrayMemory0().subarray(ptr, ptr + buf.length).set(buf);
        WASM_VECTOR_LEN = buf.length;
        return ptr;
    }

    let len = arg.length;
    let ptr = malloc(len, 1) >>> 0;

    const mem = getUint8ArrayMemory0();

    let offset = 0;

    for (; offset < len; offset++) {
        const code = arg.charCodeAt(offset);
        if (code > 0x7F) break;
        mem[ptr + offset] = code;
    }
    if (offset !== len) {
        if (offset !== 0) {
            arg = arg.slice(offset);
        }
        ptr = realloc(ptr, len, len = offset + arg.length * 3, 1) >>> 0;
        const view = getUint8ArrayMemory0().subarray(ptr + offset, ptr + len);
        const ret = cachedTextEncoder.encodeInto(arg, view);

        offset += ret.written;
        ptr = realloc(ptr, len, offset, 1) >>> 0;
    }

    WASM_VECTOR_LEN = offset;
    return ptr;
}

function takeFromExternrefTable0(idx) {
    const value = wasm.__wbindgen_externrefs.get(idx);
    wasm.__externref_table_dealloc(idx);
    return value;
}

let cachedTextDecoder = new TextDecoder('utf-8', { ignoreBOM: true, fatal: true });
cachedTextDecoder.decode();
const MAX_SAFARI_DECODE_BYTES = 2146435072;
let numBytesDecoded = 0;
function decodeText(ptr, len) {
    numBytesDecoded += len;
    if (numBytesDecoded >= MAX_SAFARI_DECODE_BYTES) {
        cachedTextDecoder = new TextDecoder('utf-8', { ignoreBOM: true, fatal: true });
        cachedTextDecoder.decode();
        numBytesDecoded = len;
    }
    return cachedTextDecoder.decode(getUint8ArrayMemory0().subarray(ptr, ptr + len));
}

const cachedTextEncoder = new TextEncoder();

if (!('encodeInto' in cachedTextEncoder)) {
    cachedTextEncoder.encodeInto = function (arg, view) {
        const buf = cachedTextEncoder.encode(arg);
        view.set(buf);
        return {
            read: arg.length,
            written: buf.length
        };
    };
}

let WASM_VECTOR_LEN = 0;

let wasmModule, wasmInstance, wasm;
function __wbg_finalize_init(instance, module) {
    wasmInstance = instance;
    wasm = instance.exports;
    wasmModule = module;
    cachedDataViewMemory0 = null;
    cachedUint8ArrayMemory0 = null;
    wasm.__wbindgen_start();
    return wasm;
}

async function __wbg_load(module, imports) {
    if (typeof Response === 'function' && module instanceof Response) {
        if (typeof WebAssembly.instantiateStreaming === 'function') {
            try {
                return await WebAssembly.instantiateStreaming(module, imports);
            } catch (e) {
                const validResponse = module.ok && expectedResponseType(module.type);

                if (validResponse && module.headers.get('Content-Type') !== 'application/wasm') {
                    console.warn("`WebAssembly.instantiateStreaming` failed because your server does not serve Wasm with `application/wasm` MIME type. Falling back to `WebAssembly.instantiate` which is slower. Original error:\n", e);

                } else { throw e; }
            }
        }

        const bytes = await module.arrayBuffer();
        return await WebAssembly.instantiate(bytes, imports);
    } else {
        const instance = await WebAssembly.instantiate(module, imports);

        if (instance instanceof WebAssembly.Instance) {
            return { instance, module };
        } else {
            return instance;
        }
    }

    function expectedResponseType(type) {
        switch (type) {
            case 'basic': case 'cors': case 'default': return true;
        }
        return false;
    }
}

function initSync(module) {
    if (wasm !== undefined) return wasm;


    if (module !== undefined) {
        if (Object.getPrototypeOf(module) === Object.prototype) {
            ({module} = module)
        } else {
            console.warn('using deprecated parameters for `initSync()`; pass a single object instead')
        }
    }

    const imports = __wbg_get_imports();
    if (!(module instanceof WebAssembly.Module)) {
        module = new WebAssembly.Module(module);
    }
    const instance = new WebAssembly.Instance(module, imports);
    return __wbg_finalize_init(instance, module);
}

async function __wbg_init(module_or_path) {
    if (wasm !== undefined) return wasm;


    if (module_or_path !== undefined) {
        if (Object.getPrototypeOf(module_or_path) === Object.prototype) {
            ({module_or_path} = module_or_path)
        } else {
            console.warn('using deprecated parameters for the initialization function; pass a single object instead')
        }
    }

    if (module_or_path === undefined) {
        module_or_path = new URL('bee_sdk_bg.wasm', import.meta.url);
    }
    const imports = __wbg_get_imports();

    if (typeof module_or_path === 'string' || (typeof Request === 'function' && module_or_path instanceof Request) || (typeof URL === 'function' && module_or_path instanceof URL)) {
        module_or_path = fetch(module_or_path);
    }

    const { instance, module } = await __wbg_load(await module_or_path, imports);

    return __wbg_finalize_init(instance, module);
}

export { initSync, __wbg_init as default };
