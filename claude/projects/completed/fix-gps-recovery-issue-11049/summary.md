# Project: Fix GPS Recovery After Signal Loss

**Status:** 📋 TODO
**Priority:** Medium-High
**Type:** Bug Fix
**Created:** 2025-11-26
**GitHub Issue:** [#11049](https://github.com/iNavFlight/inav/issues/11049)
**Estimated Effort:** Medium-High

## Overview

Fix a bug where altitude and distance-to-home values get stuck at zero after GPS signal loss and recovery.

## Problem

When GPS signal is lost and then recovered, the altitude and distance-to-home displays remain stuck at zero instead of updating with the recovered GPS data. This affects situational awareness and could be dangerous during autonomous flight modes.

**User-Reported Behavior:**
- GPS signal drops (normal occurrence)
- GPS signal is recovered
- Altitude display shows 0
- Distance-to-home display shows 0
- Values should update to current GPS-derived values but don't

## Objectives

1. Investigate the GPS recovery code path in INAV firmware
2. Identify why altitude and distance-to-home are not restored
3. Implement a fix that properly restores these values after GPS recovery
4. Ensure fix doesn't introduce regressions in GPS handling

## Scope

**In Scope:**
- Navigation subsystem GPS signal handling
- Altitude calculation after GPS recovery
- Distance-to-home calculation after GPS recovery
- Testing with SITL if possible

**Out of Scope:**
- Other GPS issues not related to signal recovery
- Changes to GPS parsing or protocol handling
- OSD display code (unless directly related to the bug)

## Implementation Steps

1. Research the GPS signal state management in navigation code
2. Trace the code path when GPS is lost and recovered
3. Identify where altitude/distance-to-home values are being zeroed
4. Identify why they're not being restored on recovery
5. Implement fix
6. Test with SITL (simulate GPS loss/recovery if possible)

## Success Criteria

- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Code compiles successfully
- [ ] No regressions in normal GPS operation
- [ ] SITL testing (if GPS loss can be simulated)

## Files to Investigate

- `src/main/navigation/navigation.c` - Main navigation logic
- `src/main/navigation/navigation_pos_estimator.c` - Position estimation
- `src/main/io/gps.c` - GPS handling
- `src/main/sensors/sensors.h` - Sensor status flags

## Priority Justification

Medium-High priority because:
- Safety-related: incorrect altitude/distance affects situational awareness
- User-reported real-world issue
- Could affect autonomous flight decisions
- However, requires navigation expertise and careful testing
