# Task Completed: Fix Transpiler CSE Mutation Bug

**Date:** 2025-12-09 17:35
**From:** Developer
**Type:** Completion Report
**Project:** fix-transpiler-cse-mutation-bug

## Status: COMPLETED

## Summary

Fixed the transpiler's Common Subexpression Elimination (CSE) bug where cached conditions were incorrectly reused after the underlying variable was mutated.

## Root Causes Found

**Two separate bugs were discovered and fixed:**

1. **Parser Bug**: `transformBodyStatement()` in parser.js didn't handle `UpdateExpression` (++/--) inside if bodies, causing them to be silently dropped. This meant `gvar[1]++` inside an if body wasn't being parsed at all.

2. **Optimizer Bug**: The CSE cache in optimizer.js wasn't invalidated when variables were mutated in statement bodies. After processing `if (gvar[1] < 2) { gvar[1]++; }`, the cache entry for `gvar[1] < 2` remained, causing subsequent identical conditions to reuse the stale result.

## Solution

### Parser Fix (parser.js)
```javascript
// Added in transformBodyStatement():
if (expr && expr.type === 'UpdateExpression') {
  return this.transformUpdateExpression(expr, stmt.loc, stmt.range);
}
```

### Optimizer Fix (optimizer.js)
Added three new methods:
- `findMutatedVariables(body)` - Recursively scans statement body for Assignment nodes
- `invalidateCacheForVariable(conditionMap, invertedMap, varName)` - Removes cache entries referencing a variable
- `conditionKeyReferencesVariable(key, varName)` - Checks if a cache key references a variable

Modified `eliminateCommonSubexpressions()` to invalidate cache AFTER processing each statement's body mutations.

### Supporting Changes
- action_generator.js: Accept `conditionGenerator` reference for codegen-level invalidation
- codegen.js: Pass `conditionGenerator` to ActionGenerator context
- condition_generator.js: Add runtime invalidation methods (for codegen-level CSE)

## Test Coverage

Created `test_cse_mutation_bug.js` with 6 comprehensive tests:
1. CSE invalidation after increment (`gvar[1]++`)
2. CSE invalidation after assignment (`gvar[1] = gvar[1] + 1`)
3. CSE invalidation after pre-increment (top-level `gvar[1]++`)
4. CSE preservation for unrelated mutation (`gvar[2]++` shouldn't invalidate `gvar[1]` conditions)
5. Multiple sequential mutations (3 consecutive if blocks)
6. Complex expressions (`gvar[1] + flight.altitude > 100`)

**All 6 tests pass.** All existing transpiler tests also pass.

## Branch

**Branch:** `fix/transpiler-cse-mutation-bug`
**Commit:** `af99ea486`
**Repository:** inav-configurator

## Files Changed

```
js/transpiler/transpiler/action_generator.js       |  14 ++
js/transpiler/transpiler/codegen.js                |   8 +-
js/transpiler/transpiler/condition_generator.js    |  55 ++++++
js/transpiler/transpiler/optimizer.js              | 102 +++++++++-
js/transpiler/transpiler/parser.js                 |   4 +
js/transpiler/transpiler/tests/test_cse_mutation_bug.js | 216 ++++++++++
6 files changed, 396 insertions(+), 3 deletions(-)
```

## Impact

This fix ensures that JavaScript code using patterns like:
```javascript
if (gvar[1] < 2) { gvar[1]++; }
if (gvar[1] < 2) { gvar[1]++; }
```

Will correctly generate TWO separate condition checks, allowing the counter to increment properly up to the limit.

---
**Developer**
