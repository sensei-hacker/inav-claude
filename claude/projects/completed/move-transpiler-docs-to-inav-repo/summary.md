# Move Transpiler Documentation to INAV Repo

**Status:** 📝 PLANNED
**Type:** Documentation / Repository Organization
**Priority:** High
**Created:** 2025-11-24
**Branch:** programming_transpiler_js

## Problem

JavaScript transpiler documentation is currently in the inav-configurator repository, but it should be in the main INAV repository alongside the logic conditions documentation. Additionally, there are no cross-links between the traditional logic conditions documentation and the new JavaScript programming documentation.

## Objectives

1. Copy TESTING_GUIDE.md to transpiler tests directory for developer reference
2. Move transpiler documentation to INAV repository
3. Create cross-links between logic conditions and JavaScript programming documentation

## Tasks

### Task 1: Copy TESTING_GUIDE.md to Tests Directory

**Source:** `inav-configurator/js/transpiler/docs/TESTING_GUIDE.md`
**Destination:** `inav-configurator/js/transpiler/transpiler/tests/TESTING_GUIDE.md`

**Purpose:** Keep testing guide close to test files for easy developer reference

### Task 2: Move Transpiler Docs to INAV Repo

**Source:** `inav-configurator/js/transpiler/` (entire directory)
**Destination:** `inav/docs/javascript_programming/`

**Contents to move:**
- `js/transpiler/docs/` - All documentation files
- `js/transpiler/api/` - API definitions
- `js/transpiler/examples/` - Example code
- `js/transpiler/scripts/` - Utility scripts (if applicable)

**Note:** The actual transpiler code (`js/transpiler/transpiler/`) stays in inav-configurator since it's part of the configurator app.

### Task 3: Add Cross-Links Between Documentation

**File to update:** `inav/docs/Programming Framework.md`

**Add links:**
1. From Logic Conditions section → JavaScript Programming Guide
2. Introduction mentioning JavaScript alternative
3. Comparison section (if appropriate)

**Files in javascript_programming/ to update:**
- Main guide (JAVASCRIPT_PROGRAMMING_GUIDE.md) should link back to Programming Framework.md
- Add section explaining relationship to traditional logic conditions

## Expected Directory Structure After Move

```
inav/
└── docs/
    ├── Programming Framework.md (updated with links)
    └── javascript_programming/
        ├── docs/
        │   ├── index.md
        │   ├── JAVASCRIPT_PROGRAMMING_GUIDE.md (updated with links)
        │   ├── TESTING_GUIDE.md
        │   ├── api_definitions_summary.md
        │   ├── OPERATIONS_REFERENCE.md
        │   ├── JavaScript_Variables.md
        │   ├── Auto_Import.md
        │   ├── TIMER_WHENCHANGED_IMPLEMENTATION.md
        │   ├── TIMER_WHENCHANGED_EXAMPLES.md
        │   ├── api_maintenance_guide.md
        │   ├── GENERATE_CONSTANTS_README.md
        │   └── implementation_summary.md
        ├── api/
        │   └── definitions/
        ├── examples/
        └── scripts/ (if applicable)

inav-configurator/
└── js/
    └── transpiler/
        ├── transpiler/
        │   ├── tests/
        │   │   ├── TESTING_GUIDE.md (copied here)
        │   │   ├── *.test.cjs
        │   │   └── ...
        │   ├── codegen.js
        │   ├── analyzer.js
        │   ├── parser.js
        │   └── ...
        ├── index.js
        └── editor/
```

## Cross-Link Examples

### In Programming Framework.md

Add near the beginning:
```markdown
## JavaScript-Based Programming (Alternative)

INAV also supports a JavaScript-based programming interface that provides a more
familiar syntax for those comfortable with JavaScript. See the
[JavaScript Programming Guide](javascript_programming/docs/JAVASCRIPT_PROGRAMMING_GUIDE.md)
for details.

The JavaScript code is transpiled into traditional logic conditions, so both methods
ultimately use the same underlying system.
```

Add in appropriate section:
```markdown
## Related Documentation

- [JavaScript Programming Guide](javascript_programming/docs/JAVASCRIPT_PROGRAMMING_GUIDE.md) -
  Alternative JavaScript-based syntax for programming logic conditions
- [JavaScript Variables](javascript_programming/docs/JavaScript_Variables.md) -
  Using variables in JavaScript programming
```

### In JAVASCRIPT_PROGRAMMING_GUIDE.md

Add near the beginning:
```markdown
## Relationship to Logic Conditions

This JavaScript programming interface is built on top of INAV's traditional
[Logic Conditions](../Programming%20Framework.md) system. The JavaScript code you
write is transpiled (converted) into logic conditions that run on the flight controller.

If you're familiar with the traditional logic conditions interface, you can think of
JavaScript programming as a more user-friendly syntax that generates the same logic
conditions behind the scenes.

See the [Programming Framework documentation](../Programming%20Framework.md) for details
about the underlying logic conditions system.
```

## Git Operations

### Step 1: Copy TESTING_GUIDE.md
```bash
cp inav-configurator/js/transpiler/docs/TESTING_GUIDE.md \
   inav-configurator/js/transpiler/transpiler/tests/TESTING_GUIDE.md
```

### Step 2: Move transpiler docs to INAV repo
```bash
# In inav-configurator
git mv js/transpiler/docs inav/docs/javascript_programming/docs
git mv js/transpiler/api inav/docs/javascript_programming/api
git mv js/transpiler/examples inav/docs/javascript_programming/examples
# scripts if needed
```

**Note:** Since these are in different repositories, this will likely require:
1. Copy files to inav repo
2. Add to git in inav repo
3. Remove from inav-configurator repo
4. Commit in both repos

### Step 3: Update cross-links
```bash
# Edit Programming Framework.md in inav
# Edit JAVASCRIPT_PROGRAMMING_GUIDE.md in inav
```

## Testing

- [ ] Verify all moved files are accessible
- [ ] Check all links work correctly
- [ ] Verify relative paths are correct
- [ ] Test links from Programming Framework.md
- [ ] Test links from JAVASCRIPT_PROGRAMMING_GUIDE.md
- [ ] Ensure TESTING_GUIDE.md is in tests directory

## Success Criteria

- [ ] TESTING_GUIDE.md copied to transpiler tests directory
- [ ] All transpiler documentation moved to inav/docs/javascript_programming/
- [ ] Programming Framework.md contains links to JavaScript programming docs
- [ ] JavaScript programming docs contain links back to Programming Framework.md
- [ ] All links are functional and use correct relative paths
- [ ] Both repositories have clean commits

## Estimated Time

~2-3 hours
- Copy TESTING_GUIDE.md: 5 minutes
- Move documentation: 30-45 minutes
- Add cross-links: 30-45 minutes
- Test all links: 30 minutes
- Git operations and commits: 30 minutes

## Notes

- This improves documentation discoverability
- Centralizes INAV documentation in main repository
- Maintains testing guide in both locations (docs and tests)
- Creates clear navigation between traditional and JavaScript approaches
- Should be done on programming_transpiler_js branch
- Will require commits to both inav and inav-configurator repos

## Related Projects

- This complements the transpiler refactoring work
- Should be completed before major merge to master
- Makes documentation easier to find for INAV users
