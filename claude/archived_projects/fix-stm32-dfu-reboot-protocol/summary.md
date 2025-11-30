# Fix STM32 DFU Reboot Protocol

**Status:** ✅ COMPLETE - Tested and working
**Priority:** Medium
**Type:** Bug Fix / Protocol Update
**Created:** 2025-11-24
**Assigned:** 2025-11-24
**Completed:** 2025-11-24
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-1720-task-fix-stm32-dfu-reboot.md`
**Branch:** `reboot_to_dfu`
**Commits:** b46c6c59, 6fc3f30c, e943ccaa
**Target Files:**
- `inav-configurator/js/protocols/stm32.js` (refactoring + new protocol)
- `inav-configurator/js/connection/connectionSerial.js` (critical bug fix)
- `inav-configurator/js/protocols/stm32usbdfu.js` (cleanup callback fix)

## Overview

Update the STM32 reboot protocol to use the new DFU command sequence instead of the legacy 'R' command. The affected code is deeply nested and needs refactoring before implementation.

## Current Behavior (Lines 98-108)

```javascript
console.log('Sending ascii "R" to reboot');
var bufferOut = new ArrayBuffer(1);
var bufferView = new Uint8Array(bufferOut);
bufferView[0] = 0x52;  // ASCII 'R'
CONFIGURATOR.connection.send(bufferOut, function () {
    // ... disconnect and poll
});
```

**Current flow:**
1. Send single character 'R' (0x52)
2. Immediately disconnect
3. Poll for DFU or serial port to reappear

## Required Behavior (New Protocol)

**New flow:**
1. Send "####\r\n"
2. Wait for "#" character to come back
3. Send "dfu\r\n"
4. Then disconnect and poll (existing logic)

**Protocol sequence:**
```
TX: ####\r\n
RX: #
TX: dfu\r\n
(then disconnect and poll)
```

## Problem: Deep Nesting (Lines 95-159)

The current code has **6-7 levels of nested callbacks**:
```
connect() callback
  └─ send() callback
      └─ disconnect() callback
          └─ setInterval()
              └─ check_usb_devices() callback
                  └─ ConnectionSerial.getDevices() callback
                      └─ connect() callback
```

**Issues:**
- Hard to read and understand
- Difficult to modify safely
- Error handling scattered throughout
- Testing is challenging

## Implementation Approach

### Phase 1: Refactor for Clarity (Before Protocol Change)

**Goal:** Make the code understandable before changing it

1. **Extract helper functions** to reduce nesting:
   ```javascript
   // Extract polling logic
   function pollForReboot(port, options, callback) { ... }

   // Extract DFU check
   function checkForDFU(port, callback) { ... }

   // Extract serial port check
   function checkForSerialPort(port, callback) { ... }
   ```

2. **Consider using Promises** instead of callbacks:
   - Modern JavaScript
   - Better error handling
   - Easier to read sequential flow
   - Can use async/await

3. **Separate concerns:**
   - Connection management
   - Protocol commands
   - Polling/retry logic

**Target:** Reduce nesting from 6-7 levels to 2-3 levels maximum

### Phase 2: Implement Protocol Change

After refactoring, implement the new protocol:

1. **Create DFU command function:**
   ```javascript
   function sendDfuRebootSequence(connection, callback) {
       // Send ####\r\n
       connection.send(createBuffer("####\r\n"), function() {
           // Wait for # response
           waitForResponse(connection, "#", function(received) {
               if (received) {
                   // Send dfu\r\n
                   connection.send(createBuffer("dfu\r\n"), function() {
                       callback(true);
                   });
               } else {
                   callback(false);
               }
           });
       });
   }
   ```

2. **Replace line 98-108** with call to new function

3. **Add response handling** - currently there's no code to read incoming data before disconnect

### Phase 3: Refactor Again (After Protocol Change)

Clean up and optimize the new code:
- Ensure consistent error handling
- Add logging at each step
- Document the protocol
- Simplify if possible

## Technical Details

### Current Code Structure (Lines 95-159)

```javascript
CONFIGURATOR.connection.connect(port, {bitrate: self.options.reboot_baud}, function (openInfo) {
    if (openInfo) {
        console.log('Sending ascii "R" to reboot');
        GUI.connect_lock = true;

        var bufferOut = new ArrayBuffer(1);
        var bufferView = new Uint8Array(bufferOut);
        bufferView[0] = 0x52;  // 'R'

        CONFIGURATOR.connection.send(bufferOut, function () {
            CONFIGURATOR.connection.disconnect(function (result) {
                if (result) {
                    var intervalMs = 200;
                    var retries = 0;
                    var maxRetries = 50;
                    var interval = setInterval(function() {
                        var tryFailed = function() {
                            retries++;
                            if (retries > maxRetries) {
                                clearInterval(interval);
                                GUI.log(i18n.getMessage('failedToFlash') + port);
                            }
                        }
                        // Check for DFU devices
                        PortHandler.check_usb_devices(function(dfu_available) {
                            if (dfu_available) {
                                clearInterval(interval);
                                STM32DFU.connect(usbDevices, hex, options);
                                return;
                            }
                            // Check for the serial port
                            ConnectionSerial.getDevices(function(devices) {
                                if (devices && devices.includes(port)) {
                                    CONFIGURATOR.connection.connect(port, {bitrate: self.baud, parityBit: 'even', stopBits: 'one'}, function (openInfo) {
                                        if (openInfo) {
                                            clearInterval(interval);
                                            self.initialize();
                                        } else {
                                            GUI.connect_lock = false;
                                            tryFailed();
                                        }
                                    });
                                    return;
                                }
                                tryFailed();
                            });
                        });
                    }, intervalMs);
                } else {
                    GUI.connect_lock = false;
                }
            });
        });
    } else {
        GUI.log(i18n.getMessage('failedToOpenSerialPort'));
    }
});
```

**Complexity metrics:**
- Total lines: 65
- Nesting depth: 7 levels
- Functions defined inside: 3
- Callbacks: 7
- Conditional branches: 8

### Key Challenges

1. **Response handling:** Current code doesn't read responses before disconnect
   - Need to add `onReceive` handler
   - Need to implement timeout for waiting for "#"
   - Must handle partial data (data might arrive in chunks)

2. **Timing:** Must not disconnect until after receiving "#" and sending "dfu\r\n"
   - Current code disconnects immediately after send
   - New code must wait for response before disconnect

3. **Error handling:** What if "#" never comes back?
   - Add timeout
   - Fall back to old behavior?
   - Report error to user?

4. **Testing:** How to test this without actual hardware?
   - Mock serial connection
   - Simulate responses
   - Integration test with real FC

## Files to Modify

**Primary:**
- `inav-configurator/js/protocols/stm32.js` (lines 95-159)

**May need to review:**
- Connection API documentation (how to receive data)
- Error handling patterns in rest of file
- Similar code patterns elsewhere in file

## Scope

### In Scope
- Refactor lines 95-159 for clarity
- Implement new DFU reboot protocol (####\r\n → # → dfu\r\n)
- Add response handling
- Add proper error handling and timeouts
- Update logging messages
- Test with real hardware

### Out of Scope
- Changing other reboot methods in the file
- Modifying STM32DFU.connect() behavior
- Backwards compatibility (NOT needed - all firmware versions support new protocol)

## Risks

**Medium Risk:**
- Breaking existing flash/DFU functionality
- Timing issues with serial communication
- Hardware-specific behavior differences

**Mitigation:**
- Test thoroughly on multiple FC types
- Keep old code commented for reference
- Add feature flag if needed
- Document expected behavior clearly

## Testing Strategy

1. **Code review** - Ensure refactoring preserves behavior
2. **Static analysis** - Lint, check for common errors
3. **Manual testing:**
   - Flash firmware via DFU on multiple FC types
   - Test with different USB cables/hubs
   - Test timeout scenarios
   - Test error paths

4. **Regression testing:**
   - Ensure normal flashing still works
   - Ensure other reboot methods unaffected

## Success Criteria

- [x] Lines 95-159 refactored to ≤3 nesting levels
- [x] New protocol implemented: ####\r\n → CLI → dfu\r\n
- [x] Response handling works correctly
- [x] Timeout handling prevents hangs
- [x] Error messages are clear and helpful
- [x] Code is well-documented
- [x] Tested successfully on real hardware
- [x] No regressions in existing functionality
- [x] Bonus: Fixed critical connectionSerial.js callback bug
- [x] Bonus: Fixed DFU cleanup preventing reconnection

## Estimated Effort

- **Phase 1 (Refactoring):** 1-2 days
- **Phase 2 (Protocol change):** 1 day
- **Phase 3 (Cleanup):** 0.5 days
- **Testing:** 1 day
- **Total:** 3.5-4.5 days

## References

- Branch: `reboot_to_dfu`
- File: `inav-configurator/js/protocols/stm32.js:95-159`
- Protocol documentation: `inav/docs/cli.md` (or similar)

## Implementation Summary

### What Was Accomplished

**Phase 1: Refactoring (Completed)**
- Reduced callback nesting from 9 levels → 3 levels
- Extracted `pollForRebootCompletion()` helper function
- Extracted `sendRebootCommand()` helper function
- Extracted `waitForResponse()` helper for serial response handling
- Greatly improved code readability and maintainability

**Phase 2: New Protocol (Completed)**
- Implemented CLI-based DFU reboot sequence:
  1. Send `####\r\n` to enter CLI mode
  2. Wait for CLI prompt response (with 2s timeout)
  3. Send `dfu\r\n` command
  4. Disconnect and poll for DFU/serial reappearance
- Replaced legacy single 'R' character command
- Added proper error handling and timeout logic

**Bonus Fixes Discovered & Implemented:**

1. **Critical Bug in connectionSerial.js** (Lines 109-114)
   - `addOnReceiveCallback()` was pushing to wrong array (`_onReceiveErrorListeners` instead of `_onReceiveListeners`)
   - Caused all receive callbacks to never fire
   - **Impact:** This bug would have prevented ANY serial receive callbacks from working
   - Fixed by correcting array references

2. **DFU Cleanup Callback Not Called** (stm32usbdfu.js:445-448)
   - When USB controlTransfer fails (expected during device reboot), callback was never called
   - Left `GUI.connect_lock = true`, preventing reconnection
   - **Impact:** Required restarting configurator after every DFU flash
   - Fixed by calling callback with error code even on failure

### Testing Results

✅ All functionality tested and working:
- DFU reboot protocol successfully enters CLI mode
- DFU flashing completes successfully
- Post-flash reconnection works without restarting configurator
- Error handling and timeouts function correctly

### Files Modified

1. **js/protocols/stm32.js** (+148 lines, refactored 65 lines)
   - New helper methods for cleaner code structure
   - New CLI-based DFU protocol implementation

2. **js/connection/connectionSerial.js** (+2 lines changed)
   - Fixed critical callback registration bug

3. **js/protocols/stm32usbdfu.js** (+2 lines)
   - Ensured cleanup callback fires even on USB error

### Branch Structure

- **`reboot_to_dfu`** - Main branch with all changes (ready for PR)
- **`fix-dfu-cleanup-callback`** - Separate branch off master with just the DFU cleanup fix (independent PR)

## Notes

- Follow file size (150 lines) and function length (12 lines) guidelines
- If helper functions are extracted, consider separate module
- Modern JavaScript (Promises/async-await) preferred over callbacks
- Ensure backward compatibility testing
