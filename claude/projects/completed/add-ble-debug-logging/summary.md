# Project: Add BLE Debug Logging

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Debugging / Logging Enhancement
**Created:** 2025-12-29
**Estimated Effort:** 2-3 hours

## Overview

Add comprehensive debug logging to BLE connection code in inav-configurator to diagnose Windows connection issue where data is sent but not received.

## Problem

**User experiencing BLE connection failure on Windows:**
- BLE device "SYNERDUINO7-BT-E-LE" connects successfully
- Notifications appear to start successfully
- Data is sent: 27 bytes
- **Data received: 0 bytes**
- MSP requests timeout
- Connection eventually closes

**Current logging is insufficient** to determine why data isn't being received.

## Issue Analysis

**From log file** (`/home/raymorris/Downloads/inav-log.txt`):
```
Found BLE device: SYNERDUINO7-BT-E-LE ✓
Connect to: SYNERDUINO7-BT-E-LE ✓
BLE notifications started ✓
Connection opened with ID: 255, Baud: 115200 ✓
MSP data request timed-out: 1 ✗
Connection closed, Sent: 27 bytes, Received: 0 bytes ✗
```

**The mystery:**
- Connection setup appears successful
- But no data is received
- Need detailed logging to understand why

## Objectives

1. Add logging around all BLE data write operations
2. Add logging around BLE notification handler (receive)
3. Add logging for service/characteristic discovery
4. Add logging for connection state changes
5. Add detailed error logging
6. Add timing information
7. Reproduce issue with new logging
8. Analyze new logs to identify root cause

## Scope

**In Scope:**
- Adding debug logging to BLE implementation
- Data send logging (hex dump, timing)
- Data receive logging (notification handler)
- Service/characteristic discovery logging
- Connection parameter logging
- Error logging improvements
- Testing on Windows with BLE device
- Analysis of new log output

**Out of Scope:**
- Fixing the actual BLE issue (separate task after diagnosis)
- BLE implementation refactoring
- Adding BLE features
- Cross-platform BLE testing (focus on Windows)

## Implementation Approach

**Key areas to add logging:**

1. **Data transmission:**
   - Before/after write operations
   - Data content (hex dump)
   - Write timing

2. **Data reception:**
   - Notification event handler
   - Received data content (hex dump)
   - Receive timing and latency

3. **Connection setup:**
   - Service discovery
   - Characteristic discovery
   - Characteristic properties (read/write/notify)
   - Notification subscription

4. **Errors:**
   - Wrap operations in try-catch
   - Log detailed error information
   - Connection state changes

## Expected Output

**New log file should show:**
- Which services/characteristics are being used
- Exact data being written (hex dump)
- Whether notification handler is being called
- Any errors during write/read operations
- Timing between operations
- Characteristic properties and capabilities

**This will help identify:**
- Wrong characteristic being used?
- Notifications not actually working?
- Data format issues?
- Silent errors?
- Timing issues?

## Success Criteria

- [ ] BLE code located
- [ ] Write operation logging added
- [ ] Receive/notification logging added
- [ ] Service/characteristic discovery logging added
- [ ] Error logging enhanced
- [ ] Timing logging added
- [ ] Tested on Windows with BLE device
- [ ] New log file captured
- [ ] Log file analyzed
- [ ] Findings reported to manager

## Files to Investigate

**BLE implementation:**
- Likely `js/serial_backend_ble.js` or similar
- Search for "BLE notifications started" string
- Web Bluetooth API usage (navigator.bluetooth)
- GATT service/characteristic handling

## Priority Justification

MEDIUM-HIGH priority because:
- User-reported issue affecting real use case
- BLE is an important connection method
- Windows is a primary platform
- Quick task (2-3 hours) to add logging
- Blocking proper diagnosis of the issue
- Need logs before we can fix the problem

## Notes

**This is a diagnostic task** - we're adding logging to understand the problem, not fixing it yet. The actual fix will be a separate task once we identify the root cause.

**Platform-specific:**
Focus on Windows where issue is occurring.

**Hypotheses to investigate:**
1. Wrong RX characteristic?
2. Notifications not working despite success message?
3. Data format mismatch?
4. MTU issues?
5. Timing/ready state issues?

## Related

- Windows BLE support
- Web Bluetooth API
- GATT protocol
- Serial communication over BLE
