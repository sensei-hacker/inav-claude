# Task Assignment: Investigate ESC Motor Spinup After Disarm

**Date:** 2025-12-29 12:25
**Project:** investigate-esc-spinup-after-disarm
**Priority:** HIGH
**Estimated Effort:** 4-6 hours
**Type:** Bug Investigation / Safety Issue

## Task

Investigate why ESCs spin up motors several seconds after disarm, and implement a fix if the root cause is EEPROM blocking.

## Problem

**Issue #10913:** https://github.com/iNavFlight/inav/issues/10913

**Symptoms:**
- Motors spin up several seconds after disarm
- Unexpected and dangerous behavior
- May be related to EEPROM save operations

**Context from Issue #9441:** https://github.com/iNavFlight/inav/issues/9441

**Pawel's explanation:**
> "The problem is that save to EEPROM is a blocking and long taking operation. FC will not generate valid DSHOT (or any) ESC frames and ESC reboot as it's the safest thing they could make."

**Hypothesis:**
When EEPROM save blocks, FC stops generating DSHOT frames → ESC interprets this as signal loss → ESC reboots → ESC might spin motors during reboot sequence.

## What to Do

### 1. Read and Analyze GitHub Issues

**Issue #10913:**
- Read complete issue description
- Note all symptoms reported
- Check for video/log evidence
- Note ESC type, protocol (DSHOT, OneShot, etc.)
- Note when spinup occurs (how many seconds after disarm?)
- Note what triggers it (disarm command, timeout, etc.)

**Issue #9441:**
- Read Pawel's full explanation
- Understand EEPROM blocking behavior
- Note any workarounds mentioned
- Check if issue was closed/fixed

**Related issues:**
Search for similar reports:
```bash
gh issue list --repo iNavFlight/inav --search "motor spin disarm" --state all
gh issue list --repo iNavFlight/inav --search "ESC reboot" --state all
gh issue list --repo iNavFlight/inav --search "EEPROM blocking" --state all
```

### 2. Investigate EEPROM Save Timing

**When does EEPROM save occur?**

Find EEPROM save operations:
```bash
cd inav
grep -r "saveEEPROM" src/
grep -r "writeEEPROM" src/
grep -r "config_streamer" src/
grep -r "saveConfigAndNotify" src/
```

**Key questions:**
- Does EEPROM save happen on disarm?
- What triggers EEPROM save?
- How long does EEPROM save take?
- Is it truly blocking (no interrupts)?
- What happens to motor outputs during save?

**Check for:**
- Stats saving on disarm
- Configuration auto-save
- Flight log statistics
- Blackbox finalization

### 3. Investigate Motor Output During EEPROM Save

**Find motor output code:**
```bash
grep -r "writeMotor" src/
grep -r "pwmWriteMotor" src/
grep -r "DSHOT" src/
grep -r "mixerUpdateStateFlags" src/
```

**Key questions:**
- What happens to motor outputs during EEPROM save?
- Are motors explicitly set to disarmed values?
- Does DSHOT signal stop during blocking operation?
- Are output pins held in a known state?

**Check files:**
- `src/main/flight/mixer.c` - Motor mixing and output
- `src/main/drivers/pwm_output.c` - PWM/DSHOT output
- `src/main/io/config_streamer.c` - EEPROM operations
- `src/main/fc/fc_core.c` - Main loop and timing

### 4. Look for Other Causes

**Beyond EEPROM, investigate:**

1. **Disarm sequence timing:**
   - Is there a delay between disarm command and motor stop?
   - Does arming state affect output immediately?

2. **ESC protocol edge cases:**
   - DSHOT special commands sent on disarm?
   - ESC telemetry interactions?
   - Bidirectional DSHOT behavior?

3. **Interrupt/timing issues:**
   - High-priority interrupts blocking motor updates?
   - Scheduler issues?
   - Task priorities?

4. **ESC-specific behavior:**
   - Some ESCs might spin motors on signal loss
   - ESC firmware behavior on reboot
   - ESC startup/calibration sequences

5. **Configuration issues:**
   - Motor idle settings
   - Min throttle settings
   - ESC protocol settings

### 5. Reproduce and Test

**If you have hardware:**
```bash
# Build firmware with debug logging
cd inav
make YUPIF7  # or your target

# Add debug logging around:
# - EEPROM save start/end
# - Motor output values
# - Disarm sequence
```

**Test scenarios:**
1. Disarm via switch
2. Disarm via timeout
3. Disarm after flight (with stats save)
4. Disarm without flight (no stats)
5. Different ESC protocols (DSHOT, OneShot, etc.)

**Monitor:**
- When does spinup occur?
- How long after disarm?
- What else is happening at that time?
- Check EEPROM save timing correlation

### 6. Proposed Solution (If EEPROM Blocking Confirmed)

**If EEPROM save is the cause, implement fix:**

**Option A: Hold motor pins low during EEPROM save**

```c
// Before EEPROM save
void prepareForEEPROMSave(void) {
    // Ensure all motors are stopped
    mixerDisarm();

    // Force all motor output pins LOW
    for (int i = 0; i < getMotorCount(); i++) {
        pwmWriteMotor(i, PWM_RANGE_ZERO);  // or appropriate zero value

        // If DSHOT, send explicit stop command
        #ifdef USE_DSHOT
        dshotCommandWrite(i, DSHOT_CMD_MOTOR_STOP, false);
        #endif
    }

    // Small delay to ensure outputs are stable
    delay(10);
}

// Call before EEPROM save
prepareForEEPROMSave();
saveEEPROM();
```

**Option B: Make EEPROM save non-blocking**
- Move EEPROM save to background task
- Use interrupt-driven write
- Split into smaller chunks
- More complex, but better long-term solution

**Option C: Defer EEPROM save**
- Don't save immediately on disarm
- Save after a delay (5-10 seconds)
- Ensure motors are truly stopped first
- Risk: Stats might be lost if FC powered off

**Recommendation:** Start with Option A (safest, simplest) if EEPROM is confirmed cause.

### 7. Code Analysis - Key Areas

**Disarm sequence:** `src/main/fc/fc_core.c`
```c
// Find where ARMED state changes to DISARMED
// Check if EEPROM save happens in same code path
```

**EEPROM save:** `src/main/io/config_streamer.c`
```c
// Understand blocking behavior
// Check if interrupts are disabled
// Measure typical save duration
```

**Motor output:** `src/main/flight/mixer.c`
```c
// Find how disarmed state affects motor output
// Check if outputs are explicitly zeroed
// Verify output pin states during disarm
```

**DSHOT output:** `src/main/drivers/dshot.c` or `src/main/drivers/pwm_output_dshot.c`
```c
// Check DSHOT frame generation during blocking operations
// Look for special disarm commands
// Verify signal continuity requirements
```

### 8. Report Findings

**Create detailed report:**

File: `claude/developer/reports/issue-10913-esc-spinup-investigation.md`

**Include:**
1. **Root cause analysis:**
   - Is it EEPROM blocking?
   - Any other contributing factors?
   - Timing analysis

2. **Code locations:**
   - Where EEPROM save happens
   - Where motor outputs are controlled
   - Critical code paths

3. **Reproduction steps:**
   - How to reproduce reliably
   - Required conditions

4. **Proposed fix:**
   - Which option (A, B, or C)
   - Code changes needed
   - Testing approach

5. **Safety considerations:**
   - Why this is dangerous
   - How fix prevents spinup
   - Any edge cases

## Success Criteria

- [ ] Issue #10913 thoroughly analyzed
- [ ] Issue #9441 context understood
- [ ] EEPROM save code located and analyzed
- [ ] Motor output code during disarm analyzed
- [ ] Other potential causes investigated
- [ ] Root cause identified (or multiple causes)
- [ ] Reproduction steps documented
- [ ] Fix proposed with code changes
- [ ] Safety impact assessed
- [ ] Comprehensive report created
- [ ] Completion report sent to manager

## Important Notes

**SAFETY CRITICAL:**
Motors spinning up unexpectedly after disarm is extremely dangerous. This could cause injury if someone is near the aircraft.

**Priority is HIGH** because of safety implications.

**Expected findings:**
Based on Pawel's comment, EEPROM blocking is likely the root cause. However, verify there are no other contributing factors.

**Testing:**
If you have hardware, reproduce the issue. If not, analyze code thoroughly and document assumptions.

**Backwards compatibility:**
Any fix should work across all ESC protocols (DSHOT, OneShot, Multishot, PWM) and all targets.

**Related work:**
Check if any recent changes addressed this (recent PRs, commits).

**ESC behavior:**
Different ESCs handle signal loss differently:
- Some stop motors immediately
- Some enter a timeout/recovery mode
- Some spin motors during startup sequence
- Understanding ESC behavior is important

**Community input:**
If needed, ask on issue #10913 for:
- ESC type and firmware
- Exact timing (seconds after disarm)
- Flight mode at disarm
- Whether stats saving is enabled

---
**Manager**
