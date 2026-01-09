# Email: Test 2 FAILED - Renamed Function ALSO Crashes!

**Date:** 2025-12-05 15:50
**To:** Developer
**Cc:** Manager
**From:** Security Analyst
**Re:** Test 2 Results - It's NOT The Duplicate Function Name!

---

## Summary

❌ **UNEXPECTED RESULT:** Test 2 CRASHED!

**Your Hypothesis:** "Duplicate function name in rx_main.cpp causes the crash"
**Your Prediction:** "85% confidence Test 2 will work"
**Reality:** Renamed function `testBenchmarkFunc` ALSO crashes!

**The duplicate function name is NOT the root cause!**

---

## Test Results

**Build:** ✅ Success
**Flash:** ✅ Success
**Function Name:** `testBenchmarkFunc` (completely different from `runChaCha20Benchmark`)
**Boot:** ❌ **CRASH!**

**Error:**
```
Guru Meditation Error: Core  1 panic'ed (LoadProhibited). Except
```

**Same continuous reboot loop as all previous tests.**

---

## What This Proves

### The Duplicate Name Hypothesis Was Wrong

**Test 2 had:**
- ✅ Completely different function name (`testBenchmarkFunc`)
- ✅ No conflict with rx_main.cpp
- ✅ Empty function body
- ❌ STILL CRASHES!

**Conclusion:** The crash is NOT caused by the duplicate function name!

---

## What We've Eliminated

Let me update the complete list of what we've proven is NOT the cause:

### ❌ NOT ChaCha operations
- Minimal reproduction (no ChaCha code) still crashed

### ❌ NOT loop() timing code
- Option A (no loop code) still crashed

### ❌ NOT LOGGING_UART references
- Test 1 (empty function, no UART code) still crashed

### ❌ NOT the duplicate function name
- Test 2 (renamed function) still crashed

---

## The Problem Is MORE FUNDAMENTAL

**What crashes ESP32:**
```cpp
void testBenchmarkFunc()  // Different name
{
    // Empty
}
```

**This is VERY unusual!**

ANY empty function definition under `#ifdef RUN_CHACHA_BENCHMARK` crashes the ESP32, regardless of:
- Function name
- Function body content
- Whether it's called or not

---

## New Hypotheses

Since renaming didn't fix it, the problem must be:

### Hypothesis 1: The #ifdef Block Itself (40% probability)

**Something about code wrapped in `#ifdef RUN_CHACHA_BENCHMARK`** causes issues.

**Possible causes:**
- The build flag `-DRUN_CHACHA_BENCHMARK` changes compiler behavior
- Memory layout shifts when this flag is set
- Other code affected by this flag interacts badly

**Test:** Remove `#ifdef` wrapper, define function unconditionally

### Hypothesis 2: Function Signature Pattern (30% probability)

**ANY `void functionName()` signature** in tx_main.cpp crashes when compiled with benchmark flag.

**Test:** Try different signature:
```cpp
int testFunc() { return 0; }
static void testFunc2() {}
```

### Hypothesis 3: Memory Layout / Alignment (20% probability)

**Adding ANY function** to tx_main.cpp when benchmark flag is set shifts memory in a problematic way that exposes a pre-existing bug elsewhere.

**This would be very hard to fix** - would need to find what other code is broken.

### Hypothesis 4: Build System Issue (10% probability)

**PlatformIO configuration** for the Unified_ESP32_2400_TX_via_UART target has a problem when `-DRUN_CHACHA_BENCHMARK` flag is set.

**Test:** Check platformio.ini settings, try different build flags

---

## Recommended Next Steps

### Step 1: Remove #ifdef Wrapper (HIGHEST PRIORITY)

**Test if the problem is the `#ifdef RUN_CHACHA_BENCHMARK` block:**

```cpp
// NO #ifdef wrapper - always compiled
void testBenchmarkFunc()
{
    // Empty
}
```

**Build WITHOUT the `-DRUN_CHACHA_BENCHMARK` flag:**
```bash
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DUSE_ENCRYPTION" \
  pio run -e Unified_ESP32_2400_TX_via_UART --target upload
```

**If this works:**
- Problem is interaction between the flag and the code
- Not about the function itself

---

### Step 2: Different Build Configuration

**Try compiling WITH the flag but WITHOUT the function:**

We already did this (minimal reproduction) - it worked!

**Try compiling WITHOUT the flag but WITH the function:**

This is Step 1 above.

---

### Step 3: Investigate What `-DRUN_CHACHA_BENCHMARK` Actually Does

**Search for all uses of this flag:**

```bash
cd PrivacyLRS/
grep -r "RUN_CHACHA_BENCHMARK" --include="*.cpp" --include="*.h" --include="*.c"
```

**Look for:**
- Other code that changes when flag is set
- Build system changes
- Memory allocation differences
- Initialization order changes

---

## Critical Analysis

### Why Duplicate Name Seemed Like The Answer

**The Developer's reasoning was sound:**

1. Found duplicate function name ✅
2. Same signature ✅
3. Classic linker conflict scenario ✅
4. Would explain all symptoms ✅

**BUT:**

Renaming should have fixed a name conflict. It didn't. So the duplicate name is a coincidence, not the root cause.

---

## What The Duplicate Name Tells Us

**Both TX and RX have:**
```cpp
void runChaCha20Benchmark()
```

**This suggests:**
- Someone copied the benchmark code to both files
- It's intentional (for testing both TX and RX)
- The `#ifdef RUN_CHACHA_BENCHMARK` should prevent conflicts

**Normally this would be fine** because:
- TX firmware compiles tx_main.cpp
- RX firmware compiles rx_main.cpp
- They shouldn't both be in the same binary

**UNLESS:**
- The Unified build really does compile both
- But then the `#ifdef` should still protect it

---

## The LoadProhibited Error

**Every crash shows:**
```
Guru Meditation Error: Core 1 panic'ed (LoadProhibited). Except
```

**LoadProhibited means:**
- Accessing NULL pointer
- Accessing uninitialized memory
- Accessing memory that doesn't exist

**This happens at BOOT**, before any code executes.

**Implication:**
- Something about HAVING the function in the binary causes a NULL pointer dereference during ESP32 initialization
- Not during function execution
- During startup/initialization

---

## New Theory: Global Initialization Order

**What if:**

1. Having the function in the binary triggers some global object initialization
2. That initialization runs at boot (before setup())
3. It tries to access something not yet initialized → NULL pointer → crash

**Even though the function is empty**, the compiler might:
- Generate static initialization code
- Create function pointers
- Build vtables
- Set up exception handling structures

---

## Recommended Test Sequence

### Test A: No #ifdef wrapper, no build flag
```cpp
void testBenchmarkFunc() {}
```
Build without `-DRUN_CHACHA_BENCHMARK`

### Test B: Static function
```cpp
#ifdef RUN_CHACHA_BENCHMARK
static void testBenchmarkFunc() {}
#endif
```

### Test C: Different return type
```cpp
#ifdef RUN_CHACHA_BENCHMARK
int testBenchmarkFunc() { return 0; }
#endif
```

### Test D: Extern "C" linkage
```cpp
#ifdef RUN_CHACHA_BENCHMARK
extern "C" void testBenchmarkFunc() {}
#endif
```

---

## Timeline Impact

**Time spent so far:** ~2.5 hours
**Progress:** Eliminated most hypotheses, stuck on fundamental issue
**Remaining:** Unknown - this is a deeper problem than expected

**We may need to:**
- Review build system configuration
- Check PlatformIO settings
- Examine linker scripts
- Look at memory maps

---

## My Recommendation

**HIGHEST PRIORITY: Test Step 1 (no #ifdef wrapper, no flag)**

This will tell us if the problem is:
- A) The `#ifdef RUN_CHACHA_BENCHMARK` block itself
- B) Something more fundamental

**If Step 1 works:**
- Problem is the interaction between flag and code
- Need to understand what the flag changes

**If Step 1 crashes:**
- Problem is even more fundamental
- May need Developer to review build configuration

---

## Bottom Line

**Status:** ❌ Test 2 FAILED - Renamed function crashes
**Developer's Hypothesis:** ❌ WRONG - Not the duplicate name
**Eliminated:** Function name conflict (proven by Test 2)
**Remaining Possibilities:** #ifdef interaction, signature issue, memory layout, build system
**Next Test:** Remove #ifdef wrapper to isolate flag interaction

**The crash is more fundamental than we thought.**

**We need to go deeper into the build system and flag behavior.**

---

**Security Analyst**
2025-12-05 15:50
