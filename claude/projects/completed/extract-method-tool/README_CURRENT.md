# Extract Method Refactoring Tool

**Status:** Phase 1 Complete ✅
**Version:** 0.1.0 (Phase 1)
**Last Updated:** 2025-12-14

---

## Quick Start

### Installation
```bash
cd claude/projects/extract-method-tool
npm install
```

### Usage
```bash
# Analyze a code block
./bin/extract-method.js analyze <file> --lines <start>-<end>

# JSON output (for programmatic use)
./bin/extract-method.js analyze <file> --lines <start>-<end> --json

# Get help
./bin/extract-method.js --help
```

### Example
```bash
./bin/extract-method.js analyze test/fixtures/simple-block.js --lines 5-7
```

---

## What Works Now (Phase 1)

✅ **Parse JavaScript files** to AST
✅ **Map line numbers** to AST nodes
✅ **Analyze blocks** for basic extraction feasibility
✅ **Report metrics:**
  - Line count
  - Statement count
  - Parent scope type
  - Basic feasibility checks

✅ **CLI with `analyze` command**
✅ **JSON output** for programmatic use
✅ **Error handling** for invalid inputs
✅ **39 passing tests**

---

## What's Coming

### Phase 2: Smart Variable Analysis (Next)
- Automatic parameter detection
- Return value detection
- Control flow analysis
- Complexity calculation

### Phase 3: Extractor
- Generate extracted function
- Generate replacement call
- Preview command

### Phase 4: Verifier
- AST equivalence checking
- Apply command

---

## Testing

```bash
# Run all tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

**Current Coverage:** 39 tests, all passing ✅

---

## Project Structure

```
extract-method-tool/
├── bin/extract-method.js      # CLI entry point
├── src/
│   ├── analyzer.js            # Block analysis
│   └── utils/
│       ├── parser.js          # Acorn wrapper
│       └── line-mapper.js     # Line-to-AST mapping
└── test/                      # Test suite (39 tests)
```

---

## Documentation

- **[PHASE1_COMPLETE.md](./PHASE1_COMPLETE.md)** - Phase 1 completion report
- **[CLI_SPEC.md](./CLI_SPEC.md)** - Complete CLI specification
- **[README.md](./README.md)** - Original project overview
- **[TOOL_EVALUATION.md](./TOOL_EVALUATION.md)** - Tool research

---

## For Claude Code

This tool is designed to be called via the Bash tool with JSON output:

```javascript
// Example Claude Code usage
const result = await bash(`extract-method analyze file.js --lines 10-20 --json`);
const analysis = JSON.parse(result);

if (analysis.feasible) {
  // Show user the analysis
  // In Phase 2+, this will include parameters and return values
}
```

---

## Notes

- Phase 1 provides basic analysis only
- Variable analysis (parameters, returns) will be in Phase 2
- Currently uses Acorn for parsing
- Ready to integrate recast and compare-ast in later phases

---

**Phase 1 Complete!** 🎉

See [PHASE1_COMPLETE.md](./PHASE1_COMPLETE.md) for full details.
