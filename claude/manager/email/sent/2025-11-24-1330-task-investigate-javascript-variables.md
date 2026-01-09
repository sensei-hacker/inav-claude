# Task: Investigate JavaScript Variables Support in Transpiler

**Priority:** Medium
**Estimated Complexity:** Moderate
**Created:** 2025-11-24
**Project:** feature-javascript-variables

## Context

We want to add support for JavaScript variable declarations (`let` and `var`) to the INAV transpiler. This will allow users to write more natural JavaScript code instead of working directly with `gvar[0]` through `gvar[7]`.

This is a feasibility study and design phase. The goal is to understand what would be needed to implement this feature and propose a concrete implementation approach.

## Requirements

### Proposed Behavior

**Local variables with `let`** - Constant folding/substitution:
```javascript
// User writes:
let foo = 5;
gvar[1] = foo;

// Transpiler generates:
gvar[1] = 5;
```

**Global variables with `var`** - Map to available gvar slots:
```javascript
// User writes:
var foo = 5;
gvar[1] = foo;

// Transpiler generates (assuming gvar[7] is unused):
gvar[7] = 5;
gvar[1] = gvar[7];
```

### Allocation Strategy for `var`

- Scan user code to find explicitly used gvar slots
- Allocate unused gvar slots starting from `gvar[7]` working downward
- Create mapping: variable name → gvar index
- Must not conflict with user's explicit gvar usage

## Technical Details

### Files to Investigate

1. **Parser** (`js/transpiler/transpiler/parser.js`)
   - How does it currently parse the AST?
   - Does it already recognize `let`/`var` declarations?
   - What AST node types exist?

2. **Analyzer** (`js/transpiler/transpiler/analyzer.js`)
   - How does semantic analysis work currently?
   - Is there symbol table support?
   - How are gvar references tracked?

3. **Code Generator** (`js/transpiler/transpiler/codegen.js`)
   - How is code currently generated?
   - Where would variable substitution fit?
   - How to implement gvar allocation?

4. **API Definitions** (`js/transpiler/api/definitions/gvar.js`)
   - How are gvars currently defined?
   - Any relevant constraints?

## Acceptance Criteria

Your investigation should produce:

- [ ] **Architecture Analysis** - Document how parser, analyzer, and codegen work
- [ ] **AST Understanding** - Document current AST structure and what changes are needed
- [ ] **Symbol Table Design** - Propose how to track variables and their scopes
- [ ] **Implementation Proposal** - Detailed design for both `let` and `var` support
- [ ] **Edge Cases** - Identify potential problems and limitations
- [ ] **Test Scenarios** - Examples of what should work and what shouldn't
- [ ] **Effort Estimate** - How complex is the implementation?

### Specific Questions to Answer

1. **Parser**: Does Acorn already parse `let`/`var` declarations into the AST?
2. **Symbol Table**: Do we need to build a symbol table from scratch, or is there existing infrastructure?
3. **Gvar Detection**: How can we detect which gvar slots are explicitly used by user code?
4. **Reassignment**: How should we handle `let foo = 5; foo = 10;`?
5. **Non-constants**: How should we handle `let foo = gvar[0] + 1;`?
6. **Scoping**: Should we enforce block scoping or function scoping?
7. **Slot Exhaustion**: What happens when user needs more than 8 gvars total?
8. **Decompiler**: Can we reasonably preserve variable names in decompilation? (Low priority)

## Alternative Approaches to Consider

Feel free to propose alternatives to the basic approach:

1. Different gvar allocation strategy (low-to-high instead of high-to-low?)
2. Explicit annotations for gvar mapping
3. Hybrid approach based on usage patterns
4. Different handling for `let` vs `var`

## References

- Original request: `claude/manager/inbox/2025-11-24-from-ray-variables.md`
- Project documentation: `claude/projects/feature-javascript-variables/`
- Transpiler source: `inav-configurator/js/transpiler/`

## Deliverable

Create a detailed investigation report in `claude/projects/feature-javascript-variables/investigation.md` with:

1. Architecture overview (how transpiler works today)
2. Proposed implementation design
3. Edge cases and limitations
4. Test scenarios
5. Implementation phases/steps
6. Effort estimate

Then send a status report to manager with your findings and recommendations.

## Notes

- Backward compatibility is not a concern until 2026-01-01
- Decompiler recovery of variable names is low priority (nice-to-have)
- Focus on clarity and correctness over optimization initially
- The goal is to make programming in the configurator more intuitive

## Timeline

Aim to complete investigation within 1-2 days of focused work.
