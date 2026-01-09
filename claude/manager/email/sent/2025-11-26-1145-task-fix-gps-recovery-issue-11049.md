# Task Assignment: Fix GPS Recovery After Signal Loss (Issue #11049)

**Date:** 2025-11-26 11:45
**Project:** fix-gps-recovery-issue-11049
**Priority:** Medium-High
**Estimated Effort:** 4-8 hours
**Branch:** From master
**GitHub Issue:** https://github.com/iNavFlight/inav/issues/11049

## Task

Investigate and fix a bug where altitude and distance-to-home values get stuck at zero after GPS signal loss and recovery.

## Background

This issue was identified during the GitHub issues review. When GPS signal is lost and then recovered, users report that altitude and distance-to-home displays remain stuck at zero instead of updating with the recovered GPS data. This is a safety concern as it affects pilot situational awareness during flight.

## What to Do

1. **Read the GitHub issue** (#11049) to understand the full context, user comments, and any additional details

2. **Investigate the GPS recovery code path:**
   - Study `src/main/io/gps.c` - GPS signal handling
   - Study `src/main/navigation/navigation_pos_estimator.c` - Position estimation
   - Study `src/main/navigation/navigation.c` - Main navigation logic
   - Understand how GPS fix status is tracked and what triggers "recovered" state

3. **Identify the root cause:**
   - Trace what happens when GPS fix is lost
   - Trace what happens when GPS fix is recovered
   - Find where altitude/distance-to-home are being zeroed
   - Find why they don't restore on recovery

4. **Implement fix:**
   - Design a solution that properly restores values after GPS recovery
   - Ensure no regressions in normal GPS operation
   - Keep changes minimal and focused

5. **Test:**
   - Verify code compiles (SITL target)
   - If possible, test GPS loss/recovery in SITL
   - Document any testing performed

## Success Criteria

- [ ] Root cause identified and documented
- [ ] Fix implemented
- [ ] Code compiles successfully (SITL)
- [ ] No obvious regressions in GPS handling
- [ ] Testing completed (as feasible)

## Files to Check

- `src/main/navigation/navigation.c`
- `src/main/navigation/navigation_pos_estimator.c`
- `src/main/navigation/navigation_pos_estimator_private.h`
- `src/main/io/gps.c`
- `src/main/io/gps.h`
- `src/main/sensors/sensors.h`

## Notes

- This requires understanding of the navigation subsystem
- Be careful with changes - navigation code is safety-critical
- If the issue is complex, a detailed investigation report is valuable even without a complete fix
- Check if there are related issues or PRs that might provide context

## Deliverables

- Completion report with:
  - Root cause analysis
  - Description of fix (if implemented)
  - Testing performed
  - Branch name and commit
  - Recommendation for PR submission

---
**Manager**
