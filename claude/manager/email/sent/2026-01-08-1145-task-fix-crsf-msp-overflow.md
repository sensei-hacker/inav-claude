# Task Assignment: Fix CRSF MSP Integer Overflow

**Date:** 2026-01-08 11:45
**Project:** fix-crsf-msp-overflow
**Priority:** High (Security)
**Repository:** inav
**GitHub Issue:** #11209

## Task

Fix integer overflow vulnerability in CRSF MSP request handling.

## What to Do

Add a bounds check in `src/main/rx/crsf.c` in the `crsfDataReceive()` function.

**Find this code:**
```c
case CRSF_FRAMETYPE_MSP_REQ:
case CRSF_FRAMETYPE_MSP_WRITE: {
    uint8_t *frameStart = (uint8_t *)&crsfFrame.frame.payload + CRSF_FRAME_ORIGIN_DEST_SIZE;
    if (bufferCrsfMspFrame(frameStart, crsfFrame.frame.frameLength - 4)) {
```

**Change to:**
```c
case CRSF_FRAMETYPE_MSP_REQ:
case CRSF_FRAMETYPE_MSP_WRITE: {
    if (crsfFrame.frame.frameLength < 4) {
        break;  // Discard malformed frame
    }
    uint8_t *frameStart = (uint8_t *)&crsfFrame.frame.payload + CRSF_FRAME_ORIGIN_DEST_SIZE;
    if (bufferCrsfMspFrame(frameStart, crsfFrame.frame.frameLength - 4)) {
```

## Why This Matters

If `frameLength` is 3, the expression `frameLength - 4` underflows to 0xFFFFFFFF, causing `memcpy()` to write massive amounts of data out of bounds. This is a security vulnerability.

## Testing

1. Build SITL
2. Verify build passes
3. If you have CRSF hardware, verify MSP over CRSF still works

## Success Criteria

- [ ] Bounds check added
- [ ] Build passes
- [ ] Comment the fix on GitHub issue #11209

## Notes

- One-line fix
- Low regression risk
- Project summary: `claude/projects/fix-crsf-msp-overflow/summary.md`

---
**Manager**
