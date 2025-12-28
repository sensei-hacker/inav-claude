# MSP2_INAV_DEBUG Query Rate Analysis

**Date:** 2025-12-27
**Status:** Analysis Complete
**Context:** Issue #11202 GPS fluctuation investigation

---

## Executive Summary

**Finding:** MSP2_INAV_DEBUG cannot capture high-frequency navEPH fluctuations.

- **Maximum MSP query rate:** ~20 Hz
- **navEPH update rate:** 1000 Hz (PID loop)
- **User-reported signal:** 198 Hz cycle
- **Conclusion:** Alternative logging method required

---

## Benchmark Results

### Test Setup
- SITL running on localhost:5760
- Background traffic: RC at 50 Hz, GPS at 10 Hz
- Query method: Blocking MSP request/response
- Script: `benchmark_msp2_debug_rate.py`

### Results Summary

| Target Rate | Achieved Rate | Success | Latency Avg | Assessment |
|-------------|---------------|---------|-------------|------------|
| 50 Hz | 20 Hz | 100% | 47.3 ms | ✗ Unreliable |
| 100 Hz | 20 Hz | 100% | 47.4 ms | ✗ Unreliable |
| 200 Hz | 20 Hz | 100% | 47.5 ms | ✗ Unreliable |

**Consistent findings across all tests:**
- Actual query rate: ~20 Hz (regardless of target)
- Query latency: ~47 ms (consistent)
- Missed deadlines: 99%

---

## Root Cause Analysis

### 1. INAV Scheduler Bottleneck

**Serial/MSP Task Configuration:**
```c
// src/main/fc/fc_tasks.c:488
[TASK_SERIAL] = {
    .taskName = "SERIAL",
    .taskFunc = taskHandleSerial,
    .desiredPeriod = TASK_PERIOD_HZ(100),     // 100 Hz = 10ms period
    .staticPriority = TASK_PRIORITY_LOW,       // Priority 1
}
```

**Implications:**
- MSP handler runs at **100 Hz maximum** (every 10 ms)
- **Low priority** - can be delayed by higher priority tasks
- Round-trip request/response requires 2+ task cycles

### 2. Latency Breakdown

**Measured: ~47 ms total**

Estimated components:
- Wait for TASK_SERIAL execution: 0-10 ms
- Process MSP2_INAV_DEBUG request: 1-2 ms
- Wait for next TASK_SERIAL to send response: 0-10 ms
- Network transmission (localhost TCP): 1 ms
- Python mspapi2 overhead: 1-2 ms
- Additional SITL delays: 20-30 ms (multiple task cycles)

**Why so slow?**
- SITL scheduler runs many high-priority tasks (GYRO, PID, IMU)
- Low-priority TASK_SERIAL gets starved
- Serial processing is not optimized for high throughput

### 3. Position Estimator Update Rate

**navEPH is updated at 1000 Hz:**

```c
// src/main/fc/fc_tasks.c
[TASK_PID] = {
    .taskName = "PID",
    .taskFunc = taskMainPidLoop,
    .desiredPeriod = TASK_PERIOD_US(1000),    // 1000 µs = 1 kHz
    .staticPriority = TASK_PRIORITY_REALTIME,  // Priority 18
}
```

Position estimator chain:
```
taskMainPidLoop() [1000 Hz, REALTIME]
  └─> updatePositionEstimator() [1000 Hz]
      └─> publishEstimatedTopic()
          └─> DEBUG_SET(DEBUG_POS_EST, 7, navEPH/navEPV)
```

**Result:** debug[] array is updated at 1000 Hz, but MSP can only read it at ~20 Hz.

---

## Signal Analysis

### Nyquist Theorem Requirements

To capture a signal without aliasing:
- **198 Hz signal** requires ≥ **396 Hz** sampling rate
- **Practical minimum:** 200-300 Hz (1-1.5× signal frequency)
- **Recommended:** 400 Hz+ (2× signal frequency)

### MSP Capability vs. Requirements

| Requirement | MSP Capability | Gap |
|-------------|----------------|-----|
| 396 Hz (Nyquist) | 20 Hz | **20× too slow** |
| 200 Hz (minimum) | 20 Hz | **10× too slow** |
| 100 Hz (marginal) | 20 Hz | **5× too slow** |

**Conclusion:** MSP2_INAV_DEBUG is fundamentally unsuitable for capturing 198 Hz fluctuations.

---

## Alternative Logging Methods

### Option 1: Blackbox Logging (RECOMMENDED)

**Advantages:**
- Runs at gyro rate (1000-8000 Hz)
- Captures debug[] array directly
- No MSP overhead
- Historical data for offline analysis

**Challenges:**
- SITL FILE logging has bugs (only 15ms decode)
- May need hardware testing or serial blackbox

**Implementation:**
```bash
# Configure blackbox
set blackbox_device = SERIAL  # or FILE (buggy in SITL)
set blackbox_rate_num = 1
set blackbox_rate_denom = 1
set debug_mode = 20  # DEBUG_POS_EST
feature BLACKBOX

# Decode log
blackbox_decode logfile.TXT
# Analyze navEPH column at full rate
```

**Status:** Infrastructure exists (see `README_GPS_BLACKBOX_TESTING.md`), but SITL has known issues.

### Option 2: Direct Memory Sampling

**Approach:** Read debug[] array from SITL memory at high frequency

**Challenges:**
- Requires SITL modifications or GDB scripting
- Complex implementation
- Not portable to hardware

### Option 3: Custom High-Frequency MSP Mode

**Approach:** Implement streaming MSP mode that pushes debug[] at high rate

**Challenges:**
- Requires firmware modification
- Still limited by serial bandwidth
- Custom code maintenance

### Option 4: Hardware Testing with Blackbox

**Approach:** Test on real hardware with working blackbox

**Advantages:**
- Proven blackbox implementation
- Real-world conditions
- No SITL bugs

**Challenges:**
- Requires physical hardware
- More complex test setup
- Harder to reproduce exact conditions

---

## Recommendations

### For Issue #11202 Investigation

**Primary Approach: Blackbox Logging**

1. **Try SITL serial blackbox:**
   ```bash
   set blackbox_device = SERIAL
   # Connect blackbox viewer to TCP port
   ```

2. **Test on real hardware:**
   - Use flight controller with SD card or flash
   - Run GPS injection test
   - Decode blackbox at full rate

3. **If blackbox unavailable:**
   - MSP at 20 Hz can still show trends
   - Won't capture 198 Hz cycle, but may show 10 Hz GPS interaction
   - Use for qualitative analysis only

### For High-Frequency Data Collection

**Do NOT use MSP2_INAV_DEBUG if:**
- Signal frequency > 10 Hz
- Need precise timing
- Require Nyquist-compliant sampling

**DO use MSP2_INAV_DEBUG if:**
- Signal frequency < 5 Hz
- Real-time monitoring (not logging)
- Low-resolution trending is acceptable

---

## Updated Script Recommendations

### gps_with_naveph_logging_mspapi2.py

**Current default:** 10 Hz query rate
**Maximum safe rate:** 20 Hz
**For 198 Hz signal:** Insufficient (need 200-400 Hz)

**Recommended changes:**

1. **Add warning about limitations:**
   ```python
   # WARNING: MSP can only query at ~20 Hz maximum
   # Cannot capture signals >10 Hz (Nyquist limit)
   # Use blackbox logging for high-frequency analysis
   ```

2. **Update default query rate:**
   ```python
   --query-rate default=20  # Increased from 10 to maximum safe rate
   ```

3. **Add validation:**
   ```python
   if args.query_rate > 20:
       print("WARNING: Rates >20 Hz are unreliable due to MSP scheduler")
       print("Achieved rate will be ~20 Hz regardless of target")
   ```

4. **Document use case:**
   ```python
   # Use this script for:
   # - Trending navEPH at 20 Hz (2 second window)
   # - GPS update correlation (10 Hz signal OK)
   # - Real-time monitoring
   #
   # DO NOT use for:
   # - 198 Hz signal capture (use blackbox)
   # - High-precision timing analysis
   # - Nyquist-compliant sampling
   ```

---

## Files Created

- **benchmark_msp2_debug_rate.py:** Query rate testing script
- **MSP_QUERY_RATE_ANALYSIS.md:** This document

---

## Technical Details

### MSP Message Overhead

**MSP2_INAV_DEBUG (0x2019):**
- Request: ~9 bytes (header + CRC)
- Response: ~41 bytes (header + 32 bytes data + CRC)
- Total: ~50 bytes per query

**At 115200 baud (hardware):**
- Theoretical max: 50 bytes × 8 bits × 115200 = 230 queries/sec
- Actual: Limited by firmware scheduler (100 Hz), not bandwidth

**At 921600 baud (SITL):**
- Theoretical max: 1840 queries/sec
- Actual: Limited by firmware scheduler (100 Hz), not bandwidth

### Scheduler Priority Levels

```c
TASK_PRIORITY_IDLE = 0        // Background only
TASK_PRIORITY_LOW = 1         // MSP, telemetry ← Serial task
TASK_PRIORITY_MEDIUM = 3      // GPS, compass
TASK_PRIORITY_MEDIUM_HIGH = 4 //
TASK_PRIORITY_HIGH = 5        //
TASK_PRIORITY_REALTIME = 18   // Gyro, PID ← Position estimator
```

**Task Execution Order:**
1. REALTIME tasks (gyro, PID) - 1000-8000 Hz
2. HIGH/MEDIUM tasks (GPS, baro) - 10-100 Hz
3. LOW tasks (MSP, serial) - 100 Hz max, **often delayed**

---

## Lessons Learned

1. **MSP is for configuration, not high-speed logging**
   - Designed for 10-100 Hz queries
   - Not suitable for time-critical data

2. **Blackbox is the right tool for flight data analysis**
   - Captures at gyro/PID rate (1000-8000 Hz)
   - No network/protocol overhead

3. **SITL limitations**
   - FILE blackbox may have bugs
   - Scheduler may not match hardware timing exactly
   - Consider hardware testing for production issues

4. **Signal processing fundamentals apply**
   - Can't skip Nyquist theorem
   - Aliasing will corrupt under-sampled signals
   - 20 Hz sampling can't capture 198 Hz signal

---

## Next Steps

1. **Investigate SITL blackbox FILE bug**
   - Why only 15ms decodes?
   - Can we fix or workaround?

2. **Test serial blackbox with SITL**
   - Configure blackbox_device = SERIAL
   - Use configurator or viewer to capture

3. **Hardware testing**
   - Borrow/use real flight controller
   - Validate GPS fluctuation on hardware
   - Compare SITL vs. hardware behavior

4. **Re-examine 198 Hz claim**
   - Is it truly 198 Hz or an artifact?
   - Could it be GPS 10 Hz × aliasing?
   - Verify with proper high-frequency logging

---

## References

- Issue #11202: https://github.com/iNavFlight/inav/issues/11202
- MSP2_INAV_DEBUG fix: `MSP2_INAV_DEBUG_FIX.md`
- Blackbox testing: `README_GPS_BLACKBOX_TESTING.md`
- Position estimator: `inav/src/main/navigation/navigation_pos_estimator.c:910-928`
- Scheduler config: `inav/src/main/fc/fc_tasks.c:488-493`
- PID task config: `inav/src/main/fc/fc_tasks.c` (TASK_PID)
