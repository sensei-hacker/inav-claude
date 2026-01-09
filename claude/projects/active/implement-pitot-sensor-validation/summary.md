# Project: Implement Pitot Sensor Validation with GPS Sanity Checks

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Safety Feature Implementation
**Created:** 2026-01-02
**Estimated Effort:** 8-12 hours
**Milestone:** 9.1 or 9.2
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

## Overview

Implement GPS-based pitot sensor validation with automatic fallback to virtual airspeed when pitot readings are implausible or failed.

## Problem

**Parent Analysis:** analyze-pitot-blockage-apa-issue (COMPLETED 2025-12-28)

INAV currently lacks proper airspeed sensor validation. When pitot tubes fail, block, or are left with covers on, the aircraft can become nearly unflyable due to incorrect gain scaling from APA (Airspeed-based PID Attenuation).

**Current Situation:**
- `pitotValidForAirspeed()` only checks: hardware timeout, calibration status, GPS fix (for virtual)
- **Missing:** GPS groundspeed validation, plausibility checks, rate-of-change limits

**Safety Impact:**
- Pitot failures are COMMON (mechanical failure, blockage, forgotten sock)
- Current APA behavior with blocked pitot: 200% gains at cruise speed
- Aircraft becomes nearly unflyable during approach/landing

## Objectives

1. **Cross-validate pitot readings against GPS groundspeed**
   - Detect implausible readings
   - Account for wind (use wind estimator)
   - Tolerate reasonable discrepancies

2. **Detect common failure modes**
   - Blocked pitot tube
   - Pitot cover left on
   - Mechanical failure
   - Rate-of-change anomalies

3. **Automatic fallback to virtual airspeed**
   - Seamless transition when pitot fails validation
   - Continue validation to detect recovery

4. **Pilot warning via OSD**
   - Display "PITOT FAIL - VIRTUAL" warning
   - Clear indication of sensor failure

## Reference Documentation

**REQUIRED READING:**
📄 `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

Sections:
- "Solution 3: GPS-Based Airspeed Sanity Checks"
- "Recommended Solution: Four-Issue Approach - Issue 1"
- "Proposed Implementation: Pitot Sensor Validation"

## Implementation Approach

### Phase 1: Core Validation (4-5 hours)
- Read analysis document
- Implement GPS-based sanity check algorithm
- Add failure state tracking
- SITL testing

### Phase 2: Automatic Fallback (2-3 hours)
- Integrate validation into APA code
- Ensure seamless fallback to virtual airspeed
- Test transition behavior

### Phase 3: OSD Warning (1-2 hours)
- Add OSD element for pitot failure
- Test display in SITL
- Ensure warning clears on recovery

### Phase 4: Edge Cases (2-3 hours)
- Handle wind uncertainty
- Add hysteresis
- Handle takeoff/landing edge cases
- Rate-of-change validation

### Phase 5: Testing & Docs (2-3 hours)
- Comprehensive SITL testing
- Hardware testing if available
- Documentation updates

## Key Algorithm

```c
bool pitotPassesGpsSanityCheck(void) {
    if (!GPS_available) return true;  // Can't validate

    float pitotAirspeed = getAirspeedEstimate();
    float gpsGroundspeed = gpsSol.groundSpeed;
    float windSpeed = getEstimatedWindSpeed();

    // Calculate expected range
    float minExpected = gpsGroundspeed - windSpeed - MARGIN;
    float maxExpected = gpsGroundspeed + windSpeed + MARGIN;

    // Check plausibility
    if (pitotAirspeed < minExpected * 0.7 ||
        pitotAirspeed > maxExpected * 1.3) {
        return false;  // Implausible
    }

    return true;
}
```

## Files to Modify

- `src/main/sensors/pitotmeter.c` - Add GPS sanity check
- `src/main/sensors/pitotmeter.h` - Add failure state enum
- `src/main/flight/pid.c` - Use validated airspeed
- `src/main/io/osd.c` - Add failure warning
- `src/main/fc/settings.yaml` - Add parameters (if needed)
- `docs/` - Document pitot validation

## Success Criteria

- [ ] GPS-based pitot sanity check implemented
- [ ] Detects blocked/failed pitot
- [ ] Automatic fallback to virtual airspeed
- [ ] OSD warning displays properly
- [ ] No false positives in normal flight
- [ ] Smooth transitions (no control glitches)
- [ ] Edge cases handled
- [ ] SITL tests pass
- [ ] Documentation updated

## Value

**Safety Improvement:**
- Makes aircraft flyable when pitot fails
- Common failure mode now handled gracefully
- Clear pilot warning of failure
- Automatic recovery when possible

**Impact:**
- Pitot failures are common (insects, ice, forgotten covers)
- Current behavior is dangerous
- This makes INAV significantly safer

## Related

- Parent analysis: analyze-pitot-blockage-apa-issue (COMPLETED)
- Related task: fix-apa-formula-limits-iterm (separate quick fix)
- GitHub issue: #11208
