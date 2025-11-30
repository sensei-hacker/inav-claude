# Todo List: Verify GPS Fix and Refactor for Obviousness

## Phase 1: Code Analysis

- [ ] Read the full `onNewGPSData()` function in navigation_pos_estimator.c
- [ ] Find where `posEstimator.gps.lastUpdateTime` is used (timeout checks)
- [ ] Trace how stale lastUpdateTime causes positions to be stuck at zero
- [ ] Document the complete code path from GPS recovery → stuck values

## Phase 2: Answer Reviewer Questions

- [ ] Explain why positions go to zero (not freeze at last values)
- [ ] Investigate the 214km flight distance jump question
- [ ] Determine if this is definitively the root cause or "test and see"
- [ ] Draft response for PR comment

## Phase 3: Refactor for Clarity (if needed)

- [ ] Evaluate if the current code structure is clear enough
- [ ] Consider adding comments explaining the timing logic
- [ ] Consider restructuring the isFirstGPSUpdate logic
- [ ] Implement any beneficial refactoring

## Phase 4: Follow-up

- [ ] Respond to reviewer on GitHub PR
- [ ] File any additional issues discovered
- [ ] Update local branch with upstream changes

## Completion

- [ ] All reviewer questions answered
- [ ] Any refactoring committed
- [ ] Send completion report to manager
