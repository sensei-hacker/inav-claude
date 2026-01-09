# Project: Fix SPI busWriteBuf Register Masking

**Status:** 📋 TODO
**Priority:** Medium
**Type:** Bug Fix
**Created:** 2026-01-08
**GitHub Issue:** #10674

## Overview

Fix incorrect register address masking in `busWriteBuf()` for SPI devices. The function sets the MSB (read mode) instead of clearing it (write mode).

## Problem

For SPI communication, the MSB of the register address indicates read/write:
- **Read:** Set MSB (`reg | 0x80`)
- **Write:** Clear MSB (`reg & 0x7F`)

The `busWrite()` function correctly uses `reg & 0x7F` for writes, but `busWriteBuf()` incorrectly uses `reg | 0x80`.

**Current (wrong):**
```c
// src/main/drivers/bus.c line 286
return spiBusWriteBuffer(dev, reg | 0x80, data, length);  // WRONG - sets read bit
```

**Correct version in busWrite():**
```c
// src/main/drivers/bus.c line 318
return spiBusWriteRegister(dev, reg & 0x7F, data);  // CORRECT - clears read bit
```

## Solution

Change line 286 from:
```c
return spiBusWriteBuffer(dev, reg | 0x80, data, length);
```
to:
```c
return spiBusWriteBuffer(dev, reg & 0x7F, data, length);
```

## Files to Modify

- `src/main/drivers/bus.c` line 286

## Testing

1. Build for a target that uses SPI sensors
2. Verify SPI devices still initialize and communicate correctly
3. If hardware available, test with SPI-based sensor (gyro, baro, etc.)

## Success Criteria

- [ ] `busWriteBuf()` uses `reg & 0x7F` instead of `reg | 0x80`
- [ ] Build passes for all targets
- [ ] SPI devices continue to function (if testable)

## Notes

- Bug has existed since at least INAV 3.0.0
- Reporter shows side-by-side comparison with correct `busWrite()` function
- One-line fix
- May explain mysterious SPI device issues users have reported
