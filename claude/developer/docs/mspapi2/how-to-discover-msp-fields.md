# How to Discover MSP Message Fields in mspapi2

## Quick Answer

**Yes!** mspapi2 provides multiple ways to discover what fields/parameters are in any MSP message.

## Method 1: Use the Introspection Tools (Easiest)

I've created `msp_introspection_tools.py` with helper functions:

```python
from msp_introspection_tools import print_message_info
from mspapi2 import InavMSP

# See all details about a message
print_message_info(InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE)
```

**Output:**
```
======================================================================
MSP2_INAV_LOGIC_CONDITIONS_SINGLE
======================================================================
Code:        8251
MSP Version: 2

--- REQUEST ---
  conditionIndex       uint8_t
    → Index of the condition to retrieve (0 to `MAX_LOGIC_CONDITIONS - 1`)

--- REPLY ---
  enabled              uint8_t
    → Boolean: 1 if enabled
  activatorId          int8_t
    → Activator ID (-1/255 if none)
  operation            uint8_t           (enum: logicOperation_e)
    → Enum `logicOperation_e` Logical operation
  ...
```

### Search for Messages

```python
from msp_introspection_tools import print_all_messages

# Find all LOGIC-related messages
print_all_messages("LOGIC")

# Output:
# MSP2_INAV_LOGIC_CONDITIONS                 = 8226
# MSP2_INAV_LOGIC_CONDITIONS_SINGLE          = 8251
# MSP2_INAV_LOGIC_CONDITIONS_STATUS          = 8230
# MSP2_INAV_SET_LOGIC_CONDITIONS             = 8227
```

### Get Field Names Programmatically

```python
from msp_introspection_tools import get_message_info
from mspapi2 import InavMSP

info = get_message_info(InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE)

# Get just the field names
request_fields = info['request']['field_names']
reply_fields = info['reply']['field_names']

print("Request needs:", request_fields)
# ['conditionIndex']

print("Reply contains:", reply_fields)
# ['enabled', 'activatorId', 'operation', 'operandAType', ...]
```

## Method 2: Access the Codec Directly

```python
from mspapi2 import MSPCodec, InavMSP

codec = MSPCodec.from_json_file('mspapi2/lib/msp_messages.json')

# Get the message spec
spec = codec._specs[InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE]

# Field names
print("Request fields:", spec.request.field_names)
print("Reply fields:", spec.reply.field_names)

# Full field details
for field in spec.reply.fields:
    print(f"{field['name']}: {field['ctype']} - {field.get('desc', '')}")
```

## Method 3: Read the JSON Schema Directly

```bash
# Using jq (command line)
jq '.MSP2_INAV_LOGIC_CONDITIONS_SINGLE' mspapi2/mspapi2/lib/msp_messages.json

# Or in Python
import json

with open('mspapi2/mspapi2/lib/msp_messages.json') as f:
    schema = json.load(f)

msg = schema['MSP2_INAV_LOGIC_CONDITIONS_SINGLE']
print("Reply fields:", [f['name'] for f in msg['reply']['payload']])
```

## Method 4: Discover at Runtime (After Getting Reply)

```python
from msp_introspection_tools import discover_reply_fields
from mspapi2 import MSPApi, InavMSP

with MSPApi(port="/dev/ttyACM0") as api:
    # Get a reply
    request = api._pack_request(
        InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE,
        {"conditionIndex": 0}
    )
    info, reply = api._request(InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE, request)

    # See what's in the reply
    discover_reply_fields(reply)
```

**Output:**
```
--- Reply contains these fields ---
  enabled              : int                  = 1
  activatorId          : int                  = -1
  operation            : int                  = 0
  operandAType         : int                  = 0
  operandAValue        : int                  = 0
  operandBType         : int                  = 0
  operandBValue        : int                  = 0
  flags                : int                  = 0
```

## Method 5: Just Try It and Let Python Tell You

```python
from mspapi2 import MSPApi, InavMSP

with MSPApi(port="/dev/ttyACM0") as api:
    request = api._pack_request(
        InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE,
        {"conditionIndex": 0}
    )
    info, reply = api._request(InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE, request)

    # Just print it!
    print(reply)
    # {'enabled': 1, 'activatorId': -1, 'operation': 0, ...}

    # Or use dict.keys()
    print("Available fields:", list(reply.keys()))
```

## Practical Workflow

Here's how I typically discover message fields:

### Step 1: Search for the message

```python
from msp_introspection_tools import print_all_messages

# What messages deal with logic conditions?
print_all_messages("LOGIC")
```

### Step 2: Get field details

```python
from msp_introspection_tools import print_message_info
from mspapi2 import InavMSP

# What fields does this message have?
print_message_info(InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE)
```

### Step 3: Write the code

Now you know:
- Request needs: `{"conditionIndex": uint8_t}`
- Reply contains: `enabled, activatorId, operation, ...`
- Which fields are enums: `operation`, `operandAType`, `operandBType`
- Which fields are bitmasks: `flags`

```python
from mspapi2 import MSPApi, InavMSP
from mspapi2.lib import InavEnums

with MSPApi(port="/dev/ttyACM0") as api:
    request = api._pack_request(
        InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE,
        {"conditionIndex": 0}  # ← You know this from print_message_info()
    )

    info, reply = api._request(InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE, request)

    # You know which fields to access and which are enums
    condition = {
        "enabled": bool(reply["enabled"]),
        "operation": InavEnums.logicOperation_e(reply["operation"]),
        "operandAType": InavEnums.logicOperandType_e(reply["operandAType"]),
        "operandAValue": reply["operandAValue"],
        # ... etc
    }
```

## Summary

**Ways to discover MSP message fields:**

1. ✅ **Use introspection tools** - `print_message_info(code)` - easiest
2. ✅ **Access codec specs** - `codec._specs[code].reply.field_names`
3. ✅ **Read JSON schema** - `jq '.MSP_MESSAGE' msp_messages.json`
4. ✅ **Runtime discovery** - `discover_reply_fields(reply)`
5. ✅ **Just try it** - Print the reply dict

**The library makes it easy!** You don't need to guess - the schema tells you everything:
- Field names
- Data types (uint8_t, int32_t, etc.)
- Which fields are enums
- Which fields are bitmasks
- Descriptions and units
- Array sizes

All of this information is in `msp_messages.json` and accessible via the introspection tools! 🎉
