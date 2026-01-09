# INAV Firmware Code Review - Task Checklist

## Phase 1: Automated Analysis

- [ ] Install cppcheck (`sudo apt install cppcheck`)
- [ ] Run cppcheck on src/main/ with recommended flags
- [ ] Save output to `cppcheck-results.txt`
- [ ] Filter out noise (unused functions in target-specific code)
- [ ] Categorize findings by directory and severity
- [ ] Create summary report of automated findings

## Phase 2: Manual Review (by priority)

### Priority 1: navigation/ (12,050 lines)
- [ ] Review cppcheck findings for this directory
- [ ] Manual review of state machine logic
- [ ] Check waypoint/RTH edge cases
- [ ] Review GPS data validation
- [ ] Document findings

### Priority 2: flight/ (7,052 lines)
- [ ] Review cppcheck findings for this directory
- [ ] Check PID controller edge cases
- [ ] Review failsafe logic
- [ ] Check motor mixing bounds
- [ ] Document findings

### Priority 3: fc/ (16,200 lines)
- [ ] Review cppcheck findings for this directory
- [ ] Check arming logic completeness
- [ ] Review mode transitions
- [ ] Check CLI command handling
- [ ] Document findings

### Priority 4: sensors/ (5,292 lines)
- [ ] Review cppcheck findings for this directory
- [ ] Check IMU fusion edge cases
- [ ] Review calibration logic
- [ ] Check overflow/underflow in calculations
- [ ] Document findings

### Priority 5: rx/ (5,201 lines)
- [ ] Review cppcheck findings for this directory
- [ ] Check protocol parsing edge cases
- [ ] Review failsafe trigger conditions
- [ ] Check channel validation
- [ ] Document findings

## Phase 3: Issue Creation

- [ ] File GitHub issues for confirmed bugs
- [ ] Create PRs for simple fixes
- [ ] Document any "won't fix" decisions with rationale

## Completion Criteria

- All cppcheck warnings reviewed and categorized
- Top 5 priority directories manually reviewed
- All confirmed bugs tracked in GitHub
