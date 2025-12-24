# Project: Fix CLI "Invalid name" Error for align_mag_roll

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix / CLI
**Created:** 2025-12-02
**Estimated Time:** 2-4 hours

---

## Overview

Fix CLI bug where `set align_mag_roll = <value>` returns "Invalid name" error, preventing users from configuring external magnetometer alignment.

---

## Problem

**User-reported issue:**
- Command: `set align_mag_roll = 900`
- Error: "Invalid name"
- Prevents external mag configuration
- Unknown if related to "erase all" during flashing

**Impact:**
- Users cannot configure external magnetometer alignment
- Affects navigation accuracy (compass alignment critical)
- May affect align_mag_pitch and align_mag_yaw as well

---

## Root Cause (Hypothesis)

**Likely causes:**
1. **Conditional compilation:** `USE_MAG` not defined for target → setting excluded
2. **Settings generation:** Field name mismatch in compassConfig_t struct
3. **CLI parsing:** Spaces around `=` not handled correctly
4. **EEPROM initialization:** PG_COMPASS_CONFIG not registered properly

**Most likely:** Conditional compilation issue where `USE_MAG` is not defined for the affected target, excluding the entire `PG_COMPASS_CONFIG` group from the settings table.

---

## Investigation Plan

### Phase 1: Reproduce (30-60 min)
1. Identify affected target
2. Test with SITL or actual hardware
3. Confirm error occurs
4. Test related settings (align_mag_pitch, align_mag_yaw)

### Phase 2: Root Cause Analysis (30-60 min)
1. Check `USE_MAG` definition for target
2. Verify setting exists in settings_generated.c
3. Check compassConfig_t struct definition
4. Test CLI parsing with/without spaces

### Phase 3: Fix (30-90 min)
1. Apply appropriate fix based on root cause
2. Rebuild firmware
3. Test on SITL or hardware
4. Verify all three align_mag_* settings work

### Phase 4: Testing (30-60 min)
1. Test save/load persistence
2. Test after "erase all"
3. Test on multiple targets if needed
4. Verify no regression on other settings

---

## Objectives

1. Identify root cause of "Invalid name" error
2. Fix CLI command `set align_mag_roll = <value>`
3. Ensure setting persists across reboots
4. Verify all three align_mag_* settings work
5. No regression on other CLI settings

---

## Scope

**In Scope:**
- Fix align_mag_roll CLI error
- Fix align_mag_pitch and align_mag_yaw (same issue)
- Test on affected target(s)
- Verify EEPROM persistence

**Out of Scope:**
- Refactoring entire CLI system
- Changes to other compass settings (unless related)
- Configurator GUI changes
- Documentation updates (can be separate task)

---

## Files to Investigate

**Primary:**
- `inav/src/main/fc/cli.c` (CLI parsing, error message)
- `inav/src/main/fc/settings.yaml` (setting definitions)
- `inav/src/main/fc/settings.c` (setting lookup)

**Secondary:**
- `inav/src/main/sensors/compass.h` (compassConfig_t struct)
- `inav/src/main/target/common_defaults.h` (USE_MAG definition)
- `inav/src/main/target/<TARGET>/target.h` (target-specific defines)

**Generated (verify after rebuild):**
- `inav/src/main/fc/settings_generated.c`
- `inav/src/main/fc/settings_generated.h`

---

## Success Criteria

- [ ] Root cause identified and documented
- [ ] `set align_mag_roll = 900` works successfully
- [ ] `set align_mag_pitch = 450` works successfully
- [ ] `set align_mag_yaw = 1800` works successfully
- [ ] Settings persist after save/reboot
- [ ] Works after "erase all" + "defaults set"
- [ ] No regression on other CLI settings
- [ ] Testing complete on affected target(s)

---

## Priority Justification

**HIGH priority because:**
- **User-facing bug:** Prevents critical configuration
- **Navigation safety:** Incorrect mag alignment causes navigation errors
- **CLI reliability:** Core functionality should work
- **Potentially widespread:** May affect multiple targets

---

## Estimated Time

**2-4 hours total:**
- Reproduce: 30-60 min
- Root cause: 30-60 min
- Fix: 30-90 min
- Testing: 30-60 min

**Risk:** MEDIUM (needs hardware testing or SITL verification)

---

## Assignment

**Assigned to:** Developer
**Assignment email:** `claude/manager/sent/2025-12-02-2200-task-cli-align-mag-roll-invalid-name.md`
**Branch:** From master
