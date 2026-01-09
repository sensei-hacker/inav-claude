# Task Assignment: Fix STM32 DFU Reboot Protocol

**Date:** 2025-11-24 17:20
**Project:** fix-stm32-dfu-reboot-protocol
**Priority:** Medium
**Estimated Effort:** 3.5-4.5 days
**Branch:** `reboot_to_dfu` (already exists)

## Task Overview

Update the STM32 reboot protocol from the legacy single 'R' command to the new DFU command sequence. The affected code is deeply nested (7 levels) and needs refactoring before implementing the protocol change.

## Current vs Required Behavior

### Current (Legacy Protocol)
**File:** `inav-configurator/js/protocols/stm32.js:98-108`

```javascript
console.log('Sending ascii "R" to reboot');
var bufferOut = new ArrayBuffer(1);
var bufferView = new Uint8Array(bufferOut);
bufferView[0] = 0x52;  // ASCII 'R'
CONFIGURATOR.connection.send(bufferOut, function () {
    // Immediately disconnect and poll
});
```

**Flow:**
1. Send 'R' character
2. Disconnect
3. Poll for DFU/serial port

### Required (New DFU Protocol)

**Protocol sequence:**
```
TX: ####\r\n
RX: #                  ← Wait for this response
TX: dfu\r\n
(then disconnect and poll as before)
```

**Flow:**
1. Send "####\r\n"
2. **Wait for "#" response** (new requirement)
3. Send "dfu\r\n"
4. Disconnect and poll (existing logic)

**Protocol documented in:** `inav/docs/cli.md`

## The Challenge: Deep Nesting

**Current code structure (lines 95-159):**
```
connect() callback
  └─ send() callback
      └─ disconnect() callback
          └─ setInterval()
              └─ check_usb_devices() callback
                  └─ ConnectionSerial.getDevices() callback
                      └─ connect() callback
```

**Complexity metrics:**
- 65 lines total
- 7 levels of nesting
- 7 callbacks
- 3 functions defined inside
- 8 conditional branches

**Problems:**
- Extremely difficult to read and understand
- Nearly impossible to modify safely
- Error handling scattered throughout
- Adding response handling would make it even worse

## Implementation Approach: 3 Phases

### Phase 1: Refactor for Clarity (BEFORE Protocol Change)

**Goal:** Make code understandable BEFORE changing it

**Tasks:**
1. **Extract helper functions** to reduce nesting:
   ```javascript
   function sendDfuRebootSequence(connection, callback) { ... }
   function pollForRebootCompletion(port, options, callback) { ... }
   function checkForDFU(callback) { ... }
   function checkForSerialPort(port, callback) { ... }
   ```

2. **Consider modern JavaScript:**
   - Promises instead of callbacks (if API supports it)
   - async/await for sequential flow
   - Better error handling

3. **Target:** Reduce from 7 levels to ≤3 levels maximum

**Success criteria for Phase 1:**
- Code functionally identical (test on hardware)
- Nesting reduced to 2-3 levels
- Each function <12 lines where possible
- Ready for protocol change

### Phase 2: Implement Protocol Change

After refactoring, implement the new protocol:

**Key additions:**
1. **Response handling** - current code doesn't read before disconnect:
   ```javascript
   function waitForResponse(connection, expectedChar, timeout, callback) {
       // Add onReceive handler
       // Implement timeout
       // Handle partial/chunked data
   }
   ```

2. **Protocol implementation:**
   - Create buffer: "####\r\n"
   - Send first command
   - Wait for "#" (with timeout)
   - Create buffer: "dfu\r\n"
   - Send second command
   - Proceed to disconnect

3. **Error handling:**
   - What if "#" never comes? (timeout)
   - What if wrong response? (error message)
   - Clear logging at each step

**Success criteria for Phase 2:**
- New protocol implemented correctly
- Response handling works
- Timeout prevents hangs
- Error messages clear and helpful

### Phase 3: Cleanup & Polish

**Tasks:**
- Review for further simplification
- Ensure consistent error handling
- Add comprehensive code comments
- Document the protocol
- Verify function lengths
- Update logging messages

## Technical Requirements

### Must Haves
- [ ] Reduce nesting to ≤3 levels (from 7)
- [ ] Implement new protocol: `####\r\n` → wait for `#` → `dfu\r\n`
- [ ] Add response handling (currently doesn't exist)
- [ ] Add timeout for waiting for "#" response
- [ ] Handle partial/chunked data correctly
- [ ] Clear error messages for all failure scenarios
- [ ] Maintain existing disconnect/poll logic
- [ ] Test successfully on real hardware

### Code Quality Guidelines
- Function length: ≤12 lines (with judgment for cohesive logic)
- File size: Keep additions reasonable
- Use helper functions when >40 new lines in one place
- Modern JavaScript preferred (Promises/async-await if API supports)
- JSDoc comments for new functions
- Inline comments explaining protocol steps

### Questions Already Answered

**Q: Is there protocol documentation?**
✅ Yes, in `inav/docs/cli.md`

**Q: Need backward compatibility / feature flag?**
✅ No. All firmware versions support the new protocol.

**Q: Which firmware versions support this?**
✅ All versions. Not a concern.

## Scope

### In Scope
- Refactor `stm32.js:95-159` for clarity
- Implement new DFU protocol sequence
- Add response handling and timeout
- Test on real hardware
- Update logging messages
- Document protocol in code

### Out of Scope
- Other reboot methods in the file (unchanged)
- STM32DFU.connect() behavior (unchanged)
- Backwards compatibility (not needed)

## Testing Strategy

### After Phase 1 (Refactor)
- [ ] Verify behavior identical to original
- [ ] Test on real hardware (if available)
- [ ] All error paths still work
- [ ] Logging output unchanged

### After Phase 2 (Protocol Change)
- [ ] Flash firmware via DFU on multiple FC types (F4, F7, H7)
- [ ] Test timeout scenarios
- [ ] Test error paths
- [ ] Test with different USB cables/hubs
- [ ] Verify logging shows protocol steps

### Regression Testing
- [ ] Normal flashing still works
- [ ] Other reboot methods unaffected
- [ ] No console errors
- [ ] Error messages display correctly

## Risks & Mitigation

**Risk:** Breaking existing flash/DFU functionality
**Mitigation:**
- Refactor first, verify identical behavior
- Test on multiple FC types
- Keep old code commented for reference

**Risk:** Timing issues with serial communication
**Mitigation:**
- Proper timeout handling
- Test with different hardware
- Handle partial data correctly

**Risk:** Hardware-specific behavior
**Mitigation:**
- Test on F4, F7, H7 if possible
- Clear error messages for debugging

## Success Criteria

**Definition of Done:**
- [ ] Lines 95-159 refactored to ≤3 nesting levels
- [ ] New protocol implemented: `####\r\n` → `#` → `dfu\r\n`
- [ ] Response handling works correctly
- [ ] Timeout prevents infinite waits
- [ ] Error messages clear and helpful
- [ ] Code well-documented
- [ ] Tested successfully on real hardware
- [ ] No regressions in existing functionality
- [ ] Code follows quality guidelines

## Estimated Timeline

**Phase 1 (Refactoring):** 1-2 days
- Extract functions
- Reduce nesting
- Test for identical behavior

**Phase 2 (Protocol):** 1 day
- Add response handling
- Implement new sequence
- Initial testing

**Phase 3 (Cleanup):** 0.5 days
- Polish code
- Final documentation

**Testing:** 1 day
- Hardware testing
- Regression testing
- Edge cases

**Total:** 3.5-4.5 days

## Project Files

**Location:** `claude/projects/fix-stm32-dfu-reboot-protocol/`

**Files:**
- `summary.md` - Complete project overview and technical details
- `todo.md` - Detailed phase-by-phase checklist

**Branch:** `reboot_to_dfu` (already exists)

**Target file:** `inav-configurator/js/protocols/stm32.js` (lines 95-159)

## Key Insights

1. **Refactor BEFORE changing** - Don't try to add protocol AND fix nesting simultaneously
2. **Extract functions** - Each level of nesting should become a named function
3. **Modern JavaScript** - Consider Promises/async-await if API allows
4. **Response handling is new** - Current code doesn't read responses before disconnect
5. **Test incrementally** - After refactor, after protocol, after cleanup

## Getting Started

1. Read `inav/docs/cli.md` - understand the protocol specification
2. Review current code (`stm32.js:95-159`) - understand all callback chains
3. Check connection API - how to receive data (onReceive handler?)
4. Start Phase 1 - begin extracting helper functions
5. Test frequently - verify behavior after each extraction

## Questions?

If you encounter issues or need clarification:
- Check project files: `claude/projects/fix-stm32-dfu-reboot-protocol/`
- Protocol docs: `inav/docs/cli.md`
- Connection API: Review other parts of `stm32.js` for receive patterns
- Report blockers via inbox with specific questions

## Notes

- This is a medium priority task
- Branch already exists: `reboot_to_dfu`
- No backward compatibility concerns
- Focus on clarity - this code will be maintained for years
- Modern, readable code is better than clever, dense code

---

**Manager**

**Assignment:** This task is now assigned to you. Please acknowledge receipt and begin with Phase 1 when ready.
