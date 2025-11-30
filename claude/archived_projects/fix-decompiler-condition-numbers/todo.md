# Todo List: Fix Decompiler Condition Number Comments

## Phase 1: Investigation

- [ ] Find where `// Condition can be read by logicCondition[N]` is generated
- [ ] Understand how chained conditions are tracked (first vs last index)
- [ ] Identify the bug - is it using the wrong index?

## Phase 2: Fix

- [ ] Fix to use the terminal/last condition index
- [ ] Test with the provided example logic conditions
- [ ] Verify the comment now shows correct numbers

## Phase 3: Testing

- [ ] Add test case for chained condition number comments
- [ ] Run full decompiler test suite
- [ ] Ensure no regressions

## Completion

- [ ] All tests passing
- [ ] Commit changes to transpiler_clean_copy branch
- [ ] Send completion report to manager
