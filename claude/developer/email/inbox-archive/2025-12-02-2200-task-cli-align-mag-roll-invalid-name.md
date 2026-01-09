# Task Assignment: Fix CLI "Invalid name" Error for align_mag_roll

**Date:** 2025-12-02 22:00
**To:** Developer
**From:** Manager
**Project:** New (standalone bug fix)
**Priority:** HIGH
**Estimated Effort:** 2-4 hours
**Branch:** From master

---

## Task

Investigate and fix CLI command `set align_mag_roll = <value>` which returns "Invalid name" error in some cases.

---

## Problem

**User report:**
- Command: `set align_mag_roll = 900` (or any value)
- Error: "Invalid name"
- Unknown if user did "erase all" when flashing (may not matter)

**Expected behavior:**
- Command should work successfully
- Setting should be accepted and applied

---

## Initial Investigation (Manager)

**Setting definition:** `inav/src/main/fc/settings.yaml:623-628`
```yaml
- name: align_mag_roll
  description: "Set the external mag alignment on the roll axis..."
  default_value: 0
  field: rollDeciDegrees
  min: -1800
  max: 3600
```

**Parent group:** `PG_COMPASS_CONFIG` (line 555)
- Type: `compassConfig_t`
- **Condition:** `USE_MAG` (line 558)
- Headers: `["sensors/compass.h"]`

**Hypothesis:**
The setting may be conditionally compiled out if `USE_MAG` is not defined for certain targets. The "Invalid name" error comes from `cliSet()` in `cli.c:4053` when no matching setting is found in the settings table.

---

## Investigation Steps

### Step 1: Reproduce the Issue

1. **Identify affected target:**
   - Which flight controller target is experiencing this?
   - Check if it's target-specific or affects all targets

2. **Check build configuration:**
   ```bash
   # For a specific target (e.g., MATEKF405SE)
   grep -r "USE_MAG" inav/src/main/target/<TARGET>/
   grep -r "USE_MAG" inav/src/main/target/common_defaults.h
   ```

3. **Verify setting exists in build:**
   - Build firmware for affected target
   - Check if `align_mag_roll` is in compiled settings table
   - Or use SITL to test CLI commands

### Step 2: Determine Root Cause

**Possible causes:**

**A. Conditional compilation issue:**
- Setting excluded because `USE_MAG` not defined for target
- Or `USE_MAG` defined but setting still missing from table

**B. Settings generation bug:**
- settings.yaml → settings_generated.c conversion problem
- Field name mismatch (`rollDeciDegrees` vs struct member)

**C. CLI parsing bug:**
- Spaces around `=` causing parse failure
- Name matching logic bug in `settingNameIsExactMatch()`

**D. EEPROM/defaults issue:**
- Settings not initialized properly after "erase all"
- PG (parameter group) not registered correctly

### Step 3: Test with SITL

Use SITL to test without hardware:

```bash
cd inav
make TARGET=SITL
./bin/SITL.elf

# In CLI:
get align_mag_roll     # Does this work?
set align_mag_roll = 900   # Does this fail?
set align_mag_roll=900     # Does this work (no spaces)?
```

---

## Likely Fixes (Based on Root Cause)

### If Cause A (Conditional Compilation):

**Fix:** Ensure `USE_MAG` is defined for affected targets

**File:** `inav/src/main/target/<TARGET>/target.h` or `common_defaults.h`
```c
#define USE_MAG
```

Or check if magnetometer support was intentionally disabled for this target.

### If Cause B (Settings Generation):

**Fix:** Check `compassConfig_t` struct definition

**File:** `inav/src/main/sensors/compass.h`
```c
typedef struct compassConfig_s {
    // ...
    int16_t rollDeciDegrees;   // Must match settings.yaml field name
    int16_t pitchDeciDegrees;
    int16_t yawDeciDegrees;
    // ...
} compassConfig_t;
```

Rebuild settings: `make clean && make TARGET=<target>`

### If Cause C (CLI Parsing):

**Fix:** Remove spaces around `=` in user command

**Workaround:** `set align_mag_roll=900` (no spaces)

**If this is the issue:** Investigate why spaces cause failure (they shouldn't).

**File:** `inav/src/main/fc/cli.c:3960-3973`
```c
// The parser should handle spaces around '='
eqptr = strstr(cmdline, "=");
// ... strips spaces before and after '=' ...
```

Test if this logic works correctly.

### If Cause D (EEPROM Issue):

**Fix:** Ensure PG_COMPASS_CONFIG is properly registered

**File:** `inav/src/main/sensors/compass.c` (or similar)
```c
PG_REGISTER_WITH_RESET_TEMPLATE(compassConfig_t, compassConfig, PG_COMPASS_CONFIG, ...);
```

Check if `defaults set` command in CLI works.

---

## Testing

### Minimal Test Case:

1. Connect to FC (or SITL)
2. Enter CLI mode
3. Test commands:
   ```
   get align_mag      # Should work
   get align_mag_roll # Should work or fail with clear error
   set align_mag_roll=0   # Test without spaces
   set align_mag_roll = 900  # Test with spaces
   save
   ```
4. Reboot and verify:
   ```
   get align_mag_roll # Should show 900
   ```

### Extended Testing:

1. Test all three align_mag settings:
   ```
   set align_mag_roll=900
   set align_mag_pitch=450
   set align_mag_yaw=1800
   save
   ```

2. Test after "erase all":
   ```
   # Flash firmware with "erase all"
   # Enter CLI
   defaults set
   set align_mag_roll=900
   save
   ```

3. Test on multiple targets (if target-specific)

---

## Files to Check

### Primary investigation:
- `inav/src/main/fc/cli.c` (line 3940+: `cliSet()`, line 4053: error message)
- `inav/src/main/fc/settings.yaml` (line 623-640: align_mag_* definitions)
- `inav/src/main/fc/settings.c` (line 108-112: `settingNameIsExactMatch()`)

### Secondary (conditional compilation):
- `inav/src/main/sensors/compass.h` (compassConfig_t struct definition)
- `inav/src/main/target/common_defaults.h` (USE_MAG definition)
- `inav/src/main/target/<AFFECTED_TARGET>/target.h`

### Generated (check after rebuild):
- `inav/src/main/fc/settings_generated.c` (auto-generated from settings.yaml)
- `inav/src/main/fc/settings_generated.h`

---

## Success Criteria

- [ ] Root cause identified
- [ ] CLI command `set align_mag_roll = 900` works successfully
- [ ] Setting persists across reboots (after `save`)
- [ ] All three align_mag_* settings work (roll, pitch, yaw)
- [ ] Works regardless of "erase all" during flashing
- [ ] Works on affected target(s)
- [ ] No regression on other settings

---

## User Communication

Once fixed, we should:
1. Identify which targets are affected
2. Determine if this is a regression (did it ever work?)
3. Consider if this affects other magnetometer-related settings
4. Document any workarounds for users on older firmware

---

## Priority Justification

**HIGH priority because:**
- **User-facing bug:** Prevents users from configuring external magnetometer
- **Navigation impact:** Incorrect mag alignment causes navigation errors
- **May affect multiple targets:** Could be widespread issue
- **CLI reliability:** Core CLI functionality should work consistently

---

## Additional Context

**Related settings (same parent group):**
- `align_mag` - Board magnetometer alignment (works?)
- `align_mag_pitch` - External mag pitch (likely same issue)
- `align_mag_yaw` - External mag yaw (likely same issue)
- `mag_hardware` - Mag hardware selection
- `mag_declination` - Magnetic declination

**If one fails, others in same group might fail too.**

---

## Questions for Investigation

1. **Which target is affected?** (user should provide)
2. **Does `get align_mag_roll` work?** (read vs write issue)
3. **Do other mag settings work?** (e.g., `set mag_declination=100`)
4. **Does `defaults set` fix it?** (EEPROM corruption)
5. **Is USE_MAG defined for this target?** (compile-time check)

---

## Reporting Back

When sending completion report, include:
1. Root cause explanation
2. Which targets were affected
3. The fix applied
4. Testing results (before/after)
5. Any workarounds for users on old firmware
6. Whether this requires a PR to upstream INAV

---

**Manager**
2025-12-02 22:00
