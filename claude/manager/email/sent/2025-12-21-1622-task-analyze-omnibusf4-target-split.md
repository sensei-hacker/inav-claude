# Task Assignment: Analyze OMNIBUSF4 Target Structure

**Date:** 2025-12-21 16:22
**Project:** inav (firmware)
**Priority:** Medium
**Estimated Effort:** 3-4 hours

## Task

Analyze the `src/main/target/OMNIBUSF4/` directory which contains 9 targets mixed together with conditional defines. Determine the best refactoring approach.

## Current Situation

The OMNIBUSF4 target directory contains 9 different targets in one directory:

1. **DYSF4PRO**
2. **DYSF4PROV2**
3. **OMNIBUSF4**
4. **OMNIBUSF4PRO**
5. **OMNIBUSF4V3_S5_S6_2SS**
6. **OMNIBUSF4V3_S5S6_SS**
7. **OMNIBUSF4V3_S6_SS**
8. **OMNIBUSF4V3**
9. **OMNIBUSF4V3_ICM**

These are managed through extensive `#ifdef` conditionals in `target.h` (290 lines).

## Two Questions to Answer

### Question 1: Logical Split

**Is there a logical split to create 2-3 separate target directories instead of one mega-directory?**

Analyze the conditional compilation patterns and identify natural groupings. Consider:
- Hardware differences (SD card vs flash, barometer types, IMU types)
- Pin mapping differences
- I2C bus differences (DYSF4PROV2 uses I2C1, others use I2C2)

**Potential groupings to evaluate:**
- **Group A:** DYSF4PRO + DYSF4PROV2 (DYS variants)
- **Group B:** OMNIBUSF4 + OMNIBUSF4PRO (original Omnibus with flash)
- **Group C:** OMNIBUSF4V3 + variants (V3 series with SD card)

### Question 2: Softserial Without Conditional Compilation

**Can the softserial variants work without separate builds?**

Currently there are 4 softserial-related targets for OMNIBUSF4V3:
- `OMNIBUSF4V3` - softserial on PC6 (UART6 TX shared)
- `OMNIBUSF4V3_S6_SS` - softserial on PA8 (S6 motor output)
- `OMNIBUSF4V3_S5S6_SS` - softserial RX on PA1 (S5), TX on PA8 (S6)
- `OMNIBUSF4V3_S5_S6_2SS` - two softserials on PA1 (S5) and PA8 (S6)

**Key insight:** PA1 and PA8 are motor outputs S5 and S6.

**Analyze whether:**
- A single `OMNIBUSF4V3` build could support softserial on S5/S6 at runtime
- The firmware already prevents motor output when a pin is used for serial
- Users could configure softserial without needing separate builds
- Any technical barriers prevent runtime pin sharing (DMA conflicts, timer conflicts, etc.)

## What to Do

1. **Read the target files:**
   - `src/main/target/OMNIBUSF4/target.h`
   - `src/main/target/OMNIBUSF4/target.c`
   - `src/main/target/OMNIBUSF4/CMakeLists.txt`

2. **Map the differences:**
   - Create a comparison table of hardware differences
   - Identify which conditionals are hardware-related vs configuration-related
   - Document pin conflicts between motor outputs and softserial

3. **Research softserial implementation:**
   - Check `src/main/io/serial.c` for pin conflict handling
   - Check `src/main/drivers/serial_softserial.c`
   - Check `src/main/drivers/pwm_output.c` for motor pin exclusion
   - Determine if runtime pin sharing already works

4. **Make recommendations:**
   - **For Question 1:** Recommend 2-3 logical target directories with rationale
   - **For Question 2:** Determine if softserial variants can be eliminated
   - Estimate effort for each refactoring approach

## Success Criteria

- [ ] Comparison table of all 9 targets showing key differences
- [ ] Identified natural groupings for 2-3 target directories
- [ ] Analyzed softserial pin sharing mechanism
- [ ] Determined if runtime softserial configuration is feasible
- [ ] Clear recommendation with effort estimates
- [ ] Sent completion report with findings

## Important Notes

- **Don't implement anything yet** - this is analysis only
- Focus on architecture and feasibility
- Consider backward compatibility (can we preserve target names?)
- Consider maintenance burden (is splitting worth it?)

## Why This Matters

The OMNIBUSF4 directory is a maintenance burden:
- 290 lines of conditional compilation
- 9 targets in one directory
- 4 targets differ ONLY by softserial pin configuration
- Confusing for users and developers

Cleaner structure would:
- Reduce conditional compilation complexity
- Make each target easier to understand
- Potentially reduce the number of builds
- Improve maintainability

---
**Manager**
