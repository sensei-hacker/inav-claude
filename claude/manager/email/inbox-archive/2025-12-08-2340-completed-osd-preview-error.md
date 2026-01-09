# Task Completion: Fix OSD Preview Error

**Date:** 2025-12-08
**From:** Developer
**Task:** fix-osd-preview-error

## Status: COMPLETE

## Summary

Fixed the "Offset is outside the bounds of the DataView" error occurring when opening the OSD tab. The root cause was race conditions in MSP data loading for logic conditions.

## Changes Made

1. **MSPHelper.js**: Added buffer length checks before DataView access
   - `MSP2_INAV_LOGIC_CONDITIONS_SINGLE`: checks `data.byteLength >= 14`
   - `MSP2_INAV_LOGIC_CONDITIONS_CONFIGURED`: checks `data.byteLength >= 8`
   - Added timeout fallback for firmware that doesn't support optimized path

2. **osd.js**: Fixed logic conditions race condition
   - Added callback to `loadLogicConditions()` that refreshes LC dropdowns after load
   - Added guard in `getLCoptions()` to return empty if conditions not yet loaded

## Commits

- **Branch:** feature/progressive-settings-loading
- **Commits:**
  - `159806ace` - Fix OSD tab race conditions with async data loading
  - `2df96a970` - Make optimized logic condition loading compatible with earlier 9.0-RX* or master (cherry-picked from upstream)

## Resolution

Cherry-picked commit `5bb233e6b` from `upstream/maintenance-9.x` which contained the complete fix including the MSPHelper.js buffer bounds checks that were causing the DataView error.

## Testing

- Confirmed OSD tab loads without DataView errors
- Logic condition dropdowns populate correctly after async load completes

## Notes

- The qodo-code-review bot suggestion about off-by-one in legacy loop is a false positive - the `-1` is intentional for the callback-chaining pattern
- Pattern documented in `claude/developer/patterns/msp-async-data-access.md`

---
**Developer**
