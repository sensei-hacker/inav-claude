# TODO: Fix STM32 DFU Reboot Protocol

**Project:** fix-stm32-dfu-reboot-protocol
**Branch:** reboot_to_dfu
**Status:** TODO
**Last Updated:** 2025-11-24

## Phase 1: Analyze & Understand Current Code

### Understanding
- [ ] Read protocol documentation in inav/docs/cli.md
- [ ] Read and document current code flow (lines 95-159)
- [ ] Identify all callback chains and dependencies
- [ ] Map out error handling paths
- [ ] Understand connection API (send/receive/disconnect)
- [ ] Document what each nesting level does

### Analysis
- [ ] Identify which parts can be extracted to functions
- [ ] Determine if Promises/async-await is feasible
- [ ] Check if similar patterns exist elsewhere in file
- [ ] Review connection API for receive/onReceive methods

## Phase 2: Refactor for Clarity (Before Change)

### Extract Helper Functions
- [ ] Create `sendDfuRebootSequence(connection, callback)`
- [ ] Create `pollForRebootCompletion(port, options, callback)`
- [ ] Create `checkForDFU(callback)`
- [ ] Create `checkForSerialPort(port, callback)`
- [ ] Create `handleRebootTimeout(port)`

### Reduce Nesting
- [ ] Convert nested callbacks to sequential function calls
- [ ] Consider Promise-based approach if API supports it
- [ ] Flatten setInterval polling logic
- [ ] Extract tryFailed logic

### Testing After Refactor
- [ ] Verify refactored code behaves identically
- [ ] Test on real hardware (if available)
- [ ] Check all error paths still work
- [ ] Verify logging output unchanged

## Phase 3: Implement Protocol Change

### Response Handling
- [ ] Add onReceive handler to connection
- [ ] Implement waitForResponse(expectedChar, timeout)
- [ ] Handle partial/chunked data
- [ ] Add timeout for "#" response

### Protocol Implementation
- [ ] Create buffer for "####\r\n"
- [ ] Send first command
- [ ] Wait for "#" response (with timeout)
- [ ] Create buffer for "dfu\r\n"
- [ ] Send second command
- [ ] Then proceed to disconnect

### Error Handling
- [ ] Handle timeout waiting for "#"
- [ ] Handle unexpected responses
- [ ] Add clear error messages
- [ ] Log errors appropriately

### Logging
- [ ] Update console.log messages
- [ ] Add protocol step logging
- [ ] Log received responses
- [ ] Log timing information

## Phase 4: Post-Implementation Refactor

### Code Quality
- [ ] Review for further simplification opportunities
- [ ] Ensure consistent error handling
- [ ] Add code comments explaining protocol
- [ ] Check function lengths (<12 lines guideline)
- [ ] Verify total file size

### Documentation
- [ ] Document new protocol in code comments
- [ ] Add JSDoc comments to new functions
- [ ] Reference protocol documentation in comments
- [ ] Note protocol requirements/expectations

## Phase 5: Testing

### Unit Testing
- [ ] Test helper functions individually
- [ ] Mock connection object for testing
- [ ] Test error paths
- [ ] Test timeout scenarios

### Integration Testing
- [ ] Test with real FC hardware
- [ ] Test with multiple FC types (F4, F7, H7)
- [ ] Test with different USB configurations
- [ ] Test timeout scenarios on real hardware

### Regression Testing
- [ ] Verify normal flashing still works
- [ ] Check other reboot methods unaffected
- [ ] Test full DFU workflow end-to-end
- [ ] Verify error messages display correctly

### Edge Cases
- [ ] Test with slow serial connections
- [ ] Test with connection interruptions
- [ ] Test with wrong responses from FC
- [ ] Test timeout scenarios

## Phase 6: Finalization

### Code Review
- [ ] Self-review all changes
- [ ] Check against coding guidelines
- [ ] Verify no console errors
- [ ] Check for TODO comments

### Commit & PR
- [ ] Commit with clear message
- [ ] Push to reboot_to_dfu branch
- [ ] Create pull request
- [ ] Document testing performed

## Notes

- Branch `reboot_to_dfu` already exists
- Target file: `inav-configurator/js/protocols/stm32.js`
- Lines affected: 95-159 (65 lines total)
- Current nesting: 7 levels
- Target nesting: ≤3 levels
- Estimated total time: 3.5-4.5 days

## Answered Questions

**Q: Is there existing protocol documentation for the new DFU sequence?**
A: Yes, documented in inav/docs/cli.md

**Q: Should we support both old and new protocols (feature flag)?**
A: No. New protocol only.

**Q: What FC firmware versions support the new protocol?**
A: All firmware versions support it. Not a concern.

## Blockers

- None currently
