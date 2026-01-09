# Task Assignment: Optimize Timer Assignments for SPEEDYBEEF7V3

**Date:** 2025-12-03 00:25
**To:** Developer
**From:** Manager
**Project:** New (hardware optimization)
**Priority:** MEDIUM
**Estimated Effort:** 2-4 hours
**Branch:** From maintenance-9.x

---

## Task

Optimize timer assignments for the SPEEDYBEEF7V3 target to ensure at least two of S5-S8 use timers NOT shared with S1-S4, allowing users to run 4 motors (S1-S4) plus 2+ servos (S5-S8) without timer conflicts.

---

## Problem

**Current Configuration:** `inav/src/main/target/SPEEDYBEEF7V3/target.c`

```c
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM2, CH1, PA15,    TIM_USE_OUTPUT_AUTO, 0, 0),  // S1
    DEF_TIM(TIM2, CH2, PB3,     TIM_USE_OUTPUT_AUTO, 0, 0),  // S2
    DEF_TIM(TIM3, CH1, PB4,     TIM_USE_OUTPUT_AUTO, 0, 0),  // S3
    DEF_TIM(TIM4, CH1, PB6,     TIM_USE_OUTPUT_AUTO, 0, 0),  // S4
    DEF_TIM(TIM4, CH2, PB7,     TIM_USE_OUTPUT_AUTO, 0, 0),  // S5  ❌ Shares TIM4 with S4
    DEF_TIM(TIM3, CH2, PB5,     TIM_USE_OUTPUT_AUTO, 0, 0),  // S6  ❌ Shares TIM3 with S3, DSHOT conflict!
    DEF_TIM(TIM3, CH3, PB0,     TIM_USE_OUTPUT_AUTO, 0, 0),  // S7  ❌ Shares TIM3 with S3
    DEF_TIM(TIM3, CH4, PB1,     TIM_USE_OUTPUT_AUTO, 0, 0),  // S8  ❌ Shares TIM3 with S3

    DEF_TIM(TIM8, CH3, PC8,  TIM_USE_LED, 0, 0),    // LED
    DEF_TIM(TIM5, CH1, PA0,  TIM_USE_ANY, 0, 0), // Camera Control
};
```

**Issues:**
- S5 shares TIM4 with S4 (motor)
- S6, S7, S8 ALL share TIM3 with S3 (motor)
- S6 has DSHOT conflict noted in comment
- Users wanting 4 motors + 2 servos will have timer conflicts

**Goal:**
- At least 2 of S5-S8 should use timers NOT used by S1-S4
- Minimize DMA conflicts
- Avoid UART timer conflicts
- Keep LED and Camera Control working

---

## Tools

### DMA Resolver Script

**Location:** `../raytools/dma_resolver/dma_resolver_optimized.js`

This script analyzes:
- Which GPIO pins can use which timers
- DMA stream assignments for each timer/channel
- Conflicts with UARTs and other peripherals
- Optimal timer assignments

**Usage:**
```bash
# Run the script (may need to open in browser or run with node)
cd ../raytools/dma_resolver
# Follow script instructions to input pin assignments
```

---

## Investigation Steps

### Step 1: Document Current State

**Timers used by S1-S4 (motors):**
- TIM2: S1, S2
- TIM3: S3
- TIM4: S4

**Timers used by S5-S8 (servos):**
- TIM4: S5 (CONFLICT with S4)
- TIM3: S6, S7, S8 (CONFLICT with S3)

**Available timers:**
- TIM1: ? (check if available)
- TIM5: Used by Camera Control (PA0)
- TIM8: Used by LED (PC8)
- TIM9-TIM14: ? (check if available on STM32F7)

### Step 2: Find GPIO Pin Capabilities

For each pin S5-S8, determine which timers it can use:

**S5 (PB7):**
- Current: TIM4_CH2
- Alternatives: ? (check STM32F7 datasheet/pinout)

**S6 (PB5):**
- Current: TIM3_CH2
- Alternatives: ? (might support TIM17 or other timers)

**S7 (PB0):**
- Current: TIM3_CH3
- Alternatives: TIM1_CH2N? TIM8_CH2N?

**S8 (PB1):**
- Current: TIM3_CH4
- Alternatives: TIM1_CH3N? TIM8_CH3N?

**Reference:** STM32F722/745/765 datasheet, Table "Alternate function mapping"

### Step 3: Check UART Timer Usage

**UARTs defined in target.h:**
- UART1: PA10/PA9
- UART2: PA3/PA2
- UART3: PB11/PB10
- UART4: PA1
- UART6: PC7/PC6

**Check if any UARTs use timers that we might want to reassign to S5-S8.**

### Step 4: Use DMA Resolver

Run `dma_resolver_optimized.js` with:
- STM32F7xx chip
- All current pin assignments (S1-S8, UARTs, LED, Camera)
- Try different timer assignments for S5-S8

**Goal:** Find assignments where:
- S5-S8 have minimal DMA conflicts
- At least 2 of S5-S8 use timers different from S1-S4
- No UART conflicts
- LED and Camera Control still work

### Step 5: Verify DMA Streams

**STM32F7 DMA stream assignments matter for DSHOT:**
- Each timer/channel maps to specific DMA stream
- Some streams shared between peripherals
- DSHOT requires DMA, so conflicts break DSHOT

**Example conflict (from comment):**
```c
DEF_TIM(TIM3, CH2, PB5, ...) // S6 Clash with S2, DSHOT does not work
```

This suggests S6's DMA stream conflicts with S2's DMA stream.

---

## Solution Approach

### Option A: Use TIM1 or TIM8 for S5-S8

If PB0, PB1, PB5, or PB7 support TIM1 or TIM8 complementary outputs:
- TIM1 and TIM8 are advanced timers (good for PWM)
- Not used by S1-S4
- Check for DMA conflicts

### Option B: Swap S3/S4 Pins

If S3 or S4 pins support different timers:
- Move S3 to different timer
- This frees up TIM3 for S6-S8
- Check if PB4 (S3) or PB6 (S4) have alternate timer functions

### Option C: Use TIM5 More Efficiently

Camera Control uses TIM5_CH1:
- See if S5-S8 pins support TIM5_CH2/CH3/CH4
- Share TIM5 between Camera and servos
- Check DMA conflicts

### Option D: Use TIM9-TIM14 (General Purpose Timers)

STM32F7 has TIM9-TIM14 available:
- Check if S5-S8 pins support these timers
- These are 16-bit general-purpose timers
- May have fewer DMA conflicts

---

## Expected Solution

**Ideal configuration example:**

```c
timerHardware_t timerHardware[] = {
    // Motors (S1-S4) - Keep as is
    DEF_TIM(TIM2, CH1, PA15,    TIM_USE_OUTPUT_AUTO, 0, 0),  // S1
    DEF_TIM(TIM2, CH2, PB3,     TIM_USE_OUTPUT_AUTO, 0, 0),  // S2
    DEF_TIM(TIM3, CH1, PB4,     TIM_USE_OUTPUT_AUTO, 0, 0),  // S3
    DEF_TIM(TIM4, CH1, PB6,     TIM_USE_OUTPUT_AUTO, 0, 0),  // S4

    // Servos (S5-S8) - Optimize these
    DEF_TIM(TIM1, CH2N, PB?, TIM_USE_OUTPUT_AUTO, 0, 0),  // S5 - New timer!
    DEF_TIM(TIM5, CH2, PA?,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S6 - New timer!
    DEF_TIM(TIM8, CH2N, PB?, TIM_USE_OUTPUT_AUTO, 0, 0),  // S7 - New timer!
    DEF_TIM(TIM3, CH4, PB1,  TIM_USE_OUTPUT_AUTO, 0, 0),  // S8 - Keep or change

    DEF_TIM(TIM8, CH3, PC8,  TIM_USE_LED, 0, 0),    // LED
    DEF_TIM(TIM5, CH1, PA0,  TIM_USE_ANY, 0, 0),    // Camera Control
};
```

**Requirements:**
- ✅ At least 2 of S5-S7 use timers NOT in {TIM2, TIM3, TIM4}
- ✅ No DMA conflicts with S1-S4
- ✅ No UART timer conflicts
- ✅ DSHOT works on all channels
- ✅ LED and Camera Control unchanged (unless better solution found)

---

## Implementation

### Step 1: Research

1. Open STM32F722 datasheet (or F745/F765)
2. Find "Alternate Function" table for GPIO pins
3. Document which timers each S5-S8 pin supports
4. Create matrix of possibilities

### Step 2: Use DMA Resolver

1. Input current configuration
2. Try alternative timer assignments
3. Check for DMA conflicts
4. Find optimal solution

### Step 3: Validate Solution

**Check:**
- No DMA stream conflicts (critical for DSHOT)
- Timers not used by UARTs
- At least 2 of S5-S8 on unique timers
- All pins support the assigned timer/channel

### Step 4: Update target.c

Modify `timerHardware[]` array with optimized assignments.

### Step 5: Test Build

```bash
cd inav
make TARGET=SPEEDYBEEF7V3
```

Verify build succeeds.

### Step 6: Document Changes

Create clear documentation:
- Which timers changed
- Why they changed
- DMA conflict resolution
- Testing recommendations

---

## Testing Recommendations

**Once changes are made:**

1. **Build test:** Verify firmware builds successfully
2. **Flash test:** Flash to actual SPEEDYBEEF7V3 hardware (if available)
3. **Motor test:** Configure 4 motors on S1-S4, verify DSHOT works
4. **Servo test:** Configure 2 servos on S5-S6 (or S5-S7), verify PWM works
5. **Mixed test:** 4 motors + 2 servos simultaneously
6. **UART test:** Verify all UARTs still work (GPS, receiver, etc.)
7. **LED test:** Verify WS2811 LED strip still works on PC8

---

## Files to Modify

**Primary:**
- `inav/src/main/target/SPEEDYBEEF7V3/target.c` - Timer assignments

**Possibly:**
- `inav/src/main/target/SPEEDYBEEF7V3/target.h` - If any defines need updating

**Documentation:**
- Add comment explaining timer optimization
- Document which configurations are supported (4 motors + N servos)

---

## Success Criteria

- [ ] Analyzed all S5-S8 pin capabilities (which timers each pin supports)
- [ ] Used DMA resolver to find optimal timer assignments
- [ ] At least 2 of S5-S8 use timers NOT used by S1-S4
- [ ] No DMA conflicts between any outputs
- [ ] No UART timer conflicts
- [ ] DSHOT comment for S6 resolved (if possible)
- [ ] Build successful
- [ ] Changes documented with clear rationale

---

## Priority Justification

**MEDIUM priority because:**
- Hardware optimization (improves usability)
- Affects fixed-wing users (need servos)
- Not urgent (current config works for multirotor)
- Requires careful analysis (DMA conflicts tricky)
- Benefits specific use case (4 motors + servos)

---

## Reference Materials

### STM32F7 Datasheet
- Table: "Alternate function mapping" for GPIO pins
- DMA request mapping
- Timer capabilities

### DMA Resolver Tool
- Location: `../raytools/dma_resolver/dma_resolver_optimized.js`
- Purpose: Analyze DMA conflicts
- Input: Pin assignments, timer assignments
- Output: Conflict warnings, optimal configurations

### Similar Targets
Check other F7 targets for reference:
```bash
grep -r "timerHardware\[" inav/src/main/target/*/target.c | grep "F7"
```

Look for targets with good servo support for ideas.

---

## Constraints

**Must maintain:**
- S1-S4 for motors (current configuration)
- LED strip on PC8 (TIM8_CH3)
- Camera Control on PA0 (TIM5_CH1)
- All UART functionality

**Must avoid:**
- DMA stream conflicts
- Timer conflicts with UARTs
- Breaking DSHOT on S1-S4
- Changing S1-S4 assignments (motors work well as-is)

---

## Expected Deliverables

1. **Analysis document:**
   - Which timers each S5-S8 pin supports
   - DMA stream mappings
   - Conflicts identified
   - Recommended solution

2. **Code changes:**
   - Modified `target.c` with optimized timer assignments
   - Comments explaining changes

3. **Testing results:**
   - Build verification
   - Hardware testing (if available)
   - DMA conflict verification

4. **Documentation:**
   - Commit message explaining optimization
   - Comments in code

---

## Questions?

If you need:
- Access to STM32F7 datasheet
- Help running DMA resolver tool
- Clarification on DMA stream conflicts
- Hardware for testing (SPEEDYBEEF7V3 board)

Let me know!

---

**Manager**
2025-12-03 00:25
