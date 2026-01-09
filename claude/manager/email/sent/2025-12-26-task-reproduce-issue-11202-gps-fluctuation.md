# Task Assignment: Reproduce Issue #11202 - GPS Signal Fluctuation with Synthetic Data

**Date:** 2025-12-26
**Project:** inav (firmware) - GPS/Navigation Testing
**Priority:** Medium-High
**Estimated Effort:** 6-8 hours

## Task

Analyze GitHub issue #11202 (GNSS signal fluctuation) and attempt to reproduce the problem using predictable synthetic MSP GPS data to isolate the root cause.

**Issue:** https://github.com/iNavFlight/inav/issues/11202

## Issue Summary

**Problem:** GPS signal instability affecting INAV 6.0-9.0 across multiple u-blox modules (M8, M9, M10)

**Symptoms:**
- Recurring EPH (estimated position error) spikes in flight logs
- Wild HDOP fluctuations (2-5 range instead of stable ~1.3)
- Reduced satellite acquisition (15-18 sats instead of 25+)
- Periodic positional corrections during navigation

**Key Finding:** `gps_ublox_nav_hz` setting significantly affects performance:
- Default 10Hz with 4 constellations: Unstable, low sat count
- Reduced to 6Hz (M10) or 9Hz (M9): Improved sat count by 8-10, HDOP stable at ~1.3
- INAV 7.0 defaults to 5Hz despite user settings (regression?)

**Regression:** INAV 6.0 had superior stability compared to 7.0+

## Objectives

### 1. Analyze the Issue

**Read and understand:**
- Full issue description and user reports
- What EPH and HDOP values indicate
- How `gps_ublox_nav_hz` affects GPS processing
- Differences between INAV 6.0 and 7.0+ GPS handling

**Questions to answer:**
- What changed in GPS code between 6.0 and 7.0?
- Why does nav_hz affect satellite acquisition?
- What causes EPH spikes and HDOP fluctuations?
- Is this a firmware bug or GPS module issue?

### 2. Create Synthetic MSP GPS Data

**Goal:** Generate predictable GPS data streams that simulate the reported problem

**Approach 1: Use mspapi2 to Send Synthetic GPS Data**

Create Python script using mspapi2 to send MSP_RAW_GPS and MSP_COMP_GPS messages:

```python
import mspapi2
import time

# Connect to SITL or real FC
fc = mspapi2.FlightController("/dev/ttyACM0")

# Simulate normal GPS data
def send_stable_gps(lat, lon, sat_count, hdop):
    gps_data = {
        'fix': 3,  # 3D fix
        'numSat': sat_count,
        'lat': lat,
        'lon': lon,
        'alt': 100,  # meters
        'groundSpeed': 0,
        'groundCourse': 0,
        'hdop': hdop  # HDOP value
    }
    fc.send_msp_gps(gps_data)

# Simulate fluctuating GPS (the problem)
def send_fluctuating_gps(lat, lon):
    for i in range(100):
        # Alternate between stable and unstable
        if i % 10 < 5:
            # Stable period
            send_stable_gps(lat, lon, sat_count=25, hdop=130)  # HDOP 1.3
        else:
            # Unstable period (EPH spike)
            send_stable_gps(lat, lon, sat_count=16, hdop=450)  # HDOP 4.5
        time.sleep(0.1)  # 10Hz update rate
```

**Approach 2: SITL with GPS Simulator**

If SITL supports GPS simulation:
- Configure simulated GPS module
- Inject fluctuating data programmatically
- Monitor INAV's response

**Data Patterns to Test:**

1. **Stable baseline:** Consistent 25 sats, HDOP 1.3
2. **Reported problem:** Fluctuating 15-18 sats, HDOP 2.0-5.0
3. **Nav rate variations:**
   - 10Hz updates (default, problematic)
   - 9Hz updates (M9 workaround)
   - 6Hz updates (M10 workaround)
   - 5Hz updates (7.0 default)

### 3. Test Different nav_hz Settings

**Settings to test:**
```bash
set gps_ublox_nav_hz = 10  # Default, reportedly problematic
set gps_ublox_nav_hz = 9   # M9 workaround
set gps_ublox_nav_hz = 6   # M10 workaround
set gps_ublox_nav_hz = 5   # INAV 7.0 default
```

**For each setting:**
- Send synthetic GPS data at corresponding rate
- Monitor EPH values in logs
- Check HDOP stability
- Observe satellite count filtering
- Look for position corrections

### 4. Compare INAV Versions

**Test on multiple versions:**
- INAV 6.0 (reportedly stable)
- INAV 7.0 (regression reported)
- INAV 9.0 (current)

**Compare:**
- GPS data processing differences
- Default settings changes
- EPH/HDOP calculation changes
- Satellite filtering logic

## Investigation Areas

### Code Locations to Check

**GPS Processing:**
- `src/main/io/gps.c` - Main GPS handling
- `src/main/io/gps_ublox.c` - u-blox specific code
- GPS state machine and data validation
- EPH (estimated position error) calculation
- HDOP filtering/processing

**Settings:**
- `gps_ublox_nav_hz` implementation
- How nav rate affects data processing
- Changes between 6.0 and 7.0

**Navigation:**
- `src/main/navigation/navigation.c`
- How GPS quality affects navigation decisions
- Position correction logic

### Specific Questions

1. **Why does nav_hz affect satellite count?**
   - Does higher rate cause GPS module to miss satellites?
   - Is this a timing/buffer issue?
   - u-blox module limitation or INAV bug?

2. **What causes EPH spikes?**
   - Calculated from GPS data or reported by module?
   - Does INAV filter/smooth EPH values?
   - Related to satellite geometry changes?

3. **INAV 7.0 regression:**
   - What GPS-related changes in 7.0?
   - Why does it default to 5Hz despite setting?
   - Is there a bug ignoring user's nav_hz setting?

## Expected Deliverables

### 1. Analysis Report

**Document:**
- Understanding of the issue
- GPS data flow in INAV
- How nav_hz affects processing
- Code changes between 6.0 and 7.0
- Hypothesis for root cause

**Location:** `claude/developer/investigations/gps-fluctuation-issue-11202/`

### 2. Synthetic Data Script

**Create:**
- Python script using mspapi2 to send GPS data
- Multiple test scenarios (stable, fluctuating, various rates)
- Documented usage instructions

**Location:** `claude/developer/test_tools/inav/gps/`

**Features:**
- Configurable satellite count
- Adjustable HDOP values
- Variable update rates (5Hz, 6Hz, 9Hz, 10Hz)
- EPH spike simulation
- Position fluctuation patterns

### 3. Reproduction Results

**Test and document:**
- Can the issue be reproduced with synthetic data?
- Which nav_hz settings trigger the problem?
- Differences between INAV versions
- Logs/screenshots showing the problem
- Whether synthetic data accurately mimics real GPS behavior

### 4. Root Cause Analysis (if found)

**If reproducible:**
- Identify the code causing the issue
- Explain why nav_hz affects satellite acquisition
- Document the regression in 7.0
- Propose potential fixes

**If NOT reproducible:**
- Explain why synthetic data differs from real GPS
- Identify what aspects can't be simulated
- Suggest alternative testing approaches

## Testing Approach

### Phase 1: Understand the Issue (2 hours)

1. Read issue #11202 thoroughly
2. Review GPS code in INAV
3. Understand EPH and HDOP metrics
4. Research u-blox module behavior
5. Compare 6.0 vs 7.0 GPS changes

### Phase 2: Create Test Infrastructure (2-3 hours)

1. Set up mspapi2 environment
2. Create synthetic GPS data generator
3. Build SITL or prepare test FC
4. Verify GPS data reception
5. Test different nav_hz settings

### Phase 3: Reproduction Testing (2-3 hours)

1. Send stable baseline data
2. Inject fluctuating patterns
3. Test various nav_hz rates
4. Monitor EPH/HDOP behavior
5. Compare with real GPS logs
6. Test on multiple INAV versions

### Phase 4: Analysis and Reporting (1 hour)

1. Document findings
2. Determine if issue is reproducible
3. Identify root cause (if possible)
4. Propose solutions or next steps

## Success Criteria

- [ ] Read and understood issue #11202
- [ ] Analyzed GPS processing code in INAV
- [ ] Created synthetic GPS data generator
- [ ] Tested with multiple nav_hz settings (5Hz, 6Hz, 9Hz, 10Hz)
- [ ] Attempted reproduction of EPH spikes and HDOP fluctuations
- [ ] Compared behavior across INAV versions (6.0, 7.0, 9.0)
- [ ] Documented whether issue is reproducible with synthetic data
- [ ] Identified potential root cause or next investigation steps
- [ ] Created reusable test script for GPS testing

## Resources

**Issue and References:**
- Issue #11202: https://github.com/iNavFlight/inav/issues/11202
- u-blox protocol documentation
- GPS message formats (MSP_RAW_GPS, MSP_COMP_GPS)

**Tools:**
- mspapi2: Python MSP library
- SITL: Software-in-the-loop for firmware testing
- Blackbox log viewer: For analyzing GPS logs

**Code Locations:**
- `src/main/io/gps.c`
- `src/main/io/gps_ublox.c`
- `src/main/navigation/navigation.c`

**MSP Messages:**
- MSP_RAW_GPS (106) - GPS position data
- MSP_COMP_GPS (107) - GPS computed data
- GPS status and satellite info

## Notes

**Challenge:** Synthetic data may not perfectly replicate real GPS module behavior, especially timing-sensitive issues or module-specific quirks.

**Alternative if not reproducible:** The investigation itself will provide valuable insights into GPS processing, even if exact reproduction fails. Document what was learned for future debugging.

**User Impact:** This affects navigation reliability and could cause unexpected flight behavior. Understanding the issue is important for user safety.

**Potential Quick Wins:**
- If 7.0 defaults to 5Hz despite settings, that's a clear bug to fix
- If documentation is unclear about nav_hz tuning, improve it
- If INAV 6.0 was more stable, identify what changed

## Why This Matters

**Safety Impact:**
- GPS instability can cause navigation errors
- RTH may behave unpredictably
- Position hold could drift

**User Experience:**
- Users are working around the issue by tuning nav_hz
- Unclear why different rates work better
- Regression from 6.0 to 7.0 needs explanation

**Root Cause Understanding:**
- Is this firmware bug or GPS module limitation?
- Can INAV handle it better?
- Should default settings change?

---
**Manager**
