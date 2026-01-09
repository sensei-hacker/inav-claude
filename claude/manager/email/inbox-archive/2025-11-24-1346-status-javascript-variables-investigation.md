# Status Report: JavaScript Variables Support Investigation

**Task Reference:** `claude/developer/inbox/2025-11-24-1330-task-investigate-javascript-variables.md`
**Status:** ✅ Completed
**Date:** 2025-11-24 13:46

## Executive Summary

Investigation **completed successfully**. Adding `let` and `var` support is **feasible and straightforward**. The transpiler has all the necessary infrastructure - just needs integration work.

**Recommendation:** ✅ Proceed with implementation (estimated 5 days)

---

## Progress Summary

Conducted comprehensive investigation of the INAV transpiler architecture. Analyzed parser, analyzer, and code generator to understand how variable support can be integrated. Created detailed implementation design with symbol table architecture, edge case analysis, and test scenarios.

**Key Finding:** Acorn already parses `let`/`var` declarations - we just need to transform and track them!

---

## Work Completed

### 1. Architecture Analysis ✅

**Parser (parser.js):**
- Uses Acorn ECMAScript parser (ES2020)
- Already parses `let`/`var` into `VariableDeclaration` nodes
- Currently ignores all except `const { ... } = inav` destructuring (line 191-207)
- Has infrastructure for extracting identifiers and values

**Analyzer (analyzer.js):**
- Already tracks gvar usage (line 655-700)
- Validates property access and gvar indices
- Has dead code and conflict detection
- **No general symbol table** - needs to be added

**Code Generator (codegen.js):**
- Can resolve identifiers to operands (line 717+)
- Handles expression generation (Math.abs, arithmetic, etc.)
- Can generate intermediate logic conditions
- Has gvar assignment operations (GVAR_SET, GVAR_INC, GVAR_DEC)

**Gvar Constraints:**
- 8 slots total: gvar[0] through gvar[7]
- Range: -1,000,000 to 1,000,000
- Both readable and writable

### 2. Implementation Design ✅

**Created SymbolTable class design:**
```javascript
class SymbolTable {
  - Track variable declarations (name, kind, value, isConstant)
  - Allocate gvar slots for 'var' variables
  - Detect explicitly used gvars to avoid conflicts
  - Resolve variable references during codegen
}
```

**Two-strategy approach:**

**`let` variables** - Constant folding:
- Parser: Extract declaration, validate constant value
- Analyzer: Add to symbol table with constant flag
- Codegen: Substitute references with constant values
- **No gvar usage** - pure compile-time substitution

**`var` variables** - Gvar allocation:
- Parser: Extract declaration
- Analyzer: Scan AST for explicit gvar usage, allocate unused slots
- Codegen: Generate initialization, map references to gvar[N]
- **Uses available gvar slots** - allocated from gvar[7] downward

**Allocation strategy:** High-to-low (start at gvar[7], work down to gvar[0])
- Rationale: Users typically use gvar[0], gvar[1] first - less conflict

### 3. Edge Cases Identified ✅

**Major limitations:**

1. **Slot exhaustion** - Max 8 gvars total (user explicit + variables)
   - Solution: Clear error with guidance to use `let` for constants

2. **`let` reassignment** - Not supported (constant only)
   - Error: "Cannot reassign 'let' variable. Use 'var' for mutable variables"

3. **Non-constant `let`** - Cannot use runtime values
   - Error: "'let' variable must be compile-time constant. Use 'var' for runtime values"

4. **No block scoping** - All variables globally scoped
   - Rationale: INAV logic conditions are flat, no true scoping

5. **Variable names lost** - Decompiler cannot recover original names
   - Future enhancement: metadata comments

6. **Variable shadowing** - Redeclaration is error
   - Error: "Variable 'foo' is already declared"

### 4. Test Scenarios Created ✅

Designed 8 comprehensive test cases covering:
- Basic `let` constant folding
- `let` with expression (constant propagation)
- Basic `var` allocation
- Mixed `let` and `var` usage
- Gvar slot conflict detection
- Error cases (reassignment, non-constant, shadowing)

### 5. Detailed Documentation ✅

**Created comprehensive investigation report:**
- File: `claude/projects/feature-javascript-variables/investigation.md`
- 10 sections, ~600 lines
- Covers architecture, design, edge cases, tests, implementation phases
- Includes code examples and expected output

---

## Answers to Specific Questions

### Q1: Does Acorn already parse `let`/`var` declarations?

✅ **Yes!** Acorn parses them into `VariableDeclaration` AST nodes with `kind: 'let' | 'var'`. We just need to transform them.

### Q2: Do we need to build a symbol table from scratch?

✅ **Yes, but simple.** Need lightweight SymbolTable class (~100 LOC) to track variables, allocate gvars, and resolve references.

### Q3: How to detect which gvar slots are used?

Walk AST and collect all `gvar[N]` references. Analyzer already does this partially for uninitialized warnings (line 655). Just need to expose it.

### Q4: How to handle `let foo = 5; foo = 10;`?

❌ **Not supported.** Error: "Cannot reassign 'let' variable." Rationale: `let` is for constants only.

### Q5: How to handle `let foo = gvar[0] + 1;`?

❌ **Not supported for `let`.** Error: "'let' must be compile-time constant."
✅ **Use `var` instead:** `var foo = gvar[0] + 1;` (allocates gvar, evaluates at runtime)

### Q6: Should we enforce block scoping?

❌ **No (initially).** All variables globally scoped. INAV logic conditions are flat - no true scoping. Future enhancement: scope validation to catch bugs.

### Q7: What happens when >8 gvars needed?

Clear error: "Cannot allocate gvar for variable 'myVar'. All 8 slots in use (5 explicit + 3 variables). Use 'let' for constants."

### Q8: Can we preserve variable names in decompilation?

❌ **Not initially.** Low priority. Future: add metadata comments.

---

## Next Steps

### Immediate (Pending Approval)

1. **Get manager approval** to proceed with implementation
2. **Create git branch** for feature work
3. **Begin Phase 1** (Foundation - 1 day):
   - Create `SymbolTable` class
   - Add to analyzer
   - Implement gvar detection
   - Unit tests

### Implementation Phases (5 days total)

- **Phase 1:** Foundation (1 day) - Symbol table infrastructure
- **Phase 2:** `let` support (1 day) - Constant folding
- **Phase 3:** `var` support (1.5 days) - Gvar allocation
- **Phase 4:** Integration & Testing (0.5 days) - End-to-end tests
- **Phase 5:** Polish (1 day) - Error messages and docs

---

## Files Created

- `claude/projects/feature-javascript-variables/investigation.md` (comprehensive report)

---

## Technical Details

### Recommended Implementation Order

1. **Symbol Table** (`js/transpiler/transpiler/symbol_table.js`)
   - Track variables and their properties
   - Allocate gvar slots
   - Resolve variable references

2. **Parser changes** (`parser.js`)
   - Transform `let` declarations: extract name and constant value
   - Transform `var` declarations: extract name and initializer
   - Handle assignment statements to variables

3. **Analyzer changes** (`analyzer.js`)
   - Add symbol table to constructor
   - Detect explicitly used gvars (scan AST)
   - Validate `let` constants (must be compile-time)
   - Allocate gvar slots for `var` variables
   - Error on reassignment to `let`
   - Error on variable redeclaration

4. **Codegen changes** (`codegen.js`)
   - Pass symbol table to codegen
   - Modify `getOperand()`: check symbol table before gvar/API lookup
   - Generate initialization for `var` declarations
   - Substitute `let` references with constants
   - Map `var` references to allocated gvar slots

### Code Size Estimate

- Symbol table class: ~100 LOC
- Parser changes: ~50 LOC
- Analyzer changes: ~150 LOC
- Codegen changes: ~50 LOC
- **Total: ~350 LOC** (excluding tests and docs)

### Performance Impact

**Minimal.** One additional symbol table lookup per identifier resolution. O(1) with Map data structure.

---

## Recommendations

### ✅ Proceed with Implementation

**Justification:**
1. **Feasible** - Infrastructure exists, straightforward integration
2. **High value** - Major UX improvement for users
3. **Low risk** - Well-scoped, can test incrementally
4. **Fast** - Only 5 days estimated
5. **Extensible** - Foundation for future features (`const`, better scoping)

**Priorities:**
1. Implement `let` first (simpler, covers most use cases)
2. Add `var` second (builds on `let` infrastructure)
3. Polish error messages and documentation

### Alternative Approaches Considered

**Rejected alternatives:**
- Low-to-high gvar allocation (more conflicts)
- Explicit annotations `@gvar(N)` (too verbose)
- Unified strategy for `let`/`var` (wastes gvar slots)

**Current approach is optimal.**

---

## Risk Assessment

### Low Risk ✅

**Mitigations in place:**
- **Slot exhaustion:** Clear errors with guidance
- **No block scoping:** Document limitation clearly
- **Lost variable names:** Document, plan future enhancement
- **Breaking changes:** None (additive feature)

---

## Questions for Manager

1. **Proceed with implementation?** Ready to start Phase 1 immediately.

2. **Priority vs Task 1 (CommonJS to ESM)?** Should I pause this and work on CommonJS conversion first?

3. **Testing strategy:** Should I test in real SITL environment, or unit tests sufficient initially?

4. **Documentation location:** Update user docs in `inavwiki/` or configurator help?

5. **Backward compatibility:** None required until 2026-01-01 (per notes). Confirmed?

---

## Conclusion

Investigation successful. JavaScript variable support is **feasible, valuable, and low-risk**. Ready to implement upon approval.

**Estimated delivery:** 5 days from approval
**Estimated LOC:** ~350 (plus tests)
**Breaking changes:** None (additive feature)

Awaiting your guidance on next steps!
