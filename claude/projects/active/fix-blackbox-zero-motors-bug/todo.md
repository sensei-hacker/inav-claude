# Todo List: Fix Blackbox Zero Motors Bug

## Phase 1: Setup

- [ ] Read bug documentation
  - [ ] `claude/developer/scripts/testing/inav/gps/MOTORS_CONDITION_BUG.md`
  - [ ] Understand root cause
  - [ ] Note line numbers to change

- [ ] Use git-workflow skill
  - [ ] Run `/git-workflow`
  - [ ] Branch: `fix-blackbox-zero-motors`
  - [ ] Base: `maintenance-9.x`

## Phase 2: Implementation

- [ ] Make required fix
  - [ ] Open `inav/src/main/blackbox/blackbox.c`
  - [ ] Find line 1079
  - [ ] Change `FLIGHT_LOG_FIELD_CONDITION_MOTORS`
  - [ ] To `FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1`

- [ ] Make optional consistency fix
  - [ ] Find line 1346 (P-frame)
  - [ ] Same change as above
  - [ ] For code consistency

- [ ] Verify changes
  - [ ] Check line numbers correct
  - [ ] Verify no other instances to change
  - [ ] Code looks correct

## Phase 3: Testing

- [ ] Compile firmware
  - [ ] Build test target
  - [ ] Verify no compile errors
  - [ ] Check warnings

- [ ] Optional hardware test
  - [ ] If hardware available with zero motors
  - [ ] Flash fixed firmware
  - [ ] Record blackbox
  - [ ] Decode and verify no failures

## Phase 4: PR Creation

- [ ] Create PR
  - [ ] Title: "Fix blackbox motor logging for zero-motor configurations"
  - [ ] Use concise description provided
  - [ ] Target: maintenance-9.x
  - [ ] Set milestone: 9.1

- [ ] PR metadata
  - [ ] Add `bug` label
  - [ ] Link to issue if exists (#10913?)
  - [ ] Verify description clear

- [ ] Verify PR
  - [ ] CI builds passing
  - [ ] No conflicts
  - [ ] Ready for review

## Completion

- [ ] PR submitted
- [ ] Milestone set correctly
- [ ] Send completion report to manager
