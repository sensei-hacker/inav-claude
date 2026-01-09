# Email: TEST 1 - Completely Empty Function

**Date:** 2025-12-05 15:30
**To:** Security Analyst
**From:** Developer
**Cc:** Manager
**Subject:** The Most Diagnostic Test - Is It The Function Or The Code Inside?

---

## Summary

Option A's crash was shocking but incredibly informative! Loop code is innocent. Now testing Test 1.

**Test 1:** Absolutely empty function - just the definition, nothing inside.

---

## What This Test Does

**The Function:**
```cpp
void runChaCha20Benchmark()
{
    // Absolutely nothing - empty function body
}
```

**What's Included:**
- ✅ Function name: `runChaCha20Benchmark`
- ✅ Function signature: `void ()`
- ✅ Empty body
- ❌ NO LOGGING_UART references
- ❌ NO code execution
- ❌ NO variable declarations
- ❌ NO operations whatsoever

**Loop Code:** Still disabled (from Option A)

---

## Why This Is The Most Important Test

**This will definitively answer:**

**Is the crash from:**
- A) The function definition itself (name, signature, linkage)?
- B) The LOGGING_UART code inside the function?

**One of these MUST be true.**

---

## Expected Results

### Scenario A: Empty Function WORKS

**If ESP32 boots successfully:**

**Conclusion:** The crash is from the LOGGING_UART.println() code inside the function!

**Why this would happen:**
- Referencing LOGGING_UART in an unused function triggers initialization
- Object lifetime issues with LOGGING_UART
- Stream object constructor/destructor problems

**Next Test:** Verify by adding simple code that doesn't use LOGGING_UART:
```cpp
void runChaCha20Benchmark() {
    volatile int x = 42;  // Simple operation
}
```

---

### Scenario B: Empty Function CRASHES

**If ESP32 still crashes:**

**Conclusion:** The function definition ITSELF causes the crash!

**This would be VERY unusual!**

**Possible causes:**
1. **Function name conflict** - "runChaCha20Benchmark" collides with something
2. **Compiler bug** - Toolchain generates bad code for this signature
3. **Memory layout** - Adding ANY function at this location breaks something
4. **Linker issue** - Symbol table corruption

**Next Tests:**
- Test 2: Rename function
- Test 3: Change signature
- Test 4: Add `static` keyword

---

## My Prediction

**I think Test 1 will WORK.**

**Reasoning:**

The LOGGING_UART hypothesis makes the most sense:

**Evidence supporting LOGGING_UART as culprit:**

1. **LOGGING_UART is a reference to TxBackpack stream** (from logging.h line 33)
2. **TxBackpack is initialized in setupHardwareFromOptions()**
3. **Unused function with UART reference might trigger early initialization**
4. **ESP32 crashes before setupHardwareFromOptions() completes**

**The sequence:**
```
Boot → Global init → setup() starts →
Compiler/linker tries to prepare runChaCha20Benchmark →
Sees LOGGING_UART reference → Tries to access TxBackpack →
TxBackpack not initialized yet → NULL pointer → CRASH
```

**Even though the function is never called**, the compiler might generate initialization code or object references that try to access LOGGING_UART at boot time.

---

## Testing Instructions

```bash
cd PrivacyLRS/src
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DUSE_ENCRYPTION -DRUN_CHACHA_BENCHMARK" \
  pio run -e Unified_ESP32_2400_TX_via_UART --target upload

stty -F /dev/ttyUSB0 115200
timeout 30 cat /dev/ttyUSB0 | tee test1_empty_function_output.txt
```

---

## Decision Tree

```
Test 1: Empty Function
│
├─ WORKS → Crash is from LOGGING_UART code
│          │
│          ├─ Test: Add simple non-UART code
│          │  └─ If works → CONFIRMED: LOGGING_UART is the problem
│          │
│          └─ Fix: Don't use LOGGING_UART in this function
│                   Use different output method or work around
│
└─ CRASHES → Crash is from function definition itself
             │
             ├─ Test 2: Rename function
             ├─ Test 3: Change signature
             ├─ Test 4: Add static keyword
             └─ Test 5: Workarounds
```

---

## If Empty Function Works - Next Steps

**Proven:** LOGGING_UART references in unused functions crash ESP32

**Root Cause:** Accessing stream objects before hardware initialization

**Solutions:**

**Option 1:** Don't use LOGGING_UART in benchmark function
```cpp
void runChaCha20Benchmark() {
    // Use Serial directly instead
    Serial.println("Benchmark starting");
}
```

**Option 2:** Ensure function is only compiled if actually used
```cpp
#ifdef RUN_CHACHA_BENCHMARK
__attribute__((used))  // Force linker to keep it
static void runChaCha20Benchmark() {
    LOGGING_UART.println("...");
}
#endif
```

**Option 3:** Delay UART access until function is actually called
```cpp
void runChaCha20Benchmark() {
    // LOGGING_UART safe to use here because function is called
    // AFTER setupHardwareFromOptions() completes
    LOGGING_UART.println("...");
}
```

Wait - that SHOULD already work since the function is only called after initialization... unless there's something about having the reference in the code that triggers early initialization.

---

## If Empty Function Crashes - Next Steps

**This would indicate a deeper issue:**

**Test 2: Different Name**
```cpp
void testFunc() {  // Completely different name
    // empty
}
```

**Test 3: Static Linkage**
```cpp
static void runChaCha20Benchmark() {
    // empty
}
```

**Test 4: Different Return Type**
```cpp
int runChaCha20Benchmark() {
    return 0;
}
```

---

## Files Changed

**File:** `PrivacyLRS/src/src/tx_main.cpp`

**Lines 1597-1603:** Empty function definition
**Loop code:** Still disabled from Option A (lines 1706-1734)

---

## Confidence Level

**Test Quality:** 100% - This WILL tell us if it's the function def or the UART code
**Prediction Confidence:** 75% - I think it's LOGGING_UART, but could be wrong
**Time to Answer:** 10 minutes

---

## What We'll Know After This Test

**If it works:**
- ✅ Function definition is fine
- ✅ Name/signature/linkage is fine
- ❌ LOGGING_UART reference is the problem
- 🎯 Next: Find workaround for UART access

**If it crashes:**
- ❌ Function definition itself is broken
- 🎯 Next: Try different names/signatures/attributes

**Either way, we'll know EXACTLY what to fix!**

---

## Timeline

**Test 1:** 10 min (this test)
**Follow-up:** 10-20 min (based on results)
**Total:** 20-30 min to find solution

---

## Bottom Line

**Test:** Completely empty function
**Purpose:** Isolate function definition vs. LOGGING_UART code
**Prediction:** Will work (LOGGING_UART is the culprit)
**Impact:** Will tell us exactly how to fix the issue

**This is the most diagnostic test yet!**

---

**Developer**
2025-12-05 15:30
