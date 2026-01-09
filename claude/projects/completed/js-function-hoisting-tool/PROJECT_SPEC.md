# JavaScript Function Hoisting Tool - Project Specification

**Project:** js-function-hoisting-tool
**Status:** Planning
**Priority:** Medium
**Assigned to:** Developer
**Created:** 2025-12-14

---

## 1. Project Overview

### 1.1 Purpose
Build a reliable JavaScript refactoring tool that can automatically hoist (extract) function definitions from JavaScript code while maintaining 100% semantic equivalence to the original code. The tool must handle modern JavaScript (ES2020+) and detect all edge cases where hoisting would change program behavior.

### 1.2 Background
The existing INAV Configurator transpiler already uses Acorn v8.14.0 for parsing JavaScript code. This project will build upon that foundation to create a specialized refactoring tool for function extraction/hoisting.

### 1.3 Success Criteria
- Tool correctly hoists function declarations and function expressions
- Output code is semantically equivalent to input (verified via automated testing)
- Tool detects and reports cases where hoisting would change behavior
- Comprehensive test suite covering all edge cases
- Clean API suitable for integration into existing tools

---

## 2. Requirements

### 2.1 Functional Requirements

**FR-1: Parse JavaScript Code**
- Use Acorn parser if it makes sense for this project (already available in project dependencies)
- Support ECMAScript 2020+ syntax
- Preserve source locations for error reporting
- Handle both scripts and modules

**FR-2: Identify Hoistable Functions**
- Detect function declarations
- Detect function expressions (named and anonymous)
- Detect arrow functions
- Detect methods in objects and classes

**FR-3: Analyze Semantic Safety**
- Detect variable shadowing conflicts
- Detect temporal dead zone (TDZ) violations
- Detect closure variable dependencies
- Detect usage-before-definition conflicts
- Detect conditional definitions (functions in if/loop blocks)
- Detect recursive references
- Detect `this` binding issues

**FR-4: Perform Safe Hoisting**
- Extract function to top-level or appropriate scope
- Preserve function name and parameters
- Maintain closure captures when necessary
- Generate syntactically valid output code
- Preserve code formatting where possible

**FR-5: Report Unsafe Cases**
- Provide clear error messages for unhoist-able functions
- Include line/column information
- Explain why hoisting would be unsafe
- Suggest alternatives when possible

**FR-6: Verification**
- Provide option to verify semantic equivalence
- Compare AST structures before/after
- Optional runtime verification (if eval-based testing is enabled)

### 2.2 Non-Functional Requirements

**NFR-1: Reliability**
- 100% semantic equivalence guarantee
- Fail-safe: if uncertain, refuse to hoist rather than risk changing behavior
- Comprehensive error handling

**NFR-2: Performance**
- Minimal memory overhead

**NFR-3: Maintainability**
- Well-documented code
- Modular architecture
- Comprehensive test coverage (>90%)
- Clear separation of concerns

**NFR-4: Usability**
- Simple CLI interface OR Programmatic API for integration
- Clear, actionable error messages
- Optional verbose mode for debugging

---

## 3. Technical Design

### 3.1 Architecture

```
┌─────────────────────────────────────────┐
│         Function Hoisting Tool          │
└─────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    ┌───▼───┐           ┌────▼────┐
    │ CLI   │           │   API   │
    └───┬───┘           └────┬────┘
        │                    │
        └──────────┬─────────┘
                   │
        ┌──────────▼──────────┐
        │   Hoisting Engine   │
        └──────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐    ┌────▼─────┐   ┌───▼────┐
│Parser │    │ Analyzer │   │Codegen │
│(Acorn)│    │          │   │        │
└───┬───┘    └────┬─────┘   └───┬────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
          ┌───────▼────────┐
          │   Verifier     │
          │  (Optional)    │
          └────────────────┘
```

### 3.2 Core Components

**3.2.1 Parser (Acorn wrapper)**
- Input: JavaScript source code (string)
- Output: Acorn AST with locations and ranges
- Configuration: ECMAScript 2020, module/script mode
- Error handling: Syntax error reporting with location

**3.2.2 Function Finder**
- Input: Acorn AST
- Output: List of function nodes with metadata
- Identifies:
  - Function declarations
  - Function expressions
  - Arrow functions
  - Object methods
  - Class methods
- Metadata: name, location, parent scope, parameters

**3.2.3 Safety Analyzer**
- Input: Function node + AST context
- Output: Safety report (safe/unsafe + reasons)
- Checks:
  - Scope analysis (no shadowing conflicts)
  - Temporal analysis (no TDZ violations)
  - Dependency analysis (closure variables)
  - Control flow analysis (conditional definitions)
  - Binding analysis (`this`, `arguments`, `super`)
  - Hoisting conflicts (variable vs function name)

**3.2.4 Code Generator**
- Input: Function node + target location
- Output: Transformed source code
- Preserves:
  - Function implementation exactly
  - Comments (where possible)
  - Source formatting (basic)
- Generates:
  - Hoisted function at target location
  - Updated code at original location

**3.2.5 Verifier (Optional)**
- Input: Original code + transformed code
- Output: Equivalence report
- Methods:
  - AST structural comparison
  - Symbol table comparison
  - Optional: Runtime behavior comparison (with test inputs)

### 3.3 Technology Stack

**Core Dependencies:**
- **Acorn** v8.14.0+ - JavaScript parser (already in package.json)
- **Node.js** v16+ - Runtime environment
- **ESM modules** - Module system

**Additional Dependencies (to be added):**
- **escodegen** or **recast** - Code generation with formatting preservation
- **estraverse** - AST traversal utilities (optional, can use Acorn's walk)
- **chalk** - CLI color output (optional)

**Development Dependencies:**
- **Node.js test runner** or **Vitest** - Testing framework
- **c8** or **nyc** - Code coverage

### 3.4 API Design

#### 3.4.1 Programmatic API

```javascript
import { FunctionHoister } from './function-hoister.js';

const hoister = new FunctionHoister({
  ecmaVersion: 2020,
  sourceType: 'module',
  preserveFormatting: true,
  verify: true
});

// Hoist a specific function by name
const result = hoister.hoistFunction(sourceCode, {
  functionName: 'calculateTotal',
  targetScope: 'top-level'
});

// Hoist all safe functions
const result = hoister.hoistAllSafe(sourceCode);

// Result object:
{
  success: boolean,
  code: string,              // Transformed code
  hoisted: Array<{           // Functions that were hoisted
    name: string,
    originalLine: number,
    newLine: number
  }>,
  skipped: Array<{           // Functions that couldn't be hoisted
    name: string,
    line: number,
    reason: string
  }>,
  warnings: Array<string>,
  verified: boolean          // If verification was run
}
```

#### 3.4.2 CLI Interface

```bash
# Hoist specific function
js-hoist input.js --function calculateTotal --output output.js

# Hoist all safe functions
js-hoist input.js --all-safe --output output.js

# Dry run (report what would be hoisted)
js-hoist input.js --all-safe --dry-run

# Verify semantic equivalence
js-hoist input.js --all-safe --verify

# Verbose output
js-hoist input.js --all-safe --verbose
```

---

## 4. Edge Cases and Safety Analysis

### 4.1 Critical Edge Cases to Handle

**EC-1: Variable Shadowing**
```javascript
// UNSAFE to hoist - would change `x` binding
let x = 1;
function outer() {
  let x = 2;
  function inner() { return x; }  // Returns 2, not 1
  return inner();
}
```

**EC-2: Temporal Dead Zone**
```javascript
// UNSAFE to hoist - TDZ violation
function useValue() {
  return value;  // ReferenceError if hoisted before declaration
}
const value = 42;
useValue();
```

**EC-3: Conditional Definitions**
```javascript
// UNSAFE to hoist - function only exists conditionally
if (someCondition) {
  function conditionalFunc() { }
}
```

**EC-4: Closure Variables**
```javascript
// SAFE but requires analysis - must preserve closure
function makeCounter() {
  let count = 0;
  function increment() { return ++count; }  // Captures `count`
  return increment;
}
```

**EC-5: `this` Binding**
```javascript
// UNSAFE to hoist - `this` binding would change
const obj = {
  value: 42,
  getValue: function() { return this.value; }  // Arrow function would change semantics
};
```

**EC-6: Arguments Object**
```javascript
// SAFE - arguments still available when hoisted
function outer() {
  function inner() {
    return arguments;  // Refers to inner's arguments, safe
  }
  return inner;
}
```

**EC-7: Recursive Functions**
```javascript
// SAFE - name binding preserved
function factorial(n) {
  return n <= 1 ? 1 : n * factorial(n - 1);
}
```

**EC-8: Function Expression Assignment**
```javascript
// Context-dependent - analyze usage
const fn = function namedFn() { };  // Can hoist with care
```

**EC-9: Mutual Recursion**
```javascript
// SAFE but complex - both must be hoisted together
function isEven(n) { return n === 0 || isOdd(n - 1); }
function isOdd(n) { return n !== 0 && isEven(n - 1); }
```

**EC-10: Generator and Async Functions**
```javascript
// SAFE - special function types preserved
async function* asyncGen() { yield await Promise.resolve(1); }
```

### 4.2 Safety Decision Matrix

| Scenario | Safe to Hoist? | Conditions |
|----------|---------------|------------|
| Function declaration at top-level | ✅ YES | Always safe |
| Function declaration in block scope | ❌ NO | Conditional definition |
| Function expression (const/let) | ⚠️ DEPENDS | Check TDZ and usage |
| Function expression (var) | ⚠️ DEPENDS | Check hoisting conflicts |
| Arrow function | ⚠️ DEPENDS | Check `this` binding |
| Method in object literal | ❌ NO | `this` binding issue |
| Class method | ❌ NO | Part of class structure |
| Nested function (pure) | ✅ YES | No external dependencies |
| Nested function (closure) | ⚠️ DEPENDS | Must preserve closures |
| IIFE | ❌ NO | Immediately invoked |
| Generator function | ✅ YES | Same as regular function |
| Async function | ✅ YES | Same as regular function |

---

## 5. Implementation Plan

### 5.1 Phase 1: Core Infrastructure (Week 1)
- **Task 1.1:** Set up project structure and build system
- **Task 1.2:** Implement Parser wrapper around Acorn
- **Task 1.3:** Implement Function Finder
- **Task 1.4:** Create basic test framework
- **Deliverable:** Can parse JS and identify all functions

### 5.2 Phase 2: Safety Analysis (Week 2)
- **Task 2.1:** Implement scope analyzer
- **Task 2.2:** Implement temporal analyzer (TDZ detection)
- **Task 2.3:** Implement closure dependency analyzer
- **Task 2.4:** Implement binding analyzer (`this`, `arguments`)
- **Task 2.5:** Write comprehensive edge case tests
- **Deliverable:** Can accurately classify functions as safe/unsafe to hoist

### 5.3 Phase 3: Code Generation (Week 3)
- **Task 3.1:** Implement basic code generator
- **Task 3.2:** Add formatting preservation
- **Task 3.3:** Handle edge cases (comments, whitespace)
- **Task 3.4:** Implement variable renaming (if needed)
- **Deliverable:** Can generate syntactically correct hoisted code

### 5.4 Phase 4: Verification & Testing (Week 4)
- **Task 4.1:** Implement AST-based verifier
- **Task 4.2:** Add optional runtime verification
- **Task 4.3:** Create comprehensive test suite (100+ test cases)
- **Task 4.4:** Performance testing and optimization
- **Deliverable:** Fully tested, verified tool

### 5.5 Phase 5: CLI & Documentation (Week 5)
- **Task 5.1:** Implement CLI interface
- **Task 5.2:** Write user documentation
- **Task 5.3:** Write API documentation
- **Task 5.4:** Create usage examples
- **Deliverable:** Production-ready tool with docs

---

## 6. Testing Strategy

### 6.1 Unit Tests
- Parser wrapper: 10+ tests
- Function finder: 20+ tests
- Safety analyzer: 50+ tests (covering all edge cases)
- Code generator: 30+ tests
- Verifier: 15+ tests

### 6.2 Integration Tests
- End-to-end hoisting: 40+ tests
- Real-world code samples: 10+ tests
- Error handling: 20+ tests

### 6.3 Verification Tests
- AST equivalence: All test cases
- Runtime equivalence: Representative sample (10+ cases)
- Performance: Large files (1000+ LOC)

### 6.4 Test Data Sources
- Manually crafted edge cases
- Real code from INAV Configurator transpiler
- Open source JavaScript libraries
- Generated test cases (property-based testing)

---

## 7. Risk Analysis

### 7.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Acorn AST incompatibility | Low | High | Thorough testing, version pinning |
| Edge case missed | Medium | Critical | Comprehensive test suite, safety-first approach |
| Code generation bugs | Medium | High | Verification step, extensive testing |
| Performance issues | Low | Medium | Benchmark early, optimize if needed |
| Formatting preservation failure | Medium | Low | Accept minor formatting changes |

### 7.2 Mitigation Strategies

**Safety-First Approach:**
- When uncertain, refuse to hoist
- Require explicit verification flag for aggressive hoisting
- Provide detailed explanations for rejected cases

**Comprehensive Testing:**
- 100+ test cases covering all edge cases
- Automated verification for every test
- Continuous integration testing

**Incremental Development:**
- Start with simple cases
- Add complexity gradually
- Test each increment thoroughly

---

## 8. Future Enhancements

**V2 Features (Future):**
- Support for TypeScript
- Integration with ESLint
- Auto-fix suggestions
- Batch processing multiple files
- IDE integration (VSCode extension)
- Configurable hoisting strategies
- Partial hoisting (extract to nearest safe scope)
- Performance profiling and optimization suggestions

---

## 9. Dependencies and Prerequisites

### 9.1 Existing Dependencies
- Acorn v8.14.0 (already installed)
- Node.js v16+
- ESM module support

### 9.2 New Dependencies to Add
```json
{
  "dependencies": {
    "recast": "^0.23.0",
    "estraverse": "^5.3.0"
  },
  "devDependencies": {
    "vitest": "^1.0.0",
    "c8": "^8.0.0",
    "chalk": "^5.3.0"
  }
}
```

### 9.3 Development Environment
- Linux/macOS/Windows
- Git for version control
- Editor with JavaScript/ESM support

---

## 10. Deliverables

### 10.1 Code Deliverables
1. `function-hoister.js` - Main hoisting engine
2. `parser.js` - Acorn wrapper
3. `function-finder.js` - Function identification
4. `safety-analyzer.js` - Safety analysis
5. `code-generator.js` - Code transformation
6. `verifier.js` - Semantic equivalence verification
7. `cli.js` - Command-line interface
8. `index.js` - Public API exports

### 10.2 Documentation Deliverables
1. README.md - Overview and quick start
2. API.md - Programmatic API documentation
3. CLI.md - Command-line interface guide
4. EDGE_CASES.md - Detailed edge case documentation
5. EXAMPLES.md - Usage examples

### 10.3 Testing Deliverables
1. Test suite (100+ test cases)
2. Test coverage report (>90% coverage)
3. Performance benchmarks
4. Verification report

---

## 11. Success Metrics

- **Correctness:** 100% semantic equivalence on test suite
- **Coverage:** >90% code coverage
- **Performance:** <1 second for 10,000 LOC files
- **Reliability:** 0 known bugs in production
- **Usability:** Clear documentation, <5 minute getting started

---

## 12. Project Timeline

**Total Duration:** 5 weeks

- Week 1: Core infrastructure
- Week 2: Safety analysis
- Week 3: Code generation
- Week 4: Verification & testing
- Week 5: CLI & documentation

**Milestones:**
- M1 (Week 1): Can parse and identify functions
- M2 (Week 2): Can classify safe/unsafe functions
- M3 (Week 3): Can generate hoisted code
- M4 (Week 4): All tests passing, verified
- M5 (Week 5): Production-ready release

---

## 13. Notes

This tool prioritizes **correctness over convenience**. If there's any doubt about semantic equivalence, the tool will refuse to hoist and explain why. This conservative approach ensures reliability and user trust.

The tool is designed to be standalone but can integrate with the existing INAV Configurator transpiler infrastructure if needed.
