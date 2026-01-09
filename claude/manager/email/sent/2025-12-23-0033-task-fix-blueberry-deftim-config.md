# Task Assignment: Fix BLUEBERRYF435 Configuration (DMA + Disable Dynamic Notch)

**Date:** 2025-12-23 00:33
**Project:** inav (firmware) - BLUEBERRY435 configuration
**Priority:** Medium-High
**Estimated Effort:** 1-2 hours

## Task

Two configuration fixes for BLUEBERRYF435 target to address performance issues:

1. **Disable dynamic gyro notch filter by default** - Performance optimization for wing aircraft
2. **Fix DEF_TIM DMA configuration** - Correct incorrect sequential DMA option parameters

**Targets:**
- `src/main/target/BLUEBERRYF435/config.c` (dynamic notch)
- `src/main/target/BLUEBERRYF435/target.c` (DMA configuration)

## Background

**Context:** These issues were discovered during the BLUEBERRY435 PID performance investigation. The board is currently overloaded at 132.1% task load.

**Problem 1 - Performance Overhead:**
The dynamic gyro notch filter adds computational overhead that this performance-constrained board cannot afford. Wing aircraft typically don't need dynamic notch filtering (designed for multirotor motor noise).

**Problem 2 - Incorrect DMA Configuration:**
The last parameter in DEF_TIM() defines the DMA option/alternate configuration. This should almost always be "0" (default DMA mapping) unless there's a specific DMA conflict that requires using an alternate DMA channel.

**Current (INCORRECT) Pattern:**
```c
DEF_TIM(TIM1, CH1, PA8,  TIM_USE_OUTPUT_AUTO, 0, 0);
DEF_TIM(TIM1, CH2, PA9,  TIM_USE_OUTPUT_AUTO, 0, 1);  // ❌ Wrong: sequential
DEF_TIM(TIM1, CH3, PA10, TIM_USE_OUTPUT_AUTO, 0, 2);  // ❌ Wrong: sequential
DEF_TIM(TIM8, CH1, PC6,  TIM_USE_OUTPUT_AUTO, 0, 3);  // ❌ Wrong: sequential
```

**Correct Pattern:**
```c
DEF_TIM(TIM1, CH1, PA8,  TIM_USE_OUTPUT_AUTO, 0, 0);  // ✓ Default DMA
DEF_TIM(TIM1, CH2, PA9,  TIM_USE_OUTPUT_AUTO, 0, 0);  // ✓ Default DMA
DEF_TIM(TIM1, CH3, PA10, TIM_USE_OUTPUT_AUTO, 0, 0);  // ✓ Default DMA
DEF_TIM(TIM8, CH1, PC6,  TIM_USE_OUTPUT_AUTO, 0, 0);  // ✓ Default DMA
```

**Exception (when alternate DMA is needed):**
```c
DEF_TIM(TIM3, CH1, PB4, TIM_USE_OUTPUT_AUTO, 0, 0);  // Default DMA
DEF_TIM(TIM3, CH2, PB5, TIM_USE_OUTPUT_AUTO, 0, 1);  // ✓ Alternate needed due to conflict
```

## What to Do

### Step 1: Review Current Configuration

1. Open `src/main/target/BLUEBERRYF435/target.c`
2. Find all DEF_TIM() definitions
3. Identify which ones have non-zero last parameter

### Step 2: Disable Dynamic Gyro Notch Filter by Default

**Additional requirement:** Turn off the dynamic gyro notch filter by default on this target.

**Reason:**
- Performance overhead (board already at 132% task load)
- Filter probably isn't needed for a wing board
- Will reduce CPU load and improve task scheduling

**Implementation:**
In `src/main/target/BLUEBERRYF435/config.c`, add default configuration to disable dynamic notch:

```c
// Disable dynamic notch filter by default (performance optimization for wing)
gyroConfigMutable()->dynamicGyroNotchEnabled = false;
```

Or add to target.h if there's a compile-time define for this.

Check how other wing targets configure this setting.

### Step 3: Analyze DMA Requirements

**Check for actual DMA conflicts:**
- Review the STM32F435 datasheet/reference manual for DMA mappings
- Check if any timers genuinely share DMA channels that would conflict
- Look at similar targets (JHEMCUF435, other F4 boards) for reference

**Most likely:**
- All or most should be "0" (default DMA)
- Only use alternate DMA if there's a documented conflict

### Step 4: Fix the DMA Configuration

1. Change sequential numbers (1, 2, 3...) to "0" where appropriate
2. Only keep non-zero values if there's a genuine DMA conflict
3. Add comments explaining any non-zero values

### Step 5: Test the Fix

**Build test:**
```bash
# Build the target to verify no compile errors
make TARGET=BLUEBERRYF435
```

**Hardware test (if available):**
- Flash to BLUEBERRY435 board
- Test motor outputs
- Verify all PWM channels work correctly
- Check for DMA errors in debug output

**If no hardware available:**
- Document that hardware testing is needed
- Note in PR that maintainers should verify on real hardware

## Why This Matters

**Potential Issues from Incorrect DMA Configuration:**

1. **Performance Impact:**
   - Incorrect DMA assignment could cause contention
   - May contribute to the performance issues being investigated
   - Could slow down timer interrupts

2. **Resource Conflicts:**
   - Multiple peripherals trying to use same DMA channel
   - DMA transfer failures
   - Unpredictable behavior

3. **Best Practices:**
   - INAV convention is to use default DMA (0) unless needed
   - Makes configuration clearer and more maintainable

**Benefits from Disabling Dynamic Notch:**

1. **Reduced CPU Load:**
   - Board currently at 132.1% task load (overloaded)
   - Dynamic notch adds computational overhead
   - Every CPU cycle counts on this target

2. **Unnecessary for Fixed-Wing:**
   - Dynamic notch designed for multirotors with motor noise
   - Wing aircraft have different vibration profiles
   - Static filtering usually sufficient for wings

3. **Improved Performance:**
   - Better task scheduling margin
   - Reduced risk of missed deadlines
   - More headroom for other features

## Success Criteria

- [ ] Disabled dynamic gyro notch filter by default in target config
- [ ] Reviewed all DEF_TIM definitions in BLUEBERRYF435 target.c
- [ ] Identified DMA option parameters that are incorrect
- [ ] Changed sequential numbers to "0" where appropriate
- [ ] Verified no genuine DMA conflicts require alternate mappings
- [ ] Built target successfully
- [ ] Documented any non-zero DMA options with comments
- [ ] Tested on hardware (if available) or documented testing needed

## Deliverables

1. **Fixed config.c** with dynamic notch disabled by default
2. **Fixed target.c** with correct DMA configurations
3. **Brief report** including:
   - Dynamic notch configuration change
   - DMA configuration issues found and fixed
   - Justification for any non-zero DMA options
   - Expected performance improvement
   - Test results (build test minimum)
4. **Commit** ready for PR or inclusion in performance investigation PR

## Reference

**Understanding Alternate DMA Parameter:**
- `../raytools/dma_resolver/` - Tool for understanding DMA mappings and conflicts

**Similar Targets to Check:**
- `src/main/target/JHEMCUF435/target.c`
- Other F4-based targets with similar peripherals

**Documentation:**
- STM32F435 Reference Manual - DMA section
- INAV timer/DMA documentation in codebase

## Notes

- This is related to the BLUEBERRY435 PID performance investigation
- Could be a contributing factor to performance issues
- Should be fixed regardless of whether it affects performance
- Keep this separate from or combine with performance investigation PR as appropriate

---
**Manager**
