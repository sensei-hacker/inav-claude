# Task Assignment: Fix Duplicate "Active When" Column

**Date:** 2025-11-24 20:10
**Project:** fix-duplicate-active-when-column
**Priority:** Low
**Estimated Effort:** ~5 minutes
**Branch:** Create from master

## Task

Remove duplicate "Active When" column in Programming tab Logic Conditions table.
Check to see whether that's only an extra <th> tag, or if it also has matching <td> tags which make up that column.

## Problem

`tabs/programming.html` shows "Active When" column twice in table header:
- **Line 23:** `<th data-i18n="logicActivator"></th>` (REMOVE THIS)
- **Line 26:** `<th data-i18n="logicActivator"></th>` (KEEP THIS)

## Solution


## Branch

**Important:** Create branch from **master**, not programming_transpiler_js.

## Testing

- Load Programming tab
- Verify "Active When" appears once (after Enabled, before Operation)
- Verify table layout looks correct

---

**Manager**
