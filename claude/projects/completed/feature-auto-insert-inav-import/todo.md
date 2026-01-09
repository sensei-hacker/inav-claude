# TODO: Auto-Insert INAV Module Import

## Phase 1: Research & Analysis

### Understand Current Implementation
- [ ] Read transpiler entry point (`js/transpiler/transpiler/index.js`)
- [ ] Check how code flows from editor to transpiler
- [ ] Review parser initialization (`js/transpiler/transpiler/parser.js`)
- [ ] Check if any preprocessing already exists
- [ ] Understand error handling flow

### Review Import Requirements
- [ ] Identify what INAV module exports
- [ ] Check if import is actually required (or optional)
- [ ] Review existing example code for import patterns
- [ ] Check documentation for import requirements
- [ ] Confirm import syntax (ESM vs CommonJS)

### Analyze Edge Cases
- [ ] Test transpiler with no import
- [ ] Test transpiler with import present
- [ ] Test with various import syntaxes
- [ ] Test with comments at top
- [ ] Document current behavior

## Phase 2: Design Solution

### Choose Implementation Approach
- [ ] Decide: Transpiler preprocessing vs Monaco integration vs Hybrid
- [ ] Document decision rationale
- [ ] Consider impact on ESM refactor project
- [ ] Plan for backward compatibility

### Design Detection Logic
- [ ] Write regex for detecting INAV import
- [ ] Handle variations: `import * as`, `import {}`, `import X`
- [ ] Handle CommonJS: `require('inav')`
- [ ] Test regex patterns with examples
- [ ] Document what counts as "has import"

### Design Insertion Logic
- [ ] Determine insertion position (line 1, after comments, etc.)
- [ ] Choose import format: `import * as inav from 'inav'`
- [ ] Decide on whitespace/formatting
- [ ] Handle empty files
- [ ] Handle files with only comments

### UX Decisions
- [ ] Decide: Transparent vs Visible insertion
- [ ] Decide: Show notification or silent
- [ ] Decide: Add settings checkbox or not
- [ ] Design error messages (if insertion fails)
- [ ] Consider undo behavior

## Phase 3: Implementation

### Create Detection Function
```javascript
- [ ] Write `hasInavImport(code)` function
- [ ] Support multiple import syntaxes
- [ ] Test with various code samples
- [ ] Add JSDoc documentation
- [ ] Handle null/undefined input
```

### Create Insertion Function
```javascript
- [ ] Write `insertInavImport(code)` function
- [ ] Detect optimal insertion position
- [ ] Preserve existing formatting
- [ ] Handle edge cases
- [ ] Add JSDoc documentation
```

### Integrate into Transpiler
- [ ] Locate transpiler entry point
- [ ] Add preprocessing step
- [ ] Call detection function
- [ ] Call insertion function if needed
- [ ] Preserve original code (for error reporting)
- [ ] Update any code that passes line numbers

### Handle Line Number Offset
- [ ] If import inserted, line numbers shift by +1 or +2
- [ ] Update error reporting to account for offset
- [ ] Update debugging to show correct lines
- [ ] Test error messages show correct line numbers

## Phase 4: Testing

### Unit Tests

Create test file: `js/transpiler/transpiler/tests/auto_import_tests.js`

**Detection Tests:**
- [ ] No import → returns false
- [ ] `import * as inav from 'inav'` → returns true
- [ ] `import { flight } from 'inav'` → returns true
- [ ] `import inav from 'inav'` → returns true
- [ ] `const inav = require('inav')` → returns true
- [ ] Import with different name → returns true
- [ ] Similar but different import → returns false
- [ ] Case variations → handled correctly

**Insertion Tests:**
- [ ] Empty string → import added
- [ ] Code without import → import added at top
- [ ] Code with comments → import added after comments
- [ ] Code with blank lines → preserves formatting
- [ ] Code with import → no change
- [ ] Multi-line code → correct position

**Integration Tests:**
- [ ] Transpile simple code without import → success
- [ ] Transpile complex code without import → success
- [ ] Transpile code with import → success (no duplicate)
- [ ] Transpile invalid code without import → import added, then error
- [ ] Check generated logic conditions are correct

### Manual Testing

- [ ] Open JavaScript Programming tab in configurator
- [ ] Test Case 1: Empty editor
  - [ ] Enter simple code: `gvar[0] = 100;`
  - [ ] Click Transpile
  - [ ] Verify transpilation succeeds
  - [ ] Check if import visible in editor

- [ ] Test Case 2: Code with import
  - [ ] Enter code with `import * as inav from 'inav'`
  - [ ] Add logic: `if (flight.yaw > 1800) { gvar[0] = 1; }`
  - [ ] Click Transpile
  - [ ] Verify no duplicate import

- [ ] Test Case 3: Code with comments
  - [ ] Enter comments at top
  - [ ] Add logic below
  - [ ] Click Transpile
  - [ ] Check import position

- [ ] Test Case 4: Load examples
  - [ ] Load each built-in example
  - [ ] Click Transpile on each
  - [ ] Verify all work correctly

- [ ] Test Case 5: Error handling
  - [ ] Enter invalid code (syntax error)
  - [ ] Click Transpile
  - [ ] Verify error shown correctly
  - [ ] Check line numbers are correct

### Edge Case Testing

- [ ] Very long code (1000+ lines)
- [ ] Code with Unicode characters
- [ ] Code with only whitespace
- [ ] Code with only comments
- [ ] Code with multiple import statements
- [ ] Code with commented-out import
- [ ] Code that tricks the regex (string containing 'import')

## Phase 5: Error Handling

### Graceful Degradation
- [ ] If detection fails → proceed without insertion
- [ ] If insertion fails → show error, don't crash
- [ ] If regex throws → catch and log
- [ ] Provide fallback behavior

### Error Messages
- [ ] "Auto-import insertion failed" message
- [ ] Suggest manual import
- [ ] Provide import example
- [ ] Link to documentation

### Logging
- [ ] Debug log when import inserted
- [ ] Debug log when import already exists
- [ ] Error log on failures
- [ ] Include relevant code snippets in logs

## Phase 6: UX Polish

### User Feedback (Optional)
- [ ] Add subtle notification: "INAV import auto-inserted"
- [ ] Show only first time (per session?)
- [ ] Add dismiss/don't show again option
- [ ] Style notification appropriately

### Settings (Optional)
- [ ] Add checkbox: "Auto-insert INAV import"
- [ ] Default: checked (enabled)
- [ ] Save preference to localStorage
- [ ] Respect user preference in transpile flow

### Visual Indicators (Optional)
- [ ] Show "ghost text" import if missing
- [ ] Highlight auto-inserted import (subtle color)
- [ ] Add icon or tooltip explaining feature

### Help Text
- [ ] Update any tooltips mentioning imports
- [ ] Update help/documentation tab
- [ ] Add FAQ entry if needed

## Phase 7: Documentation

### Code Documentation
- [ ] Add JSDoc to detection function
- [ ] Add JSDoc to insertion function
- [ ] Add inline comments explaining logic
- [ ] Document regex patterns
- [ ] Add examples in comments

### User Documentation
- [ ] Update user guide (if exists)
- [ ] Add note about auto-import feature
- [ ] Explain when/how it works
- [ ] Show example of manual import (if users prefer)
- [ ] Add troubleshooting section

### Developer Documentation
- [ ] Update transpiler architecture docs
- [ ] Note preprocessing step in flow diagram
- [ ] Document line number offset handling
- [ ] Add to changelog/release notes

### Update Examples
- [ ] Review built-in examples
- [ ] Decide: Keep imports or remove (since auto)
- [ ] Add comment explaining auto-import if helpful
- [ ] Ensure all examples work with feature

## Phase 8: Performance & Optimization

### Performance Testing
- [ ] Benchmark transpile time before/after
- [ ] Test with large code samples (1000+ lines)
- [ ] Ensure no noticeable slowdown
- [ ] Optimize regex if needed

### Code Review
- [ ] Remove any debug logging (production mode)
- [ ] Clean up commented code
- [ ] Verify no memory leaks
- [ ] Check for code duplication

### Final Testing
- [ ] Full regression test (all examples)
- [ ] Test on different browsers
- [ ] Test in Electron app
- [ ] Verify no console errors

## Phase 9: Release Preparation

### Pre-Release Checklist
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Manual testing complete
- [ ] No known bugs
- [ ] Documentation complete
- [ ] Code reviewed

### Commit & PR
- [ ] Create descriptive commit message
- [ ] Include before/after examples
- [ ] Note benefits and use cases
- [ ] Add screenshots if UI changes
- [ ] Link to project documentation

### Deployment Considerations
- [ ] Check if any migration needed
- [ ] Verify backward compatibility
- [ ] Test with existing saved code
- [ ] Plan rollback if issues

## Common Patterns

### Detection Pattern
```javascript
function hasInavImport(code) {
  // Match various import syntaxes
  const patterns = [
    /import\s+\*\s+as\s+\w+\s+from\s+['"]inav['"]/,
    /import\s+{\s*[^}]*\s*}\s+from\s+['"]inav['"]/,
    /import\s+\w+\s+from\s+['"]inav['"]/,
    /const\s+\w+\s*=\s*require\s*\(\s*['"]inav['"]\s*\)/
  ];

  return patterns.some(pattern => pattern.test(code));
}
```

### Insertion Pattern
```javascript
function insertInavImport(code) {
  if (hasInavImport(code)) {
    return code; // Already has import
  }

  // Find insertion point (after comments)
  const lines = code.split('\n');
  let insertIndex = 0;

  for (let i = 0; i < lines.length; i++) {
    const trimmed = lines[i].trim();
    if (trimmed && !trimmed.startsWith('//') && !trimmed.startsWith('/*')) {
      insertIndex = i;
      break;
    }
  }

  // Insert import
  const importLine = "import * as inav from 'inav';";
  lines.splice(insertIndex, 0, importLine, '');

  return lines.join('\n');
}
```

## Questions for Manager

- Should the import be visible in the editor or transparent?
- Should we add a settings checkbox for this feature?
- What should happen if import insertion fails?
- Should we notify users the first time import is inserted?
- How should this interact with the CommonJS to ESM refactor?

## Notes

- This is a convenience feature, not critical
- Should be completely transparent to users
- Must not break existing code
- Consider ESM vs CommonJS based on active refactor project
- May need to update after ESM refactor completes
