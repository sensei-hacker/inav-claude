# Task Assignment: Investigate gyroLuluApplyFn Performance Difference

**Date:** 2025-12-22 22:59
**Project:** inav (firmware) - BLUEBERRY435 PID performance investigation
**Priority:** High
**Estimated Effort:** 2-4 hours

## Task

Investigate the `gyroLuluApplyFn()` function to identify what might cause a significant performance difference between BLUEBERRY435 and JHEMCU boards.

## Background

**Context:** BLUEBERRY435 PID performance investigation (ongoing)

**New Finding from Manufacturer:**
- Performance bottleneck appears to be in `gyroLuluApplyFn()`
- Disabling interrupts did NOT resolve the issue
- Significant time difference between BLUEBERRY435 and JHEMCU boards

**Reference:** `claude/developer/blueberry-pid-performance-investigation/` (existing investigation)

## What to Investigate

### 1. Analyze gyroLuluApplyFn Implementation

**Location:** `src/main/sensors/gyro.c` (around line 498 based on image)

Examine:
- Function implementation details
- Filter operations (rpFilterApplyFn, lp1ApplyFn, lp2ApplyFn)
- Mathematical operations (float calculations)
- Any loops or iterations
- Memory access patterns

### 2. Compare Hardware Differences

**BLUEBERRY435 vs JHEMCU:**
- MCU type and clock speed differences
- FPU (Floating Point Unit) capabilities
- Memory/cache differences
- DMA configuration differences
- Compiler optimization differences

### 3. Profile the Function

**Look for:**
- Float operations that might be slow on one board
- Memory access patterns (cache misses?)
- Filter state array access patterns
- Any board-specific optimizations or conditionals

### 4. Check Debug Code Impact

The image shows DEBUG_SET calls:
```c
DEBUG_SET(DEBUG_LULU, 6, gyroADCf - preLulu); //LULU delta debug
DEBUG_SET(DEBUG_LULU, axis + 3, gyroADCf);    //Post LULU Debug
```

**Verify:** Are these debug statements enabled on BLUEBERRY435 but not JHEMCU? Could this explain the difference?

### 5. Review Filter State Access

```c
gyroADCf = gyroLuluApplyFn(filter_t *) &gyroLuluState[axis], gyroADCf);
```

**Check:**
- How is `gyroLuluState` array accessed?
- Any alignment issues?
- Cache line bouncing between cores?

## What to Look For

### Potential Performance Bottlenecks:

1. **FPU differences:**
   - Does BLUEBERRY435 have slower float operations?
   - Single vs double precision differences?

2. **Memory access:**
   - Filter state array in different memory regions?
   - Cache miss rates?

3. **Compiler optimization:**
   - Different optimization levels for different targets?
   - Inlining differences?

4. **Debug code:**
   - DEBUG_SET enabled on one board but not the other?
   - BEEP_TOGGLE or LED2_TOGGLE differences?

5. **Filter complexity:**
   - LULU filter using more complex operations on one board?
   - Different filter configurations?

## Success Criteria

- [ ] Analyzed gyroLuluApplyFn implementation in detail
- [ ] Identified specific operations that could cause slowdown
- [ ] Compared BLUEBERRY435 vs JHEMCU hardware capabilities
- [ ] Checked debug code and its impact
- [ ] Proposed hypothesis for performance difference
- [ ] Recommended fix or mitigation strategy
- [ ] Updated investigation documentation

## Deliverables

**Report should include:**
1. Function analysis findings
2. Hardware comparison relevant to this function
3. Hypothesis for performance difference
4. Recommended fixes or optimizations
5. Testing plan to verify the fix

**Update:** `claude/developer/blueberry-pid-performance-investigation/`

## Notes

- This is a continuation of the existing BLUEBERRY435 investigation
- Manufacturer specifically identified this function as the bottleneck
- Disabling interrupts didn't help, so interrupt latency is NOT the issue
- Focus on computational or memory access differences

## Reference Files

- `src/main/sensors/gyro.c` - Main file with gyroLuluApplyFn
- `src/main/common/filter.h` - Filter definitions
- `src/main/common/filter.c` - Filter implementations
- `src/main/target/BLUEBERRYF435/target.h` - BLUEBERRY target config
- `src/main/target/JHEMCUF435/target.h` - JHEMCU target config

---
**Manager**
