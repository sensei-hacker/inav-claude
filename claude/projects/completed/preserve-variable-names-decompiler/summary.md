# Preserve Variable Names in Decompiler

**Status:** 📝 PLANNED
**Type:** Feature Enhancement
**Priority:** High
**Created:** 2025-11-24
**Branch:** programming_transpiler_js

## Problem

When users write JavaScript code with variables, those variable names disappear between sessions:

**Example code:**
```javascript
const { flight, override, rc, gvar, edge } = inav;

let distance_to_ground = flight.agl;  // Lost on reload
var msl = flight.altitude;             // Name lost, only gvar[1] remains

gvar[0] = msl - distance_to_ground;
```

**What happens:**

1. **Transpiler phase:**
   - `let distance_to_ground = flight.agl;` → Expression substituted inline wherever used
   - `var msl = flight.altitude;` → Allocated to gvar[1], name replaced with gvar[1]
   - No variable names stored in logic conditions sent to FC

2. **Save to FC:**
   - Only logic conditions saved (no variable names)
   - User closes configurator

3. **Reload from FC:**
   - Decompiler reads logic conditions
   - `let` variables: Completely gone (expressions are inline)
   - `var` variables: Appear as anonymous `gvar[1] = flight.altitude;` (name lost)

**User experience:** Variables disappear or lose meaningful names between sessions. Very confusing!

## Proposed Solution

Store a mapping of variable names to their definitions, then use this mapping during decompilation to reconstruct variable declarations.

### Storage Strategy

**Option A: settingsCache.js (Recommended)**
- Use existing `./js/settingsCache.js` module
- Automatically scoped per FC (target + version + build)
- API: `settingsCache.get(key)` / `settingsCache.set(key, value)`

**Option B: electron-store directly**
- Direct access to electron-store
- More manual management

**Recommendation:** Use settingsCache.js for consistency with existing code.

### What to Store

**Variable mapping object:**
```javascript
{
  "let_variables": {
    "distance_to_ground": "flight.agl",
    // Or store more metadata:
    "distance_to_ground": {
      "expression": "flight.agl",
      "operands": [/* INAV operands */],
      "type": "let"
    }
  },
  "var_variables": {
    "msl": {
      "gvar": 1,
      "expression": "flight.altitude",
      "operands": [/* INAV operands */]
    }
  }
}
```

**Storage key:** `"javascript_variables"` or `"transpiler_variable_map"`

### When to Store

**During transpilation (codegen phase):**
1. VariableHandler already tracks all variables
2. Before generating final logic conditions, extract variable map
3. Store to settingsCache: `settingsCache.set('javascript_variables', variableMap)`

### When to Retrieve

**During decompilation:**
1. Load variable map: `const variableMap = settingsCache.get('javascript_variables')`
2. When generating JavaScript from logic conditions:
   - Check if operand pattern matches a `let` variable expression
   - Check if gvar index matches a `var` variable
   - If match found, generate variable declaration with original name

### Implementation Details

#### In Transpiler (codegen.js)

After code generation, before returning:
```javascript
export(ast, variableHandler) {
  // ... existing code generation ...

  // Store variable mapping
  if (variableHandler) {
    const variableMap = this.buildVariableMap(variableHandler);
    // Store via settingsCache (imported from tabs)
    // Or pass back to caller to store
    return { commands: this.commands, variableMap: variableMap };
  }

  return { commands: this.commands };
}

buildVariableMap(variableHandler) {
  const map = {
    let_variables: {},
    var_variables: {}
  };

  // Extract from variableHandler
  for (const [name, varInfo] of variableHandler.variables.entries()) {
    if (varInfo.type === 'let' || varInfo.type === 'const') {
      map.let_variables[name] = {
        expression: varInfo.expressionSource || this.astToString(varInfo.expression),
        ast: varInfo.expression  // May need serialization
      };
    } else if (varInfo.type === 'var') {
      map.var_variables[name] = {
        gvar: varInfo.gvarIndex,
        expression: varInfo.expressionSource || this.astToString(varInfo.expression)
      };
    }
  }

  return map;
}
```

#### In Tab (javascript_programming.js)

When transpiling and saving:
```javascript
import settingsCache from './js/settingsCache.js';

// After transpilation
const result = transpile(code);
if (result.variableMap) {
  settingsCache.set('javascript_variables', result.variableMap);
}
```

When loading from FC:
```javascript
// Before decompilation
const variableMap = settingsCache.get('javascript_variables') || { let_variables: {}, var_variables: {} };
const code = decompile(logicConditions, variableMap);
```

#### In Decompiler (decompiler.js)

Accept variable map as parameter:
```javascript
decompile(logicConditions, variableMap = null) {
  // ... existing decompilation ...

  // For each logic condition being decompiled:
  // 1. Check if operand pattern matches a let variable
  // 2. Check if gvar index matches a var variable
  // 3. If match, generate variable declaration instead of inline expression
}

// Helper to reconstruct let variables
reconstructLetVariables(variableMap) {
  const declarations = [];
  for (const [name, info] of Object.entries(variableMap.let_variables || {})) {
    declarations.push(`let ${name} = ${info.expression};`);
  }
  return declarations;
}

// Helper to check if gvar matches a var variable
getVarNameForGvar(gvarIndex, variableMap) {
  for (const [name, info] of Object.entries(variableMap.var_variables || {})) {
    if (info.gvar === gvarIndex) {
      return name;
    }
  }
  return null;
}
```

### Matching Strategy

**For `let` variables:**
- Store the operand pattern or expression AST
- When decompiling, if logic condition operands match the pattern, reconstruct variable
- Challenge: Expressions may be used in multiple places (by design)
- Solution: Generate variable declarations at top of decompiled code if any usage detected

**For `var` variables:**
- Simpler: gvar index is unique identifier
- When decompiling `gvar[N]`, check if N has a stored name
- Replace `gvar[N]` with variable name throughout code

### Edge Cases

1. **Variable map out of sync with FC:**
   - User edited logic conditions directly
   - Solution: Validate before using, fall back to generic names

2. **Multiple sessions with different variable names:**
   - Last write wins (settingsCache stores per-FC)

3. **User clears settings:**
   - Variables revert to generic representation
   - User can re-declare with original code

4. **Expression used in multiple places:**
   - Generate single `let` declaration at top
   - Use variable name in all matching locations

## Test Cases

### Test 1: Simple let variable
```javascript
let altitude = flight.altitude;
gvar[0] = altitude * 2;
```

**Expected after reload:**
- Variable name `altitude` preserved
- Code appears same as original

### Test 2: Multiple let variables
```javascript
let agl = flight.agl;
let msl = flight.altitude;
let diff = msl - agl;
```

**Expected after reload:**
- All three variable names preserved
- Expressions intact

### Test 3: var (global) variable
```javascript
var counter = 0;
counter = counter + 1;
```

**Expected after reload:**
- Variable name `counter` preserved
- Shows as `var counter = 0;` not `gvar[0] = 0;`

### Test 4: Mixed variables
```javascript
let distance = flight.agl;
var altitude_cache = flight.altitude;
gvar[0] = altitude_cache - distance;
```

**Expected after reload:**
- Both variable names preserved
- Code appears same as original

### Test 5: Variable map cleared
```javascript
// Original: let altitude = flight.altitude;
// After settings cleared: logic conditions decompiled without variable names
```

**Expected:**
- Falls back to generic representation
- No errors, still functional

## Implementation Plan

### Phase 1: Design and Storage (2-3 hours)
- Design variable map structure
- Implement storage in transpiler/codegen
- Add settingsCache integration
- Extract variable info from VariableHandler

### Phase 2: Decompiler Integration (3-4 hours)
- Update decompiler to accept variable map
- Implement variable reconstruction for `let`
- Implement variable name lookup for `var`
- Handle matching and substitution

### Phase 3: Tab Integration (1-2 hours)
- Update javascript_programming.js to store map after transpile
- Update to load map before decompile
- Test round-trip (transpile → save → reload → decompile)

### Phase 4: Testing (2-3 hours)
- Unit tests for variable map storage/retrieval
- Integration tests for round-trip
- Test edge cases
- Test with real examples

### Phase 5: Documentation (1 hour)
- Update user documentation
- Document storage format
- Note limitations

**Total:** 9-13 hours

## Success Criteria

- [ ] Variable names preserved between sessions
- [ ] `let` variables appear with original names after reload
- [ ] `var` variables show meaningful names instead of `gvar[N]`
- [ ] All existing tests still pass
- [ ] New tests for variable preservation pass
- [ ] Works across configurator restarts
- [ ] Gracefully handles missing or invalid variable maps

## Alternative Approaches

### Alternative 1: Store in Logic Condition Comments
- Use LC "comment" field to store variable metadata
- **Pros:** Lives with the LC data on FC
- **Cons:** Comment field may not be available, limited space

### Alternative 2: Store as Special Logic Conditions
- Create dummy LCs that store variable info
- **Pros:** Travels with configuration
- **Cons:** Wastes LC slots, hacky

### Alternative 3: User-editable mapping file
- Let users manually edit variable names
- **Pros:** User control
- **Cons:** More complex UX, error-prone

**Recommendation:** Stick with proposed solution (settingsCache)

## Notes

- This is a quality-of-life improvement for users
- Makes JavaScript programming mode more practical
- Preserves user intent (meaningful variable names)
- Storage is local to configurator (doesn't affect FC)
- Should not impact transpiler performance
- Decompiler already has round-trip challenges; this improves fidelity

## Related Work

- Depends on VariableHandler (already implemented)
- Should work with existing transpiler/decompiler pipeline
- Complements JavaScript variables feature
