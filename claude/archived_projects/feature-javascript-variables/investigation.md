# Investigation: JavaScript Variables Support in INAV Transpiler

**Date:** 2025-11-24
**Status:** Investigation Complete
**Complexity:** Moderate
**Estimated Implementation Time:** 3-5 days

## Executive Summary

Adding `let` and `var` support to the INAV transpiler is **feasible and straightforward**. The transpiler already has most of the infrastructure needed:

- **Acorn parser** already parses `let` and `var` into AST nodes
- **Analyzer** has gvar tracking and validation infrastructure
- **Code generator** can handle variable substitution and expression generation

**Recommended approach:**
1. **`let` variables:** Constant folding with substitution (simple, no gvar usage)
2. **`var` variables:** Allocate to unused gvar slots (requires symbol table)

**Key limitation:** Only 8 gvar slots total (gvar[0]-gvar[7]), shared with user's explicit gvar usage.

---

## 1. Current Transpiler Architecture

### 1.1 Parser (parser.js)

**Parser:** Uses **Acorn** ECMAScript parser with ES2020 support

**Current behavior:**
- Acorn **already parses** `let foo = 5;` and `var bar = 10;` into `VariableDeclaration` nodes
- `transformVariableDeclaration()` (line 191) currently only handles:
  ```javascript
  const { flight, waypoint, gvar } = inav;
  ```
- All other variable declarations return `null` (line 207) and are **ignored**

**AST structure for variable declarations:**
```javascript
{
  type: 'VariableDeclaration',
  kind: 'let' | 'var' | 'const',
  declarations: [
    {
      type: 'VariableDeclarator',
      id: { type: 'Identifier', name: 'foo' },
      init: { type: 'Literal', value: 5 } // or any expression
    }
  ]
}
```

**Key insight:** Acorn does the heavy lifting. We just need to transform these nodes!

### 1.2 Analyzer (analyzer.js)

**Current capabilities:**
- Property validation (flight.altitude, gvar[0], etc.)
- **Gvar tracking** - Already tracks which gvars are read and written (line 655-700)
- Dead code detection
- Conflict detection
- Range validation

**Gvar constraints:**
- 8 global variables: gvar[0] through gvar[7]
- Range: -1,000,000 to 1,000,000
- Analyzer validates gvar indices and warns about uninitialized gvars

**Key insight:** Infrastructure for tracking variables already exists! Just need to extend it.

### 1.3 Code Generator (codegen.js)

**Current capabilities:**
- Generates INAV CLI commands: `logic N 1 -1 OPERATION OPERAND_A OPERAND_B 0`
- `getOperand()` (line 717) resolves identifiers to operands:
  - `gvar[0]` → `{ type: 3, value: 0 }` (GVAR operand)
  - `flight.altitude` → `{ type: X, value: Y }` (from API mapping)
  - Numbers → `{ type: 1, value: N }` (VALUE operand)
- Can generate intermediate logic conditions for expressions

**Key insight:** Variable substitution can reuse existing operand resolution!

---

## 2. Implementation Design

### 2.1 Symbol Table Design

Create a **SymbolTable** class to track variables:

```javascript
class SymbolTable {
  constructor() {
    this.symbols = new Map(); // varName -> symbol info
    this.gvarAllocations = new Map(); // varName -> gvar index
    this.usedGvars = new Set(); // Track explicitly used gvars
  }

  // Add a variable declaration
  addVariable(name, kind, value, isConstant) {
    this.symbols.set(name, {
      name,
      kind,        // 'let' or 'var'
      value,       // Constant value or null
      isConstant,  // Can we substitute?
      gvarIndex: null  // For 'var', which gvar slot
    });
  }

  // Resolve variable name to value/gvar
  resolve(name) {
    const symbol = this.symbols.get(name);
    if (!symbol) return null;

    if (symbol.isConstant) {
      return symbol.value;  // Substitute directly
    } else {
      return `gvar[${symbol.gvarIndex}]`;  // Return gvar reference
    }
  }

  // Allocate gvar slots for 'var' declarations
  allocateGvars() {
    const availableSlots = this.findAvailableGvarSlots();

    for (const [name, symbol] of this.symbols) {
      if (symbol.kind === 'var' && !symbol.isConstant) {
        if (availableSlots.length === 0) {
          throw new Error(`No available gvar slots for variable '${name}'`);
        }
        symbol.gvarIndex = availableSlots.pop();
        this.gvarAllocations.set(name, symbol.gvarIndex);
      }
    }
  }

  // Find which gvar slots are NOT explicitly used by user
  findAvailableGvarSlots() {
    const allSlots = [7, 6, 5, 4, 3, 2, 1, 0];  // High to low
    return allSlots.filter(slot => !this.usedGvars.has(slot));
  }
}
```

**Design decisions:**
- **Allocation order:** Start at gvar[7], work down to gvar[0]
  - Rationale: Users typically use gvar[0], gvar[1], etc. from bottom up
- **Single scope:** No nested scopes (keep it simple for now)
- **No reassignment tracking** initially

### 2.2 `let` Variable Implementation (Constant Folding)

**Strategy:** Substitute variable references with their constant values

**Example:**
```javascript
// User writes:
let foo = 5;
let bar = foo + 10;
gvar[1] = bar;

// Transpiler substitutes:
// foo = 5 (constant)
// bar = 5 + 10 = 15 (constant fold)
// Generate: gvar[1] = 15
```

**Implementation:**

1. **Parser** - Transform `let` declarations:
   ```javascript
   transformVariableDeclaration(node) {
     if (node.kind === 'let') {
       const name = node.declarations[0].id.name;
       const value = this.extractValue(node.declarations[0].init);

       return {
         type: 'LetDeclaration',
         name,
         value,
         loc: node.loc,
         range: node.range
       };
     }
   }
   ```

2. **Analyzer** - Track `let` variables in symbol table:
   ```javascript
   analyzeStatement(stmt) {
     if (stmt.type === 'LetDeclaration') {
       // Check if value is a compile-time constant
       const isConstant = this.isConstantExpression(stmt.value);

       if (isConstant) {
         this.symbolTable.addVariable(stmt.name, 'let', stmt.value, true);
       } else {
         throw new Error(`let variable '${stmt.name}' must be a compile-time constant`);
       }
     }
   }
   ```

3. **Code Generator** - Substitute references:
   ```javascript
   getOperand(value) {
     // If value is an identifier, check if it's a variable
     if (typeof value === 'string') {
       const resolved = this.symbolTable.resolve(value);
       if (resolved !== null) {
         return this.getOperand(resolved); // Recursive resolve
       }
       // ... existing gvar/API checks
     }
   }
   ```

**Supported patterns:**
- ✅ `let foo = 5;` - Literal constant
- ✅ `let bar = 3 + 7;` - Constant expression (fold at parse time)
- ✅ `let baz = foo + bar;` - Reference to other constants (substitute)
- ❌ `let bad = gvar[0];` - Not a constant (runtime value)
- ❌ `let bad = flight.altitude;` - Not a constant (runtime value)

### 2.3 `var` Variable Implementation (Gvar Allocation)

**Strategy:** Map variables to unused gvar slots

**Example:**
```javascript
// User writes:
var altitude_threshold = 100;
if (flight.altitude > altitude_threshold) {
  override.throttle = 1200;
}

// Assume gvar[0-6] are explicitly used, so allocate gvar[7]
// Transpiler generates:
gvar[7] = 100;
if (flight.altitude > gvar[7]) {
  override.throttle = 1200;
}
```

**Implementation:**

1. **First pass (Analyzer)** - Detect explicitly used gvars:
   ```javascript
   analyze(ast) {
     // Scan entire AST for gvar[N] references
     this.detectUsedGvars(ast);

     // Process variable declarations
     for (const stmt of ast.statements) {
       if (stmt.type === 'VarDeclaration') {
         this.symbolTable.addVariable(stmt.name, 'var', null, false);
       }
     }

     // Allocate gvar slots for 'var' declarations
     this.symbolTable.allocateGvars();
   }

   detectUsedGvars(ast) {
     // Walk AST and find all gvar[N] references
     // Add N to symbolTable.usedGvars Set
   }
   ```

2. **Code generation** - Replace variable references:
   ```javascript
   getOperand(value) {
     if (typeof value === 'string') {
       const resolved = this.symbolTable.resolve(value);
       if (resolved !== null) {
         // For 'var', this returns "gvar[7]", etc.
         return this.getOperand(resolved);
       }
     }
   }
   ```

3. **Generate initialization** - Add gvar assignments at start:
   ```javascript
   generate(ast) {
     // Generate initialization for all 'var' declarations
     for (const [name, symbol] of this.symbolTable.symbols) {
       if (symbol.kind === 'var' && symbol.value !== null) {
         // Generate: gvar[N] = initialValue
         this.generateVarInit(symbol);
       }
     }

     // Continue with regular statement generation
     for (const stmt of ast.statements) {
       this.generateStatement(stmt);
     }
   }
   ```

**Supported patterns:**
- ✅ `var foo = 5;` - Allocate gvar, set to 5
- ✅ `var bar;` - Allocate gvar, defaults to 0
- ✅ `var baz = gvar[0] + 10;` - Allocate gvar, expression evaluated at runtime
- ✅ `foo = 20;` - Assignment to `var` variable (becomes gvar assignment)

---

## 3. Edge Cases and Limitations

### 3.1 Slot Exhaustion

**Problem:** What if user needs more than 8 total gvars?

```javascript
// User explicitly uses gvar[0] through gvar[4]
// Then declares 4 'var' variables
// Total: 5 + 4 = 9 gvars needed, but only 8 available!
```

**Solution:** Error message with helpful guidance
```
Error: Cannot allocate gvar for variable 'myVar'.
All 8 gvar slots are in use (5 explicit + 3 variables).
Suggestion: Use 'let' for constants or reduce explicit gvar usage.
```

### 3.2 Variable Reassignment

**`let` variables:**
```javascript
let foo = 5;
foo = 10;  // ❌ NOT SUPPORTED (can't reassign in constant folding)
```

**Error:** `Cannot reassign 'let' variable 'foo'. Use 'var' for mutable variables.`

**`var` variables:**
```javascript
var foo = 5;
foo = 10;  // ✅ SUPPORTED (becomes gvar[N] = 10)
```

**Implementation:** Parser needs to track assignments to identifiers and verify they're `var`, not `let`.

### 3.3 Non-Constant Initializers for `let`

```javascript
let foo = gvar[0];  // ❌ Runtime value, not constant
let bar = flight.altitude;  // ❌ Runtime value, not constant
```

**Error:** `'let' variable 'foo' must be initialized with a constant value. Use 'var' for runtime values.`

**Constant expressions allowed:**
- Literals: `5`, `true`, `"hello"`
- Arithmetic: `3 + 7`, `10 * 2`
- References to other `let` constants: `let bar = foo + 5;`

### 3.4 Scoping

**Current design:** Single global scope (no block scoping)

```javascript
if (flight.altitude > 100) {
  let foo = 5;  // ⚠️ Scope not enforced
}
gvar[0] = foo;  // Works (might be confusing)
```

**Rationale:** INAV logic conditions don't have block scope. All variables are global.

**Future enhancement:** Could enforce block scoping during semantic analysis and error if variable used outside its block.

### 3.5 Variable Shadowing

```javascript
let foo = 5;
let foo = 10;  // ❌ Redeclaration error
```

**Error:** `Variable 'foo' is already declared`

### 3.6 Uninitialized Variables

```javascript
var foo;  // No initializer
gvar[0] = foo;  // Uses default value (0)
```

**Behavior:** Defaults to 0 (INAV gvar default)

**Warning:** `Variable 'foo' used without explicit initialization. Defaults to 0.`

### 3.7 Type Checking

**Not enforced initially.** All variables are numbers (INAV only supports numeric gvars).

```javascript
var foo = true;  // Stored as 1
var bar = false; // Stored as 0
```

### 3.8 Decompiler

**Expected behavior:** Variable names **will be lost** during compilation

```javascript
// Original:
var altitude_threshold = 100;

// Compiled to:
gvar[7] = 100;

// Decompiled:
gvar[7] = 100;  // Original name 'altitude_threshold' lost
```

**Future enhancement:** Store variable mapping as comments in CLI output or separate metadata file.

---

## 4. Specific Questions Answered

### Q1: Does Acorn already parse `let`/`var` declarations into the AST?

**Answer:** ✅ Yes! Acorn parses them perfectly as `VariableDeclaration` nodes with `kind: 'let' | 'var'`.

### Q2: Do we need to build a symbol table from scratch?

**Answer:** ✅ Yes, but it's simple. Current analyzer has no general symbol table, only gvar tracking. We need a lightweight SymbolTable class (see Section 2.1).

### Q3: How can we detect which gvar slots are explicitly used?

**Answer:** Walk the AST and collect all `gvar[N]` references. Existing analyzer already does this partially for uninitialized gvar warnings (line 655).

**Implementation:**
```javascript
detectUsedGvars(ast) {
  const used = new Set();

  // Recursive AST walker
  function walk(node) {
    if (node.type === 'Assignment' && node.target.startsWith('gvar[')) {
      used.add(extractGvarIndex(node.target));
    }
    // ... walk children
  }

  walk(ast);
  return used;
}
```

### Q4: How should we handle `let foo = 5; foo = 10;`?

**Answer:** ❌ Not supported. Throw error: `Cannot reassign 'let' variable. Use 'var' for mutable variables.`

**Rationale:** `let` is for compile-time constants only. Reassignment would require gvar allocation, which defeats the purpose.

### Q5: How should we handle `let foo = gvar[0] + 1;`?

**Answer:** ❌ Not supported for `let`. Throw error: `'let' variable must be initialized with compile-time constant.`

**Alternative:** Use `var` instead:
```javascript
var foo = gvar[0] + 1;  // ✅ Supported
// Becomes: gvar[7] = gvar[0] + 1
```

### Q6: Should we enforce block scoping or function scoping?

**Answer:** **Neither initially.** All variables are globally scoped (single symbol table).

**Rationale:** INAV logic conditions are flat - no true scoping. Implementing block scope would be misleading since the compiled output doesn't preserve it.

**Future enhancement:** Could add block scope validation to catch bugs, but compiled code would still be global.

### Q7: What happens when user needs more than 8 gvars total?

**Answer:** Clear error message with guidance (see Section 3.1).

### Q8: Can we preserve variable names in decompilation?

**Answer:** ❌ Not initially. Low priority.

**Future enhancement:** Could add metadata comments:
```javascript
// gvar[7] = altitude_threshold
gvar[7] = 100;
```

---

## 5. Test Scenarios

### 5.1 Basic `let` Constant Folding

**Input:**
```javascript
let threshold = 100;
if (flight.altitude > threshold) {
  override.throttle = 1500;
}
```

**Expected output:**
```
logic 0 1 -1 GREATER_THAN FLIGHT_ALTITUDE 100 ...
logic 1 1 0 OVERRIDE_THROTTLE 1500 ...
```

**Verification:** Variable `threshold` is substituted with `100`.

### 5.2 `let` with Expression

**Input:**
```javascript
let base = 50;
let threshold = base * 2;
gvar[0] = threshold;
```

**Expected output:**
```
logic 0 1 -1 GVAR_SET 0 100 ...
```

**Verification:** `base * 2` constant-folded to `100`.

### 5.3 Basic `var` Allocation

**Input:**
```javascript
var counter = 0;
on.always(() => {
  counter++;
});
```

**Expected output (assuming gvar[7] available):**
```
logic 0 1 -1 GVAR_SET 7 0 ...        // Initialize counter
logic 1 1 -1 TRUE ...                // on.always activator
logic 2 1 1 GVAR_INC 7 1 ...         // counter++
```

**Verification:** Variable `counter` mapped to `gvar[7]`.

### 5.4 Mixed `let` and `var`

**Input:**
```javascript
let max_altitude = 500;
var current_altitude = 0;

on.always(() => {
  current_altitude = flight.altitude;
  if (current_altitude > max_altitude) {
    override.throttle = 1000;
  }
});
```

**Expected output:**
- `max_altitude` substituted with `500`
- `current_altitude` mapped to `gvar[7]`

### 5.5 Gvar Slot Conflict Detection

**Input:**
```javascript
// User explicitly uses gvar[0] through gvar[7]
gvar[0] = 1;
gvar[7] = 8;

var myVar = 10;  // No slots available!
```

**Expected:** Error message with guidance

### 5.6 `let` Reassignment Error

**Input:**
```javascript
let foo = 5;
foo = 10;
```

**Expected:** Error: `Cannot reassign 'let' variable 'foo'`

### 5.7 Non-Constant `let` Error

**Input:**
```javascript
let foo = gvar[0];
```

**Expected:** Error: `'let' variable 'foo' must be initialized with compile-time constant`

### 5.8 Variable Shadowing Error

**Input:**
```javascript
let foo = 5;
let foo = 10;
```

**Expected:** Error: `Variable 'foo' is already declared`

---

## 6. Implementation Phases

### Phase 1: Foundation (1 day)

**Goal:** Basic infrastructure

- [ ] Create `SymbolTable` class in new file `symbol_table.js`
- [ ] Add symbol table to analyzer constructor
- [ ] Implement `detectUsedGvars()` method in analyzer
- [ ] Write unit tests for symbol table

### Phase 2: `let` Support (1 day)

**Goal:** Constant folding for `let`

- [ ] Parser: Transform `let` declarations to AST nodes
- [ ] Analyzer: Validate constant expressions, add to symbol table
- [ ] Codegen: Implement variable substitution in `getOperand()`
- [ ] Add error handling for reassignment and non-constants
- [ ] Unit tests for `let` functionality

### Phase 3: `var` Support (1.5 days)

**Goal:** Gvar allocation for `var`

- [ ] Parser: Transform `var` declarations to AST nodes
- [ ] Analyzer: Implement gvar allocation logic
- [ ] Codegen: Generate initialization code for `var` declarations
- [ ] Codegen: Handle assignments to `var` variables
- [ ] Add error handling for slot exhaustion
- [ ] Unit tests for `var` functionality

### Phase 4: Integration & Testing (0.5 days)

**Goal:** End-to-end testing

- [ ] Test mixed `let` and `var` usage
- [ ] Test all edge cases (Section 5)
- [ ] Test in configurator GUI
- [ ] Verify compiled output is correct

### Phase 5: Polish (1 day)

**Goal:** Error messages and documentation

- [ ] Improve error messages (clear, actionable)
- [ ] Add warnings for best practices
- [ ] Update user documentation with examples
- [ ] Add developer documentation

**Total estimated time: 5 days**

---

## 7. Alternative Approaches Considered

### 7.1 Low-to-High Gvar Allocation

**Current design:** Allocate from gvar[7] down to gvar[0]

**Alternative:** Allocate from gvar[0] up to gvar[7]

**Pros:**
- Matches typical user pattern (users often start at gvar[0])

**Cons:**
- More likely to conflict with user's explicit usage

**Decision:** Stick with high-to-low (7→0)

### 7.2 Explicit Annotations

**Alternative:** User specifies which gvar to use

```javascript
@gvar(5)
var altitude_threshold = 100;
```

**Pros:**
- Full control over gvar allocation
- No slot conflict errors

**Cons:**
- More verbose
- Defeats the purpose of abstraction
- Non-standard syntax

**Decision:** Auto-allocation is better UX

### 7.3 Unified `let` and `var` (Both Use Gvar)

**Alternative:** Both `let` and `var` allocate gvars, no constant folding

**Pros:**
- Simpler implementation (one code path)
- Allows reassignment of `let`

**Cons:**
- Wastes gvar slots on constants
- Doesn't optimize for common use case

**Decision:** Separate strategies are better

---

## 8. Risks and Mitigation

### Risk 1: Slot Exhaustion is Frustrating

**Impact:** Users may frequently hit "no available gvar slots" errors

**Mitigation:**
- Clear error messages with suggestions
- Add warning when approaching limit (e.g., "6 of 8 gvar slots used")
- Document best practices: use `let` for constants

### Risk 2: No Block Scoping is Confusing

**Impact:** Users expect JavaScript scoping rules

**Mitigation:**
- Document clearly in user guide
- Add warnings for potentially confusing patterns
- Future: add scope validation (error if used out of block)

### Risk 3: Lost Variable Names in Decompiler

**Impact:** Decompiled code is less readable

**Mitigation:**
- Document limitation clearly
- Future: add metadata preservation

---

## 9. Recommendations

### Proceed with Implementation ✅

**Why:**
- **Feasible:** Infrastructure exists, implementation is straightforward
- **High value:** Major UX improvement for users
- **Low risk:** Well-scoped, testable incrementally
- **Fast:** ~5 days estimated time

**Suggested priority:**
1. Implement `let` first (simpler, more common use case)
2. Then implement `var` (more complex, but builds on `let` infrastructure)
3. Polish and document

### Future Enhancements

**After initial implementation:**
1. **Block scope validation** - Error if variable used outside declaration block
2. **Metadata preservation** - Store variable mappings for decompiler
3. **`const` support** - Alias for `let` (for familiarity)
4. **Better warnings** - "N of 8 gvar slots used" progress indicator
5. **Optimization** - Detect unused variables, skip gvar allocation

---

## 10. Conclusion

Adding JavaScript variable support to the INAV transpiler is **feasible and recommended**. The transpiler already has the necessary infrastructure (Acorn parser, gvar tracking, expression handling). Implementation requires:

1. **Symbol table** - Lightweight class to track variables (~100 LOC)
2. **Parser changes** - Transform `let`/`var` declarations (~50 LOC)
3. **Analyzer changes** - Gvar detection and allocation (~150 LOC)
4. **Codegen changes** - Variable substitution (~50 LOC)

**Total estimated effort:** ~5 days (350 LOC + tests + documentation)

**Key benefits:**
- More intuitive programming experience
- Better code readability
- Reduced cognitive load

**Key limitations:**
- Only 8 gvar slots total (shared with explicit usage)
- No block scoping (global scope only)
- Variable names lost in decompilation

**Next step:** Get manager approval and proceed with Phase 1 implementation.
