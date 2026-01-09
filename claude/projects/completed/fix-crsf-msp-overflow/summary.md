# Project: Fix CRSF MSP Integer Overflow

**Status:** 📋 TODO
**Priority:** High (Security)
**Type:** Bug Fix
**Created:** 2026-01-08
**GitHub Issue:** #11209

## Overview

Fix integer overflow vulnerability in CRSF MSP request handling that causes massive out-of-bounds writes when processing malformed packets.

## Problem

In `crsfDataReceive()`, when handling `CRSF_FRAMETYPE_MSP_REQ` or `CRSF_FRAMETYPE_MSP_WRITE`, if `frameLength` is 3, the expression `frameLength - 4` underflows to -1 (0xFFFFFFFF as unsigned). This is passed to `bufferCrsfMspFrame()` which does a `memcpy()` with this massive length, causing out-of-bounds writes.

**Vulnerable code:**
```c
// src/main/rx/crsf.c - crsfDataReceive()
case CRSF_FRAMETYPE_MSP_REQ:
case CRSF_FRAMETYPE_MSP_WRITE: {
    uint8_t *frameStart = (uint8_t *)&crsfFrame.frame.payload + CRSF_FRAME_ORIGIN_DEST_SIZE;
    // BUG: if frameLength is 3, subtraction overflows!
    if (bufferCrsfMspFrame(frameStart, crsfFrame.frame.frameLength - 4)) {
        crsfScheduleMspResponse(crsfFrame.frame.payload[1]);
    }
    break;
}
```

## Solution

Add bounds check before the subtraction:

```c
case CRSF_FRAMETYPE_MSP_REQ:
case CRSF_FRAMETYPE_MSP_WRITE: {
    if (crsfFrame.frame.frameLength < 4) {
        break;  // Discard malformed frame
    }
    uint8_t *frameStart = (uint8_t *)&crsfFrame.frame.payload + CRSF_FRAME_ORIGIN_DEST_SIZE;
    if (bufferCrsfMspFrame(frameStart, crsfFrame.frame.frameLength - 4)) {
        crsfScheduleMspResponse(crsfFrame.frame.payload[1]);
    }
    break;
}
```

## Files to Modify

- `src/main/rx/crsf.c` - `crsfDataReceive()` function

## Testing

1. Build SITL
2. Verify CRSF MSP still works with valid frames
3. If possible, test with malformed frame to confirm it's rejected

## Success Criteria

- [ ] Bounds check added before `frameLength - 4` subtraction
- [ ] Malformed frames (frameLength < 4) are silently discarded
- [ ] Normal CRSF MSP operation unaffected
- [ ] Build passes for all targets

## Notes

- Security issue - OOB write vulnerability
- Reporter provided exact code location and suggested fix
- One-line fix with minimal regression risk
