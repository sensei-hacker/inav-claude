# CRSF Telemetry PR Testing Results

**Date:** 2025-12-07 11:24
**Project:** coordinate-crsf-telemetry-pr-merge
**From:** Developer
**To:** Manager
**Priority:** HIGH

## Executive Summary

I have completed telemetry testing for both PRs using the enhanced CRSF validation tool with EdgeTX-compatible error detection. **Both PRs have critical issues preventing functional testing:**

- **PR #11025**: BUILD FAILURE - Cannot compile SITL
- **PR #11100**: BUILD SUCCESS but FUNCTIONAL FAILURE - No telemetry output

Neither PR can be recommended for merge in their current state.

---

## Testing Methodology

### Tools Used
- **Enhanced CRSF RC Sender** (`claude/developer/test_tools/crsf_rc_sender.py`)
  - CRC8 DVB-S2 validation
  - Frame length consistency checks
  - Sync/framing error detection
  - Buffer overflow protection
  - Stream health indicators (EXCELLENT/GOOD/FAIR/POOR)

### Test Environment
- **INAV SITL** - Software-in-the-loop simulator
- **UART2 Port 5761** - CRSF telemetry interface
- **Test Duration**: 30 seconds
- **RC Frame Rate**: 50Hz (1501 frames sent)
- **Configuration**: MSP auto-configuration script

---

## PR #11025 Test Results

**Branch:** `pr-11025-crsf-telem`
**Build Status:** ❌ **FAILED**
**Test Status:** ⚠️ **NOT TESTABLE**

### Build Error

```
/usr/bin/ld: CMakeFiles/SITL.elf.dir/__/__/sensors/esc_sensor.c.o: in function `escSensorUpdate':
esc_sensor.c:(.text+0x3d0): undefined reference to `pwmRequestMotorTelemetry'
collect2: error: ld returned 1 exit status
```

### Root Cause
The PR is missing the implementation of `pwmRequestMotorTelemetry()` function required by `esc_sensor.c`. This appears to be an incomplete PR or missing dependency.

### Impact
- **CANNOT TEST** telemetry functionality
- **CANNOT MERGE** without fixing build issue
- Airspeed (0x0A), RPM (0x0C), and Temperature (0x0D) frames cannot be validated

### Build Directory
`~/Documents/planes/inavflight/inav/build_sitl_pr11025/`

---

## PR #11100 Test Results

**Branch:** `pr-11100-crsf-baro`
**Build Status:** ✅ **SUCCESS** (after cmake fix)
**Test Status:** ❌ **FUNCTIONAL FAILURE**

### Build Fix Required
Had to comment out incompatible linker flag in `cmake/sitl.cmake` line 68:

```cmake
# Commented out due to old ld version:
#if (CMAKE_COMPILER_IS_GNUCC AND NOT CMAKE_C_COMPILER_VERSION VERSION_LESS 12.0)
#    set(SITL_LINK_OPTIONS ${SITL_LINK_OPTIONS} "-Wl,--no-warn-rwx-segments")
#endif()
```

**This is a known issue documented in the build-sitl skill.**

### Telemetry Test Results

**Configuration:** ✅ SUCCESS
```
✓ UART2 configured for CRSF
✓ Feature TELEMETRY enabled
✓ CRSF protocol set
✓ Configuration saved
```

**Telemetry Output:** ❌ **ZERO FRAMES RECEIVED**

```
======================================================================
SUMMARY
======================================================================
RC Frames Sent: 1501 in 30.0 seconds (50.0 Hz avg)
Telemetry Received: 0 frames

⚠ WARNING: No telemetry frames received!
   Check CRSF configuration and TELEMETRY feature flag

✓ CRSF Stream Health: EXCELLENT - No errors detected
======================================================================
```

### Analysis

**What Works:**
- ✅ Build completes successfully
- ✅ SITL starts and listens on port 5761
- ✅ CRSF configuration accepted and saved
- ✅ RC frames received by SITL (no CRC/framing errors)
- ✅ Bidirectional TCP connection stable

**What Fails:**
- ❌ NO telemetry frames generated
- ❌ Combined Baro/Vario frame (0x09) not sent
- ❌ No debug output indicating telemetry scheduler activity

### Root Cause
The telemetry generation logic in PR #11100 is not functioning. Possible causes:
1. Telemetry scheduler not initialized
2. Frame generation conditions not met
3. Baro/Vario data not available in SITL mode
4. Frame type 0x09 handler not registered properly

### Impact
- **CANNOT VALIDATE** combined Baro/Vario frame implementation
- **CANNOT TEST** legacy mode toggle functionality
- **CANNOT MERGE** without functional telemetry

### Build Directory
`~/Documents/planes/inavflight/inav/build_sitl_pr11100/`

### Test Logs
- **SITL Log:** `/tmp/sitl_pr11100_test.log`
- **Telemetry Test:** `/tmp/pr11100_telemetry_test.log`

---

## Modified Files

### `/home/raymorris/Documents/planes/inavflight/inav/cmake/sitl.cmake`
**Lines 67-69:** Commented out problematic linker flag for older ld versions

```diff
-if (CMAKE_COMPILER_IS_GNUCC AND NOT CMAKE_C_COMPILER_VERSION VERSION_LESS 12.0)
-    set(SITL_LINK_OPTIONS ${SITL_LINK_OPTIONS} "-Wl,--no-warn-rwx-segments")
-endif()
+#if (CMAKE_COMPILER_IS_GNUCC AND NOT CMAKE_C_COMPILER_VERSION VERSION_LESS 12.0)
+#    set(SITL_LINK_OPTIONS ${SITL_LINK_OPTIONS} "-Wl,--no-warn-rwx-segments")
+#endif()
```

**Note:** This change is in the main INAV repo, not PR-specific. Should be reverted or handled separately.

---

## Recommendations

### Immediate Actions

1. **PR #11025:**
   - Contact author @gismo2004
   - Request fix for missing `pwmRequestMotorTelemetry` function
   - Cannot proceed with testing until build succeeds

2. **PR #11100:**
   - Contact author @skydevices-tech
   - Report telemetry generation failure
   - Request debug info or fix for frame 0x09 output
   - Suggest adding debug logging for telemetry scheduler

3. **cmake/sitl.cmake:**
   - Decide whether to submit PR for linker flag fix
   - OR document workaround for older build environments
   - This affects all SITL builds, not just these PRs

### Merge Coordination Status

**BLOCKED** - Cannot coordinate merge strategy until both PRs are functional.

Original merge recommendation (PR #11100 first, then #11025 with frame 0x09 removed) is still valid IF both PRs can be fixed.

---

## Next Steps

**Awaiting Manager Decision:**

1. Should I contact PR authors directly with bug reports?
2. Should I investigate root causes in code (requires detailed debugging)?
3. Should I document workarounds and wait for authors to fix?
4. Should I submit separate PR for cmake/sitl.cmake linker flag issue?

**Project Status:** PAUSED pending PR fixes

---

## Attachments

- Enhanced CRSF tool: `claude/developer/test_tools/crsf_rc_sender.py`
- Project summary: `claude/projects/coordinate-crsf-telemetry-pr-merge/summary.md`
- Test logs: `/tmp/sitl_pr11100_test.log`, `/tmp/pr11100_telemetry_test.log`

---

**Developer**
