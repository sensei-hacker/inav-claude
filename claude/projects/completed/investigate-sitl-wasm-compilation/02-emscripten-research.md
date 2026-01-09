# Emscripten & WebAssembly Research

**Date:** 2025-12-01
**Phase:** 2 of 4 - Emscripten Capabilities Research

---

## Overview

Research into Emscripten's support for the POSIX APIs that INAV SITL depends on. Emscripten is the LLVM-based C/C++ to WebAssembly compiler.

---

## Threading Support (pthreads)

**Source:** [Emscripten pthread documentation](https://emscripten.org/docs/porting/pthreads.html)

### Verdict: ✅ SUPPORTED

**Capabilities:**
- Full POSIX threads API implementation using SharedArrayBuffer
- `pthread_create()` - ✅ Supported
- `pthread_mutex_init/lock/unlock()` - ✅ Supported
- `pthread_setschedprio()` - ⚠️ Partially supported (no full priority support)

**Requirements:**
- SharedArrayBuffer enabled (requires COOP/COEP HTTP headers)
- Compile flag: `-pthread`

**Limitations:**
- Main thread blocking (e.g., `pthread_join`) can cause busy-waiting/deadlocks
- Firefox limits threads to 20 maximum (SITL uses 8 = OK)
- No signal support (`pthread_kill` unsupported)
- `pthread_create` returns before worker actually starts (violates strict POSIX)

**SITL Compatibility:** ✅ GOOD
- SITL uses 8 threads (one per UART) - within limits
- Uses `pthread_create` and `pthread_mutex_*` - both supported
- May need to avoid main thread blocking

---

## Networking Support (BSD Sockets)

**Source:** [Emscripten networking documentation](https://emscripten.org/docs/porting/networking.html)

### Verdict: ✅ SUPPORTED (with caveats)

**Capabilities:**
All key POSIX socket functions ARE proxied:
- `socket()` - ✅ Supported
- `bind()` - ✅ Supported
- `listen()` - ✅ Supported
- `accept()` - ✅ Supported
- `send()` / `recv()` - ✅ Supported
- `sendto()` / `recvfrom()` - ✅ Supported
- `setsockopt()` / `getsockopt()` - ✅ Supported

**NOT proxied:**
- `select()` - ❌ Not available
- `poll()` - ❌ Not available

**Networking Modes:**

1. **Emulated POSIX TCP Sockets** (Default)
   - Maps TCP sockets to WebSockets automatically
   - Requires WebSockify proxy server on backend
   - Client code unchanged

2. **Direct WebSocket API**
   - Native browser WebSocket passthrough
   - Multi-threaded safe
   - Better performance

3. **POSIX Proxy Server**
   - Full TCP/UDP support via dedicated proxy
   - Requires threading and build flags

**SITL Implications:**

✅ **Perfect fit!** SITL already has WebSocket support:
- `serial_websocket.c` - Native WebSocket server (just added!)
- `serial_tcp.c` - BSD socket server

**Strategy:**
- Use Emscripten's direct WebSocket API
- SITL's existing `serial_websocket.c` code maps perfectly
- MSP communication works unchanged

**Caveat:** Need to check if SITL uses `select()` anywhere (not supported).

---

## File System Support

**Source:** [Emscripten Filesystem API](https://emscripten.org/docs/api_reference/Filesystem-API.html)

### Verdict: ✅ FULLY SUPPORTED

**Standard C File I/O:**
- `fopen()`, `fread()`, `fwrite()`, `fclose()` - ✅ All supported
- Works seamlessly through Emscripten's FS library
- POSIX-like synchronous interface

**Virtual File Systems:**

| File System | Use Case | Persistence | SITL Application |
|-------------|----------|-------------|------------------|
| MEMFS | In-memory (default) | None | Temporary files |
| IDBFS | Browser IndexedDB | Async with `syncfs()` | **EEPROM emulation!** |
| NODEFS | Node.js only | Automatic | N/A (browser target) |

**EEPROM Emulation Strategy:**
1. Mount IDBFS at `/eeprom/`
2. Use `FS.syncfs()` to persist configuration
3. Standard `fopen("/eeprom/eeprom.bin", "r+")` works unchanged
4. Optional `autoPersist: true` for automatic syncing

**SITL Compatibility:** ✅ PERFECT
- All existing file I/O code works
- Better than native (no file corruption on crash)
- Cross-browser persistent storage

---

## Timing Support

**Sources:**
- [GitHub issue #425](https://github.com/emscripten-core/emscripten/issues/425)
- [GitHub issue #1795](https://github.com/kripken/emscripten/issues/1795)

### Verdict: ✅ SUPPORTED (with checks)

**`clock_gettime(CLOCK_MONOTONIC)`:**
- ✅ Implemented using `performance.now()` (browsers)
- ✅ Implemented using `process.hrtime()` (Node.js)
- ⚠️ May not be available in all environments (old Edge workers)

**Best Practice:**
```c
// Check if monotonic clock available
if (emscripten_get_now_is_monotonic()) {
    clock_gettime(CLOCK_MONOTONIC, &ts);
} else {
    // Fallback to CLOCK_REALTIME
}
```

**Or check return value:**
```c
if (clock_gettime(CLOCK_MONOTONIC, &ts) == -1) {
    // Handle error
}
```

**SITL Compatibility:** ✅ GOOD
- High-resolution timing works
- Monotonic clock available in modern browsers
- May need error handling for older environments

---

## Prior Art Research

### Betaflight Web Configurator

**Source:** [Betaflight Configurator Online](https://oscarliang.com/betaflight-configurator-online/)

**What it is:**
- Web app at https://app.betaflight.com/
- **NOT running firmware in browser**
- Uses Web Serial API to connect to physical hardware
- Same functionality as desktop app, just web-hosted

**Verdict:** Not relevant - doesn't run firmware in WASM

### Betaflight Blackbox Parser

**Source:** [blackbox-log-ts](https://github.com/blackbox-log/blackbox-log-ts)

**What it is:**
- TypeScript library with Rust WASM parser
- Parses Betaflight/INAV flight logs in browser
- Proof that flight controller code CAN compile to WASM

**Verdict:** Promising but limited scope

### Other Flight Controllers

**Search findings:**
- No evidence of Betaflight, Cleanflight, or EmuFlight running in browser
- Some have SITL modes (native Linux execution)
- Microsoft Flight Simulator uses WASM but for game add-ons, not flight controllers

**Conclusion:**
❌ **No prior art found** for full flight controller firmware → WebAssembly compilation

✅ **This would be pioneering work!**

---

## Key Gaps Identified

### ⚠️ Use of `select()`

Emscripten does NOT proxy `select()`.

**Action Required:** Search SITL code for `select()` usage:
```bash
grep -r "select(" src/main/target/SITL/
grep -r "select(" src/main/drivers/serial_tcp.c
```

**If found:** Need to refactor to use non-blocking I/O or alternative mechanisms.

### ⚠️ UDP Simulator Communication

SITL communicates with RealFlight/X-Plane over UDP.

**Problem:** UDP not available in browsers (WebRTC Data Channels are UDP-like but have different API)

**Implications:**
- Simulator integration (RealFlight/X-Plane) won't work directly
- Would need WebSocket proxy or drop simulator support
- OR build browser-based simulator (big scope increase)

---

## Emscripten Compilation Approach

### Recommended Build Configuration

**Compiler flags:**
```bash
emcc -pthread \                          # Enable pthreads
     -s USE_PTHREADS=1 \                # SharedArrayBuffer
     -s PTHREAD_POOL_SIZE=10 \          # Pre-allocate thread pool
     -s ALLOW_MEMORY_GROWTH=1 \         # Dynamic memory
     -s EXPORTED_FUNCTIONS='[_main]' \  # Export main
     -s EXPORTED_RUNTIME_METHODS='[ccall,cwrap,FS]' \  # FS for filesystem
     -s FORCE_FILESYSTEM=1 \            # Enable FS library
     -s WEBSOCKET_URL='ws://localhost:XXXX' \  # WebSocket config
     -lwebsocket.js \                   # WebSocket library
     -O2                                # Optimization
```

**HTTP Headers Required:**
```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

---

## Summary

| Component | SITL Requirement | Emscripten Support | Status |
|-----------|------------------|-------------------|--------|
| **Threading** | pthreads (8 threads) | ✅ Via SharedArrayBuffer | ✅ READY |
| **Sockets** | BSD sockets (TCP server) | ✅ Proxied to WebSockets | ✅ READY |
| **File I/O** | fopen/fread/fwrite | ✅ MEMFS + IDBFS | ✅ READY |
| **Timing** | clock_gettime(MONOTONIC) | ✅ Via performance.now() | ✅ READY |
| **select()** | Unknown (need to check) | ❌ Not supported | ⚠️ RISK |
| **UDP** | Simulator communication | ❌ Not available | ❌ BLOCKER |

---

## Next Steps

**Phase 3 Actions:**
1. Search SITL code for `select()` usage
2. Create compatibility matrix for all SITL features
3. Assess simulator integration options
4. Estimate porting effort
5. Determine GO/MAYBE/NO-GO recommendation

---

**Overall Assessment So Far:**
✅ **Technically feasible** for core SITL functionality
⚠️ **Challenges** with simulator integration and possible `select()` usage
❌ **No prior art** - would be first-of-its-kind

