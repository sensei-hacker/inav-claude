# Reminder: Review USE_FLASH_SPI_NOR Alias PR

**Date:** 2025-11-26
**From:** Developer
**Type:** Reminder
**Remind On:** 2025-12-03 (1 week from now)

## Summary

A branch has been created with a commit adding `USE_FLASH_SPI_NOR` as an alias for `USE_FLASH_M25P16` in the INAV firmware.

## Details

**Branch:** `add-flash-spi-nor-alias`
**Repository:** inav/
**Commit:** `6c2149702` - Add USE_FLASH_SPI_NOR alias for USE_FLASH_M25P16

The M25P16 flash driver actually supports many SPI NOR flash chips (W25Q, W25X, N25Q, S25FL series), but the define name doesn't reflect this. The new alias provides a more descriptive name.

## Action Required

In one week, please:
1. Review whether to create a PR for this change
2. Decide if upstream INAV would accept this improvement
3. Assign developer to create PR if appropriate

## Files Changed

- `src/main/target/common_post.h` - Added alias definition

---

*This is an automated reminder from the developer workflow.*
