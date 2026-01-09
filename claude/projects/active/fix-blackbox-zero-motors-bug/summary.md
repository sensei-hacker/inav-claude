# Project: Fix Blackbox Zero Motors Bug

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Bug Fix
**Created:** 2025-12-29
**Estimated Effort:** 1-2 hours
**Milestone:** 9.1
**Documentation:** `claude/developer/scripts/testing/inav/gps/MOTORS_CONDITION_BUG.md`

## Overview

Fix blackbox logging bug causing catastrophic decoder failures on aircraft with zero motors (fixed-wing with servos only).

## Problem

**Bug:** I-frame motor write uses wrong condition check, writing spurious byte when motors are disabled.

**Symptoms:**
- 207 frame decode failures on fixed-wing with servos only
- Header declares 0 motor fields
- I-frame writes 1 spurious byte (0x00)
- Decoder fails catastrophically

**Root Cause:**
- Field definitions: `CONDITION(AT_LEAST_MOTORS_1)` (checks count >= 1 AND flag)
- I-frame write: `CONDITION(MOTORS)` (checks flag only)
- Inconsistent conditions → header/data mismatch

**Why it went undetected:**
- Most users have motors (multirotors)
- Rare configuration: zero motors + MOTORS flag enabled
- Affects fixed-wing with servos only

## The Fix

**Simple one-word change:**

File: `inav/src/main/blackbox/blackbox.c` line 1079

Change: `FLIGHT_LOG_FIELD_CONDITION_MOTORS` → `FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1`

**That's it!**

Optional: Same change at line 1346 for P-frame consistency (P-frame works by accident but should be consistent).

## Impact

**Who benefits:**
- Fixed-wing users with servos only (no motors)
- Default blackbox config enables MOTORS flag

**Who is unaffected:**
- Multirotor users (motorCount >= 1)
- Normal configurations

**Risk:** Very low
- Single condition change
- Matches field definition logic
- Only affects rare edge case
- Well-analyzed with test evidence

## Testing Evidence

**Platform:** JHEMCUF435 fixed-wing, motorCount=0, MOTORS flag enabled

**Before fix:**
- 207 frame decode failures
- Decoder bodge skipped 207 null bytes

**After fix:**
- 3 frame decode failures (baseline, unrelated)
- No spurious bytes

## Implementation

1. Use /git-workflow skill
2. Change one word at line 1079
3. Optional: Same change at line 1346
4. Create PR with concise description
5. Set milestone to 9.1

## Success Criteria

- [ ] Line 1079 fixed
- [ ] Optional: Line 1346 fixed
- [ ] PR created against maintenance-9.x
- [ ] Milestone set to 9.1
- [ ] Concise PR description
- [ ] Code compiles

## Priority Justification

MEDIUM priority because:
- Well-analyzed bug with clear fix
- Quick fix (1-2 hours)
- Affects rare configuration
- Low risk
- Not blocking 9.0 release
- Good candidate for 9.1 milestone

## Related

- Issue #10913 (if exists - motors after disarm, may be related)
- Blackbox logging system
- Fixed-wing configurations
