# TODO: Convert CommonJS to ESM Syntax

## Phase 1: Analysis & Planning

### Map Dependencies
- [ ] Create dependency graph of all modules
- [ ] Identify entry points (configurator_main.js, tabs)
- [ ] Identify leaf nodes (no dependencies)
- [ ] Document import/export relationships
- [ ] Identify circular dependencies (if any)

### Identify Patterns
- [ ] List all static requires (top-level)
- [ ] List all dynamic requires (inside functions)
- [ ] List all `module.exports` patterns:
  - [ ] Default exports (`module.exports = X`)
  - [ ] Named exports (`module.exports = { a, b }`)
  - [ ] Mixed exports
- [ ] Identify Node.js built-in requires (path, fs, etc.)
- [ ] Identify special cases (Monaco AMD loader)

### Create Conversion Plan
- [ ] Order files by dependency depth (leaf → root)
- [ ] Mark safe vs risky conversions
- [ ] Plan handling of dynamic requires
- [ ] Document any needed refactoring

## Phase 2: Convert Exports (Bottom-Up)

### Transpiler API Definitions (Leaf Nodes)
- [ ] `js/transpiler/api/types.js`
- [ ] `js/transpiler/api/definitions/flight.js`
- [ ] `js/transpiler/api/definitions/waypoint.js`
- [ ] `js/transpiler/api/definitions/gvar.js`
- [ ] `js/transpiler/api/definitions/events.js`
- [ ] `js/transpiler/api/definitions/helpers.js`
- [ ] `js/transpiler/api/definitions/override.js`
- [ ] `js/transpiler/api/definitions/rc.js`
- [ ] `js/transpiler/api/definitions/pid.js`
- [ ] `js/transpiler/api/definitions/index.js`

### Transpiler Utilities
- [ ] `js/transpiler/transpiler/constants.js`
- [ ] `js/transpiler/transpiler/inav_constants.js`
- [ ] `js/transpiler/transpiler/arrow_function_helper.js`
- [ ] `js/transpiler/transpiler/error_handler.js`

### Transpiler Core
- [ ] `js/transpiler/transpiler/parser.js`
- [ ] `js/transpiler/transpiler/analyzer.js`
- [ ] `js/transpiler/transpiler/codegen.js`
- [ ] `js/transpiler/transpiler/decompiler.js`
- [ ] `js/transpiler/transpiler/optimizer.js`
- [ ] `js/transpiler/transpiler/index.js`

### Transpiler Main
- [ ] `js/transpiler/index.js`

### Transpiler Editor
- [ ] `js/transpiler/editor/diagnostics.js`
- [ ] `js/transpiler/editor/monaco_loader.js` (careful - AMD loader)

### Transpiler Scripts & Examples
- [ ] `js/transpiler/scripts/generate-constants.js`
- [ ] `js/transpiler/examples/index.js`

### Core Configurator Files
- [ ] `js/msp/MSPchainer.js`
- [ ] `js/msp/MSPHelper.js`
- [ ] `js/gui.js`
- [ ] `js/fc.js`
- [ ] `js/localization.js`
- [ ] `js/keywordSearch.js`

### Tab Files
- [ ] `tabs/search.js`
- [ ] `tabs/javascript_programming.js`

### Main Entry
- [ ] `js/configurator_main.js`

## Phase 3: Convert Imports

### Update Import Syntax

For each file converted in Phase 2:

- [ ] Replace `require()` with `import`
- [ ] Add `.js` extension to relative imports
- [ ] Convert destructuring: `const { a, b } = require(...)` → `import { a, b } from ...`
- [ ] Convert default: `const X = require(...)` → `import X from ...`
- [ ] Convert namespace: Consider `import * as X from ...` for full module imports
- [ ] Use `node:` prefix for Node.js built-ins

### Handle Node.js Built-ins

- [ ] `const path = require('path')` → `import path from 'node:path'`
- [ ] `const fs = require('fs')` → `import fs from 'node:fs'`
- [ ] Check if any built-ins need different import style

### Handle Dynamic Requires

Identify and fix each dynamic require:

- [ ] `tabs/javascript_programming.js:103` - `const path = require('path')`
  - Option A: Move to top-level import
  - Option B: Use dynamic `import()` if truly runtime-needed
  - Determine correct approach

### Handle Special Cases

- [ ] Monaco AMD loader (`window.require`) - **DO NOT CHANGE**
  - Verify line 181 in javascript_programming.js is unchanged
  - Add comment explaining why it uses AMD loader

## Phase 4: Fix Import Paths

### Add File Extensions
- [ ] Search for imports without `.js` extension
- [ ] Add `.js` to all relative imports
- [ ] Example: `'./parser'` → `'./parser.js'`
- [ ] Example: '../js/gui' → '../js/gui.js'

### Verify Path Correctness
- [ ] Check all relative paths resolve correctly
- [ ] Update any paths if directory structure changed
- [ ] Test that imports find correct files

## Phase 5: Testing

### Run Transpiler Tests
- [ ] Execute unit tests: `npm test` (if available)
- [ ] Test parser with sample code
- [ ] Test analyzer with sample code
- [ ] Test codegen with sample code
- [ ] Test decompiler with sample logic
- [ ] Verify all tests pass

### Manual Integration Testing
- [ ] Start configurator: `npm start`
- [ ] Open DevTools console - check for errors
- [ ] Navigate to JavaScript Programming tab
- [ ] Load example code
- [ ] Transpile code - verify success
- [ ] Check warnings/errors display correctly
- [ ] Save to SITL/FC - verify no errors
- [ ] Navigate to Search tab - verify loads
- [ ] Search for keyword - verify works

### Check Monaco Editor
- [ ] Verify Monaco editor loads
- [ ] Verify syntax highlighting works
- [ ] Verify autocomplete works (if implemented)
- [ ] Verify no AMD loader errors

### Test Error Cases
- [ ] Try invalid code - verify errors show
- [ ] Try undefined variables - verify caught
- [ ] Try invalid functions - verify caught
- [ ] Verify error messages display correctly

### Performance Check
- [ ] Measure tab load time before/after
- [ ] Measure transpile time before/after
- [ ] Check for memory leaks (DevTools)
- [ ] Verify no performance regression

## Phase 6: Documentation

### Update Code Comments
- [ ] Add JSDoc `@module` declarations
- [ ] Document export types
- [ ] Add comments for any tricky imports
- [ ] Note why Monaco uses AMD loader

### Update Technical Docs
- [ ] Update transpiler docs if needed
- [ ] Note ESM migration in changelog
- [ ] Update developer guide (if exists)

### Update This Project
- [ ] Mark completed tasks
- [ ] Document any issues encountered
- [ ] Note any deviations from plan
- [ ] Record lessons learned

## Phase 7: Cleanup & Review

### Remove Conversion Artifacts
- [ ] Remove any temporary conversion scripts
- [ ] Remove commented-out CommonJS code
- [ ] Clean up debug logging

### Code Review Checklist
- [ ] All imports use ESM syntax
- [ ] All exports use ESM syntax
- [ ] No `require()` except Monaco AMD
- [ ] No `module.exports`
- [ ] File extensions present on relative imports
- [ ] Node.js built-ins use `node:` prefix
- [ ] No linting errors
- [ ] Code style consistent

### Final Verification
- [ ] Fresh install: `rm -rf node_modules && npm install`
- [ ] Clean start: `npm start`
- [ ] Full functionality test
- [ ] No console errors
- [ ] All tabs work
- [ ] Transpiler works end-to-end

### Create Commit
- [ ] Stage all changes: `git add .`
- [ ] Review diff carefully
- [ ] Create descriptive commit message
- [ ] Note breaking changes (if any)

## Phase 8: Post-Conversion

### Monitor for Issues
- [ ] Test with real flight controller (if possible)
- [ ] Monitor for user-reported issues
- [ ] Check CI/CD pipeline (if exists)

### Follow-Up Tasks
- [ ] Consider enabling strict ESM mode
- [ ] Consider adding module bundling optimization
- [ ] Consider adding tree-shaking analysis
- [ ] Update build pipeline if needed

## Common Conversion Patterns

### Pattern 1: Simple Default Export
```javascript
// CommonJS (BEFORE)
module.exports = MyClass;

// ESM (AFTER)
export default MyClass;
```

### Pattern 2: Named Exports Object
```javascript
// CommonJS (BEFORE)
module.exports = {
  functionA,
  functionB,
  CONSTANT
};

// ESM (AFTER)
export { functionA, functionB, CONSTANT };
```

### Pattern 3: Inline Exports
```javascript
// CommonJS (BEFORE)
function helper() { ... }
module.exports.helper = helper;

// ESM (AFTER)
export function helper() { ... }
```

### Pattern 4: Default Import
```javascript
// CommonJS (BEFORE)
const Parser = require('./parser');

// ESM (AFTER)
import Parser from './parser.js';
```

### Pattern 5: Named Imports
```javascript
// CommonJS (BEFORE)
const { GUI, TABS } = require('../js/gui');

// ESM (AFTER)
import { GUI, TABS } from '../js/gui.js';
```

### Pattern 6: Node.js Built-ins
```javascript
// CommonJS (BEFORE)
const path = require('path');

// ESM (AFTER)
import path from 'node:path';
```

### Pattern 7: Dynamic Import (if truly needed)
```javascript
// CommonJS (BEFORE)
function loadModule() {
  const mod = require('./module');
  return mod;
}

// ESM (AFTER)
async function loadModule() {
  const mod = await import('./module.js');
  return mod;
}
```

## Notes

- **Order matters** - Convert exports before imports to avoid breakage
- **Test frequently** - After each major file, test the transpiler
- **Backup first** - Create git branch before starting
- **Monaco loader** - Do NOT convert `window.require()` for Monaco
- **File extensions** - ESM requires `.js` on relative imports
- **Dynamic imports** - Use `await import()` if truly runtime-conditional

## Questions for Manager

- Should we handle dynamic requires with top-level imports or async dynamic imports?
- Any concerns about Monaco AMD loader coexistence with ESM?
- Should we convert everything in one PR or split by subsystem?
- Testing strategy: SITL only or also test with real FC?
