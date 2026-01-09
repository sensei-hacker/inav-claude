# Task Assignment: Fix Duplicate "Active When" Column

**Date:** 2025-11-24 20:10
**Project:** fix-duplicate-active-when-column
**Priority:** Low
**Estimated Effort:** ~5 minutes
**Branch:** Create from master

## Task

Remove duplicate "Active When" column header in Programming tab Logic Conditions table.

## Problem

`tabs/programming.html` shows "Active When" column twice in table header:
- **Line 23:** `<th data-i18n="logicActivator"></th>` (REMOVE THIS)
- **Line 26:** `<th data-i18n="logicActivator"></th>` (KEEP THIS)

## Solution

Delete line 23 from `tabs/programming.html`.

**Before:**
```html
<tr>
    <th data-i18n="logicActivator"></th>          <!-- Line 23: DELETE -->
    <th style="width: 50px" data-i18n="logicId"></th>
    <th style="width: 80px" data-i18n="logicEnabled"></th>
    <th data-i18n="logicActivator"></th>          <!-- Line 26: KEEP -->
    <th style="width: 120px" data-i18n="logicOperation"></th>
    ...
</tr>
```

**After:**
```html
<tr>
    <th style="width: 50px" data-i18n="logicId"></th>
    <th style="width: 80px" data-i18n="logicEnabled"></th>
    <th data-i18n="logicActivator"></th>
    <th style="width: 120px" data-i18n="logicOperation"></th>
    ...
</tr>
```

## Files

- `tabs/programming.html` (line 23)

## Branch

**Important:** Create branch from **master**, not programming_transpiler_js.

## Testing

- Load Programming tab
- Verify "Active When" appears once (after Enabled, before Operation)
- Verify table layout looks correct

---

**Manager**
