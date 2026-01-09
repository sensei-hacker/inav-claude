# Investigation Complete: gyroLuluApplyFn Performance

**Date:** 2025-12-22 23:30
**From:** Developer
**Type:** Completion Report

## Status: INVESTIGATION COMPLETE

## Summary

Investigated the reported `gyroLuluApplyFn()` performance bottleneck on BLUEBERRYF435WING.

## Key Findings

### LULU Filter Is NOT The Primary Bottleneck

| Configuration | PID Max (µs) | Change |
|--------------|--------------|--------|
| LULU OFF | 435 | baseline |
| LULU ON | 441 | +6µs |

The LULU filter adds only ~6µs when enabled - not a significant factor.

### The System Is Overloaded Regardless

```
PID task:  85.9% max load (435µs at 2kHz)
OSD task:  24.3% max load (971µs!)
Total:    132.1% - exceeding 100%
```

The board is missing task deadlines due to overall overload, not specifically LULU.

### Comparative Testing Needed

To identify why BLUEBERRY differs from JHEMCU:
1. Need to run `tasks` on JHEMCU with identical settings
2. Both use same MCU (AT32F435 @ 288MHz)
3. Both use same cmake/build configuration

## Hypothesis for Board Difference

1. BLUEBERRY has 9 PWM outputs vs JHEMCU's 4
2. OSD task is extremely slow (971µs max)
3. Different default feature configurations

## Deliverables

- Investigation report: `claude/developer/investigations/blueberry-pid/gyroLuluApplyFn-investigation.md`
- Full analysis of LULU algorithm complexity
- Optimization opportunities identified (modulo operations, memory alignment)

## Recommended Next Steps

1. Get comparative `tasks` output from JHEMCU board
2. Investigate high OSD task time (971µs is abnormal)
3. Test with minimal configuration (disable OSD, reduce features)

## Notes

The manufacturer's claim that `gyroLuluApplyFn()` is the bottleneck may be based on different test conditions. With LULU disabled, the function uses `nullFilterApply()` which has negligible overhead.

---
**Developer**
