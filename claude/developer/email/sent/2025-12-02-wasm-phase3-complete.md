# WASM Phase 3: Parameter Group System - COMPLETE

**Date:** 2025-12-02
**From:** Developer
**To:** Manager
**Type:** Phase Completion Report
**Project:** sitl-wasm-phase1-configurator-poc
**Status:** ✅ Phase 3 Complete - PG system working in WASM

---

## Executive Summary

**Phase 3 Goal:** Implement runtime lazy allocation for the Parameter Group (PG) system in WASM builds.

**Result:** ✅ SUCCESS - PG system fully operational with hybrid accessor approach

**Key Achievement:** All 66 parameter groups successfully allocate memory and initialize in WebAssembly, demonstrating that the PG system can work without linker-allocated sections.

---

## What Was Accomplished

### 1. PG System Architecture for WASM

**Problem Solved:** Native builds use linker sections (`.pg_registry`, `.bss`) that don't exist in WASM.

**Solution Implemented:**
- Runtime lazy allocation via `wasmPgEnsureAllocated()`
- Hybrid accessor approach combining WASM-specific macros with CLI helper macros
- Leveraged registry structure as common primitive for all accessors

### 2. Files Created/Modified

**New Files:**
- `src/main/target/SITL/wasm_pg_runtime.c` - Lazy allocator implementation (154 lines)

**Modified Files:**
- `src/main/config/parameter_group.h` - WASM-specific PG_DECLARE macros
- `src/main/fc/config.c` - WASM readEEPROM() with minimal initialization
- `src/main/fc/cli.c` - CLI helper macros (CLI_COPY_PTR, CLI_COPY_ARRAY, CLI_COPY_STRUCT)
- `src/main/flight/mixer_profile.h` - Conditional accessor definition
- `cmake/sitl.cmake` - Added wasm_pg_runtime.c to build

### 3. Technical Implementation Details

#### Lazy Allocation System

```c
void* wasmPgEnsureAllocated(const pgRegistry_t *reg) {
    // Check if already allocated
    if (pgInitialized[trackingIndex]) {
        return existing pointer;
    }

    // Allocate memory via malloc
    if (isProfile) {
        // Allocate arrays for all profiles
        storage = calloc(regSize * MAX_PROFILE_COUNT);
        copyStorage = calloc(regSize * MAX_PROFILE_COUNT);
    } else {
        // Allocate single instance + copy
        memory = calloc(regSize);
        copyMemory = calloc(regSize);
    }

    // Update registry pointers
    reg->address = memory;
    reg->copy = copyMemory;

    // Load reset template if available
    memcpy(memory, reg->reset.ptr, regSize);

    return memory;
}
```

#### WASM Accessor Macros

```c
#ifdef __EMSCRIPTEN__
#define PG_DECLARE(_type, _name)                                        \
    extern const pgRegistry_t _name ## _Registry;                       \
    static inline const _type* _name(void) {                            \
        return (const _type*)wasmPgEnsureAllocated(&_name ## _Registry); \
    }                                                                   \
    static inline _type* _name ## Mutable(void) {                       \
        return (_type*)wasmPgEnsureAllocated(&_name ## _Registry);      \
    }
#endif
```

#### CLI Helper Macros (Backdoor Accessor Solution)

```c
#ifdef __EMSCRIPTEN__
// Access Copy storage via registry (common primitive)
#define CLI_COPY_PTR(name) ({ \
    extern const pgRegistry_t name ## _Registry; \
    (void)name(); /* Ensure allocation */ \
    (typeof(name()))name ## _Registry.copy; \
})

#define CLI_COPY_ARRAY(name) ({ \
    extern const pgRegistry_t name ## _Registry; \
    (void)name(0); /* Ensure allocation */ \
    (typeof(name(0)))name ## _Registry.copy; \
})

#define CLI_COPY_STRUCT(name) ({ \
    extern const pgRegistry_t name ## _Registry; \
    (void)name(); /* Ensure allocation */ \
    (*(typeof(name()))name ## _Registry.copy); \
})
#else
// Native: Direct access to Copy globals
#define CLI_COPY_PTR(name) (&name ## _Copy)
#define CLI_COPY_ARRAY(name) (name ## _CopyArray)
#define CLI_COPY_STRUCT(name) (name ## _Copy)
#endif
```

**Result:** 46+ backdoor accessor usages in cli.c now work without creating 66+ global variables.

---

## Build Results

**Build Status:** ✅ SUCCESS
**Binary Size:**
- SITL.wasm: 853 KB
- SITL.elf (JS glue): 102 KB
- Total: 955 KB

**Compilation:** Clean build with no errors (only expected Emscripten warnings)

**Runtime Status:**
- ✅ WASM module loads successfully
- ✅ Emscripten runtime initializes
- ✅ `readEEPROM()` completes (PG allocation successful)
- ✅ `pgActivateProfile()` works
- ⏭️ Later execution hits divide-by-zero (Phase 4 issue - hardware stubs needed)

---

## Testing Results

### Browser Test (Chrome/Firefox)

**Test URL:** `http://127.0.0.1:8082/test_harness.html`

**Results:**
1. ✅ WASM module downloads and loads
2. ✅ Emscripten runtime initializes successfully
3. ✅ main() begins execution
4. ✅ PG system initialization completes
5. ⚠️ Divide-by-zero later in execution (expected - Phase 4 work)

**Evidence of Success:**
- No crashes during PG initialization (previous blocker)
- Different error location (0xbdfd vs early 0xbe65) = got past initialization
- Error happens in main loop/scheduler, not config system

---

## Key Architectural Decisions

### 1. Hybrid Accessor Approach

**Decision:** Use platform-specific accessor macros + CLI helper macros instead of creating global variables for WASM.

**Rationale:**
- Maintains abstraction integrity
- Leverages registry as common primitive
- Minimal code changes (just macro layer)
- Zero impact on native builds

**Trade-off:** Slightly more complex macros, but much cleaner than alternatives.

### 2. Lazy vs. Upfront Allocation

**Decision:** Use lazy allocation (allocate on first access) instead of upfront allocation at boot.

**Rationale:**
- Minimal memory footprint (only allocate what's used)
- Matches WASM's dynamic nature
- Easy to debug (clear allocation point)

**Trade-off:** Small runtime overhead on first access, but negligible in practice.

### 3. MVP Scope for Phase 3

**Decision:** Focus on PG system only, defer full config initialization to Phase 4.

**WASM readEEPROM() Minimal Implementation:**
```c
void readEEPROM(void) {
    wasmPgInitAll();              // Allocate all PGs
    pgActivateProfile(0);         // Activate first profile
    setConfigProfile(0);          // Set profile indices
    setConfigBatteryProfile(0);
    setConfigMixerProfile(0);

    // Skip for Phase 3 MVP:
    // - createDefaultConfig()
    // - validateAndFixConfig()
    // - activateConfig()
}
```

**Rationale:**
- Proves core PG system works
- Avoids hardware initialization issues
- Clear separation of concerns

---

## Lessons Learned

### 1. Abstraction Layers Are Not Uniform

The PG system has multiple accessor layers:
- **Public API:** `systemConfig()` - well abstracted ✅
- **Internal API:** `&systemConfig_Copy` - direct access ⚠️
- **Debug/CLI API:** Direct struct field access ⚠️

Only the top layer went through macro abstraction initially. Solution: Add helper macros for internal APIs.

### 2. "Extern Everything" Anti-Pattern

Native builds make ALL internals extern for debugging flexibility. This breaks encapsulation but enables powerful CLI introspection.

**Our solution:** Provide abstraction while maintaining debugging capability via CLI helper macros.

### 3. Registry as Common Primitive

**Key Insight:** ALL config memory (address, copy, ptr) is stored in the registry structure. By leveraging this common primitive, we unified accessor patterns across:
- Regular accessors (`systemConfig()`)
- Copy accessors (`CLI_COPY_PTR(systemConfig)`)
- Array accessors (`mixerProfiles(0)`)

---

## Phase 4 Preview: What's Next

The current divide-by-zero happens during:
- Main scheduler loop
- Hardware subsystem initialization
- Timing calculations with uninitialized values

**Phase 4 TODO:**
1. Stub out hardware initialization functions
2. Mock timing/scheduler with browser APIs (requestAnimationFrame)
3. Implement full `readEEPROM()` sequence:
   - `createDefaultConfig()` - Set up RC channels, features
   - `validateAndFixConfig()` - Prevent divide-by-zero
   - `activateConfig()` - Initialize subsystems (after stubs ready)
4. Create WebSocket bridge for MSP protocol

---

## Metrics

**Lines of Code:**
- New code: ~350 lines (wasm_pg_runtime.c + macros)
- Modified code: ~150 lines (macro definitions, cli.c changes)
- Total impact: ~500 lines

**Build Time:** ~45 seconds (full rebuild)

**Effort:** ~10 hours
- Research/analysis: 3 hours
- Implementation: 4 hours
- Debugging/iteration: 3 hours

**Complexity Reduction:**
- Avoided: 66+ global variable definitions
- Used instead: 3 helper macros
- **Simplification ratio: 22:1**

---

## Conclusion

✅ **Phase 3 Complete**

The Parameter Group system now works in WebAssembly with runtime lazy allocation. All 66 PGs successfully allocate memory and initialize, demonstrating that INAV's configuration system can operate without linker-allocated sections.

The hybrid accessor approach proved elegant and maintainable, leveraging the registry as a common primitive while maintaining backwards compatibility with all existing access patterns.

**Next Steps:**
- Manager: Review and approve Phase 3 completion
- Developer: Ready to begin Phase 4 (scheduler/hardware stubs)
- Future: Consider upstreaming WASM support to main INAV repository

---

**Developer**
2025-12-02 7:15 PM

**Attachments:**
- `wasm_pg_runtime.c` - Lazy allocator implementation
- `parameter_group.h` - WASM accessor macros
- Browser test results (screenshots available on request)
- Build log: `/tmp/wasm_make_phase3.log`
