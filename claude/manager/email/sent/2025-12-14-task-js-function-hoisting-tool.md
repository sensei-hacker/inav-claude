# Task Assignment: JavaScript Function Hoisting Tool

**Date:** 2025-12-14
**Project:** js-function-hoisting-tool
**Priority:** Medium
**Estimated Effort:** 3-4 weeks
**Type:** Tool Development / JavaScript Refactoring

## Task

Build a reliable JavaScript refactoring tool that can automatically hoist (extract) function definitions while guaranteeing 100% semantic equivalence to the original code.

**Key Decision:** Use **jscodeshift** (Facebook's codemod toolkit) rather than building from scratch. This reduces implementation from ~1,300 lines to ~600 lines (54% reduction) while maintaining full control over safety guarantees.

## Why jscodeshift?

After evaluating existing tools, jscodeshift is the best approach:

✅ **Handles infrastructure** - Parsing, AST traversal, code generation
✅ **We control safety** - Implement our own semantic equivalence checks
✅ **Production-ready** - Used by Facebook/React for massive codebases
✅ **Less code** - 54% reduction vs building from scratch
✅ **Already compatible** - Same AST as our Acorn-based transpiler

❌ **Rejected alternative:** babel-plugin-transform-hoist-nested-functions
  - Changes function identity (not semantically equivalent)
  - Experimental, not production-ready

## Project Documentation

**Location:** `claude/projects/js-function-hoisting-tool/`

1. **TOOL_EVALUATION.md** - Research findings and tool comparison (read this first!)
2. **PROJECT_SPEC.md** - Complete technical specification (reference for edge cases)
3. **README.md** - Project overview

## Core Requirements

1. **100% Semantic Equivalence** - Never change program behavior
2. **Safety-First** - When uncertain, refuse to hoist rather than risk changing behavior
3. **Comprehensive Edge Cases** - Handle closures, shadowing, TDZ, `this` binding, etc.
4. **Both APIs** - CLI interface and programmatic API
5. **Verification** - Automated verification of semantic equivalence

## Critical Edge Cases to Handle

Your implementation must correctly detect and handle:

1. **Variable Shadowing** - Functions capturing different variables if hoisted
2. **Temporal Dead Zone (TDZ)** - Functions using variables before declaration
3. **Conditional Definitions** - Functions defined in if/loop blocks
4. **Closure Variables** - Functions that capture outer scope variables
5. **`this` Binding** - Functions depending on dynamic `this`
6. **Arguments Object** - Functions using `arguments`
7. **Recursive Functions** - Self-referencing functions
8. **Mutual Recursion** - Multiple functions calling each other
9. **Generator/Async** - Special function types
10. **Function Expressions** - Named and anonymous function expressions

See `PROJECT_SPEC.md` Section 4 for detailed analysis of each.

## Implementation Phases

### Phase 1: Setup & Learning (3-5 days)
```bash
npm install -g jscodeshift
```

**Tasks:**
- Install jscodeshift and explore the API
- Study examples and documentation (links in TOOL_EVALUATION.md)
- Create "hello world" transformation
- Set up test framework (Vitest or Node test runner)

**Deliverable:** Basic jscodeshift transform that can identify functions

---

### Phase 2: Core Transformation (1 week)

**Tasks:**
- Implement function finder (identify all functions in AST)
- Implement safety analyzer:
  - Variable shadowing detection
  - Temporal Dead Zone detection
  - Closure variable analysis
  - `this` binding analysis
- Implement basic hoisting transformation (simple cases only)

**Deliverable:** Working hoisting for simple, pure functions with no external dependencies

---

### Phase 3: Edge Cases & Validation (1 week)

**Tasks:**
- Handle all 10 critical edge cases from above
- Implement AST-based equivalence verification
- Create comprehensive test suite (50+ test cases)
- Test with real INAV Configurator code samples

**Deliverable:** Robust tool that handles all edge cases safely

---

### Phase 4: Polish & Integration (3-5 days)

**Tasks:**
- CLI wrapper with argument parsing
- Documentation (API docs, usage examples)
- Performance testing (10,000+ LOC files)
- Integration examples

**Deliverable:** Production-ready tool with complete documentation

## Expected Code Structure

```
claude/projects/js-function-hoisting-tool/
├── src/
│   ├── transform.js          # Main jscodeshift transform (~400 lines)
│   ├── safety-analyzer.js    # Edge case detection
│   ├── verifier.js           # AST equivalence checks (~150 lines)
│   └── cli.js                # CLI interface (~50 lines)
├── test/
│   ├── fixtures/             # Test JavaScript files
│   ├── transform.test.js     # Main test suite (50+ cases)
│   └── edge-cases.test.js    # Edge case tests
└── docs/
    ├── API.md                # Programmatic API
    └── EXAMPLES.md           # Usage examples
```

**Total estimate:** ~600 lines of implementation code

## Example Usage (Target API)

### CLI
```bash
# Hoist specific function
js-hoist input.js --function calculateTotal --output output.js

# Hoist all safe functions
js-hoist input.js --all-safe --output output.js

# Dry run (show what would be hoisted)
js-hoist input.js --all-safe --dry-run

# Verify semantic equivalence
js-hoist input.js --all-safe --verify
```

### Programmatic API
```javascript
import { FunctionHoister } from './function-hoister.js';

const hoister = new FunctionHoister();
const result = hoister.hoistFunction(sourceCode, {
  functionName: 'calculateTotal',
  targetScope: 'top-level'
});

console.log(result.code);      // Transformed code
console.log(result.hoisted);   // What was hoisted
console.log(result.skipped);   // What couldn't be hoisted (with reasons)
```

## Learning Resources

**jscodeshift:**
- [GitHub](https://github.com/facebook/jscodeshift) - Official repository
- [Tutorial: Refactoring with Codemods](https://www.toptal.com/javascript/write-code-to-rewrite-your-code) - Comprehensive guide
- [Automated Refactoring with JSCodeShift](https://bacarybruno.substack.com/p/automated-refactoring-with-jscodeshift) - Getting started
- [AST Explorer](https://astexplorer.net/) - Essential tool for understanding AST

**Examples:**
- [react-codemod](https://github.com/reactjs/react-codemod) - Production codemods from React team
- [js-codemod](https://github.com/cpojer/js-codemod) - Collection of JS transformations

## Success Criteria

- [ ] jscodeshift transform correctly identifies all function types
- [ ] Safety analyzer detects all 10 critical edge cases
- [ ] Refuses to hoist unsafe cases with clear explanations
- [ ] Successfully hoists safe functions with verified semantic equivalence
- [ ] Test suite with 50+ cases, all passing
- [ ] CLI interface works as designed
- [ ] Documentation complete (API + examples)
- [ ] Code coverage >90%

## Questions?

If you have questions about:
- **Approach:** See TOOL_EVALUATION.md for detailed comparison
- **Edge cases:** See PROJECT_SPEC.md Section 4
- **jscodeshift API:** Check the learning resources above
- **Architecture:** Ask Manager for clarification

## Starting Point

1. Read `TOOL_EVALUATION.md` (understand why jscodeshift)
2. Install jscodeshift: `npm install -g jscodeshift`
3. Try the [AST Explorer](https://astexplorer.net/) with jscodeshift transform
4. Review the tutorial: [Refactoring with Codemods](https://www.toptal.com/javascript/write-code-to-rewrite-your-code)
5. Create basic transform that finds and logs all functions
6. Reply to Manager with:
   - Confirmation you understand the approach
   - Any questions about the specification
   - Proposed testing framework (Vitest? Node test runner?)
   - Estimated start date

---

**Manager**
