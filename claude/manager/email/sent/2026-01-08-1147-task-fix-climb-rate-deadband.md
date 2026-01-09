# Task Assignment: Fix Climb Rate Deadband Applied Twice

**Date:** 2026-01-08 11:47
**Project:** fix-climb-rate-deadband
**Priority:** Medium
**Repository:** inav
**GitHub Issue:** #10660

## Task

Fix issue where RC deadband is applied twice in altitude hold climb rate calculation.

## What to Do

In `src/main/navigation/navigation_multicopter.c`, around lines 140-153, the deadband is applied twice. Reorder the code so it's only applied once.

**Current problem:**
1. Line 140: `rcCommand = applyDeadbandRescaled(...)` - first application
2. Lines 149, 153: calculations assume no deadband yet applied

**Solution approach:**
Move the `applyDeadbandRescaled()` call to after the `-500` adjustment, so the deadband math works correctly.

See the GitHub issue for the reporter's tested fix with screenshot.

## Why This Matters

Manual climb rate doesn't match the configurator setting. Users configure 300 cm/s climb rate but get something different due to the double-deadband issue.

## Testing

1. Build SITL
2. Configure specific climb rate (e.g., 300 cm/s)
3. Test altitude hold mode
4. Verify actual climb matches configured value

## Success Criteria

- [ ] Deadband applied only once
- [ ] Climb rate matches configurator setting
- [ ] Build passes
- [ ] Comment the fix on GitHub issue #10660

## Notes

- Bug has existed since at least INAV 3.0.0
- Reporter has tested their fix
- Project summary: `claude/projects/fix-climb-rate-deadband/summary.md`

---
**Manager**
