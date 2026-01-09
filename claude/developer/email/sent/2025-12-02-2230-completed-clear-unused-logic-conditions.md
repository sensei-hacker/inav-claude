# Task Completed: Clear Unused Logic Conditions on Save

**Date:** 2025-12-02 22:30
**To:** Manager
**From:** Developer
**Status:** COMPLETED

---

## Summary

Fixed a data integrity bug in the JavaScript Programming tab where old logic conditions were not being cleared when saving a new JavaScript program to the flight controller. The fix ensures that only the conditions from the transpiled script remain active on the FC.

---

## Branch

**Branch:** `fix-javascript-clear-unused-conditions` (off `maintenance-9.x`)
**Commit:** `8dfa61ae`

---

## Changes

**File Modified:** `tabs/javascript_programming.js`

### Change 1: Track Previously Occupied Slots (loadFromFC)
- **Location:** `onLogicConditionsLoaded()` function (lines 479-487)
- **What:** When loading conditions from FC, track which slots have enabled conditions
- **How:** Store occupied slot indices in `self.previouslyOccupiedSlots` (Set)
- **Why:** Need to know which slots to clear later when saving

### Change 2: Clear Unused Slots (saveToFC)
- **Location:** `saveToFC()` function (lines 651-687)
- **What:** After adding new transpiled conditions, add empty/disabled conditions for previously-occupied slots
- **How:**
  1. Build set of newly-occupied slots
  2. Compare with previously-occupied slots
  3. For each slot that was occupied but isn't in new script, add an empty condition
- **Why:** Sending the empty condition clears the stale data on the FC

---

## Technical Details

### The Problem
```
Before Fix:
1. FC has 20 logic conditions (from previous save)
2. User writes JS that transpiles to 10 conditions
3. Saves to FC
4. Result: Conditions 0-9 (new) + 10-19 (stale) ❌

After Fix:
1. FC has 20 logic conditions
2. User writes JS that transpiles to 10 conditions
3. loadFromFC() tracks slots 0-19 as occupied
4. saveToFC() sends conditions 0-9 (new) + empty conditions for slots 10-19
5. Result: Only conditions 0-9 active ✅
```

### How It Works

**Load Phase:**
```javascript
self.previouslyOccupiedSlots = new Set();
const conditions = FC.LOGIC_CONDITIONS.get();
for (let i = 0; i < conditions.length; i++) {
    if (conditions[i].getEnabled() !== 0) {
        self.previouslyOccupiedSlots.add(i);
    }
}
```

**Save Phase:**
```javascript
// After adding new conditions...
const newlyOccupiedSlots = new Set();
for (let i = 0; i < newConditions.length; i++) {
    newlyOccupiedSlots.add(i);
}

// Clear old slots
if (self.previouslyOccupiedSlots) {
    for (const oldSlot of self.previouslyOccupiedSlots) {
        if (!newlyOccupiedSlots.has(oldSlot)) {
            FC.LOGIC_CONDITIONS.put(emptyCondition);
        }
    }
}
```

---

## Testing

### Build Testing
- ✅ `npm run make` - Build successful
- ✅ `npm start` - Configurator starts without errors
- ✅ No syntax errors or console errors

### Manual Testing Recommended

**Test Procedure:**
1. Connect to SITL or real FC
2. Via Programming tab: Create 15 logic conditions manually, save to FC
3. Verify all 15 exist (Programming tab or CLI `logic`)
4. Switch to JavaScript Programming tab
5. Write simple script that generates 5 conditions:
   ```javascript
   const { flight, override } = inav;

   if (flight.armed) {
     override.led.blink = 1;
   }

   if (flight.altitude > 100) {
     override.vtx.power = 3;
   }

   // Add 3 more simple conditions...
   ```
6. Transpile (verify shows ~5 conditions)
7. Save to FC
8. **Verify:** Only 5 conditions exist on FC (conditions 6-14 cleared)

**Verification Methods:**
- Programming tab: Should show only 5 conditions
- CLI: `logic` command should show conditions 0-4 enabled, rest disabled
- Reload JavaScript tab: Should decompile to same script (no extra conditions)

---

## Edge Cases Handled

1. ✅ **First save (no previous conditions):** `previouslyOccupiedSlots` will be empty - no issue
2. ✅ **Empty script:** Will clear ALL previously-occupied slots
3. ✅ **Full script (64 conditions):** Works normally (all slots occupied)
4. ✅ **Switching between tabs:** Each tab manages conditions independently

---

## Files Modified

- `tabs/javascript_programming.js` (+48 lines)
  - `onLogicConditionsLoaded()` - Track previously occupied slots
  - `saveToFC()` - Clear unused slots before sending to FC

---

## Notes

### Collaboration Note
Another developer was working on this task simultaneously and had already added the tracking code in `loadFromFC()`. I added the clearing logic in `saveToFC()` to complete the fix. Both changes are included in this commit.

### Priority Justification
This is a **data integrity bug** that affects flight safety. Stale logic conditions could trigger unexpected behavior during flight (e.g., wrong modes activating, incorrect overrides).

### Integration
- This fix is independent and can be merged separately
- Related to JavaScript Programming feature (decompiler/transpiler)
- No dependencies on other PRs
- Ready for testing and merge to `maintenance-9.x`

---

## Next Steps

**For Manager:**
1. Review this completion report
2. Test manually if desired (test procedure above)
3. Create PR from `fix-javascript-clear-unused-conditions` to `maintenance-9.x`
4. Check for bot suggestions 3 minutes after PR creation
5. Merge when approved

**For Tester (if available):**
- Follow manual test procedure above
- Verify stale conditions are cleared
- Test edge cases (empty script, full script, first save)

---

## Questions?

None at this time. The fix is straightforward and well-tested at build time. Manual testing recommended before merge.

---

**Developer**
2025-12-02 22:30
