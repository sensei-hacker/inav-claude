# Project: Implement PMW3901 Optical Flow Driver

**Status:** 🚧 IN PROGRESS
**Priority:** Medium
**Type:** Feature / Driver Implementation
**Created:** 2025-11-26
**Estimated Time:** 2-4 hours

## Overview

Add native PMW3901 optical flow sensor support over SPI to the INAV firmware.

## Problem

INAV currently supports optical flow via:
- CXOF (serial)
- MSP (external processor)
- FAKE (testing)

Users with PMW3901 sensors (a popular SPI-based optical flow sensor) must use an external processor to convert to MSP. Native support would simplify hardware setup and reduce latency.

## Objectives

1. Create PMW3901 SPI driver following existing patterns
2. Integrate with INAV's optical flow subsystem
3. Enable direct SPI connection without external processor
4. Support position hold functionality

## Scope

**In Scope:**
- PMW3901 driver implementation (SPI)
- Sensor detection via Product ID register (0x00 = 0x49)
- Motion burst read for efficient data acquisition
- Settings integration (opflow_hardware)
- Build system integration

**Out of Scope:**
- Other optical flow sensors
- I2C variant support (SPI only for now)
- Configurator UI changes (uses existing opflow settings)

## Implementation Steps

1. Create driver files:
   - `src/main/drivers/opflow/opflow_pmw3901.c`
   - `src/main/drivers/opflow/opflow_pmw3901.h`

2. Update sensor enum in `src/main/sensors/opflow.h`:
   - Add `OPFLOW_PMW3901 = 4`

3. Update settings in `src/main/fc/settings.yaml`:
   - Add "PMW3901" to opflow_hardware table

4. Update detection in `src/main/sensors/opflow.c`:
   - Add PMW3901 case in `opflowDetect()`

5. Update build in `src/main/CMakeLists.txt`:
   - Add new source files

6. Create example target configuration

## Technical Notes

- Uses existing bus abstraction (`drivers/bus.h`) for SPI
- Follows existing `virtualOpflowVTable_t` pattern
- PMW3901 uses motion burst read for efficient data acquisition
- Product ID register (0x00) returns 0x49 for detection

## Success Criteria

- [ ] Driver compiles without errors
- [ ] PMW3901 detected on supported targets
- [ ] Optical flow data read correctly
- [ ] Position hold works with PMW3901 sensor
- [ ] Documentation updated

## Estimated Time

2-4 hours

## Priority Justification

Medium priority - useful feature addition that expands hardware support. Not blocking other work.
