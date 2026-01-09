# Feasibility Assessment & Compatibility Matrix

**Date:** 2025-12-01
**Phase:** 3 of 4 - Feasibility Assessment

---

## Executive Summary

✅ **VERDICT: FEASIBLE** with moderate effort and some limitations

Compiling INAV SITL to WebAssembly is **technically possible** using Emscripten. Core firmware functionality (flight controller logic, MSP communication, EEPROM storage) can work in browsers. However, **external simulator integration** (RealFlight/X-Plane) will not be available, and some code refactoring is required.

---

## Detailed Compatibility Matrix

| Component | SITL Implementation | Emscripten Support | Status | Effort | Notes |
|-----------|---------------------|-------------------|--------|--------|-------|
| **Threading** | 8 pthread threads | ✅ SharedArrayBuffer | ✅ READY | Low | Requires COOP/COEP headers |
| **Mutex Locks** | pthread_mutex_* | ✅ Supported | ✅ READY | None | Works as-is |
| **Sockets (BSD)** | socket/bind/accept | ✅ Proxied/emulated | ⚠️ PARTIAL | Medium | See networking details below |
| **select()** | Used in TCP/WebSocket | ❌ NOT supported | ❌ BLOCKER | Medium | Requires refactoring |
| **File I/O** | fopen/fread/fwrite | ✅ MEMFS + IDBFS | ✅ READY | Low | EEPROM → IndexedDB |
| **clock_gettime** | CLOCK_MONOTONIC | ✅ performance.now() | ✅ READY | Low | Add error checking |
| **UDP Sockets** | Simulator comms | ❌ NOT available | ❌ BLOCKER | N/A | No browser UDP |
| **WebSocket (native)** | RFC 6455 implementation | ✅ Native browser API | ✅ READY | Medium | Rewrite for Emscripten API |

---

## Critical Issue: `select()` Usage

### Problem

Emscripten does **NOT** support the POSIX `select()` function.

**Found in:**
1. **`serial_tcp.c:150`** - Blocking wait for TCP connections
2. **`serial_websocket.c:417`** - Blocking wait for WebSocket connections
3. **`sim/simple_soap_client.c:121`** - Simulator communication (already blocked by UDP)

**Usage pattern:**
```c
fd_set fds;
FD_ZERO(&fds);
FD_SET(socketFd, &fds);
if (select(socketFd + 1, &fds, NULL, NULL, NULL) < 0) {  // BLOCKS HERE
    // error
}
clientFd = accept(socketFd, ...);  // Accept connection
```

### Solutions

#### Option 1: Non-Blocking Sockets + Polling ⭐ RECOMMENDED

**Approach:**
- Set socket to non-blocking mode: `fcntl(fd, F_SETFL, O_NONBLOCK)`
- Replace `select()` with polling loop:

```c
while (!connection_ready) {
    clientFd = accept(socketFd, ...);
    if (clientFd >= 0) break;  // Got connection
    if (errno != EWOULDBLOCK) return -1;  // Real error
    emscripten_sleep(10);  // Yield to browser
}
```

**Pros:**
- Minimal code changes
- Works with existing BSD socket emulation
- Can be wrapped in `#ifdef __EMSCRIPTEN__`

**Cons:**
- Polling is less efficient than event-driven
- Adds small CPU overhead

**Effort:** **Medium** (2-4 hours per file)

#### Option 2: Use Emscripten WebSocket API

**Approach:**
- For WASM build only, bypass BSD sockets entirely
- Use native `emscripten_websocket_*` functions
- Event-driven callbacks instead of blocking

```c
#ifdef __EMSCRIPTEN__
  // Use emscripten_websocket_new()
  // Set onopen/onmessage/onerror callbacks
#else
  // Existing BSD socket code
#endif
```

**Pros:**
- More efficient (event-driven)
- No select() needed
- Better performance

**Cons:**
- Larger code changes
- Two implementations to maintain

**Effort:** **High** (8-12 hours)

#### Option 3: Drop TCP, Keep WebSocket Only

**Approach:**
- For WASM build, only compile WebSocket support
- Disable TCP server code
- Refactor WebSocket to use Emscripten API

**Pros:**
- Simplest for WASM
- WebSocket is more browser-native

**Cons:**
- Loses TCP fallback
- Still needs WebSocket refactoring

**Effort:** **Medium** (4-6 hours)

---

## Networking Architecture for WASM

### Current SITL Networking

```
┌─────────────────────────────────────────┐
│           INAV SITL (Native)            │
├─────────────────────────────────────────┤
│  TCP Server (5760-5767)  ← Configurator│
│  WebSocket Server (5771-5778) ← Browser│
│  UDP Client (RealFlight/X-Plane)        │
└─────────────────────────────────────────┘
```

### Proposed WASM Architecture

```
┌─────────────────────────────────────────────┐
│       INAV SITL (WebAssembly in Browser)    │
├─────────────────────────────────────────────┤
│  WebSocket (Emscripten API) ← Configurator │
│  File I/O (IndexedDB/IDBFS) ← EEPROM       │
│  ❌ No Simulator Integration (UDP N/A)      │
└─────────────────────────────────────────────┘
```

**Key Changes:**
1. ✅ MSP over WebSocket - configurator can connect
2. ✅ EEPROM persists to IndexedDB
3. ❌ No RealFlight/X-Plane integration
4. ❌ No TCP server (WebSocket only)

---

## Feature Impact Analysis

### ✅ Features That Work

| Feature | Status | Notes |
|---------|--------|-------|
| **Flight Controller Logic** | ✅ Full | All PID, navigation, sensors |
| **MSP Protocol** | ✅ Full | Over WebSocket |
| **Configuration** | ✅ Full | EEPROM via IndexedDB |
| **Blackbox Logging** | ✅ Full | Save to browser storage |
| **CLI** | ✅ Full | Via MSP |
| **OSD** | ✅ Full | Can be rendered to canvas |
| **Modes/Logic** | ✅ Full | All flight modes |
| **Sensors (Simulated)** | ✅ Full | Can provide fake data or JS API |

### ⚠️ Features With Limitations

| Feature | Status | Limitation | Mitigation |
|---------|--------|------------|------------|
| **Threading** | ⚠️ Partial | Max 20 threads (Firefox) | SITL uses 8 = OK |
| **select()** | ⚠️ Needs Fix | Not supported | Use polling or Emscripten API |
| **Performance** | ⚠️ Unknown | WASM overhead | Likely acceptable for SITL |

### ❌ Features That Won't Work

| Feature | Status | Reason | Alternative |
|---------|--------|--------|-------------|
| **RealFlight Integration** | ❌ Blocked | Requires UDP | Build browser-based sim |
| **X-Plane Integration** | ❌ Blocked | Requires UDP | Build browser-based sim |
| **TCP Server** | ❌ Difficult | Needs select() refactor | WebSocket only |

---

## Simulator Integration Options

Since UDP is not available in browsers, external simulator integration (RealFlight/X-Plane) won't work directly.

### Alternative Approaches

#### Option A: No Simulator (MSP Testing Only)

**Use Case:** Pure firmware testing without physics simulation

**Provides:**
- MSP command testing
- Configuration validation
- CLI testing
- Blackbox format validation

**Limitations:**
- No realistic flight dynamics
- No sensor simulation

**Effort:** None (this is the baseline)

#### Option B: JavaScript Simulator

**Approach:** Build lightweight flight dynamics in JavaScript

```javascript
// Simple physics simulation
class FlightSim {
  update(motorOutputs) {
    // Calculate forces from motors
    // Update position/velocity
    // Generate sensor data (gyro, accel, baro, GPS)
    return sensorData;
  }
}

// Feed to WASM SITL
ccall('updateSensors', null, ['number', 'number'], [gyro, accel]);
```

**Provides:**
- Basic flight physics
- Sensor simulation
- 3D visualization possible

**Effort:** **High** (40-80 hours for basic sim)

#### Option C: WebRTC Data Channel Proxy

**Approach:** Use WebRTC Data Channels as UDP-like transport to external simulator

**Architecture:**
```
Browser WASM ←→ WebRTC ←→ Native Bridge ←→ UDP ←→ RealFlight
```

**Provides:**
- Access to real flight sims
- Realistic physics

**Limitations:**
- Requires native proxy server (defeats some benefits of WASM)
- Complex setup
- Latency issues

**Effort:** **Very High** (80+ hours)

---

## Build Configuration Estimate

### Emscripten Compiler Flags

```bash
emcc \
  # Threading
  -pthread \
  -s USE_PTHREADS=1 \
  -s PTHREAD_POOL_SIZE=10 \
  \
  # Memory
  -s ALLOW_MEMORY_GROWTH=1 \
  -s INITIAL_MEMORY=64MB \
  -s MAXIMUM_MEMORY=512MB \
  \
  # File System
  -s FORCE_FILESYSTEM=1 \
  -lidbfs.js \
  \
  # WebSocket
  -lwebsocket.js \
  \
  # Exports
  -s EXPORTED_FUNCTIONS='[_main,_updateSensors]' \
  -s EXPORTED_RUNTIME_METHODS='[ccall,cwrap,FS]' \
  \
  # Optimization
  -O2 \
  \
  # Output
  -o inav-sitl.js \
  $(SOURCES)
```

### Required HTTP Headers

```http
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

**Impact:** Must be served from HTTPS with these headers for SharedArrayBuffer support.

---

## Code Changes Required

### 1. Replace `select()` Calls

**Files:**
- `src/main/drivers/serial_tcp.c` (if keeping TCP)
- `src/main/drivers/serial_websocket.c`

**Change:**
```c
#ifdef __EMSCRIPTEN__
// Non-blocking accept with polling
#else
// Original select() code
#endif
```

**Effort:** 4-6 hours

### 2. WebSocket Refactor (Optional but Recommended)

**File:**
- `src/main/drivers/serial_websocket.c`

**Change:**
- For WASM, use `emscripten_websocket_*` API
- Keep BSD socket version for native builds

**Effort:** 8-12 hours

### 3. Disable Simulator Integration

**Files:**
- `cmake/sitl.cmake`
- `src/main/target/SITL/CMakeLists.txt`

**Change:**
```cmake
if(EMSCRIPTEN)
  # Exclude simulator files
  list(REMOVE_ITEM SITL_SRC
    sim/realFlight.c
    sim/xplane.c
    sim/simple_soap_client.c
  )
endif()
```

**Effort:** 1-2 hours

### 4. File System Configuration

**Files:**
- `src/main/target/SITL/target.c`

**Change:**
```c
#ifdef __EMSCRIPTEN__
EM_ASM(
  FS.mkdir('/eeprom');
  FS.mount(IDBFS, {}, '/eeprom');
  FS.syncfs(true, function(err) {
    if (err) console.error('IDBFS load failed:', err);
  });
);
#endif
```

**Effort:** 2-4 hours

### 5. Add Browser Integration Layer

**New files:**
- `src/main/target/WASM/` directory
- Browser API bindings
- Sensor injection API

**Effort:** 8-16 hours

---

## Effort Estimate Summary

| Task | Optimistic | Realistic | Pessimistic |
|------|-----------|-----------|-------------|
| Replace select() calls | 4h | 6h | 10h |
| WebSocket refactor | 6h | 10h | 16h |
| Build system changes | 2h | 4h | 8h |
| File system config | 2h | 4h | 6h |
| Browser integration | 8h | 16h | 24h |
| Testing & debugging | 8h | 16h | 32h |
| Documentation | 2h | 4h | 8h |
| **TOTAL** | **32h** | **60h** | **104h** |

**Most Likely:** ~60 hours (~1.5 weeks of full-time work)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Performance issues | Medium | High | Profile early, optimize critical paths |
| Browser compatibility | Low | Medium | Target modern browsers only |
| Threading bugs | Medium | High | Thorough testing, use ThreadSanitizer |
| Binary size too large | Low | Medium | Use -O2, strip debug symbols |
| SharedArrayBuffer blocked | Low | Critical | Document header requirements clearly |
| select() refactor breaks logic | Medium | High | Extensive testing, side-by-side comparison |

---

## Value Proposition

### Benefits of Browser-Based SITL

1. **Zero Installation**
   - No downloads, no setup
   - Works on any platform with browser

2. **Integrated Testing**
   - Test firmware changes directly in configurator
   - Immediate feedback loop

3. **Educational**
   - Interactive tutorials possible
   - Learn PID tuning safely

4. **Development**
   - Lower barrier for contributors
   - Test PRs without hardware

5. **PID Tuning Sandbox**
   - Safe experimentation
   - Instant parameter changes

### Limitations

1. **No Real Flight Dynamics**
   - Unless JS simulator built (big effort)
   - Can't replace full SITL with external sim

2. **Performance Unknown**
   - May be slower than native
   - Loop rate might be limited

3. **Complexity**
   - Requires HTTPS + special headers
   - Not as simple as native binary

---

## Recommendation Factors

### ✅ Reasons to Proceed

1. **Technically feasible** with known solutions
2. **Complements PWA configurator** work already in progress
3. **Unique value** - no other flight controller does this
4. **Reasonable effort** (~60 hours)
5. **Good learning experience** for team

### ⚠️ Reasons to Hesitate

1. **Limited without flight sim** - testing value reduced
2. **Maintenance burden** - two code paths to maintain
3. **Unknown performance** - might be too slow
4. **Niche use case** - how many users would actually use it?

---

## Next Steps

**Phase 4:** Create final recommendation based on this analysis.

