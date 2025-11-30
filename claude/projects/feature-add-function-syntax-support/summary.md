# Project: Add Transpiler Support for Function Syntax

**Status:** 📋 TODO
**Priority:** Medium-High
**Type:** Feature Enhancement
**Created:** 2025-11-24

## Overview

Add support for traditional JavaScript function syntax to the transpiler, allowing users to write `function() {}` and `function name() {}` in addition to the currently supported arrow function syntax `() => {}`.

## Problem

The transpiler currently only supports arrow function syntax for callbacks and conditions. This limits user flexibility and may be confusing for users more familiar with traditional function syntax.

**Current behavior:**
```javascript
// SUPPORTED: Arrow functions
on.always(() => {
  gvar[0] = 100;
});

edge(() => flight.yaw > 1800, () => { ... }, () => { ... });

// NOT SUPPORTED: Traditional functions
on.always(function() {  // ❌ Transpiler error or silent failure
  gvar[0] = 100;
});

edge(function() { return flight.yaw > 1800; }, function() { ... }, function() { ... });

// POSSIBLY NOT SUPPORTED: Named functions
function checkYaw() {  // ❌ May not work
  return flight.yaw > 1800;
}
edge(checkYaw, ...);
```

**User impact:**
- Users familiar with traditional JavaScript syntax can't use it
- Documentation shows arrow functions only
- Inconsistent with standard JavaScript
- Limits code reusability (can't define named helper functions)

## Proposed Solution

Extend the transpiler parser and codegen to recognize and transpile traditional function syntax:

1. **Anonymous functions:** `function() { ... }`
2. **Named functions:** `function name() { ... }`
3. **Function declarations:** `function name() { ... }` at top level
4. **Function expressions:** `const fn = function() { ... }`
5. **Function references:** Using function name as callback

### Scope

**Must Support:**
- Anonymous function expressions in helper calls
- Function declarations for reusability
- Function references as callbacks

**Examples to Support:**
```javascript
// Example 1: Anonymous function in helper
on.always(function() {
  override.throttle = 1500;
});

// Example 2: Named function declaration + reference
function isHighYaw() {
  return flight.yaw > 1800;
}

edge(isHighYaw, function() {
  gvar[0] = 1;
}, function() {
  gvar[0] = 0;
});

// Example 3: Function expression
const resetThrottle = function() {
  override.throttle = 1500;
};

on.always(resetThrottle);

// Example 4: Traditional if/else with functions
function checkAltitude() {
  if (flight.altitude > 100) {
    gvar[1] = 1;
  }
}

on.always(checkAltitude);
```

## Technical Approach

### Phase 1: Parser Updates

**Location:** `js/transpiler/transpiler/parser.js`

**Current state:**
- Parser uses Acorn to parse JavaScript
- Acorn already recognizes function syntax
- Need to ensure function nodes are preserved in AST

**Changes needed:**
- Verify Acorn options include function syntax
- Ensure function declarations are captured
- Preserve function names in AST
- Handle both `FunctionDeclaration` and `FunctionExpression` node types

**AST node types:**
```javascript
// FunctionDeclaration
{
  type: 'FunctionDeclaration',
  id: { type: 'Identifier', name: 'myFunction' },
  params: [...],
  body: { type: 'BlockStatement', body: [...] }
}

// FunctionExpression (anonymous)
{
  type: 'FunctionExpression',
  id: null,  // or { name: '...' } if named
  params: [...],
  body: { type: 'BlockStatement', body: [...] }
}

// ArrowFunctionExpression (current support)
{
  type: 'ArrowFunctionExpression',
  params: [...],
  body: { ... }
}
```

### Phase 2: Semantic Analyzer Updates

**Location:** `js/transpiler/transpiler/analyzer.js`

**Current state:**
- Analyzer validates arrow functions
- Checks scope and variable references
- May need to handle function declarations in scope

**Changes needed:**
- Recognize function declarations and add to scope
- Allow function names as valid identifiers
- Validate function references (function must be declared)
- Handle hoisting behavior (functions available before declaration)
- Validate function bodies same as arrow function bodies

**Scope handling:**
```javascript
// Function declarations should be added to scope
function myFunc() { ... }  // Add 'myFunc' to scope

// Then allow references
edge(myFunc, ...);  // Valid - 'myFunc' is in scope
```

### Phase 3: Code Generator Updates

**Location:** `js/transpiler/transpiler/codegen.js`

**Current state:**
- Codegen converts arrow functions to logic conditions
- `arrow_function_helper.js` may assist with this

**Changes needed:**
- Recognize `FunctionDeclaration` nodes
- Recognize `FunctionExpression` nodes
- Convert function body to logic conditions (same as arrow functions)
- Handle function name references
- Generate same logic condition output

**Code generation:**
```javascript
// Input: function() { gvar[0] = 1; }
// Output: Same as arrow function would generate

// Input: function name() { ... }
// Store name → logic mapping
// When referenced: edge(name, ...) → use stored logic
```

### Phase 4: Helper Function Support

**Consideration:** Named functions as helpers/reusability

**Option A: Inline expansion**
```javascript
// Input
function setThrottle() {
  override.throttle = 1500;
}
on.always(setThrottle);

// Output: Inline the function body wherever called
// Logic condition 0: always
// Logic condition 0 action: override.throttle = 1500
```

**Option B: Function call tracking**
```javascript
// Generate separate logic conditions for functions
// Call functions via special operand (if INAV supports)
// May not be possible with current INAV firmware
```

**Recommendation:** Option A (inline expansion) - simpler and works with current firmware.

### Phase 5: Testing

**Test cases:**
1. Anonymous function in `on.always()`
2. Anonymous function in helper calls (`edge`, `sticky`, etc.)
3. Named function declaration + reference
4. Function expression assigned to variable
5. Multiple functions with same logic
6. Function with parameters (if applicable)
7. Nested functions (if applicable)
8. Function hoisting behavior

## Implementation Details

### Function Body Transpilation

Functions should transpile identically to arrow functions:

```javascript
// These should produce identical logic conditions:
on.always(() => { gvar[0] = 1; });
on.always(function() { gvar[0] = 1; });

// Both should generate:
// Logic condition 0: always
// Logic condition 0 action: set gvar[0] to 1
```

### Function Name Tracking

For named functions, maintain a map:

```javascript
const functionMap = new Map();

// When encountering function declaration:
function checkAlt() { return flight.altitude > 100; }
// Store: functionMap.set('checkAlt', <function AST node>)

// When encountering function reference:
edge(checkAlt, ...)
// Lookup: functionMap.get('checkAlt')
// Transpile the stored function body
```

### Hoisting Behavior

JavaScript hoists function declarations:

```javascript
// This is valid JavaScript:
edge(checkYaw, ...);  // Reference before declaration

function checkYaw() {  // Declaration later
  return flight.yaw > 1800;
}
```

**Decision needed:**
- **Option 1:** Support hoisting (two-pass analysis)
- **Option 2:** Require forward declarations (simpler)
- **Recommendation:** Option 2 initially, Option 1 if users request it

### Error Handling

**New error cases:**
- Function declared but never used (warning?)
- Function referenced but not declared (error)
- Function with unsupported features (parameters, closures)
- Recursive functions (error - not supported)

## Benefits

1. **Improved usability:** Users can write JavaScript they're familiar with
2. **Code reusability:** Named functions for common logic
3. **Better readability:** Named functions are self-documenting
4. **Consistency:** Standard JavaScript syntax
5. **Less confusing:** Beginners often know `function` before arrow functions

## Challenges

### 1. Function Parameters

Traditional functions can have parameters:

```javascript
function setGvar(value) {  // Has parameter
  gvar[0] = value;
}
```

**Decision:**
- **Option A:** Support parameters (complex - need to track and substitute)
- **Option B:** Error on functions with parameters
- **Recommendation:** Option B initially - INAV logic conditions don't have function call semantics

### 2. Closures

Functions can capture outer scope:

```javascript
const threshold = 1800;
function check() {
  return flight.yaw > threshold;  // Captures 'threshold'
}
```

**Decision:**
- **Option A:** Support closures (complex - need scope analysis)
- **Option B:** Error on closure usage
- **Recommendation:** Option B initially - keep transpiler simple

### 3. Return Statements

Traditional functions use `return`, arrow functions can be implicit:

```javascript
// Arrow function (implicit return)
const check = () => flight.yaw > 1800;

// Traditional function (explicit return)
function check() {
  return flight.yaw > 1800;
}
```

**Solution:** Parser already handles both - codegen should extract the return value.

### 4. `this` Binding

Arrow functions and traditional functions handle `this` differently.

**Decision:** Not applicable - INAV transpiler doesn't use `this`, so no special handling needed.

### 5. Function Scope

Functions create their own scope:

```javascript
function outer() {
  let x = 1;  // Local to outer
  function inner() {
    let y = 2;  // Local to inner
    return x + y;  // Can access outer scope
  }
  return inner();
}
```

**Decision:**
- **Option A:** Support nested scopes (complex)
- **Option B:** Flatten all scopes (simpler but may cause issues)
- **Option C:** Error on nested functions
- **Recommendation:** Option C initially - keep transpiler simple

## Files to Modify

### Primary Files
- `js/transpiler/transpiler/parser.js` - Parse function syntax
- `js/transpiler/transpiler/analyzer.js` - Analyze function declarations/references
- `js/transpiler/transpiler/codegen.js` - Generate logic from functions
- `js/transpiler/transpiler/arrow_function_helper.js` - May need to rename or extend

### Testing
- Create new test file or extend existing tests
- Test each function syntax variant
- Test error cases

### Documentation
- Update transpiler docs to show function syntax
- Add examples with traditional functions
- Document limitations (no parameters, no closures, etc.)

## Success Criteria

- [ ] Anonymous functions work: `on.always(function() { ... })`
- [ ] Named function declarations work: `function name() { ... }`
- [ ] Function references work: `edge(functionName, ...)`
- [ ] Function expressions work: `const fn = function() { ... }`
- [ ] Generated logic conditions are correct
- [ ] Error messages are clear for unsupported features
- [ ] Existing arrow function code continues to work (no regression)
- [ ] Documentation updated with examples

## Estimated Time

**Total:** ~6-8 hours

- Phase 1 (Parser): 1 hour
- Phase 2 (Analyzer): 2 hours
- Phase 3 (Codegen): 2-3 hours
- Phase 4 (Helpers): 1 hour
- Phase 5 (Testing): 1-2 hours

## Priority Justification

**Medium-High Priority:**
- Improves usability significantly
- Common user request (likely)
- Relatively straightforward implementation
- High user impact for moderate effort
- Builds on existing transpiler work

**Not Critical:**
- Arrow functions already work
- Workaround exists (use arrow functions)
- No safety issues

## Related Work

- **refactor-commonjs-to-esm** - May affect import syntax but not function syntax
- **improve-transpiler-error-reporting** - Should show clear errors for unsupported function features
- **fix-transpiler-api-mismatches** - Fixed operand values that functions will use

## Future Enhancements

- Support for function parameters (with inlining/substitution)
- Support for closures (with scope capture)
- Support for generator functions (if useful)
- Support for async functions (unlikely to be useful in INAV)
- Function optimization (inline single-use functions)
- Dead code elimination (remove unused functions)

## Notes

- This is primarily a syntax sugar feature - functions and arrow functions should generate identical logic
- Keep implementation simple - error on advanced features rather than trying to support everything
- Prioritize common use cases (anonymous functions in helpers, named functions for reuse)
- Consider what JavaScript beginners would expect to work

## Examples After Implementation

```javascript
// Example 1: Simple anonymous function
on.always(function() {
  override.throttle = 1500;
});

// Example 2: Named function for reusability
function armingCheck() {
  return flight.isArmed && flight.altitude > 10;
}

on.interval(100, armingCheck, function() {
  gvar[0] = 1;
});

// Example 3: Multiple helpers using same check
function highYaw() {
  return flight.yaw > 1800;
}

edge(highYaw,
  function() { gvar[1] = 1; },
  function() { gvar[1] = 0; }
);

sticky(highYaw,
  function() { gvar[2] = 1; },
  function() { gvar[2] = 0; }
);

// Example 4: Mix of arrow and traditional
on.always(() => {
  if (flight.altitude > 100) {
    override.vtx.power = 4;
  }
});

on.always(function() {
  if (flight.altitude <= 100) {
    override.vtx.power = 1;
  }
});
```

All of these should transpile to valid INAV logic conditions.
