# Todo List: Fix CLI align_mag_roll "Invalid name" Error

## Phase 1: Reproduce Issue

- [ ] Get affected target information from user
  - [ ] Target name (e.g., MATEKF405SE)
  - [ ] Firmware version
  - [ ] Whether "erase all" was used
- [ ] Set up test environment (SITL or hardware)
- [ ] Reproduce the error
  - [ ] Test: `get align_mag_roll`
  - [ ] Test: `set align_mag_roll=900` (no spaces)
  - [ ] Test: `set align_mag_roll = 900` (with spaces)
- [ ] Test related settings
  - [ ] `get align_mag` (board mag)
  - [ ] `set align_mag_pitch = 450`
  - [ ] `set align_mag_yaw = 1800`
  - [ ] `set mag_declination = 100`

## Phase 2: Root Cause Analysis

- [ ] Check conditional compilation
  - [ ] Verify `USE_MAG` defined for target
  - [ ] Check `inav/src/main/target/<TARGET>/target.h`
  - [ ] Check `inav/src/main/target/common_defaults.h`
- [ ] Verify setting in generated code
  - [ ] Build firmware for target
  - [ ] Check `settings_generated.c` for align_mag_roll
  - [ ] Verify setting index in table
- [ ] Check struct definition
  - [ ] Examine `compassConfig_t` in `compass.h`
  - [ ] Verify field names match settings.yaml
  - [ ] Check `rollDeciDegrees`, `pitchDeciDegrees`, `yawDeciDegrees`
- [ ] Test CLI parsing
  - [ ] Debug `settingNameIsExactMatch()` function
  - [ ] Test with different spacing variations
  - [ ] Check if spaces around `=` are stripped correctly
- [ ] Document root cause findings

## Phase 3: Implement Fix

### If Cause: USE_MAG not defined
- [ ] Add `#define USE_MAG` to target.h
- [ ] Or check why it was excluded
- [ ] Rebuild firmware

### If Cause: Settings generation issue
- [ ] Fix field name in settings.yaml or struct
- [ ] Rebuild settings: `make clean && make`
- [ ] Verify in settings_generated.c

### If Cause: CLI parsing bug
- [ ] Fix space handling in `cliSet()`
- [ ] Test edge cases
- [ ] Rebuild firmware

### If Cause: EEPROM/PG registration
- [ ] Verify PG_REGISTER_WITH_RESET_TEMPLATE
- [ ] Check compass.c initialization
- [ ] Test with `defaults set`

## Phase 4: Testing

- [ ] Functional testing
  - [ ] `set align_mag_roll = 900` works
  - [ ] `set align_mag_pitch = 450` works
  - [ ] `set align_mag_yaw = 1800` works
  - [ ] Values persist after `save`
- [ ] Reboot testing
  - [ ] Save settings
  - [ ] Reboot FC
  - [ ] Verify values with `get align_mag_*`
- [ ] "Erase all" testing
  - [ ] Flash with "erase all"
  - [ ] `defaults set`
  - [ ] Set align_mag values
  - [ ] Verify they work
- [ ] Regression testing
  - [ ] Test other mag settings work
  - [ ] Test unrelated CLI settings work
  - [ ] Verify `get` commands work

## Phase 5: Documentation & PR

- [ ] Document root cause
- [ ] Document fix applied
- [ ] List affected targets (if target-specific)
- [ ] Test results summary
- [ ] Create branch and commit
- [ ] Send completion report to manager
- [ ] Create PR if appropriate

## Notes

- Priority: HIGH (user-facing navigation bug)
- Estimated time: 2-4 hours
- May affect all three align_mag_* settings
- Could be target-specific or firmware-wide
