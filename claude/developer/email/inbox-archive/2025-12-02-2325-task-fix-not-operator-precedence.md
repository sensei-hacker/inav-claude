# Task Assignment: Fix NOT Operator Precedence Bug in Transpiler

**Date:** 2025-12-02 23:25
**To:** Developer
**From:** Manager
**Project:** New (standalone bug fix)
**Priority:** HIGH
**Estimated Effort:** 1-2 hours
**Branch:** From master or maintenance branch (wherever transpiler code lives)

---

## Task

Fix logic bug in JavaScript transpiler where the NOT operator (`!`) with comparison operators generates duplicate/incorrect logic conditions due to operator precedence issues.

---

## Problem

**User-reported code:**
```javascript
const { flight, gvar } = inav;

if (flight.gpsSats < 6) {
  gvar[0] = 0;
}

if (!flight.gpsSats < 6) {  // Should mean: !(gpsSats < 6), i.e., gpsSats >= 6
  gvar[0] = 1;
}
```

**Expected behavior:**
- Condition 0: `gpsSats < 6` → set gvar[0] = 0
- Condition 1: `gpsSats >= 6` → set gvar[0] = 1 (negation of first condition)

**Actual behavior:**
- Condition 0: `gpsSats < 6` → set gvar[0] = 0
- Condition 2: `gpsSats < 6` → set gvar[0] = 1 ❌ (DUPLICATE!)

**The bug:** Transpiler generates TWO IDENTICAL conditions (both checking `< 6`)

---

## Root Cause Analysis

### JavaScript Operator Precedence

In JavaScript, the `!` (NOT) operator has higher precedence than comparison operators (`<`, `>`, etc.).

**Code:** `!flight.gpsSats < 6`

**How it's evaluated:**
```javascript
// Due to precedence:
(!flight.gpsSats) < 6  // NOT is applied to gpsSats first

// NOT flight.gpsSats:
// - If gpsSats = 0: !0 = true = 1
// - If gpsSats = 5: !5 = false = 0
// - If gpsSats = 8: !8 = false = 0

// Then: (0 or 1) < 6
// Always true!
```

**What user intended:**
```javascript
!(flight.gpsSats < 6)  // Negate the entire comparison
// Equivalent to: flight.gpsSats >= 6
```

### Transpiler Bug

The transpiler is likely:
1. Evaluating `!flight.gpsSats < 6` literally (as JavaScript does)
2. NOT recognizing this as a negated comparison
3. NOT converting to the inverse operator (`>=`)

**Result:** Generates same condition twice with different actions.

---

## Expected Solution

The transpiler should detect negated comparisons and convert them properly:

**Input:** `!flight.gpsSats < 6`

**Transpiler should recognize patterns:**
- `!(x < y)` → `x >= y`
- `!(x > y)` → `x <= y`
- `!(x <= y)` → `x > y`
- `!(x >= y)` → `x < y`
- `!(x == y)` → `x != y`
- `!(x != y)` → `x == y`

**Or:** Require parentheses and reject `!x < y` as ambiguous

---

## Investigation Steps

### Step 1: Reproduce the Issue

Create test code:
```javascript
const { flight, gvar } = inav;

if (flight.gpsSats < 6) {
  gvar[0] = 0;
}

if (!flight.gpsSats < 6) {
  gvar[0] = 1;
}
```

Transpile and examine generated logic conditions.

**Expected (buggy):**
```
logic 0 1 ... // gpsSats < 6, set gvar[0] = 0
logic 2 1 ... // gpsSats < 6, set gvar[0] = 1  ❌ SAME CONDITION!
```

### Step 2: Find Transpiler Code

**Likely locations:**
- `js/transpiler/transpiler/*.js` - Expression parsing
- Look for: UnaryExpression handling (NOT operator)
- Look for: BinaryExpression handling (comparison operators)
- Look for: Operator precedence logic

**Key files to check:**
```bash
cd js/transpiler
grep -r "UnaryExpression" transpiler/
grep -r "BinaryExpression" transpiler/
grep -r "operator.*precedence" transpiler/
grep -r "NOT\|!" transpiler/
```

### Step 3: Understand Current Parsing

**AST for:** `!flight.gpsSats < 6`

Likely parsed as:
```javascript
{
  type: 'BinaryExpression',
  operator: '<',
  left: {
    type: 'UnaryExpression',
    operator: '!',
    argument: {
      type: 'MemberExpression',
      object: 'flight',
      property: 'gpsSats'
    }
  },
  right: { type: 'Literal', value: 6 }
}
```

This is WRONG for user intent but CORRECT for JavaScript precedence.

**AST for:** `!(flight.gpsSats < 6)` (with parentheses)

Should be:
```javascript
{
  type: 'UnaryExpression',
  operator: '!',
  argument: {
    type: 'BinaryExpression',
    operator: '<',
    left: { ... gpsSats ... },
    right: { value: 6 }
  }
}
```

This allows transpiler to detect negated comparison and invert operator.

---

## Possible Solutions

### Solution A: Require Parentheses (Strict)

**Reject** code like `!flight.gpsSats < 6` as ambiguous.

**Error message:**
```
Transpilation Error:
Ambiguous NOT operator. Use parentheses to clarify:
- For negated comparison: !(flight.gpsSats < 6)
- For NOT variable: (!flight.gpsSats) < 6
Line: 4
```

**Pros:**
- Forces user to be explicit
- No ambiguity
- Easier to implement

**Cons:**
- More strict than JavaScript
- Users might be confused

### Solution B: Detect and Invert (Smart)

**Detect** pattern: `UnaryExpression(!)` → `BinaryExpression(comparison)`

**Convert:**
- `!x < y` → `x >= y`
- `!x > y` → `x <= y`
- etc.

**Implementation:**
```javascript
function transpileCondition(node) {
  // Check for: UnaryExpression(!) as left operand of comparison
  if (node.type === 'BinaryExpression' && isComparisonOp(node.operator)) {
    if (node.left.type === 'UnaryExpression' && node.left.operator === '!') {
      // WARN: Ambiguous precedence
      console.warn(`Ambiguous NOT operator at line ${node.loc.start.line}. ` +
                   `Use parentheses: !(${code}) instead of !${code}`);

      // Assume user meant negated comparison
      // Transform: !x < y → x >= y
      return transpileComparison(
        node.left.argument,  // Remove the NOT
        invertOperator(node.operator),  // Invert comparison
        node.right
      );
    }
  }

  // ... normal handling
}

function invertOperator(op) {
  const inversions = {
    '<': '>=',
    '>': '<=',
    '<=': '>',
    '>=': '<',
    '==': '!=',
    '!=': '=='
  };
  return inversions[op] || op;
}
```

**Pros:**
- Handles common user intent
- Provides helpful warning
- More user-friendly

**Cons:**
- Guesses user intent
- Adds complexity

### Solution C: Document and Warn (Minimal)

**Detect** the pattern and **warn**, but don't auto-fix:
```
Warning: Operator precedence may cause unexpected behavior.
  !flight.gpsSats < 6
  ^
Did you mean: !(flight.gpsSats < 6) ?
Use parentheses to clarify intent.
```

Then transpile as JavaScript would (literally).

**Pros:**
- Educates users
- No guessing

**Cons:**
- Doesn't fix the issue
- Users still get wrong logic

---

## Recommendation

**Implement Solution B (Detect and Invert) with Warning**

1. Detect pattern: `!variable < value`
2. Warn user about ambiguity (console + UI warning)
3. Automatically invert to `variable >= value`
4. Generate correct logic condition

**Rationale:**
- 99% of users mean "negated comparison"
- Warning educates without blocking
- Fixes the bug while guiding users to better code

---

## Files to Modify

**Likely files:**
- `js/transpiler/transpiler/condition_transpiler.js` (or similar)
- `js/transpiler/transpiler/expression_parser.js` (or similar)
- Wherever BinaryExpression and UnaryExpression are processed

**Also update:**
- Documentation explaining operator precedence
- Examples showing correct usage

---

## Testing

### Test Cases

**Test 1: Basic negation**
```javascript
// Input
if (!flight.gpsSats < 6) {
  gvar[0] = 1;
}

// Expected output: gpsSats >= 6
// Condition: GREATER_THAN_OR_EQUALS, operandA=gpsSats, operandB=6
```

**Test 2: All comparison operators**
```javascript
!flight.altitude < 100   // → altitude >= 100
!flight.altitude > 100   // → altitude <= 100
!flight.altitude <= 100  // → altitude > 100
!flight.altitude >= 100  // → altitude < 100
!flight.isArmed == 1     // → isArmed != 1
!flight.isArmed != 0     // → isArmed == 0
```

**Test 3: With parentheses (should work unchanged)**
```javascript
!(flight.gpsSats < 6)    // → gpsSats >= 6 (already correct AST)
```

**Test 4: Actual NOT of variable**
```javascript
(!flight.isArmed) < 6    // Uncommon but valid - should warn?
```

### Regression Testing

Ensure existing transpiler tests still pass:
```bash
npm test -- --grep "transpiler"
```

---

## Success Criteria

- [ ] Code `!flight.gpsSats < 6` generates condition `gpsSats >= 6`
- [ ] Warning message displayed to user about precedence
- [ ] All 6 comparison operators handled correctly
- [ ] No duplicate conditions generated
- [ ] Existing tests still pass
- [ ] New test cases added for NOT precedence

---

## Documentation Updates

**Update user documentation:**

### Good Practice:
```javascript
// ✅ RECOMMENDED: Use parentheses for clarity
if (!(flight.gpsSats < 6)) {
  gvar[0] = 1;  // Good GPS
}

// ✅ RECOMMENDED: Use inverse operator directly
if (flight.gpsSats >= 6) {
  gvar[0] = 1;  // Good GPS - clearer!
}
```

### What to Avoid:
```javascript
// ⚠️ WARNING: Ambiguous due to operator precedence
if (!flight.gpsSats < 6) {
  // Transpiler will assume you meant: gpsSats >= 6
  // But JavaScript evaluates as: (!gpsSats) < 6
  gvar[0] = 1;
}
```

---

## Priority Justification

**HIGH priority because:**
- **Logic bug:** Generates incorrect flight logic (safety issue)
- **User confusion:** Unexpected behavior, hard to debug
- **Common pattern:** Users naturally write `!condition`
- **Quick fix:** 1-2 hours, localized change

---

## Related Issues

This may also affect:
- Other unary operators (`+`, `-`, `~`)
- Bitwise operations
- Ternary operator precedence

**Consider:** Full operator precedence audit (separate task)

---

## Example Commit Message

```
Fix NOT operator precedence in transpiler conditions

The transpiler was incorrectly handling negated comparisons due to
JavaScript operator precedence. Code like `!flight.gpsSats < 6` was
being parsed as `(!flight.gpsSats) < 6` instead of the user's intent:
`!(flight.gpsSats < 6)`, resulting in duplicate/incorrect conditions.

Solution:
- Detect pattern: UnaryExpression(!) left of BinaryExpression(comparison)
- Automatically invert comparison operator (< → >=, > → <=, etc.)
- Warn user about operator precedence and suggest parentheses
- Generate correct logic condition

Changes:
- js/transpiler/transpiler/condition_transpiler.js: Add precedence detection
- Add invertOperator() helper function
- Add user warning for ambiguous NOT usage

Testing:
- All 6 comparison operators tested with NOT
- Existing transpiler tests still pass
- New test cases added for precedence handling

Fixes user-reported bug where GPS example generated duplicate conditions.
```

---

**Manager**
2025-12-02 23:25
