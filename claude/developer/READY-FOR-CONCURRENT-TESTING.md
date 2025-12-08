# System Ready for Concurrent MSP + CRSF Testing

**Date:** 2025-12-07
**Status:** ✅ ALL SYSTEMS GO
**Developer:** Claude (Developer Role)

---

## Executive Summary

The INAV SITL system is fully configured and ready for concurrent operation of:
1. **GPS injection via MSP** (port 5760)
2. **CRSF telemetry monitoring** (port 5761)

All prerequisite configuration, testing, and validation is complete. Scripts are production-ready with confirmed port separation.

---

## Current System State

### SITL Status
```
Process: SITL.elf (PID 1599177)
Status: Running
Build: /home/raymorris/Documents/planes/inavflight/inav/build_sitl_crsf
Config: eeprom.bin (loaded successfully)
```

### Port Configuration
| Port  | Protocol | Status    | Configuration                          |
|-------|----------|-----------|----------------------------------------|
| 5760  | MSP      | LISTENING | UART1, available for GPS injection     |
| 5761  | CRSF     | LISTENING | UART2, RX_SERIAL, CRSF telemetry active|

### SITL Initialization Logs
```
[SOCKET] Bind TCP [::]:5760 to UART1
[SOCKET] Bind TCP [::]:5761 to UART2
[CRSF TELEM] initCrsfTelemetry called, crsfRxIsActive=1, enabled=1
[CRSF TELEM] Total 7 frames scheduled
[CRSF TELEM] handleCrsfTelemetry called, telemetry ENABLED
```

**Key indicators:**
- ✅ Both ports bound successfully
- ✅ CRSF RX active (crsfRxIsActive=1)
- ✅ Telemetry enabled (enabled=1)
- ✅ 7 telemetry frame types scheduled

---

## Production Scripts Ready

### 1. CRSF RC + Telemetry Script
**File:** `/home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/crsf/crsf_rc_sender.py`

**Protocol:** CRSF only (NO MSP)
**Port:** 5761 (UART2)
**Dependencies:** Standard Python libraries (socket, struct, time, sys, select)

**Verified characteristics:**
- ✅ No MSP imports (no uNAVlib usage)
- ✅ Uses raw TCP sockets only
- ✅ Connects exclusively to port 5761
- ✅ Sends RC frames at 50 Hz
- ✅ Receives telemetry frames at ~53.5 Hz
- ✅ Zero port conflicts with MSP

**Usage:**
```bash
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/crsf
python3 crsf_rc_sender.py 2 --rate 50 --duration 60 --show-telemetry
```

**Expected output:**
```
RC Frames Sent: 3000+ at 50 Hz
Telemetry Received: 3200+ frames
Frame types: ATTITUDE, BARO_ALT, BATTERY, FLIGHT_MODE, VARIO, UNKNOWN_0x0D
Stream Health: EXCELLENT (0% error rate)
```

---

### 2. GPS Altitude Injection Script
**File:** `/home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps/inject_gps_altitude.py`

**Protocol:** MSP only
**Port:** 5760 (UART1)
**Dependencies:** uNAVlib (MSP library)

**Features:**
- Uses MSP_SET_RAW_GPS command
- Supports multiple altitude profiles (climb, descent, oscillate)
- Configurable update rate
- No conflicts with CRSF port

**Usage:**
```bash
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps
python3 inject_gps_altitude.py --profile climb --duration 60
```

**Profiles:**
- `climb`: Gradual altitude increase (simulates climbing aircraft)
- `descent`: Gradual altitude decrease
- `oscillate`: Sinusoidal altitude changes
- `step`: Discrete altitude steps

---

### 3. CRSF Configuration Script
**File:** `/home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/crsf/configure_sitl_crsf.py`

**Purpose:** Configure UART2 for CRSF (one-time setup)

**Status:** Already executed, configuration persisted in eeprom.bin

**Re-run only if:** eeprom.bin is deleted or UART configuration is lost

---

### 4. Telemetry Feature Enable Script
**File:** `/home/raymorris/Documents/planes/inavflight/claude/developer/test_tools/enable_telemetry_feature.py`

**Purpose:** Enable TELEMETRY feature flag (bit 10)

**Status:** Already executed, feature enabled (0x20400C06)

**Re-run only if:** eeprom.bin is deleted or feature flag is disabled

---

## Port Separation Verification

### CRSF Script Analysis
**Source code review confirms:**
```python
# Line 309: Port calculation
port = 5760 + (uart_num - 1)  # UART2 = 5761

# Line 313: Socket creation (no MSP)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Line 323: Connection
sock.connect(('127.0.0.1', port))  # Only connects to 5761
```

**Imports used:**
- `socket` - Raw TCP/IP
- `struct` - Binary packing
- `time` - Timing
- `sys` - System operations
- `select` - Non-blocking I/O

**NO MSP-RELATED IMPORTS** - Zero possibility of MSP port access

### GPS Script Analysis
**Uses uNAVlib for MSP:**
```python
# Lines 19-21
sys.path.insert(0, '/home/raymorris/Documents/planes/inavflight/uNAVlib')
from unavlib.main import MSPy
from unavlib.enums.msp_codes import MSPCodes
```

**Connects to MSP port only:**
```python
# Connects to port 5760 via MSPy context manager
with MSPy(device="5760", use_tcp=True) as board:
    # GPS injection operations
```

**Conclusion:** Complete port separation guaranteed. No conflicts possible.

---

## Test Scenarios Ready

### Scenario 1: Concurrent Operation (Basic)
**Objective:** Verify GPS injection and CRSF telemetry work simultaneously

**Terminal 1 - GPS Injection:**
```bash
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps
python3 inject_gps_altitude.py --profile climb --duration 60
```

**Terminal 2 - CRSF Telemetry:**
```bash
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/crsf
python3 crsf_rc_sender.py 2 --rate 50 --duration 60 --show-telemetry
```

**Expected result:**
- GPS altitude increases over 60 seconds
- CRSF telemetry shows altitude changes
- Both scripts run without errors
- No port conflicts

---

### Scenario 2: Dynamic Sensor Response
**Objective:** Monitor telemetry response to rapid altitude changes

**Terminal 1 - Oscillating GPS:**
```bash
python3 inject_gps_altitude.py --profile oscillate --duration 120
```

**Terminal 2 - Telemetry Monitor:**
```bash
python3 crsf_rc_sender.py 2 --rate 50 --duration 120 --show-telemetry | tee /tmp/telemetry_response.log
```

**Expected result:**
- Altitude oscillates sinusoidally
- Telemetry frames reflect altitude changes
- BARO_ALT and VARIO frames show correlated changes
- Response captured in log file

---

### Scenario 3: Stress Test
**Objective:** High-frequency GPS updates with continuous telemetry

**Terminal 1 - Fast GPS Updates:**
```bash
python3 inject_gps_altitude.py --profile climb --rate 10 --duration 300
# 10 Hz GPS updates for 5 minutes
```

**Terminal 2 - Telemetry Monitor:**
```bash
python3 crsf_rc_sender.py 2 --rate 50 --duration 300 --show-telemetry
```

**Expected result:**
- GPS updated 10 times per second
- Telemetry continues at 50 Hz
- System remains stable
- No errors or crashes

---

## Verification Checklist

Before running concurrent tests, verify:

- [x] SITL running (`pgrep -a SITL.elf`)
- [x] Port 5760 listening (`ss -tlnp | grep 5760`)
- [x] Port 5761 listening (`ss -tlnp | grep 5761`)
- [x] CRSF telemetry enabled (check SITL logs)
- [x] eeprom.bin exists and loaded
- [x] No active connections to either port (`ss -tnp | grep -E "5760|5761"`)
- [x] CRSF script has no MSP imports (verified via source code)
- [x] GPS script uses MSP only (verified via source code)

**Status:** ✅ ALL CHECKS PASSED

---

## Quick Start Commands

### Start from scratch (if SITL not running):

```bash
# 1. Start SITL
cd /home/raymorris/Documents/planes/inavflight/inav/build_sitl_crsf
./bin/SITL.elf > /tmp/sitl.log 2>&1 &

# 2. Wait for startup
sleep 5

# 3. Verify ports
ss -tlnp | grep -E "5760|5761"

# 4. Check SITL logs
tail -20 /tmp/sitl.log
```

### Run concurrent test:

**Terminal 1:**
```bash
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/gps
python3 inject_gps_altitude.py --profile climb --duration 60
```

**Terminal 2:**
```bash
cd /home/raymorris/Documents/planes/inavflight/claude/test_tools/inav/crsf
python3 crsf_rc_sender.py 2 --rate 50 --duration 60 --show-telemetry
```

---

## Documentation References

**Detailed baseline documentation:**
- `/home/raymorris/Documents/planes/inavflight/claude/developer/crsf-telemetry-baseline-complete.md`

**Key sections:**
- MSP communication pattern (critical for uNAVlib usage)
- CRSF protocol details
- Troubleshooting guide
- Performance characteristics
- Setup procedures

---

## Known Limitations

1. **Single TCP connection per port** - Only ONE client can connect to each port at a time
2. **CRSF is bidirectional** - RC sender script handles both TX and RX on same socket
3. **MSP requires receive_msg()** - All MSP commands must call receive_msg() after send
4. **SITL restart timing** - After MSP_REBOOT, wait 15 seconds before reconnecting

These are design characteristics, not bugs. Scripts are designed to work within these constraints.

---

## Success Criteria

For concurrent testing to be considered successful:

1. **GPS injection:**
   - Altitude values accepted by SITL
   - No MSP errors or timeouts
   - Clean connection handling

2. **CRSF telemetry:**
   - RC frames sent at target rate (50 Hz)
   - Telemetry frames received at ~53.5 Hz
   - Zero CRC errors
   - All expected frame types present

3. **Concurrent operation:**
   - Both scripts run simultaneously without errors
   - No port conflicts or connection refused errors
   - Altitude changes visible in telemetry data
   - System remains stable throughout test

4. **Data correlation:**
   - GPS altitude changes reflected in BARO_ALT telemetry frames
   - Climb/descent rates visible in VARIO telemetry frames
   - Timing relationship between injection and telemetry response

---

## Next Steps

1. **Execute Scenario 1** - Basic concurrent operation test
2. **Validate data correlation** - Confirm GPS changes appear in telemetry
3. **Execute Scenario 2** - Dynamic sensor response with oscillating profile
4. **Analyze results** - Document telemetry response characteristics
5. **Execute Scenario 3** - Stress test with high-frequency updates

---

## Status Summary

| Component                | Status      | Notes                                    |
|--------------------------|-------------|------------------------------------------|
| SITL                     | ✅ READY    | Running, ports listening, telemetry on   |
| Port 5760 (MSP)          | ✅ FREE     | Available for GPS injection              |
| Port 5761 (CRSF)         | ✅ FREE     | Available for RC + telemetry             |
| CRSF Configuration       | ✅ COMPLETE | Persisted in eeprom.bin                  |
| TELEMETRY Feature        | ✅ ENABLED  | Bit 10 set (0x20400C06)                  |
| CRSF RC Script           | ✅ VERIFIED | No MSP deps, port separation confirmed   |
| GPS Injection Script     | ✅ READY    | MSP only, no CRSF conflicts              |
| Port Separation          | ✅ VERIFIED | Source code analysis confirms safety     |
| Documentation            | ✅ COMPLETE | Baseline and readiness docs available    |

---

**SYSTEM STATUS: ✅ READY FOR CONCURRENT MSP + CRSF TESTING**

All prerequisites met. All scripts verified. No blockers identified.

Proceed with test execution.
