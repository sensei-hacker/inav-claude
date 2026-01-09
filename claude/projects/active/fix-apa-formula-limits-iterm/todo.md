# Todo List: Fix APA Formula - Limits, I-term, Default

## Preparation (15 minutes)

- [ ] Read analysis document
  - [ ] Open `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`
  - [ ] Read "Issue 2: I-Term Scaling" section
  - [ ] Read "Issue 4: Asymmetric Limits" section
  - [ ] Understand rationale for each change
  - [ ] Note control theory explanation

- [ ] Locate code
  - [ ] Find APA implementation in `src/main/flight/pid.c`
  - [ ] Search for "apa_pow" to find the formula
  - [ ] Identify exact lines to modify (around line 448)
  - [ ] Note current implementation

- [ ] Locate settings
  - [ ] Find apa_pow in `src/main/fc/settings.yaml`
  - [ ] Note current default value (120)
  - [ ] Note current description

## Implementation (45 minutes)

### Change 1: Update Limits

- [ ] Open `src/main/flight/pid.c`
  - [ ] Find the tpaFactor constraint line
  - [ ] Current: `constrainf(tpaFactor, 0.3f, 2.0f)`
  - [ ] Change to: `constrainf(tpaFactor, 0.5f, 1.5f)`
  - [ ] Add comment explaining change
  - [ ] Reference GitHub issue #11208

- [ ] Verify change
  - [ ] Check syntax is correct
  - [ ] Ensure 0.5f and 1.5f (not 0.5, 1.5)
  - [ ] Comment is clear

### Change 2: Remove I-term Scaling

- [ ] Find I-term scaling code
  - [ ] Locate the lines that scale PIFF
  - [ ] Identify the I-term scaling line
  - [ ] Should be: `pidState[axis].I *= tpaFactor;`

- [ ] Comment out I-term scaling
  - [ ] Change to: `// pidState[axis].I *= tpaFactor;  // Removed`
  - [ ] Add explanatory comment above
  - [ ] Explain control theory rationale
  - [ ] Reference GitHub issue #11208

- [ ] Add detailed comment
  ```c
  // Note: I-term is NOT scaled with airspeed
  // Rationale: I-term compensates for steady-state error and should remain
  // constant across the flight envelope. Scaling I causes windup at low
  // speeds and overshoot at high speeds. Only P/D/FF need aerodynamic scaling.
  // See GitHub issue #11208 for detailed control theory analysis.
  ```

- [ ] Verify P/D/FF still scaled
  - [ ] Check P scaling line still active
  - [ ] Check D scaling line still active
  - [ ] Check FF scaling line still active
  - [ ] Only I-term should be commented out

### Change 3: Set Default to 0

- [ ] Open `src/main/fc/settings.yaml`
  - [ ] Search for "apa_pow"
  - [ ] Find the setting definition
  - [ ] Note current default_value: 120

- [ ] Change default value
  - [ ] Change `default_value: 120` to `default_value: 0`
  - [ ] Verify syntax (YAML format)

- [ ] Update description
  - [ ] Old: Brief description
  - [ ] New: "Fixed Wing APA (Airspeed-based PID Attenuation) power curve. 0=disabled (default), 120=recommended if enabled. Requires validated pitot sensor. Higher values = more aggressive scaling. Range [0-200]"
  - [ ] Clear that 0 = disabled
  - [ ] Clear that 120 = recommended active value
  - [ ] Mention pitot sensor requirement

- [ ] Verify YAML syntax
  - [ ] Proper indentation
  - [ ] Quotes if needed
  - [ ] No syntax errors

## Testing (45 minutes)

### Build Testing

- [ ] Build firmware
  - [ ] Choose test target: `./build.sh MATEKF405`
  - [ ] Verify compilation succeeds
  - [ ] No warnings related to changes
  - [ ] Build second target to verify

### SITL Testing - Scenario 1: Disabled (Default)

- [ ] Launch SITL with default settings
  - [ ] apa_pow should be 0
  - [ ] Load firmware in configurator
  - [ ] Verify apa_pow = 0 in CLI

- [ ] Test flight
  - [ ] Fly at various airspeeds
  - [ ] Expected: No gain scaling
  - [ ] Aircraft flies normally
  - [ ] Verify gains constant regardless of airspeed

### SITL Testing - Scenario 2: Enabled

- [ ] Enable APA
  - [ ] Set apa_pow = 120
  - [ ] Save and reboot

- [ ] Test flight with APA enabled
  - [ ] Fly at cruise speed (85 km/h)
  - [ ] Expected: tpaFactor = 1.0
  - [ ] Fly slow (56.7 km/h = 0.67×cruise)
  - [ ] Expected: tpaFactor = 1.5 (not 2.0)
  - [ ] Fly fast (127.5 km/h = 1.5×cruise)
  - [ ] Expected: tpaFactor = 0.5 (not 0.3)

- [ ] Verify I-term not scaled
  - [ ] Add debug logging: `DEBUG_SET(DEBUG_PID, 0, pidState[FD_PITCH].I);`
  - [ ] Fly at different airspeeds
  - [ ] Expected: I-term value constant
  - [ ] P/D/FF should vary with airspeed

### Mathematical Verification

- [ ] Calculate expected values
  - [ ] apa_pow = 120, cruise = 85 km/h
  - [ ] At 85 km/h: tpaFactor = (85/85)^1.2 = 1.0 ✓
  - [ ] At 56.7 km/h: tpaFactor = (85/56.7)^1.2 = 1.5 ✓
  - [ ] At 127.5 km/h: tpaFactor = (85/127.5)^1.2 = 0.5 ✓

- [ ] Compare to old limits
  - [ ] Old limits [0.3, 2.0]: range 0.45×cruise to 2.73×cruise
  - [ ] New limits [0.5, 1.5]: range 0.67×cruise to 1.5×cruise
  - [ ] Verify new range is narrower and safer

## Documentation (30 minutes)

- [ ] Update documentation
  - [ ] Find appropriate docs file (Tuning.md or Sensors.md)
  - [ ] Document that APA is disabled by default
  - [ ] Explain how to enable: set apa_pow = 120
  - [ ] Explain pitot sensor requirement
  - [ ] Document changes from INAV 9.0

- [ ] Add release notes content
  ```markdown
  IMPORTANT: Fixed Wing APA now disabled by default (apa_pow = 0)

  To enable APA with improved formula:
  1. Verify pitot sensor is working and validated
  2. Set: apa_pow = 120
  3. Test carefully before flight

  Changes in INAV 9.1:
  - APA scaling limits changed from [0.3, 2.0] to [0.5, 1.5] (safer)
  - I-term no longer scaled with airspeed (better control)
  - Default disabled for safety (opt-in feature)
  ```

- [ ] Update CLI help text (if needed)
  - [ ] Check if apa_pow has help text
  - [ ] Update to mention 0=disabled, 120=active

## Pull Request (15 minutes)

- [ ] Create commit
  - [ ] Stage changes: `git add pid.c settings.yaml docs/...`
  - [ ] Write commit message:
    ```
    Fix APA formula: safer limits, remove I-term scaling, disable by default

    - Change limits from [0.3, 2.0] to [0.5, 1.5] (safer, symmetric)
    - Don't scale I-term (fixes windup/overshoot control theory issue)
    - Set apa_pow default to 0 (disabled, opt-in for safety)

    Rationale:
    - Symmetric limits [0.5, 1.5] are more physically justified
    - I-term should not scale with airspeed (steady-state compensation)
    - Feature requires working pitot sensor, should be opt-in

    To enable: set apa_pow = 120

    Fixes #11208

    Reference: claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md
    ```

- [ ] Create pull request
  - [ ] Reference GitHub issue #11208
  - [ ] Reference analysis document
  - [ ] Explain all three changes
  - [ ] Include test results
  - [ ] Note migration impact (users must re-enable)

## Completion Report

- [ ] Report to manager
  - [ ] Summary of three changes
  - [ ] Test results
  - [ ] User impact notes (need to re-enable)
  - [ ] PR link

- [ ] Archive project notes
  - [ ] Move to archive if needed
  - [ ] Clean up working files

## Success Checklist

- [ ] Limits changed to [0.5, 1.5]
- [ ] I-term scaling removed (commented out)
- [ ] P/D/FF still scaled
- [ ] apa_pow default set to 0
- [ ] Description updated
- [ ] Code compiles successfully
- [ ] SITL tests pass (disabled and enabled scenarios)
- [ ] I-term verified not scaling
- [ ] Mathematical verification correct
- [ ] Documentation updated
- [ ] Release notes drafted
- [ ] Pull request created
- [ ] Manager notified

## Notes

**Simple but Important:**
- Only 3 lines of code changed
- Significant safety improvement
- Better control characteristics
- Users must consciously opt-in

**Migration Impact:**
- Existing users will have APA disabled after upgrade
- Intentional for safety
- Users must manually re-enable with apa_pow = 120
- Document this clearly in release notes
