# TODO: Fix Transpiler API Definition Mismatches

## Phase 1: Investigation & Analysis

### Verify the Bug

- [ ] Set up test environment
  - [ ] Clone/checkout bak_inav-configurator branch
  - [ ] Install dependencies
  - [ ] Verify transpiler runs

- [ ] Reproduce the bug
  - [ ] Create test case: `if (flight.yaw > 1800) {...}`
  - [ ] Run through transpiler
  - [ ] Verify generates operand value 17 (wrong!)
  - [ ] Document actual vs expected output

- [ ] Verify against firmware source
  - [ ] Locate INAV firmware operand definitions
  - [ ] Confirm FLIGHT_PARAM values in firmware
  - [ ] Verify inav_constants.js was correctly generated
  - [ ] Document firmware version used

### Analyze Scope

- [ ] Review all API definition files
  - [ ] flight.js - List all properties and operand values
  - [ ] override.js - Check for mismatches
  - [ ] rc.js - Check for mismatches
  - [ ] waypoint.js - Check for mismatches
  - [ ] gvar.js - Check for mismatches
  - [ ] pid.js - Check for mismatches

- [ ] Create comprehensive mismatch report
  - [ ] List every incorrect operand value
  - [ ] Document correct value from inav_constants.js
  - [ ] Note firmware source reference
  - [ ] Prioritize by usage/impact

- [ ] Identify missing parameters
  - [ ] Compare inav_constants.js FLIGHT_PARAM with flight.js
  - [ ] List all 25+ missing parameters
  - [ ] Research what each parameter does
  - [ ] Determine which should be exposed to users

### Research Fix Strategy

- [ ] Analyze current architecture
  - [ ] How are API definitions loaded?
  - [ ] Can they import from inav_constants.js?
  - [ ] Are there circular dependencies?
  - [ ] What's the module loading order?

- [ ] Test constant import approach
  - [ ] Create proof-of-concept with one parameter
  - [ ] Verify constants can be imported
  - [ ] Check for any runtime issues
  - [ ] Verify decompiler still works

- [ ] Evaluate options
  - [ ] Option A: Refactor to use constants (automated sync)
  - [ ] Option B: Manual fix + validation tests
  - [ ] Option C: Auto-generate flight.js from constants
  - [ ] Document pros/cons of each

- [ ] Make decision and document
  - [ ] Choose fix strategy
  - [ ] Document rationale
  - [ ] Get approval if needed

## Phase 2: Design & Planning

### Design the Fix

- [ ] Create detailed implementation plan
  - [ ] List all files to modify
  - [ ] Define exact changes for each file
  - [ ] Identify any refactoring needed
  - [ ] Plan for backwards compatibility

- [ ] Design validation system
  - [ ] Spec out operand validation test suite
  - [ ] Plan round-trip tests
  - [ ] Design CI/CD integration
  - [ ] Plan regression tests

- [ ] Plan migration strategy
  - [ ] How to handle existing user scripts?
  - [ ] Need for migration tool?
  - [ ] Communication plan for users
  - [ ] Deprecation warnings if needed

### Create Test Plan

- [ ] Unit test specifications
  - [ ] Test each operand value matches constant
  - [ ] Test all missing parameters added correctly
  - [ ] Test import/require statements work
  - [ ] Test no regressions in other areas

- [ ] Integration test specifications
  - [ ] Round-trip transpile/decompile tests
  - [ ] Test real JavaScript programming scenarios
  - [ ] Test all flight parameters in context
  - [ ] Test edge cases

- [ ] Manual test procedures
  - [ ] Test on SITL
  - [ ] Test on real hardware (if available)
  - [ ] Test each fixed parameter
  - [ ] Verify UI displays correct values

## Phase 3: Implementation

### Fix Critical Operand Mismatches

- [ ] Update flight.js structure (if using constants approach)
  - [ ] Add require/import for inav_constants.js
  - [ ] Extract OPERAND_TYPE, FLIGHT_PARAM
  - [ ] Test module loads correctly

- [ ] Fix individual parameters in flight.js
  - [ ] Fix: yaw (17 → FLIGHT_PARAM.YAW / 40)
  - [ ] Fix: heading (17 → FLIGHT_PARAM.YAW / 40)
  - [ ] Fix: isArmed (18 → FLIGHT_PARAM.IS_ARMED / 17)
  - [ ] Fix: isAutoLaunch (19 → FLIGHT_PARAM.IS_AUTOLAUNCH / 18)
  - [ ] Fix: isFailsafe (20 → FLIGHT_PARAM.IS_FAILSAFE / 24)
  - [ ] Fix: gpsSats (9 → FLIGHT_PARAM.GPS_SATS / 8)
  - [ ] Fix: groundSpeed (11 → FLIGHT_PARAM.GROUND_SPEED / 9)

- [ ] Investigate uncertain parameters
  - [ ] Research: flightTime (currently 16)
  - [ ] Research: batteryRemainingCapacity (currently 18)
  - [ ] Research: batteryPercentage (currently 19)
  - [ ] Fix or document if not in firmware

### Add Missing Parameters

- [ ] Add missing navigation parameters
  - [ ] IS_ALTITUDE_CONTROL (19)
  - [ ] IS_POSITION_CONTROL (20)
  - [ ] IS_EMERGENCY_LANDING (21)
  - [ ] IS_RTH (22)
  - [ ] IS_LANDING (23)

- [ ] Add missing telemetry parameters
  - [ ] CRSF_LQ_UPLINK (29)
  - [ ] CRSF_SNR (30)
  - [ ] CRSF_LQ_DOWNLINK (44)
  - [ ] CRSF_RSSI_DBM (45)

- [ ] Add missing sensor parameters
  - [ ] AGL_STATUS (35)
  - [ ] AGL (36)
  - [ ] RANGEFINDER_RAW (37)

- [ ] Add missing control parameters
  - [ ] STABILIZED_ROLL (25)
  - [ ] STABILIZED_PITCH (26)
  - [ ] STABILIZED_YAW (27)

- [ ] Add missing configuration parameters
  - [ ] ACTIVE_PROFILE (33)
  - [ ] BATT_CELLS (34)
  - [ ] ACTIVE_MIXER_PROFILE (38)
  - [ ] MIXER_TRANSITION_ACTIVE (39)
  - [ ] BATT_PROFILE (42)

- [ ] Add missing distance/speed parameters
  - [ ] SPEED_3D (10)
  - [ ] AIR_SPEED (11)
  - [ ] HOME_DISTANCE_3D (28)
  - [ ] LOITER_RADIUS (32)
  - [ ] FLOWN_LOITER_RADIUS (43)

- [ ] Add missing state parameters
  - [ ] FW_LAND_STATE (41)

### Verify Other API Files

- [ ] Check override.js
  - [ ] Review all operand values
  - [ ] Fix any mismatches found
  - [ ] Add missing parameters if any

- [ ] Check rc.js
  - [ ] Review all operand values
  - [ ] Fix any mismatches found
  - [ ] Add missing parameters if any

- [ ] Check waypoint.js
  - [ ] Review all operand values
  - [ ] Fix any mismatches found
  - [ ] Add missing parameters if any

## Phase 4: Testing

### Create Automated Tests

- [ ] Create operand validation test file
  - [ ] Test flight.js values match FLIGHT_PARAM
  - [ ] Test override.js values (if applicable)
  - [ ] Test rc.js values (if applicable)
  - [ ] Test all operand types are correct

- [ ] Create round-trip tests
  - [ ] Test: flight.yaw transpile/decompile
  - [ ] Test: flight.isArmed transpile/decompile
  - [ ] Test: All fixed parameters
  - [ ] Test: All new parameters

- [ ] Create regression tests
  - [ ] Test existing functionality still works
  - [ ] Test timer() and whenChanged() unaffected
  - [ ] Test other API definitions unaffected

### Run Test Suite

- [ ] Run unit tests
  - [ ] All operand validation tests pass
  - [ ] All round-trip tests pass
  - [ ] All regression tests pass
  - [ ] Fix any failures

- [ ] Run integration tests
  - [ ] Test full transpile pipeline
  - [ ] Test decompiler
  - [ ] Test with real INAV logic conditions
  - [ ] Verify correct operand values in output

### Manual Testing

- [ ] Test on SITL
  - [ ] Load test script with fixed parameters
  - [ ] Verify logic conditions work correctly
  - [ ] Test each repaired parameter
  - [ ] Test new parameters

- [ ] Test round-trip scenarios
  - [ ] Write JS → transpile → decompile → verify
  - [ ] Test complex logic conditions
  - [ ] Verify parameter names preserved correctly

- [ ] Test edge cases
  - [ ] Test with all operand types
  - [ ] Test boundary values
  - [ ] Test error conditions

## Phase 5: Documentation

### Update Code Documentation

- [ ] Add comments to flight.js
  - [ ] Document why constants are used
  - [ ] Note relationship to inav_constants.js
  - [ ] Warn against hardcoding values

- [ ] Update API definition docs
  - [ ] Document new parameters
  - [ ] Update operand value references
  - [ ] Add validation process documentation

- [ ] Add inline comments for each parameter
  - [ ] Document purpose
  - [ ] Document valid ranges
  - [ ] Document units

### Create Migration Guide

- [ ] Document breaking changes
  - [ ] List affected parameters
  - [ ] Show old vs new behavior
  - [ ] Provide examples

- [ ] Create migration checklist for users
  - [ ] How to test existing scripts
  - [ ] What to look for
  - [ ] How to fix issues

### Update Test Documentation

- [ ] Document validation tests
  - [ ] How to run them
  - [ ] What they check
  - [ ] How to add new tests

- [ ] Document testing procedures
  - [ ] Manual test steps
  - [ ] Required hardware
  - [ ] Expected results

## Phase 6: Code Review & PR

### Prepare for Review

- [ ] Self-review all changes
  - [ ] Check code style consistency
  - [ ] Verify no debug code left
  - [ ] Ensure all TODOs addressed
  - [ ] Verify comments are clear

- [ ] Run final test sweep
  - [ ] All automated tests pass
  - [ ] Manual tests completed
  - [ ] No regressions found

- [ ] Create comprehensive changeset summary
  - [ ] List all files changed
  - [ ] Summarize changes
  - [ ] Document testing performed

### Create Pull Request

- [ ] Write detailed PR description
  - [ ] Describe the critical bug
  - [ ] Explain root cause
  - [ ] Show fix approach
  - [ ] List all changes
  - [ ] Include test results

- [ ] Add supporting materials
  - [ ] Link to audit report
  - [ ] Include before/after examples
  - [ ] Show test output
  - [ ] Add migration guide

- [ ] Link related items
  - [ ] Reference audit report issue
  - [ ] Link to documentation PR (complementary)
  - [ ] Tag as critical bug fix

### Address Review Feedback

- [ ] Respond to review comments
- [ ] Make requested changes
- [ ] Re-run tests after changes
- [ ] Update PR description if needed

### Merge

- [ ] Get required approvals
- [ ] Final test run
- [ ] Merge to main branch
- [ ] Tag release if appropriate

## Notes

- **CRITICAL:** This is a data corruption bug - prioritize over other work
- Coordinate with firmware team if operand values are unclear
- Consider notifying users about the fix (breaking change)
- May want to add runtime warnings for common migration issues
- Keep documentation PR separate to avoid confusion
