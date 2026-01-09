# Todo List: Fix Pre-existing Tab Errors

## Bug 1: Ports Tab - checkMSPPortCount

- [ ] Investigation
  - [ ] Read `tabs/ports.js` around line 206
  - [ ] Find `on_tab_loaded_handler` function
  - [ ] Locate `checkMSPPortCount()` call
  - [ ] Determine intended purpose

- [ ] Determine Fix Approach
  - [ ] Should function exist? (check git history, similar code)
  - [ ] Should call be removed? (dead code)
  - [ ] Is there a similar function with different name?

- [ ] Implement Fix
  - [ ] Either: Define `checkMSPPortCount()` function
  - [ ] Or: Remove the call if not needed
  - [ ] Or: Fix incorrect function name

- [ ] Test
  - [ ] Navigate to Ports tab
  - [ ] Verify no console error
  - [ ] Test port configuration
  - [ ] Verify MSP ports work correctly

## Bug 2: Magnetometer Tab - modelUrl

- [ ] Investigation
  - [ ] Read `tabs/magnetometer.js` around line 742
  - [ ] Find context of `modelUrl` usage
  - [ ] Determine what it should reference

- [ ] Determine Fix Approach
  - [ ] Should be a variable declaration?
  - [ ] Should be a parameter?
  - [ ] Is it a typo for different variable?
  - [ ] Check if related to 3D model loading

- [ ] Implement Fix
  - [ ] Either: Declare/define `modelUrl` variable
  - [ ] Or: Fix to use correct variable name
  - [ ] Or: Remove if dead code

- [ ] Test
  - [ ] Navigate to Magnetometer tab
  - [ ] Verify no console error
  - [ ] Test magnetometer calibration
  - [ ] Check 3D model display (if present)

## General Testing

- [ ] Clean console
  - [ ] Clear browser console
  - [ ] Load configurator
  - [ ] Navigate through all tabs
  - [ ] Verify no errors for Ports or Magnetometer tabs

- [ ] Functional testing
  - [ ] All tabs load successfully
  - [ ] No new errors introduced
  - [ ] Ports tab fully functional
  - [ ] Magnetometer tab fully functional

## Documentation

- [ ] Document fixes in completion report
  - [ ] Describe what was wrong
  - [ ] Explain fix applied
  - [ ] Confirm testing results

## Completion

- [ ] Both bugs fixed
- [ ] All tests passing
- [ ] Console clean
- [ ] Send completion report to manager
