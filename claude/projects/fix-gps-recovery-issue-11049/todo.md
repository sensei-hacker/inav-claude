# Todo List: Fix GPS Recovery After Signal Loss

## Phase 1: Investigation

- [ ] Read GitHub issue #11049 for full context and user comments
- [ ] Study GPS signal state management in `src/main/io/gps.c`
- [ ] Study navigation position estimator (`navigation_pos_estimator.c`)
- [ ] Identify how GPS fix status is tracked
- [ ] Trace what happens when GPS fix is lost
- [ ] Trace what happens when GPS fix is recovered

## Phase 2: Root Cause Analysis

- [ ] Identify where altitude value is being zeroed/stuck
- [ ] Identify where distance-to-home is being zeroed/stuck
- [ ] Understand the intended recovery behavior
- [ ] Document the bug's root cause

## Phase 3: Implementation

- [ ] Design fix approach
- [ ] Implement fix
- [ ] Verify code compiles (SITL target)
- [ ] Review changes for potential side effects

## Phase 4: Testing

- [ ] Test normal GPS operation in SITL
- [ ] Test GPS loss scenario (if simulatable)
- [ ] Test GPS recovery scenario (if simulatable)
- [ ] Document testing results

## Completion

- [ ] Code compiles successfully
- [ ] Root cause documented
- [ ] Fix implemented and tested
- [ ] Send completion report to manager
