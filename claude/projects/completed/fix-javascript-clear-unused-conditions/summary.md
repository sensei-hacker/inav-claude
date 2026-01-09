# Project: Fix JavaScript Programming - Clear Unused Logic Conditions

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix / Data Integrity
**Created:** 2025-12-02
**Estimated Time:** 1-2 hours

---

## Overview

Fix data integrity bug in JavaScript Programming tab where saving a transpiled script doesn't clear pre-existing logic conditions that are not part of the new script.

---

## Problem

When a user saves a JavaScript program to the flight controller:
- **Current:** Only writes new conditions, leaves old/stale conditions in unused slots
- **Expected:** Should clear any previously-occupied slots that aren't in the new script
- **Impact:** Stale logic conditions remain active, could cause unexpected flight behavior

**Example:**
1. User has 20 logic conditions on FC
2. Writes JavaScript that generates 10 conditions
3. Saves to FC
4. **BUG:** FC has 10 new + 10 stale conditions (should be only 10 new)

---

## Root Cause

**File:** `inav-configurator/tabs/javascript_programming.js`

The `saveToFC()` function:
1. Calls `FC.LOGIC_CONDITIONS.flush()` - clears in-memory array
2. Populates with new transpiled conditions
3. Calls `mspHelper.sendLogicConditions()`
4. **Problem:** Only sends conditions in the array, doesn't clear unused slots on FC

---

## Solution

**Smart approach - don't send all 64 slots:**

1. **At load:** Track which slots were occupied (`loadFromFC()`)
2. **At save:**
   - Identify newly-occupied slots (from transpiler)
   - For previously-occupied but now-unused slots: add disabled condition
   - Send all (new + cleared)

**Benefits:**
- Only sends necessary conditions
- More efficient than sending all 64
- Maintains data integrity

---

## Objectives

1. Track previously-occupied logic condition slots at load time
2. Clear unused slots at save time
3. Ensure only transpiled conditions remain on FC
4. No regression in Programming tab behavior

---

## Scope

**In Scope:**
- Modify `tabs/javascript_programming.js` (loadFromFC, saveToFC)
- Track occupied slots at load
- Clear unused slots at save
- Manual testing with SITL

**Out of Scope:**
- Changes to Programming tab (should continue working normally)
- Changes to MSPHelper (unless investigation reveals necessary)
- Refactoring LogicConditionsCollection (unless required)

---

## Implementation Plan

### Investigation Phase (30 min)
1. Analyze `LogicConditionsCollection` - how it stores conditions
2. Analyze `sendLogicConditions()` - how it sends indices
3. Determine if Collection needs refactoring or if current approach works

### Implementation Phase (30-60 min)
1. Add slot tracking in `loadFromFC()`
2. Add slot clearing in `saveToFC()`
3. Test with SITL (15→5 condition test)

### Testing Phase (15-30 min)
1. Manual test: 15 conditions → 5 conditions
2. Verify via Programming tab and CLI
3. Test edge cases (empty script, first save, full script)

---

## Success Criteria

- [ ] Previously-occupied slots tracked at load
- [ ] Unused slots cleared at save
- [ ] Manual test passes (15→5)
- [ ] Programming tab still works (no regression)
- [ ] CLI shows correct conditions
- [ ] Decompiler shows correct script after reload

---

## Files Modified

**Primary:**
- `inav-configurator/tabs/javascript_programming.js`

**Possibly (TBD after investigation):**
- `inav-configurator/js/logicConditionsCollection.js`
- `inav-configurator/js/msp/MSPHelper.js`

---

## Testing Strategy

**Manual Test:**
1. Setup: Create 15 conditions via Programming tab, save
2. Test: Write JS script with 5 conditions, save
3. Verify: Only 5 conditions exist (Programming tab + CLI)
4. Edge: Test empty script (all cleared)
5. Edge: Test 64 conditions (all slots used)

---

## Priority Justification

**HIGH priority because:**
- **Flight safety:** Stale logic conditions could trigger unexpected behavior
- **Data integrity:** Users expect save operation to be authoritative
- **User confusion:** Decompiler might show different code than what was saved
- **Current blocker:** Feature is incomplete without proper cleanup

---

## Related Work

- JavaScript Programming transpiler (PR #2439, #2451)
- May be included in existing PR or separate bugfix PR
- Should be fixed before transpiler feature is considered complete

---

## Estimated Time

**1-2 hours total:**
- Investigation: 30 min
- Implementation: 30-60 min
- Testing: 15-30 min

**Risk:** LOW (well-scoped, clear solution)

---

## Assignment

**Assigned to:** Developer
**Assignment email:** `claude/manager/sent/2025-12-02-2155-task-clear-unused-logic-conditions.md`
**Branch:** TBD (master or maintenance branch with JS transpiler)
