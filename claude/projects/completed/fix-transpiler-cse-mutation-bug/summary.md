# Fix Transpiler CSE Mutation Bug

## Problem

The JavaScript transpiler's Common Subexpression Elimination (CSE) optimization incorrectly reuses expressions involving variables that have been mutated between uses.

### Example 1: Incorrect output

**Input JavaScript:**
```javascript
if (gvar[1] < 2) {
  gvar[1]++;
}

if (gvar[1] < 2) {
  gvar[1]++;
}
```

**Actual Output:** (WRONG - only 1 logic condition)
```
logic 0 1 -1 3 5 1 0 2 0
```

**Expected:** Two separate condition checks because `gvar[1]` may have changed after the first `gvar[1]++`.

### Example 2: Partial fix reveals the issue

**Input JavaScript:**
```javascript
gvar[1]++;

if (gvar[1] < 2) {
  gvar[1] = gvar[1] + 1;
}

if (gvar[1] < 2) {
  gvar[1] = gvar[1] + 1;
}
```

**Actual Output:** (Still wrong - CSE reuses `gvar[1] < 2` check)
```
logic 0 1 -1 19 0 1 0 1 0
logic 1 1 -1 3 5 1 0 2 0     <- First check (correct)
logic 2 1 1 19 0 1 0 1 0
logic 3 1 1 19 0 1 0 1 0     <- Missing: Second gvar[1] < 2 check!
```

**Expected:** The second `if (gvar[1] < 2)` should generate a NEW comparison, not reuse the first one, because `gvar[1]` was modified inside the first `if` block.

## Root Cause

The CSE optimization tracks expressions like `gvar[1] < 2` and reuses them. However, it doesn't invalidate cached expressions when:
1. The variable is mutated (`gvar[1]++` or `gvar[1] = ...`)
2. An assignment occurs that could affect the cached expression's value

## Solution Approaches

### Option 1: Invalidate on Mutation (Recommended)
When processing an assignment or increment:
1. Identify which variables are being modified
2. Invalidate any cached CSE entries that reference those variables
3. Future uses will generate fresh expressions

**Pseudocode:**
```javascript
function invalidateCachedExpressions(mutatedVar) {
  for (let key in cseCache) {
    if (expressionReferences(key, mutatedVar)) {
      delete cseCache[key];
    }
  }
}
```

### Option 2: Mark Expressions as Non-Cacheable
Add a flag during expression analysis that marks expressions involving mutable state as "do not cache" or "single-use only."

### Option 3: Scope-Based CSE
Only reuse expressions within the same basic block (between control flow changes). Reset CSE cache at:
- Function boundaries
- After any assignment statement
- At control flow merge points

## Files to Investigate

The CSE logic is likely in:
- `inav-configurator/js/transpiler/` directory
- Look for: `cse`, `cache`, `expression`, `optimize`

## Test Cases

```javascript
// Test 1: Increment in if body
if (gvar[1] < 2) { gvar[1]++; }
if (gvar[1] < 2) { gvar[1]++; }
// Expected: TWO separate comparisons

// Test 2: Assignment in if body
if (gvar[1] < 2) { gvar[1] = gvar[1] + 1; }
if (gvar[1] < 2) { gvar[1] = gvar[1] + 1; }
// Expected: TWO separate comparisons

// Test 3: Unrelated mutation
gvar[2] = 5;
if (gvar[1] < 2) { ... }
if (gvar[1] < 2) { ... }
// Expected: CAN reuse (gvar[2] doesn't affect gvar[1])

// Test 4: Sequential increments
gvar[1]++;
let x = gvar[1];  // Should see incremented value
gvar[1]++;
let y = gvar[1];  // Should see second increment
// Expected: x and y get different values
```

## Impact

**Severity:** HIGH - Logic conditions execute incorrectly, potentially causing unexpected flight behavior.

**User Impact:** Any JavaScript using loops or repeated conditionals with mutations may silently generate wrong logic.
