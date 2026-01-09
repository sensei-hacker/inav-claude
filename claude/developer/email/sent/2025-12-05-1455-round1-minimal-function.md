# Email: BINARY SEARCH - Round 1: Minimal Function Test

**Date:** 2025-12-05 14:55
**To:** Security Analyst
**From:** Developer
**Cc:** Manager
**Subject:** Round 1 - Testing if Function Can Be Called At All

---

## Summary

Excellent work confirming the crash is in my code! Starting binary search now.

**Round 1 Test:** Minimal benchmark function with ONLY a print statement - no ChaCha code at all.

---

## What This Round Tests

**Function:**
```cpp
void runChaCha20Benchmark()
{
    LOGGING_UART.println("\n========================================");
    LOGGING_UART.println("ChaCha12 Benchmark - Starting");
    LOGGING_UART.println("========================================");
    LOGGING_UART.flush();
}
```

**Loop Code:** Enabled - calls the function after 5 seconds

**What's Included:**
- ✅ Function definition
- ✅ Function call from loop()
- ✅ LOGGING_UART output
- ❌ NO ChaCha objects
- ❌ NO encryption code
- ❌ NO complex operations

---

## Expected Results

### Scenario A: Works (Most Likely)

**If ESP32 boots and runs without crashing:**

**Expected Output:**
```
DEBUG: Waiting 5 seconds before benchmark...
[5 seconds pass]
DEBUG: About to call runChaCha20Benchmark()...

========================================
ChaCha12 Benchmark - Starting
========================================

DEBUG: runChaCha20Benchmark() RETURNED!
```

**Conclusion:** The crash is in the BODY of the benchmark function (ChaCha operations)

**Next Step:** Round 2 - Add variable declarations and ChaCha object creation

---

### Scenario B: Crashes (Unlikely)

**If ESP32 crashes when calling the function:**

**Conclusion:** Something about defining/calling the function itself causes issues

**Possible Causes:**
- Stack overflow from function call
- Name conflict with existing function
- Something very unusual

**Next Step:** Further investigation into function definition itself

---

## Testing Instructions

```bash
cd PrivacyLRS/src
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DUSE_ENCRYPTION -DRUN_CHACHA_BENCHMARK" \
  pio run -e Unified_ESP32_2400_TX_via_UART --target upload

stty -F /dev/ttyUSB0 115200
timeout 15 cat /dev/ttyUSB0 | tee round1_output.txt
```

**Wait at least 10 seconds** to see if:
1. Boot messages appear
2. "DEBUG: Waiting 5 seconds..." appears
3. After 5 more seconds, benchmark messages appear
4. "RETURNED!" message appears

---

## Binary Search Plan

### Round 1 (This Test): Minimal Function
- ✅ Function exists
- ✅ Function is called
- ❌ No actual benchmark code

### Round 2 (If Round 1 works): Add Declarations
```cpp
void runChaCha20Benchmark() {
    LOGGING_UART.println("Starting...");

    const uint8_t test_key[32] = { ... };
    const uint8_t test_nonce[8] = { ... };
    uint8_t plaintext[8] = { ... };
    uint8_t ciphertext[8];

    LOGGING_UART.println("Declarations OK");
}
```

### Round 3 (If Round 2 works): Add ChaCha Object
```cpp
void runChaCha20Benchmark() {
    // ... declarations ...

    ChaCha cipher12(12);  // ← Most likely culprit
    LOGGING_UART.println("ChaCha object created");
}
```

### Round 4 (If Round 3 works): Add Initialization
```cpp
void runChaCha20Benchmark() {
    // ... declarations & object ...

    cipher12.setKey(test_key, 32);
    cipher12.setIV(test_nonce, 8);
    cipher12.setCounter(test_counter, 8);

    LOGGING_UART.println("ChaCha initialized");
}
```

### Round 5 (If Round 4 works): Add Encryption
```cpp
void runChaCha20Benchmark() {
    // ... everything above ...

    cipher12.encrypt(ciphertext, plaintext, 8);
    LOGGING_UART.println("Single encryption OK");
}
```

### Round 6 (If Round 5 works): Add Loop
```cpp
void runChaCha20Benchmark() {
    // ... everything above ...

    for (uint32_t i = 0; i < 1000; i++) {
        cipher12.encrypt(ciphertext, plaintext, 8);
        if (i % 100 == 0) yield();
    }
    LOGGING_UART.println("Loop complete");
}
```

---

## My Prediction

**Round 1:** ✅ Will work (function call is fine)
**Round 2:** ✅ Will work (variable declarations are fine)
**Round 3:** ❌ Will CRASH (ChaCha object creation fails)

**Why I think ChaCha object creation will crash:**
1. We're creating it on the stack in a function
2. ChaCha constructor might allocate memory that fails
3. ESP32 might have issues with the crypto library initialization
4. The object might be too large for the function's stack frame

---

## Timeline

**Round 1:** 10 min (this test)
**Round 2:** 10 min (if Round 1 works)
**Round 3:** 10 min (if Round 2 works)
**Estimated total:** 30-60 minutes to find exact problematic line

---

## Files Changed

**File:** `PrivacyLRS/src/src/tx_main.cpp`

**Lines 1597-1606:** Minimal benchmark function
**Lines 1706-1732:** Loop code to call benchmark after 5 seconds

---

## What to Report

**Please send me:**

1. **Did it crash?** YES or NO
2. **If NO crash, what output did you see?**
3. **If crash, at what point?** (boot, after 5 seconds, during function call, etc.)

**Based on your answer, I'll prepare Round 2 immediately.**

---

## Bottom Line

**Test:** Minimal function with just print statements
**Purpose:** Verify function calling mechanism works
**Expected:** Should work fine
**Next:** Add actual benchmark code piece by piece

**This round should complete in ~10 minutes!**

---

**Developer**
2025-12-05 14:55
