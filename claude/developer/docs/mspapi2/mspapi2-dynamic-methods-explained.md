# mspapi2: Dynamic Method Generation Explained

## Overview

**mspapi2** is a modern Python library for MSP (MultiWii Serial Protocol) communication with INAV/Betaflight flight controllers. Unlike traditional libraries that hardcode every MSP message, mspapi2 uses **schema-driven dynamic generation** to support all 249 MSP messages from a single JSON schema file.

## How Dynamic Generation Works

### 1. The MSP Message Schema (`msp_messages.json`)

At the heart of mspapi2 is a comprehensive JSON schema file that defines all MSP messages:

```json
{
    "MSP_API_VERSION": {
        "code": 1,
        "mspv": 1,
        "request": null,
        "reply": {
            "payload": [
                {
                    "name": "mspProtocolVersion",
                    "ctype": "uint8_t",
                    "desc": "MSP Protocol version",
                    "units": ""
                },
                {
                    "name": "apiVersionMajor",
                    "ctype": "uint8_t",
                    "desc": "INAV API Major version",
                    "units": ""
                },
                {
                    "name": "apiVersionMinor",
                    "ctype": "uint8_t",
                    "desc": "INAV API Minor version",
                    "units": ""
                }
            ]
        }
    },
    "MSP_FC_VARIANT": {
        "code": 2,
        "mspv": 1,
        "request": null,
        "reply": {
            "payload": [
                {
                    "name": "fcVariantIdentifier",
                    "desc": "4-character identifier string (e.g., \"INAV\")",
                    "ctype": "char",
                    "array": true,
                    "array_size": 4
                }
            ]
        }
    }
    // ... 247 more messages
}
```

**Key information in schema:**
- **code**: MSP command code (numeric)
- **request**: Payload structure for requests (if any)
- **reply**: Payload structure for replies (if any)
- **Field definitions**: name, C type (uint8_t, int16_t, etc.), array info

**Total messages defined:** 249

### 2. Dynamic Enum Generation (`InavMSP`)

When mspapi2 loads, it **dynamically creates an IntEnum** from the schema:

```python
# From mspcodec.py line 38-70
def _load_multiwii_enum(schema_path: Path) -> type[enum.IntEnum]:
    with schema_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    members: Dict[str, int] = {}
    for name, node in data.items():
        code = int(node.get("code"))
        members[name] = code

    return enum.IntEnum("InavMSP", members)

# Automatically executed at module load:
InavMSP = _load_multiwii_enum(Path(__file__).with_name("lib") / "msp_messages.json")
```

**Result:** You can now access all MSP codes by name:

```python
from mspapi2 import InavMSP

print(InavMSP.MSP_API_VERSION)      # 1
print(InavMSP.MSP_ATTITUDE)         # 108
print(InavMSP.MSP_RAW_GPS)          # 106
print(InavMSP.MSP_NAV_STATUS)       # 121
# ... and 245 more!
```

### 3. Dynamic Pack/Unpack (`MSPCodec`)

The `MSPCodec` class reads the schema and can **pack/unpack ANY message** without hardcoding:

```python
from mspapi2 import MSPCodec, InavMSP

# Load codec with schema
codec = MSPCodec.from_json_file('msp_messages.json')

# Unpack a reply - codec reads schema to know structure
raw_bytes = b'\x00\x02\x08'
result = codec.unpack_reply(InavMSP.MSP_API_VERSION, raw_bytes)
# Returns: {
#   'mspProtocolVersion': 0,
#   'apiVersionMajor': 2,
#   'apiVersionMinor': 8
# }

# Pack a request - codec reads schema to know structure
data = {'channelValue': [1500, 1500, 1000, 1500]}
packed = codec.pack_request(InavMSP.MSP_SET_RAW_RC, data)
```

**How it works:**
1. Codec loads schema into `MessageSpec` objects
2. Each `MessageSpec` contains:
   - Field names
   - C types (uint8_t, int16_t, float, etc.)
   - Struct format string (e.g., `"<HHH"` for 3 uint16_t values)
3. When you call `pack_request()` or `unpack_reply()`:
   - Codec looks up the message spec
   - Uses Python's `struct` module with the format string
   - Automatically packs/unpacks based on schema

### 4. High-Level API Methods (`MSPApi`)

While the codec handles ANY message, `MSPApi` provides **convenience methods** for common operations:

```python
from mspapi2 import MSPApi

api = MSPApi(port="/dev/ttyACM0", baudrate=115200)
api.open()

# Convenience method - manually defined
info, version = api.get_api_version()
# Internally calls: self._request(InavMSP.MSP_API_VERSION)

# Another convenience method
info, attitude = api.get_attitude()
# Returns: {'roll': -2.5, 'pitch': 1.3, 'heading': 178}

# These methods add value beyond raw codec:
# - Unit conversions (raw IMU → degrees)
# - Data formatting (bytes → strings)
# - Error handling
# - Metadata (latency, caching info)
```

**MSPApi provides ~40 high-level methods** for common tasks, but you can also:

```python
# Use low-level access for ANY message
info, raw_data = api._request(InavMSP.MSP_WHATEVER)
```

## Three Levels of Access

### Level 1: Convenience Methods (Recommended)
```python
from mspapi2 import MSPApi

api = MSPApi(port="/dev/ttyACM0")
api.open()
info, version = api.get_api_version()
info, gps = api.get_raw_gps()
```

**Features:**
- Type hints
- Unit conversions
- Friendly data structures
- ~40 common operations

### Level 2: Dynamic Codec (Any Message)
```python
from mspapi2 import MSPCodec, InavMSP, MSPSerial

codec = MSPCodec.from_json_file('msp_messages.json')
serial = MSPSerial('/dev/ttyACM0', 115200)
serial.open()

# Send any message by code
code, payload = serial.request(int(InavMSP.MSP_CUSTOM_MESSAGE), b'')
data = codec.unpack_reply(InavMSP.MSP_CUSTOM_MESSAGE, payload)
```

**Features:**
- Access to ALL 249 messages
- Schema-driven (no hardcoding)
- Lower-level control

### Level 3: Raw Bytes
```python
from mspapi2 import MSPSerial

serial = MSPSerial('/dev/ttyACM0', 115200)
serial.open()

# Send raw MSP message
code, payload = serial.request(1, b'')  # MSP_API_VERSION
print(payload.hex())
```

## Key Advantages

### 1. **No Hardcoding**
- Traditional approach: Write a class/function for each MSP message
- mspapi2 approach: Define in JSON, code handles it automatically

### 2. **Easy Updates**
- Add new MSP message: Edit JSON schema
- Old approach: Write new code for each message

### 3. **Complete Coverage**
- Supports ALL 249 MSP messages
- Many libraries only implement common ones

### 4. **Type Safety**
- Enum prevents typos: `InavMSP.MSP_API_VERSION` vs magic number `1`
- Schema validates field names and types

### 5. **Self-Documenting**
- Schema includes descriptions, units, C types
- Can generate documentation from schema

## Practical Examples

### Example 1: Get Flight Controller Info
```python
from mspapi2 import MSPApi

with MSPApi(port="/dev/ttyACM0", baudrate=115200) as api:
    # Convenience methods
    info, version = api.get_api_version()
    print(f"API Version: {version['apiVersionMajor']}.{version['apiVersionMinor']}")

    info, variant = api.get_fc_variant()
    print(f"FC Variant: {variant['fcVariantIdentifier']}")

    info, board = api.get_board_info()
    print(f"Board: {board['boardIdentifier']}")
```

### Example 2: Read GPS Data
```python
from mspapi2 import MSPApi

with MSPApi(port="/dev/ttyACM0", baudrate=115200) as api:
    info, gps = api.get_raw_gps()
    print(f"GPS Fix: {gps['fixType']}")
    print(f"Satellites: {gps['numSat']}")
    print(f"Position: {gps['lat']}, {gps['lon']}")
    print(f"Altitude: {gps['alt']}m")
    print(f"Speed: {gps['speed']} cm/s")
```

### Example 3: Set Waypoint Using Enums
```python
from mspapi2 import MSPApi
from mspapi2.lib import InavEnums

with MSPApi(port="/dev/ttyACM0", baudrate=115200) as api:
    info, _ = api.set_waypoint(
        waypointIndex=0,
        action=InavEnums.navWaypointActions_e.NAV_WP_ACTION_WAYPOINT,
        latitude=37.123456,
        longitude=-122.123456,
        altitude=50.0,
        flag=0,
    )
    print(f"Waypoint set (latency: {info['latency_ms']}ms)")
```

### Example 4: Check Navigation State
```python
from mspapi2 import MSPApi
from mspapi2.lib import InavEnums, InavMSP

with MSPApi(port="/dev/ttyACM0", baudrate=115200) as api:
    info, status = api.get_nav_status()

    # Use enums for readable comparisons
    if status["navState"] == InavEnums.navigationFSMState_t.NAV_FSM_HOLD_INFINITELY:
        print("Aircraft is holding position")

    if status["navError"] != InavEnums.navSystemStatus_Error_e.NAV_ERROR_NONE:
        print(f"Navigation error: {status['navError'].name}")
```

### Example 5: Direct Codec Usage (Any Message)
```python
from mspapi2 import MSPCodec, InavMSP, MSPSerial

# For messages without convenience methods
codec = MSPCodec.from_json_file('mspapi2/lib/msp_messages.json')
serial = MSPSerial('/dev/ttyACM0', 115200)
serial.open()

# Access ANY message dynamically
code, payload = serial.request(int(InavMSP.MSP_BOXIDS), b'')
data = codec.unpack_reply(InavMSP.MSP_BOXIDS, payload)
print(f"Box IDs: {data['boxIds']}")

serial.close()
```

## Architecture Summary

```
┌─────────────────────────────────────────────────┐
│         msp_messages.json (Schema)              │
│  - Defines all 249 MSP messages                 │
│  - Field names, types, descriptions             │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│       InavMSP Enum (Auto-generated)             │
│  - MSP_API_VERSION = 1                          │
│  - MSP_ATTITUDE = 108                           │
│  - ... 247 more                                 │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│         MSPCodec (Dynamic Pack/Unpack)          │
│  - pack_request(code, data) -> bytes            │
│  - unpack_reply(code, bytes) -> dict            │
│  - Uses schema to pack/unpack ANY message       │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│           MSPSerial (Transport)                 │
│  - request(code, payload) -> (code, reply)      │
│  - Handles serial/TCP communication             │
│  - MSP v1/v2 protocol framing                   │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│         MSPApi (High-Level Helpers)             │
│  - get_api_version() -> dict                    │
│  - get_attitude() -> dict                       │
│  - set_waypoint(...) -> dict                    │
│  - ~40 convenience methods                      │
│  - Plus access to ALL messages via codec        │
└─────────────────────────────────────────────────┘
```

## Why This Matters

### Traditional Approach (uNAVlib, other libraries):
```python
# Hardcoded for each message
class MSPy:
    def MSP_API_VERSION(self):
        # Hardcoded pack/unpack logic
        return self.send_RAW_msg(MSPCodes['MSP_API_VERSION'], ...)

    def MSP_ATTITUDE(self):
        # More hardcoded logic
        return self.send_RAW_msg(MSPCodes['MSP_ATTITUDE'], ...)

    # Need to write code for EVERY message
```

### mspapi2 Approach:
```python
# Schema-driven
codec = MSPCodec.from_json_file('msp_messages.json')

# Works for ANY message in schema
data1 = codec.unpack_reply(InavMSP.MSP_API_VERSION, bytes)
data2 = codec.unpack_reply(InavMSP.MSP_ATTITUDE, bytes)
data3 = codec.unpack_reply(InavMSP.MSP_ANYTHING, bytes)
```

**Result:**
- Less code
- Easier maintenance
- Complete coverage
- Schema is documentation

## Contributing

The library author welcomes PRs! If you find issues or want to add features:
- GitHub: https://github.com/xznhj8129/mspapi2
- The schema file can be extended
- New convenience methods can be added to MSPApi
- Improvements to codec, transport, or server welcome

## Summary

**mspapi2's dynamic generation:**

1. **Schema file** (`msp_messages.json`) defines all 249 MSP messages
2. **Dynamic enum** (`InavMSP`) auto-generated from schema at import time
3. **Dynamic codec** (`MSPCodec`) packs/unpacks ANY message using schema
4. **Convenience layer** (`MSPApi`) provides typed helpers for common tasks
5. **Complete flexibility** - use high-level API or drop to codec for any message

