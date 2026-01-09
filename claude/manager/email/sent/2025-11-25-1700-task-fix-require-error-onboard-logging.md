# Task Assignment: Fix require() Error in Onboard Logging Tab

**Date:** 2025-11-25 17:00
**Project:** fix-require-error-onboard-logging
**Priority:** High
**Estimated Effort:** 1-2 hours
**Branch:** Create from master

## Task

Fix the "Uncaught ReferenceError: require is not defined" error that occurs during tab switching in the configurator.

## Error Details

```
Uncaught ReferenceError: require is not defined
    at configurator_main.js:246:29
    at TABS.onboard_logging.cleanup (onboard_logging.js:467:9)
    at GUI_control.tab_switch_cleanup (gui.js:107:31)
    at HTMLAnchorElement.<anonymous> (configurator_main.js:144:21)
```

**Call Stack:**
1. Tab click event handler triggers cleanup (`configurator_main.js:144`)
2. GUI calls tab_switch_cleanup (`gui.js:107`)
3. Onboard logging tab cleanup executes (`onboard_logging.js:467`)
4. **Error occurs at `configurator_main.js:246`** - `require()` statement executed

## Problem

This is a regression from the ESM conversion (refactor-commonjs-to-esm project). A `require()` statement was missed during the CommonJS → ES Modules conversion.

**Impact:**
- Breaks tab switching functionality
- Affects all users
- High severity - core functionality broken

## Root Cause

The configurator was converted to ES Modules, but at least one `require()` statement remains. In browser environments without a bundler, `require()` is not defined - only ES6 `import` works.

## Fix Required

### Step 1: Locate the require() Statement

Examine these files:
- `js/configurator_main.js:246` - Primary error location
- `tabs/onboard_logging.js:467` - Cleanup function that triggers it

Find what module is being required and why.

### Step 2: Convert to ES Import

**Example - If you find:**
```javascript
// In cleanup function or elsewhere
const SomeModule = require('./some_module');
```

**Convert to:**
```javascript
// At top of file
import SomeModule from './some_module.js';
```

**Important:**
- Move import to top of file (ES6 requirement)
- Add `.js` extension to local module paths
- Use correct import syntax (default vs. named)
- Ensure imported module exports correctly

### Step 3: Verify Module Exports

If the imported module uses CommonJS exports:
```javascript
module.exports = { something };
```

Convert to ES export:
```javascript
export { something };
// or
export default something;
```

### Step 4: Search for Other require() Statements

```bash
grep -r "require(" js/ tabs/ --include="*.js" | grep -v node_modules
```

Convert any remaining `require()` statements to `import`.

## Testing

**Required Testing:**
1. Open configurator
2. Navigate to onboard logging tab
3. Switch to another tab
4. **Verify:** No error in console
5. **Verify:** Tab switching works smoothly
6. Test switching between multiple tabs rapidly

**Regression Testing:**
- Test all tabs still function correctly
- Verify no new errors appear
- Check that cleanup executes properly

## Success Criteria

- [ ] No "require is not defined" error in console
- [ ] Tab switching works without errors
- [ ] Onboard logging cleanup executes successfully
- [ ] No remaining `require()` in main codebase (excluding node_modules)
- [ ] All tabs function correctly
- [ ] All tests pass

## Technical Notes

**CommonJS (OLD - causes error):**
```javascript
const module = require('./module');
module.exports = { something };
```

**ES Modules (NEW - correct):**
```javascript
import module from './module.js';
export { something };
```

**Why this matters:**
- Browser environments don't have `require()`
- ES6 imports are native in modern browsers
- Configurator uses native ES modules (no bundler)

## Estimated Time

- Investigation: 15-30 min
- Fix: 15-30 min
- Testing: 30-60 min

**Total: 1-2 hours**

This should be a straightforward fix - likely just converting 1-3 `require()` statements to `import`.

## Deliverables

1. **Code Fix:**
   - Convert require() to import statements
   - Ensure proper module exports
   - Clean up any CommonJS remnants

2. **Test Results:**
   - Confirm error resolved
   - Verify tab switching works
   - Report any other require() statements found

3. **Completion Report:**
   - Describe what was found
   - Explain fix applied
   - Confirm testing completed
   - List any additional require() statements converted

## Priority Justification

**High Priority:**
- Breaks core functionality (tab switching)
- Affects all users of configurator
- Quick fix (1-2 hours)
- Regression from recent work
- Should be resolved immediately

## Notes

- This is likely an oversight from the ESM conversion
- May reveal other incomplete conversions
- Good opportunity to ensure ESM conversion is 100% complete
- Consider adding ESLint rule to prevent `require()` in future

## Questions?

If you find `require()` being used for Node.js built-ins (like `fs`, `path`, `crypto`), consult with manager as these may need browser-compatible alternatives.

---

**Manager**
