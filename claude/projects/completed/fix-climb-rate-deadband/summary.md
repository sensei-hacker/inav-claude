# Project: Fix Climb Rate Deadband Applied Twice

**Status:** 📋 TODO
**Priority:** Medium
**Type:** Bug Fix
**Created:** 2026-01-08
**GitHub Issue:** #10660

## Overview

Fix issue where manual climb rate doesn't match configurator setting because the RC deadband is applied twice in the altitude hold code path.

## Problem

In `navigation_multicopter.c`, the deadband is applied twice:
1. First at line 140: `rcCommand = applyDeadbandRescaled(...)`
2. Again at lines 149 and 153 which operate on the already-deadbanded value

This causes the actual climb rate to differ from the configured value.

**Current flow:**
```c
// Line 140 - First deadband application
rcCommand = applyDeadbandRescaled(rcCommand, rcControlsConfig()->alt_hold_deadband, -500, 500);

// Lines 149, 153 - These assume rcCommand hasn't had deadband applied yet
// but it already has, causing incorrect calculations
```

## Solution

Reorder the code so deadband is applied after the neutral point calculation:

```c
// Move deadband application after the -500/500 adjustment
rcCommand = rcCommand - 500;
rcCommand = applyDeadbandRescaled(rcCommand, rcControlsConfig()->alt_hold_deadband, -500, 500);
```

The reporter has tested this fix and confirms it works correctly.

## Files to Modify

- `src/main/navigation/navigation_multicopter.c` lines 140-153

## Testing

1. Build SITL or firmware
2. Configure specific climb rate in configurator
3. Test altitude hold mode
4. Measure actual climb rate matches configured value
5. Verify throttle response feels correct

## Success Criteria

- [ ] Deadband applied only once in climb rate calculation
- [ ] Manual climb rate matches configurator setting
- [ ] Altitude hold behavior unchanged at stick center
- [ ] No regression in altitude hold stability

## Notes

- Bug has existed since at least INAV 3.0.0
- Reporter has tested the fix
- Affects all multicopter altitude hold users
- May explain "my climb rate feels wrong" reports
