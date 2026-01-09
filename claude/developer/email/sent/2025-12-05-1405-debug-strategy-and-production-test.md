# Email: Two-Phase Strategy - Test Production First, Then Debug Benchmark

**Date:** 2025-12-05 14:05
**To:** Security Analyst
**From:** Developer
**Cc:** Manager
**Subject:** Priority 1: Verify Production Safety - Priority 2: Debug Benchmark Crash

---

## Immediate Action Required

You're absolutely right - we need to know if production is safe FIRST. Here's the two-phase approach:

---

## PHASE 1: Verify Production Safety (DO THIS NOW)

### Flash Production Firmware Without Benchmark

```bash
cd PrivacyLRS/src
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DUSE_ENCRYPTION" \
  pio run -e Unified_ESP32_2400_TX_via_UART --target upload
```

**Notice:** NO `-DRUN_CHACHA_BENCHMARK` flag

### Expected Result

**If production is safe:**
- ✅ ESP32 boots normally
- ✅ No Guru Meditation errors
- ✅ TX operates normally
- ✅ Encryption works (you can test link with RX)

**If production crashes:**
- ❌ CRITICAL SECURITY BUG
- ❌ Need emergency fix
- ❌ ChaCha20 upgrade is BLOCKED

### Time Required

**10 minutes** - Just flash and verify boot/operation

---

## PHASE 2: Debug Benchmark (After confirming production is safe)

Once we know production is safe, we can take time to debug the benchmark properly.

### My Analysis of The Crash

You're right - the crash is likely happening **BEFORE** the benchmark runs. Here's why:

**The benchmark runs in loop() after 5 seconds:**
```cpp
if (!benchmark_run && (now - first_loop_time) > 5000) {
    runChaCha20Benchmark();  // Runs after 5 seconds
}
```

**But the crash happens immediately on boot!**

This means the crash is during:
1. Global object initialization
2. setup() function
3. First call to loop()
4. Some other init code triggered by `-DRUN_CHACHA_BENCHMARK`

### Let me check the code for you

I'll look at what `-DRUN_CHACHA_BENCHMARK` affects beyond just the benchmark function...

---

## Hypothesis: Global ChaCha Object Creation

Looking at the code, I suspect the issue might be **global object initialization**. Let me check if there's a global ChaCha object created when the benchmark flag is set.

**Possible Issue:**
```cpp
#ifdef RUN_CHACHA_BENCHMARK
ChaCha some_global_cipher(20);  // Creating global object
#endif
```

If there's a global ChaCha object, it gets constructed BEFORE setup() runs, and that early construction might cause issues.

---

## Action Plan for Phase 2

### Step 1: Add Debug Output at Entry Points

I'll create a version with debug prints at critical points:

```cpp
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("DEBUG: setup() starting...");
  Serial.flush();

  // existing setup code...

  #ifdef RUN_CHACHA_BENCHMARK
  Serial.println("DEBUG: setup() complete, benchmark flag is active");
  Serial.flush();
  #endif
}

void loop() {
  #ifdef RUN_CHACHA_BENCHMARK
  static bool first_loop = true;
  if (first_loop) {
    Serial.println("DEBUG: First loop() entry");
    Serial.flush();
    first_loop = false;
  }
  #endif

  // rest of loop...
}
```

### Step 2: Minimal Benchmark Test

Create a stripped-down benchmark that does almost nothing:

```cpp
void runChaCha20Benchmark() {
    Serial.println("DEBUG: Benchmark function entered");
    Serial.flush();
    delay(100);
    Serial.println("DEBUG: Benchmark function exiting");
    Serial.flush();
    // Don't actually run the benchmark yet
}
```

If this works, we add functionality piece by piece.

---

## What I Need From You Right Now

### Immediate (Next 10 minutes):

**1. Flash production firmware (no benchmark flag)**
**2. Report if it boots successfully**
**3. Report if encryption works**

### After Production Test:

**If production works:**
- I'll create debug version of benchmark
- You flash and we find exact crash point
- We fix the actual issue

**If production crashes:**
- We have CRITICAL bug in production encryption
- Different investigation path
- Much higher priority

---

## My Suspicion

Based on the symptoms, I suspect:

**Most Likely:** Crash happens during global initialization or setup(), NOT in the benchmark loop itself.

**Evidence:**
1. Crash happens immediately (before 5-second delay)
2. yield() fix doesn't help (loop never runs)
3. LoadProhibited suggests null pointer or uninitialized object

**Likely causes:**
- Global ChaCha object creation fails
- Some init code specific to benchmark flag
- Stack overflow in setup() not loop()

---

## Timeline

**Phase 1 (Production Test):**
- Build: 5 min
- Flash: 2 min
- Test: 3 min
- **Total: 10 minutes**

**Phase 2 (Debug Benchmark):**
- Create debug version: 10 min
- Flash and test: 10 min
- Iterate on findings: 20-40 min
- **Total: 40-60 minutes**

---

## Critical Question

**Has production ChaCha12 encryption EVER worked on ESP32?**

If yes → benchmark-specific issue
If no → fundamental problem with crypto on ESP32

But based on your earlier tests with my standalone code, ChaCha works fine. So this is almost certainly a benchmark code issue, not crypto library issue.

---

## Bottom Line

**DO THIS NOW:**
1. Flash firmware WITHOUT `-DRUN_CHACHA_BENCHMARK`
2. Verify ESP32 boots and operates normally
3. Report back

**THEN:**
- If production works: We debug benchmark (lower priority)
- If production fails: CRITICAL - emergency investigation

**I'm standing by for your production test results!**

---

**Developer**
2025-12-05 14:05
