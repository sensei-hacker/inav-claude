# Task Assignment: Extract Duplicated extractValue() Function

**Date:** 2025-12-10 22:00
**Project:** Transpiler Simplification
**Priority:** High
**Estimated Effort:** 1-2 hours
**Branch:** From `decompiler-pid` (or current transpiler branch)

## Task

Extract the duplicated `extractValue()` function from `parser.js` and `arrow_function_helper.js` into a shared utility module.

## Background

Your simplification review identified that `extractValue()` exists in two places:
- `parser.js:665-717` (~50 lines)
- `arrow_function_helper.js:228-281` (~50 lines)

These are nearly identical implementations. Bug fixes must currently be applied twice, and there's risk of the implementations diverging.

## What to Do

### Phase 1: Test-Driven Development (IMPORTANT)

**The current code is working well. Before changing anything:**

1. Write tests that exercise the existing `extractValue()` function
2. Cover these cases mentioned in your review:
   - NumericLiteral, StringLiteral
   - UnaryExpression (negation)
   - BinaryExpression (constant folding)
   - Identifier, MemberExpression
   - ParenthesizedExpression
3. Run tests to verify they pass with current implementation

### Phase 2: Implementation

1. Create `expression_utils.js` (or similar) in the transpiler directory
2. Move `extractValue()` to the new module
3. Export the function
4. Update `parser.js` to import from shared module
5. Update `arrow_function_helper.js` to import from shared module
6. Run tests to verify nothing broke

### Phase 3: Cleanup

1. Remove the duplicate implementations
2. Run full test suite
3. Verify the transpiler still works end-to-end (compile + decompile round-trip)

## Investigation Required

While you're working on this, please also investigate:

**Item #7 - Potential Dead Code:** Verify if `groupConditions()` and `decompileGroup()` in `decompiler.js` are still used or can be removed. The tree-based decompiler may have replaced the older group-based approach.

Report your findings on this in your completion report.

## Success Criteria

- [ ] Tests written BEFORE implementation changes
- [ ] `extractValue()` exists in single location only
- [ ] Both `parser.js` and `arrow_function_helper.js` import from shared module
- [ ] All existing tests pass
- [ ] Transpiler compile/decompile round-trip works
- [ ] Investigation complete for Item #7 (dead code)

## Files to Modify

- `js/transpiler/transpiler/parser.js` - Remove duplicate, add import
- `js/transpiler/transpiler/arrow_function_helper.js` - Remove duplicate, add import
- NEW: `js/transpiler/transpiler/expression_utils.js` (or similar)

## Notes

- This is Item #1 from your simplification review
- We'll work through the 8 items one at a time
- **Be extra careful** - the current code is working well
- Test-driven development is mandatory for this project

---
**Manager**
