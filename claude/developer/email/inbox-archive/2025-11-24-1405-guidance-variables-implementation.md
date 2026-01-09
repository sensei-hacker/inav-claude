# Implementation Guidance: JavaScript Variables Support

**Date:** 2025-11-24 14:05
**Reference:** Investigation report received and reviewed
**Status:** ✅ Approved to Proceed with Clarifications

## Investigation Review

Excellent work on the investigation! The analysis is thorough and the proposed architecture is sound. However, I need to provide some important clarifications based on stakeholder input.

## Key Requirement Changes

### 1. `let` Variable Expression Support ✅ REQUIRED

**IMPORTANT CHANGE:** `let` variables **MUST support expressions**, not just compile-time constants.

**Previously proposed (INCORRECT):**
```javascript
let foo = gvar[0] + 1;  // ❌ Error: "must be compile-time constant"
```

**Corrected requirement (CORRECT):**
```javascript
let foo = gvar[0] + 1;  // ✅ Supported via expression substitution
gvar[1] = foo;

// Transpiles to:
gvar[1] = gvar[0] + 1;
```

**Implementation approach:**
- `let` variables store the **expression AST**, not just constant values
- When a `let` variable is referenced, substitute with the entire expression
- This is still compile-time substitution (no gvar allocation)
- The expression is evaluated each time the variable is used

**Examples:**

```javascript
// Example 1: Simple expression
let altitude = flight.altitude;
if (altitude > 100) { ... }
// Becomes: if (flight.altitude > 100) { ... }

// Example 2: Complex expression
let combined = gvar[0] + gvar[1] * 2;
gvar[2] = combined;
// Becomes: gvar[2] = gvar[0] + gvar[1] * 2;

// Example 3: Multiple uses (expression copied each time)
let speed = flight.speed;
gvar[0] = speed;
gvar[1] = speed + 100;
// Becomes:
// gvar[0] = flight.speed;
// gvar[1] = flight.speed + 100;
```

**What's NOT supported:**
- `let` reassignment: `let foo = 5; foo = 10;` ❌ Error
- This keeps `let` semantics simple and prevents mutation bugs

### 2. Code Organization - Helper Class Threshold

**Rule:** If variable handling would **ADD more than 40 NEW lines** to any single main file (parser.js, analyzer.js, or codegen.js), abstract some of the new code to a helper class.

**Important clarifications:**
- This is about **NEW lines added**, not total file size
- The helper class itself can be **100+ lines** - that's perfectly fine
- Goal: Keep the main transpiler files focused and readable

**Your estimates:**
- Parser changes: ~50 **NEW** LOC ⚠️ **Exceeds threshold - use helper**
- Analyzer changes: ~150 **NEW** LOC ⚠️ **Exceeds threshold - use helper**
- Codegen changes: ~50 **NEW** LOC ⚠️ **Exceeds threshold - use helper**

**Action required:** Plan to use helper class(es) from the start.

**Suggested approach:**

**Option A: Single helper (`variable_handler.js` or `variable_manager.js`)**
```javascript
// Helper class can be 100-200+ lines - that's fine!
class VariableHandler {
  constructor(symbolTable);

  // For parser
  extractVariableDeclaration(node);

  // For analyzer
  validateLetDeclaration(name, initExpr);
  validateVarDeclaration(name, initExpr);
  allocateGvarSlots(usedSlots, varDeclarations);

  // For codegen
  resolveLetReference(varName);  // Returns expression AST
  resolveVarReference(varName);  // Returns gvar[N]
}
```

**Option B: Separate helpers per concern**
- `symbol_table.js` - Core symbol tracking (can be 100+ lines)
- `variable_resolver.js` - Resolution logic for codegen (can be 50+ lines)
- `gvar_allocator.js` - Gvar slot allocation (can be 50+ lines)

Choose the option that makes the most sense architecturally.

### 3. Gvar Helper Integration (Optional)

**If and only if it makes sense**, the helper class can also handle gvar-related logic that currently exists in analyzer/codegen.

**Potential consolidation:**
- Gvar slot detection (currently in analyzer.js:655-700)
- Gvar validation (range checking, conflicts)
- Gvar allocation strategy (high-to-low)

**Don't force it** - only consolidate if it naturally fits the design and improves code clarity.

## Updated Implementation Plan

### Phase 1: Foundation & Design (1-1.5 days)

1. **Design helper class(es)**
   - Decide: single `VariableHandler` vs multiple focused helpers
   - Define clear interfaces
   - Consider gvar integration (if beneficial)
   - Helper class(es) can be 100-200+ lines total - no problem

2. **Create helper class(es)**
   - Implement core variable tracking
   - Implement expression storage for `let`
   - Implement gvar allocation for `var`
   - Unit tests for helper class

3. **Update SymbolTable**
   - Store expression AST for `let` variables (not just constant values)
   - Track allocation metadata for `var` variables

### Phase 2: `let` Support (1-1.5 days)

1. **Parser integration**
   - Use helper to extract `let` declarations
   - Store full expression AST
   - Keep **NEW code** in parser.js minimal (< 40 NEW lines)

2. **Analyzer integration**
   - Use helper to validate `let` semantics
   - Detect reassignment attempts → error
   - Keep **NEW code** in analyzer.js minimal (< 40 NEW lines)

3. **Codegen integration**
   - Use helper to resolve `let` references
   - Substitute entire expression AST at usage sites
   - Keep **NEW code** in codegen.js minimal (< 40 NEW lines)

4. **Testing**
   - Test constant expressions: `let x = 5;`
   - Test runtime expressions: `let x = gvar[0] + 1;`
   - Test complex expressions: `let x = flight.altitude * 2 + gvar[1];`
   - Test multiple references (expression copied each time)
   - Test reassignment errors

### Phase 3: `var` Support (1.5 days)

*(No changes from your original plan - this part was correct)*

### Phase 4: Integration & Testing (0.5-1 day)

Test with realistic examples combining `let` and `var`.

### Phase 5: Polish (1 day)

Error messages, documentation, edge case handling.

**Revised total estimate: 5-6 days**

## Technical Guidance

### Expression Substitution Details

When resolving a `let` variable reference:

```javascript
// Symbol table entry for 'let' variable:
{
  name: 'mySpeed',
  kind: 'let',
  expressionAST: { type: 'BinaryExpression', operator: '+', left: {...}, right: {...} },
  isConstant: false  // Can be any expression, not just constants
}

// At codegen time, when you see 'mySpeed' identifier:
// 1. Look up in symbol table
// 2. If kind === 'let', return the stored expressionAST
// 3. Generate code from that AST (it will inline the expression)
```

### Preventing Reassignment

```javascript
// Parser should detect:
let foo = 5;
foo = 10;  // AssignmentExpression targeting 'foo'

// Check if 'foo' is in symbol table with kind='let'
// If yes: Error - "Cannot reassign 'let' variable 'foo'"
```

## Questions Answered

> 1. Proceed with implementation?

✅ **YES** - Proceed with revised requirements

> 2. Priority vs Task 1 (CommonJS to ESM)?

CommonJS to ESM is **completed and archived**. This is now the active priority.

> 3. Testing strategy?

Unit tests initially, then manual testing in configurator. SITL testing would be good but not required for initial implementation.

> 4. Documentation location?

Update both:
- Configurator help (user-facing)
- Developer docs in `js/transpiler/docs/` (technical)

> 5. Backward compatibility?

✅ Confirmed - Not required until 2026-01-01

## Additional Code Quality Guidelines

### File Size
- **Guideline:** If a file would be over **150 lines**, consider if it can and should be broken into smaller logical segments
- **Use judgment:** Some cohesive structures (like comprehensive lists) shouldn't be divided
- **Prioritize:** Logical coherence over arbitrary line counts

### Function Length
- **Guideline:** Consider if functions longer than **12 lines** should be divided
- **Look for:** Natural breakpoints or logical sub-tasks
- **Extract:** Helper functions with clear, descriptive names
- **Balance:** Don't over-fragment - some complex algorithms naturally exceed 12 lines

### Rationale
These guidelines improve:
- Code readability and maintainability
- Ease of testing (smaller units)
- Collaboration (smaller diffs, clearer changes)
- Debugging (easier to isolate issues)

## Approval to Proceed

✅ **Approved** to begin implementation with these updated requirements:

1. `let` supports expressions (not just constants)
2. Use helper class(es) to keep NEW code in main files under 40 lines per file
3. Helper class(es) can be 100-200+ lines total - that's fine
4. Consider gvar integration in helper if it makes sense
5. Follow file size (150 lines) and function length (12 lines) guidelines
6. Estimate updated to 5-6 days

## Next Steps

1. **Respond with updated design** showing:
   - Helper class structure (single vs multiple)
   - How expression substitution will work
   - How you'll keep NEW code in main files under 40 lines
   - Whether gvar integration makes sense

2. **After design approval, create git branch** and begin Phase 1

3. **Send status updates** at each phase completion

Looking forward to seeing the updated design!

---

**Manager**
