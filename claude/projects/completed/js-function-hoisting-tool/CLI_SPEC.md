# Extract Method Refactoring Tool - CLI Specification

**Project:** js-function-hoisting-tool (renamed to extract-method-tool)
**Type:** Extract Method Refactoring CLI
**Created:** 2025-12-14
**Updated:** 2025-12-14

---

## Overview

A CLI tool for extracting blocks of code into separate functions with verification of semantic equivalence.

**Key Principle:** User specifies line numbers → Tool analyzes → Reports metrics → User confirms → Tool applies with verification

---

## CLI Design

### Tool Name: `extract-method`

### Usage Modes

#### Mode 1: Analyze (check if extraction is reasonable)
```bash
extract-method analyze <file> --lines <start>-<end>

# Example
extract-method analyze src/config.js --lines 145-195
```

**Output:**
```
Analysis of src/config.js lines 145-195:

✓ Extraction is FEASIBLE

Metrics:
  Lines of code: 51
  Parameters needed: 3
    - userData (used, not defined)
    - config (used, not defined)
    - options (used, not defined)
  Return value: saveResult (modified, used after block)
  Control flow: 1 early return, 0 breaks, 0 continues
  External dependencies: 2 functions (validateData, saveToDatabase)
  Complexity: Medium

Recommendation: ✓ Good candidate for extraction

Suggested function name: handleSave (based on context)

Next: Run with --preview to see the extraction
```

#### Mode 2: Preview (show what it would look like)
```bash
extract-method preview <file> --lines <start>-<end> [--name <functionName>]

# Example
extract-method preview src/config.js --lines 145-195 --name handleSave
```

**Output:**
```
Preview of extraction from src/config.js lines 145-195:

==== EXTRACTED FUNCTION ====

function handleSave(userData, config, options) {
  if (!validateData(userData)) {
    return { success: false, error: 'Invalid data' };
  }

  const processed = processUserData(userData, config);
  const saveResult = saveToDatabase(processed, options);

  if (saveResult.success) {
    updateUI(saveResult);
    logAction('save', saveResult);
  }

  return saveResult;
}

==== MODIFIED SWITCH CASE ====

  case 'save':
    saveResult = handleSave(userData, config, options);
    break;

==== VERIFICATION ====
✓ AST comparison: PASS (semantically equivalent)
✓ No variable scope issues
✓ Control flow preserved

Next: Run with --apply to make changes
```

#### Mode 3: Apply (actually do it)
```bash
extract-method apply <file> --lines <start>-<end> --name <functionName> [--location <before|after|top>]

# Example
extract-method apply src/config.js --lines 145-195 --name handleSave --location before
```

**Output:**
```
Applying extraction to src/config.js...

✓ Extracted 51 lines to function handleSave()
✓ Updated original location (line 145)
✓ Inserted function at line 130 (before switch statement)
✓ AST verification: PASS
✓ File written successfully

Changes:
  Lines extracted: 145-195 (51 lines)
  New function: handleSave() at line 130
  Original code replaced: line 145 (now 1 line)
  Net change: -50 lines

Done! Review changes and test thoroughly.
```

#### Mode 4: One-Step (analyze + preview + apply)
```bash
extract-method auto <file> --lines <start>-<end> --name <functionName>

# Example
extract-method auto src/config.js --lines 145-195 --name handleSave
```

Shows analysis + preview, prompts for confirmation, then applies.

---

## CLI Options

### Global Options
```
--help              Show help
--version           Show version
--verbose           Verbose output (show AST details)
--dry-run           Show what would happen without changing files
```

### Extraction Options
```
--lines <start>-<end>     Line range to extract (REQUIRED)
--name <functionName>     Name for extracted function (required for apply)
--location <where>        Where to place function (default: before)
                          Options: before, after, top (of file)
--no-verify               Skip AST verification (not recommended)
--format                  Run prettier/formatter after extraction
```

### Analysis Options
```
--max-params <n>          Warn if parameters exceed n (default: 5)
--max-complexity <n>      Warn if complexity exceeds n (default: 10)
```

---

## Exit Codes

```
0   Success
1   Invalid arguments
2   File not found
3   Invalid line range
4   Extraction not feasible (too many params, scope issues, etc.)
5   AST verification failed
6   File write error
```

---

## Output Formats

### Default: Human-readable text
```bash
extract-method analyze src/config.js --lines 145-195
```

### JSON output (for programmatic use)
```bash
extract-method analyze src/config.js --lines 145-195 --json
```

**Output:**
```json
{
  "feasible": true,
  "metrics": {
    "linesOfCode": 51,
    "parameters": [
      { "name": "userData", "reason": "used-not-defined" },
      { "name": "config", "reason": "used-not-defined" },
      { "name": "options", "reason": "used-not-defined" }
    ],
    "returnValue": {
      "name": "saveResult",
      "reason": "modified-used-after"
    },
    "controlFlow": {
      "earlyReturns": 1,
      "breaks": 0,
      "continues": 0
    },
    "externalDeps": ["validateData", "saveToDatabase"],
    "complexity": 7
  },
  "recommendation": "good-candidate",
  "suggestedName": "handleSave"
}
```

---

## Implementation Architecture

### Tech Stack

```
extract-method (CLI)
├── Commander.js (CLI framework)
├── Acorn (JavaScript parser)
├── jscodeshift / recast (AST manipulation)
├── compare-ast (semantic verification)
└── Chalk (colored output)
```

### File Structure

```
claude/projects/extract-method-tool/
├── package.json
├── bin/
│   └── extract-method          # CLI entry point
├── src/
│   ├── cli.js                  # CLI interface
│   ├── analyzer.js             # Analyzes code block
│   ├── extractor.js            # Performs extraction
│   ├── verifier.js             # AST verification
│   └── utils/
│       ├── parser.js           # Acorn wrapper
│       ├── scope-analyzer.js   # Variable scope analysis
│       └── formatter.js        # Code formatting
└── test/
    ├── fixtures/               # Test files
    └── *.test.js               # Tests
```

### Core Modules

#### 1. Analyzer (`src/analyzer.js`)
```javascript
export function analyzeExtraction(filePath, startLine, endLine) {
  // 1. Parse file to AST
  // 2. Extract block AST nodes
  // 3. Analyze variable usage:
  //    - Variables used but not defined → parameters
  //    - Variables defined and used after → return value
  // 4. Detect control flow (return, break, continue)
  // 5. Calculate complexity
  // 6. Return metrics

  return {
    feasible: boolean,
    metrics: {...},
    issues: [...],
    suggestion: {...}
  };
}
```

#### 2. Extractor (`src/extractor.js`)
```javascript
export function extractMethod(filePath, options) {
  // 1. Parse file to AST
  // 2. Extract block nodes
  // 3. Build new function:
  //    - Generate parameters
  //    - Generate return statement
  //    - Handle control flow transformations
  // 4. Replace original with function call
  // 5. Insert function at specified location
  // 6. Generate transformed code

  return {
    originalCode: string,
    transformedCode: string,
    extractedFunction: string,
    location: {...}
  };
}
```

#### 3. Verifier (`src/verifier.js`)
```javascript
export function verifyEquivalence(original, transformed) {
  // 1. Parse both to AST
  // 2. Use compare-ast to check equivalence
  // 3. Check variable scopes match
  // 4. Return verification result

  return {
    passed: boolean,
    issues: [...],
    astDiff: {...}
  };
}
```

---

## Variable Analysis Algorithm

This is the critical part - determining parameters and return values.

### Parameters Detection

A variable becomes a **parameter** if:
1. Used in the extracted block
2. NOT defined in the extracted block
3. Defined BEFORE the extracted block

**Algorithm:**
```javascript
function findParameters(blockAST, beforeAST) {
  const usedVars = findAllUsedVariables(blockAST);
  const definedVars = findAllDefinedVariables(blockAST);
  const availableVars = findAllDefinedVariables(beforeAST);

  // Parameters = (used - defined) ∩ available
  const parameters = usedVars
    .filter(v => !definedVars.has(v))
    .filter(v => availableVars.has(v));

  return parameters;
}
```

### Return Value Detection

A variable becomes the **return value** if:
1. Modified in the extracted block
2. Used AFTER the extracted block

**Algorithm:**
```javascript
function findReturnValue(blockAST, afterAST) {
  const modifiedVars = findAllModifiedVariables(blockAST);
  const usedAfter = findAllUsedVariables(afterAST);

  // Return value = modified ∩ usedAfter
  const returnVars = modifiedVars
    .filter(v => usedAfter.has(v));

  return returnVars;
}
```

### Multiple Return Values

If multiple variables are modified and used after:
```javascript
// Option 1: Return object
return { saveResult, updateStatus, errorLog };

// Option 2: Destructuring
const { saveResult, updateStatus, errorLog } = handleSave(...);
```

---

## Control Flow Transformations

### Handling `break` in switch cases

**Original:**
```javascript
case 'save':
  doSomething();
  if (error) break;
  doMore();
  break;
```

**Extracted:**
```javascript
function handleSave() {
  doSomething();
  if (error) return;  // break → return
  doMore();
}

case 'save':
  handleSave();
  break;
```

### Handling `return` in functions

**Original:**
```javascript
function process() {
  doSetup();
  if (invalid) return null;
  const result = doWork();
  return result;
}
```

**Extracted:**
```javascript
function validateAndDoWork() {
  if (invalid) return null;  // return preserved
  const result = doWork();
  return result;
}

function process() {
  doSetup();
  const result = validateAndDoWork();
  if (result === null) return null;  // Check for early return
  return result;
}
```

### Handling `continue` in loops

**Original:**
```javascript
for (const item of items) {
  if (skip(item)) continue;
  process(item);
}
```

**Extracted:**
```javascript
function processItem(item) {
  if (skip(item)) return false;  // continue → return false
  process(item);
  return true;
}

for (const item of items) {
  processItem(item);
}
```

---

## Example Usage (for Claude Code)

When user asks me to extract a method, I would:

```bash
# Step 1: Analyze
extract-method analyze src/tabs/programming.js --lines 234-298 --json

# Parse JSON output, report to user

# Step 2: Preview (if user wants to see it)
extract-method preview src/tabs/programming.js --lines 234-298 --name handleSaveToFlightController

# Show preview to user, ask for confirmation

# Step 3: Apply (if user confirms)
extract-method apply src/tabs/programming.js --lines 234-298 --name handleSaveToFlightController --location before
```

---

## Dependencies

```json
{
  "dependencies": {
    "acorn": "^8.14.0",
    "commander": "^12.0.0",
    "recast": "^0.23.0",
    "compare-ast": "^2.2.0",
    "chalk": "^5.3.0"
  },
  "devDependencies": {
    "vitest": "^1.0.0",
    "c8": "^8.0.0"
  }
}
```

---

## Error Handling

### Too Many Parameters
```
❌ Extraction not feasible

Issue: Too many parameters required (8)
  - userData, config, options, sessionData, ...

Recommendation: Consider extracting a smaller block
```

### Multiple Return Values
```
⚠️  Warning: Multiple return values detected

Variables modified and used after block:
  - saveResult
  - updateStatus
  - errorLog

Options:
  1. Return object: { saveResult, updateStatus, errorLog }
  2. Split into multiple extractions
  3. Refactor to reduce coupling

Proceed with object return? (yes/no)
```

### Control Flow Issues
```
❌ Extraction not feasible

Issue: Contains 'continue' statement in loop
  Loop is outside the extraction boundary

Recommendation: Extract the entire loop, or use different selection
```

### Scope Issues
```
❌ Extraction not feasible

Issue: Variable 'tempResult' used after block but not defined before
  This suggests the block is not self-contained

Recommendation: Adjust line range to include variable definition
```

---

## Success Metrics

- ✅ Can analyze any valid JavaScript code block
- ✅ Correctly identifies parameters (95%+ accuracy)
- ✅ Correctly identifies return values (95%+ accuracy)
- ✅ AST verification passes for all extractions
- ✅ Handles common control flow patterns
- ✅ Clear error messages for infeasible extractions
- ✅ Easy for Claude Code to use via CLI

---

## Future Enhancements (V2)

- TypeScript support
- Multiple return value strategies (destructuring, tuple, etc.)
- Extract to class method (not just function)
- Interactive mode with prompts
- Batch extraction (extract multiple blocks)
- Integration with git (create commit automatically)

---

## Notes

This tool is **conservative** - it will refuse extraction rather than risk breaking code. When in doubt, it reports the issue and asks the user to adjust the selection.

The tool is designed to be **Claude Code friendly** - JSON output, clear exit codes, and structured output make it easy for me to parse and report to users.
