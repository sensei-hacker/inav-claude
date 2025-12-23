# mspapi2 Logic Conditions Examples

This directory contains example scripts demonstrating how to use mspapi2 to fetch INAV Logic Conditions, specifically using `MSP2_INAV_LOGIC_CONDITIONS_SINGLE`.

## Background

See **[mspapi2-dynamic-methods-explained.md](./mspapi2-dynamic-methods-explained.md)** for a complete explanation of how mspapi2's schema-driven architecture works.

## Examples

### 1. Simple Example: `fetch_logic_condition_simple.py`

**Best for:** Understanding the basic pattern

A minimal example showing how to fetch a single logic condition using the codec directly:

```bash
python3 fetch_logic_condition_simple.py
```

**What it demonstrates:**
- The three-step pattern for accessing ANY MSP message:
  1. Pack request data: `api._pack_request(code, data_dict)`
  2. Send request: `api._request(code, payload)`
  3. Process reply: Convert enums, format values
- How to use `InavEnums` for readable output
- Minimal code focusing on core concepts

**Code snippet:**
```python
# Pack the request with condition index
request_payload = api._pack_request(
    InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE,
    {"conditionIndex": 0}
)

# Send request and get reply
info, reply = api._request(
    InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE,
    request_payload
)

# Process reply
condition = {
    "enabled": bool(reply["enabled"]),
    "operation": InavEnums.logicOperation_e(reply["operation"]),
    # ... more fields
}
```

### 2. Full Example: `fetch_logic_conditions_example.py`

**Best for:** Production use and learning best practices

A comprehensive example with proper argument parsing, error handling, and formatting:

```bash
# Fetch single condition via serial
python3 fetch_logic_conditions_example.py --condition-index 0

# Fetch all conditions
python3 fetch_logic_conditions_example.py --all

# Use TCP connection (e.g., to msp_server.py)
python3 fetch_logic_conditions_example.py --tcp localhost:9000 --condition-index 0

# Different serial port
python3 fetch_logic_conditions_example.py --port /dev/ttyACM1 --all
```

**What it demonstrates:**
- Command-line argument parsing
- TCP vs serial connection options
- Fetching single condition vs all conditions
- Pretty-printed output with enum names
- Proper error handling
- Connection context manager usage
- Formatting operands based on type
- Extracting and displaying flag bitmasks

## Why MSP2_INAV_LOGIC_CONDITIONS_SINGLE?

INAV supports two ways to fetch logic conditions:

| Message | Fetches | Use Case |
|---------|---------|----------|
| `MSP2_INAV_LOGIC_CONDITIONS` | All conditions at once | Initial load, full sync |
| `MSP2_INAV_LOGIC_CONDITIONS_SINGLE` | One condition by index | Update single condition, reduce bandwidth |

The SINGLE version is more efficient when you only need one condition, especially over slow links.

## Understanding Logic Conditions

Logic Conditions are part of INAV's Programming Framework (requires `USE_PROGRAMMING_FRAMEWORK`). They allow conditional logic like:

```
IF (RC_Channel_5 > 1700) AND (GPS_Fix == TRUE)
THEN Set_GVAR_0 = 1
```

**Each condition has:**
- **enabled**: Boolean on/off
- **activatorId**: Optional activator (another logic condition or -1 for none)
- **operation**: The logical operation (AND, OR, GREATER_THAN, etc.)
- **operandA**: First operand (type + value)
- **operandB**: Second operand (type + value)
- **flags**: Additional flags (bitmask)

**Operand types:**
- `VALUE`: Direct numeric value
- `RC_CHANNEL`: RC channel (1-18)
- `FLIGHT`: Flight parameter (RSSI, VBAT, altitude, etc.)
- `FLIGHT_MODE`: Flight mode check
- `LC`: Another logic condition
- `GVAR`: Global variable
- `PID`: PID value
- `WAYPOINTS`: Waypoint-related value

## The Pattern: Accessing Messages Without Convenience Methods

While `MSPApi` has ~40 convenience methods like `get_api_version()`, `get_attitude()`, etc., you can access **any of the 249 MSP messages** using the codec directly:

```python
# General pattern for ANY message
from mspapi2 import MSPApi, InavMSP

with MSPApi(port="/dev/ttyACM0") as api:
    # For messages that need request data:
    request_payload = api._pack_request(
        InavMSP.MSP_YOUR_MESSAGE,
        {"field1": value1, "field2": value2}
    )
    info, reply = api._request(InavMSP.MSP_YOUR_MESSAGE, request_payload)

    # For messages with no request payload:
    info, reply = api._request(InavMSP.MSP_YOUR_MESSAGE)

    # Reply is a dict with field names from schema
    print(reply)
```

**The codec automatically:**
- Looks up message structure in `msp_messages.json`
- Packs/unpacks using correct binary format
- Validates field names and types
- Returns structured dict (not raw bytes)

## Schema Reference

To see what fields a message has, check the schema:

```bash
# View MSP2_INAV_LOGIC_CONDITIONS_SINGLE structure
jq '.MSP2_INAV_LOGIC_CONDITIONS_SINGLE' mspapi2/lib/msp_messages.json

# List all available messages
jq 'keys' mspapi2/lib/msp_messages.json
```

Or use the `InavMSP` enum in Python:

```python
from mspapi2 import InavMSP

# See all available messages
for name in InavMSP.__members__:
    print(name, InavMSP[name].value)
```

## Related Documentation

- **[mspapi2-dynamic-methods-explained.md](./mspapi2-dynamic-methods-explained.md)** - How mspapi2's schema-driven architecture works
- **[mspapi2 README](../../mspapi2/README.md)** - Library documentation
- **INAV Wiki** - Logic Conditions programming guide

## Tips

1. **Use enums for readability**: Convert numeric enum values to `InavEnums.*` types
2. **Check the schema**: `jq '.MSP_MESSAGE_NAME' mspapi2/lib/msp_messages.json`
3. **Handle activatorId**: Value of 255 (0xFF) means "none"
4. **Parse flags**: Flags are bitmasks, use bitwise AND to check individual flags
5. **Use TCP for testing**: Connect to `msp_server.py` instead of direct serial

## Installation

```bash
cd mspapi2
pip install -e .
```

## Running Examples

```bash
# Make sure you're in the project root
cd /path/to/inavflight

# Run simple example
python3 claude/developer/fetch_logic_condition_simple.py

# Run full example
python3 claude/developer/fetch_logic_conditions_example.py --help
```
