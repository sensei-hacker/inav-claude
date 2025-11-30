# Phase 2: Error System Design

**Date:** 2025-11-23
**Status:** Design Complete - Ready for Implementation

## Design Decisions

### 1. Error Collection Strategy

**Decision: Collect All Errors, Then Throw at End** ✅

**Rationale:**
- Matches analyzer pattern (proven to work well)
- Shows user ALL errors at once (better UX)
- User can fix multiple issues before retrying
- More helpful than stopping at first error

**Implementation:**
```javascript
class INAVCodeGenerator {
  constructor() {
    this.errors = [];  // Collect errors here
    this.warnings = []; // Optional warnings
    // ... existing code
  }

  generate(ast) {
    this.errors = [];
    this.warnings = [];

    // ... generate code

    // At the end, throw if errors
    if (this.errors.length > 0) {
      const errorMsg = 'Code generation errors:\n' +
        this.errors.map(e => `  - ${e.message}${e.line ? ` (line ${e.line})` : ''}`).join('\n');
      throw new Error(errorMsg);
    }

    return this.commands;
  }
}
```

### 2. Error Object Structure

**Simple Structure (Consistent with Analyzer):**

```javascript
{
  message: string,   // Human-readable error message
  line: number,      // Line number in source code (if available)
  type?: string,     // Optional: 'error' | 'warning' for categorization
  code?: string,     // Optional: Error code for programmatic handling
  suggestion?: string // Optional: Helpful suggestion
}
```

**Examples:**

```javascript
// Basic error
{
  message: "Unknown operand 'customVariable'",
  line: 5
}

// Error with suggestion
{
  message: "Unknown operand 'customVariable'. Available: flight.*, rc.*, gvar[0-7]",
  line: 5,
  type: 'error',
  code: 'unknown_operand',
  suggestion: "Did you mean 'gvar[0]'?"
}

// Validation error
{
  message: "edge() requires exactly 3 arguments (condition, duration, action)",
  line: 12,
  type: 'error',
  code: 'invalid_args'
}
```

### 3. Line Number Tracking

**Challenge:** CodeGen receives AST nodes that may have `loc` property, but not all code paths preserve it.

**Solution:**
```javascript
// Helper method to extract line number
getLineNumber(node) {
  if (node && node.loc && node.loc.start) {
    return node.loc.start.line;
  }
  return null; // Unknown line
}

// Usage in error collection
this.errors.push({
  message: `Unknown operand: ${value}`,
  line: this.getLineNumber(currentNode)
});
```

**Fallback:** If line number unavailable, show error without line number. Better than not showing error at all!

### 4. Backward Compatibility

**Status:** NOT A CONCERN ✅

This is a **new feature** for INAV (as of 2025-11-23, until 2026-01-01). There is no existing production code that would break. Users are currently in beta testing phase, so making errors visible is exactly what they need.

**Impact:**
- No migration path needed
- No compatibility shims required
- Can enforce strict error checking immediately
- Better UX for beta testers

## Error Messages Design

### Template Format

**Good error message includes:**
1. What's wrong (clear description)
2. Where it is (line number if available)
3. Why it's wrong (context)
4. How to fix it (suggestions)

**Template:**
```
[What] [Context]. [Suggestion]
Example: "Unknown operand 'foo'. Available: flight.*, rc.*, gvar[0-7]"
```

### Error Messages by Category

#### Category 1: Unknown Operands (CRITICAL)

**Current:** `console.warn('Unknown operand: ' + value)`
**Location:** codegen.js:666

**New Messages:**

| Context | Message |
|---------|---------|
| Simple unknown | `Unknown operand '${value}'. Available: flight.*, rc.*, gvar[0-7], waypoint.*, pid.*` |
| Typo detected | `Unknown operand '${value}'. Did you mean '${suggestion}'?` |
| Accessing property | `Unknown property '${prop}' on '${obj}'. Available: ${available.join(', ')}` |

**Implementation:**
```javascript
// codegen.js:666
// OLD:
console.warn(`Unknown operand: ${value}`);
return { type: OPERAND_TYPE.VALUE, value: 0 };

// NEW:
this.addError(
  `Unknown operand '${value}'. Available: flight.*, rc.*, gvar[0-7], waypoint.*, pid.*`,
  null,
  'unknown_operand'
);
return { type: OPERAND_TYPE.VALUE, value: 0 }; // Return dummy value to continue collecting errors
```

#### Category 2: Invalid Function Arguments (HIGH)

**Affected Functions:**
- edge(condition, duration, action)
- sticky(onCondition, offCondition, action)
- delay(condition, duration, action)
- timer(onMs, offMs, action)
- whenChanged(value, threshold, action)

**Error Messages:**

| Function | Error | Message |
|----------|-------|---------|
| edge | Wrong arg count | `edge() requires exactly 3 arguments (condition, duration, action). Got ${args.length}` |
| edge | Wrong type | `edge() argument 1 must be an arrow function, got ${type}` |
| sticky | Wrong arg count | `sticky() requires exactly 3 arguments (onCondition, offCondition, action). Got ${args.length}` |
| delay | Wrong arg count | `delay() requires exactly 3 arguments (condition, duration, action). Got ${args.length}` |
| timer | Non-numeric | `timer() durations must be numeric literals. Got: ${typeof value}` |
| timer | Negative value | `timer() durations must be positive. Got: ${value}ms` |
| whenChanged | Wrong arg count | `whenChanged() requires exactly 3 arguments (value, threshold, action). Got ${args.length}` |
| whenChanged | Invalid threshold | `whenChanged() threshold must be a positive number. Got: ${value}` |

**Example Implementation:**
```javascript
// codegen.js:235
// OLD:
if (!args || args.length !== 3) {
  console.warn('edge() requires 3 arguments');
  return null;
}

// NEW:
if (!args || args.length !== 3) {
  this.addError(
    `edge() requires exactly 3 arguments (condition, duration, action). Got ${args?.length || 0}`,
    node,
    'invalid_args'
  );
  return null;
}
```

#### Category 3: Invalid Assignment Targets (CRITICAL)

**Current:** `console.warn('Unknown assignment target: ' + target)` (line 633)

**New Messages:**

| Context | Message |
|---------|---------|
| Unknown target | `Cannot assign to '${target}'. Only gvar[0-7], rc[0-17], and override.* are writable` |
| Read-only property | `Cannot assign to '${target}'. This property is read-only` |
| Invalid syntax | `Invalid assignment target: ${target}. Expected format: gvar[N], rc[N], or override.property` |

#### Category 4: Invalid RC Channel Access (HIGH)

**Current:**
- `console.warn('Invalid rc array syntax')` (line 600)
- `console.warn('RC channel out of range')` (line 608)

**New Messages:**

| Error | Message |
|-------|---------|
| Invalid syntax | `Invalid RC channel syntax: '${target}'. Expected format: rc[0] through rc[17]` |
| Out of range | `RC channel ${channel} out of range. INAV supports rc[0] through rc[17]` |

#### Category 5: Unsupported Features (MEDIUM)

**Current:**
- `console.warn('Unsupported function call')` (line 720)
- `console.warn('Unsupported expression type')` (line 740)
- `console.warn('Unknown statement type')` (line 106)
- `console.warn('Unknown condition type')` (line 515)

**New Messages:**

| Feature | Message |
|---------|---------|
| Unknown function | `Unsupported function: ${funcName}(). Supported: edge(), sticky(), delay(), timer(), whenChanged(), Math.abs(), Math.min(), Math.max()` |
| Unknown expression | `Unsupported expression type: ${exprType}. Use arithmetic operators (+, -, *, /) or supported functions` |
| Unknown statement | `Unsupported statement type: ${stmtType}. Only assignments and event handlers are supported` |
| Unknown condition | `Unsupported condition type: ${condType}. Use comparison operators (>, <, ===, etc.) and logical operators (&&, ||, !)` |

#### Category 6: Math Function Errors (MEDIUM)

**Current:** `console.warn('Math.abs() requires exactly 1 argument')` (line 695)

**New Messages:**

| Function | Error | Message |
|----------|-------|---------|
| Math.abs | Wrong args | `Math.abs() requires exactly 1 argument. Got ${args.length}` |
| Math.min | Wrong args | `Math.min() requires exactly 2 arguments. Got ${args.length}` |
| Math.max | Wrong args | `Math.max() requires exactly 2 arguments. Got ${args.length}` |

## Implementation Strategy

### Step-by-Step Plan

#### Step 1: Add Error Collection Infrastructure (30 min)

**File:** `codegen.js`

```javascript
class INAVCodeGenerator {
  constructor() {
    this.errors = [];
    this.warnings = [];
    this.currentNode = null; // Track current AST node for line numbers
    // ... existing code
  }

  /**
   * Helper to get line number from AST node
   */
  getLineNumber(node) {
    if (node && node.loc && node.loc.start) {
      return node.loc.start.line;
    }
    return null;
  }

  /**
   * Add error to collection
   */
  addError(message, node = null, code = null, suggestion = null) {
    this.errors.push({
      message,
      line: this.getLineNumber(node || this.currentNode),
      type: 'error',
      code,
      suggestion
    });
  }

  /**
   * Add warning to collection
   */
  addWarning(message, node = null, code = null) {
    this.warnings.push({
      message,
      line: this.getLineNumber(node || this.currentNode),
      type: 'warning',
      code
    });
  }

  generate(ast) {
    this.errors = [];
    this.warnings = [];
    this.commands = [];
    this.lcIndex = 0;

    // ... existing generation code

    // At the end, throw if errors exist
    if (this.errors.length > 0) {
      const errorMsg = 'Code generation errors:\n' +
        this.errors.map(e => {
          const lineInfo = e.line ? ` (line ${e.line})` : '';
          return `  - ${e.message}${lineInfo}`;
        }).join('\n');
      throw new Error(errorMsg);
    }

    return this.commands;
  }
}
```

#### Step 2: Convert Critical Errors First (1 hour)

Priority order (highest risk first):

1. **Unknown operand** (line 666) - CRITICAL
2. **Unknown assignment target** (line 633) - CRITICAL
3. **Unknown statement type** (line 106) - CRITICAL
4. **Unknown condition type** (line 515) - CRITICAL

**Pattern for conversion:**

```javascript
// BEFORE:
console.warn(`Unknown operand: ${value}`);
return { type: OPERAND_TYPE.VALUE, value: 0 };

// AFTER:
this.addError(
  `Unknown operand '${value}'. Available: flight.*, rc.*, gvar[0-7], waypoint.*, pid.*`,
  null,
  'unknown_operand'
);
return { type: OPERAND_TYPE.VALUE, value: 0 }; // Continue collecting errors
```

#### Step 3: Convert Validation Errors (1 hour)

Convert all helper function validation (edge, sticky, delay, timer, whenChanged):

- Lines 235, 245 (edge validation)
- Lines 271, 281 (sticky validation)
- Lines 310, 320 (delay validation)
- Lines 349, 359, 364 (timer validation)
- Lines 391, 401, 406, 416 (whenChanged validation)

#### Step 4: Convert Remaining Errors (30 min)

- RC channel errors (lines 600, 608)
- Unsupported features (lines 720, 740)
- Math function errors (line 695)

#### Step 5: Testing (1 hour)

Create test file to verify each error type shows correctly.

## Test Cases

### Test 1: Unknown Operand (Analyzer)
```javascript
const code = `
const { flight, gvar } = inav;
if (customVariable > 5) {
  gvar[0] = 1;
}
`;
```
**Expected:** Error on line 3 - "Unknown API object 'customVariable'"
**Note:** Analyzer currently catches this - verify it still works

### Test 2: Unknown Operand (CodeGen)
```javascript
const code = `
const { flight, gvar } = inav;
on.always(() => {
  gvar[0] = unknownVar;
});
`;
```
**Expected:** Error - "Unknown operand 'unknownVar'"
**Note:** Currently silent - will be fixed

### Test 3: Invalid edge() Arguments
```javascript
const code = `
const { flight, gvar } = inav;
edge(flight.yaw > 1800);
`;
```
**Expected:** Error - "edge() requires exactly 3 arguments. Got 1"

### Test 4: Invalid timer() Duration
```javascript
const code = `
const { gvar } = inav;
timer(-1000, 2000, () => { gvar[0] = 1; });
`;
```
**Expected:** Error - "timer() durations must be positive. Got: -1000ms"

### Test 5: RC Channel Out of Range
```javascript
const code = `
const { rc, gvar } = inav;
on.always(() => {
  rc[20] = 1500;
});
`;
```
**Expected:** Error - "RC channel 20 out of range. INAV supports rc[0] through rc[17]"

### Test 6: Read-Only Assignment
```javascript
const code = `
const { flight } = inav;
on.always(() => {
  flight.yaw = 100;
});
`;
```
**Expected:** Error from analyzer - "Cannot assign to 'flight.yaw'. Not a valid INAV writable property"
**Note:** Analyzer already catches this - verify still works

### Test 7: Math.abs() Wrong Args
```javascript
const code = `
const { flight, gvar } = inav;
if (Math.abs(flight.yaw, flight.pitch) > 900) {
  gvar[0] = 1;
}
`;
```
**Expected:** Error - "Math.abs() requires exactly 1 argument. Got 2"

### Test 8: Multiple Errors (Verify All Shown)
```javascript
const code = `
const { flight, gvar } = inav;
edge(flight.yaw > 1800);
timer(-500, 1000, () => { gvar[0] = unknownVar; });
rc[25] = 1500;
`;
```
**Expected:** Multiple errors shown:
1. edge() requires 3 arguments
2. timer() duration must be positive
3. Unknown operand 'unknownVar' (or caught by analyzer)
4. RC channel out of range

## Complete List of Changes

### All console.warn() Calls to Convert

| Line | Current Warning | Category | Priority |
|------|----------------|----------|----------|
| 106 | `Unknown statement type: ${stmt.type}` | Unsupported | CRITICAL |
| 235 | `edge() requires 3 arguments` | Validation | HIGH |
| 245 | `edge() condition must be arrow function` | Validation | HIGH |
| 271 | `sticky() requires 3 arguments` | Validation | HIGH |
| 281 | `sticky() conditions must be arrow functions` | Validation | HIGH |
| 310 | `delay() requires 3 arguments` | Validation | HIGH |
| 320 | `delay() condition must be arrow function` | Validation | HIGH |
| 349 | `timer() requires 3 arguments` | Validation | HIGH |
| 359 | `timer() durations must be numeric` | Validation | HIGH |
| 364 | `timer() durations must be positive` | Validation | HIGH |
| 391 | `whenChanged() requires 3 arguments` | Validation | HIGH |
| 401 | `whenChanged() threshold must be numeric` | Validation | HIGH |
| 406 | `whenChanged() threshold must be positive` | Validation | HIGH |
| 416 | `whenChanged() invalid value` | Validation | HIGH |
| 515 | `Unknown condition type: ${condition.type}` | Unsupported | CRITICAL |
| 600 | `Invalid rc array syntax: ${target}` | RC Access | HIGH |
| 608 | `RC channel ${channel} out of range` | RC Access | HIGH |
| 633 | `Unknown assignment target: ${target}` | Assignment | CRITICAL |
| 666 | `Unknown operand: ${value}` | Operand | CRITICAL |
| 695 | `Math.abs() requires exactly 1 argument` | Math | MEDIUM |
| 720 | `Unsupported function call` | Unsupported | MEDIUM |
| 740 | `Unsupported expression type` | Unsupported | MEDIUM |

**Total: 21 conversions**

## Summary of Changes

### Files to Modify

1. **codegen.js** (~250 lines of changes)
   - Add `errors`, `warnings`, `currentNode` properties
   - Add `addError()`, `addWarning()`, `getLineNumber()` methods
   - Modify `generate()` to throw on errors at end
   - Replace 21 `console.warn()` calls with `addError()`

2. **Test file** (NEW - ~200 lines)
   - Create manual test scenarios
   - Test each error type
   - Verify error messages are correct
   - Verify line numbers are included
   - Verify multiple errors shown together

3. **Documentation** (~50 lines)
   - Update project docs
   - Add error codes reference
   - Document error handling flow

## Estimated Time

- Step 1 (Infrastructure): 30 min
- Step 2 (Critical errors): 1 hour
- Step 3 (Validation errors): 1 hour
- Step 4 (Remaining errors): 30 min
- Step 5 (Testing): 1 hour
- Documentation: 30 min
- **Total: 4.5 hours**

## Design Questions & Decisions

### Q1: Error vs Warning distinction?

**Decision:** All should be errors (block transpilation)
- Rationale: All these cases produce incorrect/incomplete output
- Warnings are for things like "uninitialized gvar" (analyzer already handles)
- Better to block than allow corrupted logic

### Q2: Fuzzy matching for suggestions?

**Decision:** Defer to future enhancement
- Nice to have, not critical
- Can add later without breaking changes
- Focus on getting errors visible first

### Q3: Line number fallback?

**Decision:** Show error without line if unavailable
- Better than not showing error at all
- Most errors should have line numbers from AST
- Can improve tracking in future if needed

### Q4: Error codes for programmatic handling?

**Decision:** Yes, include them
- Low cost to add now
- Enables future tooling
- Useful for automated testing
- Can link to documentation

## Ready for Implementation

✅ All design decisions made
✅ Error messages written
✅ Implementation strategy defined
✅ Test cases documented
✅ No backward compatibility concerns
✅ Estimated timeline: 4.5 hours

**Next:** Proceed to Phase 3 (Implementation)
