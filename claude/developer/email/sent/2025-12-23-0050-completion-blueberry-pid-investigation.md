# Investigation Complete: BLUEBERRYF435WING PID Performance

**Date:** 2025-12-23 00:50
**From:** Developer
**Type:** Completion Report

## Status: INVESTIGATION COMPLETE

## Summary

Investigated the reported PID performance difference between BLUEBERRYF435WING (435µs) and JHEMCUF435 (254µs) boards. The manufacturer incorrectly attributed the issue to `gyroLuluApplyFn()`.

## Root Cause Identified

**The primary bottleneck is the Dynamic Gyro Notch Filter, not the LULU filter.**

| Configuration | PID Max | PID Avg | Change |
|---------------|---------|---------|--------|
| Original (notch ON) | 435µs | 178µs | baseline |
| Dynamic notch OFF | 320µs | 110µs | **-115µs max, -68µs avg** |
| JHEMCU baseline | 254µs | 94µs | target |

The dynamic gyro notch adds ~110µs per PID cycle due to FFT computation overhead.

## What Was Tested (No Effect)

1. Timer hardware configuration (10 → 5 entries)
2. TIM_USE_OUTPUT_AUTO → TIM_USE_MOTOR
3. MAX_PWM_OUTPUT_PORTS (9 → 4)
4. Barometer disabled (baro_hardware = NONE)

None of these changes improved PID timing.

## Key Findings

1. **LULU filter impact**: Only ~6µs when enabled (NOT the bottleneck)
2. **Dynamic notch impact**: ~110µs overhead (THE bottleneck)
3. **I2C errors**: 320+ errors from barometer, but not causing PID delays
4. **Remaining gap**: 66µs difference even with notch disabled (320µs vs 254µs)

## Recommendations for BLUEBERRY Users

1. Disable dynamic notch: `set dynamic_gyro_notch_enabled = OFF`
2. Use LULU filter instead (minimal overhead)
3. Or use static notch filters tuned to known frequencies

## Documentation Updated

- `claude/developer/investigations/blueberry-pid/settings-comparison.md`
- `claude/developer/investigations/blueberry-pid/gyroLuluApplyFn-investigation.md`

## Firmware Changes

Original target files restored - no permanent changes made to INAV codebase.

## Notes

The 66µs remaining difference between boards (with notch disabled) may warrant further investigation. Possible causes:
- Settings not captured during normalization
- Hardware variation
- Different FFT/filter implementations per board

---
**Developer**
