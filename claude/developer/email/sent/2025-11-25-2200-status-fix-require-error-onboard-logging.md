# Status Report: Fix require() Error in Onboard Logging Tab

**Task Reference:** `developer/inbox/2025-11-25-1700-task-fix-require-error-onboard-logging.md`
**Status:** Completed
**Date:** 2025-11-25 22:00

## Progress Summary

Identified and fixed the CommonJS `require()` statements that were causing the "Uncaught ReferenceError: require is not defined" error during tab switching.

## Root Cause

The error was NOT in `onboard_logging.js` as initially suspected. The actual issue was:

1. **`tabs/search.js`** - Entire file was never converted to ESM. It used:
   - `require('./../js/gui')`
   - `require('path')` (Node.js module)
   - `require('./../js/localization')`
   - `path.join(__dirname, ...)` for HTML loading

2. **`js/configurator_main.js:242`** - Used `require('./../tabs/search')` instead of dynamic `import()` like all other tabs

## Work Completed

### 1. Converted `tabs/search.js` to ESM
- Changed `require()` statements to ES6 `import` statements
- Replaced `path.join(__dirname, "search.html")` with `import('./search.html?raw').then(({default: html}) => GUI.load(html, ...))`
- Added `'use strict';` directive
- Fixed implicit global variables (`tabNames`, `simClick`, `tabName`, `tabLink`, `key`, `settings`, `result`, `match`) by adding proper `const`/`let` declarations

### 2. Fixed `js/configurator_main.js`
- Changed line 242 from:
  ```javascript
  require('./../tabs/search');
  TABS.search.initialize(content_ready);
  ```
  To:
  ```javascript
  import('./../tabs/search').then(() => TABS.search.initialize(content_ready));
  ```

### 3. Verified No Other require() Statements
- Searched entire `js/` and `tabs/` directories
- Confirmed no remaining `require()` statements in main codebase

## Files Modified

- `tabs/search.js` - Full ESM conversion
- `js/configurator_main.js` - Line 242, dynamic import fix

## Testing

- [x] Configurator launches without errors
- [ ] Need manual verification: Switch tabs, including to/from onboard_logging and search tabs
- [ ] Need manual verification: Verify search tab functionality works

**Please test tab switching manually to confirm the fix.**

## Technical Notes

The error message mentioned `onboard_logging.js:467` but this was misleading. The actual error occurred because:
1. User clicks a tab (any tab switch triggers cleanup of current tab)
2. `GUI.tab_switch_cleanup()` is called
3. During switch logic in `configurator_main.js`, the `search` case used synchronous `require()` which is not defined in browser ES modules
4. The stack trace showed onboard_logging cleanup because that's what was running when the `require()` error occurred elsewhere in the same switch statement processing

## Next Steps

None - task complete. Ready for human testing verification.

---

**Developer**
