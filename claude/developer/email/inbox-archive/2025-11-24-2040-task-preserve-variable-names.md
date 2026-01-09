# Task Assignment: Preserve Variable Names in Decompiler

**Date:** 2025-11-24 20:40
**Project:** preserve-variable-names-decompiler
**Priority:** High
**Estimated Effort:** 9-13 hours
**Branch:** programming_transpiler_js

## Task

Implement variable name preservation so that `let` and `var` variable names persist between configurator sessions.

## Problem

Variable names currently disappear when reloading from flight controller:

**User writes:**
```javascript
const { flight, override, rc, gvar, edge } = inav;

let distance_to_ground = flight.agl;
var msl = flight.altitude;

gvar[0] = msl - distance_to_ground;
```

**After save → close configurator → reopen → load from FC:**
```javascript
// let variable completely gone (expression was inlined)
// var variable lost name:
gvar[1] = flight.altitude;  // was "var msl"

gvar[0] = gvar[1] - flight.agl;  // unreadable!
```

**This is very confusing for users!**

## Root Cause

1. Transpiler substitutes `let` variables inline (by design for efficiency)
2. Variable names are not stored in logic conditions sent to FC
3. Decompiler has no way to recover original variable names
4. Result: Variables appear as anonymous expressions or gvar indices

## Solution

Store a mapping of variable names to their definitions locally (using settingsCache), then use this mapping during decompilation to reconstruct variable declarations.

### Storage Approach

Use existing `./js/settingsCache.js` module:
- Already implemented and integrated
- Automatically scoped per FC (target + version + build)
- Simple API: `settingsCache.get(key)`, `settingsCache.set(key, value)`

**Variable map structure:**
```javascript
{
  "let_variables": {
    "distance_to_ground": {
      "expression": "flight.agl",
      "type": "let"
    }
  },
  "var_variables": {
    "msl": {
      "gvar": 1,
      "expression": "flight.altitude"
    }
  }
}
```

**Storage key:** `'javascript_variables'`

## Implementation Overview

### Phase 1: Generate Variable Map in Transpiler

**File:** `js/transpiler/transpiler/codegen.js`

Add method to extract variable info from VariableHandler:

```javascript
buildVariableMap(variableHandler) {
  const map = {
    let_variables: {},
    var_variables: {}
  };

  if (!variableHandler || !variableHandler.variables) {
    return map;
  }

  for (const [name, varInfo] of variableHandler.variables.entries()) {
    if (varInfo.type === 'let' || varInfo.type === 'const') {
      map.let_variables[name] = {
        expression: this.astToExpressionString(varInfo.expression),
        type: varInfo.type
      };
    } else if (varInfo.type === 'var') {
      map.var_variables[name] = {
        gvar: varInfo.gvarIndex,
        expression: this.astToExpressionString(varInfo.expression)
      };
    }
  }

  return map;
}
```

Update `export()` to return variable map in result.

### Phase 2: Store Variable Map in Tab

**File:** `tabs/javascript_programming.js`

After transpilation, store variable map:

```javascript
import settingsCache from './js/settingsCache.js';

// After transpile
const result = transpile(userCode);

if (result.variableMap) {
  settingsCache.set('javascript_variables', result.variableMap);
}
```

Before decompilation, load variable map:

```javascript
const variableMap = settingsCache.get('javascript_variables') || {
  let_variables: {},
  var_variables: {}
};

const decompiled = decompile(logicConditions, variableMap);
```

### Phase 3: Use Variable Map in Decompiler

**File:** `js/transpiler/transpiler/decompiler.js`

Update signature to accept variable map:

```javascript
export function decompile(logicConditions, variableMap = null) {
  // ...
}
```

**For var variables:**
- Look up gvar index in variable map
- Replace `gvar[N]` with original variable name throughout code
- Generate declaration: `var msl = flight.altitude;`

**For let variables:**
- Reconstruct declarations at top of code
- Use original variable names

```javascript
getVarNameForGvar(gvarIndex, variableMap) {
  if (!variableMap || !variableMap.var_variables) {
    return null;
  }

  for (const [name, info] of Object.entries(variableMap.var_variables)) {
    if (info.gvar === gvarIndex) {
      return name;
    }
  }

  return null;
}

reconstructLetVariables(variableMap) {
  const declarations = [];

  if (!variableMap || !variableMap.let_variables) {
    return declarations;
  }

  for (const [name, info] of Object.entries(variableMap.let_variables)) {
    const type = info.type || 'let';
    declarations.push(`${type} ${name} = ${info.expression};`);
  }

  return declarations;
}
```

## Expected Result

After implementation, the example code should survive round-trip:

**Original:**
```javascript
let distance_to_ground = flight.agl;
var msl = flight.altitude;
gvar[0] = msl - distance_to_ground;
```

**After save → reload → decompile:**
```javascript
let distance_to_ground = flight.agl;
var msl = flight.altitude;
gvar[0] = msl - distance_to_ground;
```

**Perfect preservation!**

## Alternative Approaches Welcome

If you have a better solution, document it and discuss with manager before implementing. The proposed approach is a suggestion, not a requirement.

**Alternative ideas to consider:**
- Store in logic condition comments (if available)
- Use different storage mechanism
- Different matching strategy for decompiler

## Testing Requirements

### Unit Tests

- [ ] Test variable map building from VariableHandler
- [ ] Test map serialization/storage
- [ ] Test map retrieval
- [ ] Test decompiler with variable map

### Integration Tests

- [ ] Test round-trip: transpile → store → decompile
- [ ] Test let variables preserved
- [ ] Test var variables show names
- [ ] Test mixed variables
- [ ] Test missing variable map (graceful degradation)

### Manual Tests

- [ ] Test in actual configurator
- [ ] Write code with variables
- [ ] Save to FC
- [ ] Close and reopen configurator
- [ ] Load from FC
- [ ] Verify variable names preserved

## Success Criteria

- [ ] Variable names preserved between sessions
- [ ] let variables appear with original names after reload
- [ ] var variables show names instead of gvar[N]
- [ ] All existing transpiler tests pass
- [ ] New tests for variable preservation pass
- [ ] No errors when variable map missing
- [ ] Works across configurator restarts

## Implementation Steps Summary

1. Design variable map structure
2. Extract variable info from VariableHandler in codegen
3. Store variable map via settingsCache in tab
4. Update decompiler signature to accept variable map
5. Implement var variable name lookup
6. Implement let variable reconstruction
7. Generate proper variable declarations in decompiled code
8. Write unit tests
9. Write integration tests
10. Manual testing
11. Handle edge cases (missing map, cleared cache, etc.)
12. Update documentation

## Estimated Time

- Phase 1 (Design & Storage): 2-3 hours
- Phase 2 (Decompiler Integration): 3-4 hours
- Phase 3 (Tab Integration): 1-2 hours
- Phase 4 (Testing): 2-3 hours
- Phase 5 (Documentation): 1 hour

**Total:** 9-13 hours

## Important Notes

- This is a quality-of-life improvement for users
- Makes JavaScript programming mode much more practical
- Storage is local to configurator (doesn't affect FC or firmware)
- Must handle missing/invalid variable maps gracefully
- Should not impact transpiler performance

## Completion

Send report to `claude/manager/inbox/` with:
- Summary of implementation
- Test results (all passing)
- Known limitations
- Sample before/after showing variable preservation

---

**Manager**
