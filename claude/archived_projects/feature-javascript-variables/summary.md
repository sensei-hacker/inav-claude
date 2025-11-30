# Feature: JavaScript Variables Support in Transpiler

**Status:** ✅ Complete
**Priority:** Medium
**Created:** 2025-11-24
**Design Approved:** 2025-11-24
**Phase 1 Complete:** 2025-11-24
**All Phases Complete:** 2025-11-24
**Completed:** 2025-11-24
**Project Type:** Feature Enhancement
**Branch:** `feature-javascript-variables`
**Commits:** 4 commits (ac6c5e85, 0ec20347, 808c5cbc, 7677e1b9)

## Overview

Add support for JavaScript `let` and `var` variable declarations in the INAV transpiler. This will enable users to write more natural JavaScript code that gets compiled to the logic conditions language.

## Motivation

Currently, users must work directly with global variables (`gvar[0]` through `gvar[7]`), which is unintuitive and error-prone. Supporting JavaScript variable syntax would:

1. Make code more readable and maintainable
2. Allow users to write familiar JavaScript
3. Reduce cognitive load when programming
4. Enable better code organization

## Technical Approach

### Local Variables (`let`)

Local variables would be handled via **constant folding/substitution**:

```javascript
// User writes:
let foo = 5;
gvar[1] = foo;

// Transpiler generates:
gvar[1] = 5;
```

**Implementation:**
- Parse `let` declarations and track in symbol table
- Substitute references with their constant values
- Optimize out the declaration entirely

**Constraints:**
- Must be compile-time constants
- No reassignment allowed (or limited reassignment with substitution)
- Scoping rules need definition

### Global Variables (`var`)

Global variables would be **mapped to available gvar slots**:

```javascript
// User writes:
var foo = 5;
gvar[1] = foo;

// Transpiler generates:
gvar[7] = 5;
gvar[1] = gvar[7];
```

**Implementation:**
- Analyze user code to identify explicitly used gvar slots
- Allocate unused gvar slots (starting from gvar[7] downward) for `var` declarations
- Create mapping table: variable name → gvar index
- Replace all references with corresponding gvar access

**Constraints:**
- Limited to available gvar slots (8 total: gvar[0] through gvar[7])
- Must not conflict with user's explicit gvar usage
- Allocation strategy: high-to-low (start at gvar[7])

### Alternative Approaches to Consider

1. **Different allocation strategy**: Start from gvar[0] and work up?
2. **Explicit annotation**: User specifies which gvar to use (`@gvar(3) var foo`)?
3. **Compiler warnings**: Warn when running out of gvar slots?
4. **Hybrid approach**: Use both substitution and gvar allocation based on usage patterns?

## Decompiler Impact

**Expected behavior:** Decompiler likely **cannot recover** original variable names

- User code: `var foo = 5; gvar[1] = foo;`
- Compiled: `gvar[7] = 5; gvar[1] = gvar[7];`
- Decompiled: `gvar[7] = 5; gvar[1] = gvar[7];` (variable names lost)

**Possible enhancement:** Store variable mapping as metadata (comments? separate file?)

## Scope

### In Scope - Phase 1 (Investigation)
- Analyze current transpiler architecture
- Design variable tracking system
- Evaluate implementation complexity
- Identify edge cases and limitations
- Document proposed approach

### In Scope - Phase 2 (Implementation, if approved)
- Implement `let` constant substitution
- Implement `var` gvar allocation
- Add semantic analysis for variable scoping
- Update error reporting
- Add test cases

### Out of Scope
- `const` declarations (defer to future)
- Object destructuring
- Array destructuring
- Block scoping complexity
- Decompiler recovery of variable names
- Backward compatibility (not required until 2026-01-01)

## Technical Dependencies

- Transpiler parser (`js/transpiler/transpiler/parser.js`)
- Semantic analyzer (`js/transpiler/transpiler/analyzer.js`)
- Code generator (`js/transpiler/transpiler/codegen.js`)
- Symbol table / scope tracking (may need to create)

## Risks and Challenges

1. **Symbol table complexity**: Need proper scoping and tracking
2. **Limited gvar slots**: Only 8 available, could run out quickly
3. **Reassignment handling**: How to handle `let foo = 5; foo = 10;`?
4. **Expression complexity**: Non-constant expressions need gvar allocation
5. **Error messages**: Clear feedback when hitting limitations

## Success Criteria

- [ ] Clear understanding of implementation requirements
- [ ] Documented design for both `let` and `var` support
- [ ] Identified edge cases and limitations
- [ ] Proposed user-facing syntax and semantics
- [ ] Implementation plan with phases

## Open Questions

1. How to handle variable reassignment?
2. What to do when running out of gvar slots?
3. Should block scoping be enforced?
4. How to handle non-constant initializers for `let`?
5. Should we support function parameters as variables?
6. Error handling strategy for unsupported patterns?

## Related Files

- `js/transpiler/transpiler/parser.js` - AST parsing
- `js/transpiler/transpiler/analyzer.js` - Semantic analysis
- `js/transpiler/transpiler/codegen.js` - Code generation
- `js/transpiler/api/definitions/gvar.js` - Global variable API

## Timeline

- **Phase 1 (Investigation)**: 1-2 days
- **Phase 2 (Implementation)**: 3-5 days (if approved)
- **Total**: 4-7 days

## Next Steps

1. Developer investigates current transpiler architecture
2. Developer proposes detailed implementation design
3. Manager reviews and approves/adjusts approach
4. Implementation proceeds in phases
