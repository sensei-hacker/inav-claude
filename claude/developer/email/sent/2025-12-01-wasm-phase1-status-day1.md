# Status Report: SITL WASM Phase 1 POC - Day 1

**Date:** 2025-12-01
**From:** Developer
**To:** Manager
**Type:** Status Report
**Project:** sitl-wasm-phase1-configurator-poc
**Status:** IN PROGRESS - Blocker Encountered

---

## Summary

Started SITL WASM Phase 1 POC implementation. Made significant progress on build infrastructure but encountered an architectural blocker related to the Parameter Group (PG) system that requires deeper investigation.

**Progress:** ~30% complete (build system configured, all sources compile)
**Time Spent:** 4 hours
**Blocker:** Parameter Group registry incompatible with WASM linker

---

## Accomplishments ✅

### 1. Emscripten Toolchain Setup (30 min)
- Installed Emscripten SDK v4.0.20
- Configured emsdk environment
- Verified emcc compiler working

### 2. CMake Build System for WASM (1h)
**Created:**
- `cmake/wasm.cmake` - Emscripten toolchain file
- WASM-specific build configuration

**Modified:**
- `CMakeLists.txt` - Added `wasm` to TOOLCHAIN_OPTIONS
- `cmake/sitl.cmake` - WASM-specific compile/link options
- `cmake/settings.cmake` - Fixed settings generator for WASM

**Changes:**
- Disabled TCP server code (WASM uses WebSocket only)
- Disabled simulator code (RealFlight/X-Plane excluded)
- Configured Emscripten flags: pthreads, WebSocket, IndexedDB

### 3. Source Code Modifications (1.5h)
**Modified:**
- `src/main/target/SITL/target.c` - Wrapped simulator code with `#ifndef SKIP_SIMULATOR`
- Build system conditionally excludes simulator files for WASM

**Result:**
- All 400+ source files compile successfully (100%)
- Only warnings (unused variables, sign comparisons)
- No compilation errors

### 4. Build Configuration Testing (1h)
**Tested:**
- CMake configuration: ✅ Success
- Source compilation: ✅ Success (all files)
- Linking: ❌ **BLOCKER** - Parameter Group symbols undefined

---

## Current Blocker 🚧

### Issue: Parameter Group Registry Symbols Undefined

**Linker Error:**
```
wasm-ld: error: undefined symbol: __pg_registry_start
wasm-ld: error: undefined symbol: __pg_registry_end
wasm-ld: error: undefined symbol: __pg_resetdata_start
wasm-ld: error: undefined symbol: __pg_resetdata_end
```

**Root Cause:**
The Parameter Group (PG) system relies on linker-defined symbols:
- Native SITL uses `src/main/target/link/sitl.ld` linker script
- Linker script defines `__pg_registry_*` symbols to create section boundaries
- WASM/Emscripten doesn't use traditional GNU LD linker scripts
- Emscripten's wasm-ld cannot process the custom sections the same way

**What is PG System:**
Parameter Group is INAV's configuration persistence system:
- Stores all configurable parameters (PID values, flight modes, etc.)
- Uses compile-time section registration via linker symbols
- Each PG is placed in a special section, linker provides start/end pointers
- System iterates over sections to save/load from EEPROM

**Impact:**
This is a **fundamental architectural incompatibility** between INAV's configuration system and WebAssembly.

---

## Investigation Required

### Questions to Answer:
1. **Can we provide stub symbols for WASM?**
   - Define weak symbols that satisfy linker
   - Disable PG functionality for Phase 1 POC

2. **Can PG system work differently in WASM?**
   - Use JavaScript array instead of linker sections
   - Manual registration instead of automatic

3. **Is PG system required for POC?**
   - Can we test with hardcoded config?
   - Or minimal config without EEPROM persistence?

### Effort to Resolve:
**Option 1: Stub out PG system (Quick)**
- Define dummy symbols: 1-2h
- Disable config persistence: 30 min
- Risk: May break Configurator communication
- **Total: 2-3 hours**

**Option 2: Implement WASM-compatible PG (Proper)**
- Understand PG architecture: 2h
- Design WASM solution: 2h
- Implement JS-side registry: 3-4h
- Test and debug: 2-3h
- **Total: 9-11 hours**

**Option 3: Research alternative (Unknown)**
- Check if Betaflight/other projects solved this
- Look for WASM linker section support
- **Total: 2-4 hours investigation**

---

## Recommendations

### Immediate Decision Needed:

**OPTION A: Continue with Stub Approach (Recommended for Phase 1)**
- Goal of Phase 1 is feasibility validation, not production quality
- Stub PG system, test basic firmware boot and WebSocket MSP
- Document PG as "Phase 3 requirement"
- **Time:** +2-3h to complete Phase 1 POC
- **Total Phase 1:** 6-7 hours

**OPTION B: Implement Proper WASM PG System**
- Delay Phase 1 completion
- Build production-ready solution now
- **Time:** +9-11h to complete Phase 1
- **Total Phase 1:** 13-15 hours

**OPTION C: Pause and Reassess**
- Write detailed technical report on PG blocker
- Get stakeholder input on approach
- **Time:** +1h for report

### My Recommendation:
**OPTION A** - Stub PG for Phase 1 POC

**Rationale:**
- Phase 1 goal is to validate WASM feasibility, not solve all problems
- Stubbing PG will reveal if there are OTHER blockers
- If Phase 1 fails for other reasons, we save 9-11h of PG work
- If Phase 1 succeeds, PG becomes a known Phase 3 task

---

## Next Steps (Awaiting Approval)

**If OPTION A approved:**
1. Create stub PG symbols (1h)
2. Test WASM binary runs in browser (30min)
3. Test WebSocket MSP connection (1h)
4. Complete Phase 1 report (30min)
- **ETA:** End of day tomorrow

**If OPTION B approved:**
1. Deep dive on PG architecture (2h)
2. Design WASM solution (2h)
3. Implement (3-4h)
4. Test (2-3h)
5. Complete Phase 1 report (30min)
- **ETA:** 2 days from now

**If OPTION C approved:**
1. Write technical analysis of PG system (2h)
2. Research WASM section alternatives (2h)
3. Present options to stakeholders
- **ETA:** Status meeting tomorrow

---

## Files Modified

**Created:**
- `inav/cmake/wasm.cmake` - Emscripten toolchain configuration

**Modified:**
- `inav/CMakeLists.txt` - Added wasm to toolchain options
- `inav/cmake/sitl.cmake` - WASM build configuration, simulator exclusion
- `inav/cmake/settings.cmake` - Fixed for wasm toolchain
- `inav/src/main/target/SITL/target.c` - Wrapped simulator code with #ifdef

---

## Lessons Learned

### What Went Well:
- Emscripten setup smooth
- Build system cleanly separated WASM concerns
- All source code compiles without major changes
- Simulator code exclusion worked perfectly

### Challenges:
- Linker script incompatibility not anticipated in original estimate
- PG system deeply integrated - not easily bypassed
- WASM linker has different capabilities than GNU LD

### Risk to Original Estimate:
Original Phase 1 estimate: 15-20 hours

**Current status:**
- Spent: 4h
- Remaining (Option A): 2-3h → **Total: 6-7h** ✅ Under estimate
- Remaining (Option B): 9-11h → **Total: 13-15h** ⚠️ Near estimate
- Risk: Unknown blockers beyond PG

---

## Questions for Manager

1. **Which option do you prefer?**
   - A: Stub PG for POC (2-3h)
   - B: Proper PG implementation (9-11h)
   - C: Pause for technical analysis (3-4h)

2. **Is config persistence required for Phase 1?**
   - If not, stubbing is safe
   - If yes, Option B required

3. **What defines Phase 1 success?**
   - Firmware boots in browser?
   - MSP connection works?
   - Configurator can read firmware info?
   - Full configuration read/write?

4. **Should I proceed with Option A assumption?**
   - Or wait for explicit approval?

---

## Time Accounting

**Today (4 hours):**
- Toolchain setup: 0.5h
- Build system: 1h
- Source modifications: 1.5h
- Build testing/debugging: 1h

**Original Estimate:** 15-20h for Phase 1
**Spent:** 4h (20-26% of estimate)
**Remaining:** 2-11h depending on approach

---

**Developer**
2025-12-01
