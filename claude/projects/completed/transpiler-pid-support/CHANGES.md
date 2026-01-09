# Transpiler Decompiler Changes

Track changes made so documentation and examples can be updated.

## Decompiler Output Format Changes

### 1. STICKY - Named parameters
**Before:**
```javascript
sticky(() => onCondition, () => offCondition, () => {
  // body
});
```

**After:**
```javascript
sticky({
  on: () => onCondition,
  off: () => offCondition
}, () => {
  // body
});
```

### 2. EDGE - Simplified syntax (when used as activator with body)
**Before:**
```javascript
edge(() => condition, { duration: 100 }, () => {
  // body
});
```

**After:**
```javascript
edge(condition, 100, () => {
  // body
});
```

**When referenced inline:** `edge(condition, 100)`

### 3. DELAY - Simplified syntax
**Before:**
```javascript
delay(() => condition, { duration: 100 }, () => {
  // body
});
```

**After:**
```javascript
delay(condition, 100, () => {
  // body
});
```

**When referenced inline:** `delay(condition, 100)`

### 4. DELTA - Function call syntax
**Before:** `/* delta(value, threshold) */ true`
**After:** `delta(value, threshold)`

**When used as activator with body:**
```javascript
delta(value, threshold, () => {
  // body
});
```

### 5. STICKY - Variable + if style (all stickys)
**Before:** Callback style mixed with inline references
```javascript
sticky({
  on: () => condition1,
  off: () => condition2
}, () => {
  // body
});
// Referenced elsewhere as logicCondition[25]
```

**After:** All stickys rendered as variable assignment + if block
```javascript
// Declaration at top
let latch1; // logicCondition[2] - sticky/timer state

// Definition clearly shows what sets/resets the latch
latch1 = sticky({
  on: () => condition1,
  off: () => condition2
});
if (latch1) {
  // body
}

// Referenced elsewhere as latch1
if (!latch1) { ... }
```

**Benefits:**
- Consistent style for all stickys
- Clear separation of "what sets the state" vs "what happens when true"
- Variables available for reference elsewhere
- Matches mental model of stateful latch

### 6. Expression hoisting for deeply nested calls
Deeply nested function calls are automatically hoisted to variables for readability.

**Before:**
```javascript
gvar[0] = (Math.min(110, Math.max(0, Math.round((rc[12] - 1000) * 110 / 1000))) * 28);
override.throttle = Math.max(Math.min(1800, ((pid[3].output + 3000) / 2)), Math.max(1250, Math.min(1800, ((pid[3].output + 3000) / 2))));
```

**After:**
```javascript
let rounded = Math.round((rc[12] - 1000) * 110 / 1000);
gvar[0] = Math.min(110, Math.max(0, rounded)) * 28;

let clamped = Math.min(1800, ((pid[3].output + 3000) / 2));
override.throttle = Math.max(clamped, Math.max(1250, clamped));
```

Features:
- Triggers when nesting depth exceeds 3
- Descriptive variable names: `rounded`, `clamped`, `bounded`, etc.
- Deduplication: identical expressions reuse the same variable
- Removes superfluous outer parentheses

### 7. Arithmetic simplification
- `x + 0` → `x`
- `x - 0` → `x`
- `x * 1` → `x`
- `x / 1` → `x`
- `x * 0` → `0`

### 7. NOT operator precedence
**Before:** `!complex expression` (wrong precedence)
**After:** `!(complex expression)`

### 8. GVAR action references
**Before:** `logicCondition[24]` (for GVAR_SET/INC/DEC)
**After:** `gvar[0]` (the actual variable)

---

## Compiler Changes Implemented

The following compiler changes were implemented to support full round-trip decompile → recompile:

### 9. Sticky Assignment Syntax (IMPLEMENTED)
The compiler now accepts variable assignment syntax for sticky:

```javascript
var latch1;
latch1 = sticky({
  on: () => flight.altitude > 100,
  off: () => flight.altitude < 50
});
if (latch1) {
  gvar[0] = 1;
}
```

**Implementation:**
- `parser.js`: New `StickyAssignment` node type for `latch1 = sticky({...})` assignments
- `codegen.js`: New `generateStickyAssignment()` method, `latchVariables` Map to track variable → LC index
- `condition_generator.js`: New `generateIdentifier()` method to resolve latch variables in conditions

### 10. Flight Mode API (IMPLEMENTED - separate commit)
The `flight.mode.*` nested object was added to `flight.js` API definition (commit `dda0d9842`).

### 11. edge() and delta() in Conditions (IMPLEMENTED)
The compiler now supports `edge()` and `delta()` inside sticky conditions:

```javascript
latch1 = sticky({
  on: () => flight.altitude > 100,
  off: () => edge(rc[4], 200) || delta(rc[5], 90) || flight.gpsValid === 0
});
```

**Implementation:**
- `condition_generator.js`: Added `edge()` and `delta()` handlers in `generateCall()`
- `arrow_function_helper.js`: Added `CallExpression` handling in `transformCondition()`
- `codegen.js`: Modified `generateAction()` to handle `StickyAssignment` inside if blocks

### 12. Nested StickyAssignment Handling (IMPLEMENTED)
Sticky assignments inside if bodies are now properly processed:

```javascript
if (someCondition) {
  latch1 = sticky({ on: () => x, off: () => y });
  if (latch1) {
    gvar[0] = 1;
  }
}
```

### 13. Removed Math.round() from Decompiler Output (IMPLEMENTED)
INAV logic conditions don't have a ROUND operation. The decompiler was outputting `Math.round()` for `MAP_INPUT` and `MAP_OUTPUT` operations, but this wasn't compilable. Fixed by removing `Math.round()` since INAV integer division already truncates.

**Changes:**
- `condition_decompiler.js`: Removed `Math.round()` from `handleMapInput()` and `handleMapOutput()`
- `action_decompiler.js`: Removed `Math.round/floor/ceil` from hoisting pattern and nameMap

### 14. Expression Generator Handles Literals (IMPLEMENTED)
Added support for `Literal`, `Identifier`, and `MemberExpression` types in expression_generator.js, allowing complex nested expressions like `Math.min(110, Math.max(0, expr)) * 28` to compile correctly.

### 15. Parser Preserves CallExpression in Arithmetic (IMPLEMENTED)
When parsing arithmetic expressions like `Math.min(...) * 28`, the parser now preserves the full AST for CallExpression nodes instead of trying to extract just an identifier string.

## Round-Trip Status

**NOW WORKS:**
- `var latch1 = sticky({...}); if (latch1) {...}` - ✅ Full round-trip support
- `flight.mode.poshold` - ✅ Full round-trip support (commit `dda0d9842`)
- `edge(condition, duration)` inside sticky conditions - ✅ Full round-trip support
- `delta(value, threshold)` inside sticky conditions - ✅ Full round-trip support
- Nested sticky assignments inside if blocks - ✅ Full round-trip support
- Complex nested Math.min/max expressions - ✅ Full round-trip support
- `MAP_INPUT` and `MAP_OUTPUT` operations - ✅ Full round-trip support (without Math.round)

## Test Updates

Updated tests to match new tree-based decompiler behavior:

1. **decompiler.test.cjs** - Warning tests now use invalid operand type (99) instead of PID (6), since PID is now supported
2. **chained_conditions.test.cjs** - Updated to expect nested if blocks instead of && chains, and conditions without actions are now skipped

### Test Results (125 tests pass)

All `run_*.cjs` test runners pass (125 tests total across 13 suites).

**Tests not yet verified** (Jest ESM/CommonJS conflict prevents running):
- `variable_map.test.cjs`
- `const_support.test.cjs`

---

## Files Modified

**Decompiler:**
- `js/transpiler/transpiler/decompiler.js`
- `js/transpiler/transpiler/condition_decompiler.js`
- `js/transpiler/transpiler/action_decompiler.js`

**Compiler (for round-trip support):**
- `js/transpiler/transpiler/parser.js` - Added `StickyAssignment` node type, preserve CallExpression in arithmetic
- `js/transpiler/transpiler/codegen.js` - Added `generateStickyAssignment()`, `latchVariables` Map, `StickyAssignment` handling in `generateAction()`
- `js/transpiler/transpiler/condition_generator.js` - Added `generateIdentifier()` for latch resolution, `edge()` and `delta()` support in `generateCall()`
- `js/transpiler/transpiler/arrow_function_helper.js` - Added `CallExpression` handling in `transformCondition()`
- `js/transpiler/transpiler/expression_generator.js` - Added `Literal`, `Identifier`, `MemberExpression` handling
- `js/transpiler/api/definitions/flight.js` - Added `mode` nested object (separate commit)

**Decompiler (for round-trip support):**
- `js/transpiler/transpiler/condition_decompiler.js` - Removed `Math.round()` from MAP_INPUT/MAP_OUTPUT
- `js/transpiler/transpiler/action_decompiler.js` - Removed `Math.round/floor/ceil` from hoisting
