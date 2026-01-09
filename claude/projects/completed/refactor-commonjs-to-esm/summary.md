# Project: Convert CommonJS to ESM Syntax

**Status:** ✅ Complete
**Priority:** Medium
**Type:** Refactor
**Created:** 2025-11-24
**Completed:** 2025-11-24

## Overview

Convert all CommonJS `require()` and `module.exports` syntax to modern ESM `import`/`export` syntax across the INAV Configurator codebase.

## Context

The project's `package.json` already declares `"type": "module"` (line 7), indicating the project is configured for ESM. However, many files still use legacy CommonJS syntax:

- **91 `require()` calls** across 23 files
- **51 `module.exports` statements** across 30 files

This creates inconsistency and prevents taking full advantage of ESM features like tree-shaking, static analysis, and better IDE support.

## Scope

### Primary Files (User-Specified)

**Configurator Main:**
- `js/configurator_main.js:242` - Dynamic require for search tab
- `js/configurator_main.js:247` - Dynamic require for javascript_programming tab

**Tabs:**
- `tabs/javascript_programming.js` - 8 requires (lines 9-14, 103, 181)
  - MSPChainerClass, mspHelper, GUI/TABS, FC, path, i18n
  - Dynamic `require('path')` at line 103
  - Monaco loader `window.require()` at line 181 (special case)
- `tabs/search.js` - 3 requires (lines 1-3)
  - GUI/TABS, path, i18n

**Transpiler (entire directory):**
- `js/transpiler/*.js` - All transpiler files including:
  - `api/definitions/*.js` (flight, waypoint, gvar, events, helpers, override, rc, pid)
  - `transpiler/*.js` (parser, analyzer, codegen, decompiler, error_handler, optimizer, etc.)
  - `editor/*.js` (diagnostics, monaco_loader)
  - `scripts/*.js` (generate-constants)
  - `examples/*.js`

### Dependency Chain Files

All files referenced by the above, including:
- `js/msp/MSPchainer.js`
- `js/msp/MSPHelper.js`
- `js/gui.js`
- `js/fc.js`
- `js/localization.js`
- `js/keywordSearch.js`
- Any other files that export to or import from the above

## Technical Challenges

### 1. Dynamic Requires

Some requires are inside functions, not at top level:

```javascript
// tabs/javascript_programming.js:103
const path = require('path');
```

**Solution:** Move to top-level imports or use dynamic `import()` if truly needed at runtime.

### 2. Monaco Loader Special Case

```javascript
// tabs/javascript_programming.js:181
window.require(['vs/editor/editor.main'], function() { ... });
```

**Solution:** This is Monaco's AMD loader - leave unchanged. Only convert Node.js `require()`.

### 3. Destructuring Imports

```javascript
// CommonJS
const { GUI, TABS } = require('./../js/gui');

// ESM
import { GUI, TABS } from './../js/gui.js';
```

**Note:** ESM requires `.js` extension in relative imports.

### 4. Default vs Named Exports

Need to check each `module.exports` to determine if it should be:
- `export default` (single export)
- `export { ... }` (named exports)
- `export const/function/class` (inline exports)

### 5. Node.js Built-ins

```javascript
// CommonJS
const path = require('path');

// ESM
import path from 'node:path';
// or
import * as path from 'path';
```

Prefer `node:` prefix for clarity.

### 6. Circular Dependencies

CommonJS handles circular dependencies more gracefully than ESM. Need to identify and potentially refactor circular imports.

## Implementation Plan

### Phase 1: Analysis (2 hours)
1. Map all require() calls to their sources
2. Identify dynamic vs static requires
3. Identify circular dependencies
4. Map all module.exports patterns
5. Create dependency graph

### Phase 2: Exports First (3 hours)
Convert all `module.exports` to ESM exports:
1. Start with leaf nodes (no dependencies)
2. Transpiler API definitions
3. Transpiler utilities
4. Main transpiler modules
5. Tab modules
6. Configurator main

### Phase 3: Imports (3 hours)
Convert all `require()` to ESM imports:
1. Update import paths (add .js extensions)
2. Convert destructuring syntax
3. Handle Node.js built-ins
4. Move dynamic requires to top or use dynamic import()

### Phase 4: Testing (2 hours)
1. Test transpiler unit tests
2. Test configurator tabs load correctly
3. Test Monaco editor integration
4. Verify no runtime errors
5. Test with Electron dev tools

### Phase 5: Cleanup (1 hour)
1. Remove any conversion utilities
2. Update documentation
3. Verify consistency

## Expected Benefits

1. **Modern JavaScript** - Align with ES6+ standards
2. **Better Performance** - Enable tree-shaking and dead code elimination
3. **Static Analysis** - Better IDE support, faster module resolution
4. **Consistency** - Match package.json configuration
5. **Future-Proof** - CommonJS is legacy, ESM is the standard

## Files to Convert

### Transpiler (Priority 1 - Most Impact)
```
js/transpiler/
├── index.js
├── api/
│   ├── definitions/
│   │   ├── index.js
│   │   ├── flight.js
│   │   ├── waypoint.js
│   │   ├── gvar.js
│   │   ├── events.js
│   │   ├── helpers.js
│   │   ├── override.js
│   │   ├── rc.js
│   │   └── pid.js
│   └── types.js
├── transpiler/
│   ├── index.js
│   ├── parser.js
│   ├── analyzer.js
│   ├── codegen.js
│   ├── decompiler.js
│   ├── error_handler.js
│   ├── optimizer.js
│   ├── constants.js
│   ├── inav_constants.js
│   └── arrow_function_helper.js
├── editor/
│   ├── diagnostics.js
│   └── monaco_loader.js
├── scripts/
│   └── generate-constants.js
└── examples/
    └── index.js
```

### Tabs (Priority 2)
```
tabs/
├── javascript_programming.js
└── search.js
```

### Core Files (Priority 3)
```
js/
├── configurator_main.js
├── gui.js
├── fc.js
├── localization.js
├── keywordSearch.js
└── msp/
    ├── MSPchainer.js
    └── MSPHelper.js
```

## Risk Assessment

**Low Risk:**
- Transpiler internal modules (well-tested, isolated)
- API definitions (simple exports)

**Medium Risk:**
- Tab modules (user-facing, integration points)
- Core configurator files (many dependencies)

**High Risk:**
- Dynamic requires (may break if not handled correctly)
- Circular dependencies (may need refactoring)
- Monaco loader integration (must preserve AMD loader)

## Testing Strategy

1. **Unit Tests** - Run existing transpiler tests
2. **Integration** - Load each tab in configurator
3. **End-to-End** - Transpile code, save to FC (SITL)
4. **Manual** - Open DevTools, check for module errors

## Success Criteria

- [ ] All `require()` calls converted to `import`
- [ ] All `module.exports` converted to `export`
- [ ] No runtime errors in Electron
- [ ] All tabs load correctly
- [ ] Transpiler functions correctly
- [ ] Unit tests pass
- [ ] Code is more maintainable

## Estimated Time

**Total:** ~11 hours

- Phase 1 (Analysis): 2 hours
- Phase 2 (Exports): 3 hours
- Phase 3 (Imports): 3 hours
- Phase 4 (Testing): 2 hours
- Phase 5 (Cleanup): 1 hour

## Related Projects

- **improve-transpiler-error-reporting** (completed) - Error handling system
- **fix-transpiler-api-mismatches** (completed) - API definitions accuracy

This refactor will make the codebase more maintainable for future enhancements.
