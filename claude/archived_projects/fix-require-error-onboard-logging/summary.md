# Project: Fix require() Error in Onboard Logging Tab

**Status:** ✉️ ASSIGNED
**Priority:** High
**Type:** Bug Fix
**Created:** 2025-11-25
**Assignee:** Developer

## Overview

Fix "Uncaught ReferenceError: require is not defined" error that occurs when switching tabs in the configurator, specifically involving the onboard logging tab cleanup.

## Problem

**Error Message:**
```
Uncaught ReferenceError: require is not defined
    at configurator_main.js:246:29
    at TABS.onboard_logging.cleanup (onboard_logging.js:467:9)
    at GUI_control.tab_switch_cleanup (gui.js:107:31)
    at HTMLAnchorElement.<anonymous> (configurator_main.js:144:21)
```

**Symptom:**
- Error occurs during tab switching
- Originates from onboard logging tab cleanup
- Prevents proper tab cleanup/switching
- Breaks configurator functionality

**Root Cause (Suspected):**
This is a CommonJS vs. ES Modules issue. The configurator was recently converted from CommonJS to ESM (see completed project: refactor-commonjs-to-esm). This error indicates a `require()` statement was missed during the conversion.

The error trace shows:
1. Primary error location: `configurator_main.js:246`
2. Triggered during: `TABS.onboard_logging.cleanup` at `onboard_logging.js:467`
3. Called from: `GUI_control.tab_switch_cleanup` at `gui.js:107`
4. Initiated by: Tab click event handler at `configurator_main.js:144`

## Impact

**Severity:** High
- Breaks tab switching functionality
- Affects all users of the configurator
- Prevents proper cleanup when leaving onboard logging tab
- May cause memory leaks or state corruption
- Regression from ESM conversion work

**User Experience:**
- Tab switching fails with error
- Console shows error message
- May leave configurator in inconsistent state

## Scope

### Primary Goal

Fix the `require()` reference error by converting remaining CommonJS code to ES modules.

### Investigation Required

1. **Locate the require() statement:**
   - Check `configurator_main.js:246`
   - Check `onboard_logging.js:467` (cleanup function)
   - Examine what module is being required

2. **Determine correct ES module syntax:**
   - Identify the module being imported
   - Convert to proper `import` statement
   - Ensure module is exported correctly

3. **Verify no other require() statements:**
   - Search entire codebase for remaining `require()`
   - Convert any remaining CommonJS to ESM
   - Ensure consistency across all files

### Files to Examine

**Primary suspects:**
- `js/configurator_main.js` (line 246)
- `tabs/onboard_logging.js` (line 467, cleanup function)
- `js/gui.js` (tab switch cleanup)

**Related files:**
- Any modules being required
- Module export definitions

## Technical Details

### CommonJS vs. ES Modules

**Old (CommonJS):**
```javascript
const module = require('./path/to/module');
module.exports = { something };
```

**New (ES Modules):**
```javascript
import module from './path/to/module.js';
export { something };
```

### Likely Fix

The fix will involve:
1. Finding the `require()` statement at configurator_main.js:246
2. Identifying what it's trying to import
3. Converting to ES6 `import` statement at top of file
4. Ensuring the imported module uses `export` syntax
5. Testing tab switching to verify fix

### Example Conversion

**Before:**
```javascript
function cleanup() {
    // ... cleanup code ...
    const SomeModule = require('./some_module'); // Line 467 (example)
    SomeModule.doSomething();
}
```

**After:**
```javascript
import SomeModule from './some_module.js'; // Top of file

function cleanup() {
    // ... cleanup code ...
    SomeModule.doSomething();
}
```

## Investigation Steps

1. **Read the error location:**
   - Examine `configurator_main.js:246`
   - Examine `onboard_logging.js:467`
   - Identify what's being required

2. **Find the pattern:**
   - Is it requiring a Node.js built-in? (like `fs`, `path`)
   - Is it requiring a local module?
   - Is it requiring a package?

3. **Determine solution:**
   - If Node.js built-in: May need browser-compatible alternative
   - If local module: Convert to ES import
   - If package: Ensure package supports ESM or use alternative

4. **Apply fix:**
   - Convert require() to import statement
   - Move import to top of file
   - Ensure imported module exports correctly

5. **Search for other occurrences:**
   - Grep for remaining `require(` in codebase
   - Convert any remaining instances
   - Ensure complete ESM conversion

## Testing

**Functional Testing:**
1. Open configurator
2. Navigate to onboard logging tab
3. Switch to another tab
4. Verify no error in console
5. Verify cleanup executes properly
6. Test switching between multiple tabs

**Regression Testing:**
- Test all tab switching combinations
- Verify all tabs still function correctly
- Check console for any errors
- Test with real FC if possible

**Edge Cases:**
- Rapid tab switching
- Switching while tab is loading
- Switching during data operations

## Success Criteria

- [ ] Error no longer appears in console
- [ ] Tab switching works without errors
- [ ] Onboard logging tab cleanup executes successfully
- [ ] No remaining `require()` statements in main code
- [ ] All tabs function correctly
- [ ] No new errors introduced

## Estimated Time

**Total:** 1-2 hours

- Investigation: 30 min
- Fix implementation: 30 min
- Testing: 30-60 min

This should be a quick fix - likely just 1-3 lines need to be changed.

## Priority Justification

**High Priority:**
- Breaks core functionality (tab switching)
- Affects all users
- Easy and quick to fix
- Regression from recent work
- Should be fixed before next release

## Deliverables

1. **Code Fix:**
   - Convert require() to import statement
   - Ensure proper module exports

2. **Verification:**
   - Test tab switching
   - Verify no errors in console
   - Confirm cleanup executes

3. **Completion Report:**
   - Describe the issue found
   - Explain the fix applied
   - Confirm testing results
   - Note any remaining require() statements found

## Notes

- This is likely a simple oversight from the ESM conversion
- Should be a quick 1-line fix (plus moving import to top)
- May reveal other missed conversions
- Good opportunity to verify ESM conversion is complete

## Related Work

- **Completed:** refactor-commonjs-to-esm (converted configurator to ES modules)
- This is a bug fix for missed conversion during that project

## Follow-up

After fixing this specific error:
- Search for any other `require()` statements
- Verify complete ESM conversion
- Consider adding linter rule to prevent `require()` in future code
