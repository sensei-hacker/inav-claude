# Email: TEST 2 - Renamed Function (The Smoking Gun Test)

**Date:** 2025-12-05 15:45
**To:** Security Analyst
**From:** Developer
**Cc:** Manager
**Subject:** The Most Critical Test - Is It The Function Name?

---

## Summary

Test 1's crash of an empty function was shocking! LOGGING_UART is innocent. Now testing if the name itself is the problem.

**Test 2:** Same empty function, completely different name.

---

## What I Found BEFORE Creating Test 2

**I searched the codebase for "runChaCha20Benchmark":**

```bash
grep -r "runChaCha20Benchmark" --include="*.cpp" --include="*.h"
```

**Result:**
```
src/src/tx_main.cpp:void runChaCha20Benchmark()
src/src/rx_main.cpp:void runChaCha20Benchmark()
```

**THERE'S ANOTHER FUNCTION WITH THE SAME NAME IN rx_main.cpp!**

---

## The Duplicate Function

**File:** `rx_main.cpp` (RX firmware, not TX)
**Line:** 2183

**Both files define:**
```cpp
void runChaCha20Benchmark()
```

**BUT:** We're building TX firmware, so rx_main.cpp shouldn't be compiled...

**UNLESS:** Both TX and RX files are being linked together somehow, causing a symbol conflict!

---

## Test 2: Different Name

**Old Name (crashed):**
```cpp
void runChaCha20Benchmark()
{
    // empty
}
```

**New Name (testing):**
```cpp
void testBenchmarkFunc()
{
    // empty
}
```

**Changes:**
- Function renamed from `runChaCha20Benchmark` to `testBenchmarkFunc`
- Still completely empty
- Still wrapped in `#ifdef RUN_CHACHA_BENCHMARK`
- Loop code still disabled (from Option A)

---

## Expected Results

### If Renamed Function WORKS:

**Conclusion:** ✅ CONFIRMED! The name "runChaCha20Benchmark" conflicts with rx_main.cpp!

**Root Cause:** Duplicate symbol in linker

**Why this causes crash:**
- TX and RX files both compiled into same binary (or linked together)
- Two functions with identical name
- Linker creates corrupted symbol table
- ESP32 tries to call function → jumps to wrong address → crash

**Fix:** Rename the TX version to something unique:
```cpp
void txRunChaCha20Benchmark()  // Add tx_ prefix
// OR
void runChaCha12BenchmarkTX()  // Add TX suffix
```

---

### If Renamed Function STILL CRASHES:

**Conclusion:** It's NOT the name

**Next Tests:**
- Try `static void testBenchmarkFunc()` (change linkage)
- Try different signature
- Check if ANY function definition causes crash
- Investigate memory layout issues

---

## Why TX and RX Might Be Linked Together

**Possible build configurations:**

1. **Unified build system** - Compiles both TX and RX into same binary, selects at runtime
2. **Shared object files** - Some .o files include symbols from both
3. **Library compilation** - Both files compiled into a library together
4. **PlatformIO configuration** - Build system includes both source files

**This would explain:**
- Why defining a function in TX crashes
- Why the same name exists in RX
- Why renaming will likely fix it

---

## Testing Instructions

```bash
cd PrivacyLRS/src
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DUSE_ENCRYPTION -DRUN_CHACHA_BENCHMARK" \
  pio run -e Unified_ESP32_2400_TX_via_UART --target upload

stty -F /dev/ttyUSB0 115200
timeout 30 cat /dev/ttyUSB0 | tee test2_renamed_function_output.txt
```

---

## My Prediction

**I predict Test 2 will WORK.**

**Confidence:** 85% (higher than before!)

**Reasoning:**

1. **Found duplicate function name** in rx_main.cpp
2. **Same exact signature** `void runChaCha20Benchmark()`
3. **Classic linker symbol conflict** scenario
4. **Renaming eliminates the conflict**

**This explains EVERYTHING:**
- Why minimal reproduction worked (no function defined)
- Why Round 1 crashed (function defined)
- Why Option A crashed (unused function still in symbol table)
- Why Test 1 crashed (empty function still conflicts)

**The ESP32 wasn't crashing because of our CODE - it was crashing because of a DUPLICATE SYMBOL!**

---

## If Test 2 Works - The Complete Solution

**Proven:** Function name conflict between tx_main.cpp and rx_main.cpp

**Permanent Fix:**

**Option A: Add Prefix (Recommended)**
```cpp
// In tx_main.cpp
#ifdef RUN_CHACHA_BENCHMARK
void txRunChaCha20Benchmark()  // tx_ prefix
{
    LOGGING_UART.println("ChaCha12 Benchmark Starting...");
    // ... rest of benchmark code ...
}
#endif
```

**Option B: Add Suffix**
```cpp
void runChaCha20Benchmark_TX()  // _TX suffix
```

**Option C: Use Namespace**
```cpp
namespace tx {
    void runChaCha20Benchmark()
    {
        // ...
    }
}
```

**Option D: Make Static (File-local)**
```cpp
static void runChaCha20Benchmark()  // Only visible in tx_main.cpp
```

---

## Why I Didn't Catch This Earlier

**Hindsight analysis:**

I SHOULD have searched for name conflicts immediately when the function definition crashed. The clues were there:

1. **Empty function crashes** → Must be name/symbol issue
2. **TX firmware project** → Might include RX files
3. **Unified target name** → "Unified_ESP32" suggests both TX and RX

**Lesson learned:** When function definition itself crashes, always check for duplicate symbols FIRST!

---

## Files Changed

**File:** `PrivacyLRS/src/src/tx_main.cpp`

**Lines 1597-1603:** Function renamed to `testBenchmarkFunc`

---

## Timeline

**Test 2:** 10 min (this test)
**If successful:** 5 min to implement permanent fix with proper name
**Total:** 15 min to complete solution

---

## The Full Debug Journey

**2+ hours of debugging led us here:**

1. ❌ "It's the ChaCha operations" → NO
2. ❌ "It's the Serial/UART init" → NO
3. ❌ "It's the loop timing code" → NO
4. ❌ "It's LOGGING_UART references" → NO
5. ✅ "It's a duplicate function name!" → **YES! (probably)**

**We eliminated everything systematically until only one possibility remained.**

---

## Confidence Level

**Test Quality:** 100% - This WILL tell us if it's the name
**Prediction Confidence:** 85% - Very likely it's the duplicate name
**Time to Solution:** 15 minutes if prediction is correct

---

## Bottom Line

**Test:** Empty function with different name (`testBenchmarkFunc`)
**Purpose:** Confirm function name conflict hypothesis
**Prediction:** Will work (85% confidence)
**Root Cause:** Duplicate `runChaCha20Benchmark` in tx_main.cpp and rx_main.cpp
**Fix:** Rename TX version with tx_ prefix or make it static

**If this works, we've found the root cause and can implement the full benchmark in 15 minutes!**

---

**Developer**
2025-12-05 15:45
