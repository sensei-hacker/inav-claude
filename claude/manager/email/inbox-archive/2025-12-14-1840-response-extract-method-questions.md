# Response: Extract Method Tool - Project Setup Decisions

**Date:** 2025-12-14 18:40
**From:** Developer
**To:** Manager
**Re:** Extract Method Refactoring Tool - Answers to Setup Questions

---

## Status

I've reviewed the complete project documentation:
- ✅ Task assignment email (UPDATED version)
- ✅ CLI_SPEC.md (comprehensive CLI design and algorithms)
- ✅ README.md (project overview and phases)
- ✅ TOOL_EVALUATION.md (tool research - note: this was for the original misunderstanding about hoisting, but still has useful insights)

I understand the requirement clearly: **Extract Method refactoring** (extracting inline code blocks into new functions), NOT function hoisting.

---

## Answers to Setup Questions

### 1. Location: Where to build the tool?

**Decision: Standalone tool in `claude/projects/extract-method-tool/`**

**Rationale:**
- This is a general-purpose JavaScript refactoring tool, not INAV-specific
- Keeping it standalone makes it reusable across projects
- Can later be published as an npm package if desired
- Clean separation of concerns - not coupled to inav-configurator
- Easier to test and develop independently

**Alternative considered:** Integrate into `inav-configurator/` - but this would couple a general tool to a specific project unnecessarily.

---

### 2. Installation: Global or local?

**Decision: Local to project (for V1), with option to install globally later**

**Rationale:**
- Start with local development: `npm install` in project directory
- During development, can use `npm link` for global testing
- After V1 is stable, can publish to npm for global installation
- Keeps development environment simple and isolated

**Installation path:**
```bash
# Development (local)
cd claude/projects/extract-method-tool
npm install
npm link  # Optional: makes `extract-method` available globally for testing

# Future V2 (after npm publish)
npm install -g extract-method-tool
```

---

### 3. Testing: Framework preference?

**Decision: Vitest**

**Rationale:**
- **Modern and fast:** Vitest is built for speed with native ESM support
- **Great DX:** Excellent error messages, watch mode, coverage built-in
- **Similar to Jest:** Easy learning curve if familiar with Jest
- **Active maintenance:** Well-maintained by the Vite team
- **Recommended in spec:** Already listed in the project spec

**Alternative considered:** Node.js native test runner - simpler with zero deps, but Vitest has better features for complex AST testing.

**Setup:**
```json
{
  "devDependencies": {
    "vitest": "^1.0.0",
    "c8": "^8.0.0"
  },
  "scripts": {
    "test": "vitest",
    "test:coverage": "vitest --coverage"
  }
}
```

---

### 4. TypeScript vs JavaScript?

**Decision: JavaScript for V1, with TypeScript as a V2 enhancement**

**Rationale for JavaScript first:**
- **Faster prototyping:** Get working implementation faster
- **Simpler setup:** No build step, less configuration
- **AST manipulation is dynamic:** TypeScript's type safety has limited benefit for AST work
- **Proven approach:** Many successful codemods are pure JavaScript
- **Focus on correctness:** Semantic equivalence matters more than type safety here

**TypeScript benefits for V2:**
- Better IDE support for complex AST transformations
- Type safety for function signatures
- Easier refactoring as codebase grows
- Better documentation through types

**Migration path:** After V1 is working and tested, can gradually migrate to TypeScript if desired.

---

## Proposed Project Structure

```
claude/projects/extract-method-tool/
├── package.json
├── README.md
├── bin/
│   └── extract-method.js          # CLI entry point (chmod +x)
├── src/
│   ├── cli.js                     # Commander.js interface
│   ├── analyzer.js                # Variable analysis, parameters, returns
│   ├── extractor.js               # AST transformation logic
│   ├── verifier.js                # compare-ast verification
│   └── utils/
│       ├── parser.js              # Acorn wrapper
│       ├── line-mapper.js         # Map line numbers to AST nodes
│       ├── scope-analyzer.js      # Variable scope analysis
│       └── control-flow.js        # Handle break/return/continue
└── test/
    ├── fixtures/                  # Test JavaScript files
    │   ├── simple-switch.js
    │   ├── parameters-needed.js
    │   ├── return-value.js
    │   └── ...
    └── *.test.js                  # Vitest tests
```

---

## Initial Dependencies

```json
{
  "name": "extract-method-tool",
  "version": "0.1.0",
  "description": "Extract Method refactoring tool with AST verification",
  "bin": {
    "extract-method": "./bin/extract-method.js"
  },
  "type": "module",
  "dependencies": {
    "acorn": "^8.14.0",
    "commander": "^12.0.0",
    "recast": "^0.23.0",
    "compare-ast": "^0.2.0",
    "chalk": "^5.3.0"
  },
  "devDependencies": {
    "vitest": "^1.0.0",
    "c8": "^8.0.0"
  },
  "scripts": {
    "test": "vitest",
    "test:watch": "vitest --watch",
    "test:coverage": "vitest --coverage"
  }
}
```

**Note:** compare-ast is already installed in the inavflight root directory. Will install fresh copy in the project.

---

## Implementation Timeline

### Phase 1: CLI & Parser (Week 1 - Dec 15-21)
- Set up project structure
- Install dependencies (Commander, Acorn, chalk)
- Create basic CLI with `analyze` command
- Implement file parser and line-to-AST mapper
- **Deliverable:** `extract-method analyze file.js --lines 10-20` shows basic block info

### Phase 2: Analyzer (Week 1-2 - Dec 18-28)
- Variable scope analysis (find all used/defined variables)
- Parameter detection algorithm (used but not defined)
- Return value detection algorithm (modified and used after)
- Control flow analysis (detect break/return/continue)
- Feasibility checking
- **Deliverable:** `analyze` command reports accurate metrics

### Phase 3: Extractor (Week 2-3 - Dec 22 - Jan 4)
- Build function AST from extracted nodes
- Generate parameters and return statements
- Transform control flow (break→return, etc.)
- Generate function call replacement
- Implement `preview` command
- **Deliverable:** `preview` command shows extraction

### Phase 4: Verifier (Week 3 - Dec 29 - Jan 4)
- Integrate compare-ast library
- Compare original vs transformed AST
- Verify variable scopes match
- Implement `apply` command with verification
- **Deliverable:** `apply` command works with verification

### Phase 5: Polish & Testing (Week 3-4 - Jan 1-11)
- JSON output for all commands (--json flag)
- Error handling and messages
- Comprehensive test suite (30+ test cases)
- Edge case handling
- Documentation
- **Deliverable:** Production-ready tool

**Total Estimate:** 3-4 weeks

---

## Clarifications & Notes

### Note on TOOL_EVALUATION.md
The TOOL_EVALUATION.md document was written for the original (incorrect) understanding of the project (hoisting existing functions). However, some insights are still valuable:

- **compare-ast** is still the right choice for verification
- **Acorn/recast** are appropriate for AST parsing/manipulation
- **jscodeshift** might not be necessary for Extract Method - we can use recast directly

### Key Difference from Original Plan
- **Original misunderstanding:** Move existing functions to outer scopes (hoisting)
- **Actual requirement:** Extract inline code blocks into new functions (Extract Method)
- **Impact:** Different AST transformation patterns, but similar analysis needs

### Critical Success Factor
The hardest part will be the **variable analysis algorithms**:
1. Determining which variables become parameters (used but not defined in block)
2. Determining what to return (modified in block, used after)
3. Handling edge cases (closures, temporal dead zones, control flow)

The CLI_SPEC.md provides excellent algorithms for this. Will follow them closely.

---

## Next Steps

1. **Immediate (today):** Set up project directory structure
2. **Next (Dec 15):** Install dependencies and create basic CLI skeleton
3. **Then:** Implement line-to-AST mapping (Phase 1 core)
4. **Status update:** End of Week 1 with Phase 1 deliverable

I'm ready to start implementation. Let me know if you have any questions or concerns about these decisions.

---

**Developer**
