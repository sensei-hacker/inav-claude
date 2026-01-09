# Task Completed: GitHub Issues Review

## Status: COMPLETED

## Summary
Reviewed 25 open issues from both inav-configurator and inav firmware repositories. Below are issues I may be able to address, plus two hardware support requests that warrant investigation.

---

## RECOMMENDED ISSUES TO FIX

### Immediate Action (Low effort, high impact)

#### 1. #2380 - Alignment Tool Crashes in Demo Mode
- **Problem:** Configurator crashes with "ECONNRESET" error when clicking Alignment Tool in demo mode
- **Estimated effort:** LOW-MEDIUM
- **Why good candidate:** Multiple users confirmed, clear reproduction steps, can test without hardware

#### 2. #2400 - Foxeer M10Q-250 Model Wrong Rotation
- **Problem:** Magnetometer 3D model rotated 90 degrees from physical orientation
- **Estimated effort:** LOW
- **Why good candidate:** Likely just a data/configuration change

### Short-term (Medium effort)

#### 3. #2407 - Linux 3D Animation Not Working
- **Problem:** Aircraft visualization empty on Linux (AMD GPU, Wayland)
- **Workaround:** Navigate to Mixer tab first, then return - suggests initialization order issue
- **Estimated effort:** MEDIUM

#### 4. #2373 - WGS84 Elevation Data Broken
- **Problem:** Elevation data shows WGS84 line flat at 0
- **Estimated effort:** MEDIUM
- **Why good candidate:** Could be API integration issue with Bing Maps

### Consider for Future

#### 5. #2361 - Bluetooth Device Chooser UX
- **Problem:** Long scrolling list, no filtering, unsorted devices
- **Estimated effort:** MEDIUM
- **Suggestions provided:** Add filter input, alphabetical sorting

#### 6. #11049 - GPS Recovery After Signal Loss (Firmware)
- **Problem:** Altitude and distance-to-home stuck at zero after GPS signal loss/recovery
- **Estimated effort:** MEDIUM-HIGH
- **Note:** Requires navigation expertise

---

## HARDWARE SUPPORT - RECOMMEND INVESTIGATION

#### #2398 - Add QMC5883P Compass Support
- Someone should investigate adding support for this compass sensor

#### #2405 - Add ICM-42688P Gyro/Accel Support (Skystars H743 Dual Gyro)
- Someone should investigate adding support for this IMU

---

## Files Modified
None - research task

## Notes
- Configurator issues (#2380, #2400, #2407, #2373, #2361) are most accessible for me to work on
- Issue #2380 is ideal first target since it can be tested in demo mode without hardware
