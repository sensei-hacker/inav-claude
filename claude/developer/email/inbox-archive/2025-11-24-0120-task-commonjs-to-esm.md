# Task: Convert CommonJS to ESM Syntax

**Priority:** Medium
**Estimated Complexity:** Moderate
**Assigned Date:** 2025-11-24
**Estimated Time:** ~11 hours

## Context

The INAV Configurator's `package.json` declares `"type": "module"`, indicating the project should use modern ES Module (ESM) syntax. However, the codebase still contains legacy CommonJS `require()` and `module.exports` syntax throughout.

**Current state:**
- **91 `require()` calls** across 23 files
- **51 `module.exports` statements** across 30 files
- Mix of ESM and CommonJS creates inconsistency
- Missing out on ESM benefits (tree-shaking, static analysis, better IDE support)

This task is to modernize the codebase by converting all CommonJS syntax to ESM.

## The Problem

**Inconsistency:** Some modules use `require()` while the project is configured for ESM.

**Examples:**

```javascript
// tabs/javascript_programming.js (CommonJS)
const MSPChainerClass = require('./../js/msp/MSPchainer');
const { GUI, TABS } = require('./../js/gui');
const FC = require('./../js/fc');
const path = require('path');

// Should be (ESM)
import MSPChainerClass from './../js/msp/MSPchainer.js';
import { GUI, TABS } from './../js/gui.js';
import FC from './../js/fc.js';
import path from 'node:path';
```

```javascript
// js/transpiler/transpiler/error_handler.js (CommonJS)
module.exports = ErrorHandler;

// Should be (ESM)
export default ErrorHandler;
```

## Your Task

Convert all CommonJS syntax to ESM throughout the codebase, following the dependency chain from the specified files.

**Project Location:** `claude/projects/refactor-commonjs-to-esm/`

**Files Available:**
- `summary.md` - Complete technical overview and conversion strategy
- `todo.md` - Detailed phase-by-phase checklist

## Scope

### Primary Targets (User-Specified)

**1. Configurator Main**
- `js/configurator_main.js:242` - Dynamic require for search tab
- `js/configurator_main.js:247` - Dynamic require for javascript_programming tab

**2. Tabs**
- `tabs/javascript_programming.js` - 8 requires (MSP, GUI, FC, path, i18n)
- `tabs/search.js` - 3 requires (GUI, path, i18n)

**3. Transpiler (All Files)**
- `js/transpiler/*` - Entire transpiler directory including:
  - API definitions (flight, waypoint, gvar, events, helpers, override, rc, pid)
  - Transpiler core (parser, analyzer, codegen, decompiler, optimizer)
  - Editor integration (diagnostics, monaco_loader)
  - Scripts and examples

**4. Dependency Chain**
- All files imported by the above
- Follow the chain: MSP modules, GUI, FC, localization, etc.
- For files other than js/configurator_main.js javascript_programming.\* and js/transpiler/\* , report back your findings to the manager but do not change files outside of that scope right now

## Key Requirements

### 1. Convert All Exports

Change `module.exports` to ESM exports:

```javascript
// Pattern 1: Default export
module.exports = MyClass;  →  export default MyClass;

// Pattern 2: Named exports
module.exports = { a, b, c };  →  export { a, b, c };

// Pattern 3: Inline exports
module.exports.func = func;  →  export function func() { ... }
```

### 2. Convert All Imports

Change `require()` to ESM imports:

```javascript
// Default import
const X = require('./module');  →  import X from './module.js';

// Named imports (destructuring)
const { a, b } = require('./module');  →  import { a, b } from './module.js';

// Node.js built-ins
const path = require('path');  →  import path from 'node:path';
```

### 3. Add File Extensions

ESM requires explicit `.js` extensions on relative imports:

```javascript
// WRONG (will fail)
import Parser from './parser';

// CORRECT
import Parser from './parser.js';
```

### 4. Handle Special Cases

**Monaco AMD Loader** - Do NOT convert:
```javascript
// tabs/javascript_programming.js:181
window.require(['vs/editor/editor.main'], function() { ... });
// ^^^ Leave this unchanged - it's Monaco's AMD loader, not Node.js require
```

**Dynamic requires** - Evaluate on a case-by-case basis:
```javascript
// tabs/javascript_programming.js:103
const path = require('path');  // Inside a function
// → Move to top-level import if possible
// → Use dynamic import() if truly runtime-conditional
```

## Implementation Strategy

**Recommended order** (see todo.md for full checklist):

### Phase 1: Analysis (2 hours)
- Map all dependencies
- Identify circular dependencies (if any)
- Plan conversion order (leaf nodes first)

### Phase 2: Convert Exports (3 hours)
- Start with transpiler API definitions (leaf nodes)
- Move up dependency tree
- Transpiler utilities → Core → Main
- Tabs → Configurator main (last)

### Phase 3: Convert Imports (3 hours)
- Update all require() calls
- Add .js extensions
- Fix import paths
- Handle Node.js built-ins with node: prefix

### Phase 4: Testing (2 hours)
- Run transpiler unit tests (if available)
- Start configurator: `npm start`
- Test JavaScript Programming tab
- Test Search tab
- Verify Monaco editor loads
- Check for console errors

### Phase 5: Cleanup (1 hour)
- Remove any conversion artifacts
- Update documentation
- Final review

## Technical Challenges

### Challenge 1: Dynamic Requires
Some requires are inside functions. Evaluate whether they can move to top-level or need async dynamic imports.

### Challenge 2: Circular Dependencies
ESM handles circular dependencies differently than CommonJS. If any exist, may need refactoring.

### Challenge 3: Monaco AMD Loader
The Monaco editor uses an AMD loader (`window.require`). This is NOT Node.js require - leave it unchanged!

### Challenge 4: File Extensions
ESM requires explicit `.js` extensions. Easy to miss - search carefully.

## Testing Requirements

**Must pass:**
- [ ] Configurator starts without errors (`npm start`)
- [ ] JavaScript Programming tab loads
- [ ] Search tab loads
- [ ] Monaco editor initializes correctly
- [ ] Transpiler can transpile code
- [ ] No console errors in DevTools
- [ ] All tabs functional

**Nice to have:**
- [ ] Test with SITL if available
- [ ] Performance comparison (should be same or better)

## Success Criteria

You'll know this is complete when:
- [ ] All `require()` calls converted to `import` (except Monaco AMD)
- [ ] All `module.exports` converted to `export`
- [ ] All relative imports have `.js` extension
- [ ] Node.js built-ins use `node:` prefix
- [ ] Configurator starts and runs without errors
- [ ] All tabs load correctly
- [ ] Transpiler functions correctly
- [ ] Code is consistent with ESM standards

## Expected Benefits

1. **Consistency** - Match package.json configuration
2. **Performance** - Enable tree-shaking and dead code elimination
3. **Developer Experience** - Better IDE support, faster module resolution
4. **Modern Standards** - Align with ES6+ best practices
5. **Future-Proof** - ESM is the standard, CommonJS is legacy

## Important Notes

### Order Matters
Convert exports BEFORE imports. If you convert a file's imports before converting what it imports from, things will break.

### Test Frequently
After converting each major subsystem (e.g., transpiler API definitions), test the configurator. Catch issues early.

### Monaco Loader
**DO NOT TOUCH `window.require()` FOR MONACO EDITOR!** This is a different require system (AMD), not Node.js CommonJS.

### Backup First
Create a git branch before starting. This is a large refactor.

### File Extensions
ESM is strict about file extensions. Don't forget the `.js`!

## Communication

**Questions to ask:**
- Found circular dependencies - how should I refactor?
- Dynamic require at line X - move to top or use dynamic import()?
- Monaco AMD loader concerns - verify my understanding?

**Status updates:**
- After Phase 1: Share dependency graph findings
- After Phase 2: Report on exports conversion
- After Phase 4: Report testing results

## Resources

**Project Files:**
- `claude/projects/refactor-commonjs-to-esm/summary.md` - Full technical details
- `claude/projects/refactor-commonjs-to-esm/todo.md` - Detailed checklist

**Code Location:**
- `bak_inav-configurator/js/transpiler/` - Transpiler modules
- `bak_inav-configurator/tabs/` - Tab modules
- `bak_inav-configurator/js/configurator_main.js` - Main entry

**Related:**
- Previous transpiler work gives you familiarity with the codebase
- Error reporting system (recently completed) should continue working after conversion

## Common Pitfalls

1. **Forgetting .js extensions** - ESM requires them
2. **Converting Monaco AMD loader** - Don't do it!
3. **Not testing frequently** - Test after each major section
4. **Wrong export type** - Check if default vs named export
5. **Circular dependencies** - ESM is stricter than CommonJS

## Conversion Examples

See todo.md for complete pattern examples, including:
- Simple default exports
- Named exports objects
- Inline exports
- Default imports
- Named imports (destructuring)
- Node.js built-ins
- Dynamic imports (if needed)

## Next Steps

1. Read `summary.md` for complete context
2. Read `todo.md` for detailed checklist
3. Create git branch for this work
4. Begin Phase 1: Analysis
5. Map dependencies and create conversion plan
6. Send status report after Phase 1

This is a moderate complexity task that will significantly improve code quality. Take your time, test frequently, and ask questions if you encounter unexpected issues.

Looking forward to seeing the codebase fully modernized with ESM!

---

**Manager Note:** This follows the three completed transpiler projects. The developer is familiar with the transpiler codebase structure, which will help with this refactor.
