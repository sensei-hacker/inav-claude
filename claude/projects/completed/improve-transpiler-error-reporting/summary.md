# Project: Improve Transpiler Error Reporting

**Type:** Enhancement / Bug Fix
**Status:** ✅ Complete
**Completed:** 2025-11-23
**Target Version:** INAV Configurator 9.0.1
**Pull Request:** TBD
**Priority:** Medium

## Overview

Improve transpiler error handling to warn users when code cannot be transpiled, instead of silently skipping code or only logging warnings to the console that users won't see.

## Problem Statement

### Current Behavior (BAD)

When the transpiler encounters code it doesn't know how to handle:
- **Silently skips the code** - No user notification
- **Only console warnings** - Users don't have DevTools open
- **Example:** "Unknown operand" in console
- **Result:** User thinks their code is saved, but it's incomplete/wrong

### Expected Behavior (GOOD)

When transpiler encounters unsupported code:
- **Show clear error in UI** - Modal dialog or error panel
- **Highlight problem code** - Point to exact line/construct
- **Explain what's wrong** - "Variable 'foo' is not defined"
- **Prevent save** - Don't allow saving incomplete transpilation
- **Provide guidance** - Suggest how to fix or what's supported

## User Impact

### Current Risk

**HIGH** - This is a safety issue:
1. User writes code they think works
2. Transpiler silently fails to convert parts of it
3. User saves incomplete logic to flight controller
4. Aircraft behaves unexpectedly (safety hazard!)
5. User has no idea why

### Example Scenario

```javascript
// User's code
if (flight.yaw > 1800 && customVariable > 5) {
  override.vtx.power = 4;
}
```

**Current behavior:**
- Console: "Unknown operand: customVariable"
- Transpiler: Skips the condition or generates invalid logic
- User: Sees no error, thinks it saved correctly
- Result: Logic doesn't work as expected

**Desired behavior:**
- UI Error: "Error on line 1: 'customVariable' is not defined. Available variables: gvar[0-7], flight.*, rc.*"
- Save button: Disabled with red warning
- User: Knows exactly what to fix

## Technical Approach

### Phase 1: Audit Error Paths

1. **Identify all error cases in transpiler**
   - Parser errors (syntax)
   - Analyzer errors (undefined variables)
   - CodeGen errors (unsupported constructs)
   - Unknown operands
   - Type mismatches
   - Constraint violations

2. **Document current error handling**
   - Which errors are caught?
   - Which are logged to console?
   - Which are silently ignored?
   - Which throw exceptions?

### Phase 2: Design Error Reporting System

**Error Categories:**

1. **Fatal Errors** (block transpilation)
   - Syntax errors
   - Undefined variables
   - Unsupported language features
   - Type errors

2. **Warnings** (transpile but warn user)
   - Potentially unsafe constructs
   - Performance concerns
   - Best practice violations

3. **Info** (optional feedback)
   - Optimization opportunities
   - Usage tips

**Error Data Structure:**

```javascript
{
  severity: 'error' | 'warning' | 'info',
  message: 'Human-readable error message',
  line: 5,
  column: 12,
  code: 'undefined_variable',
  suggestion: 'Did you mean: gvar[0]?',
  source: 'if (flight.yaw > customVariable) {'
}
```

### Phase 3: UI Integration

**Error Display Options:**

1. **Inline Errors** (like VS Code)
   - Red squiggly underlines
   - Hover for details
   - Error list panel

2. **Modal Dialog** (simpler)
   - Show all errors when transpile fails
   - List each error with line number
   - OK/Cancel buttons

3. **Status Bar** (minimal)
   - "❌ 3 errors, 1 warning"
   - Click to expand details

**Recommended:** Combination approach
- Status bar for quick overview
- Error list panel for details
- Prevent save when errors exist

### Phase 4: Implementation

**Modify Transpiler:**

```javascript
// parser.js - Collect errors instead of just logging
class Parser {
  constructor() {
    this.errors = [];
  }

  parseExpression(node) {
    if (this.isUnknownOperand(node)) {
      this.errors.push({
        severity: 'error',
        message: `Unknown operand: ${node.name}`,
        line: node.loc.start.line,
        code: 'unknown_operand',
        suggestion: this.suggestSimilar(node.name)
      });
      return null; // Don't continue with bad parse
    }
  }
}
```

**Modify UI:**

```javascript
// tabs/javascript_programming.js
function transpileCode() {
  const result = transpiler.transpile(code);

  if (result.errors.length > 0) {
    // Show errors to user
    showErrorDialog(result.errors);

    // Disable save button
    disableSaveButton();

    // Highlight error lines in editor
    highlightErrors(result.errors);

    return;
  }

  // Success - enable save
  enableSaveButton();
  updateLogicConditions(result.conditions);
}
```

## Files to Modify

### Transpiler Core

- `js/transpiler/transpiler/parser.js`
  - Collect parsing errors
  - Don't throw, collect and return

- `js/transpiler/transpiler/analyzer.js`
  - Validate variable references
  - Check type compatibility
  - Collect semantic errors

- `js/transpiler/transpiler/codegen.js`
  - Validate operands exist
  - Check constraint violations
  - Collect generation errors

- `js/transpiler/index.js`
  - Aggregate all errors
  - Return structured error object

### UI Components

- `tabs/javascript_programming.js`
  - Display errors to user
  - Disable save on errors
  - Highlight error lines
  - Clear errors on successful transpile

### Error Utilities (New)

- `js/transpiler/errors.js` (create)
  - Error class definitions
  - Error formatting utilities
  - Suggestion engine (fuzzy match)

## Error Messages to Improve

### Current Console-Only Warnings

Find and fix all instances of:
```javascript
console.warn('Unknown operand');
console.error('Invalid condition');
// etc.
```

Replace with:
```javascript
this.errors.push({
  severity: 'error',
  message: 'Unknown operand: ' + name,
  // ... full error object
});
```

### Common Error Cases

1. **Undefined variable**
   - `customVariable` → Suggest `gvar[0]` or similar flight.*

2. **Unknown operand**
   - `flight.unknownProperty` → List available properties

3. **Syntax error**
   - Missing semicolon, parentheses, etc.

4. **Type mismatch**
   - `flight.yaw = "hello"` → "Cannot assign string to numeric property"

5. **Unsupported feature**
   - `for (let i = 0; i < 10; i++)` → "Loops are not supported. Use timer() instead"

6. **Too complex**
   - Exceeds condition count limit
   - Exceeds nesting depth

## Testing Strategy

### Error Test Cases

Create test suite for error handling:

```javascript
describe('Error Reporting', () => {
  it('should error on undefined variable', () => {
    const code = 'if (undefinedVar > 5) {}';
    const result = transpile(code);
    expect(result.errors).toHaveLength(1);
    expect(result.errors[0].code).toBe('undefined_variable');
  });

  it('should suggest similar variables', () => {
    const code = 'if (flght.yaw > 5) {}'; // typo: flght
    const result = transpile(code);
    expect(result.errors[0].suggestion).toContain('flight');
  });

  it('should prevent save when errors exist', () => {
    // Test UI state management
  });
});
```

### Manual Testing

- [ ] Test each error type shows in UI
- [ ] Test save button disabled on error
- [ ] Test save button enabled on success
- [ ] Test error highlighting in editor
- [ ] Test suggestion quality
- [ ] Test with DevTools closed (user view)

## Success Criteria

- [ ] No silent failures in transpiler
- [ ] All errors reported to user via UI
- [ ] Save button disabled when errors exist
- [ ] Clear, actionable error messages
- [ ] Error highlighting in code editor
- [ ] Suggestions for common mistakes
- [ ] Console logging only in debug mode
- [ ] Comprehensive test coverage

## User Experience

### Before (Current)

1. User writes code with typo
2. Clicks "save to flight controller"
3. Save appears successful
4. Logic doesn't work
5. User confused, no idea what's wrong

### After (Improved)

1. User writes code with typo
2. Error appears immediately: "Unknown variable 'flght'. Did you mean 'flight'?"
3. Save button grayed out with "Fix errors before saving"
4. User fixes typo
5. Error clears, save enabled
6. Save succeeds with correct code

## Risks & Considerations

### Breaking Changes

- May reveal errors in existing saved code
- Users might see errors on code that "worked before"
- Consider migration/compatibility mode?

### Performance

- Error collection shouldn't slow down transpiler
- Keep error data structures efficient
- Don't check for errors twice

### UX Concerns

- Don't overwhelm user with too many errors
- Show most important errors first
- Progressive disclosure (show 5, "and 10 more...")

## Related Work

- Can leverage existing syntax highlighting in editor
- Could integrate with Monaco Editor error system if used
- Similar to IDE error reporting (VS Code, etc.)

## Notes

- This should be high priority - affects user safety
- Consider adding to automated tests project (MCP testing)
- May want telemetry on common errors to improve suggestions
- Could help identify gaps in documentation
