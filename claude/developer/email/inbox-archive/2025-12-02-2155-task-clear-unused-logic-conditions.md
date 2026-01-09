# Task Assignment: Clear Unused Logic Conditions on Save

**Date:** 2025-12-02 21:55
**To:** Developer
**From:** Manager
**Project:** New (standalone bug fix)
**Priority:** HIGH
**Estimated Effort:** 1-2 hours
**Branch:** From master or maintenance branch (check which branch has JS transpiler)

---

## Task

When saving a JavaScript program to the flight controller via the JavaScript Programming tab, we need to clear any pre-existing logic conditions that are NOT part of the new transpiled script.

---

## Problem

**Current behavior:**
1. User has 20 logic conditions on FC (from previous save or Programming tab)
2. User writes JavaScript that transpiles to 10 logic conditions
3. Saves to FC
4. **BUG:** FC now has conditions 0-9 (new script) PLUS conditions 10-19 (old, stale)

**Root cause:**
- `saveToFC()` in `tabs/javascript_programming.js` calls `FC.LOGIC_CONDITIONS.flush()` (line 603)
- This only clears the **in-memory** array
- Then populates it with new transpiled conditions (lines 606-634)
- Calls `mspHelper.sendLogicConditions` (line 639)
- `sendLogicConditions()` only sends conditions that exist in the array
- **Missing:** Sending disabled/empty conditions for previously-used slots

---

## Solution (Smart Approach)

**Don't send empty conditions for ALL 64 slots - that's wasteful.**

Instead:
1. **At load time** (`loadFromFC()`): Track which slots were occupied
2. **At save time** (`saveToFC()`):
   - Determine which slots are now being used (from transpiler output)
   - For slots that were previously occupied but are NOT in new script:
     - Add disabled/empty condition objects to `FC.LOGIC_CONDITIONS`
   - Send all conditions (new + cleared old slots)

---

## Implementation Details

### Step 1: Track Previously Occupied Slots

In `loadFromFC()` (around line 475), after loading logic conditions:

```javascript
// Store which slots were occupied before we modify them
self.previouslyOccupiedSlots = new Set();
const conditions = FC.LOGIC_CONDITIONS.get();
for (let i = 0; i < conditions.length; i++) {
    if (conditions[i].getEnabled() !== 0) {
        self.previouslyOccupiedSlots.add(i);
    }
}
```

### Step 2: Clear Unused Slots at Save Time

In `saveToFC()`, after populating new conditions (after line 634):

```javascript
// Clear previously-occupied slots that are NOT in the new script
const newlyOccupiedSlots = new Set();
const newConditions = FC.LOGIC_CONDITIONS.get();
for (let i = 0; i < newConditions.length; i++) {
    newlyOccupiedSlots.add(i);
}

// Find slots that need to be cleared (were occupied, now aren't)
if (self.previouslyOccupiedSlots) {
    for (const oldSlot of self.previouslyOccupiedSlots) {
        if (!newlyOccupiedSlots.has(oldSlot)) {
            // This slot was occupied before but isn't in new script
            // Add a disabled/empty condition to clear it
            const emptyCondition = {
                enabled: 0,
                activatorId: -1,
                operation: 0,
                operandAType: 0,
                operandAValue: 0,
                operandBType: 0,
                operandBValue: 0,
                flags: 0,

                getEnabled: function() { return this.enabled; },
                getActivatorId: function() { return this.activatorId; },
                getOperation: function() { return this.operation; },
                getOperandAType: function() { return this.operandAType; },
                getOperandAValue: function() { return this.operandAValue; },
                getOperandBType: function() { return this.operandBType; },
                getOperandBValue: function() { return this.operandBValue; },
                getFlags: function() { return this.flags; }
            };

            FC.LOGIC_CONDITIONS.put(emptyCondition);
        }
    }
}
```

### Step 3: Fix sendLogicConditions to Send by Index

**WAIT - Check this first:** The current `sendLogicConditions()` in `MSPHelper.js` sends conditions sequentially (0, 1, 2...) based on array order, but it includes the index in the buffer (line 2469: `buffer.push(conditionIndex)`).

**Issue:** If we have conditions at indices [0,1,2,15,20], the current code sends them as indices [0,1,2,3,4] which is WRONG.

**We need to either:**
- **Option A:** Ensure `FC.LOGIC_CONDITIONS` stores conditions with their actual indices (may require refactoring the Collection)
- **Option B:** Modify approach to send ALL 64 slots (disabled for unused)

**Investigate first** - Check if `LogicConditionsCollection` maintains index information or if conditions are just in a plain array.

---

## Files to Check

### Primary files:
- `inav-configurator/tabs/javascript_programming.js` (saveToFC, loadFromFC)
  - Line 475+: loadFromFC() - track occupied slots
  - Line 603+: saveToFC() - clear unused slots

### Secondary (may need changes):
- `inav-configurator/js/logicConditionsCollection.js` - How conditions are stored
- `inav-configurator/js/msp/MSPHelper.js` - sendLogicConditions (line 2451+)

### Reference (don't modify, just understand):
- `inav-configurator/js/logicCondition.js` - LogicCondition class structure

---

## Testing

### Manual Test Procedure:

1. **Setup:**
   - Connect to SITL or real FC
   - Via Programming tab: Create 15 logic conditions manually
   - Save to FC
   - Verify all 15 exist (via Programming tab or CLI `logic`)

2. **Test clearing:**
   - Switch to JavaScript Programming tab
   - Write simple script that generates 5 logic conditions:
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
   - Transpile (verify shows ~5 conditions)
   - Save to FC
   - **Verify:** Only 5 conditions exist on FC (conditions 6-14 should be cleared)

3. **Verification methods:**
   - Programming tab: Should show only 5 conditions
   - CLI: `logic` command should show conditions 0-4 enabled, rest disabled
   - Reload JavaScript tab: Should decompile to same script (no extra conditions)

---

## Success Criteria

- [ ] Previously-occupied slots are tracked at load time
- [ ] Unused slots are cleared at save time
- [ ] Only the conditions from the transpiled script remain on FC
- [ ] Old/stale conditions are removed
- [ ] Manual test passes (15→5 condition test)
- [ ] No regression: Saving from Programming tab still works normally

---

## Edge Cases to Consider

1. **First save (no previous conditions):** `previouslyOccupiedSlots` will be empty/undefined - handle gracefully
2. **Empty script:** Should clear ALL previously-occupied slots
3. **Full script (64 conditions):** Should work normally (all slots occupied)
4. **Switching between Programming tab and JS tab:** Each should manage conditions independently

---

## Investigation Questions

Before implementing, answer these:

1. **How does `LogicConditionsCollection` store conditions?**
   - Plain array (indices 0,1,2...) or indexed map?
   - Does it preserve original FC slot indices?

2. **How does `sendLogicConditions()` determine slot indices?**
   - Uses array index (wrong if sparse)?
   - Or stored index property (correct)?

3. **Do we need to refactor `LogicConditionsCollection`?**
   - To support sparse arrays or index mapping?
   - Or is simpler to send all 64 slots?

**Recommendation:** Start by investigating current behavior, then choose best implementation approach.

---

## Notes

- This is a **data integrity bug** - users could have stale/incorrect conditions active
- **High priority** because it affects flight safety (wrong logic conditions could trigger unexpected behavior)
- Related to transpiler/decompiler feature (PR #2439, #2451?)
- May want to include in same PR or separate bugfix PR

---

## Questions?

If you need clarification on:
- Expected behavior
- Implementation approach
- Testing procedure
- Integration with existing PRs

Let me know before starting implementation.

---

**Manager**
2025-12-02 21:55
