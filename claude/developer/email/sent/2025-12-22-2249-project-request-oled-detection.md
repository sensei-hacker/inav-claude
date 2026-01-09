# Project Request: OLED Display Auto-Detection

**Date:** 2025-12-22 22:49
**From:** Developer
**To:** Manager
**Type:** Project Request

## Summary

I've started work on integrating OLED display auto-detection into INAV, based on the ss_oled library's detection algorithm. Requesting this be tracked as a project.

## Completed So Far

- Added controller type enum (SSD1306, SH1106, SH1107, SSD1309)
- Implemented `detectOledController()` function that reads status register 0x00
- Added LOG_ERROR debug messages to show detection results
- Code compiles successfully (tested with YUPIF7 target)

## Still Needed

- Update drawing code to handle different display widths:
  - **SSD1306:** 128 pixels wide (standard)
  - **SH1106:** 132 pixels wide (requires +2 pixel X offset)
  - **SH1107:** 128x128 displays (different aspect ratio)

## Files Modified

- `inav/src/main/drivers/display_ug2864hsweg01.c`

## Goal

Auto-detect which OLED controller is connected and adjust the display handling accordingly, so users don't need to configure it manually.

## Reference

- ss_oled library detection: https://github.com/bitbank2/ss_oled/blob/01fb9a53388002bbb653c7c05d8e80ca413aa306/src/ss_oled.cpp#L810

---
**Developer**
