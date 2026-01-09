# Finding #5 Investigation: Add Bisect Method for Benchmark Crash

**Date:** 2025-12-05 13:00
**To:** Security Analyst / Cryptographer
**From:** Manager
**Re:** Additional investigation approach - bisect method
**Priority:** HIGH

---

## Additional Investigation Method

Please continue investigating the cause of the ESP32 crash. I'm adding a bisect approach to help narrow down the problem quickly.

---

## If Production Works But Benchmark Crashes

**Scenario:** Production firmware runs fine, but benchmark code crashes.

This tells us:
- ChaCha12 encryption itself is working
- The crash is specific to the benchmark implementation
- Something in the benchmark code is causing the issue

---

## Bisect Method

Use a **binary search approach** to isolate the problematic code:

### Step 1: Initial State
- Production code: ✅ Works
- Production + full benchmark: ❌ Crashes

### Step 2: Remove Half the Benchmark Code
Comment out approximately half of the benchmark code.

**Test:** Does it still crash?

### Step 3a: If It Still Crashes
The problem is in the **remaining half** of the code.
- Comment out half of the remaining code
- Test again
- Repeat until you find the minimal crashing code

### Step 3b: If It Stops Crashing
The problem is in the **commented half** of the code.
- Uncomment half of what you commented
- Test again
- Repeat until you find the minimal crashing code

---

## Example Bisect Process

**Original benchmark structure (hypothetical):**
```cpp
// 1. Setup/initialization
ChaCha cipher(20);
uint8_t key[32] = {...};
uint8_t nonce[12] = {...};
cipher.setKey(key, 32);
cipher.setIV(nonce, 12);

// 2. Data preparation
uint8_t testData[1024];
memset(testData, 0, sizeof(testData));

// 3. Timing setup
unsigned long startTime = micros();

// 4. Benchmark loop
for (int i = 0; i < 10000; i++) {
    cipher.encrypt(testData, 1024);
}

// 5. Results calculation
unsigned long endTime = micros();
float throughput = calculateThroughput(...);

// 6. Serial output
Serial.print("Throughput: ");
Serial.println(throughput);
```

**Iteration 1:** Comment out sections 4-6 (second half)
- Crash? → Problem is in sections 1-3
- No crash? → Problem is in sections 4-6

**Iteration 2:** Assume crash is in sections 4-6, comment out section 6
- Crash? → Problem is in sections 4-5
- No crash? → Problem is in section 6 (serial output)

**Iteration 3:** Continue until minimal crashing code identified

---

## What You're Looking For

**Common causes of benchmark-specific crashes:**

1. **Buffer size issues**
   - Benchmark uses large buffer (1024 bytes)
   - Production uses small buffer (8 bytes)
   - Large buffer causes stack overflow

2. **Loop iteration count**
   - Benchmark runs 10,000+ iterations
   - Causes heap fragmentation or memory leak
   - Each iteration allocates memory that's not freed

3. **Timing/delay issues**
   - Benchmark measures time with micros()/millis()
   - Tight loop without delays
   - Starves other tasks or watchdog timer

4. **Serial output**
   - Heavy serial printing
   - Buffer overflow in serial driver
   - Conflicts with interrupts

5. **Multiple ChaCha objects**
   - Benchmark creates multiple cipher objects
   - Production uses single shared object
   - Heap fragmentation or alignment issues

6. **Stack usage**
   - Benchmark has deep call stack
   - Large local variables
   - Stack overflow

---

## Investigation Priority

### Priority 1: Verify Production Safety (Phase 3 from previous email)
**Must do first** - flash normal firmware, confirm encryption works

### Priority 2: If Production Works, Use Bisect Method
**Start here** - use binary search to isolate crash

### Priority 3: If Bisect Identifies Root Cause
- Document the specific code causing crash
- Analyze why that code fails
- Propose fix or workaround

---

## Expected Outcome

After bisection, you should be able to report:

```
Production encryption: ✅ Works fine

Benchmark crash isolated to:
- Specific code: [line X to line Y]
- Root cause hypothesis: [stack overflow / heap issue / etc]
- Minimal reproducer: [exact code that crashes]
```

Then we can:
1. Fix the specific issue
2. Re-run benchmark successfully
3. Obtain actual performance data
4. Resume Finding #5 analysis

---

## Timeline

**Bisect method is fast:**
- If benchmark has ~100 lines, takes ~7 iterations to isolate (log₂(100) ≈ 6.6)
- Each iteration: comment code, build, flash, test (~5 minutes)
- **Total: ~30-45 minutes to isolate root cause**

Much faster than analyzing every line individually!

---

## Tools

**Binary search visualization:**
```
Iteration 0: [████████████████] (100% code, crashes)
Iteration 1: [████████........] (50% code)
Iteration 2: [████............] (25% code) or [........████....] (25% code)
Iteration 3: [██..............] (12.5% code)
...
Iteration 7: [█...............] (1 line - found it!)
```

---

## Communication

**Keep me updated:**
- Phase 3 results (production safety)
- Bisect progress (which half has the problem)
- Root cause when identified
- Any insights or questions during investigation

**I'll notify you when:**
- Developer completes their investigation
- We have decisions to make about fixes
- Finding #5 can resume

---

## Summary

**New approach:** If production works but benchmark crashes, use bisect method:
1. Comment out half the benchmark code
2. Test for crash
3. Repeat on the problematic half
4. Isolate minimal crashing code in ~7 iterations

**Goal:** Fast root cause identification (30-45 min vs hours of analysis)

**Next step:** Verify production safety first, then bisect if needed

---

**Manager**
2025-12-05 13:00
