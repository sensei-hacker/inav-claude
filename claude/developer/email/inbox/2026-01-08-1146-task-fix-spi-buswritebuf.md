# Task Assignment: Fix SPI busWriteBuf Register Masking

**Date:** 2026-01-08 11:46
**Project:** fix-spi-buswritebuf
**Priority:** Medium
**Repository:** inav
**GitHub Issue:** #10674

## Task

Fix incorrect SPI register address masking in `busWriteBuf()`.

## What to Do

In `src/main/drivers/bus.c`, line 286, change:

```c
return spiBusWriteBuffer(dev, reg | 0x80, data, length);
```

to:

```c
return spiBusWriteBuffer(dev, reg & 0x7F, data, length);
```

## Why This Matters

For SPI, the MSB indicates read (1) or write (0):
- `busWrite()` correctly uses `reg & 0x7F` (clears MSB for write)
- `busWriteBuf()` incorrectly uses `reg | 0x80` (sets MSB - wrong!)

This bug has existed since at least INAV 3.0.0 and may cause SPI buffer writes to fail silently.

## Testing

1. Build for any SPI-sensor target (most targets)
2. Verify build passes
3. If hardware available, verify SPI sensors still work

## Success Criteria

- [ ] Line 286 changed from `| 0x80` to `& 0x7F`
- [ ] Build passes
- [ ] Comment the fix on GitHub issue #10674

## Notes

- One-line fix
- Compare with `busWrite()` at line 318 for reference
- Project summary: `claude/projects/fix-spi-buswritebuf/summary.md`

---
**Manager**
