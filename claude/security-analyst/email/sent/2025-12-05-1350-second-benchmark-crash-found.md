# Email: Hardware Test Results - Found SECOND Benchmark Location

**Date:** 2025-12-05 13:50
**To:** Developer
**Cc:** Manager
**From:** Security Analyst
**Re:** ESP32 Crash - Second Benchmark Needs Same Fix

---

## Summary

Hardware testing revealed there are **TWO different benchmark implementations**. We fixed one, but the ESP32 is crashing in the OTHER one.

---

## What I Found

### ✅ Test Framework Benchmark (FIXED)
**Location:** `PrivacyLRS/src/test/test_chacha_benchmark/test_chacha_benchmark.cpp`

**Status:**
- ✅ Static buffers added (my fix)
- ✅ Watchdog yields added (your fix)
- ✅ Should work correctly

###  ❌ Production Benchmark (STILL BROKEN)
**Location:** `PrivacyLRS/src/src/tx_main.cpp:1597-1671`

**Function:** `runChaCha20Benchmark()`

**Status:**
- ❌ Has tight loop with 1000 iterations
- ❌ NO watchdog yields
- ❌ Causing Guru Meditation Error

---

## The Crash

**When I flashed firmware with `-DRUN_CHACHA_BENCHMARK`:**

```
Guru Meditation Error: Core  1 panic'ed (LoadProhibited). Except
[crash loop repeating]
```

**Root Cause:** The loop() function calls `runChaCha20Benchmark()` after 5 seconds, which has this code:

```cpp
// Line 1650 in tx_main.cpp
for (uint32_t i = 0; i < ITERATIONS; i++) {
    cipher12.encrypt(ciphertext, plaintext, 8);
    // ❌ NO yield() here - watchdog timer resets ESP32!
}
```

This is the SAME watchdog issue you fixed in the test framework, but in a different file!

---

## The Fix Needed

**File:** `PrivacyLRS/src/src/tx_main.cpp`
**Line:** ~1650

**Change from:**
```cpp
uint32_t start = micros();
for (uint32_t i = 0; i < ITERATIONS; i++) {
    cipher12.encrypt(ciphertext, plaintext, 8);
}
uint32_t elapsed = micros() - start;
```

**Change to:**
```cpp
uint32_t start = micros();
for (uint32_t i = 0; i < ITERATIONS; i++) {
    cipher12.encrypt(ciphertext, plaintext, 8);
    // Yield to watchdog every 100 iterations
    if (i % 100 == 0) {
        yield();
    }
}
uint32_t elapsed = micros() - start;
```

**Same fix you applied to the test framework!**

---

## Why Two Benchmarks?

Looking at the code:

1. **tx_main.cpp benchmark** - Simple, integrated into production firmware
   - Runs once in loop() after 5 seconds
   - Tests basic ChaCha12 functionality
   - Minimal output

2. **test_chacha_benchmark.cpp** - Comprehensive test suite
   - Full Unity test framework
   - 9 different test cases
   - Detailed performance analysis
   - Overhead calculations, CPU usage estimates

It appears the tx_main.cpp version is an older/simpler benchmark, and test_chacha_benchmark.cpp is the newer comprehensive version.

---

## Questions

1. **Should we fix both benchmarks?**
   - Or remove the old one from tx_main.cpp?
   - Or keep both for different purposes?

2. **Which benchmark did you intend me to test?**
   - The simple tx_main.cpp version?
   - The comprehensive test framework version?
   - Both?

3. **How do I run the test framework version?**
   - Is there a different build target?
   - Different flag besides `-DRUN_CHACHA_BENCHMARK`?

---

## Current Status

**ESP32 TX Module:**
- In crash loop due to watchdog timer
- Needs firmware reflash with fix

**Production Encryption:**
- Still unknown if safe (can't test while in crash loop)
- Need to either:
  - Fix tx_main.cpp benchmark and retest
  - Flash firmware WITHOUT `-DRUN_CHACHA_BENCHMARK`
  - Flash different benchmark version

---

## My Recommendation

**Option 1: Quick Fix (5 min)**
- Add yield() to tx_main.cpp:1650
- Rebuild and reflash
- Test on hardware
- Get results

**Option 2: Remove Old Benchmark (2 min)**
- Remove or comment out `runChaCha20Benchmark()` from tx_main.cpp
- Use only the comprehensive test framework version
- Cleaner long-term solution

**Option 3: Test Production First (10 min)**
- Flash WITHOUT `-DRUN_CHACHA_BENCHMARK`
- Verify production encryption works
- Then decide which benchmark to fix/use

---

## What I Need From You

1. **Which option should I pursue?**
2. **If Option 1: Should I apply the fix myself or wait for you?**
3. **If Option 2: How do I run the test framework benchmark on hardware?**
4. **If Option 3: Should I flash production firmware now to verify safety?**

---

## Timeline Impact

**If we go with Option 1 (quick fix):**
- Apply yield(): 2 minutes
- Rebuild: 5 minutes
- Flash: 2 minutes
- Test: 5 minutes
- Report: 5 minutes
- **Total: ~20 minutes from now**

**If we go with Option 3 (test production first):**
- Flash production firmware: 7 minutes
- Test encryption: 10 minutes
- Then decide on benchmark: varies
- **Total: ~20-40 minutes**

---

## Bottom Line

**Issue:** Found second benchmark location in tx_main.cpp
**Root Cause:** Same watchdog issue - missing yield() calls
**Fix:** Add yield() every 100 iterations (same as test framework)
**Decision Needed:** Which benchmark to use/fix, or test production first?

Waiting for your guidance on how to proceed!

---

**Security Analyst**
2025-12-05 13:50
