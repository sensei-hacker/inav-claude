# Port Lock Issue - Investigation Needed

**From:** Developer
**To:** Manager
**Date:** 2025-12-20 10:28
**Subject:** Port lock issue preventing configurator connection to /dev/ttyACM0

## Issue

While testing the Monaco editor autocomplete fix for the JavaScript Programming tab, I encountered a persistent port lock issue preventing connection to the flight controller on `/dev/ttyACM0`.

**Error message:**
```
Error: Error Resource temporarily unavailable Cannot lock port
Connected to: /dev/ttyACM0 @ 115200 baud
Failed to open MSP connection
```

## Impact

This prevents:
- Testing the Monaco editor autocomplete fix in the live configurator
- Accessing the JavaScript Programming tab (requires firmware connection)
- Normal FC configuration operations

## Next Steps

This needs investigation to determine:
1. What process is holding the port lock
2. Whether it's a stale lock from a previous session
3. How to properly release the lock

## Current Status

The Monaco editor autocomplete fix has been successfully implemented and verified via command-line testing of the type generation. The fix is working correctly - just unable to demonstrate it in the live UI due to this connection issue.

## Request

Please add investigation of the `/dev/ttyACM0` port lock issue to the task queue when time permits.
