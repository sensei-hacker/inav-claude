# CRSF Telemetry Testing Status

**Date:** 2025-12-07
**Developer:** Claude
**Task:** Testing CRSF telemetry in SITL for PR #11025

---

## Summary

Working on testing CRSF telemetry frames (AIRSPEED, RPM, TEMPERATURE) in SITL. Made significant progress on test infrastructure and debug tooling. Currently debugging why telemetry frames are not being transmitted.

---

## Work Completed

### 1. ✅ Test Infrastructure Created

**File:** `/home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/test_crsf_telemetry.sh`
- Comprehensive 7-step automated test workflow
- Verifies SITL binary has CRSF support
- Enables TELEMETRY feature flag via MSP
- Configures CRSF on UART2
- Tests for PR #11025 frames (AIRSPEED 0x0A, RPM 0x0C, TEMPERATURE 0x0D)
- 300 lines of robust error handling

**File:** `/home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/quick_test_crsf.sh`
- Quick build-test cycle script
- Options: `-r` (rebuild), `-c` (clean), `-s` (skip test)
- Streamlines repetitive development workflow
- Usage: `./quick_test_crsf.sh -r` to rebuild and test

### 2. ✅ Debug Instrumentation Added

**File:** `src/main/telemetry/crsf.c`

Added SD() macro debug output to trace telemetry flow:

```c
// At initialization
SD(fprintf(stderr, "[CRSF TELEM] initCrsfTelemetry called, crsfRxIsActive=%d, enabled=%d\n",
    crsfRxIsActive(), crsfTelemetryEnabled));

// Frame scheduling
SD(fprintf(stderr, "[CRSF TELEM] Scheduled RPM frame (index %d)\n", index-1));
SD(fprintf(stderr, "[CRSF TELEM] Scheduled TEMP frame (index %d)\n", index-1));
SD(fprintf(stderr, "[CRSF TELEM] Total %d frames scheduled\n", crsfScheduleCount));

// Runtime status
SD(fprintf(stderr, "[CRSF TELEM] handleCrsfTelemetry called but telemetry DISABLED\n"));
SD(fprintf(stderr, "[CRSF TELEM] handleCrsfTelemetry called, telemetry ENABLED\n"));
```

### 3. ✅ Build Environment Setup

**Branch:** `pr-11025-crsf-telem` (has both PR #11025 and fake sensors)
**Build Directory:** `build_sitl_crsf`
**Binary Location:** `build_sitl_crsf/bin/SITL.elf`

**Build verified:**
```bash
nm build_sitl_crsf/bin/SITL.elf | grep -E "crsfRxSendTelemetryData|fakeEscSensor"
# Output: Symbols found ✓
```

**Changes:**
- `src/main/target/SITL/target.h:101` - Enabled CRSF telemetry compilation
- Added `#ifdef SITL_BUILD` includes for stdio.h
- Added `build/debug.h` include for SD() macro

---

## Current Issue: No Telemetry Frames Being Sent

### Test Result
```
[6/7] Testing CRSF telemetry...
  ✓ RC sender running
  Capturing telemetry for 10 seconds...

CRSF Telemetry Test Results:
0 unique frame types received

PR #11025 Frames:
  ✗ AIRSPEED (0x0A): NOT RECEIVED
  ✗ RPM (0x0C): NOT RECEIVED
  ✗ TEMPERATURE (0x0D): NOT RECEIVED

✗ FAILURE: No PR #11025 frames received
```

### Hypotheses

**1. TELEMETRY Feature Flag Issue**
- Test script enables `FEATURE_TELEMETRY` (bit 10)
- SITL reboots after configuration
- Need to verify flag persists after reboot

**2. CRSF RX Not Active**
- `initCrsfTelemetry()` checks `crsfRxIsActive()`
- Returns true only if CRSF serial port is open
- May need RX configured BEFORE telemetry init

**3. Fake Sensors Not Detected**
- Airspeed frame only scheduled if `sensors(SENSOR_PITOT)` returns true
- Fake pitot sensor may not be registering at runtime
- Need to verify sensor detection during init

**4. Frame Generation Functions Missing**
- PR #11025 may not have all frame generation functions implemented
- Need to verify: `crsfFrameAirspeedSensor()`, `crsfFrameRpm()`, `crsfFrameTemp()` exist

---

## Debug Strategy

### Next Steps

**1. Manual SITL Test with Log Monitoring**
```bash
# Terminal 1: Start SITL and watch logs
cd ~/Documents/planes/inavflight/inav/build_sitl_crsf
rm -f eeprom.bin
./bin/SITL.elf 2>&1 | grep "CRSF TELEM"

# Terminal 2: Configure via MSP
python3 ../enable_telemetry_feature.py
sleep 5
python3 ../configure_sitl_crsf.py
```

**2. Check Debug Output**
Look for these messages:
- `[CRSF TELEM] initCrsfTelemetry called, crsfRxIsActive=X, enabled=X`
- `[CRSF TELEM] Scheduled RPM frame (index X)`
- `[CRSF TELEM] handleCrsfTelemetry called, telemetry ENABLED`

**3. Verify Initialization Order**
```c
// Expected order in fc_init.c:
Line 551: rxInit()        // Opens CRSF port if configured
Line 609: telemetryInit() // Calls initCrsfTelemetry()
```

**4. Check Sensor Detection**
Add more debug to see if fake sensors are detected:
```c
#ifdef USE_PITOT
    if (sensors(SENSOR_PITOT)) {
        SD(fprintf(stderr, "[CRSF TELEM] PITOT sensor DETECTED\n"));
    } else {
        SD(fprintf(stderr, "[CRSF TELEM] PITOT sensor NOT detected\n"));
    }
#endif
```

**5. Alternative: Use GDB**
```bash
cd ~/Documents/planes/inavflight/inav/build_sitl_crsf
gdb ./bin/SITL.elf
(gdb) break initCrsfTelemetry
(gdb) break handleCrsfTelemetry
(gdb) run
```

---

## Files Modified

### Source Code
- `src/main/telemetry/crsf.c` - Added debug output
- `src/main/target/SITL/target.h` - Enabled CRSF telemetry (line 101)

### Test Infrastructure
- `claude/test_tools/inav/test_crsf_telemetry.sh` - Comprehensive test (existing)
- `claude/test_tools/inav/quick_test_crsf.sh` - Quick build-test cycle (NEW)

### Documentation
- `claude/developer/crsf-sitl-telemetry-breakthrough.md` - Previous findings
- `claude/developer/crsf-telemetry-investigation-status.md` - Investigation notes
- `claude/developer/crsf-telemetry-test-plan.md` - Test plan
- `claude/developer/2025-12-07-crsf-telemetry-testing-status.md` - This document

---

## Technical Context

### CRSF Telemetry Flow

```
1. fc_init.c:551  → rxInit()
   - Opens serial port for CRSF RX
   - Port must be configured via MSP_SET_RX_CONFIG

2. fc_init.c:609  → telemetryInit()
   - Calls initCrsfTelemetry()

3. telemetry/crsf.c:654 → crsfTelemetryEnabled = crsfRxIsActive()
   - Checks if CRSF port is open
   - Sets crsfTelemetryEnabled flag

4. Schedule task → handleCrsfTelemetry()
   - Runs periodically (every loop)
   - Calls crsfRxSendTelemetryData()
   - Sends one frame per cycle (100ms = 10Hz)
```

### Frame Scheduling Logic

```c
// Only schedule airspeed if PITOT sensor detected AT INIT TIME
#ifdef USE_PITOT
    if (sensors(SENSOR_PITOT)) {
        crsfSchedule[index++] = BV(CRSF_FRAME_AIRSPEED_INDEX);
    }
#endif
```

**Implication:** Even with fake sensors, if `sensors(SENSOR_PITOT)` returns false during `initCrsfTelemetry()`, the airspeed frame will NEVER be scheduled.

### Fake Sensor Implementation

The `pr-11025-crsf-telem` branch includes commit 9456888b:
- `src/main/sensors/esc_sensor_fake.c` - Fake ESC (RPM + temp)
- `src/main/sensors/temperature_fake.c` - Fake temperature sensors
- `src/main/sensors/pitot_fake.c` - Fake pitot sensor (if exists)

Need to verify:
1. Fake sensors are initialized before `initCrsfTelemetry()`
2. `sensors(SENSOR_PITOT)` returns true
3. ESC sensor fake data is available

---

## Previous Breakthroughs

### SITL Crash Issue - SOLVED
**Problem:** SITL crashed when enabling TELEMETRY feature
**Solution:** Issue resolved in previous session (documented in `crsf-sitl-telemetry-breakthrough.md`)

### MSP_SET_RX_CONFIG Bug - FIXED
**Problem:** Wrong byte layout in configure script
**Solution:** Updated to match fc_msp.c:2964-2987 format

### CRSF Compilation - ENABLED
**Problem:** CRSF telemetry disabled by default in SITL
**Solution:** Commented out `#undef USE_TELEMETRY_CRSF` in target.h

---

## Quick Commands

### Build and Test
```bash
# Quick rebuild and test
cd ~/Documents/planes/inavflight/claude/test_tools/inav
./quick_test_crsf.sh -r

# Clean rebuild
./quick_test_crsf.sh -c

# Just test (no rebuild)
./quick_test_crsf.sh
```

### Manual Testing
```bash
# Start SITL
cd ~/Documents/planes/inavflight/inav/build_sitl_crsf
rm -f eeprom.bin
./bin/SITL.elf 2>&1 | tee /tmp/sitl.log

# In another terminal: Configure
cd ~/Documents/planes/inavflight/inav
python3 enable_telemetry_feature.py
sleep 10
python3 configure_sitl_crsf.py

# Watch for telemetry
python3 crsf_stream_parser.py 2
```

### Debug Build
```bash
cd ~/Documents/planes/inavflight/inav/build_sitl_crsf
cmake -DSITL=ON -DCMAKE_BUILD_TYPE=Debug ..
make -j4
```

---

## Resources

**CRSF Protocol:**
- Frame format: `[SYNC][LEN][TYPE][PAYLOAD...][CRC]`
- Sync byte: 0xC8
- Max frame: 64 bytes
- CRC: CRC8 DVB-S2

**Frame Types (PR #11025):**
- 0x0A: CRSF_FRAMETYPE_AIRSPEED_SENSOR
- 0x0C: CRSF_FRAMETYPE_RPM
- 0x0D: CRSF_FRAMETYPE_TEMPERATURE (not in crsf.h, may be missing!)

**Key Code Locations:**
- Telemetry init: `src/main/telemetry/crsf.c:650`
- Telemetry handler: `src/main/telemetry/crsf.c:711`
- Frame definitions: `src/main/rx/crsf.h:92`
- FC init: `src/main/fc/fc_init.c:551,609`

---

## Status

**Overall:** 🟡 IN PROGRESS

**Components:**
- ✅ Test infrastructure complete
- ✅ Debug instrumentation added
- ✅ Build environment working
- 🟡 Telemetry transmission - under investigation
- ⏸️ Frame validation - pending telemetry working

**Next Session:**
1. Run SITL manually and check debug output
2. Verify initialization order and timing
3. Check sensor detection status
4. Consider using GDB if debug output insufficient
5. May need to add initialization for fake sensors

---

**Last Updated:** 2025-12-07 14:30 UTC
**Developer:** Claude (Developer role)
