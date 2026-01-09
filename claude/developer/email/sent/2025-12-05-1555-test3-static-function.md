# Email: TEST 3 - Static Linkage (Last Simple Test)

**Date:** 2025-12-05 15:55
**To:** Security Analyst
**From:** Developer
**Cc:** Manager
**Subject:** Testing Static Linkage - Then We Escalate To Manager

---

## Summary

Test 2's failure was shocking - it's NOT the function name. I have one more simple test before we need to escalate this to the Manager for build system investigation.

**Test 3:** Static function (file-local linkage)

---

## What This Tests

**Function:**
```cpp
static void testBenchmarkFunc()
{
    // Empty
}
```

**Change:** Added `static` keyword

**What static does:**
- Makes function file-local (not exported as global symbol)
- Prevents linker from putting it in global symbol table
- Should eliminate any cross-file conflicts

---

## Why This Might Work

**If the problem is symbol table related:**
- `static` makes the function invisible to linker
- No global symbol = no conflict possible
- ESP32 boot process won't see this symbol

**This would suggest:**
- NOT about the code itself
- NOT about the function name specifically
- ABOUT how symbols are processed during ESP32 boot

---

## Expected Results

### If Static Function WORKS:

**Conclusion:** The problem is GLOBAL SYMBOL VISIBILITY!

**Root Cause:** Something about exporting a global function symbol when `-DRUN_CHACHA_BENCHMARK` is set crashes ESP32 boot process

**Fix:** Use `static` for benchmark function:
```cpp
#ifdef RUN_CHACHA_BENCHMARK
static void runChaCha20Benchmark() {
    // Full benchmark code
}
#endif
```

---

### If Static Function STILL CRASHES:

**Conclusion:** The problem is DEEPER than we can debug at the code level.

**This means:**
- NOT the code
- NOT the function name
- NOT the linkage
- SOMETHING ABOUT THE BUILD/COMPILE/LINK PROCESS ITSELF

**Action Required:** **ESCALATE TO MANAGER**

**Manager needs to investigate:**
1. PlatformIO build configuration
2. Linker scripts for ESP32
3. Memory layout with vs. without benchmark flag
4. Compiler optimization settings
5. Whether this is a known ESP32 toolchain issue

---

## If Test 3 Fails - What I'll Send To Manager

**Email Subject:** "CRITICAL: ESP32 Build System Issue - Unable to Add ANY Function With Benchmark Flag"

**Summary for Manager:**
- ✅ Production firmware works fine
- ❌ Adding ANY function under `#ifdef RUN_CHACHA_BENCHMARK` crashes ESP32 at boot
- ❌ NOT the function code (empty function crashes)
- ❌ NOT the function name (renamed function crashes)
- ❌ NOT UART references (no UART code crashes)
- ❌ NOT linkage (if Test 3 fails)

**Hypothesis:** Build system or ESP32 toolchain issue when `-DRUN_CHACHA_BENCHMARK` flag is set

**Request:** Manager to review:
- platformio.ini configuration
- ESP32 linker configuration
- Whether Unified build compiles both TX and RX into same binary
- Memory map differences with/without flag

---

## Testing Instructions

```bash
cd PrivacyLRS/src
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DUSE_ENCRYPTION -DRUN_CHACHA_BENCHMARK" \
  pio run -e Unified_ESP32_2400_TX_via_UART --target upload

stty -F /dev/ttyUSB0 115200
timeout 30 cat /dev/ttyUSB0 | tee test3_static_function_output.txt
```

---

## My Prediction

**I honestly don't know anymore.**

**My track record on predictions:** 0 for 3
- Round 1: ❌ Wrong
- Option A: ❌ Wrong
- Test 1: ❌ Wrong
- Test 2: ❌ Wrong

**Confidence:** 50% (no idea which way this will go)

---

## The Debugging Journey So Far

**3 hours of systematic elimination:**

1. ❌ ChaCha operations
2. ❌ Loop timing code
3. ❌ LOGGING_UART references
4. ❌ Function name conflict
5. ❓ Global symbol visibility (Test 3)
6. ❓ Build system configuration (if Test 3 fails)

**We've been methodical and systematic, but the problem keeps being deeper than expected.**

---

## Files Changed

**File:** `PrivacyLRS/src/src/tx_main.cpp`

**Lines 1597-1603:** Added `static` keyword to function

---

## Timeline

**Test 3:** 10 min (this test)
**If successful:** 30 min to implement full benchmark with static
**If unsuccessful:** Escalate to Manager for build system investigation

---

## Bottom Line

**Test:** Empty function with `static` keyword
**Purpose:** Test if global symbol visibility is the issue
**Prediction:** 50/50 - no confidence either way
**If fails:** ESCALATE TO MANAGER - this is beyond code-level debugging

**This is our last simple test before we need build system expertise.**

---

**Developer**
2025-12-05 15:55
