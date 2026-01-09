# Status Update: Implementing PMW3901 Optical Flow Sensor

**Date:** 2025-11-26
**From:** Developer
**Type:** Status Update

## Summary

Beginning implementation of PMW3901 optical flow sensor support over SPI in the INAV firmware.

## Background

The PMW3901 is a popular SPI-based optical flow sensor used for position hold on drones. INAV currently supports optical flow via:
- CXOF (serial)
- MSP (external processor)
- FAKE (testing)

Adding native PMW3901 support will allow direct SPI connection without an external processor.

## Planned Changes

1. **New driver files:**
   - `src/main/drivers/opflow/opflow_pmw3901.c`
   - `src/main/drivers/opflow/opflow_pmw3901.h`

2. **Update sensor enum:** `src/main/sensors/opflow.h`
   - Add `OPFLOW_PMW3901 = 4`

3. **Update settings:** `src/main/fc/settings.yaml`
   - Add "PMW3901" to opflow_hardware table

4. **Update detection:** `src/main/sensors/opflow.c`
   - Add PMW3901 case in `opflowDetect()`

5. **Update build:** `src/main/CMakeLists.txt`
   - Add new source files

6. **Target configuration example** for boards with PMW3901

## Estimated Effort

2-4 hours for initial implementation and basic testing

## Notes

- Will use existing bus abstraction (`drivers/bus.h`) for SPI
- Will follow existing `virtualOpflowVTable_t` pattern
- PMW3901 uses motion burst read for efficient data acquisition
- Product ID register (0x00) returns 0x49 for detection

---

**Developer**
