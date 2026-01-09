# Todo List: Fix GPS Recovery After Signal Loss

## Phase 1: Investigation

- [x] Read GitHub issue #11049 for full context and user comments
- [x] Study GPS signal state management in `src/main/io/gps.c`
- [x] Study navigation position estimator (`navigation_pos_estimator.c`)
- [x] Identify how GPS fix status is tracked
- [x] Trace what happens when GPS fix is lost
- [x] Trace what happens when GPS fix is recovered

## Phase 2: Root Cause Analysis

- [x] Identify where altitude value is being zeroed/stuck
- [x] Identify where distance-to-home is being zeroed/stuck
- [x] Understand the intended recovery behavior
- [x] Document the bug's root cause

## Phase 3: Implementation

- [x] Design fix approach
- [x] Implement fix
- [x] Verify code compiles (SITL target)
- [x] Review changes for potential side effects

## Phase 4: Testing

- [x] Test normal GPS operation in SITL
- [x] Test GPS loss scenario (if simulatable)
- [x] Test GPS recovery scenario (if simulatable)
- [x] Document testing results

## Completion

- [x] Code compiles successfully
- [x] Root cause documented
- [x] Fix implemented and tested
- [x] PR submitted (#11144)
- [x] Send completion report to manager
