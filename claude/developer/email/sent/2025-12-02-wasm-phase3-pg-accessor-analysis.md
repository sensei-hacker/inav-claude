# WASM Phase 3: PG Accessor Architecture Analysis

**Date:** 2025-12-02
**From:** Developer
**To:** Manager
**Type:** Technical Investigation Report
**Project:** sitl-wasm-phase1-configurator-poc
**Status:** Architecture analysis complete, approach pivot recommended

---

## Executive Summary

**Attempted Approach:** Runtime lazy allocation via accessor macros
**Result:** Partially successful, but hits architectural limitations
**Recommendation:** Hybrid approach combining upfront allocation with accessor abstraction

**Key Insight Discovered:** The PG system accessor layer can abstract platform differences, but the codebase has many "backdoor" accessors that bypass the abstraction.

---

## The Original Insight: Leverage Existing Abstraction

The PG system was **already designed for platform abstraction:**

```c
// parameter_group.h already has platform switches
#ifdef __APPLE__
  // macOS sections
#elif __EMSCRIPTEN__
  // WASM manual registry (done in Phase 1)
#else
  // GNU LD sections
#endif
```

The `PG_DECLARE` macros hide implementation details - **perfect place to add WASM-specific runtime accessors.**

### What We Implemented

**WASM accessor macros** that call a runtime function instead of directly accessing globals:

```c
#ifdef __EMSCRIPTEN__
void* wasmPgEnsureAllocated(const pgRegistry_t *reg);

#define PG_DECLARE(_type, _name)                                        \
    extern const pgRegistry_t _name ## _Registry;                       \
    static inline const _type* _name(void) {                            \
        return (const _type*)wasmPgEnsureAllocated(&_name ## _Registry); \
    }                                                                   \
    // ... mutable version
#endif
```

**Runtime lazy allocator** that malloc()s memory on first access:

```c
void* wasmPgEnsureAllocated(const pgRegistry_t *reg) {
    if (!pgInitialized[trackingIndex]) {
        // Allocate reg->address
        // Allocate reg->copy
        // Load defaults
        pgInitialized[trackingIndex] = true;
    }
    return reg->address;
}
```

**This works beautifully for:**
- `systemConfig()` - returns config pointer
- `pidProfile()` - returns profile pointer
- `motorConfig()` - returns config pointer
- All accessor functions defined by `PG_DECLARE` macros

---

## The Problem: Backdoor Accessors

Many parts of the codebase directly access **internal PG variables** that bypass the accessor functions:

### 1. Direct Copy Storage Access

**Native builds create globals:**
```c
// From PG_REGISTER macro expansion:
systemConfig_t systemConfig_System;  // Primary storage
systemConfig_t systemConfig_Copy;    // Copy for diff/restore
```

**Code uses them directly:**
```c
// cli.c:4481
printFeature(dumpMask, &featureConfig_Copy, featureConfig());
                        ^^^^^^^^^^^^^^^^^^^
                        Direct global access!
```

### 2. Array Copy Access

**Native:**
```c
// From PG_REGISTER_ARRAY:
modeActivationCondition_t modeActivationConditions_SystemArray[20];
modeActivationCondition_t modeActivationConditions_CopyArray[20];
```

**Usage:**
```c
// cli.c:4511
printAux(dumpMask, modeActivationConditions_CopyArray, modeActivationConditions(0));
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                   Direct array access!
```

### 3. Struct Field Access on Copy

```c
// cli.c:4486
printLed(dumpMask, ledStripConfig_Copy.ledConfigs, ledStripConfig()->ledConfigs);
                   ^^^^^^^^^^^^^^^^^^^
                   Accessing fields on Copy global!
```

---

## Accessor Pattern Analysis

### What ALL Accessors Have in Common

**Every piece of config memory comes from the registry:**

```c
typedef struct pgRegistry_s {
    pgn_t pgn;
    uint16_t size;
    uint8_t *address;      // ← Primary storage (_System, _SystemArray)
    uint8_t *copy;         // ← Copy storage (_Copy, _CopyArray)
    uint8_t **ptr;         // ← Profile current pointer
    union {
        void *ptr;         // Reset template data
        pgResetFunc *fn;   // Reset function
    } reset;
} pgRegistry_t;
```

**The relationship:**
- `systemConfig_System` → stored at `reg->address`
- `systemConfig_Copy` → stored at `reg->copy`
- `modeActivationConditions_SystemArray` → stored at `reg->address`
- `modeActivationConditions_CopyArray` → stored at `reg->copy`

**Key insight:** Both primary and copy storage are allocated by `wasmPgEnsureAllocated()` and stored in the registry.

### The Backdoor Problem

Code expects to do:
```c
&featureConfig_Copy              // Take address of global
modeActivationConditions_CopyArray[i]  // Index into global array
ledStripConfig_Copy.ledConfigs        // Access field of global struct
```

These require **lvalue globals that exist at link time.** You can't fake them with functions or macros that return pointers.

---

## Count of Backdoor Accessors

```bash
$ grep -E "_Copy\b|_CopyArray\b" src/main/fc/cli.c | wc -l
46
```

**46 direct accesses in cli.c alone!**

And CLI is critical for the Configurator to work (MSP commands call into CLI functions).

---

## Possible Solutions

### Solution A: Provide All Backdoor Accessors

**Create WASM-specific global pointers that get populated:**

```c
#ifdef __EMSCRIPTEN__
// Extern pointer declarations
extern systemConfig_t *systemConfig_Copy_ptr;

// Accessor macro that sets up pointer on first use
#define systemConfig_Copy (*systemConfig_Copy_ptr_get())

static inline systemConfig_t* systemConfig_Copy_ptr_get(void) {
    if (!systemConfig_Copy_ptr) {
        wasmPgEnsureAllocated(&systemConfig_Registry);
        systemConfig_Copy_ptr = (systemConfig_t*)systemConfig_Registry.copy;
    }
    return systemConfig_Copy_ptr;
}
```

**Problem:** Requires 66 PGs × multiple accessor variants = hundreds of definitions

**Estimate:** 8-12 hours to implement all variants

### Solution B: Manual Upfront Allocation (Original Phase 3 Plan)

**Abandon lazy allocation, allocate everything at boot:**

```c
// In wasm_pg_init.c
#ifdef __EMSCRIPTEN__
// Manually allocate storage for all 66 PGs
static systemConfig_t systemConfig_System_storage;
static systemConfig_t systemConfig_Copy_storage;
// ... 64 more PGs

void wasmPgInitAll(void) {
    // Point all registry entries to these allocations
    systemConfig_Registry.address = (uint8_t*)&systemConfig_System_storage;
    systemConfig_Registry.copy = (uint8_t*)&systemConfig_Copy_storage;
    // ... 64 more assignments

    // Then reset all to defaults
    pgResetAll(MAX_PROFILE_COUNT);
}
#endif
```

Then modify REGISTER macros to create proper extern symbols for WASM:

```c
#ifdef __EMSCRIPTEN__
#define PG_REGISTER_I(_type, _name, _pgn, _version, _reset) \
    extern _type _name ## _System;  /* Declare, allocated in wasm_pg_init.c */ \
    extern _type _name ## _Copy;    \
    extern const pgRegistry_t _name ## _Registry;
#else
    // Native: allocate globals inline
    _type _name ## _System;
    _type _name ## _Copy;
    // ...
#endif
```

**Problem:** Requires listing all 66 PGs manually
**Benefit:** Zero code changes outside parameter_group system
**Estimate:** 6-8 hours

### Solution C: Hybrid Approach (RECOMMENDED)

**Combine the best of both:**

1. **Keep lazy allocation runtime** - wasmPgEnsureAllocated() works great
2. **Provide extern symbol redirects** - for backwards compat with backdoor accessors
3. **Script-generate the externs** - from PG registry (already have this data)

```c
// In generated wasm_pg_externs.c:
#ifdef __EMSCRIPTEN__
// Generated for each PG:
_type *_name ## _System_ptr = NULL;
_type *_name ## _Copy_ptr = NULL;

// Externs declared in wasm_pg_externs.h:
#define _name ## _System (*_name ## _System_ptr_get())
#define _name ## _Copy (*_name ## _Copy_ptr_get())

static inline _type* _name ## _System_ptr_get(void) {
    if (!_name ## _System_ptr) {
        wasmPgEnsureAllocated(&_name ## _Registry);
        _name ## _System_ptr = (type*)_name ## _Registry.address;
        _name ## _Copy_ptr = (_type*)_name ## _Registry.copy;
    }
    return _name ## _System_ptr;
}
// ... repeat for all 66 PGs
#endif
```

**Benefits:**
- Accessors work (lazy allocation)
- Backdoors work (macro redirects)
- Can be script-generated (no manual listing)
- Preserves the abstraction insight

**Estimate:** 4-6 hours

---

## Architectural Lessons Learned

### 1. Abstraction Layers Are Not Uniform

The PG system has multiple accessor layers:
- **Public API:** `systemConfig()` - well abstracted
- **Internal API:** `&systemConfig_Copy` - direct access
- **Debug/CLI API:** Direct struct field access

Only the top layer goes through the macro abstraction.

### 2. Copy Storage Pattern

**Purpose of Copy:**
- CLI `diff` command shows changes vs defaults
- Config rollback on validation failure
- Backup for  config corruption detection

**Usage pattern:**
```c
// Take snapshot before changes
memcpy(&config_Copy, config(), sizeof(config_t));

// Make changes
configMutable()->field = newValue;

// Compare or restore
if (changed) {
    printDiff(&config_Copy, config());
}
```

This pattern requires **copy to be an lvalue** (can take address).

### 3. The "Extern Everything" Anti-Pattern

Native builds make ALL internals extern:
```c
extern systemConfig_t systemConfig_System;  // Not just for internal use!
extern systemConfig_t systemConfig_Copy;     // CLI uses these directly
```

This breaks encapsulation but enables powerful debugging (CLI can inspect everything).

**Trade-off:** Flexibility vs. abstraction integrity

---

## Recommendation

**Choose Solution C (Hybrid):**

1. Keep the wasmPgEnsureAllocated() runtime (already implemented)
2. Generate WASM-specific extern symbol macros
3. Update PG_REGISTER macros to use externs for WASM
4. Script-generate the 66 PG extern definitions

**Rationale:**
- Preserves the elegant accessor insight
- Minimal code changes (just macro layer)
- Scriptable (no manual listing)
- Backwards compatible with all access patterns

**Time estimate:** 4-6 hours additional work

**Total Phase 3 time:** ~8-10 hours (2-3h done, 4-6h remaining)

---

## Alternative: Minimal Viable Product

**If time is constrained, use Solution B:**
- Manually allocate 66 PGs upfront
- Zero runtime overhead
- Works with all access patterns
- No macro cleverness needed

**Trade-off:** Loses the elegant abstraction, but ships faster

---

## Next Steps (Awaiting Approval)

1. **Decision:** Which solution to implement?
2. **If Hybrid (C):** Create script to generate extern redirects
3. **If Manual (B):** Create wasm_pg_init.c with manual allocations
4. **Test:** Build, load in browser, verify init succeeds
5. **Complete:** Phase 3 done, fully working WASM SITL

---

**Developer**
2025-12-02 2:30 PM

**Files Created This Session:**
- `src/main/config/parameter_group.h` - WASM accessor macros (modified)
- `src/main/target/SITL/wasm_pg_runtime.c` - Lazy allocator (created)
- `src/main/flight/mixer_profile.h` - Wrapped native-only accessor (modified)

**Build Status:** Compilation blocked on backdoor accessor incompatibility

**Attachments:**
- Build log showing 46 `_Copy` / `_CopyArray` errors in CLI alone
