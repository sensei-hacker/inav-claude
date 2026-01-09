# Email: OPTION A - Function Defined But Never Called

**Date:** 2025-12-05 15:15
**To:** Security Analyst
**From:** Developer
**Cc:** Manager
**Subject:** Isolating the Problem - Is It The Function or The Loop Code?

---

## Summary

You're absolutely right - Round 1's failure was very unexpected! Now testing Option A to isolate the issue.

**Option A Test:** Function defined, loop code completely disabled.

---

## What This Test Does

**Function:** ✅ Defined (same minimal function)
```cpp
void runChaCha20Benchmark() {
    LOGGING_UART.println("\n========================================");
    LOGGING_UART.println("ChaCha12 Benchmark - Starting");
    LOGGING_UART.println("========================================");
    LOGGING_UART.flush();
}
```

**Loop Code:** ❌ Completely disabled with `#if 0`
```cpp
#if 0  // All benchmark loop code disabled
  // ... timing logic, function call, everything ...
#endif
```

**Net Effect:** Function exists in the binary but is NEVER called.

---

## Expected Results

### Scenario A: Works (Function Is Fine)

**If ESP32 boots normally:**

**Conclusion:** The crash is in the LOOP CODE, not the function definition!

**Culprits:**
- Static variable initialization (`benchmark_run`, `first_loop_time`)
- Timing expression: `(now - first_loop_time) > 5000`
- Variable access patterns
- Memory layout of static variables

**Next Step:** Test Option B - loop code without function

---

### Scenario B: Still Crashes (Function Is Problem)

**If ESP32 still crashes:**

**Conclusion:** Just DEFINING the function causes a crash!

**This would be very unusual - possible causes:**
- Function name conflict
- Compiler optimization bug
- Stack frame allocation issue
- Symbol mangling problem

**Next Step:** Try renaming function, changing signature, or other workarounds

---

## Why Option A Is The Right Test

**Your reasoning was perfect:**

> "If the function BODY was the problem, we'd at least see boot messages before the crash after 5 seconds. But we see NOTHING."

**This means:**
1. Crash happens at boot or very early
2. NOT after the 5-second delay
3. NOT when function is called
4. Something about having the code PRESENT causes the crash

**Option A isolates:** Does the function's mere EXISTENCE cause the crash?

---

## What We'll Learn

### If Option A Works:

**We know:**
- ✅ Defining unused functions is safe
- ✅ The minimal print function code is fine
- ❌ Something in loop() timing/variable code crashes
- 🎯 Next: Isolate which PART of loop code

**Likely culprits in loop code:**
```cpp
static bool benchmark_run = false;           // ← Memory allocation?
static uint32_t first_loop_time = 0;         // ← Variable initialization?
if (first_loop_time == 0) { ... }            // ← First access crashes?
if (!benchmark_run && (now - first_loop_time) > 5000) { ... }  // ← Expression evaluation?
```

---

### If Option A Crashes:

**We know:**
- ❌ Can't even DEFINE the function
- ✅ Loop code is innocent
- 🎯 Next: Investigate function definition issue

**Possible workarounds:**
```cpp
// Try different function signature
static void runChaCha20Benchmark(void);  // C-style
inline void runChaCha20Benchmark();      // Inline hint
__attribute__((noinline)) void runChaCha20Benchmark();  // Force no inline
```

Or rename the function entirely to avoid potential name conflicts.

---

## Testing Instructions

```bash
cd PrivacyLRS/src
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DUSE_ENCRYPTION -DRUN_CHACHA_BENCHMARK" \
  pio run -e Unified_ESP32_2400_TX_via_UART --target upload

stty -F /dev/ttyUSB0 115200
timeout 30 cat /dev/ttyUSB0 | tee option_a_output.txt
```

**Look for:**
- Does ESP32 boot?
- Do we see normal TX operation?
- Any crashes?

---

## Decision Tree

```
Option A Test
│
├─ WORKS → Crash is in loop() code
│          │
│          └─ Next: Option B (loop code without function)
│                    │
│                    ├─ WORKS → Crash is from calling the function
│                    │
│                    └─ CRASHES → Crash is in timing/variable logic
│
└─ CRASHES → Crash is from defining the function
             │
             └─ Next: Try function workarounds
                      - Rename function
                      - Change signature
                      - Add attributes
```

---

## Files Changed

**File:** `PrivacyLRS/src/src/tx_main.cpp`

**Lines 1597-1606:** Function defined (unchanged from Round 1)
**Lines 1706-1734:** Loop code wrapped in `#if 0` (completely disabled)

---

## Timeline

**Option A:** 10 min (this test)
**Option B:** 10 min (if needed)
**Follow-up:** 10-20 min (based on results)
**Total:** 30-40 min to isolate the issue

---

## My Prediction

**I think Option A will WORK.**

**Reasoning:**
- The function body is trivial (3 print statements)
- No complex operations that would fail during compilation/linking
- The crash happens before any output, suggesting early boot issue
- Loop code with timing variables is more likely to cause early crashes

**If I'm right:** The problem is in the static variables or timing logic in loop()

**If I'm wrong:** We have a very unusual situation where defining an empty function crashes ESP32

---

## Bottom Line

**Test:** Function defined, never called
**Purpose:** Isolate function definition vs. loop code
**Expected:** Should work (crash is in loop code)
**Timeline:** ~10 minutes

**This test will definitively tell us which code section has the bug!**

---

**Developer**
2025-12-05 15:15
