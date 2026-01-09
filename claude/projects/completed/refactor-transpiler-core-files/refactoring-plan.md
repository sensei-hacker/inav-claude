# Transpiler Core Files Refactoring Plan

**Date:** 2025-11-25
**Expected Outcome:** 28-39% code reduction (1,000-1,400 lines)
**Estimated Time:** 14-21 hours (spread across multiple sessions)

## Strategy: Three-Phase Approach

### Phase 1: Low-Risk Helper Extraction (4-6 hours)
Extract helper methods within each file without changing file structure.
**Risk:** LOW | **Testing:** After each file

### Phase 2: Method Decomposition (8-12 hours)
Split massive methods (>100 lines) into smaller, focused methods.
**Risk:** MEDIUM | **Testing:** After each method split

### Phase 3: Optional Shared Modules (if time permits)
Create shared utility modules for cross-file patterns.
**Risk:** MEDIUM-HIGH | **Testing:** Integration tests

---

## PHASE 1: Helper Extraction (LOW RISK)

### File 1: codegen.js (Day 1, 2-3 hours)

#### 1.1 Extract Argument Validation Helper
**Location:** Lines 269-276, 313-320, 360-367, 407-414, 461-468, 629-636, 651-658, 673-680, 695-702

**Create method:**
```javascript
validateFunctionArgs(fnName, args, expectedCount, stmt) {
  if (!args || args.length !== expectedCount) {
    this.errorHandler.addError(
      `${fnName}() requires exactly ${expectedCount} arguments`,
      stmt,
      'invalid_args'
    );
    return false;
  }
  return true;
}
```

**Usage:**
```javascript
if (!this.validateFunctionArgs('edge', stmt.args, 3, stmt)) return;
```

**Expected savings:** ~150 lines
**Test:** Run transpiler tests after implementation

---

#### 1.2 Extract Logic Command Generator
**Location:** Lines 183-186, 209-211, 241-244, 298-300 (40+ occurrences)

**Create method:**
```javascript
pushLogicCommand(operation, operandA, operandB, activatorId = -1, flags = 0) {
  this.commands.push(
    `logic ${this.lcIndex} 1 ${activatorId} ${operation} ` +
    `${operandA.type} ${operandA.value} ${operandB.type} ${operandB.value} ${flags}`
  );
  return this.lcIndex++;
}
```

**Usage:**
```javascript
const resultId = this.pushLogicCommand(
  OPERATION.GREATER_THAN,
  leftOperand,
  rightOperand,
  activatorId
);
```

**Expected savings:** ~100 lines
**Test:** Run transpiler tests after implementation

---

#### 1.3 Extract Math Operation Handler
**Location:** Lines 1019-1040 (min), 1042-1063 (max), 1065-1086 (sin), 1088-1109 (cos), 1111-1132 (tan)

**Create method:**
```javascript
generateMathOperation(mathMethod, expr, activatorId) {
  const opMap = {
    'min': OPERATION.MIN,
    'max': OPERATION.MAX,
    'sin': OPERATION.SIN,
    'cos': OPERATION.COS,
    'tan': OPERATION.TAN,
    'abs': OPERATION.ABS
  };

  const operation = opMap[mathMethod];
  if (!operation) return null;

  // Validation and generation logic
  if (mathMethod === 'abs') {
    // Single argument
    if (!expr.arguments || expr.arguments.length !== 1) {
      this.errorHandler.addError(/*...*/);
      return { type: OPERAND_TYPE.VALUE, value: 0 };
    }
    const arg = this.getOperand(expr.arguments[0], activatorId);
    return this.pushLogicCommand(operation, arg, {type: OPERAND_TYPE.VALUE, value: 0}, activatorId);
  } else {
    // Two arguments (min, max, trig)
    if (!expr.arguments || expr.arguments.length !== 2) {
      this.errorHandler.addError(/*...*/);
      return { type: OPERAND_TYPE.VALUE, value: 0 };
    }
    const left = this.getOperand(expr.arguments[0], activatorId);
    const right = this.getOperand(expr.arguments[1], activatorId);
    return this.pushLogicCommand(operation, left, right, activatorId);
  }
}
```

**Expected savings:** ~200 lines
**Test:** Run transpiler tests, especially Math function tests

---

### File 2: analyzer.js (Day 1, 1-2 hours)

#### 2.1 Extract Error/Warning Helpers
**Location:** Lines 188-192, 193-197, 379-383, etc. (20+ occurrences)

**Create methods:**
```javascript
addError(message, line) {
  this.errors.push({ message, line });
}

addWarning(type, message, line) {
  this.warnings.push({ type, message, line });
}
```

**Expected savings:** ~50 lines
**Test:** Run analyzer tests

---

#### 2.2 Extract GVAR Validation
**Location:** Lines 186-197, 376-390

**Create method:**
```javascript
validateGvarAccess(gvarStr, line) {
  const index = this.extractGvarIndex(gvarStr);
  if (index === -1) {
    this.addError(`Invalid gvar syntax: ${gvarStr}`, line);
    return false;
  }
  if (index >= this.gvarCount) {
    this.addError(`Invalid gvar index ${index}. Maximum is ${this.gvarCount - 1}`, line);
    return false;
  }
  return true;
}
```

**Expected savings:** ~40 lines
**Test:** Run analyzer tests

---

#### 2.3 Combine isAlwaysTrue/isAlwaysFalse
**Location:** Lines 594-634, 639-679

**Create method:**
```javascript
isConstantCondition(condition, targetValue) {
  // targetValue: true for isAlwaysTrue, false for isAlwaysFalse
  if (!condition) return false;

  if (condition.type === 'Literal') {
    return targetValue ? !!condition.value : !condition.value;
  }

  if (condition.type === 'BinaryExpression') {
    // ... shared logic
  }

  if (condition.type === 'LogicalExpression') {
    if (condition.operator === '&&') {
      return targetValue ?
        (this.isConstantCondition(condition.left, true) && this.isConstantCondition(condition.right, true)) :
        (this.isConstantCondition(condition.left, false) || this.isConstantCondition(condition.right, false));
    }
    // ... etc
  }

  return false;
}

// Wrappers for backward compatibility
isAlwaysTrue(condition) {
  return this.isConstantCondition(condition, true);
}

isAlwaysFalse(condition) {
  return this.isConstantCondition(condition, false);
}
```

**Expected savings:** ~35 lines
**Test:** Run analyzer tests, especially dead code detection

---

### File 3: decompiler.js (Day 2, 1 hour)

#### 3.1 Extract Warning Helper
**Location:** Lines 340, 373, 401, 468, 550, etc. (15+ occurrences)

**Create method:**
```javascript
addWarning(message) {
  this.warnings.push(message);
}
```

**Expected savings:** ~15 lines
**Test:** Run decompiler tests

---

#### 3.2 Extract Override Operation Map
**Location:** Lines 575-662 (switch statement)

**Create:**
```javascript
constructor() {
  // ... existing code
  this.overrideOperationMap = {
    [OPERATION.OVERRIDE_THROTTLE_SCALE]: 'override.throttleScale',
    [OPERATION.OVERRIDE_THROTTLE]: 'override.throttle',
    [OPERATION.OVERRIDE_VTX_POWER]: 'override.vtx.power',
    [OPERATION.OVERRIDE_VTX_BAND]: 'override.vtx.band',
    [OPERATION.OVERRIDE_VTX_CHANNEL]: 'override.vtx.channel',
    [OPERATION.OVERRIDE_ARM_SAFETY]: 'override.armSafety',
    [OPERATION.SWAP_ROLL_YAW]: 'override.swapRollYaw',
    [OPERATION.INVERT_ROLL]: 'override.invertRoll',
    [OPERATION.INVERT_PITCH]: 'override.invertPitch',
    [OPERATION.INVERT_YAW]: 'override.invertYaw',
    [OPERATION.OVERRIDE_OSD_LAYOUT]: 'override.osdLayout',
    [OPERATION.OVERRIDE_HEADING]: 'override.heading',
    [OPERATION.OVERRIDE_LOITER_RADIUS]: 'override.loiterRadius',
    [OPERATION.OVERRIDE_CONTROL_PROFILE]: 'override.controlProfile',
    [OPERATION.OVERRIDE_ANGLE]: 'override.angle',
    [OPERATION.OVERRIDE_RATE]: 'override.rate'
  };
}

decompileOverrideAction(lc, allConditions) {
  const target = this.overrideOperationMap[lc.operation];
  if (!target) return null;

  const value = this.decompileOperand(lc.operandBType, lc.operandBValue, allConditions);
  return `${target} = ${value};`;
}
```

**Expected savings:** ~80 lines
**Test:** Run decompiler tests

---

### File 4: parser.js (Day 2, 1 hour)

#### 4.1 Extract Warning Helper
**Location:** Lines 307-312, 332-336, 360-365, 517-522

**Create method:**
```javascript
addWarning(message, loc) {
  this.warnings.push({
    type: 'warning',
    message,
    line: loc ? loc.start.line : 0
  });
}
```

**Expected savings:** ~15 lines
**Test:** Run parser tests

---

#### 4.2 Extract Type Checking Helpers
**Location:** Throughout transformCondition and transformExpression

**Create methods:**
```javascript
isLiteral(expr) {
  return expr && expr.type === 'Literal';
}

isIdentifier(expr) {
  return expr && expr.type === 'Identifier';
}

isMemberExpression(expr) {
  return expr && expr.type === 'MemberExpression';
}

isBinaryExpression(expr) {
  return expr && expr.type === 'BinaryExpression';
}
```

**Expected savings:** ~20 lines
**Test:** Run parser tests

---

### Phase 1 Testing Checklist

After completing each file's helper extraction:
- [ ] Run unit tests for that file
- [ ] Run integration tests
- [ ] Verify no functionality changes
- [ ] Test with example JavaScript code
- [ ] Run round-trip test (JS → CLI → JS)

**Phase 1 Expected Outcome:**
- codegen.js: 450 lines → ~1,050 lines (17% reduction)
- analyzer.js: 125 lines → ~730 lines (15% reduction)
- decompiler.js: 95 lines → ~697 lines (12% reduction)
- parser.js: 35 lines → ~587 lines (6% reduction)
- **Total Phase 1 savings:** ~705 lines (20% total reduction)

---

## PHASE 2: Method Decomposition (MEDIUM RISK)

### File 1: codegen.js (Day 3-4, 4-5 hours)

#### 2.1 Split generateCondition (213 lines → 4-5 methods)
**Location:** Lines 525-737

**New structure:**
```javascript
generateCondition(condition, activatorId) {
  if (!condition) return null;

  switch (condition.type) {
    case 'Literal':
      return this.generateLiteralCondition(condition, activatorId);
    case 'MemberExpression':
      return this.generateMemberCondition(condition, activatorId);
    case 'BinaryExpression':
      return this.generateBinaryCondition(condition, activatorId);
    case 'LogicalExpression':
      return this.generateLogicalCondition(condition, activatorId);
    case 'UnaryExpression':
      return this.generateUnaryCondition(condition, activatorId);
    case 'CallExpression':
      return this.generateCallCondition(condition, activatorId);
    default:
      this.errorHandler.addError(/*...*/);
      return null;
  }
}

// New private methods (30-40 lines each)
generateBinaryCondition(condition, activatorId) { /*...*/ }
generateLogicalCondition(condition, activatorId) { /*...*/ }
generateCallCondition(condition, activatorId) { /*...*/ }
generateMemberCondition(condition, activatorId) { /*...*/ }
generateLiteralCondition(condition, activatorId) { /*...*/ }
generateUnaryCondition(condition, activatorId) { /*...*/ }
```

**Benefits:** Improved readability, easier testing, clearer error messages
**Test:** Run all condition generation tests

---

#### 2.2 Split generateExpression (251 lines → 6-7 methods)
**Location:** Lines 977-1227

**New structure:**
```javascript
generateExpression(expr, activatorId) {
  if (!expr) return { type: OPERAND_TYPE.VALUE, value: 0 };

  if (expr.type === 'CallExpression') {
    return this.generateCallExpression(expr, activatorId);
  }

  // Handle other expression types
  // ... similar delegation pattern
}

// New private methods
generateCallExpression(expr, activatorId) {
  const funcName = expr.callee?.name;

  // Delegate to specialized handlers
  if (funcName === 'abs') return this.generateMathAbs(expr, activatorId);
  if (['min', 'max'].includes(funcName)) return this.generateMathMinMax(funcName, expr, activatorId);
  if (['sin', 'cos', 'tan'].includes(funcName)) return this.generateMathTrig(funcName, expr, activatorId);
  if (funcName === 'mapInput') return this.generateMapInput(expr, activatorId);
  if (funcName === 'mapOutput') return this.generateMapOutput(expr, activatorId);
  if (['xor', 'nand', 'nor'].includes(funcName)) return this.generateLogicGate(funcName, expr, activatorId);
  if (funcName === 'approxEqual') return this.generateApproxEqual(expr, activatorId);

  this.errorHandler.addError(/*...*/);
  return { type: OPERAND_TYPE.VALUE, value: 0 };
}

generateMathAbs(expr, activatorId) { /*...*/ }
generateMathMinMax(funcName, expr, activatorId) { /*...*/ }
generateMathTrig(funcName, expr, activatorId) { /*...*/ }
generateMapInput(expr, activatorId) { /*...*/ }
generateMapOutput(expr, activatorId) { /*...*/ }
generateLogicGate(funcName, expr, activatorId) { /*...*/ }
generateApproxEqual(expr, activatorId) { /*...*/ }
```

**Benefits:** Each function type has its own method, easier to test
**Test:** Run all expression generation tests

---

#### 2.3 Split generateAction (171 lines → 4-5 methods)
**Location:** Lines 742-912

**New structure:**
```javascript
generateAction(action, activatorId) {
  if (action.operation === '=') {
    return this.generateAssignmentAction(action, activatorId);
  } else if (action.operation === '++') {
    return this.generateIncrementAction(action, activatorId);
  } else if (action.operation === '--') {
    return this.generateDecrementAction(action, activatorId);
  }

  this.errorHandler.addError(/*...*/);
}

// New private methods
generateAssignmentAction(action, activatorId) {
  if (action.target.startsWith('gvar[')) {
    return this.generateGvarAssignment(action, activatorId);
  } else if (action.target.startsWith('override.')) {
    return this.generateOverrideAssignment(action, activatorId);
  } else if (action.target.startsWith('rc[')) {
    return this.generateRcOverride(action, activatorId);
  }

  this.errorHandler.addError(/*...*/);
}

generateGvarAssignment(action, activatorId) { /*...*/ }
generateOverrideAssignment(action, activatorId) { /*...*/ }
generateRcOverride(action, activatorId) { /*...*/ }
generateIncrementAction(action, activatorId) { /*...*/ }
generateDecrementAction(action, activatorId) { /*...*/ }
```

**Benefits:** Clearer action type handling, easier to extend
**Test:** Run all action generation tests

---

### File 2: analyzer.js (Day 4, 2-3 hours)

#### 2.4 Split checkPropertyAccess (119 lines → 3-4 methods)
**Location:** Lines 367-485

**New structure:**
```javascript
checkPropertyAccess(propPath, line) {
  if (propPath.startsWith('gvar[')) {
    return this.checkGvarAccess(propPath, line);
  }

  if (propPath.startsWith('rc[')) {
    return this.checkRcAccess(propPath, line);
  }

  return this.checkApiPropertyAccess(propPath, line);
}

// New private methods
checkGvarAccess(propPath, line) {
  // Lines 369-390
  // GVAR validation logic
}

checkRcAccess(propPath, line) {
  // Lines 394-422
  // RC channel validation logic
}

checkApiPropertyAccess(propPath, line) {
  // Lines 424-485
  // API property validation logic
}
```

**Benefits:** Each namespace has its own validation method
**Test:** Run all property access validation tests

---

### File 3: decompiler.js (Day 5, 2 hours)

#### 2.5 Split decompileCondition (136 lines → 4-5 methods)
**Location:** Lines 418-553

**New structure:**
```javascript
decompileCondition(lc, allConditions) {
  const op = lc.operation;

  // Group by category
  if (this.isComparisonOp(op)) {
    return this.decompileComparison(lc, allConditions);
  }

  if (this.isLogicalOp(op)) {
    return this.decompileLogical(lc, allConditions);
  }

  if (this.isMathOp(op)) {
    return this.decompileMath(lc, allConditions);
  }

  if (this.isSpecialOp(op)) {
    return this.decompileSpecial(lc, allConditions);
  }

  this.addWarning(`Unsupported operation: ${op}`);
  return 'true';
}

// Category checkers
isComparisonOp(op) {
  return [OPERATION.EQUAL, OPERATION.GREATER_THAN, OPERATION.LOWER_THAN, OPERATION.APPROX_EQUAL].includes(op);
}

isLogicalOp(op) {
  return [OPERATION.AND, OPERATION.OR, OPERATION.NOT, OPERATION.XOR, OPERATION.NAND, OPERATION.NOR].includes(op);
}

isMathOp(op) {
  return [OPERATION.ADD, OPERATION.SUB, OPERATION.MUL, OPERATION.DIV, OPERATION.MODULUS,
          OPERATION.MIN, OPERATION.MAX, OPERATION.ABS,
          OPERATION.SIN, OPERATION.COS, OPERATION.TAN,
          OPERATION.MAP_INPUT, OPERATION.MAP_OUTPUT].includes(op);
}

isSpecialOp(op) {
  return [OPERATION.STICKY, OPERATION.EDGE, OPERATION.DELAY, OPERATION.TIMER, OPERATION.DELTA,
          OPERATION.LOW, OPERATION.MID, OPERATION.HIGH].includes(op);
}

// Decompilation methods
decompileComparison(lc, allConditions) { /*...*/ }
decompileLogical(lc, allConditions) { /*...*/ }
decompileMath(lc, allConditions) { /*...*/ }
decompileSpecial(lc, allConditions) { /*...*/ }
```

**Benefits:** Operations grouped by category, easier to maintain
**Test:** Run all decompilation tests

---

#### 2.6 Split decompileAction (117 lines → 3-4 methods)
**Location:** Lines 561-677

**New structure:**
```javascript
decompileAction(lc, allConditions) {
  const op = lc.operation;

  if (this.isGvarOp(op)) {
    return this.decompileGvarAction(lc, allConditions);
  }

  if (this.isOverrideOp(op)) {
    return this.decompileOverrideAction(lc, allConditions);
  }

  if (op === OPERATION.OVERRIDE_RC) {
    return this.decompileRcOverride(lc, allConditions);
  }

  this.addWarning(`Unsupported action operation: ${op}`);
  return '// Unknown action';
}

// Category checker
isGvarOp(op) {
  return [OPERATION.GVAR_SET, OPERATION.GVAR_INC, OPERATION.GVAR_DEC].includes(op);
}

isOverrideOp(op) {
  return this.overrideOperationMap.hasOwnProperty(op);
}

// Decompilation methods
decompileGvarAction(lc, allConditions) { /*...*/ }
decompileOverrideAction(lc, allConditions) { /*...*/ } // Uses map from Phase 1
decompileRcOverride(lc, allConditions) { /*...*/ }
```

**Benefits:** Action categories clearly separated
**Test:** Run all action decompilation tests

---

### Phase 2 Testing Checklist

After each method split:
- [ ] Run unit tests for split methods
- [ ] Run integration tests
- [ ] Verify identical output to original
- [ ] Test edge cases
- [ ] Run round-trip test (JS → CLI → JS)
- [ ] Check error messages still accurate

**Phase 2 Expected Outcome:**
- Massive methods (>100 lines) eliminated
- Methods now 20-40 lines each
- Significantly improved maintainability
- No functional changes
- **Additional savings:** ~300-400 lines through better organization

---

## PHASE 3: Shared Modules (OPTIONAL, if time permits)

### 3.1 Create Shared API Mapping Utility (2-3 hours)

**New file:** `transpiler/shared/api_mapper.js`

**Extract from:**
- codegen.js: lines 39-74 (buildOperandMapping)
- analyzer.js: lines 42-88 (buildAPIStructure)
- decompiler.js: lines 58-98 (buildOperandMapping)

**Expected savings:** ~100 lines across 3 files
**Risk:** MEDIUM-HIGH (affects all three files)
**Test:** Full integration test suite

---

### 3.2 Create Base Condition Visitor (3-4 hours)

**New file:** `transpiler/shared/condition_visitor.js`

**Provides:** Base class for recursive condition traversal

**Used by:**
- codegen.js: generateCondition
- analyzer.js: checkCondition, findGvarReads
- parser.js: transformCondition

**Expected savings:** ~80 lines across 3 files
**Risk:** HIGH (fundamental change to traversal pattern)
**Test:** Extensive unit and integration tests

---

### Phase 3 Testing Requirements

- [ ] Unit tests for shared modules
- [ ] Integration tests with all consumers
- [ ] Regression tests comparing before/after
- [ ] Performance tests (ensure no slowdown)
- [ ] Round-trip tests
- [ ] Real-world example tests

---

## TESTING STRATEGY

### Test After Each Change

**Quick verification:**
```bash
cd inav-configurator/js/transpiler/transpiler/tests
node run_variable_handler_tests.cjs
node run_const_tests.cjs
node run_auto_import_tests.cjs
node run_let_integration_tests.cjs
```

**Manual round-trip test:**
```bash
cd inav-configurator/js/transpiler
node -e "
const { Transpiler } = require('./transpiler/index.js');
const { Decompiler } = require('./transpiler/decompiler.js');

const testCode = \`
const { flight, gvar } = inav;
if (flight.altitude > 100) {
  gvar[0] = 1;
}
\`;

const transpiler = new Transpiler();
const result = transpiler.transpile(testCode);
console.log('Commands:', result.commands.length);

const decompiler = new Decompiler();
const decompiled = decompiler.decompile(/* parse commands */);
console.log('Success:', decompiled.success);
"
```

### Regression Test Suite

After completing each phase:
1. Run all existing unit tests
2. Run integration tests
3. Test with all example files in `examples/`
4. Compare output before/after refactoring (should be identical)
5. Check error message quality

---

## COMMIT STRATEGY

### After Each Phase:

**Phase 1 commit message:**
```
Refactor: Extract helper methods in transpiler core files

- Extract argument validation helper (codegen.js)
- Extract logic command generator (codegen.js)
- Extract Math operation handler (codegen.js)
- Extract error/warning helpers (analyzer.js)
- Extract GVAR validation (analyzer.js)
- Combine isAlwaysTrue/isAlwaysFalse (analyzer.js)
- Extract warning helper (decompiler.js)
- Extract override operation map (decompiler.js)
- Extract warning helper (parser.js)
- Extract type checking helpers (parser.js)

Reduces code duplication by ~705 lines (20% total reduction)
All tests passing, no functional changes
```

**Phase 2 commit message:**
```
Refactor: Split massive methods in transpiler core files

- Split generateCondition into 6 focused methods (codegen.js)
- Split generateExpression into 7 focused methods (codegen.js)
- Split generateAction into 5 focused methods (codegen.js)
- Split checkPropertyAccess into 3 methods (analyzer.js)
- Split decompileCondition into 4 methods (decompiler.js)
- Split decompileAction into 3 methods (decompiler.js)

Improves maintainability by eliminating methods >100 lines
All methods now 20-40 lines, easier to test and understand
All tests passing, no functional changes
```

---

## SUCCESS CRITERIA

- [ ] All tests pass (100% pass rate)
- [ ] No functional regressions
- [ ] ≥20% file size reduction achieved
- [ ] No methods >100 lines remain
- [ ] Code duplication significantly reduced
- [ ] Error messages remain clear and helpful
- [ ] Performance not degraded

---

## ROLLBACK PLAN

If any phase causes issues:
1. `git stash` current changes
2. `git log --oneline -10` to find pre-refactor commit
3. `git reset --hard <commit>` to rollback
4. Review what went wrong
5. Fix approach and retry

---

## TIMELINE ESTIMATE

| Phase | Time | Cumulative |
|-------|------|------------|
| Phase 1: Helper Extraction | 4-6 hours | 4-6 hours |
| Phase 2: Method Decomposition | 8-12 hours | 12-18 hours |
| Phase 3: Shared Modules (optional) | 5-7 hours | 17-25 hours |
| **Testing & Verification** | 3-5 hours | **15-23 hours** |

**Target:** Complete Phase 1 and Phase 2 within allocated 14-21 hours
**Phase 3:** Only if time permits and first two phases go smoothly

---

## NEXT STEPS

1. Review this plan with user
2. Start Phase 1 with codegen.js
3. Test after each helper extraction
4. Commit after completing each file
5. Move to next file

Ready to begin implementation? Starting with Phase 1.1: Extract argument validation helper in codegen.js.
