# Session State: OLED Display Auto-Detection

**Last Updated:** 2025-12-22
**Status:** In Progress
**Branch:** `feature/oled-auto-detection` (based on `maintenance-9.x`)
**Commit:** `e82115a457`

## Summary

Integrating OLED display auto-detection into INAV, based on the ss_oled library's detection algorithm. The goal is to auto-detect which OLED controller is connected and adjust display handling accordingly.

## Completed

1. **Added controller type enum** in `src/main/drivers/display_ug2864hsweg01.c`:
   - `OLED_CONTROLLER_UNKNOWN`
   - `OLED_CONTROLLER_SSD1306` - Most common 128x64/128x32
   - `OLED_CONTROLLER_SH1106` - 132x64 with 2-pixel offset
   - `OLED_CONTROLLER_SH1107` - 128x128 displays
   - `OLED_CONTROLLER_SSD1309` - Similar to SSD1306

2. **Implemented `detectOledController()` function**:
   - Reads status register 0x00 from the OLED controller
   - Masks lower nibble to identify controller type
   - Detection logic:
     - `0x07` or `0x0F` → SH1107
     - `0x08` → SH1106
     - `0x03` or `0x06` → SSD1306
     - Unknown defaults to SSD1306

3. **Added LOG_ERROR debug messages**:
   - Raw status register value
   - Masked controller ID bits
   - Detected controller name
   - Init sequence progress

4. **Build verified** with YUPIF7 target

## Still TODO

1. **Update drawing code for SH1106**:
   - SH1106 has 132-pixel wide RAM but 128-pixel display
   - Needs +2 pixel X offset when setting column address
   - Modify `i2c_OLED_set_xy()` and `i2c_OLED_set_line()` to apply offset

2. **Consider SH1107 support**:
   - 128x128 displays have different aspect ratio
   - May need different initialization sequence

## Key Files

- `inav/src/main/drivers/display_ug2864hsweg01.c` - Main driver (modified)
- `inav/src/main/drivers/display_ug2864hsweg01.h` - Header
- `inav/src/main/io/dashboard.c` - Uses the OLED driver

## Reference

- ss_oled library: https://github.com/bitbank2/ss_oled
- Detection code: https://github.com/bitbank2/ss_oled/blob/01fb9a53388002bbb653c7c05d8e80ca413aa306/src/ss_oled.cpp#L810

## Notes

- `USE_LOG` compiler flag required for LOG_* macros to work
- Runtime log level must be set to appropriate level via CLI (`set log_level = X`)
- Tested build target: YUPIF7 (has `USE_DASHBOARD` enabled)

## To Resume

```bash
cd /home/raymorris/Documents/planes/inavflight/inav
git checkout feature/oled-auto-detection
```

Then implement X offset for SH1106 in `i2c_OLED_set_xy()` and related functions.
