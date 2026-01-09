# Email: Debug Version Ready - Will Show Exact Crash Location

**Date:** 2025-12-05 14:15
**To:** Security Analyst
**From:** Developer
**Cc:** Manager
**Subject:** Comprehensive Debug Output Added - Ready to Find Crash Point

---

## Summary

✅ **Debug version is ready!** I've added detailed trace messages throughout setup() and loop() to pinpoint exactly where the crash occurs.

---

## What I Added

### Debug Messages at Key Points:

**1. setup() Entry** (Line 1683)
```
DEBUG: setup() ENTRY
```

**2. After Each Major Setup Step:**
```
DEBUG: setupHardwareFromOptions() OK
DEBUG: setupTarget() OK
DEBUG: devicesRegister() OK
DEBUG: devicesInit() OK
```

**3. setup() Complete** (Line 1796)
```
DEBUG: setup() COMPLETE - No crashes!
```

**4. loop() First Entry** (Line 1812)
```
DEBUG: loop() FIRST ENTRY
```

**5. Benchmark Wait** (Line 1819)
```
DEBUG: Starting 5-second wait before benchmark...
```

**6. Before Benchmark Call** (Line 1825)
```
DEBUG: About to call runChaCha20Benchmark()...
```

**7. After Benchmark Returns** (Line 1829)
```
DEBUG: runChaCha20Benchmark() RETURNED!
```

Plus all the existing debug output inside the benchmark function itself.

---

## How This Will Help

The crash will be isolated to ONE of these intervals:

**Interval 1:** Before "setup() ENTRY"
- Crash during global initialization
- **Fix:** Move objects or init code

**Interval 2:** setup() ENTRY → setupHardwareFromOptions() OK
- Crash in hardware options parsing
- **Fix:** Check hardware configuration

**Interval 3:** Between setup steps
- Crash in specific init function
- **Fix:** Add guards or checks to that function

**Interval 4:** setup() complete → loop() entry
- Crash after setup, before loop
- **Fix:** Check post-setup initialization

**Interval 5:** loop() → 5-second wait message
- Crash on first loop() execution
- **Fix:** Check loop initialization code

**Interval 6:** After 5 seconds → "About to call benchmark"
- Crash in normal loop code
- **Fix:** Check loop logic

**Interval 7:** "About to call benchmark" → (crash)
- Crash AT THE START of benchmark function
- **Fix:** Check benchmark function entry

**Interval 8:** Inside benchmark → "RETURNED"
- Crash during benchmark execution
- **Fix:** We already know where (the loop or setup)

---

## Testing Instructions

### Build and Flash

```bash
cd PrivacyLRS/src
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DUSE_ENCRYPTION -DRUN_CHACHA_BENCHMARK" \
  pio run -e Unified_ESP32_2400_TX_via_UART --target upload
```

### Capture Output

```bash
stty -F /dev/ttyUSB0 115200
timeout 30 cat /dev/ttyUSB0 | tee debug_output.txt
```

### Analyze Results

**Look for the LAST debug message before crash:**

**Example Scenario 1:**
```
DEBUG: setup() ENTRY
DEBUG: setupHardwareFromOptions() OK
DEBUG: setupTarget() OK
[CRASH HERE]
```
**Conclusion:** Crash in devicesRegister()

**Example Scenario 2:**
```
DEBUG: setup() ENTRY
DEBUG: setupHardwareFromOptions() OK
DEBUG: setupTarget() OK
DEBUG: devicesRegister() OK
DEBUG: devicesInit() OK
DEBUG: setup() COMPLETE - No crashes!
DEBUG: loop() FIRST ENTRY
DEBUG: Starting 5-second wait before benchmark...
DEBUG: About to call runChaCha20Benchmark()...

========================================
ChaCha12 Test - Finding #5
[CRASH HERE]
```
**Conclusion:** Crash inside runChaCha20Benchmark(), likely at the ChaCha object creation (line 1619)

---

## Expected Timeline

**Build:** 5 min
**Flash:** 2 min
**Capture output:** 1 min
**Analyze:** 2 min
**Total:** ~10 minutes to identify crash point

---

## Probable Scenarios

Based on the immediate crash on boot, **most likely:**

### Scenario A: Crash in setup()
If we see "setup() ENTRY" but NOT "setup() COMPLETE":
- Crash is in one of the setup functions
- Likely devicesInit() or Radio.Begin()

### Scenario B: Crash on global init
If we DON'T see "setup() ENTRY" at all:
- Crash during global object construction
- Happens BEFORE setup() runs
- Most difficult to fix

### Scenario C: Crash in loop()
If we see "loop() FIRST ENTRY" but then crash:
- Crash in loop initialization
- Easier to isolate and fix

---

## Next Steps After Debug Output

**Once you tell me the last message before crash:**

**1. I'll know exactly which function/line is failing**
**2. I'll create targeted fix for that specific issue**
**3. We test the fix**
**4. Benchmark runs successfully**

---

## Code Changes Made

**File:** `src/src/tx_main.cpp`

**Lines modified:**
- 1680-1685: setup() entry debug
- 1689-1712: setup() step-by-step debug
- 1795-1798: setup() complete debug
- 1809-1821: loop() entry and wait debug
- 1825-1830: benchmark call debug

**All wrapped in `#ifdef RUN_CHACHA_BENCHMARK`** so they only appear when benchmark flag is set.

---

## Important Notes

1. **Serial.flush() after each print** - Ensures message appears before crash
2. **All debug only when benchmark flag set** - No impact on production
3. **Detailed enough to isolate to specific function** - Should take ONE test iteration

---

## Ready to Test

**You can flash and test immediately!**

The debug output will tell us EXACTLY where the crash occurs, then I can create a proper fix.

Looking forward to seeing which interval the crash happens in!

---

**Developer**
2025-12-05 14:15
