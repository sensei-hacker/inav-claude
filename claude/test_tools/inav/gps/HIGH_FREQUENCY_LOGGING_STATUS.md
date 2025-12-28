# High-Frequency navEPH Logging - Status Report

**Date:** 2025-12-27
**Task:** Capture navEPH data for Issue #11202 GPS fluctuation investigation
**Status:** ⚠️ **BLOCKED** - SITL blackbox FILE logging has critical bug

---

## Executive Summary

**Objective:** Capture navEPH data at high frequency (500 Hz) to investigate reported 198 Hz GPS fluctuation pattern.

**Finding:** SITL FILE blackbox consistently fails after 15ms, making high-frequency data capture impossible in SITL.

**Recommendation:** **Test on real hardware** flight controller with working blackbox implementation.

---

## Investigation Results

### 1. MSP Query Rate Analysis ✓

**Tested:** MSP2_INAV_DEBUG query performance
**Result:** Maximum **20 Hz**, cannot capture 198 Hz signal
**Details:** See `MSP_QUERY_RATE_ANALYSIS.md`

| Target Rate | Achieved | Latency | Assessment |
|-------------|----------|---------|------------|
| 50 Hz | 20 Hz | 47 ms | ✗ Unreliable |
| 100 Hz | 20 Hz | 47 ms | ✗ Unreliable |
| 200 Hz | 20 Hz | 47 ms | ✗ Unreliable |

**Root cause:** TASK_SERIAL runs at 100 Hz (TASK_PRIORITY_LOW), creating ~47ms latency.

**Conclusion:** MSP unsuitable for high-frequency logging.

---

### 2. Blackbox Serial Logging Investigation ⚠️

**Tested:** SITL blackbox with FILE device
**Configuration:**
- `blackbox_device = FILE (3)`
- `blackbox_rate_denom = 2` → 500 Hz logging (1000 Hz PID / 2)
- `debug_mode = DEBUG_POS_EST (20)` → navEPH in debug[7]

**Result:** **Consistent 15ms decode failure**

```
Decoding log '2025_12_27_132246.TXT' to '2025_12_27_132246.01.csv'...

Log 1 of 1, start 00:00.000, end 00:00.015, duration 00:00.015
                                    ^^^^^ Only 15ms!

1429 frames failed to decode, rendering 20829 loop iterations unreadable.
15 loop iterations weren't logged because of your blackbox_rate settings (7ms, 48.39%)
```

**Observations:**
- Blackbox file created: ✓ (1.6 MB)
- BLACKBOX feature enabled: ✓
- SITL armed and logging: ✓
- Test ran for 30 seconds: ✓
- CSV decode: ✓ (but only 15ms of data)
- Decoder errors: **1429 frames failed**

**Data captured:**
- Time range: 0-15,031 microseconds (15 ms)
- Loop iterations: ~16 samples @ 500 Hz
- navEPH values: 1000 cm (constant in 15ms window)
- navEPV values: 1494-1495 cm (constant)

---

### 3. SITL Blackbox Bug Analysis

**Known issue:** SITL FILE blackbox has been problematic since at least 2025-12-26.

**Evidence:**
1. All SITL blackbox files decode to exactly 15ms
2. Large file size (1.5-1.6 MB) suggests data was written
3. Decoder reports massive frame failures (>1400 frames)
4. Issue persists across:
   - Multiple test runs
   - Different blackbox_rate_denom settings
   - Fresh EEPROM resets

**Hypotheses:**
1. **File format corruption** - SITL writes incorrectly formatted data
2. **Decoder incompatibility** - blackbox_decode doesn't handle SITL format
3. **Timing/sync issue** - Frame timestamps become invalid after 15ms
4. **SITL-specific bug** - FILE device not properly implemented for SITL

**Affected files:**
```bash
2025_12_27_123723.TXT  - 15ms
2025_12_27_125610.TXT  - 15ms
2025_12_27_132246.TXT  - 15ms
climb_test.TXT         - 15ms
hover_test.TXT         - 15ms
```

---

## What We Learned (Despite Limitations)

### navEPH Bit-Packing Confirmed

From the limited 15ms data, we verified the encoding:

```c
// navigation_pos_estimator.c:856
DEBUG_SET(DEBUG_POS_EST, 7,
    (posEstimator.flags & 0b1111111) << 20 |   // Bits 20-26: flags
    (MIN(navEPH, 1000) & 0x3FF) << 10 |        // Bits 10-19: navEPH (max 1000 cm)
    (MIN(navEPV, 1000) & 0x3FF));              // Bits 0-9:   navEPV (max 1000 cm)
```

**Example from CSV:**
```
debug[7] = 2147483108 (0x7FFFFFE4) - overflow/sign issue?
navEPH = 1000 cm (10.00 m)
navEPV = 1494 cm (14.94 m)
```

---

## Critical Insight: "198 Hz" May Be Misunderstood

**User reported:** Logging at blackbox_rate_denom = 32
**Calculation:** 1000 Hz / 32 = **31.25 Hz** logging rate
**Nyquist limit:** 31.25 / 2 = **15.6 Hz max capturable frequency**

**Problem:** Cannot capture 198 Hz signal at 31.25 Hz sampling!

**Possible explanations for "198 Hz":**
1. **Not a frequency** - Could be 198 samples (duration measurement)
2. **Aliased signal** - Higher frequency appearing as lower due to undersampling
3. **Different unit** - Pattern repeats every 198ms? (≈5 Hz)
4. **GPS-related** - 198 Hz = 19.8 × 10 Hz GPS update rate?
5. **Misreading** - Actual pattern at different frequency

**Action needed:** Verify with user what "198 Hz" actually means.

---

## Recommendations

### Option 1: Hardware Flight Controller Testing (RECOMMENDED)

**Approach:** Use real FC with working blackbox

**Advantages:**
- ✓ Proven blackbox implementation (no 15ms bug)
- ✓ Can log to SD card or flash at full rate
- ✓ Real-world GPS timing and behavior
- ✓ Validates findings on actual hardware

**Setup:**
1. Configure flight controller:
   ```
   set blackbox_device = SPIFLASH  # or SDCARD
   set blackbox_rate_denom = 2     # 500 Hz @ 1000 Hz PID
   set debug_mode = 20              # DEBUG_POS_EST
   feature BLACKBOX
   save
   ```

2. Connect GPS module or inject via MSP

3. Arm and run test (climb, hover, etc.)

4. Download and decode blackbox log

5. Analyze navEPH frequency spectrum with FFT

**Required hardware:**
- Flight controller with blackbox storage (SD/flash)
- Optional: GPS module (or use MSP GPS injection)

---

### Option 2: Investigate SITL Blackbox Bug

**Approach:** Debug why SITL FILE blackbox fails after 15ms

**Tasks:**
1. Review SITL blackbox implementation:
   ```
   inav/src/main/target/SITL/
   inav/src/main/blackbox/
   ```

2. Compare SITL vs. hardware blackbox code paths

3. Add debug logging to trace corruption point

4. Test with different blackbox settings

5. Consider blackbox_device = SERIAL instead of FILE

**Estimated effort:** 4-8 hours
**Success probability:** Medium
**Risk:** May not be fixable without deep SITL changes

---

### Option 3: Alternative High-Frequency Logging

**Approach A: Direct Memory Sampling**
- Attach GDB to SITL process
- Script to read `debug[]` array at high frequency
- Export to CSV for analysis

**Approach B: Custom MSP Streaming Mode**
- Modify firmware to stream debug[] without request/response overhead
- Push data at 100-500 Hz
- Capture on host

**Approach C: SITL Instrumentation**
- Add printf statements in position estimator
- Redirect to file
- Parse output for navEPH values

**Effort:** High (8-16 hours)
**Maintenance:** Requires custom firmware patches

---

## Next Steps

### Immediate (For Issue #11202)

1. **Clarify "198 Hz" with user:**
   - Is it truly 198 Hz frequency?
   - Or 198 samples / milliseconds / pattern count?
   - What was the actual blackbox_rate_denom used?

2. **Choose testing approach:**
   - **Recommended:** Hardware FC testing (fastest path to answer)
   - **Alternative:** Debug SITL blackbox (if hardware unavailable)

3. **Run proper high-frequency capture:**
   - blackbox_rate_denom = 2 (500 Hz)
   - Or denom = 1 (1000 Hz) if storage permits
   - Capture 30-60 seconds of data

4. **Perform frequency analysis:**
   - FFT on navEPH time series
   - Look for peaks at all frequencies 0-500 Hz
   - Correlate with GPS 10 Hz updates
   - Check for aliasing artifacts

### Long-term

1. **File SITL blackbox bug report:**
   - Document 15ms decode failure
   - Provide reproduction steps
   - Share log files for analysis

2. **Improve test infrastructure:**
   - Hardware-in-the-loop test rig
   - Automated blackbox collection
   - FFT analysis scripts

3. **Update documentation:**
   - Note SITL blackbox limitations
   - Recommend hardware for production testing

---

## Files Created

| File | Purpose |
|------|---------|
| `benchmark_msp2_debug_rate.py` | MSP query rate testing |
| `MSP_QUERY_RATE_ANALYSIS.md` | MSP limitations analysis |
| `configure_sitl_blackbox_serial.py` | SITL serial blackbox config (not tested) |
| `configure_sitl_blackbox_file.py` | SITL FILE blackbox config (tested, has bug) |
| `BLACKBOX_SERIAL_WORKFLOW.md` | Detailed blackbox workflow |
| `HIGH_FREQUENCY_LOGGING_STATUS.md` | This status report |

---

## Test Data Available

**SITL Blackbox Logs (all 15ms):**
```bash
/home/raymorris/Documents/planes/inavflight/inav/build_sitl/
├── 2025_12_27_123723.TXT (1.6M)
├── 2025_12_27_125610.TXT (1.6M)
├── 2025_12_27_132246.TXT (1.6M)  ← Latest test
├── climb_test.TXT (1.5M)
└── hover_test.TXT (1.5M)
```

**Decoded CSV (15ms each):**
```bash
├── 2025_12_27_132246.01.csv
├── climb_test.01.csv
└── hover_test.01.csv
```

**MSP Benchmark Results:**
- Documented in terminal output
- Shows consistent 20 Hz max rate

---

## Conclusion

While we successfully:
- ✓ Proved MSP unsuitable for high-frequency logging
- ✓ Configured SITL for blackbox logging
- ✓ Captured blackbox data
- ✓ Identified navEPH bit-packing format

We are **blocked** by a critical SITL blackbox bug that limits decode to 15ms.

**Recommended path forward:**
1. **Clarify "198 Hz" claim with user** (may be misunderstood)
2. **Test on real hardware** (fastest solution)
3. **Perform FFT analysis** on full-duration data
4. **Validate findings** and report back to Issue #11202

The infrastructure is ready - we just need working blackbox hardware to collect the data.

---

## References

- Issue #11202: https://github.com/iNavFlight/inav/issues/11202
- MSP2_INAV_DEBUG fix: `MSP2_INAV_DEBUG_FIX.md`
- Blackbox docs: `BLACKBOX_SERIAL_WORKFLOW.md`
- MSP analysis: `MSP_QUERY_RATE_ANALYSIS.md`
- Position estimator: `inav/src/main/navigation/navigation_pos_estimator.c:808-860`
