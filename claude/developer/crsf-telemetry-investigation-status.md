# CRSF Telemetry Investigation Status

**Date:** 2025-12-07
**Task:** Integrate fake sensors into INAV SITL for testing CRSF telemetry frames (PR #11025)
**Status:** IN PROGRESS - Root cause identified, blocked by SITL crash

---

## Summary

Successfully identified why CRSF telemetry is not transmitting, but investigation is blocked by a SITL crash when enabling the TELEMETRY feature flag via MSP.

---

## Completed Work

### 1. ✅ CRSF Compilation Enabled
- **File:** `src/main/target/SITL/target.h:101`
- **Change:** Commented out `#undef USE_TELEMETRY_CRSF`
- **Result:** CRSF telemetry code now compiled into SITL binary
- **Verification:** `nm build/bin/SITL.elf | grep crsfRxSendTelemetryData` shows symbol present

### 2. ✅ MSP_SET_RX_CONFIG Bug Fixed
- **File:** `configure_sitl_crsf.py:85-123`
- **Root Cause:** Script was using wrong MSP_SET_RX_CONFIG byte layout
  - Wrong: Byte 0 = 9 (incorrect enum), Byte 23 = 2
  - Correct: Byte 0 = 6 (SERIALRX_CRSF), Byte 23 = 1 (RX_TYPE_SERIAL)
- **Fix:** Updated script with correct MSP format from `fc_msp.c:2964-2987`
- **Result:** UART2 now binds to port 5761 successfully

### 3. ✅ Comprehensive Test Script Created
- **File:** `/home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/test_crsf_telemetry.sh`
- **Features:**
  - Automated 7-step test workflow
  - Verifies SITL binary has CRSF support
  - Enables TELEMETRY feature flag
  - Configures CRSF on UART2
  - Tests for PR #11025 frames (AIRSPEED, RPM, TEMPERATURE)
- **Status:** Works through step 3, fails at step 4 (SITL crash)

---

## Root Cause Analysis

### Telemetry Initialization Timing

**The Problem:**
`initCrsfTelemetry()` sets `crsfTelemetryEnabled` based on whether the CRSF RX serial port is open at initialization time.

**Code Flow (fc_init.c):**
```
Line 551: rxInit()           → Opens CRSF serial port if configured
Line 609: telemetryInit()    → Calls initCrsfTelemetry()
```

**Initialization Logic (telemetry/crsf.c:650-654):**
```c
void initCrsfTelemetry(void) {
    crsfTelemetryEnabled = crsfRxIsActive();  // Checks serialPort != NULL
    // ... schedule frames
}
```

**The Solution:**
Configure CRSF RX via MSP → Save to EEPROM → Reboot. On next boot:
1. `rxInit()` opens CRSF port (because config saved)
2. `telemetryInit()` sees port is active
3. Telemetry enabled!

---

## Current Blocker

### SITL Crashes After Enabling TELEMETRY Feature

**Observed Behavior:**
```bash
[4/7] Enabling TELEMETRY feature flag...
  Enabling TELEMETRY feature...
✓ TELEMETRY enabled, SITL rebooting...
✗ SITL died after reboot
```

**What Happens:**
1. Test script enables TELEMETRY feature (bit 10 = 0x400) via MSP_SET_FEATURE_CONFIG
2. Script saves config via MSP_EEPROM_WRITE
3. Script reboots SITL via MSP_REBOOT
4. **SITL crashes during startup** with eeprom showing saved config

**EEPROM Output Before Crash:**
```
[EEPROM] Program word  0x561a724299cc = 00000000
[EEPROM] Program word  0x561a724299d0 = 00010500
... (truncated)
[EEPROM] Saved 'eeprom.bin'
```

**Build Directory:** `/home/raymorris/Documents/planes/inavflight/inav/build/`

---

## Technical Findings

### 1. CRSF Telemetry Frame Scheduling (telemetry/crsf.c:686-692)

Frames are **conditionally scheduled** based on sensor detection:

```c
#ifdef USE_ESC_SENSOR
    crsfSchedule[index++] = BV(CRSF_FRAME_RPM_INDEX);      // Line 681
#endif

#if defined(USE_ESC_SENSOR) || defined(USE_TEMPERATURE_SENSOR)
    crsfSchedule[index++] = BV(CRSF_FRAME_TEMP_INDEX);     // Line 684
#endif

#ifdef USE_PITOT
    if (sensors(SENSOR_PITOT)) {
        crsfSchedule[index++] = BV(CRSF_FRAME_AIRSPEED_INDEX);  // Lines 687-689
    }
#endif
```

**Implication:** Even with telemetry enabled, AIRSPEED frame requires `sensors(SENSOR_PITOT)` to return true at runtime.

### 2. Fake Sensor Defines (target.h:65-75)

The SITL target **does** have fake sensors enabled:
```c
#define USE_PITOT_FAKE              // Line 65
#define USE_ESC_SENSOR              // Line 73
#define USE_TEMPERATURE_SENSOR      // Line 75
```

### 3. MSP_SET_RX_CONFIG Format (fc_msp.c:2964-2987)

**Critical Discovery:** MSP command uses custom serialization, NOT rxConfig_t struct layout:

| Byte(s) | Field | Value for CRSF |
|---------|-------|----------------|
| 0 | serialrx_provider | 6 (SERIALRX_CRSF) |
| 1-2 | maxcheck | 1900 |
| 3-4 | midrc | 1500 (ignored) |
| 5-6 | mincheck | 1100 |
| 7 | spektrum_sat_bind | 0 |
| 8-9 | rx_min_usec | 885 |
| 10-11 | rx_max_usec | 2115 |
| 12-22 | compatibility padding | 11 bytes of 0x00 |
| 23 | receiverType | 1 (RX_TYPE_SERIAL) |

---

## Files Modified

### Source Code
- `src/main/target/SITL/target.h:101` - Enabled CRSF compilation

### Configuration Scripts
- `configure_sitl_crsf.py:85-123` - Fixed MSP_SET_RX_CONFIG format

### Test Infrastructure
- `/home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/test_crsf_telemetry.sh` - Comprehensive test script (300 lines)

---

## Next Steps

### Immediate Priority: Fix SITL Crash

1. **Investigate crash cause**
   - Check if TELEMETRY feature flag conflicts with SITL configuration
   - Review SITL-specific telemetry initialization
   - May need to check if telemetry ports are properly configured for SITL

2. **Alternative approaches:**
   - Skip TELEMETRY feature flag (may already be enabled by default)
   - Use CLI commands instead of MSP to configure
   - Pre-configure eeprom.bin before first boot

### After Crash Fixed

3. **Verify sensor detection**
   - Confirm `sensors(SENSOR_PITOT)` returns true for fake sensors
   - Check if fake sensors register during SITL init

4. **Test telemetry transmission**
   - Run complete test script
   - Verify PR #11025 frames (0x0A AIRSPEED, 0x0C RPM, 0x0D TEMPERATURE)

---

## Test Commands

### Build SITL with CRSF
```bash
cd /home/raymorris/Documents/planes/inavflight/inav
# Edit src/main/target/SITL/target.h line 101: // #undef USE_TELEMETRY_CRSF
mkdir -p build && cd build
cmake -DSITL=ON ..
make -j4
```

### Run Comprehensive Test
```bash
cd /home/raymorris/Documents/planes/inavflight/inav
/home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/test_crsf_telemetry.sh build
```

### Manual Configuration Test
```bash
cd /home/raymorris/Documents/planes/inavflight/inav/build
rm -f eeprom.bin
./bin/SITL.elf &  # Start SITL
sleep 3
python3 ../configure_sitl_crsf.py  # Configure CRSF
# SITL reboots automatically
sleep 8
ss -tlnp | grep 5761  # Should show UART2 listening
```

---

## References

### Key Code Locations

**Initialization:**
- `src/main/fc/fc_init.c:551` - `rxInit()` call
- `src/main/fc/fc_init.c:609` - `telemetryInit()` call
- `src/main/telemetry/telemetry.c:133-135` - `initCrsfTelemetry()` call
- `src/main/telemetry/crsf.c:650-692` - CRSF telemetry init logic

**RX Configuration:**
- `src/main/rx/rx.c:296-305` - RX type switching (opens serial port)
- `src/main/rx/crsf.c:330-333` - `crsfRxIsActive()` implementation
- `src/main/fc/fc_msp.c:2964-2987` - MSP_SET_RX_CONFIG handler

**Telemetry:**
- `src/main/telemetry/crsf.c:702-740` - `handleCrsfTelemetry()` scheduler
- `src/main/rx/crsf.h` - RX enum definitions

### Frame Types (PR #11025)
- `0x0A` - CRSF_FRAMETYPE_AIRSPEED
- `0x0C` - CRSF_FRAMETYPE_RPM
- `0x0D` - CRSF_FRAMETYPE_TEMPERATURE

---

## Notes

- The MSP configuration approach is correct: configure → save → reboot
- The initialization order is correct: RX before telemetry
- UART2 binding works after MSP_SET_RX_CONFIG fix
- **Main blocker:** SITL crashes when TELEMETRY feature is enabled

---

**Last Updated:** 2025-12-07
**Author:** Claude (Developer role)
**Session:** CRSF Telemetry Integration for PR #11025
