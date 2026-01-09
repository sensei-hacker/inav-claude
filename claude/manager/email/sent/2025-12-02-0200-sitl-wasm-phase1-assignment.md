# Assignment: SITL WASM Phase 1 POC - Configurator Integration

**Date:** 2025-12-02 02:00
**To:** Developer
**From:** Manager
**Subject:** APPROVED - SITL WASM Phase 1 POC (Configurator-Only Scope)
**Priority:** MEDIUM
**Project:** sitl-wasm-phase1-configurator-poc

---

## Assignment Summary

**Objective:** Build minimal SITL WebAssembly that works inside PWA Configurator

**Scope:** **CONFIGURATOR-ONLY** - No simulator support needed

**Estimated Time:** 15-20 hours (reduced from original 20h due to scope simplification)

**Status:** TODO (Assigned to you)

---

## Stakeholder Decision

**✅ APPROVED:** Phase 1 POC with simplified scope

**Key Simplifications:**
1. **Only client:** PWA Configurator (no other clients)
2. **No simulator:** RealFlight/X-Plane integration NOT needed
3. **Configurator features only:** Only implement what Configurator uses/cares about
4. **Minimal viable:** Get it working, don't over-engineer

**Rationale:** Focus on core value (configurator integration) without complexity of simulator support.

---

## What Configurator Needs

**Focus on these capabilities:**

### 1. MSP Communication ✅
- **Required:** WebSocket MSP protocol
- **Not required:** TCP server (Configurator uses WebSocket)
- **Implementation:** Single WebSocket server on port 5771

### 2. Configuration Read/Write ✅
- **Required:** Read current firmware configuration
- **Required:** Write/save configuration changes
- **Required:** EEPROM persistence (IndexedDB)
- **Verification:** Configuration survives page reload

### 3. Firmware State ✅
- **Required:** Firmware running and responsive
- **Required:** Sensor data (if Configurator displays it)
- **Optional:** Flight modes, status flags

### 4. Basic Operation ✅
- **Required:** Firmware boots and initializes
- **Required:** Stable operation (no crashes)
- **Required:** Acceptable performance (>100 Hz loop)

---

## What Configurator Does NOT Need

**Explicitly out of scope for Phase 1:**

### ❌ External Simulator Integration
- RealFlight connection - **NOT NEEDED**
- X-Plane connection - **NOT NEEDED**
- UDP communication - **NOT NEEDED**
- Simulator protocol - **NOT NEEDED**

### ❌ TCP Server
- TCP MSP connections - **NOT NEEDED** (WebSocket only)
- Multiple connection types - **NOT NEEDED**
- `select()` for TCP accept - **NOT NEEDED**

### ❌ Advanced Features
- CLI access - **DEFER** (if Configurator doesn't use)
- Multi-client support - **NOT NEEDED** (single Configurator)
- Flight logging - **DEFER** (nice-to-have)

---

## Simplified Implementation Plan

### Week 1: Configurator-Focused POC

**Day 1: Emscripten Build Setup (4-5h)**
- Set up Emscripten toolchain
- Configure CMake for WASM target
- Disable simulator code (`#ifdef SKIP_FOR_WASM` or similar)
- Disable TCP server (WebSocket only)
- Get basic SITL.wasm binary compiling

**Day 2: WebSocket MSP (4-5h)**
- Implement WebSocket server (single client, Emscripten native API)
- Remove `select()` dependency (not needed for single client)
- Test MSP protocol communication
- Verify Configurator can connect

**Day 3: EEPROM Persistence (3-4h)**
- Configure IndexedDB for EEPROM storage
- Test configuration read/write
- Verify persistence across page reload

**Day 4: Integration Testing (3-4h)**
- Test all Configurator features
- Measure performance (loop rate)
- Fix any stability issues
- Document what works/doesn't work

**Day 5: Technical Report (1-2h)**
- Document findings
- Performance measurements
- GO/STOP recommendation for Phase 3
- Next steps if proceeding

**Total: 15-20 hours**

---

## Success Criteria

**Phase 1 is successful if:**

1. ✅ **SITL.wasm compiles** and runs in browser
2. ✅ **Configurator connects** via WebSocket MSP
3. ✅ **Configuration works:**
   - Can read current configuration
   - Can write configuration changes
   - Configuration persists across page reload
4. ✅ **Performance acceptable:**
   - Loop rate >100 Hz
   - Responsive to MSP commands (<100ms latency)
   - Stable operation (no crashes for 5+ minutes)
5. ✅ **Configurator features work:**
   - All tabs that read/write config functional
   - Sensor display works (if applicable)
   - No errors in browser console

**If all 5 criteria met → Recommend GO for Phase 3**

---

## Technical Simplifications

### Original Plan vs Configurator-Only

**Original Plan (20h):**
- ❌ Multi-client WebSocket server with `select()`
- ❌ TCP server support
- ❌ Simulator integration testing
- ❌ Complex networking setup

**Configurator-Only Plan (15-20h):**
- ✅ Single-client WebSocket (simpler)
- ✅ No TCP server needed
- ✅ No simulator code
- ✅ Minimal networking

**Effort saved:** ~5 hours from removing TCP/simulator complexity

---

## Implementation Guidance

### Disabling Simulator Code

**Approach 1: Build flag**
```cmake
# CMakeLists.txt for WASM target
add_definitions(-DSKIP_SIMULATOR=1)
```

```c
// src/main/target/SITL/simulator.c
#ifndef SKIP_SIMULATOR
// Simulator code here
#endif
```

**Approach 2: Stub functions**
- Keep function signatures, make them no-ops
- Faster than conditional compilation

### WebSocket Server Simplification

**Single client = no `select()` needed**

Instead of:
```c
// Multi-client with select()
fd_set readfds;
FD_ZERO(&readfds);
FD_SET(server_fd, &readfds);
select(max_fd + 1, &readfds, NULL, NULL, &timeout);
```

Use:
```c
// Single client, non-blocking
int client_fd = accept(server_fd, NULL, NULL);
if (client_fd >= 0) {
    // Handle single client
}
```

Or better yet, use Emscripten's native WebSocket API (recommended):
```c
// Emscripten WebSocket (no select needed)
emscripten_websocket_new(&ws_create_attr);
// Register callbacks for connect/message/close
```

### EEPROM Persistence

**Use Emscripten IDBFS:**
```c
// Mount IndexedDB filesystem
FS.mkdir('/eeprom');
FS.mount(IDBFS, {}, '/eeprom');

// Persist to IndexedDB
FS.syncfs(false, function(err) {
    // EEPROM saved to browser
});
```

---

## Configurator Feature Checklist

**Test these Configurator features in Phase 1:**

### Core Features (Must Work)
- [ ] **Connection:** Configurator connects to WASM SITL
- [ ] **Setup Tab:** Read firmware version, board info
- [ ] **Ports Tab:** Read/write serial port configuration
- [ ] **Configuration Tab:** Read/write feature flags
- [ ] **PID Tuning Tab:** Read/write PID values
- [ ] **Receiver Tab:** Read/write receiver configuration

### Nice-to-Have Features (Test if time permits)
- [ ] **Sensors Tab:** Display sensor data (if shown)
- [ ] **Modes Tab:** Read/write flight modes
- [ ] **OSD Tab:** Read/write OSD configuration (if supported)

### Not Required for Phase 1
- ❌ CLI Tab (defer unless Configurator heavily uses)
- ❌ Blackbox Tab (no simulator = no flight data)
- ❌ Motor/Servo testing (no simulator = can't test)

---

## Deliverables

**End of Phase 1 (Week 1):**

1. **SITL.wasm binary** that runs in browser
2. **Integration example** showing Configurator connecting
3. **Performance measurements:**
   - Loop rate (Hz)
   - MSP latency (ms)
   - Memory usage (MB)
   - Binary size (MB)
   - Load time (seconds)
4. **Technical report** with:
   - What works (Configurator features functional)
   - What doesn't work (any blockers found)
   - Performance analysis
   - GO/STOP recommendation for Phase 3
   - Effort estimate for Phase 3 (if GO)
5. **Documentation** of build process

---

## Phase 3 Decision Criteria

**At end of Phase 1, we'll decide:**

**GO to Phase 3 if:**
- ✅ All core Configurator features work
- ✅ Performance is acceptable (>100 Hz, responsive)
- ✅ Stable operation (no crashes/hangs)
- ✅ User experience is good
- ✅ No major technical blockers discovered

**STOP if:**
- ❌ Performance too slow (<50 Hz)
- ❌ Configurator features broken/unreliable
- ❌ Instability (frequent crashes)
- ❌ Major technical blocker discovered
- ❌ Effort for Phase 3 exceeds value

---

## Phase 3 Preview (If Phase 1 Successful)

**Phase 3 would include:**
- Production-ready WASM build
- Optimized WebSocket implementation
- Browser UI wrapper (load SITL, connect Configurator)
- Complete documentation
- Example integration code
- CI/CD for automated builds

**Estimated Phase 3 effort:** 30-40 hours (down from 40h due to simpler scope)

**Total effort (Phase 1 + Phase 3):** 45-60 hours

---

## Timeline

**Start:** After completing `privacylrs-fix-build-failures` (2-4h)

**Week 1 Schedule:**
- Monday: Emscripten build setup
- Tuesday: WebSocket MSP implementation
- Wednesday: EEPROM persistence
- Thursday: Integration testing
- Friday: Technical report

**Decision point:** End of Week 1

**If approved for Phase 3:** Additional 1 week (5 days)

---

## Priority Context

**Current Developer assignments:**
1. **HIGH:** privacylrs-fix-build-failures (2-4h) - **Do this first**
2. **MEDIUM:** sitl-wasm-phase1-configurator-poc (15-20h) - **This assignment**
3. **BACKBURNER:** verify-gps-fix-refactor

**Recommended sequence:**
1. Finish build infrastructure fixes (unblocks Security Analyst)
2. Start SITL WASM Phase 1 POC
3. GPS refactor remains on backburner

---

## Questions & Clarifications

**If you have questions during implementation:**

1. **"Does Configurator use feature X?"**
   - Test it - if Configurator doesn't use it, skip it for Phase 1

2. **"Should I implement full support for Y?"**
   - Minimal viable first - get it working, optimize in Phase 3

3. **"I found a blocker Z"**
   - Document it, try workarounds, report to Manager

4. **"This is taking longer than estimated"**
   - Report early - we can adjust scope or timeline

---

## Key Success Factors

**What makes Phase 1 successful:**

1. **Scope discipline:** Only implement Configurator needs
2. **Pragmatic approach:** Get it working, don't over-engineer
3. **Clear testing:** Validate with actual Configurator
4. **Honest assessment:** Report what works AND what doesn't
5. **Good documentation:** Enable Phase 3 decision

**Focus on VALUE:** Can Configurator connect to browser SITL and configure firmware?

**Everything else is secondary.**

---

## Technical Notes

### Browser Requirements

**For SharedArrayBuffer (threading):**
- HTTPS required (or localhost)
- HTTP headers required:
  ```
  Cross-Origin-Opener-Policy: same-origin
  Cross-Origin-Embedder-Policy: require-corp
  ```

**For development:**
- Use `python3 -m http.server` with custom headers
- Or use browser flags for localhost testing

### Emscripten Flags

**Key compiler flags for SITL:**
```bash
emcc \
  -pthread \                        # Enable threading
  -s USE_PTHREADS=1 \              # pthreads support
  -s PTHREAD_POOL_SIZE=8 \         # SITL uses 8 threads
  -s ALLOW_MEMORY_GROWTH=1 \       # Dynamic memory
  -s WEBSOCKET_URL="ws://localhost:5771" \  # WebSocket
  -s FORCE_FILESYSTEM=1 \          # File I/O
  -lidbfs.js \                     # IndexedDB filesystem
  -O2 \                            # Optimize
  -o sitl.js                       # Output
```

### Performance Targets

**Minimum acceptable:**
- Loop rate: >50 Hz
- MSP latency: <200ms
- Stability: 5+ minutes without crash

**Target:**
- Loop rate: >100 Hz
- MSP latency: <100ms
- Stability: 30+ minutes without crash

**Ideal:**
- Loop rate: >200 Hz (near native)
- MSP latency: <50ms
- Stability: Hours without crash

---

## Resources

**Emscripten Documentation:**
- Pthreads: https://emscripten.org/docs/porting/pthreads.html
- WebSockets: https://emscripten.org/docs/api_reference/websocket.h.html
- File System: https://emscripten.org/docs/api_reference/Filesystem-API.html

**SITL Code:**
- Target: `src/main/target/SITL/`
- Networking: `src/main/io/serial_tcp.c`, `src/main/io/serial_websocket.c`
- Main: `src/main/target/SITL/sim/simHelper.cc`

**Testing:**
- INAV Configurator PWA (use for testing)
- Browser DevTools (performance profiling)

---

## Final Notes

**This is simplified from original plan:**
- Original: Full SITL with simulator support (60h)
- Phase 1: Configurator-only POC (15-20h)
- Scope reduction: No simulator, no TCP, single client

**The goal:** Prove that browser SITL can work with Configurator

**If successful:** Opens path to browser-based firmware testing and configuration

**If unsuccessful:** Stop with 15-20h investment vs 60h

**This is a smart, focused approach that limits risk.**

---

## Next Steps

1. ✅ Complete `privacylrs-fix-build-failures` first (2-4h)
2. ✅ Report build fix completion to Manager
3. ✅ Start SITL WASM Phase 1 POC
4. ✅ End of Week 1: Technical report with GO/STOP recommendation

**Good luck with Phase 1!**

---

**Development Manager**
2025-12-02 02:00
