# Extract Method Refactoring Tool

**Status:** 📋 Planning
**Priority:** Medium
**Assigned:** Developer (pending assignment)

## Quick Summary

Build a CLI tool for extracting blocks of code into separate functions with verification of semantic equivalence.

**Key Change:** This is **Extract Method** refactoring (create new functions from inline code), NOT function hoisting (moving existing functions).

## Objective

Create a CLI tool that:
- User specifies line numbers of code to extract
- Tool analyzes the block and reports metrics (parameters needed, return values, complexity)
- Tool shows preview of extraction
- User confirms
- Tool performs extraction and verifies semantic equivalence using AST comparison

## Use Case Example

**Before (long switch case):**
```javascript
switch(action) {
  case 'save':
    // 50 lines of code here
    validateData();
    checkPermissions();
    const data = collectFormData();
    saveToDatabase(data);
    // ... 45 more lines
    break;
}
```

**After extraction:**
```javascript
switch(action) {
  case 'save':
    handleSave();
    break;
}

function handleSave() {
  // 50 lines of code moved here
  validateData();
  checkPermissions();
  const data = collectFormData();
  saveToDatabase(data);
  // ... 45 more lines
}
```

## Key Requirements

1. **Line-Based Selection** - User specifies exact line range to extract
2. **Smart Analysis** - Automatically determine parameters, return values, control flow
3. **Verification** - Use compare-ast to prove semantic equivalence (not just estimate)
4. **LLM-Assisted** - Can use Claude for complex cases, but verify with tools
5. **CLI Interface** - Easy for Claude Code to call via Bash tool
6. **Conservative** - Refuse extraction rather than risk breaking code

## Technology

- **Acorn v8.14.0** - JavaScript parser (already available)
- **Commander.js** - CLI framework
- **recast / jscodeshift** - AST manipulation
- **compare-ast** - Semantic equivalence verification
- **Chalk** - Colored CLI output
- **Node.js v16+** - Runtime

## CLI Interface

```bash
# Analyze a code block
extract-method analyze <file> --lines 145-195

# Preview extraction
extract-method preview <file> --lines 145-195 --name handleSave

# Apply extraction
extract-method apply <file> --lines 145-195 --name handleSave

# JSON output (for Claude Code)
extract-method analyze <file> --lines 145-195 --json
```

See [CLI_SPEC.md](./CLI_SPEC.md) for complete CLI documentation.

## Documentation

- **[CLI_SPEC.md](./CLI_SPEC.md)** - Complete CLI specification and design
- **[TOOL_EVALUATION.md](./TOOL_EVALUATION.md)** - Research findings and tool comparison
- **[PROJECT_SPEC.md](./PROJECT_SPEC.md)** - Original spec (for reference on edge cases)

## Project Structure

```
extract-method-tool/
├── README.md                    # This file
├── CLI_SPEC.md                  # CLI specification
├── TOOL_EVALUATION.md           # Tool research
├── package.json
├── bin/
│   └── extract-method           # CLI entry point
├── src/
│   ├── cli.js                   # CLI interface (Commander.js)
│   ├── analyzer.js              # Code block analysis
│   ├── extractor.js             # Extraction logic
│   ├── verifier.js              # AST verification (compare-ast)
│   └── utils/
│       ├── parser.js            # Acorn wrapper
│       ├── scope-analyzer.js    # Variable scope analysis
│       └── formatter.js         # Code formatting
└── test/
    ├── fixtures/                # Test JavaScript files
    └── *.test.js                # Test suite
```

## Implementation Phases

### Phase 1: CLI & Parser (Week 1)
- Set up project with Commander.js
- Implement file parsing with Acorn
- Create line-to-AST node mapper
- Basic `analyze` command

### Phase 2: Analyzer (Week 1-2)
- Variable scope analysis (parameters detection)
- Return value detection
- Control flow analysis (break, return, continue)
- Complexity calculation
- Feasibility checking

### Phase 3: Extractor (Week 2-3)
- Generate extracted function from AST nodes
- Generate function call replacement
- Handle control flow transformations
- Insert function at specified location
- Output preview mode

### Phase 4: Verifier (Week 3)
- Integrate compare-ast
- AST equivalence checking
- Scope validation
- Report verification results

### Phase 5: Polish & Testing (Week 3-4)
- JSON output for programmatic use
- Error handling and clear messages
- Comprehensive test suite
- Documentation and examples

## Critical Edge Cases

The tool must correctly handle:

1. **Parameters Detection** - Variables used but not defined in block
2. **Return Value Detection** - Variables modified in block and used after
3. **Multiple Return Values** - Returning objects or using destructuring
4. **Control Flow - break** - Transform to `return` in switch cases
5. **Control Flow - return** - Preserve early returns
6. **Control Flow - continue** - Transform to return flags in loops
7. **Scope Issues** - Variables not available at extraction boundary
8. **Too Many Parameters** - Warn when extraction requires excessive params
9. **Side Effects** - Detect modifications to external state
10. **Nested Blocks** - Correctly identify block boundaries

See CLI_SPEC.md for detailed algorithms and transformations.

## Example Usage

### For Claude Code (via Bash tool)
```bash
# Step 1: Analyze the code block
extract-method analyze src/config.js --lines 145-195 --json

# Step 2: Preview the extraction
extract-method preview src/config.js --lines 145-195 --name handleSave

# Step 3: Apply if user confirms
extract-method apply src/config.js --lines 145-195 --name handleSave --location before
```

### For Direct CLI Use
```bash
# Analyze a switch case
extract-method analyze src/tabs/programming.js --lines 234-298

Output:
✓ Extraction is FEASIBLE
  Parameters needed: 3 (userData, config, options)
  Return value: saveResult
  Complexity: Medium

# Preview what it would look like
extract-method preview src/tabs/programming.js --lines 234-298 --name handleSaveToFC

# Apply the extraction
extract-method apply src/tabs/programming.js --lines 234-298 --name handleSaveToFC
```

## Success Metrics

- ✅ Correctly identifies parameters (95%+ accuracy)
- ✅ Correctly identifies return values (95%+ accuracy)
- ✅ AST verification passes for all extractions
- ✅ Handles common control flow patterns (break, return, continue)
- ✅ Clear error messages for infeasible extractions
- ✅ Easy for Claude Code to use via CLI
- ✅ >90% test coverage

## Safety Philosophy

**This tool prioritizes correctness over convenience.**

When there's any doubt about semantic equivalence, the tool will:
1. Refuse to extract
2. Explain exactly why it's infeasible
3. Suggest adjustments to the line range or approach

This conservative approach ensures the tool is trustworthy and reliable. Better to require manual refactoring than to risk breaking code.

## Next Steps for Developer

1. Review [CLI_SPEC.md](./CLI_SPEC.md) - Complete CLI design and algorithms
2. Review [TOOL_EVALUATION.md](./TOOL_EVALUATION.md) - Why we chose this approach
3. Set up project structure with Commander.js
4. Implement Phase 1: CLI & Parser
5. Start with `analyze` command (report metrics only)

## Questions Before Starting

1. **Location:** Build as standalone tool in this directory, or integrate into `inav-configurator/`?
2. **Testing:** Preference for Vitest or Node.js test runner?
3. **TypeScript:** JavaScript for V1, TypeScript for V2?
4. **Installation:** Global npm install (`npm install -g`) or local to inav-configurator?

## Related Resources

- **Acorn:** https://github.com/acornjs/acorn - JavaScript parser
- **Commander.js:** https://github.com/tj/commander.js - CLI framework
- **compare-ast:** https://github.com/jugglinmike/compare-ast - AST equivalence verification
- **Recast:** https://github.com/benjamn/recast - AST manipulation with format preservation
- **jscodeshift:** https://github.com/facebook/jscodeshift - Codemod toolkit (alternative approach)
- **ESTree Spec:** https://github.com/estree/estree - AST format specification

## Contact

For questions or feedback on this specification, please contact the project manager.
