# Email: ESP32 Still Crashing - Fix Present But Not Working

**Date:** 2025-12-05 14:00
**To:** Developer
**Cc:** Manager
**From:** Security Analyst
**Re:** Hardware Test Results - Still Getting Guru Meditation Error

---

## Summary

❌ **ESP32 still crashing** despite the watchdog yield fix being present in the code.

---

## Test Results

**Firmware Built:** ✅ Successfully
**Firmware Flashed:** ✅ Successfully
**ESP32 Boot:** ❌ Crashes with Guru Meditation Error

**Error Message:**
```
Guru Meditation Error: Core  1 panic'ed (LoadProhibited). Except
[crash loop repeating]
```

---

## Verification

I verified the fix IS in the source code:

**File:** `PrivacyLRS/src/src/tx_main.cpp`
**Lines 1650-1656:**
```cpp
uint32_t start = micros();
for (uint32_t i = 0; i < ITERATIONS; i++) {
    cipher12.encrypt(ciphertext, plaintext, 8);
    // Yield to watchdog every 100 iterations to prevent ESP32 watchdog reset
    if (i % 100 == 0) {
        yield();
    }
}
uint32_t elapsed = micros() - start;
```

**The yield() fix is definitely there!**

---

## Analysis

The crash is happening, but we don't know WHERE in the code. Possibilities:

### 1. Crash Happens BEFORE Benchmark
The benchmark runs after 5 seconds in loop(). Maybe the crash occurs during:
- Setup/initialization
- WiFi/BLE initialization
- Hardware setup
- BEFORE reaching the benchmark code

### 2. Different Code Path
Maybe `-DRUN_CHACHA_BENCHMARK` affects other parts of the code that we haven't fixed?

### 3. The yield() Isn't Being Called
Maybe the compiler optimized it out, or there's a syntax issue?

### 4. Stack Overflow in DIFFERENT Function
Maybe another function (not the benchmark loop) has stack issues?

---

## What I Cannot See

**Without full crash log, I don't know:**
- Stack trace
- Which function crashed
- What address caused LoadProhibited
- Which line of code failed

**The serial output only shows:** `Guru Meditation Error: Core  1 panic'ed (LoadProhibited). Except`

Then it cuts off and repeats the crash loop.

---

## Recommendations

### Option 1: Add Debug Output BEFORE Benchmark

Add prints to see how far it gets:

```cpp
void loop() {
  uint32_t now = millis();

  #ifdef RUN_CHACHA_BENCHMARK
  static bool benchmark_run = false;
  static uint32_t first_loop_time = 0;

  if (first_loop_time == 0) {
    first_loop_time = now;
    Serial.println("DEBUG: First loop(), waiting 5 seconds...");  // ADD THIS
  }

  if (!benchmark_run && (now - first_loop_time) > 5000) {
    Serial.println("DEBUG: About to run benchmark...");  // ADD THIS
    Serial.flush();
    runChaCha20Benchmark();
    Serial.println("DEBUG: Benchmark completed!");  // ADD THIS
    benchmark_run = true;
  }
  #endif

  // ... rest of loop
}
```

This will show us IF the benchmark even starts.

### Option 2: Capture Full Crash Log

The ESP32 outputs a detailed crash log with:
- Register dump
- Stack trace
- Backtrace
- Exception cause

But it's being cut off. We need to:
- Increase serial buffer
- Slow down baud rate
- Use ESP exception decoder

### Option 3: Test Without Benchmark

Flash firmware WITHOUT `-DRUN_CHACHA_BENCHMARK` to verify:
- Does production firmware work?
- Is the crash specific to benchmark code?

```bash
cd PrivacyLRS/src
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DUSE_ENCRYPTION" \
  pio run -e Unified_ESP32_2400_TX_via_UART --target upload
```

This would prove if production encryption is safe.

### Option 4: Bisect the Problem

Comment out half of `runChaCha20Benchmark()` to find which part crashes:

```cpp
void runChaCha20Benchmark() {
    Serial.println("Step 1...");
    // ... steps 1-3 ...

    /*
    Serial.println("Step 4...");
    // Comment out steps 4-6 to test
    */
}
```

---

## My Recommendation

**Start with Option 3 (Test Without Benchmark):**

1. Flash production firmware (no benchmark)
2. Verify it boots and works
3. Proves production is safe
4. Then we can debug benchmark separately

**Time: 10 minutes**

If production works, then:

**Option 1 (Add Debug Output):**
- Shows us where crash occurs
- Quick to implement
- **Time: 15 minutes**

---

## Questions for You

1. **Should I test production firmware first (without benchmark)?**
2. **Do you want to add debug output to narrow down where it crashes?**
3. **Can you decode the Guru Meditation error from the partial message?**
4. **Is there a way to get the full crash log with stack trace?**

---

## Current Status

**ESP32:** In crash loop
**Production Safety:** UNKNOWN (can't test while crashing)
**Benchmark:** Cannot run (crashes before completion)
**Next Step:** Awaiting your guidance

---

## Possible Root Causes

Since the yield() fix is present but still crashing:

1. **Crash is earlier** - Before benchmark even runs
2. **Stack overflow elsewhere** - Different function/initialization
3. **Memory corruption** - Heap fragmentation or buffer overflow
4. **Serial buffer overflow** - Too much debug output
5. **Compiler optimization** - yield() optimized away (unlikely)

---

## Bottom Line

**Status:** Firmware flashed, ESP32 crashes immediately
**Fix Applied:** Yes (yield() is in the code)
**Result:** Still crashes with LoadProhibited error
**Need:** Either test production without benchmark, or add debug output to find crash location

Waiting for your direction!

---

**Security Analyst**
2025-12-05 14:00
