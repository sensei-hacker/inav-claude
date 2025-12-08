# CRSF Telemetry SITL Testing - Findings and Lessons Learned

**Date:** 2025-12-06
**Task:** Test CRSF telemetry frames from PR #11025 using SITL
**Status:** Infrastructure complete, CRSF RX initialization needs investigation

---

## Executive Summary

Built complete CRSF testing infrastructure including RC frame generator and telemetry parser. Successfully configured SITL for CRSF via Configurator. Discovered that SITL CRSF RX requires additional setup beyond basic configuration - likely needs simulator integration or special initialization sequence.

### Key Discovery: MSP Configuration Requirements

**Critical finding:** CRSF configuration requires **TWO separate settings**:
1. **Receiver Type:** `RX_TYPE_SERIAL` (via MSP_SET_RX_CONFIG byte 23)
2. **Serial RX Provider:** `SERIALRX_CRSF` (via MSP_SET_RX_CONFIG byte 0)
3. **UART Function:** `FUNCTION_RX_SERIAL` (via MSP2_COMMON_SET_SERIAL_CONFIG)

Missing any of these prevents CRSF from activating.

### Key Discovery: eeprom.bin Persistence

**MSP_REBOOT is required** after MSP_EEPROM_WRITE for configuration to persist to disk.

Sequence:
```python
# 1. Configure settings
board.send_RAW_msg(MSPCodes['MSP2_COMMON_SET_SERIAL_CONFIG'], data=config_data)
board.send_RAW_msg(MSPCodes['MSP_SET_RX_CONFIG'], data=rx_config_data)

# 2. Save to EEPROM
board.send_RAW_msg(MSPCodes['MSP_EEPROM_WRITE'], data=[])
time.sleep(0.5)

# 3. REBOOT to persist (THIS IS REQUIRED!)
board.send_RAW_msg(MSPCodes['MSP_REBOOT'], data=[])
time.sleep(15)  # Wait for SITL to restart and initialize EEPROM
```

Without MSP_REBOOT, eeprom.bin file is not created.

---

## Tools Created

### 1. crsf_rc_sender.py (152 lines)
**Purpose:** Sends CRSF RC channel frames to SITL to stimulate CRSF RX

**Features:**
- Generates valid CRSF_FRAMETYPE_RC_CHANNELS_PACKED frames
- 16 channels, 11-bit encoding (172-1811 range)
- Configurable frame rate (default 50Hz - CRSF standard)
- CRC8 DVB-S2 validation

**Usage:**
```bash
python3 crsf_rc_sender.py 2 --rate 50 --duration 60
```

**Frame Structure:**
```
[Address: 0xC8][Length: 24][Type: 0x16][Payload: 22 bytes][CRC8]
```

### 2. crsf_stream_parser.py (216 lines)
**Purpose:** Captures and validates CRSF telemetry frames from SITL

**Features:**
- TCP connection to SITL UARTs
- Frame-by-frame parsing with CRC8 validation
- Boundary corruption detection
- Frame type identification
- Statistics reporting
- Detects new frames from PR #11025

**CRC8 Implementation:** Validated against:
- INAV source code (`src/main/common/crc.c:57-68`)
- TBS official CRSF specification
- Multiple reference implementations

**Usage:**
```bash
python3 crsf_stream_parser.py 2  # UART2
```

### 3. configure_sitl_crsf.py (Updated)
**Purpose:** Automated CRSF configuration via MSP

**Key Fix:** Added MSP_REBOOT after EEPROM_WRITE

**Status:** Sends correct MSP commands but CRSF RX doesn't fully initialize in SITL

---

## SITL Configuration Status

### ✅ Working Configuration (via INAV Configurator GUI)

**Settings Applied:**
1. Receiver Tab:
   - Receiver Type → **Serial**
   - Serial Receiver Provider → **CRSF**

2. Ports Tab:
   - UART2 → **Serial RX** (automatically set when receiver configured)

3. Result:
   - eeprom.bin created (32KB)
   - UART2 (port 5761) listening
   - Configuration persists across reboots

### ⚠️ Partial: MSP Configuration Script

**What Works:**
- MSP commands send successfully
- eeprom.bin created and loaded
- UART2 port binds

**What Doesn't Work:**
- CRSF RX doesn't fully initialize
- Connections to UART2 immediately disconnect
- No telemetry output

**Hypothesis:** SITL CRSF RX might require:
- Simulator connection sending CRSF frames
- Additional initialization sequence
- Special SITL flags or environment

---

## Testing Workflow Discovered

### Correct SITL CRSF Test Sequence

1. **Build SITL for target PR**
   ```bash
   cd inav
   git fetch origin pull/11025/head:pr-11025-crsf-telem
   git checkout pr-11025-crsf-telem
   mkdir build_sitl_pr11025 && cd build_sitl_pr11025
   cmake -DSITL=ON ..
   make -j4
   ```

2. **Configure CRSF (use Configurator - most reliable)**
   ```bash
   cd /path/to/inav-configurator
   npm start
   # Connect to localhost:5760
   # Receiver → Serial → CRSF
   # Save & Reboot
   ```

3. **Start SITL**
   ```bash
   cd build_sitl_pr11025
   ./bin/SITL.elf &
   ```

4. **Send CRSF RC frames** (triggers telemetry)
   ```bash
   python3 crsf_rc_sender.py 2 --rate 50 &
   ```

5. **Capture telemetry**
   ```bash
   python3 crsf_stream_parser.py 2
   ```

### Current Blocker

CRSF RX in SITL doesn't activate telemetry even when:
- ✅ Configuration saved correctly
- ✅ UART2 port listening
- ✅ Valid CRSF RC frames sent
- ✅ Connections established

**Next Investigation Steps:**
1. Check if SITL CRSF requires simulator (JSBSim/X-Plane) connection
2. Review SITL CRSF RX initialization code
3. Test with RX_TYPE_MSP instead (known working in sitl_arm_test.py)
4. Check if CRSF needs `--sim` parameter to SITL

---

## Code References

### INAV Source Files Analyzed

**rx/rx.h:62-67** - Receiver type enum:
```c
typedef enum {
    RX_TYPE_NONE = 0,
    RX_TYPE_SERIAL,    // Value: 1
    RX_TYPE_MSP,       // Value: 2
    RX_TYPE_SIM
} rxReceiverType_e;
```

**rx/rx.h:69-85** - Serial RX provider enum:
```c
typedef enum {
    SERIALRX_SPEKTRUM1024 = 0,
    SERIALRX_SPEKTRUM2048,
    SERIALRX_SBUS,
    SERIALRX_SUMD,
    SERIALRX_IBUS,
    SERIALRX_JETIEXBUS,
    SERIALRX_CRSF,         // Value: 6
    SERIALRX_FPORT,
    // ...
} rxSerialReceiverType_e;
```

**telemetry/crsf.c:654** - Telemetry activation check:
```c
void initCrsfTelemetry(void)
{
    // CRSF telemetry enabled only if CRSF RX is active
    crsfTelemetryEnabled = crsfRxIsActive();
    // ...
}
```

**rx/crsf.c:330-333** - RX active check:
```c
bool crsfRxIsActive(void)
{
    return serialPort != NULL;  // Serial port must be initialized
}
```

**telemetry/crsf.c:712** - Telemetry trigger:
```c
void handleCrsfTelemetry(timeUs_t currentTimeUs)
{
    if (!crsfTelemetryEnabled) {
        return;
    }
    crsfRxSendTelemetryData();  // Triggered by RX module
    // ...
}
```

**Key Insight:** CRSF telemetry is sent **by the RX module**, not independently. The RX must be receiving and parsing CRSF RC frames to trigger telemetry responses.

---

## MSP Protocol Constants

### MSP Commands Used

| Code | Name | Purpose |
|------|------|---------|
| 44 | MSP_RX_CONFIG | Read receiver configuration |
| 45 | MSP_SET_RX_CONFIG | Set receiver configuration |
| 4106 | MSP2_COMMON_SERIAL_CONFIG | Read serial port configuration |
| 4107 | MSP2_COMMON_SET_SERIAL_CONFIG | Set serial port configuration |
| 250 | MSP_EEPROM_WRITE | Save configuration to EEPROM |
| 68 | MSP_REBOOT | Reboot flight controller |

### MSP_SET_RX_CONFIG Payload (24 bytes)

```python
struct.pack('<BIBBBB',
    uart_id,           # byte 0: UART identifier (1 = UART2)
    function_mask,     # bytes 1-4: Function mask (64 = RX_SERIAL)
    msp_baud,          # byte 5: MSP baudrate index
    gps_baud,          # byte 6: GPS baudrate index
    telem_baud,        # byte 7: Telemetry baudrate index
    periph_baud        # byte 8: Peripheral baudrate index
)
```

### RX Config Structure (24 bytes)

| Byte | Field | CRSF Value |
|------|-------|------------|
| 0 | serialrx_provider | 6 (SERIALRX_CRSF) |
| 1-2 | maxcheck | 1900 |
| 3-4 | midrc | 1500 |
| 5-6 | mincheck | 1100 |
| 7 | spektrum_sat_bind | 0 |
| 8-9 | rx_min_usec | 885 |
| 10-11 | rx_max_usec | 2115 |
| 12-22 | (various, not critical) | - |
| 23 | **receiverType** | **1 (RX_TYPE_SERIAL)** |

---

## Frame Specifications

### CRSF RC Channels Frame (Type 0x16)

```
[Address: 0xC8]
[Length: 24]       # Type (1) + Payload (22) + CRC (1)
[Type: 0x16]       # RC_CHANNELS_PACKED
[Payload: 22 bytes] # 16 channels × 11 bits = 176 bits = 22 bytes
[CRC8]             # DVB-S2 over Type + Payload
```

**Channel Encoding:**
- Range: 172-1811 (11-bit)
- Midpoint: 992 (= 1500us)
- Formula: `value = (us - 1000) * 1.639 + 172`

### CRSF Telemetry Frames (from PR #11025)

**Baseline Frames:**
- 0x02: GPS (15 bytes)
- 0x07: VARIO (2 bytes)
- 0x08: BATTERY (8 bytes)
- 0x1E: ATTITUDE (6 bytes)

**New Frames (PR #11025):**
- **0x09: BAROMETER** (2 bytes) - Simple altitude
- **0x0A: AIRSPEED** (2 bytes) - Pitot sensor
- **0x0C: RPM** (variable) - ESC telemetry
- **0x0D: TEMPERATURE** (variable) - Up to 20 sensors

---

## Lessons Learned

### 1. MSP Configuration is Multi-Step

CRSF requires coordinated configuration across multiple subsystems:
- Receiver type (RX config)
- Serial provider (RX config)
- UART function (Serial config)

Missing any step results in silent failure.

### 2. MSP_REBOOT is Mandatory

`MSP_EEPROM_WRITE` alone is insufficient. The reboot:
- Triggers eeprom.bin file creation
- Persists configuration to disk
- Reinitializes all subsystems with new config

### 3. SITL CRSF RX is Complex

Unlike MSP receiver (RX_TYPE_MSP = 2), CRSF receiver requires:
- Valid CRSF RC frame parsing
- Proper frame timing (50Hz standard)
- Possibly simulator integration

### 4. CRC8 DVB-S2 is Iterative

```python
# WRONG: One-shot calculation
crc = crc8_dvb_s2(0, entire_payload)

# CORRECT: Byte-by-byte iteration
crc = 0
for byte in payload:
    crc = crc8_dvb_s2(crc, byte)
```

### 5. Static Functions Block Unit Testing

All CRSF frame generation functions in `telemetry/crsf.c` are `static`:
```c
static void crsfFrameGps(sbuf_t *dst)           // Line 222
static void crsfFrameVarioSensor(sbuf_t *dst)   // Line 241
static void crsfFrameAirSpeedSensor(sbuf_t *dst)// Line 308
```

Cannot be called from external unit tests. SITL/integration testing required.

### 6. CRSF Telemetry is Bidirectional

Telemetry is not autonomous - it's **triggered by the RX module** in response to receiving RC frames. Without valid RC input, no telemetry output.

---

## File Inventory

### Created Files

1. `/home/raymorris/Documents/planes/inavflight/inav/crsf_rc_sender.py` (152 lines)
2. `/home/raymorris/Documents/planes/inavflight/inav/crsf_stream_parser.py` (216 lines)
3. `/home/raymorris/Documents/planes/inavflight/inav/configure_sitl_crsf.py` (105 lines, updated)
4. `/home/raymorris/Documents/planes/inavflight/claude/developer/crsf-sitl-testing-findings.md` (this file)

### Modified Files (Temporary)

1. `cmake/sitl.cmake` - Lines 67-70 commented (linker fix for older ld versions)

### SITL Binary

1. `build_sitl_pr11025/bin/SITL.elf` (1.4MB)
2. `build_sitl_pr11025/eeprom.bin` (32KB, CRSF configured)

---

## Recommended Next Actions

### Short-term (Complete PR #11025 Testing)

1. **Test with Simulator Integration**
   - Connect SITL to JSBSim or X-Plane
   - Use simulator's RC input to trigger CRSF
   - Verify telemetry responses

2. **Alternative: Use RX_TYPE_MSP**
   - Configure RX as MSP instead of CRSF
   - Send MSP_SET_RAW_RC commands
   - Test if telemetry activates (likely will work based on sitl_arm_test.py)

3. **Debug CRSF RX Initialization**
   - Add debug logging to SITL CRSF RX code
   - Rebuild SITL with `-DDEBUG_CRSF`
   - Identify why serialPort not initializing

### Long-term (Improve CRSF Testing)

1. **Create SITL CRSF Skill**
   - Document complete setup procedure
   - Include all configuration steps
   - Add troubleshooting guide

2. **Contribute SITL CRSF Documentation**
   - Submit PR to INAV wiki
   - Help future developers

3. **Explore CRSF Unit Testing Alternatives**
   - Propose making frame functions non-static
   - Or create test-specific build target

---

## Skills to Create/Update

### New Skill: `test-crsf-sitl`

**Purpose:** Complete workflow for testing CRSF telemetry changes using SITL

**Content:**
- Build SITL for specific PR
- Configure CRSF (Configurator method)
- Run RC sender + telemetry parser
- Validate frame integrity
- Test missing sensor handling

### Update Skill: `sitl-arm`

**Add Section:** CRSF vs MSP Receiver Configuration

**Key Points:**
- MSP_REBOOT requirement after EEPROM_WRITE
- receiver_type + serialrx_provider both required
- CRSF needs RC input, MSP doesn't

---

## References

### Documentation
- [TBS CRSF Specification](https://github.com/tbs-fpv/tbs-crsf-spec/blob/main/crsf.md)
- [INAV SITL Documentation](https://github.com/iNavFlight/inav/blob/master/docs/SITL/SITL.md)

### INAV Source Files
- `src/main/rx/rx.h` - Receiver types and serial RX providers
- `src/main/rx/crsf.c` - CRSF RX implementation
- `src/main/telemetry/crsf.c` - CRSF telemetry implementation
- `src/main/io/serial.h` - Serial port function masks
- `src/main/common/crc.c` - CRC8 DVB-S2 implementation

### Reference Implementations
- [Arduino-CRSF](https://github.com/stepinside/Arduino-CRSF/)
- [CircuitPython-CRSF](https://github.com/kenken64/circuitpython-CRSF)
- [sitl_arm_test.py](../test_tools/sitl_arm_test.py) - Working MSP example

---

**Developer**
2025-12-06
