# GPS Blackbox Testing Infrastructure

Complete workflow for capturing blackbox logs while sending GPS altitude data to SITL for testing navigation and EPH behavior.

## Overview

This infrastructure allows you to:
1. Configure SITL for MSP receiver and blackbox logging
2. Keep SITL armed continuously while sending RC data
3. Inject GPS altitude data via MSP_SET_RAW_GPS
4. Capture blackbox logs for analysis

## Quick Start

```bash
# Terminal 1: Run complete test (configuration + GPS injection + blackbox)
cd ~/Documents/planes/inavflight
./claude/test_tools/inav/gps/run_gps_blackbox_test.sh climb 60

# The script will:
# 1. Start/restart SITL
# 2. Configure MSP receiver, blackbox, and ARM mode
# 3. Arm SITL and inject GPS data for 60 seconds
# 4. Capture blackbox log
```

## Step-by-Step Manual Procedure

### 1. Start SITL

```bash
cd inav/build_sitl
pkill -9 SITL.elf 2>/dev/null
rm -f eeprom.bin  # Optional: fresh config
./bin/SITL.elf > /tmp/sitl.log 2>&1 &
sleep 10  # Wait for initialization
```

### 2. Configure SITL (one-time per eeprom.bin)

```bash
cd ~/Documents/planes/inavflight

# Configure MSP receiver, ARM mode, HITL, and test arming
python3 claude/test_tools/inav/sitl/sitl_arm_test.py 5760

# Enable blackbox FILE logging
python3 claude/test_tools/inav/gps/enable_blackbox.py

# Enable BLACKBOX feature flag
python3 claude/test_tools/inav/gps/enable_blackbox_feature.py
```

**Note:** Configuration persists in `eeprom.bin`. If you delete `eeprom.bin`, you must reconfigure.

### 3. Run GPS Test with Continuous Arming

```bash
# Run immediately after sitl_arm_test.py (while still armed)
# OR run sitl_arm_test.py again first if SITL was disarmed

python3 claude/test_tools/inav/gps/gps_with_rc_keeper.py --profile climb --duration 60

# Available profiles:
#   climb   - 0m to 100m at 5 m/s
#   descent - 100m to 0m at 2 m/s
#   hover   - constant 50m
#   sine    - oscillating ±30m around 50m
```

### 4. Capture Blackbox Log

```bash
cd inav/build_sitl
sleep 3  # Wait for blackbox to flush

# Find the timestamped log file
ls -lh 202*.TXT

# Rename for analysis
mv 2025_*.TXT my_test.TXT
```

### 5. Decode and Analyze

```bash
# Decode to CSV
blackbox_decode my_test.TXT

# Analyze navEPH behavior
# Fields of interest:
#   - navEPH: Position estimator's horizontal error (cm)
#   - navEPV: Position estimator's vertical error (cm)
#   - BaroAlt: Barometer altitude (cm)
```

## Scripts

### gps_with_rc_keeper.py
**Purpose:** Send GPS altitude data + continuous RC to keep SITL armed

**Features:**
- Enables HITL mode (bypasses sensor calibration)
- Sends RC at 50Hz with AUX1=HIGH to arm and maintain armed state
- Injects GPS altitude at 10Hz using MSP_SET_RAW_GPS
- Waits for arming confirmation before starting GPS injection
- Supports multiple altitude profiles (climb, descent, hover, sine)

**Usage:**
```bash
python3 gps_with_rc_keeper.py --profile climb --duration 60 --port 5760
```

**Parameters:**
- `--profile`: Motion profile (climb/descent/hover/sine)
- `--duration`: Test duration in seconds (default: 60)
- `--port`: MSP port (default: 5760)

**Dependencies:**
- uNAVlib library
- SITL must be configured for MSP receiver (via sitl_arm_test.py)

### run_gps_blackbox_test.sh
**Purpose:** Complete automated test wrapper

**Usage:**
```bash
./run_gps_blackbox_test.sh <profile> <duration>

# Examples:
./run_gps_blackbox_test.sh climb 60
./run_gps_blackbox_test.sh hover 30
```

**What it does:**
1. Ensures SITL is running
2. Runs sitl_arm_test.py to configure and arm
3. Immediately runs gps_with_rc_keeper.py
4. Reports blackbox log location

## Configuration Scripts

### sitl_arm_test.py
**Location:** `claude/test_tools/inav/sitl/sitl_arm_test.py`

**Purpose:** Configure SITL for MSP receiver and test arming

**What it configures:**
- RX type to MSP (byte 23 in RX_CONFIG = 2)
- ARM mode on AUX1 (1700-2100us range)
- HITL mode (bypasses sensor calibration)
- Saves config and reboots SITL

**Exit status:**
- 0: Successfully armed
- 1: Failed to arm (check arming blockers in output)

### enable_blackbox.py
**Purpose:** Configure blackbox for FILE logging (SITL-specific)

**Settings:**
- `blackbox_device = FILE (3)`
- `blackbox_rate_num = 1`
- `blackbox_rate_denom = 1`

**Output:** Timestamped .TXT files in `build_sitl/` directory
Format: `YYYY_MM_DD_HHMMSS.TXT`

### enable_blackbox_feature.py
**Purpose:** Enable BLACKBOX feature flag (bit 19)

**Note:** Feature flags are separate from blackbox device settings. Both must be enabled.

## Workflow Details

### Why Two Steps (sitl_arm_test + gps_with_rc_keeper)?

1. **sitl_arm_test.py**: Configures SITL one-time settings (MSP receiver, ARM mode)
   - Must save to EEPROM and reboot
   - Tests that arming works
   - Exits after successful arm

2. **gps_with_rc_keeper.py**: Keeps SITL armed and injects GPS
   - Runs for specified duration (e.g., 60s)
   - Must start immediately after sitl_arm_test.py
   - If gap > 200ms, SITL disarms (MSP receiver timeout)

### Why Manual Steps Instead of One Script?

During development, we found:
- Configuration needs to persist (EEPROM)
- Blackbox settings require feature flag + device setting
- Arming has blockers that need debugging
- Separation allows testing each component

The `run_gps_blackbox_test.sh` wrapper combines them for convenience.

## Common Issues

### SITL Won't Arm

**Symptom:** `✗ SITL failed to arm - check ARM mode configuration`

**Solution:**
```bash
# Reconfigure SITL
python3 claude/test_tools/inav/sitl/sitl_arm_test.py 5760

# Then immediately run GPS test (within 200ms or SITL disarms)
python3 claude/test_tools/inav/gps/gps_with_rc_keeper.py --profile climb --duration 60
```

### No Blackbox Log Created

**Check:**
1. BLACKBOX feature enabled? Run `enable_blackbox_feature.py`
2. Blackbox device set to FILE? Run `enable_blackbox.py`
3. SITL actually armed? Check GPS test output for "✓ SITL is ARMED!"
4. Wait 3-5 seconds after test for blackbox to flush

### Blackbox Log Only 15ms of Data

**Known Issue:** SITL FILE logging may have bugs causing early termination or decode errors.

**Workaround:** Use serial port logging instead:
- Configure `blackbox_device = SERIAL (0)`
- Use blackbox log viewer to capture from TCP port

## Technical Details

### MSP Commands Used

| Command | Purpose |
|---------|---------|
| MSP_SET_RAW_RC (200) | Send RC channel data (50Hz) |
| MSP_SET_RAW_GPS (201) | Inject GPS altitude (10Hz) |
| MSP_SIMULATOR (0x201F) | Enable HITL mode |
| MSP2_INAV_STATUS (0x2000) | Query arming status |
| MSP_SET_RX_CONFIG (45) | Configure receiver type |
| MSP_SET_MODE_RANGE (35) | Configure ARM mode |
| MSP_EEPROM_WRITE (250) | Save settings |
| MSP_REBOOT (68) | Reboot FC |

### RC Channel Order

INAV uses AETR mapping:
```
Channel 0 (Raw 0) -> Roll
Channel 1 (Raw 1) -> Pitch
Channel 2 (Raw 2) -> Throttle
Channel 3 (Raw 3) -> Yaw
Channel 4 (Raw 4) -> AUX1 (ARM switch)
```

### GPS Data Format (MSP_SET_RAW_GPS)

```c
struct {
    uint8_t  fixType;      // 0=no fix, 3=3D fix
    uint8_t  numSat;       // Number of satellites
    int32_t  lat;          // Latitude * 1e7
    int32_t  lon;          // Longitude * 1e7
    uint16_t alt_m;        // Altitude in meters
    uint16_t groundSpeed;  // Speed in cm/s
}
```

### Blackbox Fields for Analysis

```csv
navEPH          - Position estimator horizontal error (cm)
navEPV          - Position estimator vertical error (cm)
navPos[0,1,2]   - Estimated position (cm)
navVel[0,1,2]   - Estimated velocity (cm/s)
BaroAlt         - Barometer altitude (cm)
GPS_altitude    - GPS altitude (cm)
```

## GPS Issue #11202 Investigation

**Goal:** Test if stable GPS EPH produces stable navEPH or if position estimator amplifies fluctuations.

**Hypothesis:** Position estimator runs at 1000Hz and grows EPH by factor (1 + dt) between GPS updates, creating sawtooth pattern.

**Test Plan:**
1. Run stable GPS scenario (constant EPH=100cm)
2. Run fluctuating GPS scenario (EPH varies 150-450cm)
3. Compare navEPH amplitudes in blackbox logs

**Status:** Infrastructure complete, blackbox FILE logging has issues (only 15ms data decoded).

**Next Steps:**
- Try serial blackbox logging instead of FILE
- Or use MSP2_SENSOR_GPS to inject EPH directly (current scripts use MSP_SET_RAW_GPS which doesn't include EPH)

## Related Documentation

- SITL Arming: `claude/test_tools/inav/sitl/README.md`
- MSP Protocol: `.claude/skills/msp-protocol/SKILL.md`
- GPS Issue #11202: `claude/developer/investigations/gps-fluctuation-issue-11202/`
