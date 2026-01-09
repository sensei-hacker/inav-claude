# Task Assignment: Investigate DMA Usage and Cleanup Opportunities

**Date:** 2025-11-24 20:20
**Project:** investigate-dma-usage-cleanup
**Priority:** Medium
**Estimated Effort:** 8-12 hours
**Type:** Research / Documentation
**Branch:** N/A (documentation project)

## Task

Analyze INAV firmware DMA usage and create comprehensive documentation. Identify potential cleanup opportunities similar to Betaflight's DMA optimization work.

## Background

INAV's DMA usage has been questioned - suggestions that certain peripherals may overuse DMA or create resource contention. Betaflight completed extensive DMA cleanup. We need to:

1. Document current INAV DMA usage patterns
2. Understand what Betaflight did
3. Identify improvement opportunities

## Scope

### Platforms (Priority Order)
1. **F7** (primary focus)
2. **H7** (primary focus)
3. **F4** (note issues that don't apply to F7/H7)

### Analysis Areas
- DMA architecture and abstraction layer
- Peripheral DMA usage (UART, SPI, timers, SD card, ADC)
- Target board configurations
- Resource allocation patterns
- Comparison with Betaflight

## Key Files to Review

**DMA Core:**
- `src/main/drivers/dma.h` - Abstraction layer
- `src/main/drivers/dma_stm32f4xx.c`
- `src/main/drivers/dma_stm32f7xx.c`
- `src/main/drivers/dma_stm32h7xx.c`
- `src/main/drivers/dma_cli*.c` - CLI interface

**Peripheral Drivers:**
- `src/main/drivers/serial_uart*.c` - UART DMA
- `src/main/drivers/bus_spi*.c` - SPI DMA
- `src/main/drivers/max7456.c` - OSD SPI
- `src/main/drivers/sdcard/sdmmc_sdio*.c` - SD card
- `src/main/drivers/pwm_output.c` - Motor timers
- `src/main/drivers/light_ws2811strip.c` - LED strips
- `src/main/sensors/gyro.c` - Gyro SPI

**Target Configs:**
- `src/main/target/*/target.h` (sample 10-15 popular boards)

## Deliverables

### Primary: DMA Usage Documentation

Create `inav/docs/development/DMA-USAGE.md` with:

1. **DMA Architecture Overview**
   - Resource abstraction (tags, descriptors, ownership)
   - Platform differences (F4/F7/H7)

2. **DMA Channel Inventory**
   - Controllers and streams per platform
   - Resource tables

3. **Peripheral DMA Mappings**
   - Which peripherals use DMA
   - Typical channel assignments
   - Conflicts and constraints

4. **Target-Specific Configurations**
   - Examples from popular boards
   - Common patterns
   - Known limitations

5. **Areas for Potential Improvement** (if found)
   - Overuse or unnecessary allocations
   - Resource conflicts
   - Betaflight comparison

### Secondary: Research Notes

Create `claude/projects/investigate-dma-usage-cleanup/research-notes.md`:
- Betaflight cleanup investigation
- Code analysis findings
- Questions/uncertainties

## Research Questions

1. **Betaflight:** What did their DMA cleanup accomplish?
   - Which commits/PRs?
   - What problems were solved?
   - Techniques used?

2. **INAV Allocation:** How are DMA channels allocated?
   - Compile-time vs runtime?
   - Hardcoded vs configurable?

3. **Conflicts:** Common DMA conflicts across boards?
   - UART vs SPI contention?
   - Timer conflicts?
   - SD card vs other peripherals?

4. **Requirements:** Which peripherals *must* use DMA?
   - Critical: Gyro (high-frequency)
   - Important: UART (telemetry, GPS, RC)
   - Optional: ?

5. **Waste:** Unused or wasted DMA allocations?
   - Peripherals claiming but not using DMA?
   - Conservative allocations that could be freed?

## Approach

**Phase 1:** Research Betaflight's DMA cleanup (2-3 hours)
- Search GitHub for DMA-related PRs/commits
- Document approach and findings

**Phase 2:** Analyze INAV DMA architecture (2-3 hours)
- Review core DMA abstraction layer
- Document platform implementations

**Phase 3:** Map peripheral DMA usage (3-4 hours)
- Analyze each peripheral type
- Document DMA vs polling strategies

**Phase 4:** Review target configurations (1-2 hours)
- Sample 10-15 representative boards
- Identify patterns and conflicts

**Phase 5:** Document findings (2-3 hours)
- Write comprehensive documentation
- Identify improvement opportunities

**Total:** 8-12 hours

## Success Criteria

- [ ] Comprehensive DMA documentation created
- [ ] All major peripherals analyzed
- [ ] F7/H7 platforms fully covered
- [ ] Betaflight research complete
- [ ] Improvement areas identified (if any)
- [ ] Documentation clear for new developers

## Notes

- **Primary goal:** Document current state
- **Secondary goal:** Identify improvements opportunistically
- No code changes required in this phase
- If major issues found, create follow-up project for implementation
- Focus on F7/H7 - note F4 issues separately only if they differ

## Completion

Send completion report to `claude/manager/inbox/` with:
- Summary of findings
- Link to documentation created
- List of improvement opportunities (if any)
- Suggested follow-up projects (if needed)

---

**Manager**
