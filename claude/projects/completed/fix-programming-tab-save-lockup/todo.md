# TODO: Fix Programming Tab Save Lockup

## Phase 1: Reproduce & Document

### Setup Environment
- [ ] Ensure bak_inav-configurator is available
- [ ] Install dependencies if needed
- [ ] Verify transpiler is working
- [ ] Locate "edge detection" example

### Reproduce with DevTools
- [ ] Launch configurator with DevTools open
- [ ] Navigate to JavaScript Programming tab
- [ ] Load "edge detection" example
- [ ] Click "save to flight controller"
- [ ] Capture console output
- [ ] Capture network activity
- [ ] Note exact behavior (when does it lock up?)
- [ ] Take screenshots if helpful

### Document Bug Details
- [ ] Record exact error messages
- [ ] Note console warnings
- [ ] Document lockup symptoms
- [ ] Check if Configurator crashes or just hangs
- [ ] Try force-quit and restart
- [ ] Document state after restart

### Verify Partial Save
- [ ] After lockup, restart configurator
- [ ] Connect to FC (or SITL)
- [ ] Read back logic conditions
- [ ] Compare with expected from edge detection
- [ ] Document which conditions saved
- [ ] Document which conditions missing

### Test Other Examples
- [ ] Try simplest example
- [ ] Try medium complexity example
- [ ] Try most complex example
- [ ] Document which work and which don't
- [ ] Look for pattern

## Phase 2: Investigation

### Examine Save Flow Code
- [ ] Read `tabs/javascript_programming.js`
- [ ] Find save button click handler
- [ ] Trace save to FC function
- [ ] Understand MSP command construction
- [ ] Check for error handling
- [ ] Check for timeouts
- [ ] Look for async/await or promise handling

### Analyze Edge Detection Example
- [ ] Find edge detection example code
- [ ] Run through transpiler manually
- [ ] Check generated logic conditions
- [ ] Count number of conditions
- [ ] Calculate payload size
- [ ] Compare with other examples

### Check MSP Implementation
- [ ] Find MSP helper/communication code
- [ ] Check command size limits
- [ ] Check timeout values
- [ ] Check error handling
- [ ] Look for buffer overflow protections

### Identify Root Cause
- [ ] Test hypothesis: MSP timeout
- [ ] Test hypothesis: Payload too large
- [ ] Test hypothesis: UI thread blocking
- [ ] Test hypothesis: Broken promise chain
- [ ] Test hypothesis: Missing error handler
- [ ] Document findings

## Phase 3: Create Fix

### Design Solution
- [ ] Choose fix strategy based on root cause
- [ ] Consider edge cases
- [ ] Plan error handling
- [ ] Plan user feedback
- [ ] Get approval if needed

### Implement Fix
- [ ] Add proper timeout handling
- [ ] Add payload size validation
- [ ] Add progress indication
- [ ] Ensure async operations don't block UI
- [ ] Add error handling for all failure modes
- [ ] Add logging for debugging

### Add Safety Checks
- [ ] Validate transpiled output before saving
- [ ] Check condition count against limits
- [ ] Check payload size against limits
- [ ] Disable save button during save
- [ ] Re-enable button on completion/error

### Improve User Feedback
- [ ] Show spinner/progress during save
- [ ] Show success message
- [ ] Show clear error messages
- [ ] Allow cancel if possible
- [ ] Update UI state properly

## Phase 4: Testing

### Test Fix with Original Bug
- [ ] Load edge detection example
- [ ] Save to FC
- [ ] Verify no lockup
- [ ] Verify all conditions saved
- [ ] Verify UI responsive
- [ ] Verify can switch tabs

### Test All Examples
- [ ] Test simple examples
- [ ] Test complex examples
- [ ] Test edge detection
- [ ] Test maximum size example
- [ ] All should save successfully

### Test Error Conditions
- [ ] Test with no FC connected
- [ ] Test with disconnected FC (unplug during save)
- [ ] Test with SITL
- [ ] Test with real hardware
- [ ] Test rapid repeated saves
- [ ] Test cancel during save

### Regression Testing
- [ ] Verify transpiler still works
- [ ] Verify load from FC works
- [ ] Verify examples load correctly
- [ ] Verify other tabs unaffected
- [ ] No new bugs introduced

### Verify Save Correctness
- [ ] After save, read back conditions
- [ ] Compare with expected
- [ ] Verify byte-for-byte match
- [ ] Test on real FC if possible

## Phase 5: Documentation

### Update Code Comments
- [ ] Document save flow
- [ ] Document error handling
- [ ] Document timeout values
- [ ] Document size limits

### User Documentation
- [ ] Update any user guides if needed
- [ ] Document known limitations
- [ ] Document error messages

### Developer Documentation
- [ ] Document fix in commit message
- [ ] Add comments explaining the bug
- [ ] Document any changes to save protocol

## Phase 6: Pull Request

### Prepare PR
- [ ] Create clear PR description
- [ ] Include before/after behavior
- [ ] Link to bug report (if exists)
- [ ] Include test results
- [ ] Add screenshots/videos if helpful

### Address Review
- [ ] Respond to review comments
- [ ] Make requested changes
- [ ] Re-test after changes

### Merge
- [ ] Get approval
- [ ] Merge to main branch
- [ ] Verify in next release

## Additional Tasks

### Optional Improvements
- [ ] Add save verification (read back and compare)
- [ ] Add save history/undo
- [ ] Add diff view before save
- [ ] Add dry-run mode
- [ ] Add detailed save log

### Follow-up Investigation
- [ ] Why was edge detection special?
- [ ] Are there firmware version compatibility issues?
- [ ] Should we add automated tests for save?
- [ ] Should we add MSP command size checks elsewhere?

## Notes

- Prioritize getting error messages first (DevTools open)
- Don't make changes until root cause is clear
- Consider user safety - partial saves are dangerous
- May need to coordinate with firmware team if FC-side issue
- Document everything - this could help debug similar issues
