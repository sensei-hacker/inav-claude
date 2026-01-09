# Task Assignment: Fix Decompiler Condition Number Comments

**Date:** 2025-11-29 10:45
**Project:** fix-decompiler-condition-numbers
**Priority:** Medium
**Estimated Effort:** 1-2 hours
**Branch:** transpiler_clean_copy

## Task

The decompiler generates comments like `// Condition can be read by logicCondition[N]` but the condition numbers are wrong. Fix the decompiler to show the correct condition index.

## Background

When logic conditions are chained together (each referencing the previous as an activator), the decompiler should indicate which condition index holds the final result that can be read.

**Example Logic Conditions:**
```
logic 0 1 -1 1 2 39 0 1 0    # mixerTransitionActive === 1
logic 1 1 0 1 2 17 0 1 0     # AND isArmed === 1 (activator: 0)
logic 2 1 1 2 2 9 0 1111 0   # AND groundSpeed > 1111 (activator: 1)
...
logic 19 1 -1 1 2 38 0 1 0   # activeMixerProfile === 1
logic 20 1 19 1 2 17 0 1 0   # AND isArmed === 1 (activator: 19)
logic 21 1 20 1 2 18 0 0 0   # AND isAutoLaunch === 0 (activator: 20)
logic 22 1 21 3 2 11 0 1111 0 # AND airSpeed < 1111 (activator: 21)
```

**Current Decompiled Output (WRONG):**
```javascript
if (flight.mixerTransitionActive === 1 && flight.isArmed === 1 && flight.groundSpeed > 1111) {
  // Condition can be read by logicCondition[0]   <-- WRONG
}

if (flight.activeMixerProfile === 1 && flight.isArmed === 1 && flight.isAutoLaunch === 0 && flight.airSpeed < 1111) {
  // Condition can be read by logicCondition[19]  <-- WRONG
}
```

**Expected Output (CORRECT):**
```javascript
if (flight.mixerTransitionActive === 1 && flight.isArmed === 1 && flight.groundSpeed > 1111) {
  // Condition can be read by logicCondition[2]   <-- Last in chain
}

if (flight.activeMixerProfile === 1 && flight.isArmed === 1 && flight.isAutoLaunch === 0 && flight.airSpeed < 1111) {
  // Condition can be read by logicCondition[22]  <-- Last in chain
}
```

The comment should reference the **terminal condition** (last in the chain), not the first, because that's where the combined result is stored.

## What to Do

1. **Find the comment generation code**
   - Search for `Condition can be read by` in the decompiler
   - Understand how it determines the condition number

2. **Identify the bug**
   - The code is likely using the first condition index in the chain
   - It should use the last/terminal condition index

3. **Fix the logic**
   - When building chained conditions, track the terminal index
   - Use that index in the comment

4. **Test**
   - Use the provided example to verify correct output
   - Add a test case for this scenario
   - Run full test suite

## Success Criteria

- [ ] First chain shows `logicCondition[2]` (not 0)
- [ ] Second chain shows `logicCondition[22]` (not 19)
- [ ] Test case added for chained condition comments
- [ ] All existing tests pass

## Files to Check

- `inav-configurator/js/transpiler/decompiler.js`
- `inav-configurator/js/transpiler/helpers/condition_decompiler.js`
- `inav-configurator/tests/transpiler/`

## Notes

- This is on the transpiler_clean_copy branch (PR #2439)
- The condition number matters because users may want to reference the result in other logic conditions or OSD elements

---
**Manager**
