# Extract Method Refactoring Tool

A command-line tool for analyzing and extracting JavaScript code blocks into separate functions. Uses AST analysis to identify parameters, return values, and verify semantic equivalence.

**Current Version:** 0.3.0 (Phase 3)
**Status:** Analyze and Preview commands functional, Apply coming in Phase 4

---

## Installation

```bash
cd claude/projects/extract-method-tool
npm install
```

### Optional: Global Installation

To use `extract-method` from anywhere:

```bash
npm link
```

This makes the `extract-method` command available globally.

---

## Quick Start

### Analyze a code block

```bash
./bin/extract-method.js analyze <file> --lines <start>-<end>
```

**Example:**
```bash
./bin/extract-method.js analyze src/config.js --lines 145-195
```

**Output:**
```
Analysis of src/config.js lines 145-195:

✓ Extraction is FEASIBLE

Metrics:
  Lines of code: 51
  Statements: 15
  Parent scope: SwitchCase
  Parameters needed: 3 (analysis incomplete)
  Return value: saveResult (analysis incomplete)

Recommendation: ✓ Block appears extractable

Note: Full variable analysis will be implemented in Phase 2
```

---

## Commands

### `analyze` - Check if extraction is feasible

Analyzes a code block and reports whether it can be extracted into a function.

**Usage:**
```bash
extract-method analyze <file> --lines <start>-<end> [options]
```

**Arguments:**
- `<file>` - Path to JavaScript file
- `--lines <start>-<end>` - Line range to analyze (e.g., `10-20`)

**Options:**
- `--json` - Output results as JSON (for scripts/tools)
- `--verbose` - Show detailed AST information
- `--help` - Display help

**Examples:**

Analyze a switch case block:
```bash
extract-method analyze src/app.js --lines 50-75
```

Get JSON output for programmatic use:
```bash
extract-method analyze src/app.js --lines 50-75 --json
```

**JSON Output Format:**
```json
{
  "feasible": true,
  "filePath": "src/app.js",
  "startLine": 50,
  "endLine": 75,
  "lineCount": 26,
  "statementCount": 8,
  "parentType": "FunctionDeclaration",
  "issues": [],
  "metrics": {
    "parameters": [],
    "returnValue": null,
    "controlFlow": {
      "earlyReturns": 0,
      "breaks": 0,
      "continues": 0
    },
    "complexity": 0
  },
  "suggestion": {
    "recommended": true,
    "reason": "Block appears extractable"
  }
}
```

---

### `preview` - Preview extracted function ✅ AVAILABLE

Shows what the extracted function will look like before applying changes.

**Usage:**
```bash
extract-method preview <file> --lines <start>-<end> --name <functionName> [options]
```

**Options:**
- `--json` - Output results as JSON
- `--verbose` - Show detailed error messages

**Status:** ✅ Fully implemented (Phase 3)

---

### `apply` - Apply the extraction (Coming in Phase 4)

Performs the extraction and modifies the source file.

**Usage:**
```bash
extract-method apply <file> --lines <start>-<end> --name <functionName> [--location <where>]
```

**Options:**
- `--location <where>` - Where to place the function: `before`, `after`, or `top` (default: `before`)

**Status:** Not yet implemented

---

## Exit Codes

The tool uses standard exit codes for automation:

- **0** - Success (extraction is feasible)
- **2** - File not found or parse error
- **4** - Extraction not feasible

**Example usage in scripts:**
```bash
if extract-method analyze myfile.js --lines 10-20; then
  echo "Extraction is feasible"
else
  echo "Cannot extract this block"
fi
```

---

## What It Does (Phases 1-3 Complete)

✅ **Analysis (Phase 1)**
- Parses JavaScript files
- Identifies statements in line ranges
- Determines containing scope
- Checks basic feasibility

✅ **Variable Scope Analysis (Phase 2)**
- Detects which variables need to be passed as parameters
- Detects which variables need to be returned
- Analyzes control flow (break, return, continue)
- Identifies warnings (too many parameters, multiple returns)

✅ **Code Generation (Phase 3)**
- Generates extracted function with proper signature
- Transforms control flow (break → return)
- Generates replacement function call
- Provides preview before applying changes
- JSON output for automation

⏳ **Coming in Phase 4:**
- Apply command to modify files
- AST verification with compare-ast
- Backup and rollback support

---

## Common Use Cases

### Extract a long switch case

**Before:**
```javascript
switch(action) {
  case 'save':
    // 50 lines of code here
    validateData();
    checkPermissions();
    const data = collectFormData();
    saveToDatabase(data);
    updateUI();
    // ... 45 more lines
    break;
}
```

**Steps:**
1. Identify the line range (e.g., lines 145-195)
2. Analyze: `extract-method analyze myfile.js --lines 145-195`
3. Preview: `extract-method preview myfile.js --lines 145-195 --name handleSave` (Phase 3)
4. Apply: `extract-method apply myfile.js --lines 145-195 --name handleSave` (Phase 4)

**After:**
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
  updateUI();
  // ... 45 more lines
}
```

---

## Error Messages

### No statements found
```
❌ Extraction is NOT FEASIBLE

Issues:
  ❌ No statements found in the specified line range
```

**Cause:** The line range contains only comments or whitespace.
**Solution:** Adjust the line range to include actual code statements.

---

### Parse error
```
Error: Parse error: Unexpected token (1:5)
```

**Cause:** The JavaScript file has syntax errors.
**Solution:** Fix syntax errors in the file before analyzing.

---

### Invalid line range
```
Error: Invalid line range format. Use: <start>-<end> (e.g., 10-20)
```

**Cause:** Line range format is incorrect.
**Solution:** Use the format `10-20` (numbers separated by a dash).

---

## Tips for Best Results

### Choose complete blocks

Select line ranges that form complete logical units:

✅ **Good:** Entire case block in a switch
```bash
extract-method analyze file.js --lines 10-25  # Full case block
```

❌ **Bad:** Partial statements
```bash
extract-method analyze file.js --lines 12-14  # Middle of a function
```

### Check feasibility first

Always run `analyze` before attempting extraction:

```bash
# Step 1: Check if extraction is possible
extract-method analyze myfile.js --lines 50-100

# Step 2: If feasible, preview the changes (Phase 3)
# extract-method preview myfile.js --lines 50-100 --name myFunction

# Step 3: If preview looks good, apply (Phase 4)
# extract-method apply myfile.js --lines 50-100 --name myFunction
```

---

## Testing

The tool includes comprehensive tests:

```bash
# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

Test fixtures are available in `test/fixtures/` for reference.

---

## Integration with Tools

### Using with Claude Code

Claude Code can call this tool via the Bash tool:

```javascript
// Analyze a code block
const result = await bash('extract-method analyze file.js --lines 10-20 --json');
const analysis = JSON.parse(result);

if (analysis.feasible) {
  // Show user the analysis and offer to extract
}
```

### Using in scripts

```bash
#!/bin/bash
# Script to analyze multiple files

for file in src/*.js; do
  if extract-method analyze "$file" --lines 50-100 --json > /dev/null 2>&1; then
    echo "$file: Extraction feasible"
  fi
done
```

---

## Current Limitations (Phase 3)

- ❌ **No file modification** - Cannot apply extractions yet (Phase 4)
- ❌ **No verification** - No AST-based equivalence checking yet (Phase 4)
- ❌ **No backup/rollback** - No safety net for file modifications yet (Phase 4)

These features are planned for Phase 4.

---

## Version History

### 0.3.0 (Phase 3) - 2025-12-15
- ✅ `preview` command fully functional
- ✅ Extractor module for code generation
- ✅ Control flow transformation (break → return)
- ✅ Function signature generation with parameters
- ✅ Return statement insertion
- ✅ Replacement call generation
- ✅ 86 passing tests (27 new extractor tests)

### 0.2.0 (Phase 2) - 2025-12-14
- ✅ Variable scope analysis
- ✅ Parameter detection
- ✅ Return value detection
- ✅ Control flow analysis
- ✅ 59 passing tests (20 new scope analyzer tests)

### 0.1.0 (Phase 1) - 2025-12-14
- ✅ Initial release
- ✅ `analyze` command with basic feasibility checking
- ✅ JSON output support
- ✅ Line-to-AST mapping
- ✅ Statement detection
- ✅ 39 passing tests

---

## Getting Help

### Command-line help

```bash
extract-method --help                    # General help
extract-method analyze --help            # Help for analyze command
```

### Documentation files

- `PHASE1_COMPLETE.md` - Phase 1 completion details
- `CLI_SPEC.md` - Complete CLI specification
- `README_CURRENT.md` - Current status quick reference

---

## License

ISC

---

## Feedback

This tool is under active development. Current phase: **Phase 3 Complete** (Analyze and Preview commands).

Upcoming phases:
- **Phase 4** - Apply command (modify files with verification)
