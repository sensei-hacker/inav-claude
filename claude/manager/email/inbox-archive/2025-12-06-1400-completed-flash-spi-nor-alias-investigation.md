# Task Completed: Flash SPI NOR Alias Investigation

**Date:** 2025-12-06 14:00
**Status:** COMPLETED - NO ACTION NEEDED

## Summary

Investigated the flash SPI NOR alias work and JEDEC ID support. The original concern was about W25Q128 support, but investigation revealed that W25Q128 is already fully supported with two JEDEC ID variants. The actual chip requiring support is PY25Q128 (Puya), which is being handled as a separate task.

## Investigation Results

### Branch Reviewed
- **Branch:** `add-flash-spi-nor-alias`
- **Commit:** `6c2149702f` - Add USE_FLASH_SPI_NOR alias for USE_FLASH_M25P16
- **File changed:** `src/main/target/common_post.h`

### What the Alias Does
The alias provides a more descriptive name (`USE_FLASH_SPI_NOR`) for the M25P16 driver, which actually supports a wide range of SPI NOR flash chips beyond the original M25P16:
- Winbond W25Q series (W25Q80 through W25Q256)
- Winbond W25X series
- Macronix MX25L series
- Micron N25Q series
- Cypress S25FL series
- And other compatible chips

### W25Q128 JEDEC ID Analysis
The W25Q128 chip is **already fully supported** with two JEDEC ID variants:
- `0xEF4018` - W25Q128 (16MB, 256 sectors) - lines 93-95 in flash_m25p16.c
- `0xEF7018` - W25Q128_DTR (16MB, 256 sectors) - lines 99-101 in flash_m25p16.c

### Current JEDEC ID Table Coverage
The driver currently supports 22 different flash chip variants from multiple manufacturers:
- **Macronix:** 3 chips (MX25L series)
- **Micron:** 3 chips (M25P, N25Q series)
- **Winbond W25Q:** 8 chips (W25Q80, W25Q16, W25Q32, W25Q64, W25Q128, W25Q256)
- **Winbond W25X:** 1 chip (W25X32)
- **Cypress/Spansion:** 3 chips (S25FL series)
- **Other:** 4 chips (BergMicro, Zbit, EON)

### Actual Issue Identified
The user clarified that the manufacturer actually meant **PY25Q128** (Puya chip), not W25Q128 (Winbond). The PY25Q128 is a separate task and will be handled independently.

## Recommendation

✅ **PR with alias only** - The USE_FLASH_SPI_NOR alias is useful and should be submitted as-is.

No JEDEC ID additions are needed for this PR because:
1. W25Q128 is already fully supported
2. PY25Q128 (Puya) is being handled as a separate task
3. The alias work stands on its own merit (better naming)

## PR Status

The alias PR is ready to be created:
- Branch exists: `add-flash-spi-nor-alias`
- Commit ready: `6c2149702f`
- No conflicts expected
- Improves code clarity without functional changes

## Files Reviewed

- `src/main/target/common_post.h` - Alias definition (lines 138-143)
- `src/main/drivers/flash_m25p16.c` - JEDEC ID table and driver implementation

## Notes

- The M25P16 driver name is historically misleading - the alias helps
- No build testing needed - this is a preprocessor alias only
- Upstream INAV would likely accept this as it improves code readability
- The separate PY25Q128 task will handle the Puya chip JEDEC ID addition

## Outcome

**Task closed.** The investigation confirmed:
1. ✅ Alias work is good and ready for PR
2. ✅ W25Q128 already supported (no action needed)
3. ✅ PY25Q128 is separate task (handled elsewhere)

---

**Developer**
2025-12-06 14:00
