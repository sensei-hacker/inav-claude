# Task Assignment: Investigate Flash SPI NOR Alias & JEDEC IDs

**Date:** 2025-12-06 12:30
**Project:** flash-spi-nor-alias-review
**Priority:** MEDIUM
**Estimated Effort:** 1-2 hours
**Branch:** From `add-flash-spi-nor-alias` (already exists)

---

## Task

Review the Flash SPI NOR alias work and investigate if JEDEC IDs need to be added to support additional flash chips.

---

## Background

**Reminder from Nov 26:**
- You created branch `add-flash-spi-nor-alias`
- Commit `6c2149702` - Added `USE_FLASH_SPI_NOR` as alias for `USE_FLASH_M25P16`
- Purpose: More descriptive name for SPI NOR flash driver
- The M25P16 driver supports many chips: W25Q, W25X, N25Q, S25FL series

**User insight:** The flash NOR alias might refer to a chip that needs JEDEC IDs added to the code.

---

## What to Do

### Step 1: Review Existing Branch

Check the current state of your branch:

```bash
cd inav
git checkout add-flash-spi-nor-alias
git log --oneline -5
```

Review what you changed:
- `src/main/target/common_post.h` - The alias definition

### Step 2: Investigate JEDEC ID Requirements

**Check the flash driver:**

**File:** `src/main/drivers/flash_m25p16.c` (or similar)

Look for:
1. JEDEC ID table - List of supported chip IDs
2. Chip detection code - How it identifies flash chips
3. Supported chip list - Which chips are currently recognized

**Example of what to look for:**
```c
static const flashDevice_t flashDevices[] = {
    { 0xEF4018, W25Q128_PAGESIZE, W25Q128_PAGES_PER_SECTOR },  // W25Q128
    { 0xEF7018, W25Q128_PAGESIZE, W25Q128_PAGES_PER_SECTOR },  // W25Q128 (alt ID)
    { 0x202018, M25P128_PAGESIZE, M25P128_PAGES_PER_SECTOR },  // M25P128
    // ... more IDs
};
```

### Step 3: Check for Missing JEDEC IDs

**Research if there are flash chips that:**
1. Are commonly used in flight controllers
2. Should work with the M25P16 driver
3. Are missing from the JEDEC ID table

**Common SPI NOR flash chips to check:**
- W25Q series (W25Q16, W25Q32, W25Q64, W25Q128, W25Q256)
- GigaDevice GD25Q series
- Macronix MX25L series
- Winbond W25X series
- Micron N25Q series
- Spansion/Cypress S25FL series

**How to verify:**
- Check datasheets for JEDEC ID (usually first 3 bytes: Manufacturer + Device)
- Compare against the driver's ID table
- Identify any missing entries

### Step 4: Document Findings

Create or update documentation:

**If JEDEC IDs are missing:**
```markdown
## Missing JEDEC IDs

The following flash chips are compatible but missing from the ID table:

| Chip | JEDEC ID | Capacity | Status |
|------|----------|----------|--------|
| GD25Q128 | 0xC84018 | 16MB | Missing |
| MX25L12835F | 0xC22018 | 16MB | Missing |
```

**If alias is sufficient:**
```markdown
## Flash SPI NOR Alias

The USE_FLASH_SPI_NOR alias provides a more descriptive name for the M25P16 driver.

No JEDEC ID additions needed - all common chips already supported.
```

### Step 5: Implement Additions (if needed)

**If JEDEC IDs need to be added:**

1. Add missing IDs to the flash device table
2. Test build with additions
3. Update documentation
4. Prepare PR description with chip compatibility list

**Example addition:**
```c
// Add to flashDevices[] table
{ 0xC84018, W25Q128_PAGESIZE, W25Q128_PAGES_PER_SECTOR },  // GD25Q128
{ 0xC22018, W25Q128_PAGESIZE, W25Q128_PAGES_PER_SECTOR },  // MX25L12835F
```

---

## Success Criteria

- [ ] Reviewed existing branch and commit
- [ ] Investigated flash driver JEDEC ID table
- [ ] Identified any missing JEDEC IDs
- [ ] Documented findings
- [ ] Added missing IDs (if applicable)
- [ ] Tested build
- [ ] Recommended PR approach (alias only, or alias + IDs)

---

## Files to Check

**INAV repository:**
- `src/main/target/common_post.h` - Your alias definition
- `src/main/drivers/flash_m25p16.c` - Flash driver implementation
- `src/main/drivers/flash.h` - Flash API definitions
- `docs/development/Hardware Debugging.md` - Flash chip documentation (if exists)

**Reference commits:**
- Your commit `6c2149702` on branch `add-flash-spi-nor-alias`
- Previous flash driver updates (search git log for "flash" or "JEDEC")

---

## Expected Output

### Completion Report Format

```markdown
## Investigation Results

**Branch reviewed:** add-flash-spi-nor-alias
**Commit:** 6c2149702

### Current Alias Implementation
[What the alias does]

### JEDEC ID Analysis
- **Chips currently supported:** [list]
- **Missing JEDEC IDs found:** [list or "None"]

### Recommendation
- [ ] PR with alias only (no IDs needed)
- [ ] PR with alias + additional JEDEC IDs
- [ ] Do not submit PR (reason)

### Changes Made (if applicable)
[List of JEDEC IDs added]
```

---

## Reference

**Previous similar work:**
- W25Q128 support investigation (completed Nov 30)
- Found W25Q128 already supported with 2 JEDEC ID variants

**Context:**
- Many flight controllers use various SPI NOR flash chips
- Driver should support common chips
- JEDEC ID is how the driver identifies the chip
- Missing IDs mean "unknown flash chip" errors at boot

---

## Notes

- **Historical context:** The M25P16 driver name is misleading - it supports many chips beyond M25P16
- **The alias helps:** USE_FLASH_SPI_NOR is more accurate/descriptive
- **Check real hardware:** If you have flight controllers, check what flash chips they use
- **Upstream benefit:** If you find missing IDs, upstream INAV would likely accept them

This is a low-priority task but useful for improving flash chip compatibility.

---

## Timeline

**Review due:** Overdue (original reminder was Dec 3)
**Estimated effort:** 1-2 hours
- 30 min: Review branch and driver code
- 30 min: Check JEDEC IDs and research chips
- 30 min: Add missing IDs (if needed)
- 30 min: Documentation and completion report

---

**Manager**
2025-12-06 12:30
