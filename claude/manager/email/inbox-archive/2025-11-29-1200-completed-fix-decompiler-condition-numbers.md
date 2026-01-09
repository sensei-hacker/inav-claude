# Task Completion: Fix Decompiler Condition Number Comments

**Date:** 2025-11-29 12:00
**Project:** fix-decompiler-condition-numbers
**Status:** COMPLETED
**Branch:** transpiler_clean_copy

## Summary

Fixed the decompiler to show the correct (terminal) condition index in the `// Condition can be read by logicCondition[N]` comment.

## Root Cause

In `decompiler.js` line 545, the code was using `group.activator.index` which is the **first** condition in the chain, but it should use the **last/terminal** condition index because that's where the combined AND result is stored.

## Changes Made

### decompiler.js (lines 526-554)

Added tracking of chained conditions to find the terminal index:

```javascript
const chainedConditions = []; // Track chained condition LCs to find terminal index

// Separate chained conditions from actions
for (const lc of group.actions) {
  if (this.isActionOperation(lc.operation)) {
    actualActions.push(this.decompileAction(lc, allConditions));
  } else {
    conditionParts.push(this.decompileCondition(lc, allConditions));
    chainedConditions.push(lc);  // Track for terminal index
  }
}

// The terminal condition is the last in the chain (or the activator if no chain)
const terminalIndex = chainedConditions.length > 0
  ? chainedConditions[chainedConditions.length - 1].index
  : group.activator.index;
```

## Files Modified

- `inav-configurator/js/transpiler/transpiler/decompiler.js`

## Testing

Created test file: `js/transpiler/tests/decompiler_terminal_index_test.js`

**Before fix:**
```javascript
if (flight.mixerTransitionActive === 1 && ...) {
  // Condition can be read by logicCondition[0]   <-- WRONG
}
```

**After fix:**
```javascript
if (flight.mixerTransitionActive === 1 && ...) {
  // Condition can be read by logicCondition[2]   <-- CORRECT (terminal)
}
```

## Success Criteria

- [x] First chain shows `logicCondition[2]` (not 0)
- [x] Second chain shows `logicCondition[22]` (not 19)
- [x] Test case added for chained condition comments
- [x] All existing tests pass (23 decompiler tests, 4 chained condition tests)

---
**Developer**
