# TODO: Preserve Variable Names in Decompiler

**Created:** 2025-11-24
**Status:** Not yet assigned

---

## Phase 1: Design Variable Map Structure

- [ ] Design variable map JSON structure
  ```javascript
  {
    "let_variables": {
      "variableName": {
        "expression": "flight.agl",  // Source expression as string
        "type": "let"  // or "const"
      }
    },
    "var_variables": {
      "variableName": {
        "gvar": 1,  // Allocated gvar index
        "expression": "flight.altitude"
      }
    }
  }
  ```

- [ ] Document storage format in project files
- [ ] Consider serialization requirements (AST vs string)

**Deliverable:** Variable map design document

---

## Phase 2: Extract Variable Info from VariableHandler

- [ ] Review VariableHandler structure in `transpiler/variable_handler.js`
- [ ] Identify what info is available:
  - [ ] Variable name
  - [ ] Variable type (let/const/var)
  - [ ] Expression (AST or source)
  - [ ] Gvar index (for var)
- [ ] Design extraction method

**Deliverable:** Understanding of VariableHandler data

---

## Phase 3: Implement Variable Map Building in Codegen

- [ ] Open `js/transpiler/transpiler/codegen.js`
- [ ] Add method `buildVariableMap(variableHandler)`:
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

- [ ] Add helper `astToExpressionString(ast)` to convert AST to string
- [ ] Modify `export()` method to return variable map:
  ```javascript
  export(ast, variableHandler) {
    // ... existing generation ...

    const result = {
      commands: this.commands,
      errors: this.errorHandler.getErrors(),
      warnings: this.errorHandler.getWarnings()
    };

    if (variableHandler) {
      result.variableMap = this.buildVariableMap(variableHandler);
    }

    return result;
  }
  ```

- [ ] Test variable map generation

**Deliverable:** Codegen generates variable map

---

## Phase 4: Update Transpiler Index to Pass Variable Map

- [ ] Open `js/transpiler/index.js`
- [ ] Ensure `transpile()` returns variable map from codegen
- [ ] Verify variable map is in result object

**Deliverable:** Transpiler exports variable map

---

## Phase 5: Integrate settingsCache in JavaScript Programming Tab

- [ ] Open `tabs/javascript_programming.js`
- [ ] Import settingsCache:
  ```javascript
  import settingsCache from './js/settingsCache.js';
  ```

- [ ] Find transpile/save code section
- [ ] After successful transpile, store variable map:
  ```javascript
  const result = transpile(userCode);

  if (result.variableMap) {
    settingsCache.set('javascript_variables', result.variableMap);
    console.log('Variable map stored:', result.variableMap);
  }
  ```

- [ ] Find load/decompile code section
- [ ] Before decompile, load variable map:
  ```javascript
  const variableMap = settingsCache.get('javascript_variables') || {
    let_variables: {},
    var_variables: {}
  };

  const decompiled = decompile(logicConditions, variableMap);
  ```

**Deliverable:** Tab stores and retrieves variable map

---

## Phase 6: Update Decompiler Signature

- [ ] Open `js/transpiler/transpiler/decompiler.js`
- [ ] Add `variableMap` parameter to decompile function:
  ```javascript
  export function decompile(logicConditions, variableMap = null) {
    // Existing code...
  }
  ```

- [ ] Store variable map in decompiler state if needed
- [ ] Prepare for variable reconstruction

**Deliverable:** Decompiler accepts variable map

---

## Phase 7: Implement var Variable Name Reconstruction

- [ ] In decompiler, add helper method:
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
  ```

- [ ] When decompiling gvar references (e.g., `gvar[1]`):
  - [ ] Check if gvar index has stored name
  - [ ] If found, use variable name instead of `gvar[N]`
  - [ ] Generate variable declaration at top of code

- [ ] Track which var variables have been declared

**Deliverable:** var variables show original names

---

## Phase 8: Implement let Variable Reconstruction

- [ ] Add helper to generate let variable declarations:
  ```javascript
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

- [ ] Insert let variable declarations at top of decompiled code
- [ ] Consider: Should we detect if variable is actually used?
  - [ ] Option A: Always include (simpler)
  - [ ] Option B: Only include if expression detected in LCs (complex)
  - [ ] **Recommend:** Option A for initial implementation

**Deliverable:** let variables reconstructed in decompiled code

---

## Phase 9: Handle Variable Substitution in Expressions

- [ ] When decompiling expressions, check if they match let variables
- [ ] If operand pattern matches a let variable expression:
  - [ ] Option A: Use variable name instead of inline expression
  - [ ] Option B: Keep inline (since let is substituted anyway)
  - [ ] **Decision needed:** Check with manager

- [ ] For var variables:
  - [ ] Always replace `gvar[N]` with variable name if available

**Deliverable:** Variables used correctly in decompiled code

---

## Phase 10: Add Variable Declaration Section

- [ ] Structure decompiled code output:
  ```javascript
  // Variable declarations
  let distance_to_ground = flight.agl;
  var msl = flight.altitude;

  // Logic code
  gvar[0] = msl - distance_to_ground;
  ```

- [ ] Ensure proper formatting and spacing
- [ ] Add comment headers if helpful

**Deliverable:** Clean variable declaration section

---

## Phase 11: Unit Tests for Variable Map Storage

- [ ] Create test file: `variable_map_storage.test.cjs`
- [ ] Test variable map building:
  ```javascript
  test('buildVariableMap extracts let variables', () => {
    // Test with let variables
  });

  test('buildVariableMap extracts var variables', () => {
    // Test with var variables
  });

  test('buildVariableMap handles mixed variables', () => {
    // Test with both let and var
  });
  ```

- [ ] Test map serialization/deserialization

**Deliverable:** Unit tests for variable map building

---

## Phase 12: Integration Tests for Round-Trip

- [ ] Create test file: `variable_preservation.test.cjs`
- [ ] Test round-trip preservation:
  ```javascript
  test('let variables preserved after round-trip', () => {
    const code = 'let alt = flight.altitude; gvar[0] = alt;';
    const transpiled = transpile(code);
    // Simulate save to settingsCache
    const decompiled = decompile(transpiled.commands, transpiled.variableMap);
    // Verify 'alt' appears in decompiled code
  });

  test('var variables show names not gvar indices', () => {
    const code = 'var counter = 0; counter = counter + 1;';
    const transpiled = transpile(code);
    const decompiled = decompile(transpiled.commands, transpiled.variableMap);
    // Verify 'counter' appears, not 'gvar[N]'
  });
  ```

**Deliverable:** Integration tests pass

---

## Phase 13: Manual Testing

- [ ] Test in actual configurator:
  - [ ] Write code with let variables
  - [ ] Transpile and save to FC
  - [ ] Close configurator
  - [ ] Reopen configurator
  - [ ] Load from FC
  - [ ] Verify variables appear with original names

- [ ] Test with var variables:
  - [ ] Write code with var variables
  - [ ] Follow same round-trip
  - [ ] Verify names preserved

- [ ] Test edge cases:
  - [ ] Empty variable map
  - [ ] Cleared settings cache
  - [ ] Multiple sessions

**Deliverable:** Manual test results

---

## Phase 14: Handle Edge Cases

- [ ] Variable map missing or null:
  - [ ] Decompiler should work without errors
  - [ ] Fall back to generic representation

- [ ] Variable map out of sync:
  - [ ] Validate before using
  - [ ] Skip invalid entries

- [ ] Settings cache cleared:
  - [ ] Handle gracefully
  - [ ] Don't break decompilation

**Deliverable:** Robust error handling

---

## Phase 15: Documentation

- [ ] Update JAVASCRIPT_PROGRAMMING_GUIDE.md:
  - [ ] Note that variable names are preserved
  - [ ] Explain storage mechanism
  - [ ] Mention limitations

- [ ] Update implementation_summary.md:
  - [ ] Document variable map structure
  - [ ] Document storage strategy

- [ ] Add comments to code explaining variable preservation

**Deliverable:** Updated documentation

---

## Phase 16: Performance Check

- [ ] Verify no performance impact on transpile
- [ ] Verify no performance impact on decompile
- [ ] Check storage size (should be minimal)

**Deliverable:** Performance validation

---

## Phase 17: Completion

- [ ] Run all transpiler tests
- [ ] Verify 100% pass rate
- [ ] Create summary of changes
- [ ] Document known limitations
- [ ] Send completion report to manager inbox

**Deliverable:** Completion report

---

## Test Example Code

```javascript
const { flight, override, rc, gvar, edge } = inav;

let distance_to_ground = flight.agl;
var msl = flight.altitude;

gvar[0] = msl - distance_to_ground;
```

**Expected after reload:**
```javascript
const { flight, override, rc, gvar, edge } = inav;

let distance_to_ground = flight.agl;
var msl = flight.altitude;

gvar[0] = msl - distance_to_ground;
```

---

## Notes

- settingsCache.js API:
  - `settingsCache.get(key)` - returns value or undefined
  - `settingsCache.set(key, value)` - stores value
  - `settingsCache.flush()` - clears all (for testing)

- Storage key: `'javascript_variables'`

- Variable map is stored per FC configuration (handled by settingsCache)

- Alternative storage approach: If programmer has better idea, discuss with manager first

---

## Decision Points

- [ ] Should let variables be substituted back into expressions, or kept as declarations?
  - **Current approach:** Keep as declarations at top
  - **Alternative:** Try to substitute (more complex matching)

- [ ] Should we validate variable map against current LCs?
  - **Current approach:** Use as-is, fail gracefully
  - **Alternative:** Validate and warn user (more complex)
