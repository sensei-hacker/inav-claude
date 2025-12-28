# MSP2_INAV_DEBUG Truncation Issue - RESOLVED

**Date:** 2025-12-27
**Status:** ✅ FIXED

---

## Summary

Fixed MSP2_INAV_DEBUG truncation issue that was preventing navEPH data logging. The root cause was using the wrong MSP command code.

### Problem

- MSP2_INAV_DEBUG appeared to return only 4 bytes instead of 32 bytes (8 × uint32)
- Initial investigation suggested response truncation
- Raw socket tests showed SITL was actually sending `length=4` in the MSP response header

### Root Cause

**Used wrong MSP command code:**
- ❌ **WRONG**: `0x2009` (MSP2_INAV_ANALOG)
- ✅ **CORRECT**: `0x2019` (MSP2_INAV_DEBUG)

The incorrect code (0x2009) was triggering a different MSP handler that returns only 4 bytes.

### Solution

Updated `gps_with_naveph_logging_mspapi2.py` to use the correct MSP code:

```python
from mspapi2 import MSPApi, InavMSP

# CORRECT: Use the enum from mspapi2
MSP2_INAV_DEBUG = int(InavMSP.MSP2_INAV_DEBUG.value)  # 0x2019
```

### Verification

Tested with SITL and confirmed:
- ✅ Receives full 32 bytes (8 × uint32)
- ✅ navEPH data correctly extracted from `debug[7]`
- ✅ 299 samples logged at 10 Hz over 30 seconds
- ✅ navEPH = 200 cm (2 meters) - constant
- ✅ navEPV = 500-1000 cm (5-10 meters) - varies during climb

---

## Test Results

### Sample Data (climb profile, 30 seconds)

```
timestamp,elapsed,gps_altitude_m,navEPH_cm,navEPV_cm
1766861774.158735,0.000,0.0,1000,1000
1766861774.258958,0.100,0.5,200,715
1766861774.359460,0.201,1.0,200,918
...
1766861804.076810,29.918,100.0,200,587
```

### Statistics

```
          timestamp     elapsed  gps_altitude_m    navEPH_cm    navEPV_cm
count  2.990000e+02  299.000000      299.000000   299.000000   299.000000
mean   1.766862e+09   14.959395       66.522074   202.675585   711.107023
std    8.680110e+00    8.680117       33.475058    46.265195   139.401219
min    1.766862e+09    0.000000        0.000000   200.000000   500.000000
max    1.766862e+09   29.918000      100.000000  1000.000000  1000.000000
```

### navEPH Decoding

From `debug[7]` value:

```python
navEPV = debug[7] & 0x3FF           # Lower 10 bits
navEPH = (debug[7] >> 10) & 0x3FF   # Bits 10-19
flags  = (debug[7] >> 20) & 0x7F    # Bits 20-26
```

Example:
```
debug[7] = 1025000 (0x000fa3e8)
  → navEPV = 1000 cm (10.00 m)
  → navEPH = 1000 cm (10.00 m)
  → flags  = 0x00
```

---

## Usage

### Quick Start

```bash
cd /home/raymorris/Documents/planes/inavflight

# 1. Start SITL (if not running)
cd inav/build_sitl
./bin/SITL.elf > /tmp/sitl.log 2>&1 &
sleep 10

# 2. Configure SITL
python3 claude/test_tools/inav/sitl/sitl_arm_test.py 5760

# 3. Run navEPH logging
python3 claude/test_tools/inav/gps/gps_with_naveph_logging_mspapi2.py \
    --profile climb \
    --duration 60 \
    --output /tmp/naveph_climb.csv \
    --query-rate 10
```

### Profiles

- **climb**: 0m → 100m at 5 m/s
- **descent**: 100m → 0m at 2 m/s
- **hover**: constant 50m
- **sine**: oscillating ±30m around 50m

### Output Analysis

```bash
# View CSV
column -t -s, /tmp/naveph_climb.csv | less

# Statistics
python3 -c 'import pandas as pd; df=pd.read_csv("/tmp/naveph_climb.csv"); print(df.describe())'

# Plot (requires matplotlib)
python3 -c '
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("/tmp/naveph_climb.csv")
fig, ax = plt.subplots(2, 1, figsize=(12, 8))
ax[0].plot(df["elapsed"], df["gps_altitude_m"], label="GPS Altitude")
ax[0].set_ylabel("Altitude (m)")
ax[0].legend()
ax[0].grid(True)
ax[1].plot(df["elapsed"], df["navEPH_cm"], label="navEPH", marker="o")
ax[1].plot(df["elapsed"], df["navEPV_cm"], label="navEPV", marker="x")
ax[1].set_xlabel("Time (s)")
ax[1].set_ylabel("Accuracy (cm)")
ax[1].legend()
ax[1].grid(True)
plt.tight_layout()
plt.savefig("/tmp/naveph_plot.png", dpi=150)
print("Plot saved to /tmp/naveph_plot.png")
'
```

---

## Technical Details

### MSP Command Codes

| Name | Code (hex) | Code (dec) | Purpose |
|------|------------|------------|---------|
| MSP2_INAV_DEBUG | 0x2019 | 8217 | Read debug[] array (8 × uint32) |
| MSP2_INAV_ANALOG | 0x2009 | 8201 | Read analog values (wrong code used initially) |
| MSP_DEBUG | 0x00FE | 254 | Read debug[] array (4 × uint16, MSPv1) |

### Debug Mode

For navEPH logging, must set `debug_mode = DEBUG_POS_EST` (20):

```python
# Via MSP
setting_name = b'debug_mode\0'
payload = setting_name + struct.pack('<B', 20)
api._serial.send(0x1004, payload)  # MSP2_COMMON_SET_SETTING
api._serial.send(250, b'')  # MSP_EEPROM_WRITE
```

### Firmware Reference

- MSP handler: `inav/src/main/fc/fc_msp.c:999-1003`
- Debug constants: `inav/src/main/build/debug.h:76` (DEBUG_POS_EST = 20)
- navEPH update: `inav/src/main/navigation/navigation_pos_estimator.c:840`

---

## Files

### Scripts

- **`gps_with_naveph_logging_mspapi2.py`**: Main script (FIXED)
- **`gps_with_rc_keeper.py`**: GPS injection without navEPH logging
- **`run_gps_blackbox_test.sh`**: Automated blackbox test wrapper

### Documentation

- **`README_GPS_BLACKBOX_TESTING.md`**: Blackbox logging guide
- **`MSP2_INAV_DEBUG_FIX.md`**: This file

---

## Lessons Learned

1. **Always use enum values from libraries** - Don't hardcode MSP command codes
2. **Verify MSP codes with raw socket tests** - Helps identify wrong handlers
3. **Check response length field** - MSP header contains actual payload length
4. **Test with fresh SITL instance** - Avoids state issues

---

## Future Work

### Blackbox Logging

Alternative investigation paths:
1. **Serial blackbox** - Use `blackbox_device = SERIAL` instead of FILE
2. **Fix SITL blackbox FILE** - Debug why only 15ms decodes correctly
3. **Hardware testing** - Use real flight controller

### MSP2_INAV_DEBUG Applications

Now that MSP2_INAV_DEBUG works reliably, can be used for:
- Real-time position estimator monitoring
- GPS accuracy investigation
- Navigation algorithm tuning
- Flight mode debugging

---

## References

- INAV MSP Protocol: `mspapi2/docs/GETTING_STARTED.md`
- MSP Command Reference: https://github.com/iNavFlight/inav/wiki/MSP-V2
- Position Estimator: `inav/src/main/navigation/navigation_pos_estimator.c`
- Debug Modes: `inav/src/main/build/debug.h`
