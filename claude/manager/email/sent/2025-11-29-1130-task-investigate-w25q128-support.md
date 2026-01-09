# Task Assignment: Investigate W25Q128 Blackbox Chip Support

**Date:** 2025-11-29 11:30
**Priority:** Medium
**Type:** Investigation
**Estimated Effort:** 1-2 hours

## Task

Investigate the current support for the W25Q128 SPI NOR flash chip (commonly used for blackbox logging) in both the INAV 8.0.1 branch and master branch.

## Background

The W25Q128 is a 128Mbit (16MB) SPI NOR flash chip from Winbond that is commonly used on flight controllers for blackbox data logging. We need to understand the current state of support for this chip in INAV.

## What to Do

1. **Check branch 8.0.1:**
   - Identify the flash driver code (likely in `src/main/drivers/flash*`)
   - Determine if W25Q128 is explicitly supported
   - Check the JEDEC ID detection code
   - Note any chip-specific handling or limitations

2. **Check master branch:**
   - Same investigation as above
   - Note any differences from 8.0.1

3. **Document findings:**
   - Which chips are explicitly supported?
   - How is chip detection done (JEDEC IDs)?
   - What is the maximum supported flash size?
   - Are there any known issues or limitations?

## Files to Check

- `src/main/drivers/flash.c`
- `src/main/drivers/flash.h`
- `src/main/drivers/flash_m25p16.c` (or similar)
- `src/main/drivers/flash_w25n.c` (if exists)
- Any target-specific flash configurations

## Success Criteria

- [ ] Report on W25Q128 support status in branch 8.0.1
- [ ] Report on W25Q128 support status in master
- [ ] List of supported JEDEC IDs in both branches
- [ ] Any differences between branches noted
- [ ] Recommendations if support is missing or incomplete

## Notes

This is related to the existing `add-flash-spi-nor-alias` branch work. Understanding current chip support will help inform future improvements to the flash driver naming and support.

---
**Manager**
