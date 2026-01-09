# Task Assignment: Fix Transpiler CSE Mutation Bug

**Date:** 2025-12-09
**To:** Developer
**From:** Manager
**Priority:** HIGH
**Project:** fix-transpiler-cse-mutation-bug

## Problem

The JavaScript transpiler's Common Subexpression Elimination (CSE) incorrectly reuses expressions after the underlying variable has been mutated.

### Reproduction Case 1

**Input:**
```javascript
if (gvar[1] < 2) {
  gvar[1]++;
}

if (gvar[1] < 2) {
  gvar[1]++;
}
```

**Actual Output:** (WRONG)
```
logic 0 1 -1 3 5 1 0 2 0
```

Only ONE logic condition generated! The second `if (gvar[1] < 2)` is incorrectly optimized away because CSE thinks the expression result is unchanged.

**Expected:** Two separate `gvar[1] < 2` comparisons because `gvar[1]++` modifies the variable between checks.

### Reproduction Case 2

```javascript
gvar[1]++;

if (gvar[1] < 2) {
  gvar[1] = gvar[1] + 1;
}

if (gvar[1] < 2) {
  gvar[1] = gvar[1] + 1;
}
```

**Output:**
```
logic 0 1 -1 19 0 1 0 1 0
logic 1 1 -1 3 5 1 0 2 0
logic 2 1 1 19 0 1 0 1 0
logic 3 1 1 19 0 1 0 1 0
```

Note: Only ONE `gvar[1] < 2` check (logic 1). The second `if` statement doesn't generate its own comparison.

## Root Cause

CSE caches expression results like `gvar[1] < 2` and reuses them. But it doesn't invalidate the cache when:
- `gvar[1]++` is executed
- `gvar[1] = ...` is executed

## Solution

When processing any assignment or mutation:
1. Identify which variable(s) are being modified
2. Invalidate any CSE cache entries that reference those variables
3. Subsequent uses will generate fresh logic conditions

**Key insight:** Any expression involving `gvar[X]` must be invalidated when `gvar[X]` is assigned/incremented.

## Files to Investigate

Look in `inav-configurator/js/transpiler/` for:
- CSE cache implementation
- Expression caching logic
- Assignment/increment handling

Search for: `cse`, `cache`, `expression`, `gvar`, `optimize`

## Test Cases to Add

```javascript
// Test: Mutation invalidates CSE
if (gvar[1] < 2) { gvar[1]++; }
if (gvar[1] < 2) { gvar[1]++; }
// Assert: TWO separate comparison logic conditions

// Test: Unrelated mutation doesn't invalidate
gvar[2] = 5;
if (gvar[1] < 2) { ... }
if (gvar[1] < 2) { ... }
// Assert: CAN reuse comparison (gvar[2] doesn't affect gvar[1])
```

## Deliverables

1. Identify where CSE cache is implemented
2. Add cache invalidation on variable mutation
3. Add regression tests for the reproduction cases
4. Create PR with fix

## Reference

See: `claude/projects/fix-transpiler-cse-mutation-bug/summary.md`
