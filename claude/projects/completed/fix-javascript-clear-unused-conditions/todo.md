# Todo List: Fix JavaScript Programming - Clear Unused Logic Conditions

## Phase 1: Investigation

- [ ] Analyze `LogicConditionsCollection` class
  - [ ] Understand how conditions are stored (array vs map)
  - [ ] Check if original FC slot indices are preserved
- [ ] Analyze `sendLogicConditions()` in MSPHelper
  - [ ] Verify how slot indices are determined
  - [ ] Check if sparse arrays work correctly
- [ ] Document findings and choose implementation approach

## Phase 2: Implementation

- [ ] Modify `loadFromFC()` in javascript_programming.js
  - [ ] Add tracking of previously-occupied slots
  - [ ] Store in instance variable (e.g., `self.previouslyOccupiedSlots`)
- [ ] Modify `saveToFC()` in javascript_programming.js
  - [ ] Calculate which slots are newly occupied
  - [ ] Identify previously-occupied but now-unused slots
  - [ ] Add disabled conditions for unused slots
- [ ] Handle edge cases
  - [ ] First save (no previous conditions)
  - [ ] Empty script (clear all)
  - [ ] Full script (64 conditions)

## Phase 3: Testing

- [ ] Create test setup (15 conditions via Programming tab)
- [ ] Test main scenario (15→5 conditions)
  - [ ] Verify via Programming tab
  - [ ] Verify via CLI `logic` command
  - [ ] Verify via JS tab reload/decompile
- [ ] Test edge case: empty script
  - [ ] All previous conditions cleared
- [ ] Test edge case: first save
  - [ ] No errors when previouslyOccupiedSlots is empty
- [ ] Test edge case: 64 conditions
  - [ ] All slots used, no clearing needed
- [ ] Test regression: Programming tab
  - [ ] Normal save/load still works

## Phase 4: Documentation & PR

- [ ] Update code comments
- [ ] Test locally (npm run make, verify build)
- [ ] Create branch and commit
- [ ] Send completion report to manager

## Notes

- Priority: HIGH (data integrity / flight safety)
- Estimated time: 1-2 hours
- Files: primarily `tabs/javascript_programming.js`
- May need LogicConditionsCollection or MSPHelper changes (TBD)
