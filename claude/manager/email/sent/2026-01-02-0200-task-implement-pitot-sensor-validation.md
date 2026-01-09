# Task Assignment: Implement Pitot Sensor Validation with GPS Sanity Checks

**Date:** 2026-01-02 02:00
**Project:** implement-pitot-sensor-validation
**Priority:** HIGH
**Estimated Effort:** 8-12 hours
**Type:** Safety Feature Implementation
**Milestone:** 9.1 or 9.2
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

## Task

Implement GPS-based pitot sensor validation with automatic fallback to virtual airspeed when pitot readings are implausible or failed.

## Background

**Parent Analysis:** analyze-pitot-blockage-apa-issue (COMPLETED 2025-12-28)

The pitot blockage APA safety analysis identified that INAV currently lacks proper airspeed sensor validation. When pitot tubes fail, block, or are left with covers on, the aircraft can become nearly unflyable due to incorrect gain scaling.

**Current Situation:**
- `pitotValidForAirspeed()` only checks: hardware timeout, calibration status, GPS fix (for virtual)
- **No sanity checks:** GPS groundspeed validation, plausibility checks, rate-of-change limits

**Safety Impact:**
- Pitot failures are COMMON (mechanical failure, blockage, forgotten sock)
- Current APA behavior with blocked pitot: 200% gains at cruise speed
- Makes aircraft nearly unflyable during approach/landing

## Reference Documentation

**REQUIRED READING:**

📄 **Analysis Report:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

Read sections:
- "Solution 3: GPS-Based Airspeed Sanity Checks" (pages ~15-18)
- "Recommended Solution: Four-Issue Approach - Issue 1"
- "Proposed Implementation: Pitot Sensor Validation"
- Code examples and algorithm description

**Key sections from analysis:**
- Current code location: `src/main/sensors/pitotmeter.c:315-323`
- Proposed sanity check algorithm
- GPS cross-validation approach
- Edge cases and false positive prevention
- Testing strategy

## Objectives

Implement robust pitot sensor validation that:

1. **Cross-validates pitot readings against GPS groundspeed**
   - Detect implausible readings (e.g., 25 km/h when GPS shows 85 km/h)
   - Account for wind (use wind estimator if available)
   - Tolerate reasonable discrepancies (±30% for wind uncertainty)

2. **Detects common failure modes**
   - Blocked pitot tube (reads too low or zero)
   - Pitot cover left on (reads zero or very low)
   - Mechanical failure (stuck reading)
   - Rate-of-change anomalies (sudden unrealistic changes)

3. **Automatic fallback to virtual airspeed**
   - When pitot fails validation, use GPS-based virtual airspeed
   - Seamless transition (no control glitches)
   - Continue validation to detect recovery

4. **Pilot warning via OSD**
   - Display "PITOT FAIL - VIRTUAL" when using virtual airspeed
   - Clear indication that sensor has failed
   - Warning persists until pitot validates again

## Implementation Requirements

### 1. Pitot Validation Function

**Location:** `src/main/sensors/pitotmeter.c`

**Enhance `pitotValidForAirspeed()` or create new function:**

```c
bool pitotValidForAirspeed(void) {
    // Existing checks
    if (!pitotIsHealthy()) return false;

    // NEW: GPS-based sanity check
    if (!pitotPassesGpsSanityCheck()) {
        pitotFailureState = PITOT_FAIL_SANITY;
        return false;
    }

    return true;
}

bool pitotPassesGpsSanityCheck(void) {
    // Only validate if GPS is available and valid
    if (!sensors(SENSOR_GPS) || !STATE(GPS_FIX)) {
        return true; // Can't validate without GPS, assume OK
    }

    float pitotAirspeed = getAirspeedEstimate();
    float gpsGroundspeed = gpsSol.groundSpeed; // cm/s

    // Get wind estimate if available
    float windSpeed = 0;
    if (isEstimatedWindValid()) {
        windSpeed = getEstimatedWindSpeed();
    }

    // Calculate expected airspeed range
    // Airspeed = groundspeed ± wind (with uncertainty margin)
    float minExpectedAirspeed = gpsGroundspeed - windSpeed - SANITY_MARGIN;
    float maxExpectedAirspeed = gpsGroundspeed + windSpeed + SANITY_MARGIN;

    // Check if pitot reading is plausible
    if (pitotAirspeed < minExpectedAirspeed * 0.7 ||
        pitotAirspeed > maxExpectedAirspeed * 1.3) {
        // Pitot reading implausible
        return false;
    }

    // Check rate of change (detect sudden jumps)
    if (abs(pitotAirspeed - lastPitotAirspeed) > MAX_AIRSPEED_CHANGE_RATE * dT) {
        return false;
    }

    return true;
}
```

**Key parameters to define:**
- `SANITY_MARGIN` - uncertainty margin for wind (e.g., 30% of GPS speed)
- `MAX_AIRSPEED_CHANGE_RATE` - maximum realistic airspeed change (e.g., 5 m/s²)
- Hysteresis to prevent oscillation between valid/invalid

### 2. Failure State Tracking

**Add to pitot state:**
```c
typedef enum {
    PITOT_OK,
    PITOT_FAIL_TIMEOUT,
    PITOT_FAIL_CALIBRATION,
    PITOT_FAIL_SANITY,      // NEW: Failed GPS sanity check
} pitotFailureState_e;

pitotFailureState_e pitotFailureState = PITOT_OK;
```

### 3. Automatic Fallback

**In APA code (`pid.c`):**
```c
// Use virtual airspeed if pitot fails validation
float airspeed;
if (pitotValidForAirspeed()) {
    airspeed = getAirspeedEstimate(); // Pitot-based
} else {
    airspeed = getVirtualAirspeed();  // GPS-based fallback
}

// Continue with APA calculation using validated airspeed
```

### 4. OSD Warning

**Add OSD element:**
```c
// In OSD code
if (pitotFailureState == PITOT_FAIL_SANITY) {
    displayWrite(osdDisplayPort, x, y, "PITOT FAIL - VIRTUAL");
}
```

**Requirements:**
- Display prominently when pitot fails sanity check
- Blink or highlight to ensure pilot notices
- Clear when pitot validates again

## Edge Cases to Handle

### 1. GPS Not Available
- Can't validate without GPS - assume pitot is OK
- Don't fail pitot just because GPS is unavailable
- Only validate when GPS fix is good

### 2. Wind Uncertainty
- Wind estimator may not be accurate in all conditions
- Use conservative margins (±30% or more)
- Better to tolerate some error than false positive

### 3. Aggressive Maneuvers
- During rapid climbs/dives, airspeed changes rapidly
- Rate-of-change check should account for normal maneuvers
- Consider disabling validation during high-g maneuvers

### 4. Takeoff/Landing
- Low airspeeds near stall speed
- GPS and pitot may legitimately differ
- Consider minimum airspeed threshold before validation

### 5. Hysteresis
- Once pitot fails, require sustained good readings to re-validate
- Prevent rapid oscillation between valid/invalid
- Example: Require 5 consecutive good readings to clear failure

## Testing Requirements

### 1. SITL Testing

**Scenario 1: Blocked Pitot at Cruise**
```bash
# Simulate pitot reading 25 km/h while GPS shows 85 km/h
# Expected: Pitot fails sanity check, automatic fallback to virtual
# Expected: OSD shows "PITOT FAIL - VIRTUAL"
# Expected: Aircraft remains controllable with correct gains
```

**Scenario 2: Pitot Recovery**
```bash
# Pitot blocked, then unblocked
# Expected: Sustained good readings restore pitot validity
# Expected: OSD warning clears
# Expected: Smooth transition back to pitot-based airspeed
```

**Scenario 3: Windy Conditions**
```bash
# Simulate strong headwind/tailwind
# Expected: Validation accounts for wind
# Expected: No false positives with legitimate wind
```

### 2. Hardware Testing (If Available)

- Cover pitot tube, observe automatic fallback and warning
- Uncover pitot tube, observe recovery
- Fly in various wind conditions, verify no false positives
- Verify aircraft remains controllable when pitot fails

### 3. Regression Testing

- Ensure no impact when pitot is working normally
- Verify virtual airspeed still works when GPS unavailable
- Check all existing pitot functionality unchanged

## Files to Modify

**Primary:**
- `src/main/sensors/pitotmeter.c` - Add GPS sanity check validation
- `src/main/sensors/pitotmeter.h` - Add failure state enum, function declarations

**Secondary:**
- `src/main/flight/pid.c` - Use validated airspeed for APA
- `src/main/io/osd.c` - Add pitot failure warning display
- `src/main/fc/settings.yaml` - Add parameters if needed (margins, thresholds)

**Documentation:**
- `docs/Sensors.md` or `docs/Pitot.md` - Document pitot validation
- `docs/OSD.md` - Document pitot failure warning

## Implementation Phases

### Phase 1: Core Validation (4-5 hours)
1. Read analysis document section on pitot validation
2. Implement GPS-based sanity check algorithm
3. Add failure state tracking
4. Test in SITL with blocked pitot scenario

### Phase 2: Automatic Fallback (2-3 hours)
1. Integrate validation into APA code
2. Ensure seamless fallback to virtual airspeed
3. Test transition behavior (no control glitches)

### Phase 3: OSD Warning (1-2 hours)
1. Add OSD element for pitot failure
2. Test display in SITL
3. Ensure warning clears on recovery

### Phase 4: Edge Cases and Polish (2-3 hours)
1. Handle wind uncertainty
2. Add hysteresis for stability
3. Handle takeoff/landing edge cases
4. Add rate-of-change validation

### Phase 5: Testing and Documentation (2-3 hours)
1. Comprehensive SITL testing
2. Hardware testing if available
3. Update documentation
4. Create test cases

## Success Criteria

- [ ] GPS-based pitot sanity check implemented
- [ ] Detects blocked/failed pitot (reads low when GPS shows cruise)
- [ ] Automatic fallback to virtual airspeed
- [ ] OSD warning displays when pitot fails
- [ ] No false positives in normal flight (including wind)
- [ ] Smooth transitions (no control glitches)
- [ ] Edge cases handled properly
- [ ] SITL tests pass all scenarios
- [ ] Hardware testing successful (if available)
- [ ] Documentation updated
- [ ] Code review addressed

## Deliverables

1. **Code Implementation**
   - Pitot validation with GPS sanity checks
   - Automatic fallback logic
   - OSD warning display
   - Edge case handling

2. **Testing**
   - SITL test scenarios documented
   - Hardware test results (if available)
   - Test cases for regression testing

3. **Documentation**
   - Updated sensor documentation
   - OSD documentation for warning
   - Code comments explaining algorithm

4. **Pull Request**
   - Clear description of safety improvement
   - Reference GitHub issue #11208
   - Reference analysis document
   - Test results included

5. **Completion Report**
   - Summary of implementation
   - Test results
   - Any issues encountered
   - Recommendations for users

## Important Notes

### This is a Safety Feature

**Pitot failures are common and dangerous:**
- Forgotten pitot covers before takeoff
- Blocked tubes from insects/dirt
- Mechanical failures
- Ice accumulation

**This feature makes aircraft flyable when pitot fails.**

### Conservative Approach

- **Avoid false positives** - Don't fail pitot when it's actually working
- Use wide margins for wind uncertainty
- Only validate when GPS is reliable
- Require sustained failures before triggering

### GPS Dependency

- Feature requires GPS for validation
- Falls back to existing behavior without GPS
- Virtual airspeed already GPS-based (this just makes it automatic)

### User Impact

- Transparent when pitot works correctly (no change)
- Automatic safety when pitot fails (major improvement)
- Clear warning when using virtual airspeed (pilot awareness)

### Backward Compatibility

- Existing functionality unchanged
- New validation adds safety without breaking anything
- Users can disable if needed (parameter)

## Parameters to Consider

**Potential settings.yaml entries:**
```yaml
- name: pitot_gps_sanity_check
  description: "Enable GPS-based pitot sanity checking [OFF/ON]"
  default_value: ON

- name: pitot_sanity_margin
  description: "Airspeed sanity check margin in % of GPS speed"
  default_value: 30
  min: 10
  max: 50
```

## References

- **Analysis Document:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`
- **GitHub Issue:** https://github.com/iNavFlight/inav/issues/11208
- **Parent Project:** analyze-pitot-blockage-apa-issue (COMPLETED)
- **Current Code:** `src/main/sensors/pitotmeter.c:315-323`
- **Related Code:** `src/main/flight/pid.c` (APA implementation)

---

**Manager**
