# Project: Investigate ESC Motor Spinup After Disarm

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Investigation / Safety Issue
**Created:** 2025-12-29
**Estimated Effort:** 4-6 hours
**GitHub Issue:** [#10913](https://github.com/iNavFlight/inav/issues/10913)
**Branch: test-dma-during-flash-erase**

## Overview

Investigate and fix dangerous behavior where motors spin up several seconds after disarm, likely caused by EEPROM blocking preventing valid DSHOT signal generation.

## Problem

**SAFETY CRITICAL:** Motors spinning up unexpectedly after disarm is extremely dangerous and could cause injury.

**User Report (Issue #10913):**
- Motors spin up several seconds after disarm
- Unexpected and dangerous behavior

**Context from Issue #9441:**
Pawel explained that EEPROM save is a blocking operation that prevents FC from generating valid DSHOT/ESC frames, causing ESCs to reboot as a safety measure.

**Likely cause:**
1. User disarms aircraft
2. EEPROM save triggered (stats, config, etc.)
3. EEPROM save blocks for ~1-2 seconds
4. FC cannot generate valid DSHOT frames during block
5. ESC interprets missing signal as failure
6. ESC reboots as safety measure
7. **ESC spins motors during reboot/startup sequence**

## Objectives

1. Read and fully understand Issues #10913 and #9441
2. Locate EEPROM save operations that happen on/after disarm
3. Analyze motor output behavior during EEPROM blocking
4. Investigate other potential causes beyond EEPROM
5. Propose and implement fix (likely: hold motor pins low during save)
6. Create comprehensive investigation report

## Scope

**In Scope:**
- Issue analysis and research
- EEPROM save timing investigation
- Motor output code during disarm
- DSHOT signal generation during blocking
- Root cause identification
- Proposed fix implementation
- Safety analysis
- Comprehensive report

**Out of Scope:**
- Complete EEPROM rewrite (too complex for this issue)
- ESC firmware changes
- Hardware modifications

## Expected Root Cause

Based on Pawel's comment and issue description, likely:
- EEPROM save blocks CPU
- DSHOT signal stops
- ESC reboots
- Motor spinup during ESC reboot

## Proposed Solution

**If EEPROM blocking confirmed:**

**Option A (Preferred):** Hold motor output pins LOW during EEPROM save
- Simple, safe, effective
- Ensures pins are in known state
- Works across all ESC protocols

**Option B:** Make EEPROM save non-blocking
- More complex
- Better long-term solution
- Requires significant refactoring

**Option C:** Defer EEPROM save
- Save after delay (5-10 seconds)
- Simpler but less robust
- Risk of data loss if powered off

**Recommendation:** Start with Option A (safest, quickest).

## Code Areas to Investigate

**Key files:**
- `src/main/io/config_streamer.c` - EEPROM operations
- `src/main/fc/fc_core.c` - Main loop, disarm sequence
- `src/main/flight/mixer.c` - Motor output control
- `src/main/drivers/pwm_output.c` - PWM/DSHOT output
- `src/main/drivers/dshot.c` - DSHOT protocol

**Key functions:**
- EEPROM save triggers on disarm
- Motor output during disarmed state
- DSHOT frame generation
- Pin state management

## Success Criteria

- [ ] Issues #10913 and #9441 fully analyzed
- [ ] EEPROM save timing understood
- [ ] Motor output during save analyzed
- [ ] Other causes ruled out or identified
- [ ] Root cause confirmed
- [ ] Fix implemented (if EEPROM is cause)
- [ ] Safety analysis documented
- [ ] Testing approach defined
- [ ] Comprehensive report created

## Safety Considerations

**Why this is critical:**
- Motors spinning after disarm is unexpected
- User may be near aircraft assuming it's safe
- Could cause serious injury
- Violates user expectations of disarm behavior

**Fix requirements:**
- Must prevent any motor spinup after disarm
- Must work across all ESC protocols
- Must not introduce new failure modes
- Must be thoroughly tested

## Priority Justification

HIGH priority because:
- **Safety critical** - risk of injury
- User-reported real-world issue
- Affects all DSHOT users (potentially)
- Based on known EEPROM blocking issue
- Clear path to fix (if confirmed)
- Must be fixed before next release

## Testing Requirements

**If hardware available:**
- Reproduce issue reliably
- Test fix across ESC protocols
- Verify motor pins stay low during save
- Test edge cases

**If no hardware:**
- Thorough code analysis
- Timing analysis
- Document assumptions
- Request community testing

## Expected Deliverables

1. **Investigation Report:** `claude/developer/reports/issue-10913-esc-spinup-investigation.md`
   - Root cause analysis
   - Code analysis
   - Timing analysis
   - Proposed fix with code
   - Testing approach
   - Safety considerations

2. **Code Implementation:**
   - Fix for confirmed root cause
   - Works across all ESC protocols
   - Properly tested

3. **PR (if fix implemented):**
   - Clear description of problem and fix
   - Reference to issues #10913 and #9441
   - Testing evidence

## Related Issues

- Issue #10913 (primary)
- Issue #9441 (EEPROM blocking context)
- Search for related motor/ESC/disarm issues

## Notes

**Community input:**
If needed, ask on issue #10913 for:
- ESC type and firmware version
- Exact timing (how many seconds?)
- Flight mode at disarm
- Statistics saving enabled?
- DSHOT protocol version

**ESC behavior varies:**
Different ESC firmware handles signal loss differently. Understanding the specific ESC behavior is important.

**Backwards compatibility:**
Any fix must work across:
- All ESC protocols (DSHOT, OneShot, Multishot, PWM)
- All hardware targets
- All ESC types

**Quick win potential:**
If EEPROM is confirmed cause, Option A fix is straightforward and could be implemented quickly.
