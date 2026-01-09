# Task Assignment: Fix Blackbox Zero Motors Bug

**Date:** 2025-12-29 12:30
**Project:** fix-blackbox-zero-motors-bug
**Priority:** MEDIUM
**Estimated Effort:** 1-2 hours
**Type:** Bug Fix
**Milestone:** 9.1

## Task

Fix blackbox logging bug that causes catastrophic decoder failures on aircraft with zero motors (fixed-wing with servos only).

## Problem

**Documentation:** `claude/test_tools/inav/gps/MOTORS_CONDITION_BUG.md`

**Bug Summary:**
- I-frame motor write function uses wrong condition check
- Writes 1 spurious byte when `BLACKBOX_FEATURE_MOTORS` enabled but `getMotorCount() == 0`
- Causes header/data mismatch → 207 frame decode failures

**Root Cause:**
Field definitions use `CONDITION(AT_LEAST_MOTORS_1)` (checks motor count >= 1 AND flag), but I-frame write uses `CONDITION(MOTORS)` (checks flag only).

**Result:**
- Header: 0 motor fields (correct - motorCount < 1)
- I-frame: Writes motor[0] unconditionally (wrong - 1 spurious byte)
- Decoder expects next frame marker, gets 0x00 → catastrophic failure

## The Fix

**File:** `inav/src/main/blackbox/blackbox.c`

### Required Change (Line 1079)

**Change from:**
```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_MOTORS)) {
    blackboxWriteUnsignedVB(blackboxCurrent->motor[0] - getThrottleIdleValue());

    const int motorCount = getMotorCount();
    for (int x = 1; x < motorCount; x++) {
        blackboxWriteSignedVB(blackboxCurrent->motor[x] - blackboxCurrent->motor[0]);
    }
}
```

**Change to:**
```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1)) {
    blackboxWriteUnsignedVB(blackboxCurrent->motor[0] - getThrottleIdleValue());

    const int motorCount = getMotorCount();
    for (int x = 1; x < motorCount; x++) {
        blackboxWriteSignedVB(blackboxCurrent->motor[x] - blackboxCurrent->motor[0]);
    }
}
```

**That's it!** One word changed: `MOTORS` → `AT_LEAST_MOTORS_1`

### Optional Consistency Fix (Line 1346 - P-frame)

P-frame works by accident (loop starts at 0, so 0 bytes when motorCount=0), but should be fixed for consistency:

**Change from:**
```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_MOTORS)) {
    blackboxWriteArrayUsingAveragePredictor16(offsetof(blackboxMainState_t, motor), getMotorCount());
}
```

**Change to:**
```c
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1)) {
    blackboxWriteArrayUsingAveragePredictor16(offsetof(blackboxMainState_t, motor), getMotorCount());
}
```

## What to Do

### 1. Use git-workflow Skill

**Start the workflow:**
```
/git-workflow
```

**When prompted, provide:**
- **Branch name:** `fix-blackbox-zero-motors`
- **Base branch:** `maintenance-9.x` (for 9.1 milestone)
- **Files to modify:** `src/main/blackbox/blackbox.c`

### 2. Make the Changes

**Required:**
- Line 1079: Change `FLIGHT_LOG_FIELD_CONDITION_MOTORS` to `FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1`

**Optional (for consistency):**
- Line 1346: Same change in P-frame write

### 3. Create PR with Concise Description

**PR Title:**
```
Fix blackbox motor logging for zero-motor configurations
```

**PR Description (concise):**
```markdown
## Problem
Blackbox I-frame writes motor[0] unconditionally when `BLACKBOX_FEATURE_MOTORS` is enabled, even when `getMotorCount() == 0`. This causes header/data mismatch and catastrophic decoder failures (200+ frame failures) on fixed-wing aircraft with servos only.

## Root Cause
I-frame write function uses `FLIGHT_LOG_FIELD_CONDITION_MOTORS` (flag only) instead of `FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1` (flag + motor count check), inconsistent with field definitions.

## Fix
Change I-frame condition from `MOTORS` to `AT_LEAST_MOTORS_1` to match field definition.

## Impact
- Fixes blackbox decode failures on aircraft with zero motors
- No effect on normal multirotor configurations (motorCount >= 1)
- No decoder changes needed

## Testing
Tested on JHEMCUF435 fixed-wing with servos only, motorCount=0:
- Before: 207 frame decode failures
- After: 3 frame decode failures (baseline, unrelated issue)

Fixes #10913 (if there's a related issue, otherwise remove this line)
```

### 4. Set Milestone

**In PR:**
- Set milestone to `9.1`
- Add label `bug` if available

### 5. Testing (Optional)

If you have hardware with zero motors (fixed-wing with servos only):
- Flash fixed firmware
- Record blackbox log
- Decode with standard blackbox_decode
- Verify no spurious frame failures

If no hardware available, the fix is well-analyzed and low-risk.

## Success Criteria

- [ ] git-workflow skill used to create branch
- [ ] Line 1079 condition changed to `AT_LEAST_MOTORS_1`
- [ ] Optional: Line 1346 changed for consistency
- [ ] PR created against maintenance-9.x
- [ ] PR has concise, clear description
- [ ] Milestone set to 9.1
- [ ] Code compiles without errors
- [ ] PR submitted

## Important Notes

**Why this is safe:**
- Single condition change
- Matches existing field definition logic
- Only affects rare case (motorCount=0 with MOTORS flag enabled)
- No changes to data structures or decoder

**Who is affected:**
- Fixed-wing aircraft with servos only (no motors)
- Default blackbox config has MOTORS enabled
- Rare configuration, which is why bug went undetected

**Why P-frame works by accident:**
P-frame uses loop starting at 0, so when motorCount=0, loop doesn't execute → 0 bytes written → correct.
I-frame writes motor[0] unconditionally outside loop → 1 byte written → wrong.

**Documentation reference:**
The complete analysis is in `claude/test_tools/inav/gps/MOTORS_CONDITION_BUG.md` - refer to this for full technical details if needed.

---
**Manager**
