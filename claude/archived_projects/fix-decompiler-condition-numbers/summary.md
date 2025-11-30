# Project: Fix Decompiler Condition Number Comments

**Status:** 📋 TODO
**Priority:** Medium
**Type:** Bug Fix
**Created:** 2025-11-29
**Branch:** transpiler_clean_copy
**Related PR:** [#2439](https://github.com/iNavFlight/inav-configurator/pull/2439)
**Estimated Time:** 1-2 hours

## Overview

The decompiler generates comments like `// Condition can be read by logicCondition[N]` but the condition numbers are incorrect.

## Problem

When decompiling logic conditions, the generated comments that indicate which logic condition index can be used to read the result show wrong numbers.

**Example from user report:**

Original logic conditions:
```
logic 0 1 -1 1 2 39 0 1 0
logic 1 1 0 1 2 17 0 1 0
logic 2 1 1 2 2 9 0 1111 0
...
logic 19 1 -1 1 2 38 0 1 0
logic 20 1 19 1 2 17 0 1 0
logic 21 1 20 1 2 18 0 0 0
logic 22 1 21 3 2 11 0 1111 0
```

Decompiled output:
```javascript
if (flight.mixerTransitionActive === 1 && flight.isArmed === 1 && flight.groundSpeed > 1111) {
  // Condition can be read by logicCondition[0]   <-- Should this be [2]?
}

if (flight.activeMixerProfile === 1 && flight.isArmed === 1 && flight.isAutoLaunch === 0 && flight.airSpeed < 1111) {
  // Condition can be read by logicCondition[19]  <-- Should this be [22]?
}
```

The comment should reference the **last condition in the chain** (the one that holds the final result), not the first.

## Objectives

1. Identify where the condition number comment is generated
2. Fix it to use the correct condition index (the terminal/last condition in the chain)
3. Add test case for this scenario

## Scope

**In Scope:**
- Fix the condition number in decompiler comments
- Ensure the number refers to the readable result condition

**Out of Scope:**
- Other decompiler features
- Transpiler changes

## Implementation Steps

1. Find where `// Condition can be read by logicCondition[N]` is generated in the decompiler
2. Understand how chained conditions are tracked
3. Fix to use the terminal condition index instead of the first
4. Test with the provided example
5. Add a test case

## Success Criteria

- [ ] Condition numbers in comments are correct
- [ ] The number refers to the last/terminal condition in the chain
- [ ] Test case added
- [ ] All existing tests pass

## Key Files

- `inav-configurator/js/transpiler/decompiler.js`
- `inav-configurator/js/transpiler/helpers/condition_decompiler.js`
- `inav-configurator/tests/transpiler/`
