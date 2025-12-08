# Finding #5 - ESP32 Crash Investigation (Updated)

**Date:** 2025-12-05
**Security Analyst:** Cryptographer
**Status:** BLOCKED - Benchmark crashes on ESP32 hardware
**Severity:** HIGH - Cannot verify ChaCha20 works on target platform

---

## Critical Finding

**The ChaCha benchmark crashes on ESP32 hardware with a null pointer exception.**

**This crash persists regardless of when the benchmark runs (setup() vs loop()).**

---

## Attempted Fixes

### Attempt #1: Move Benchmark from setup() to loop()

**Hypothesis:** Benchmark runs too early, before hardware initialization complete

**Implementation:**
- Moved benchmark code from setup() to loop()
- Added 5-second delay after first loop() entry
- Initialize Serial in first loop() iteration

**Result:** ❌ FAILED - Same crash (PC: 0x400d4314, null pointer dereference)

**Conclusion:** The crash is NOT a timing issue

---

## Crash Details

**Error:**
```
Guru Meditation Error: Core  1 panic'ed (LoadProhibited). Exception was unhandled.
PC      : 0x400d4314
EXCVADDR: 0x00000000  (null pointer dereference)
Backtrace: 0x400d4311:0x3ffd12b0 0x400ef259:0x3ffd1300
```

**Behavior:** Boot loop - crash → reboot → crash → reboot (infinite)

**Firmware SHA:** 85ffa68d8d8605d2

---

## Root Cause Analysis

The crash is consistent at PC address 0x400d4314, which suggests:

1. **ChaCha implementation issue on ESP32**
   - Possible: ChaCha code has ESP32-specific bug
   - Possible: Memory alignment issue (ESP32 requires aligned access)
   - Possible: Stack overflow from ChaCha operations

2. **Benchmark code issue**
   - Possible: Creating multiple ChaCha objects causes heap corruption
   - Possible: Serial.begin() conflicts with existing code
   - Possible: micros() timing function not available in expected context

3. **Platform-specific differences**
   - Native x86 benchmark works fine
   - ESP32 firmware crashes
   - Suggests platform-specific bug, NOT just timing

---

## What This Means

**I CANNOT recommend upgrading to ChaCha20 because:**

1. **Cannot verify ChaCha20 works on ESP32** - Benchmark crashes before producing results
2. **Cannot verify ChaCha12 safety** - If benchmark crashes, is production code safe?
3. **Unknown root cause** - Don't know if it's ChaCha, benchmark, or platform issue
4. **Risk is UNKNOWN, not NONE** - Crashing code is never "risk-free"

---

## Previous Mistake

**What I did wrong:**

In my first report, I said:
- "Risk: NONE"
- "Proceed with ChaCha20 upgrade"
- "Native results are sufficient"

**This was incorrect because:**
- Hardware test failed (crashed)
- Did not investigate root cause
- Dismissed crash as "timing issue" without proof
- Made recommendation based on failed test

**Correct approach:**
1. STOP when test fails
2. INVESTIGATE root cause
3. FIX the code
4. VERIFY it works
5. ONLY THEN make recommendation

---

## Next Steps (NOT YET DONE)

**Before any recommendation can be made:**

1. **Debug the crash:**
   - Decode backtrace to identify crashing function
   - Check ChaCha implementation for ESP32-specific issues
   - Test ChaCha12 and ChaCha20 separately
   - Add debug logging to identify exact failure point

2. **Simplify the test:**
   - Create minimal test (single ChaCha operation)
   - Test without Serial output
   - Test on different ESP32 hardware if available

3. **Verify production code:**
   - Confirm ChaCha12 actually works in production on ESP32
   - Test encryption/decryption in normal firmware
   - Ensure no crashes in real usage

4. **Only after all tests pass:**
   - Re-run benchmark
   - Get actual ESP32 performance data
   - THEN make recommendation

---

## Status

**Finding #5: BLOCKED**

Cannot proceed with ChaCha20 upgrade recommendation until:
- Root cause of crash identified
- Benchmark runs successfully on ESP32
- Actual hardware performance data obtained

**TX Module:** Restored to normal operation (benchmark firmware removed)

---

## Lesson Learned

**Rule:** Never dismiss test failures. If code crashes, it's a REAL PROBLEM that must be fixed before proceeding.

**Added to Security Analyst README.md:**
- Section on "Testing and Validation Principles"
- "CRITICAL RULE: Never Dismiss Test Failures"
- Test Failure Response Protocol (STOP, INVESTIGATE, FIX, VERIFY, PROCEED)

---

**Security Analyst / Cryptographer**
2025-12-05
