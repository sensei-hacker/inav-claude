# Project: Fix Search Tab tabNames Error

**Status:** 📋 TODO
**Priority:** High
**Type:** Bug Fix
**Created:** 2025-11-29
**Estimated Time:** 30 minutes - 1 hour

## Overview

The Search tab in the configurator throws a JavaScript error on load due to undefined `tabNames` variable.

## Problem

**Error:**
```
search.js:9 Uncaught (in promise) ReferenceError: tabNames is not defined
    at search.js:9:10
```

The search tab references a `tabNames` variable that is not defined or not properly imported.

## Objectives

1. Find where `tabNames` should be defined/imported
2. Add the missing import or define the variable
3. Verify the search tab works correctly

## Scope

**In Scope:**
- Fix the undefined `tabNames` error in search.js
- Ensure search tab loads without errors

**Out of Scope:**
- Other search functionality issues
- Unrelated tab errors

## Implementation Steps

1. Read `tabs/search.js` line 9 to see how `tabNames` is used
2. Find where `tabNames` is defined in the codebase
3. Add the missing import to search.js
4. Test the search tab loads without errors

## Success Criteria

- [ ] No console error on search tab load
- [ ] Search tab functions correctly
- [ ] All existing tests pass

## Key Files

- `inav-configurator/tabs/search.js` - Has the error at line 9
- Search for `tabNames` definition in the codebase
