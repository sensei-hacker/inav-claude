# Task Completed: fix-cli-align-mag-roll-invalid-name

## Status: COMPLETED - Not a Bug

## Summary

The reported issue where `set align_mag_roll = <value>` returns "Invalid name" was investigated and determined to be target-specific behavior, not a firmware bug.

## Root Cause

The NexusX target does not define `USE_MAG` in its target configuration. Magnetometer-related settings like `align_mag_roll`, `align_mag_pitch`, and `align_mag_yaw` are conditionally compiled and only available on targets with magnetometer support enabled.

## Resolution

No code fix required. This is expected behavior - targets without magnetometer hardware don't expose mag settings in CLI.

**User solutions:**
- Use a target with mag support enabled
- If hardware supports mag, enable `USE_MAG` in target's `target.h`

## PR Reference

https://github.com/iNavFlight/inav/pull/11157

## Files Modified

None - no code changes needed.

## Notes

This is working as designed. The conditional compilation system correctly excludes settings for hardware features not supported by the target.
