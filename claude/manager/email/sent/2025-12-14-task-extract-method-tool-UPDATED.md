# Task Assignment: Extract Method Refactoring Tool (UPDATED)

**Date:** 2025-12-14 (Updated)
**Project:** extract-method-tool (formerly js-function-hoisting-tool)
**Priority:** Medium
**Estimated Effort:** 3-4 weeks
**Type:** CLI Tool Development

---

## IMPORTANT: Specification Changed

**Original misunderstanding:** Tool to hoist existing functions to outer scopes

**Actual requirement:** Tool to **extract inline code blocks** into new functions (Extract Method refactoring)

This is a completely different problem! Please disregard the previous assignment email dated 2025-12-14.

---

## Task

Build a CLI tool for **Extract Method** refactoring that:
1. User specifies line numbers of code to extract
2. Tool analyzes and reports metrics (parameters, return values, complexity)
3. Tool shows preview of extraction
4. User confirms
5. Tool performs extraction with AST-verified semantic equivalence

---

## Use Case Example

**Before (long switch case):**
```javascript
switch(action) {
  case 'save':
    // 50 lines of inline code
    validateData();
    checkPermissions();
    const data = collectFormData();
    saveToDatabase(data);
    updateUI();
    logAction('save', data);
    // ... 45 more lines
    break;
}
```

**After extraction:**
```javascript
switch(action) {
  case 'save':
    handleSave();  // Extracted to function
    break;
}

function handleSave() {
  // 50 lines moved here
  validateData();
  checkPermissions();
  const data = collectFormData();
  saveToDatabase(data);
  updateUI();
  logAction('save', data);
  // ... 45 more lines
}
```

---

## CLI Interface Design

### Three Commands

#### 1. Analyze
```bash
extract-method analyze <file> --lines 145-195

Output:
✓ Extraction is FEASIBLE
  Parameters needed: 3 (userData, config, options)
  Return value: saveResult
  Control flow: 1 early return
  Complexity: Medium
```

#### 2. Preview
```bash
extract-method preview <file> --lines 145-195 --name handleSave

Output:
[Shows extracted function code]
[Shows modified original code]
✓ AST verification: PASS
```

#### 3. Apply
```bash
extract-method apply <file> --lines 145-195 --name handleSave
```

### For Claude Code Integration

All commands support `--json` for programmatic use:
```bash
extract-method analyze <file> --lines 145-195 --json
```

This makes it easy for me (Claude Code) to call via Bash tool and parse results.

---

## Core Challenge: Smart Extraction

The hard part is automatically determining:

### 1. Parameters (variables used but not defined in block)

**Algorithm:**
```
parameters = (variables used in block) - (variables defined in block) ∩ (variables available before block)
```

**Example:**
```javascript
// Before block
const userData = getUserData();
const config = getConfig();

// Block to extract (lines 100-120)
if (!validateData(userData)) {  // uses userData
  return false;
}
const processed = processData(userData, config);  // uses both
saveToDatabase(processed);  // uses processed (defined in block)

// Analysis
// Used: userData, config, processed
// Defined: processed
// Parameters: userData, config (used but not defined)
```

### 2. Return Value (variables modified in block and used after)

**Algorithm:**
```
returnValue = (variables modified in block) ∩ (variables used after block)
```

**Example:**
```javascript
// Block (lines 100-120)
let saveResult = null;  // modified
saveResult = saveToDatabase(data);

// After block (line 121+)
if (saveResult.success) {  // used after
  console.log('Saved!');
}

// Analysis
// Modified: saveResult
// Used after: saveResult
// Return value: saveResult
```

### 3. Control Flow Transformations

**break in switch → return**
```javascript
// Original
case 'save':
  doWork();
  if (error) break;  // Exit switch
  doMore();
  break;

// Extracted
function handleSave() {
  doWork();
  if (error) return;  // Exit function
  doMore();
}
```

---

## Project Documentation

**Read these in order:**

1. **[CLI_SPEC.md](claude/projects/js-function-hoisting-tool/CLI_SPEC.md)**
   - Complete CLI design
   - Detailed algorithms for parameter/return detection
   - Control flow transformation patterns
   - Error handling

2. **[README.md](claude/projects/js-function-hoisting-tool/README.md)**
   - Project overview
   - Implementation phases
   - Critical edge cases

3. **[TOOL_EVALUATION.md](claude/projects/js-function-hoisting-tool/TOOL_EVALUATION.md)**
   - Research on existing tools
   - Why we're not using jscodeshift alone
   - Why we're building a custom CLI

---

## Technology Stack

```
Dependencies:
- acorn ^8.14.0          (JavaScript parser - already available)
- commander ^12.0.0      (CLI framework)
- recast ^0.23.0         (AST manipulation with format preservation)
- compare-ast ^2.2.0     (Semantic equivalence verification)
- chalk ^5.3.0           (Colored CLI output)

Dev Dependencies:
- vitest ^1.0.0          (Testing framework)
- c8 ^8.0.0              (Code coverage)
```

---

## Implementation Phases

### Phase 1: CLI & Parser (Week 1)
**Goal:** Parse file and map line numbers to AST nodes

**Tasks:**
- Set up project with Commander.js
- Create Acorn parser wrapper
- Implement line-to-AST-node mapper
- Basic `analyze` command that reports block info

**Deliverable:** `extract-method analyze file.js --lines 10-20` shows basic block info

---

### Phase 2: Analyzer (Week 1-2)
**Goal:** Smart analysis of what becomes parameters/returns

**Tasks:**
- Variable scope analysis (find all used/defined variables)
- Parameter detection algorithm
- Return value detection algorithm
- Control flow analysis (detect break/return/continue)
- Complexity calculation
- Feasibility checking (too many params, scope issues, etc.)

**Deliverable:** `analyze` command reports accurate metrics

---

### Phase 3: Extractor (Week 2-3)
**Goal:** Generate the extracted function

**Tasks:**
- Build function AST from extracted block nodes
- Generate parameters list
- Generate return statement
- Transform control flow (break→return, etc.)
- Generate function call to replace original
- Insert function at specified location
- Implement `preview` command

**Deliverable:** `preview` command shows extraction

---

### Phase 4: Verifier (Week 3)
**Goal:** Prove semantic equivalence

**Tasks:**
- Integrate compare-ast library
- Compare original vs transformed AST
- Verify variable scopes match
- Report verification results
- Implement `apply` command with verification

**Deliverable:** `apply` command works with verification

---

### Phase 5: Polish & Testing (Week 3-4)
**Goal:** Production-ready tool

**Tasks:**
- JSON output for all commands
- Error handling and messages
- Comprehensive test suite (30+ test cases)
- Edge case handling
- Documentation

**Deliverable:** Fully tested, documented tool

---

## Critical Algorithms

### Line-to-AST Node Mapping

```javascript
function getNodesForLines(ast, startLine, endLine) {
  const nodes = [];

  traverse(ast, {
    enter(node) {
      if (node.loc) {
        const nodeLine = node.loc.start.line;
        if (nodeLine >= startLine && nodeLine <= endLine) {
          nodes.push(node);
        }
      }
    }
  });

  return nodes;
}
```

### Variable Usage Analysis

```javascript
function analyzeVariables(blockNodes, beforeNodes, afterNodes) {
  const usedInBlock = findUsedVariables(blockNodes);
  const definedInBlock = findDefinedVariables(blockNodes);
  const availableBefore = findDefinedVariables(beforeNodes);
  const usedAfter = findUsedVariables(afterNodes);

  // Parameters = used but not defined, and available before
  const parameters = usedInBlock
    .filter(v => !definedInBlock.has(v))
    .filter(v => availableBefore.has(v));

  // Return values = modified in block and used after
  const modifiedInBlock = findModifiedVariables(blockNodes);
  const returnValues = modifiedInBlock
    .filter(v => usedAfter.has(v));

  return { parameters, returnValues };
}
```

---

## Success Criteria

- [ ] CLI works for analyze/preview/apply commands
- [ ] Correctly identifies parameters (95%+ accuracy on test cases)
- [ ] Correctly identifies return values (95%+ accuracy)
- [ ] Handles control flow transformations (break/return/continue)
- [ ] AST verification proves semantic equivalence
- [ ] Clear error messages for infeasible extractions
- [ ] JSON output for programmatic use
- [ ] Test suite with 30+ cases covering edge cases
- [ ] Easy for Claude Code to use

---

## Edge Cases to Handle

1. **Too many parameters** (>5) - warn user
2. **Multiple return values** - return object or suggest split
3. **break in switch** - transform to return
4. **continue in loop** - transform to return flag
5. **Scope issues** - variable not available at boundary
6. **Nested blocks** - identify correct boundaries
7. **Side effects** - detect external state modifications
8. **Early returns** - preserve semantics

See CLI_SPEC.md for detailed handling of each.

---

## Example Test Cases

**Test 1: Simple switch case**
```javascript
// Input: Lines 5-10
switch(x) {
  case 1:
    const y = x + 1;
    console.log(y);
    break;
}

// Expected: 0 parameters, no return value
```

**Test 2: Parameters needed**
```javascript
// Input: Lines 10-15
const config = getConfig();  // line 8
// Extract this:
const result = processData(config);  // uses config
saveResult(result);

// Expected: 1 parameter (config)
```

**Test 3: Return value needed**
```javascript
// Extract lines 10-12:
let output = null;
output = compute();
// End extraction
console.log(output);  // line 13, uses output

// Expected: return value (output)
```

---

## Questions Before Starting

1. **Location:** Build as standalone tool in `claude/projects/extract-method-tool/` or integrate into `inav-configurator/`?

2. **Installation:** Global npm tool or local to project?

3. **Testing:** Preference for Vitest vs Node.js test runner?

4. **TypeScript:** JavaScript for V1 (simpler), TypeScript for V2?

---

## Getting Started

1. Read CLI_SPEC.md (complete design with algorithms)
2. Set up project structure
3. Install dependencies (Commander.js, Acorn, recast, compare-ast, chalk)
4. Create basic CLI with Commander.js
5. Implement Phase 1 (parsing + line mapping)
6. Reply to Manager with:
   - Answers to questions above
   - Proposed project location
   - Any clarifications needed
   - Estimated start date

---

**Manager**
