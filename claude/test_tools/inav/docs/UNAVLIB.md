# uNAVlib - MSP Library for Python

## Overview

uNAVlib is a Python library for communicating with INAV/Betaflight flight controllers via the MSP (MultiWii Serial Protocol). It provides a clean API for sending commands and receiving telemetry.

We have our own copy of uNAVlib in the uNAVlib/ directory / repository. We can edit it.
## Installation

```bash
pip3 install git+https://github.com/xznhj8129/uNAVlib
```

## Repository

- GitHub: https://github.com/xznhj8129/uNAVlib
- Originally forked from YAMSPy (https://github.com/thecognifly/YAMSPy)

## Basic Usage

### Connecting to a Flight Controller

```python
from unavlib.main import MSPy

# Serial connection
with MSPy(device='/dev/ttyUSB0', loglevel='WARNING') as board:
    if board == 1:
        print("Connection failed")
    else:
        print(f"Connected to {board.CONFIG['flightControllerIdentifier']}")

# TCP connection (for SITL)
with MSPy(device='5761', use_tcp=True, loglevel='WARNING') as board:
    # device is the port number as a string
    pass
```

### Sending Raw MSP Messages

```python
# MSP code constants
MSP_SET_RAW_GPS = 201
MSP_COMP_GPS = 107
MSP_SET_RAW_RC = 200

# Send a message with payload
payload = [...]  # list of bytes
board.send_RAW_msg(MSP_SET_RAW_GPS, data=payload)

# Send a request (no payload)
board.send_RAW_msg(MSP_COMP_GPS, data=[])
```

### Receiving and Processing Messages

```python
# Receive and process a message
board.send_RAW_msg(MSP_COMP_GPS, data=[])
dataHandler = board.receive_msg()
board.process_recv_data(dataHandler)

# Access processed data
distance = board.GPS_DATA.get('distanceToHome', None)
direction = board.GPS_DATA.get('directionToHome', None)
```

### GPS Data Structures

After processing MSP_RAW_GPS or MSP_COMP_GPS:

```python
board.GPS_DATA = {
    'fix': int,              # 0=no fix, 1=2D, 2=3D
    'numSat': int,           # Number of satellites
    'lat': int,              # Latitude * 10^7
    'lon': int,              # Longitude * 10^7
    'alt': int,              # Altitude in meters
    'speed': int,            # Ground speed in cm/s
    'ground_course': int,    # Course in degrees * 10
    'hdop': int,             # HDOP * 100
    'distanceToHome': int,   # Distance to home in meters
    'directionToHome': int,  # Direction to home in degrees
    'update': int,           # Update flag
}
```

### Sending RC Channels

```python
# RC channel values (16 channels, 16-bit each)
channels = [1500, 1500, 1500, 1000, 1000, 1500, 1500, 1500,
            1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]

# Convert to bytes
data = []
for ch in channels:
    data.extend([ch & 0xFF, (ch >> 8) & 0xFF])

board.send_RAW_msg(MSP_SET_RAW_RC, data=data)
```

## Key MSP Codes

From `unavlib/enums/msp_codes.py`:

| Code | Name | Description |
|------|------|-------------|
| 106 | MSP_RAW_GPS | Request GPS data |
| 107 | MSP_COMP_GPS | Request distance/direction to home |
| 200 | MSP_SET_RAW_RC | Send RC channel values |
| 201 | MSP_SET_RAW_GPS | Inject GPS data |
| 108 | MSP_ATTITUDE | Request attitude (roll/pitch/yaw) |
| 109 | MSP_ALTITUDE | Request altitude |

## Example: GPS Data Injection

```python
import struct
from unavlib.main import MSPy

def create_gps_payload(fix_type, num_sat, lat, lon, alt_m, ground_speed):
    """Create MSP_SET_RAW_GPS payload."""
    return list(struct.pack('<BBiiHH',
        fix_type,      # 0=no fix, 1=2D, 2=3D
        num_sat,       # number of satellites
        lat,           # latitude * 10^7
        lon,           # longitude * 10^7
        alt_m,         # altitude in meters
        ground_speed   # ground speed in cm/s
    ))

# Connect and inject GPS
with MSPy(device='5761', use_tcp=True, loglevel='WARNING') as board:
    if board != 1:
        # Inject GPS position (London)
        lat = int(51.5074 * 1e7)
        lon = int(-0.1278 * 1e7)

        payload = create_gps_payload(
            fix_type=2,
            num_sat=12,
            lat=lat,
            lon=lon,
            alt_m=100,
            ground_speed=0
        )
        board.send_RAW_msg(201, data=payload)
```

## Notes

- The library logs to `MSPy.log` by default
- Set `loglevel='WARNING'` to reduce log verbosity
- TCP connections use `use_tcp=True` with device as port string
- Serial connections auto-detect baud rate (default 115200)
- The library handles MSP v1 and v2 protocols automatically

## Installed Location

```
Installed in ~/.local/lib/python3.10/site-packages/unavlib/
Editable copy in ~/Documents/inavflight/uNAVlib/ 
```

Key files:
- `main.py` - Main MSPy class
- `enums/msp_codes.py` - MSP code definitions
- `modules/process.py` - Message processing handlers

---

## Related Skills

- **msp-protocol** - MSP protocol reference and command definitions
- **sitl-arm** - Example scripts using uNAVlib to arm SITL
- **build-sitl** - Build SITL for MSP testing with uNAVlib
