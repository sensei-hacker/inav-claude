# Task Assignment: Implement Fix for Issue #9912 Auto-Trim

**Date:** 2025-12-28 11:05
**Project:** Issue #9912 - Continuous Auto-Trim During Maneuvers
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 3-4 hours
**Branch:** From `maintenance-9.x`

## Task

Implement the fix for Issue #9912 based on your completed root cause analysis. Create a PR and mark it with "needs testing" label.

## Background

You completed the analysis and identified the root cause:
- **Issue:** Missing I-term stability check in servo autotrim
- **Location:** `src/main/flight/servos.c:644`
- **Problem:** Transient I-term is transferred to servo trim during maneuver transitions
- **Report:** `claude/developer/reports/issue-9912-autotrim-analysis.md`

## What to Do

### 1. Implement I-term Stability Detection

Based on your analysis, implement the fix:

**Current code (`servos.c:644`):**
```c
if (fabsf(axisIterm) > SERVO_AUTOTRIM_UPDATE_SIZE) {
    // Immediately transfers to trim - no stability check
}
```

**Required fix:**
```c
if (fabsf(axisIterm) > SERVO_AUTOTRIM_UPDATE_SIZE && itermIsStable) {
    // Only transfer when I-term rate of change is low
}
```

**Implementation details:**
- Track I-term rate of change (delta per 500ms cycle)
- Only allow trim update when rate of change is below threshold
- Add configurable parameter for rate limit threshold
- Consider using a moving average or low-pass filter on I-term delta

### 2. Add Configuration Parameter

Add a new parameter to control I-term stability detection:

```c
// In appropriate settings group (e.g., servoConfig or navConfig)
uint16_t servo_autotrim_iterm_threshold;  // Maximum I-term change rate (units TBD)
```

**Default value:** Choose conservatively based on typical I-term behavior

### 3. Test with DEBUG_AUTOTRIM

Enable and test with the DEBUG_AUTOTRIM mode:

```bash
# Build SITL with debug enabled
cd inav
/build-sitl

# Run SITL and test maneuvers
# Monitor servoMiddleUpdateCount during:
# - Straight and level flight (should update normally)
# - Turn entry/exit (should NOT update during transients)
# - Other maneuvers
```

**Test scenarios:**
1. Straight and level → should apply autotrim normally
2. During turn → should NOT apply autotrim
3. Transition from turn to level → should NOT apply until I-term stabilizes
4. Verify transient I-term is not transferred to trim

### 4. Update Documentation

If needed, update any relevant documentation about autotrim behavior.

### 5. Create Pull Request

**Use the /create-pr skill:**

```bash
/create-pr
```

**PR Title:** "Fix #9912: Add I-term stability check to servo autotrim"

**PR Description template:**
```markdown
## Summary
Fixes #9912 - Continuous auto-trim active during maneuvers

Add I-term stability detection to servo autotrim to prevent transferring transient I-term to servo trim during maneuver transitions.

## Root Cause
The autotrim code verified all flight conditions (level attitude, centered sticks, low rotation rate) but failed to check that the I-term was in a steady state before transferring it to servo trim.

During maneuver transitions (e.g., exiting a turn), I-term accumulates transient error. When the plane momentarily satisfies all level-flight conditions, this transient I-term is incorrectly transferred to servo midpoints.

## Changes
- Added I-term rate-of-change tracking
- Added stability threshold check before applying autotrim
- Added configurable parameter: `servo_autotrim_iterm_threshold`
- Only transfers I-term to trim when rate of change is below threshold

## Testing
- [x] Tested with DEBUG_AUTOTRIM in SITL
- [x] Straight and level: autotrim works normally
- [x] During turns: autotrim does not activate
- [x] Turn transitions: autotrim waits for I-term to stabilize

**Note:** This PR requires flight testing to validate the fix in real-world conditions.

## Related
- Issue #9912
- Analysis report: `claude/developer/reports/issue-9912-autotrim-analysis.md`

Fixes #9912
```

**IMPORTANT:** Add the "needs testing" label to the PR:
```bash
gh pr edit <PR_NUMBER> --add-label "needs testing"
```

## Success Criteria

- [ ] I-term rate-of-change tracking implemented
- [ ] Stability threshold check added before autotrim
- [ ] Configuration parameter added and documented
- [ ] Tested with DEBUG_AUTOTRIM in SITL
- [ ] Straight and level flight: autotrim works normally
- [ ] During maneuvers: autotrim correctly waits for stability
- [ ] PR created from `maintenance-9.x` branch
- [ ] PR marked with "needs testing" label
- [ ] PR references issue #9912
- [ ] CI builds passing

## Files to Modify

**Primary:**
- `inav/src/main/flight/servos.c` - Add I-term stability check
- `inav/src/main/fc/settings.yaml` (or appropriate config file) - Add parameter

**Reference:**
- Your analysis report: `claude/developer/reports/issue-9912-autotrim-analysis.md`
- Issue #9912 on GitHub
- DEBUG_AUTOTRIM implementation

## Notes

**Branch:** Use `maintenance-9.x` as base branch

**Needs Testing Label:** Critical! This fix changes flight behavior and requires real-world flight testing to validate. The "needs testing" label ensures maintainers know this needs actual flight verification.

**Parameter Tuning:** The I-term stability threshold may need tuning based on flight testing feedback. Choose a conservative default that errs on the side of caution (stricter stability requirement).

**Consider Edge Cases:**
- Very slow I-term drift (should still allow autotrim)
- Gusty conditions (may cause I-term fluctuations)
- Different aircraft types (fixed-wing vs multirotor)

**Testing Limitations:** SITL testing can verify the logic works, but cannot fully validate real flight dynamics. Make this clear in the PR description.

---
**Manager**
