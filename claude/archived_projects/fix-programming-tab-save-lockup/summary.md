# Project: Fix Programming Tab Save Lockup

**Type:** Bug Fix
**Status:** ✅ COMPLETE
**Completed:** 2025-11-24
**Branch:** programming_transpiler_js
**Commit:** 808c5cbc
**Priority:** Medium-High

## Overview

Fix a bug where the "save to flight controller" button in the JavaScript Programming tab causes the Configurator to lock up, preventing tab switching and potentially causing incomplete saves.

## Reported Behavior

**Symptoms:**
- Click "save to flight controller" in JavaScript Programming tab
- Configurator locks up - cannot switch to different tabs
- Only some logic conditions are saved (incomplete save)
- Observed when saving "edge detection" example
- Only seen with DevTools closed (limited debugging info available)

**Expected Behavior:**
- Save should complete successfully
- All logic conditions should be saved
- UI should remain responsive
- User should be able to switch tabs
- Progress indication should be shown

## Technical Context

### Affected Components

**Primary:**
- `tabs/javascript_programming.js` - Main JavaScript programming tab
- Save to FC functionality
- Logic condition serialization
- MSP communication during save

**Related:**
- `js/transpiler/` - Code generation (may affect save payload)
- `js/msp/` - MSP protocol implementation
- Serial communication layer
- UI state management

### Known Information

✅ **Known:**
- Bug triggers on "save to flight controller" button click
- Happens with "edge detection" example
- Only partial save occurs
- DevTools closed when observed (no console errors captured)
- UI becomes unresponsive (tab switching locked)

❌ **Unknown:**
- Does it happen with other examples?
- Does it happen every time or intermittently?
- Exact point of failure in save process
- Whether it's an MSP timeout issue
- Whether it's a transpiler output issue
- Error messages (DevTools was closed)

## Investigation Strategy

### Phase 1: Reproduce the Bug

1. **Reproduce with DevTools open**
   - Load "edge detection" example
   - Open DevTools console
   - Click "save to flight controller"
   - Capture any error messages
   - Note exactly when UI locks up

2. **Test with other examples**
   - Try simple examples (does it work?)
   - Try complex examples (do they also lock up?)
   - Identify pattern - what makes edge detection special?

3. **Verify partial save**
   - Read back logic conditions from FC after lockup
   - Compare with expected conditions
   - Determine which conditions saved and which didn't

### Phase 2: Root Cause Analysis

**Potential Causes to Investigate:**

1. **MSP Communication Issue**
   - Save payload too large?
   - MSP timeout not handled?
   - Response parsing error?
   - Serial buffer overflow?

2. **Transpiler Output Issue**
   - Edge detection generates invalid logic conditions?
   - Malformed MSP payload?
   - Too many conditions for FC memory?

3. **UI State Management**
   - Save button doesn't disable properly?
   - Event handler blocks UI thread?
   - Promise/callback chain broken?
   - Missing error handler causes hang?

4. **Asynchronous Operation Issue**
   - Save process doesn't complete
   - No timeout mechanism
   - Callback never fires
   - Promise never resolves/rejects

### Phase 3: Instrumentation

Add debugging to understand save flow:

```javascript
// Log each step of save process
console.log('[Save] Starting save to FC');
console.log('[Save] Transpiling code');
console.log('[Save] Generated logic conditions:', conditions);
console.log('[Save] Sending MSP command');
console.log('[Save] MSP response received');
console.log('[Save] Save complete');
```

Track:
- How many conditions generated
- Size of MSP payload
- Time taken for each step
- Any errors/warnings

## Reproduction Steps

1. Open INAV Configurator (bak_inav-configurator or inav-configurator)
2. Navigate to JavaScript Programming tab
3. Load "edge detection" example
4. Open DevTools console
5. Click "save to flight controller"
6. Observe:
   - Console messages
   - Network activity
   - UI responsiveness
   - Tab switching ability
7. After lockup (or timeout), read back logic conditions
8. Compare saved vs expected

## Files to Investigate

### Primary Files

- `tabs/javascript_programming.js`
  - Save button click handler
  - Save to FC function
  - MSP command construction
  - UI state management during save

### Supporting Files

- `js/transpiler/index.js` - Transpilation entry point
- `js/transpiler/transpiler/codegen.js` - Logic condition generation
- `js/msp/MSPHelper.js` or similar - MSP communication
- `js/serial.js` or similar - Serial communication

### Example File

- Look for "edge detection" example
  - In `js/transpiler/examples/` directory?
  - Built-in examples list?
  - What makes it special?

## Testing Strategy

### Minimal Test Case

Create simplest code that reproduces issue:
1. Start with edge detection example
2. Remove features one by one
3. Find minimal code that still locks up

### Edge Cases to Test

- [ ] Simple example (1-2 conditions)
- [ ] Complex example (many conditions)
- [ ] Edge detection example (reported case)
- [ ] Maximum conditions (boundary test)
- [ ] Empty/invalid code
- [ ] Code with syntax errors

### Save Flow Testing

- [ ] Save with FC connected (real hardware)
- [ ] Save with SITL
- [ ] Save with no FC connected (should show error)
- [ ] Cancel during save
- [ ] Multiple rapid saves

## Potential Fixes

### If MSP Timeout Issue

```javascript
// Add timeout handling
const savePromise = sendMSPCommand(conditions);
const timeoutPromise = new Promise((_, reject) =>
  setTimeout(() => reject(new Error('Save timeout')), 5000)
);

Promise.race([savePromise, timeoutPromise])
  .then(() => {
    // Success
  })
  .catch(error => {
    // Handle error, unlock UI
  });
```

### If UI Blocking Issue

```javascript
// Ensure save is non-blocking
async function saveToFC() {
  try {
    disableSaveButton();
    showSpinner();

    // Use setTimeout to yield to UI thread
    await new Promise(resolve => setTimeout(resolve, 0));

    const conditions = await transpile();
    const result = await sendToFC(conditions);

    showSuccess();
  } catch (error) {
    showError(error);
  } finally {
    enableSaveButton();
    hideSpinner();
  }
}
```

### If Payload Size Issue

```javascript
// Check payload size before sending
if (conditions.length > MAX_CONDITIONS) {
  showError('Too many logic conditions. Maximum is ' + MAX_CONDITIONS);
  return;
}

if (calculatePayloadSize(conditions) > MAX_MSP_SIZE) {
  showError('Generated code is too large for flight controller');
  return;
}
```

## Success Criteria

- [ ] Bug reproduced with DevTools open
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Edge detection example saves successfully
- [ ] UI remains responsive during save
- [ ] All conditions saved correctly
- [ ] Proper error handling for timeouts
- [ ] Proper error handling for large payloads
- [ ] User feedback during save (spinner/progress)
- [ ] No regressions in other examples

## Risks & Considerations

### Safety Concerns

- Partial saves could leave FC in inconsistent state
- User might not realize save didn't complete
- Could affect flight safety if invalid conditions loaded

### User Impact

- **High** - Blocks core functionality
- Users can't use JavaScript programming feature
- No workaround available

### Complexity

- May require deep dive into MSP protocol
- May need to understand FC memory limitations
- May need serial communication debugging

## Related Issues

- Check GitHub issues for similar reports
- Check Discord/forum for user reports
- May be related to INAV firmware version compatibility

## Notes

- Start with DevTools open to get error messages
- May want to add telemetry/logging to save process
- Consider adding save validation step
- Should show clear error messages to user
- Consider adding "verify save" function to read back and compare

## Implementation Summary

**Root Cause Identified:**
The transpiler's `VariableHandler` was being created once in the Parser constructor and reused across multiple `transpile()` calls. When saving to FC, the transpiler is called multiple times, and the second call would fail because variables from the first call were still registered, causing "already declared" errors and blocking the save.

**Solution Implemented:**
**Commit 808c5cbc** - "transpiler: fix VariableHandler state reuse across multiple transpile calls"

Changes made:
- Parser: Create fresh VariableHandler in `parse()` method instead of constructor
- Analyzer: Create fresh VariableHandler if not provided by parser
- Test infrastructure: Support multiple transpile calls with same instance

**Testing:**
- ✅ 37/37 VariableHandler unit tests passing
- ✅ 14/14 integration tests passing
- ✅ Save to FC now completes successfully without lockup

**Impact:**
- Users can now save JavaScript programming logic conditions without configurator lockup
- All logic conditions save properly
- UI remains responsive throughout save process
