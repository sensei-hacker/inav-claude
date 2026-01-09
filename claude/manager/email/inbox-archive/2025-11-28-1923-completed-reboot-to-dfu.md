# Task Completed: Reboot to DFU and IPC Listener Fixes

## Status: COMPLETED

## Summary

The reboot_to_dfu feature for inav-configurator is complete and pushed. This includes fixes for DFU flashing reliability and an IPC listener memory leak that caused forEach errors and CRC failures.

## Branch

`reboot_to_dfu` pushed to origin (sensei-hacker/inav-configurator)

## Commits (6 total)

1. Reboot to dfu: replace "R" with "# dfu", Also refactor dfu reboot
2. DFU reboot - remove extra debugging code
3. DFU flash: Fix failure to connect after flash (skipped cleanup callback)
4. Reconnect after flash: Valid bot suggestions
5. Improve STM32 DFU reboot reliability and add upfront DFU check
6. Fix IPC listener memory leak and duplicate callback bug

## Changes

### DFU Reboot Feature
- Replace "R" reboot command with "# dfu" for more reliable DFU entry
- Add upfront DFU device check before attempting reboot
- Fix cleanup callback that was being skipped after flash

### IPC Listener Fix (commit 6)
- Add off* methods to preload.js for IPC listener removal
- Implement lazy IPC registration in connection classes
- Fix duplicate callback registration that caused CRC errors
- Affected files: preload.js, connection.js, connectionSerial.js, connectionTcp.js, connectionUdp.js

## Testing

- Build: npm start successful
- Serial connection: Works, no CRC errors
- DFU flashing: Works correctly
- Tab switching: Works correctly
- Reconnect after flash: Works correctly

## Files Modified

- js/main/preload.js
- js/connection/connection.js
- js/connection/connectionSerial.js
- js/connection/connectionTcp.js
- js/connection/connectionUdp.js
- .gitignore

## Notes

Ready for PR creation to upstream when desired.
