# Task Assignment: Fix Decompiler "Unknown operation 3 (Lower Than)" Error

**Date:** 2025-11-28 19:30
**Project:** Transpiler Bug Fix
**Priority:** High
**Estimated Effort:** 1-2 hours
**Branch:** transpiler_clean_copy (inav-configurator)

## Task

Fix the decompiler error "Unknown operation 3 (Lower Than) in action" that occurs when decompiling certain logic conditions.

## Problem

When decompiling the following logic conditions, the transpiler produces the warning:
```
Decompilation Warnings:
Unknown operation 3 (Lower Than) in action
```

## Logic Conditions That Trigger the Error

```
logic 0 1 -1 4 1 8 0 0 0
logic 1 1 -1 5 1 8 0 0 0
logic 2 1 -1 6 1 8 0 0 0
logic 3 1 0 18 0 7 0 0 0
logic 4 1 1 18 0 7 0 10 0
logic 5 1 2 18 0 7 0 17 0
logic 6 1 -1 36 5 7 0 45 0
logic 7 1 -1 15 4 6 0 500 0
logic 8 1 -1 18 0 6 4 7 0
logic 12 0 15 0 0 0 0 0 0
logic 13 0 12 0 0 0 0 0 0
logic 17 0 15 0 0 0 0 0 0
logic 18 0 16 0 0 0 0 0 0
logic 20 1 -1 1 2 17 0 1 0
logic 21 1 -1 1 2 18 0 0 0
logic 22 1 -1 7 4 20 4 21 0
logic 23 1 22 3 2 11 0 1111 0
```

## Analysis

The error mentions "operation 3 (Lower Than) in action". Looking at line:
```
logic 23 1 22 3 2 11 0 1111 0
```

The format is: `logic <id> <enabled> <activator> <operation> <operandA_type> <operandA_value> <operandB_type> <operandB_value> <flags>`

So logic 23 has:
- activator: 22 (LC 22)
- operation: 3 (which is "Lower Than" / less than comparison)
- operandA: type 2, value 11
- operandB: type 0, value 1111

The decompiler appears to not recognize operation 3 when used as an "action". The issue is likely in the action_decompiler.js - it may be treating a comparison operation as an action incorrectly, or may be missing the mapping for operation 3.

## Files to Investigate

- `js/transpiler/transpiler/action_decompiler.js` - Action decompilation logic
- `js/transpiler/transpiler/condition_decompiler.js` - Condition decompilation logic
- `js/transpiler/transpiler/decompiler.js` - Main decompiler
- `js/transpiler/transpiler/constants.js` - Operation ID mappings

## What to Do

1. Reproduce the error using the logic conditions above
2. Identify why operation 3 (Lower Than) triggers "unknown operation in action"
3. Determine if this is:
   - A missing operation mapping
   - An incorrect classification of the operation as an action vs condition
   - A logic error in the decompiler flow
4. Implement the fix
5. Test with the provided logic conditions
6. Verify no regression with other logic conditions

## Success Criteria

- [ ] The provided logic conditions decompile without warnings
- [ ] Operation 3 (Lower Than) is correctly handled
- [ ] No regression in other decompilation scenarios
- [ ] Changes committed to transpiler_clean_copy branch

## Notes

- The "Lower Than" operation (id 3) is a comparison, typically used as a condition
- The error says "in action" which suggests the decompiler may be misclassifying this
- Check how similar comparison operations (Greater Than, Equal, etc.) are handled

---
**Manager**
