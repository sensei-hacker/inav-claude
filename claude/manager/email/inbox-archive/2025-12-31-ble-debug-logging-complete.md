# Task Complete: BLE Debug Logging

**Date:** 2025-12-31
**Project:** add-ble-debug-logging
**Status:** Complete - Ready for Testing
**File Modified:** `inav-configurator/js/connection/connectionBle.js`

## Summary

Added comprehensive debug logging to the BLE (Bluetooth Low Energy) connection code in INAV Configurator to diagnose Windows connection issues where data is sent but not received.

## Changes Made

### 1. Connection Sequence Logging

Added detailed logging throughout the entire BLE connection flow:

- **Device Request (`request()`)**: Logs device discovery, device ID, initial GATT state
- **Device Opening (`openDevice()`)**: Logs the sequence: request → connect → start notifications
- **Connection (`connectImplementation()`)**: Logs path, options, success/failure
- **GATT Connection (`connectBle()`)**: Most detailed logging added here

### 2. Service and Characteristic Discovery

The `connectBle()` function now logs:

- Number of services found and their UUIDs
- Device type matching (CC2541, Nordic NRF, SpeedyBee Type 1/2)
- Expected write/read characteristic UUIDs
- All characteristics found with their properties:
  - `read`, `write`, `writeWithoutResponse`, `notify`, `indicate`
- Which characteristic is used for WRITE
- Which characteristic is used for READ (notifications)
- Any mismatches or missing characteristics

### 3. Notification Setup Logging

The `startNotification()` function now logs:

- Which characteristic notifications are being enabled on
- Full characteristic properties
- Validation that the characteristic supports `notify`
- Success/failure with timing
- Ready status message

### 4. Data Transmission Logging

The `sendImplementation()` function now logs:

**Before sending:**
- Total bytes to send
- Number of chunks (20-byte BLE buffer limit)
- Full data in hex and ASCII format
- Target characteristic UUID

**Per chunk:**
- Chunk number and size
- Hex data for each chunk
- Write duration per chunk
- Any write errors with details

**After sending:**
- Total bytes sent
- Total chunks
- Total transmission time

### 5. Data Reception Logging

The notification handler (`_handleOnCharateristicValueChanged`) now logs:

**When data is received:**
- Number of bytes received
- Data in hex format
- Data in ASCII format (printable chars only)
- Timestamp

**This is the KEY logging** - if no data appears here, we know notifications aren't working.

### 6. Disconnect and Error Logging

Added logging for:
- GATT server disconnect events (with device name, ID, timestamp)
- Disconnect process (step-by-step)
- All error conditions with detailed error objects
- Connection state changes

## What This Will Show

### If Working Correctly:

```
[BLE] → SENDING 27 bytes (will split into 2 chunks of max 20 bytes):
[BLE]   Hex:   24 4d 3c 00 00 ...
[BLE]   Chunk 1: Writing 20 bytes: 24 4d 3c ...
[BLE]   Chunk 1: Write completed in 5ms
[BLE]   Chunk 2: Writing 7 bytes: ...
[BLE]   Chunk 2: Write completed in 3ms
[BLE] ✓ All data sent: 27 bytes in 2 chunks (total time: 8ms)

[BLE] ← RECEIVED 15 bytes:
[BLE]   Hex:   24 4d 3e 0b ...
[BLE]   ASCII: $M>...
[BLE]   Timestamp: 1704034567890
```

### If Broken (Windows Issue):

```
[BLE] → SENDING 27 bytes ...
[BLE]   Chunk 1: Write completed in 5ms
[BLE]   Chunk 2: Write completed in 3ms
[BLE] ✓ All data sent: 27 bytes in 2 chunks (total time: 8ms)

(NO RECEIVED MESSAGES - THIS IS THE BUG)
```

## Testing Required

### Prerequisites:
- Windows machine with BLE device "SYNERDUINO7-BT-E-LE" (or similar)
- INAV Configurator running in development mode

### Test Steps:

1. **Start configurator in dev mode:**
   ```bash
   cd inav-configurator
   npm start
   ```

2. **Open DevTools:** Press Ctrl+Shift+I to open Chrome DevTools console

3. **Connect to BLE device:**
   - Click BLE connection button
   - Select the device
   - Observe console output

4. **Capture logs:**
   - Copy all console output starting from `[BLE] === Starting BLE connection sequence ===`
   - Save to a file for analysis

5. **Look for these specific things:**

   ✅ **Service Discovery:**
   - Are the correct services found?
   - Does the service UUID match one of: CC2541, Nordic NRF, or SpeedyBee?

   ✅ **Characteristic Properties:**
   - Does the READ characteristic have `notify: true`?
   - Does the WRITE characteristic have `write: true` or `writeWithoutResponse: true`?

   ✅ **Notifications:**
   - Does `startNotifications()` succeed?
   - Is the event listener added successfully?

   ✅ **Data Flow:**
   - Do you see `[BLE] → SENDING` messages?
   - Do you see any `[BLE] ← RECEIVED` messages?
   - **If no RECEIVED messages, that confirms the bug**

   ✅ **Errors:**
   - Any error messages in the log?
   - Any unexpected characteristic UUIDs?

## Hypotheses to Test

Based on the original issue report, here are possible causes:

### 1. Wrong Characteristic for Notifications
**Check:** Are notifications being enabled on the correct characteristic?
**Look for:** Mismatch between `readCharateristic` UUID in the device profile and the actual characteristic

### 2. Notification Property Not Supported
**Check:** Does the characteristic actually support `notify`?
**Look for:** `canNotify: false` in the characteristic properties log

### 3. Event Listener Not Firing
**Check:** Is the `characteristicvaluechanged` event actually firing?
**Look for:** Event listener added successfully but never receiving events

### 4. Windows-Specific Web Bluetooth Bug
**Check:** Does the same code work on Linux/macOS?
**Look for:** Platform-specific behavior differences

### 5. Data Format Issue
**Check:** Is data being received but in wrong format?
**Look for:** Events firing but `value.byteLength` being 0

## Files Modified

- `inav-configurator/js/connection/connectionBle.js` (lines 63-373)

## Next Steps

1. **User Testing:** Need Windows machine with BLE device to test
2. **Log Analysis:** Capture full console output during connection attempt
3. **Root Cause:** Identify why notifications aren't delivering data
4. **Fix:** Implement solution based on root cause
5. **Verify:** Confirm data reception works after fix

## Notes

- All logging uses `[BLE]` prefix for easy filtering
- Hex and ASCII output helps identify MSP protocol frames
- Timing information helps identify performance issues
- Error details include error name, code, and message for debugging

## Original Issue

- User: Windows machine
- Device: SYNERDUINO7-BT-E-LE
- Problem: Connection succeeds, notifications start, but **0 bytes received**
- Sent: 27 bytes
- Received: 0 bytes
- MSP requests timeout

This logging will help identify exactly where the data flow breaks down.

---

**Developer**
