# Project: Auto-Insert INAV Module Import

**Status:** ✅ COMPLETE
**Priority:** Low-Medium
**Type:** Feature Enhancement
**Created:** 2025-11-24
**Assigned:** 2025-11-24
**Completed:** 2025-11-24
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-1730-task-auto-insert-inav-import.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-auto-insert-inav-import-complete.md`
**Time:** ~2 hours (vs 5.5 hour estimate)
**Branch:** programming_transpiler_js

## Overview

Automatically insert the INAV module import line in the Monaco editor at transpile time if it doesn't already exist. This improves user experience by eliminating a common boilerplate requirement.

## Problem

Users writing JavaScript code for the INAV transpiler must manually include an import statement for the INAV module at the top of their code. Forgetting this import is a common error that causes transpilation to fail.

**Current behavior:**
```javascript
// User must manually write:
import * as inav from 'inav';

// Then their code:
if (flight.yaw > 1800) {
  override.throttle = 1500;
}
```

**If user forgets the import:**
- Transpilation may fail
- Unclear error messages
- User has to manually add it

## Proposed Solution

At transpile time, automatically detect if the INAV module import is missing and insert it if needed.

**New behavior:**
```javascript
// User writes:
if (flight.yaw > 1800) {
  override.throttle = 1500;
}

// Transpiler automatically prepends (if missing):
import * as inav from 'inav';

// Then transpiles the complete code
```

**Benefits:**
- Reduced friction for users
- One less thing to remember
- Cleaner user code (boilerplate hidden)
- Fewer transpilation errors from missing imports

## Technical Approach

### Option 1: Transpiler Preprocessing (Recommended)

Modify the transpiler to check for INAV import before parsing:

**Location:** `js/transpiler/transpiler/index.js` or `parser.js`

**Logic:**
1. Accept user code as input
2. Check if code contains INAV import statement
3. If missing, prepend import line
4. Continue with normal transpilation

**Pseudo-code:**
```javascript
function transpile(userCode) {
  // Check for import
  const hasInavImport = /import\s+.*\s+from\s+['"]inav['"]/i.test(userCode);

  if (!hasInavImport) {
    userCode = "import * as inav from 'inav';\n\n" + userCode;
  }

  // Continue with existing transpilation
  return parse(userCode);
}
```

### Option 2: Monaco Editor Integration

Modify Monaco editor to insert import on blur or transpile button click:

**Location:** `tabs/javascript_programming.js` Monaco setup

**Logic:**
1. User clicks "Transpile" button
2. Get code from Monaco editor
3. Check for import
4. If missing, temporarily insert it for transpilation
5. Optionally: Update editor with inserted line (or keep hidden)

**Considerations:**
- Should the inserted line be visible to user?
- Should it be saved with their code?
- Or only inserted for transpilation (transparent)?

### Option 3: Hybrid Approach

- Show import in editor as gray "ghost text" if missing
- Auto-insert for transpilation
- Let user explicitly add it if they want

## Implementation Details

### Detection Logic

**What to check for:**
- `import * as inav from 'inav'`
- `import { ... } from 'inav'`
- `import inav from 'inav'`
- `const inav = require('inav')` (if CommonJS still in use)

**Regex pattern:**
```javascript
const inavImportPattern = /(?:import\s+(?:\*\s+as\s+)?\w+|import\s*{[^}]*})\s+from\s+['"]inav['"]|const\s+\w+\s*=\s*require\(['"]inav['"]\)/;
```

### Insert Position

**Where to insert:**
- Top of file (line 1)
- After any existing comments/docstrings
- Before first code statement

**Format:**
```javascript
import * as inav from 'inav';

```
(Note: Add blank line after for readability)

### Edge Cases

1. **User has different import name:**
   ```javascript
   import * as INAV from 'inav';  // Should recognize this
   ```

2. **User has partial import:**
   ```javascript
   import { flight } from 'inav';  // Should recognize this
   ```

3. **Multiple imports:**
   ```javascript
   import * as inav from 'inav';
   import * as helpers from 'helpers';  // Don't duplicate INAV
   ```

4. **Comments at top:**
   ```javascript
   // My flight code
   // Version 1.0

   // Should insert AFTER comments
   if (flight.yaw > 1800) { ... }
   ```

## User Experience Considerations

### Visibility Decision

**Option A: Transparent insertion**
- Import inserted only for transpilation
- Not shown in editor
- User code stays clean
- **Pro:** Less visual clutter
- **Con:** "Magic" behavior may confuse users

**Option B: Visible insertion**
- Import added to editor content
- User sees it happen
- Gets saved with code
- **Pro:** Explicit, educational
- **Con:** More clutter, harder to remove

**Option C: Optional insertion**
- Add checkbox: "Auto-insert INAV import"
- Default: on
- User can disable if they want control
- **Pro:** User choice
- **Con:** One more setting

**Recommendation:** Start with Option A (transparent), add Option C (checkbox) if users request it.

### Error Messaging

If auto-insertion fails or causes issues:
- Show clear error: "Failed to auto-insert INAV import"
- Explain how to manually add it
- Provide example

### Documentation

Update user documentation:
- Note that INAV import is auto-inserted
- Explain they can manually add it if preferred
- Show what the import looks like

## Testing Requirements

### Unit Tests
- [ ] Code with no import → import inserted
- [ ] Code with import → no duplicate
- [ ] Code with different import syntax → recognized
- [ ] Code with comments → insert in correct position
- [ ] Empty code → import added
- [ ] Code with syntax errors → still insert (let parser catch errors)

### Integration Tests
- [ ] Transpile simple code without import → success
- [ ] Transpile complex code without import → success
- [ ] Transpile code with import → no change
- [ ] Save code → verify behavior
- [ ] Load examples → verify behavior

### Manual Testing
- [ ] Open JavaScript Programming tab
- [ ] Write code without import
- [ ] Click Transpile
- [ ] Verify transpilation succeeds
- [ ] Check if editor shows import (based on UX decision)
- [ ] Test with various code examples

## Implementation Plan

### Phase 1: Research (1 hour)
- Review current transpiler entry point
- Identify best insertion point
- Check for existing import handling
- Review Monaco editor API (if needed)

### Phase 2: Core Implementation (2 hours)
- Write import detection function
- Write import insertion function
- Integrate into transpile flow
- Handle edge cases

### Phase 3: Testing (1 hour)
- Write unit tests
- Test with examples
- Test edge cases
- Verify no regressions

### Phase 4: UX Polish (1 hour)
- Decide on visibility approach
- Add error handling
- Update UI if needed
- Add user feedback (toast/notification?)

### Phase 5: Documentation (30 min)
- Update code comments
- Update user documentation
- Note in changelog

**Total Estimated Time:** ~5.5 hours

## Success Criteria

- [ ] Code without INAV import transpiles successfully
- [ ] Code with INAV import continues to work (no regression)
- [ ] No duplicate imports inserted
- [ ] Edge cases handled correctly
- [ ] User experience is smooth
- [ ] No performance impact
- [ ] Documentation updated

## Risks

**Low Risk:**
- Simple detection and insertion logic
- Isolated change (doesn't affect existing functionality)
- Easy to test

**Potential Issues:**
- May conflict with future module system changes
- Need to update if INAV module name changes
- Edge cases with unusual import syntax

## Related Work

- **refactor-commonjs-to-esm** - May affect import syntax
- **improve-transpiler-error-reporting** - Should show clear errors if insertion fails
- **Monaco editor integration** - Already in place for syntax highlighting

## Future Enhancements

- Auto-import other common modules (helpers, etc.)
- Suggest imports based on code analysis (e.g., if user uses `flight.*`, suggest INAV import)
- Import statement intellisense/autocomplete
- "Organize imports" command to clean up unused imports

## Notes

- This is a quality-of-life improvement, not a critical feature
- Should be transparent and "just work"
- Maintain backward compatibility with existing code
- Consider ESM vs CommonJS syntax (based on refactor-commonjs-to-esm project)

## Files to Modify

**Primary:**
- `js/transpiler/transpiler/index.js` - Main transpiler entry point
- OR `js/transpiler/transpiler/parser.js` - If preprocessing before parse

**Secondary (if Monaco integration):**
- `tabs/javascript_programming.js` - Transpile button handler

**Testing:**
- Create new test file or add to existing transpiler tests

**Documentation:**
- User guide (if exists)
- In-code comments
