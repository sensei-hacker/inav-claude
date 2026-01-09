# Task Completed: Fix preload.mjs forEach Error

## Status: COMPLETED

## Summary

Fixed an IPC listener memory leak that caused `forEach` errors, plus fixed a duplicate callback registration bug that caused CRC errors and MSP timeouts.

## PR

No PR yet - changes are local. Ready for review before PR submission.

## Root Cause Analysis

### Issue 1: forEach Error on undefined

The error `Cannot read properties of undefined (reading 'forEach')` occurred because:

1. **IPC listeners accumulated without cleanup**: Each time a connection object was created, it registered IPC event listeners that were never removed.

2. **No removal mechanism existed**: The `preload.js` API only provided `on*` methods, no `off*` methods.

3. **Stale listeners fired on destroyed objects**: Old listeners tried to access `this._onReceiveListeners` on garbage-collected objects.

### Issue 2: CRC Errors and MSP Timeouts (discovered during testing)

During testing, we discovered CRC failures introduced in commit `1562b38f`. Root cause:

1. **Duplicate callback registration**: The base class `addOnReceiveListener()` was:
   - Pushing callback to `_onReceiveListeners` array
   - ALSO calling `addOnReceiveCallback()` which pushed again

2. **Result**: Every data packet was delivered twice to each listener, corrupting MSP protocol parsing.

3. **Why it wasn't caught before**: Prior to the ESM refactor fix, `addOnReceiveCallback` pushed to the wrong array (`_onReceiveErrorListeners`), so it was effectively a no-op.

## Changes

### 1. `js/main/preload.js` - Added IPC listener removal methods

- Modified all `on*` handlers to return the handler function
- Added corresponding `off*` methods using `ipcRenderer.removeListener()`
- Affected: TCP, Serial, UDP, ChildProcess handlers

### 2. `js/connection/connectionSerial.js` - Lazy IPC registration

- IPC handlers registered at connect time via `registerIpcListeners()`
- Cleanup via `removeIpcListeners()` on disconnect
- Prevents stale handlers when connection object is reused

### 3. `js/connection/connectionTcp.js` - Same pattern

- `registerIpcListeners()` and `removeIpcListeners()` methods added

### 4. `js/connection/connectionUdp.js` - Same pattern

- `registerIpcListeners()` and `removeIpcListeners()` methods added

### 5. `js/connection/connection.js` - Two fixes

- Call `removeIpcListeners()` during disconnect if subclass implements it
- **Fixed duplicate registration**: Removed `addOnReceiveCallback()` call from `addOnReceiveListener()` (and same for error variant)

## Testing

- **Build**: `npm start` builds successfully
- **Serial connection**: Works, no CRC errors
- **Flashing**: Works correctly
- **Tab switching**: Works correctly
- **Reconnect**: Works correctly

## Files Modified

- `js/main/preload.js`
- `js/connection/connection.js`
- `js/connection/connectionSerial.js`
- `js/connection/connectionTcp.js`
- `js/connection/connectionUdp.js`

## Notes

- `connectionBle.js` unchanged - uses Web Bluetooth API, not IPC
- Fixed typo: "Serial conenection closed" -> "Serial connection closed"
- The CRC bug was technically introduced in commit `1562b38f` which fixed the wrong array names but exposed the duplicate registration issue
