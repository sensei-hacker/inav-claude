# Task Status: SPEEDYBEEF7V3 Timer Optimization Analysis

**Date:** 2025-12-04 23:10
**To:** Manager
**From:** Developer
**Task:** optimize-speedybeef7v3-timers
**Status:** ANALYSIS COMPLETE - GOAL UNACHIEVABLE

---

## Summary

Completed comprehensive analysis of SPEEDYBEEF7V3 timer assignments. **The optimization goal is physically impossible** with the current pin assignments. No code changes made - current configuration is optimal given hardware constraints.

---

## Analysis Performed

### 1. Pin Timer Capabilities Research

Analyzed STM32F745 datasheet for all S1-S8 pin alternate functions:

| Output | Pin  | Available Timers |
|--------|------|------------------|
| S1 | PA15 | TIM2_CH1 only |
| S2 | PB3  | TIM2_CH2 only |
| S3 | PB4  | TIM3_CH1 only |
| S4 | PB6  | TIM4_CH1 only |
| S5 | PB7  | TIM4_CH2 only |
| S6 | PB5  | TIM3_CH2 only |
| S7 | PB0  | TIM1_CH2N, TIM3_CH3, TIM8_CH2N |
| S8 | PB1  | TIM1_CH3N, TIM3_CH4, TIM8_CH3N |

**Finding:** S1-S6 have ZERO alternatives. Only S7 and S8 have options.

### 2. DMA Mapping Analysis

Used DMA resolver tool (`~/Documents/planes/raytools/dma_resolver/`) to check DMA support:

**Current Configuration DMA Analysis:**
- ✅ No DMA stream conflicts detected
- ⚠️ Timer sharing exists (by design, unavoidable)

**Complementary Output DMA Test:**
```
TIM1_CH2N: NO DMA MAPPING
TIM1_CH3N: NO DMA MAPPING
TIM8_CH2N: NO DMA MAPPING
TIM8_CH3N: NO DMA MAPPING
```

**Critical Finding:** Complementary timer outputs (CHxN) do NOT have DMA support, therefore **cannot support DSHOT** (motors require DMA for DSHOT).

### 3. Current vs. Desired Configuration

**Current Configuration:**
```c
DEF_TIM(TIM2, CH1, PA15, TIM_USE_OUTPUT_AUTO, 0, 0),  // S1
DEF_TIM(TIM2, CH2, PB3,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S2
DEF_TIM(TIM3, CH1, PB4,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S3
DEF_TIM(TIM4, CH1, PB6,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S4
DEF_TIM(TIM4, CH2, PB7,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S5 (shares TIM4 with S4)
DEF_TIM(TIM3, CH2, PB5,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S6 (shares TIM3 with S3)
DEF_TIM(TIM3, CH3, PB0,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S7 (shares TIM3 with S3)
DEF_TIM(TIM3, CH4, PB1,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S8 (shares TIM3 with S3)
```

**Timer Usage:**
- TIM2: S1, S2
- TIM3: S3, S6, S7, S8 (heavily shared)
- TIM4: S4, S5

**All 8 outputs support DSHOT** ✅

---

## Why Goal Is Unachievable

**Original Goal:** At least 2 of S5-S8 should use timers NOT shared with S1-S4, while ALL outputs support DSHOT/motors.

**Constraint Analysis:**

1. **S5 (PB7) - LOCKED**
   - Only supports TIM4_CH2
   - Must share TIM4 with S4 (motor)
   - No alternatives exist

2. **S6 (PB5) - LOCKED**
   - Only supports TIM3_CH2
   - Must share TIM3 with S3 (motor)
   - No alternatives exist

3. **S7 (PB0) - Limited Options**
   - TIM3_CH3: Shares with S3 (current config)
   - TIM1_CH2N: No DMA → servo-only, no DSHOT
   - TIM8_CH2N: No DMA → servo-only, no DSHOT

4. **S8 (PB1) - Limited Options**
   - TIM3_CH4: Shares with S3 (current config)
   - TIM1_CH3N: No DMA → servo-only, no DSHOT
   - TIM8_CH3N: No DMA → servo-only, no DSHOT

**Conclusion:** To get S7/S8 on different timers (TIM1/TIM8), we must use complementary outputs which lack DMA support, making them servo-only and unable to run motors with DSHOT.

---

## Options Evaluated

### Option A: Keep Current Configuration ✅ RECOMMENDED
- **Pros:**
  - All 8 outputs support DSHOT/motors
  - No DMA conflicts
  - Build verified successful
- **Cons:**
  - Timer sharing exists (S3 shares TIM3 with S6/S7/S8, S4 shares TIM4 with S5)
  - Users running 4 motors + servos will have timer conflicts

### Option B: Use TIM1 Complementary for S7/S8 ❌ REJECTED
```c
DEF_TIM(TIM1, CH2N, PB0, TIM_USE_OUTPUT_AUTO, 0, 1),  // S7
DEF_TIM(TIM1, CH3N, PB1, TIM_USE_OUTPUT_AUTO, 0, 0),  // S8
```
- **Pros:**
  - S7/S8 on TIM1 (independent from motors)
  - Reduces timer conflicts for 4 motors + 2 servos use case
- **Cons:**
  - S7/S8 become servo-only (no DSHOT support)
  - Not all outputs can be motors

**Decision:** Rejected per user requirement that all outputs must support motors.

---

## Reference: Other Targets

Checked other INAV targets using complementary outputs:
- **ANYFCM7**: Uses TIM1_CH2N (PB0) and TIM1_CH3N (PB1) - same pins!
- **ALIENFLIGHTNGF7**: Uses TIM8_CH2N and TIM1_CH3N
- **AIKONF7**: Uses TIM1_CH3N

These targets use complementary outputs for **servo-only outputs**, not motors requiring DSHOT.

---

## Files Analyzed

**Code:**
- `inav/src/main/target/SPEEDYBEEF7V3/target.c` (timer definitions)
- `inav/F745_alt_functions.txt` (STM32F745 pinout reference)

**Tools Used:**
- `~/Documents/planes/raytools/dma_resolver/dma_resolver_optimized.js`
- Created `analyze_speedybeef7v3.js` for configuration analysis
- Created `test_complementary_dma.js` to verify DMA support

---

## Build Verification

```bash
cd inav/build
cmake ..
make SPEEDYBEEF7V3
```

**Result:** ✅ Build successful, no errors or warnings

---

## Recommendations

1. **Keep current timer configuration** - No code changes needed
2. **Document limitation** - Update target documentation to note timer sharing
3. **Hardware consideration** - Future board revisions could use different pins for S5-S8 that support alternative timers

### For Users

**Current supported configurations:**
- ✅ 4 motors (S1-S4) with DSHOT
- ✅ 8 motors with DSHOT (if used as octocopter)
- ⚠️ 4 motors + 4 servos (S5-S8): Timer conflicts exist but functionally works
  - S5 shares TIM4 with motor S4
  - S6-S8 share TIM3 with motor S3
  - DSHOT may have conflicts on shared timers

---

## Conclusion

The SPEEDYBEEF7V3 hardware pin assignments make the optimization goal unachievable while maintaining DSHOT support on all outputs. The current configuration is already optimal given these constraints.

**No code changes recommended.**

Released lock: `claude/locks/inav.lock`

---

**Developer**
2025-12-04 23:10
