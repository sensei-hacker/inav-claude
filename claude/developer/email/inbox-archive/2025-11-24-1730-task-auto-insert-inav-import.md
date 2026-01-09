# Task Assignment: Auto-Insert INAV Module Import

**Date:** 2025-11-24 17:30
**Project:** feature-auto-insert-inav-import
**Priority:** Low-Medium
**Estimated Effort:** ~5.5 hours
**Type:** Feature Enhancement

## Task Overview

Automatically insert the INAV module import statement at transpile time if it's missing from the user's code. This eliminates a common source of transpilation errors and improves user experience by removing boilerplate.

## Problem Statement

Users must currently remember to write this line at the top of every script:

```javascript
import * as inav from 'inav';
```

**When forgotten:**
- Transpilation fails
- Error messages may be unclear
- User has to manually add it
- Creates friction and frustration

**Goal:** Make this import automatic and transparent, so users can focus on writing their flight logic.

## Current vs Required Behavior

### Current (Manual Import Required)

```javascript
// User must write:
import * as inav from 'inav';

const { flight, override } = inav;

if (flight.yaw > 1800) {
  override.throttle = 1500;
}
```

### After Implementation (Automatic)

```javascript
// User writes:
const { flight, override } = inav;

if (flight.yaw > 1800) {
  override.throttle = 1500;
}

// Transpiler automatically prepends before parsing:
// import * as inav from 'inav';
```

## Implementation Approach

### Recommended: Transpiler Preprocessing

**Location:** `js/transpiler/transpiler/index.js` (main entry point)

**Logic:**
1. Accept user code as input
2. Check if code contains INAV import (any valid syntax)
3. If missing, prepend `import * as inav from 'inav';\n\n`
4. Continue with normal transpilation

**Detection pattern:**
```javascript
const inavImportPattern = /(?:import\s+(?:\*\s+as\s+)?\w+|import\s*{[^}]*})\s+from\s+['"]inav['"]|const\s+\w+\s*=\s*require\(['"]inav['"]\)/;

function transpile(userCode) {
  // Check for any form of INAV import
  const hasInavImport = inavImportPattern.test(userCode);

  if (!hasInavImport) {
    // Prepend import (with blank line for readability)
    userCode = "import * as inav from 'inav';\n\n" + userCode;
  }

  // Continue with existing transpilation
  return parse(userCode);
}
```

### Detection Requirements

The pattern should recognize all these valid imports:

```javascript
// Standard wildcard import
import * as inav from 'inav';

// Destructured import
import { flight, override } from 'inav';

// Default import (less common)
import inav from 'inav';

// Different variable name
import * as INAV from 'inav';

// CommonJS (if still in use anywhere)
const inav = require('inav');
```

**Should NOT match:**
- Comments mentioning "inav"
- String literals
- Imports from other modules

## Edge Cases to Handle

### 1. Comments at Top of File

```javascript
// My flight control script
// Version 2.0

if (flight.yaw > 1800) { ... }
```

**Question:** Insert before or after comments?
**Recommendation:** Insert at line 1 (before comments). Standard practice for imports.

### 2. Existing Import (No Duplicate)

```javascript
import * as inav from 'inav';

// Should detect and NOT insert duplicate
```

### 3. Partial Import Already Exists

```javascript
import { flight } from 'inav';

// Should recognize this counts as INAV import
// Do NOT add another one
```

### 4. Empty Code

```javascript
// Empty editor
```

**Behavior:** Insert import. User might be starting fresh.

### 5. Code with Syntax Errors

```javascript
if flight.yaw > 1800 {  // Missing parentheses
  ...
}
```

**Behavior:** Still insert import. Let parser catch syntax errors afterward.

## User Experience Decisions

### Visibility: Transparent Insertion (Recommended)

**Approach:**
- Import inserted only for transpilation
- NOT visible in Monaco editor
- NOT saved to user's code
- Completely transparent to user

**Rationale:**
- Cleaner user code
- Less visual clutter
- Users focus on their logic, not boilerplate
- Can always manually add if they want

**Alternative (if requested later):**
- Add checkbox: "Auto-insert INAV import" (default: on)
- Users can disable if they want full control

### Error Handling

If something goes wrong with auto-insertion:
- Log clear error message
- Show user what's needed: "Please add: import * as inav from 'inav';"
- Don't fail silently

## Implementation Plan

### Phase 1: Research & Setup (1 hour)

**Tasks:**
- [ ] Review current transpiler entry point (`js/transpiler/transpiler/index.js`)
- [ ] Identify exact insertion point in transpile flow
- [ ] Check if ESM refactor is complete (it is!)
- [ ] Review existing import handling code
- [ ] Verify import syntax used in examples/tests

### Phase 2: Core Implementation (2 hours)

**Tasks:**
- [ ] Write `hasInavImport(code)` detection function
- [ ] Write `insertInavImport(code)` insertion function
- [ ] Integrate into main transpile function
- [ ] Handle all edge cases listed above
- [ ] Add clear code comments

**Key functions:**
```javascript
/**
 * Checks if code contains an INAV module import statement
 * @param {string} code - JavaScript source code
 * @returns {boolean} - True if INAV import exists
 */
function hasInavImport(code) {
  const pattern = /(?:import\s+(?:\*\s+as\s+)?\w+|import\s*{[^}]*})\s+from\s+['"]inav['"]|const\s+\w+\s*=\s*require\(['"]inav['"]\)/;
  return pattern.test(code);
}

/**
 * Prepends INAV import to code if missing
 * @param {string} code - JavaScript source code
 * @returns {string} - Code with INAV import
 */
function ensureInavImport(code) {
  if (!hasInavImport(code)) {
    return "import * as inav from 'inav';\n\n" + code;
  }
  return code;
}
```

### Phase 3: Testing (1 hour)

**Unit tests to write:**
- [ ] Empty code → import inserted
- [ ] Code without import → import inserted
- [ ] Code with wildcard import → no duplicate
- [ ] Code with destructured import → no duplicate
- [ ] Code with different variable name → recognized
- [ ] Code with comments → import still inserted
- [ ] Code with syntax errors → import inserted (errors caught later)

**Integration tests:**
- [ ] Transpile example code without import → succeeds
- [ ] Transpile code with import → no change
- [ ] Verify transpiler output matches expected

### Phase 4: UX Polish (1 hour)

**Tasks:**
- [ ] Add error handling for insertion failures
- [ ] Test with all existing example code
- [ ] Verify no performance impact
- [ ] Consider logging (debug mode): "Auto-inserted INAV import"

### Phase 5: Documentation (30 minutes)

**Tasks:**
- [ ] Add code comments explaining auto-insertion
- [ ] Update user documentation (if exists)
- [ ] Note in changelog/release notes
- [ ] Add JSDoc comments to new functions

## Testing Checklist

### Automated Tests
- [ ] Code without import transpiles successfully
- [ ] Code with import works unchanged (no regression)
- [ ] No duplicate imports created
- [ ] All import syntax variations recognized
- [ ] Edge cases handled correctly

### Manual Testing in Configurator
- [ ] Open JavaScript Programming tab
- [ ] Write code without `import * as inav from 'inav';`
- [ ] Click Transpile button
- [ ] Verify successful transpilation
- [ ] Check console for errors
- [ ] Test with various example scripts
- [ ] Verify existing examples still work

## Success Criteria

**Definition of Done:**
- [ ] User code without import transpiles successfully
- [ ] Existing code with import continues to work (no regression)
- [ ] No duplicate imports inserted
- [ ] All edge cases handled
- [ ] Tests written and passing
- [ ] No performance degradation
- [ ] Code well-documented
- [ ] User-facing documentation updated

## Code Quality Guidelines

**Follow project standards:**
- Function length: ≤12 lines where possible
- File additions: Keep additions minimal and focused
- Use modern JavaScript (ESM syntax confirmed with refactor)
- Add clear comments for regex patterns
- JSDoc comments for all new functions

## Files to Modify

**Primary:**
- `js/transpiler/transpiler/index.js` - Main transpiler entry point (most likely)
- OR `js/transpiler/transpiler/parser.js` - If preprocessing happens before parse

**Testing:**
- Add to existing transpiler test suite
- OR create new test file for import handling

**Documentation:**
- Update user guide (if exists in `js/transpiler/transpiler/docs/`)
- Add inline code comments

## Technical Notes

### Why ESM Syntax?

The `refactor-commonjs-to-esm` project (completed 2025-11-24) converted all transpiler code to ESM. Use ESM import syntax:

```javascript
import * as inav from 'inav';  // ✅ Use this
const inav = require('inav');   // ❌ Don't use this (legacy)
```

### Line Number Offset

**Question:** If we prepend 2 lines, do error line numbers get offset?

**Answer:** Likely yes. The parser will report errors based on the modified code (with import). This is acceptable since:
- Most errors won't be in the import line
- Users won't see the auto-inserted import
- Error messages still point to their code

**If this becomes an issue:**
- Track line offset
- Adjust error line numbers in error reporting
- Revisit in error reporting improvements

## Risks

**Low Risk:**
- Simple, isolated change
- Easy to test
- No impact on existing functionality
- Quick implementation

**Potential Issues:**
- Edge case with unusual import syntax → Regex might miss it
- Future module system changes → May need to update pattern
- User confusion if something goes wrong → Clear error messages mitigate this

## Future Enhancements (Out of Scope)

- Auto-import other common modules
- Suggest imports based on code analysis
- "Organize imports" command
- Import intellisense/autocomplete

These can be separate projects if user demand exists.

## Getting Started

1. **Read the transpiler code:**
   - `js/transpiler/transpiler/index.js` - Main entry point
   - Understand current transpile flow

2. **Write the detection function:**
   - Start with simple regex
   - Test against example code
   - Refine for edge cases

3. **Integrate into transpile:**
   - Find exact insertion point
   - Add `ensureInavImport()` call
   - Test with simple examples

4. **Expand and test:**
   - Add edge case handling
   - Write unit tests
   - Manual testing in configurator

5. **Polish and document:**
   - Clean up code
   - Add comments
   - Update documentation

## Questions?

If you encounter issues or need clarification:
- Check project files: `claude/projects/feature-auto-insert-inav-import/`
- Review completed ESM refactor: `claude/archived_projects/refactor-commonjs-to-esm/`
- Review transpiler test files for patterns
- Report blockers via inbox

## Summary

This is a straightforward quality-of-life improvement:
- Auto-insert `import * as inav from 'inav';` if missing
- Transparent to user (not visible in editor)
- Reduces common errors
- Simple regex-based detection
- ~5.5 hours estimated effort

The ESM refactor is complete, so this is the perfect time to implement this feature using clean ESM syntax.

---

**Manager**

**Assignment:** This task is now assigned to you. Please acknowledge receipt and begin with Phase 1 (Research) when ready.
