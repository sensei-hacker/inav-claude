# Task Completion: Fix BLUEBERRYF435WING Configuration

**Date:** 2025-12-23 08:47
**From:** Developer
**Task:** fix-blueberry-deftim-config

## Status: COMPLETE

## Summary

Investigated and implemented the dynamic notch filter fix for BLUEBERRYF435WING. The DMA configuration was analyzed and found to be **already correct** for AT32F43x targets.

## Changes Made

### Dynamic Notch Filter Disabled by Default

**File:** `src/main/target/BLUEBERRYF435WING/config.c`

- Added `#include "sensors/gyro.h"`
- Added code to disable dynamic gyro notch filter by default:
```c
#ifdef USE_DYNAMIC_FILTERS
    gyroConfigMutable()->dynamicGyroNotchEnabled = 0;
#endif
```

**Rationale:**
- Board is performance-constrained (was at 132% task load)
- Dynamic notch designed for multirotor motor noise detection
- Wing aircraft have different vibration profiles; static filtering usually sufficient
- Reduces CPU load and improves task scheduling margin

### DMA Configuration Analysis - NO CHANGES NEEDED

The DMA configuration in `target.c` is **correct** for AT32F43x targets:
- AT32F43x has DMAMUX allowing arbitrary DMA stream assignment
- The sequential numbering (0,1,2,3,4,5,6,8,9,10) is intentional
- DMA option 7 is skipped to avoid conflict with ADC1 (DMA2_CHANNEL1)

## Commit

- **Branch:** `fix-blueberry-disable-dynamic-notch`
- **Commit:** `b7bfdeed54`

## Pull Request

- **PR:** #11199
- **URL:** https://github.com/iNavFlight/inav/pull/11199
- **Target:** `iNavFlight/inav` → `maintenance-9.x`

## Build Verification

Both target variants built successfully:
- BLUEBERRYF435WING - OK (FLASH1: 62.07%, RAM: 83.93%)
- BLUEBERRYF435WING_SD - OK

## Qodo Review

Qodo bot suggested using `false` instead of `0` and guarding the include. Analysis shows the current code follows existing INAV conventions (`ez_tune.c` uses `= 1`/`= 0`). No changes needed.

---
**Developer**
