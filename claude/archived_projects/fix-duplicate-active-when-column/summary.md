# Fix Duplicate "Active When" Column

**Status:** ✉️ ASSIGNED
**Type:** Bug Fix
**Priority:** Low
**Created:** 2025-11-24
**Assigned:** 2025-11-24
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2010-task-fix-duplicate-column.md`
**Branch:** Create from master

## Problem

In `tabs/programming.html`, the Logic Conditions table header shows "Active When" column twice:
- Line 23: First instance (before ID# column)
- Line 26: Second instance (after Enabled column)

This creates visual duplication and confusion in the Programming tab UI.

## Solution

Remove the first instance of the "Active When" column header (line 23) from `tabs/programming.html`.

## Expected Result

Table header should show columns in this order:
- ID#
- Enabled
- Active When (only once)
- Operation
- Operand A
- Operand B
- Flags
- Status

## Files to Modify

**Primary:**
- `tabs/programming.html` (line 23) - Remove duplicate `<th data-i18n="logicActivator"></th>`

## Estimated Time

~5 minutes

## Testing

- Visual inspection of Programming tab
- Verify "Active When" appears only once in correct position
- Ensure table layout looks correct
