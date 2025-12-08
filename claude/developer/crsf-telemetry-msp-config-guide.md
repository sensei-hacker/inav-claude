# CRSF Telemetry Configuration for SITL - MSP Method

## Summary

CRSF telemetry can be enabled in SITL using MSP configuration commands. The key is to follow the proper sequence when removing MSP from a UART and assigning it to Serial RX.

## Prerequisites

- SITL built with CRSF telemetry support (PR #11025 branch: `pr-11025-crsf-telem`)
- Debug instrumentation added to `src/main/telemetry/crsf.c` (optional but helpful)

## Configuration Sequence (CRITICAL ORDER)

**IMPORTANT:** You must perform these steps in this exact order:

### Step 1: Remove MSP from UART2

First, read the current serial configuration and remove FUNCTION_MSP from UART2:

```python
import struct
from unavlib.main import MSPy
from unavlib.enums.msp_codes import MSPCodes

with MSPy(device='5760', use_tcp=True, loglevel='WARNING') as board:
    # Read current config
    if board.send_RAW_msg(MSPCodes['MSP_CF_SERIAL_CONFIG'], data=[]):
        dataHandler = board.receive_msg()
        raw_data = dataHandler.get('dataView', [])

    # Modify UART2 to remove MSP (set to FUNCTION_NONE or 0)
    serial_config = [
        2,              # UART2 identifier
        0, 0, 0, 0,     # functionMask = 0 (no functions)
        0, 0, 0, 0      # baud rates
    ]

    if board.send_RAW_msg(MSPCodes['MSP_SET_CF_SERIAL_CONFIG'], data=serial_config):
        dataHandler = board.receive_msg()
```

### Step 2: Set UART2 to Serial RX

Now configure UART2 for SERIAL_RX function:

```python
    FUNCTION_RX_SERIAL = 0x40
    PERIPH_BAUD_420000 = 5

    serial_config = [
        2,                          # UART2 identifier
        FUNCTION_RX_SERIAL, 0, 0, 0,  # functionMask (little-endian)
        0, 0, 0,                    # unused baud rates
        PERIPH_BAUD_420000         # periph_baud for CRSF
    ]

    if board.send_RAW_msg(MSPCodes['MSP_SET_CF_SERIAL_CONFIG'], data=serial_config):
        dataHandler = board.receive_msg()
```

### Step 3: Configure RX Type and Protocol

Set the receiver type to SERIAL and protocol to CRSF:

```python
    SERIALRX_CRSF = 6
    RX_TYPE_SERIAL = 1

    rx_config = [
        SERIALRX_CRSF,              # provider = CRSF
        0x6C, 0x07,                 # maxcheck = 1900
        0xDC, 0x05,                 # midrc = 1500
        0x4C, 0x04,                 # mincheck = 1100
        0,                          # spektrum_sat_bind
        0x75, 0x03,                 # rx_min_usec = 885
        0x43, 0x08,                 # rx_max_usec = 2115
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # padding (11 bytes)
        RX_TYPE_SERIAL              # receiverType = SERIAL
    ]

    if board.send_RAW_msg(MSPCodes['MSP_SET_RX_CONFIG'], data=rx_config):
        dataHandler = board.receive_msg()
```

### Step 4: Enable TELEMETRY Feature

Enable the TELEMETRY feature flag:

```python
    # Read current features
    if board.send_RAW_msg(MSPCodes['MSP_FEATURE_CONFIG'], data=[]):
        dataHandler = board.receive_msg()
        board.process_recv_data(dataHandler)

    current_features = board.FEATURE_CONFIG.get('featureMask', 0)
    FEATURE_TELEMETRY = 0x400  # Bit 10

    new_features = current_features | FEATURE_TELEMETRY
    data = struct.pack('<I', new_features)

    if board.send_RAW_msg(MSPCodes['MSP_SET_FEATURE_CONFIG'], data=list(data)):
        dataHandler = board.receive_msg()
```

### Step 5: Save and Reboot

**CRITICAL:** You MUST save to EEPROM and reboot for changes to take effect:

```python
    # Save configuration
    if board.send_RAW_msg(MSPCodes['MSP_EEPROM_WRITE'], data=[]):
        import time
        time.sleep(0.5)

    # Reboot SITL
    board.send_RAW_msg(MSPCodes['MSP_REBOOT'], data=[])
```

## Verification

After SITL reboots, check the debug output for:

```
[SOCKET] Bind TCP [::]:5760 to UART1
[SOCKET] Bind TCP [::]:5761 to UART2
[CRSF TELEM] initCrsfTelemetry called, crsfRxIsActive=1, enabled=1
[CRSF TELEM] Scheduled RPM frame (index 5)
[CRSF TELEM] Scheduled TEMP frame (index 6)
[CRSF TELEM] Total 7 frames scheduled
[CRSF TELEM] handleCrsfTelemetry called, telemetry ENABLED
```

**Key indicators:**
- `crsfRxIsActive=1` - CRSF RX is active
- `enabled=1` - Telemetry is enabled
- Both UART1 and UART2 are listening on their respective ports

## Common Mistakes

1. **Not removing MSP first:** Trying to add SERIAL_RX while MSP is still on the same UART won't work - you can't have both functions on the same port simultaneously.

2. **Not saving before reboot:** Configuration changes are only applied after MSP_EEPROM_WRITE + MSP_REBOOT.

3. **Wrong order:** The sequence matters - remove MSP, then add SERIAL_RX, then configure RX type/protocol, then save/reboot.

## Files Modified

### Debug Instrumentation (Optional)

Added to `src/main/telemetry/crsf.c`:

```c
// At top of file
#ifdef SITL_BUILD
#include <stdio.h>
#endif
#include "build/debug.h"

// In initCrsfTelemetry()
SD(fprintf(stderr, "[CRSF TELEM] initCrsfTelemetry called, crsfRxIsActive=%d, enabled=%d\n",
    crsfRxIsActive(), crsfTelemetryEnabled));

// In frame scheduling
SD(fprintf(stderr, "[CRSF TELEM] Scheduled RPM frame (index %d)\n", index-1));
SD(fprintf(stderr, "[CRSF TELEM] Scheduled TEMP frame (index %d)\n", index-1));

// In handleCrsfTelemetry()
if (!crsfTelemetryEnabled) {
    if (!debugOnce) {
        SD(fprintf(stderr, "[CRSF TELEM] handleCrsfTelemetry called but telemetry DISABLED\n"));
        debugOnce = true;
    }
    return;
}
```

### SITL Target Configuration

**File:** `src/main/target/SITL/target.h:101`

Ensure CRSF telemetry is enabled:
```c
// #undef USE_TELEMETRY_CRSF  // ENABLED FOR TESTING PR #11025
```

## Testing Telemetry

Once configured, you can test telemetry transmission:

1. Start CRSF RC sender (on UART2/port 5761):
```bash
python3 crsf_rc_sender.py 2 --rate 50
```

2. Monitor telemetry frames:
```bash
python3 crsf_stream_parser.py 2
```

Expected frames:
- 0x02: GPS
- 0x08: Battery Sensor
- 0x14: Link Statistics
- 0x1E: Attitude
- 0x0C: RPM (if ESC sensor active)
- 0x0D: Temperature (if temperature sensor active)

## Port Configuration

- **UART1 (TCP port 5760):** MSP (configurator connection)
- **UART2 (TCP port 5761):** CRSF RX + Telemetry

This allows simultaneous configurator access and CRSF telemetry testing.
