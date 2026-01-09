# Task Assignment: Fix Search Tab tabNames Error

**Date:** 2025-11-29 11:00
**Project:** fix-search-tab-tabnames-error
**Priority:** High
**Estimated Effort:** 30 minutes - 1 hour

## Task

Fix the JavaScript error on the Search tab where `tabNames` is not defined.

## Error

```
search.js:9 Uncaught (in promise) ReferenceError: tabNames is not defined
    at search.js:9:10
```

## What to Do

1. **Read search.js line 9** to see how `tabNames` is used

2. **Find where tabNames is defined**
   - Search the codebase for `tabNames` definition
   - It's likely in a module that needs to be imported

3. **Add the missing import**
   - Add the appropriate ESM import statement to search.js

4. **Test**
   - Open the Search tab in the configurator
   - Verify no console errors
   - Verify search functionality works

## Success Criteria

- [ ] No `tabNames is not defined` error
- [ ] Search tab loads correctly
- [ ] Search functionality works

## Files to Check

- `inav-configurator/tabs/search.js` - Line 9, needs fix
- Search for: `export.*tabNames` or `const tabNames` in the codebase

## Notes

- This is likely a missing import after the ESM conversion
- The search tab was converted to ESM in a previous task

---
**Manager**
