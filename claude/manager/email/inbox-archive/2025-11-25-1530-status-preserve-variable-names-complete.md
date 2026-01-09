# Completion Report: Preserve Variable Names in Decompiler

**Date:** 2025-11-25
**Task Reference:** 2025-11-24-2040-task-preserve-variable-names.md
**Status:** Complete
**Branch:** programming_transpiler_js
**Commit:** 9ee7ce93

---

## Summary

Variable name preservation is fully implemented. Variable names now persist between configurator sessions using settingsCache.

---

## Implementation

### Phase 1: Generate Variable Map (codegen.js)

- `buildVariableMap()` - extracts variable info from VariableHandler.symbols
- `astToExpressionString()` - converts AST nodes back to source strings
- `generateTopLevelAssignment()` - support for bare gvar assignments

### Phase 2: Transpiler Integration (index.js)

- Added `variableMap` to transpiler result object

### Phase 3: Tab Integration (javascript_programming.js)

- Store variable map after transpile: `settingsCache.set('javascript_variables', ...)`
- Retrieve before decompile: `settingsCache.get('javascript_variables')`

### Phase 4: Decompiler Updates (decompiler.js)

- Accept `variableMap` parameter in `decompile()`
- `getVarNameForGvar()` - lookup variable name by gvar index
- `reconstructLetVariables()` / `reconstructVarVariables()` - generate declarations
- `isActionOperation()` - identify action vs condition operations
- `isVarInitialization()` - detect var inits to avoid duplication
- Updated `decompileOperand()` to substitute variable names for gvar references
- Updated `decompileAction()` for GVAR_SET/INC/DEC to use variable names
- Skip intermediate calculations (LCs only referenced as operands)
- Handle unconditional actions properly

---

## Test Results

**Node-based tests:** All pass

```
✅ Variable map building
✅ let variables preserved
✅ var variables show names instead of gvar[N]
✅ No duplicate var initializations
✅ Intermediate calculations skipped
✅ Graceful degradation without variable map
```

**Manual testing:** Passed (performed by user)

---

## Before/After Example

**Original code:**
```javascript
const { flight, gvar } = inav;

let distance_to_ground = flight.agl;
var msl = flight.altitude;

gvar[0] = msl - distance_to_ground;
```

**After save → reload → decompile (with variable map):**
```javascript
// INAV JavaScript Programming
// Decompiled from logic conditions

const { flight, override, rc, gvar } = inav;

// Variable declarations
let distance_to_ground = flight.agl;
var msl = flight.altitude;

gvar[0] = (msl - flight.agl);
```

**Without variable map (fallback):**
```javascript
gvar[7] = flight.altitude;
gvar[0] = (gvar[7] - flight.agl);
```

---

## Files Modified

1. `js/transpiler/transpiler/codegen.js`
2. `js/transpiler/transpiler/index.js` (previous commit)
3. `tabs/javascript_programming.js` (previous commit)
4. `js/transpiler/transpiler/decompiler.js`

## Files Created

1. `js/transpiler/transpiler/tests/test_variable_map.js`
2. `js/transpiler/transpiler/tests/test_toplevel_assignment.js`
3. `js/transpiler/transpiler/tests/variable_map.test.cjs`

---

## Known Limitations

1. Variable map stored locally per FC config - if settingsCache cleared, names lost
2. `let` variables appear in declarations but expressions remain inlined in logic body (by design)
3. Complex nested expressions may not reconstruct perfectly

---

## Success Criteria Met

- ✅ Variable names preserved between sessions
- ✅ let variables appear with original names after reload
- ✅ var variables show names instead of gvar[N]
- ✅ New tests for variable preservation pass
- ✅ No errors when variable map missing
- ✅ Works across configurator restarts
- ✅ Manual testing passed

---

## Recommendation

Ready to merge. Project can be archived.
