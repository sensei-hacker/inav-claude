# Task Completed: Fix Decompiler Chained Conditions

## Status: COMPLETED

## Summary
Fixed the decompiler to properly handle chained conditions with activators. This resolves the "Unknown operation 3 (Lower Than) in action" error and properly outputs combined AND conditions from activator chains.

## Branch
`transpiler_clean_copy` - commit 42d1febd

## Issues Fixed

### 1. "Unknown operation 3 (Lower Than) in action" error
**Cause:** `isActionOperation()` was incomplete - missing many action operations. Comparison operations with activators were being incorrectly treated as actions.

**Fix:** Expanded `isActionOperation()` with complete list of all action operations (GVAR_SET, GVAR_INC, GVAR_DEC, PORT_SET, OVERRIDE_ARMING_SAFETY, OVERRIDE_THROTTLE_SCALE, SWAP_ROLL_YAW, SET_VTX_POWER_LEVEL, etc.)

### 2. "Logic condition X has no valid activator" warnings
**Cause:** Only direct children were collected, not grandchildren in activator chains.

**Fix:** Added `collectDescendants()` method to recursively collect all descendants in an activator chain.

### 3. Chained conditions not being output
**Cause:** Chains like LC0→LC1→LC2 where all are conditions (no actions) produced no output because `decompileActionOrCondition()` returned null for conditions.

**User insight:** "It doesn't matter if there are no actions to perform when they are true. Logic conditions can be read from external code."

**Fix:** Modified `decompileGroup()` to:
1. Separate chained conditions from actual actions
2. Build combined AND condition from all conditions in the chain
3. Output the combined condition even if there are no actions

## Example Output

Input:
```
logic 0 1 -1 1 2 39 0 1 0   # LC0: param39 == 1 (root)
logic 1 1 0 1 2 17 0 1 0    # LC1: isArmed == 1, activator=0
logic 2 1 1 2 2 9 0 1111 0  # LC2: groundSpeed > 1111, activator=1
```

Output:
```javascript
if (flight.mixerTransitionActive === 1 && flight.isArmed === 1 && flight.groundSpeed > 1111) {
  // Condition can be read by logicCondition[0]
}
```

## Files Changed

### Modified
- `js/transpiler/transpiler/decompiler.js`
  - Added `collectDescendants()` method
  - Expanded `isActionOperation()` with all action operations
  - Modified `decompileGroup()` to build combined AND conditions

### Added
- `js/transpiler/transpiler/tests/chained_conditions.test.cjs` - 4 new tests
- `js/transpiler/transpiler/tests/run_chained_conditions_tests.cjs` - test runner

## Testing
- All 23 existing decompiler tests pass
- All 4 new chained condition tests pass
- Tested with user's original logic conditions - works correctly

---
**Developer**
