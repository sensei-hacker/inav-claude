# Project: Reproduce Issue #9912 - Continuous Auto Trim During Maneuvers

**Status:** 🚧 IN PROGRESS (Theory Identified, Needs Verification)
**Priority:** MEDIUM
**Type:** Testing / Bug Reproduction / Root Cause Analysis
**Created:** 2025-12-23
**Estimated Effort:** 3-5 hours (original), additional time for verification

## Overview

Investigate and reproduce GitHub issue #9912 where continuous auto trim remains active during maneuvers, causing incorrect servo midpoint adjustments.

**GitHub Issue:** https://github.com/iNavFlight/inav/issues/9912

## Problem

Users report that continuous auto trim is incorrectly adjusting servo midpoints during maneuvers, not just during steady level flight as intended.

## Progress

Developer performed deep code analysis and identified a **theory** for the root cause (not yet verified).

## Theory - Missing I-term Stability Check

**Location:** `src/main/common/servos.c:644`

The autotrim function verifies flight conditions before transferring I-term to servo midpoints:
- Level flight attitude
- Centered sticks
- Low rotation rates

**BUT** it fails to check if the I-term is in **steady state**.

**The Bug Mechanism:**
1. During maneuvers, I-term accumulates transient error (normal PID behavior)
2. Plane momentarily satisfies level-flight conditions (attitude, sticks, rotation)
3. At that moment, the transient I-term value is incorrectly transferred to servo midpoints
4. This captures maneuver-induced error as a permanent trim offset

**Key Insight:** The I-term during a maneuver contains transient error that should NOT be treated as trim offset. Only steady-state I-term (stable over time) represents actual trim requirements.

## Proposed Fix

Add I-term rate-of-change stability check before allowing trim transfer:

```c
// Pseudocode concept
static float previousIterm[AXIS_COUNT];
static timeMs_t lastItermCheck;

bool isItermStable(int axis) {
    float itermDelta = fabs(currentIterm[axis] - previousIterm[axis]);
    float deltaTime = currentTime - lastItermCheck;
    float itermRate = itermDelta / deltaTime;

    // Only allow trim if I-term has been stable for sufficient time
    return itermRate < ITERM_STABILITY_THRESHOLD;
}
```

## Verification Needed

Theory needs verification through one of:

1. **SITL Reproduction:** Create test script to reproduce the bug
   - Simulate maneuvers followed by brief level periods
   - Check if trim changes during these transitions

2. **Pilot Testing:** Have pilot test the proposed fix on real hardware
   - Compare trim behavior before/after fix
   - Verify fix doesn't break normal trim operation

3. **Additional Analysis:** Further code investigation to confirm theory
   - Trace exact code path during maneuver → level transition
   - Verify I-term values at trim transfer point

## Files Involved

- `src/main/common/servos.c` - Main autotrim logic (line 644)
- `src/main/flight/pid.c` - I-term calculation
- Analysis report: `claude/developer/reports/issue-9912-autotrim-analysis.md`

## Success Criteria

- [ ] Theory verified through reproduction or testing
- [ ] Root cause confirmed
- [ ] Fix implemented and tested
- [ ] PR created if fix verified
- [ ] Issue #9912 resolved or updated with findings

## Next Steps

1. Either create SITL reproduction script (original task goal)
2. Or work with pilot/maintainers to test proposed fix
3. Verify theory matches actual bug behavior before implementing fix

## Related

- **GitHub Issue:** [#9912](https://github.com/iNavFlight/inav/issues/9912)
- **Analysis Report:** `claude/developer/reports/issue-9912-autotrim-analysis.md`
- **Assignment Email:** `claude/manager/sent/2025-12-23-0029-task-reproduce-issue-9912.md`
