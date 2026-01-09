# Investigate DMA Usage and Cleanup Opportunities

**Status:** 📝 PLANNED
**Type:** Research / Analysis / Documentation
**Priority:** Medium
**Created:** 2025-11-24
**Branch:** N/A (documentation project)

## Problem

It has been suggested that INAV's DMA usage needs "cleanup" - that certain peripherals may overuse DMA channels or create DMA resource contention. Betaflight reportedly completed an extensive DMA cleanup that improved resource availability and reduced conflicts.

Currently, INAV's DMA allocation and usage patterns across F4, F7, and H7 platforms have not been systematically documented or analyzed for optimization opportunities.

## Objective

**Phase 1 (Primary):** Document current DMA usage patterns across INAV firmware
**Phase 2 (Secondary):** Identify areas for potential improvement if noticed during analysis

## Scope

### Platforms
- **Primary Focus:** F7 and H7 microcontrollers
- **Secondary:** F4 issues that don't apply to F7/H7 should be noted separately
- **Out of Scope:** AT32F43x (unless similar patterns apply)

### Analysis Areas

1. **DMA Architecture Overview**
   - Document INAV's DMA abstraction layer
   - Platform-specific implementations (F4/F7/H7)
   - DMA tag system and resource ownership

2. **Peripheral DMA Usage**
   - UART (serial communication)
   - SPI (gyro, OSD MAX7456, SD card)
   - Timers (motor outputs, LED strips)
   - ADC (battery monitoring, current sensing)
   - SDIO/SDMMC (SD card on H7)

3. **DMA Channel Assignments**
   - Review target-specific DMA configurations
   - Identify patterns across board definitions
   - Document conflicts or resource constraints

4. **Comparison with Betaflight**
   - Research Betaflight's DMA cleanup changes
   - Identify techniques or patterns INAV could adopt
   - Note differences in approach or requirements

## Known DMA-Related Code

### Core DMA Infrastructure
- `src/main/drivers/dma.h` - DMA abstraction layer
- `src/main/drivers/dma_stm32f4xx.c` - F4 implementation
- `src/main/drivers/dma_stm32f7xx.c` - F7 implementation
- `src/main/drivers/dma_stm32h7xx.c` - H7 implementation
- `src/main/drivers/dma_at32f43x.c` - AT32 implementation
- `src/main/drivers/dma_cli.h` - DMA CLI interface
- `src/main/drivers/dma_cli_stm32_impl.c` - CLI implementation

### Peripheral Drivers Using DMA
- `src/main/drivers/serial_uart*.c` - UART DMA
- `src/main/drivers/bus_spi*.c` - SPI DMA
- `src/main/drivers/max7456.c` - OSD MAX7456 SPI
- `src/main/drivers/sdcard/sdmmc_sdio*.c` - SD card DMA
- `src/main/drivers/light_ws2811strip.c` - LED strip timers
- `src/main/drivers/pwm_output.c` - Motor output timers
- `src/main/drivers/timer*.c` - Timer DMA
- `src/main/sensors/gyro.c` - Gyro SPI DMA

### Target Configurations
- `src/main/target/*/target.h` - Board-specific DMA assignments
- Common boards to review:
  - MATEKF405/MATEKF722 (popular F4/F7)
  - H7 boards (DAKEFPVH743, TBS_LUCID_H7, etc.)
  - Check 10-15 representative targets

## Deliverables

### Primary Deliverable: DMA Usage Documentation

Create comprehensive markdown document: `inav/docs/development/DMA-USAGE.md`

**Required Sections:**

1. **DMA Architecture Overview**
   - Resource abstraction (dmaTag_t, DMA_t)
   - Platform differences (F4 vs F7 vs H7)
   - Ownership and initialization

2. **DMA Channel Inventory**
   - Table of DMA controllers and streams/channels per platform
   - F4: 2 controllers × 8 streams each
   - F7: 2 controllers × 8 streams each
   - H7: 2 controllers × 8 streams each (BDMA differences)

3. **Peripheral DMA Mappings**
   - Which peripherals use DMA
   - Typical channel assignments
   - Conflicts and constraints

4. **Target-Specific Configurations**
   - Examples from popular boards
   - Common DMA assignment patterns
   - Known issues or limitations

5. **Areas for Potential Improvement** (if identified)
   - Overuse or unnecessary DMA allocations
   - Resource conflicts
   - Comparison with Betaflight approach

### Secondary Deliverables

- **Research Notes:** `claude/projects/investigate-dma-usage-cleanup/research-notes.md`
  - Betaflight cleanup investigation
  - Code analysis findings
  - Questions or uncertainties

- **Issue List:** If problems are found, create list of potential cleanup tasks

## Research Questions

1. What did Betaflight's DMA cleanup accomplish?
   - Which commits/PRs implemented the changes?
   - What specific issues were addressed?
   - What techniques were used?

2. How does INAV currently allocate DMA channels?
   - Compile-time vs runtime allocation?
   - Hardcoded vs configurable?
   - Platform-specific strategies?

3. Are there common DMA conflicts across boards?
   - UART vs SPI contention?
   - Timer conflicts with serial?
   - SD card vs other peripherals?

4. Which peripherals *must* use DMA vs could use polling?
   - Critical: Gyro SPI (high-frequency sampling)
   - Important: UART (telemetry, GPS, RC)
   - Optional: ?

5. Are there unused or wasted DMA allocations?
   - Peripherals that claim DMA but don't use it?
   - Conservative allocations that could be freed?

## Success Criteria

- [ ] Comprehensive DMA usage documentation created
- [ ] All major peripherals' DMA usage patterns documented
- [ ] F7 and H7 platforms fully analyzed
- [ ] F4 differences noted (where applicable)
- [ ] Betaflight cleanup research completed
- [ ] Potential improvements identified (if any exist)
- [ ] Documentation suitable for future developers

## Estimated Time

**Phase 1 (Documentation):** 8-12 hours
- Betaflight research: 2-3 hours
- Code analysis: 4-6 hours
- Documentation writing: 2-3 hours

**Phase 2 (Improvement identification):** Ongoing during Phase 1
- No additional time allocation (opportunistic)

**Total:** ~8-12 hours

## Notes

- This is primarily a documentation and research project
- No code changes required in Phase 1
- Focus on understanding current state before proposing changes
- If significant issues are found, create separate project for cleanup implementation
- Documentation should be accessible to new INAV developers

## Related Work

- DFU protocol work touched peripheral initialization
- Future projects may depend on understanding DMA resource availability
- May inform board support decisions (which features can coexist on resource-constrained boards)
