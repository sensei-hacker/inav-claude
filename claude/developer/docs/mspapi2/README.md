# mspapi2 Documentation

Complete documentation and examples for using **mspapi2** - a modern, schema-driven Python library for MSP (MultiWii Serial Protocol) communication with INAV/Betaflight flight controllers.

## 📚 Documentation Files

### Core Concepts

**[mspapi2-dynamic-methods-explained.md](./mspapi2-dynamic-methods-explained.md)** (14 KB)
- **Start here!** Complete explanation of how mspapi2 works
- Schema-driven architecture overview
- Dynamic enum and codec generation
- Three levels of API access
- Architecture diagrams
- Comparison with traditional hardcoded approaches

### Practical Guides

**[how-to-discover-msp-fields.md](./how-to-discover-msp-fields.md)** (6.4 KB)
- How to discover what fields/parameters a message has
- 5 different methods with examples
- Practical workflow for working with new messages
- Using the introspection tools

**[mspapi2-examples-README.md](./mspapi2-examples-README.md)** (6 KB)
- Guide to the example scripts
- Command-line usage
- Understanding Logic Conditions
- The pattern for accessing messages without convenience methods

## 🛠️ Tools & Examples

### Introspection Tools

**[msp_introspection_tools.py](./msp_introspection_tools.py)** (8.1 KB)
```bash
# Discover what fields a message has
python3 msp_introspection_tools.py

# Or use programmatically:
from msp_introspection_tools import print_message_info
from mspapi2 import InavMSP

print_message_info(InavMSP.MSP2_INAV_LOGIC_CONDITIONS_SINGLE)
```

**Functions provided:**
- `print_message_info(code)` - Display message structure
- `get_message_info(code)` - Get info dict programmatically
- `print_all_messages(filter)` - Search for messages
- `list_all_messages(filter)` - Get message list
- `get_schema_raw(name)` - Read JSON schema directly
- `discover_reply_fields(reply)` - Inspect reply dict

### Example Scripts

**[fetch_logic_condition_simple.py](./fetch_logic_condition_simple.py)** (2.6 KB)
```bash
# Minimal example showing the core pattern
python3 fetch_logic_condition_simple.py
```

**What it demonstrates:**
- The 3-step pattern for accessing ANY MSP message
- Pack request → Send request → Process reply
- Converting enums for readability
- Minimal code focusing on core concepts

**[fetch_logic_conditions_example.py](./fetch_logic_conditions_example.py)** (7.8 KB)
```bash
# Full-featured example with CLI options
python3 fetch_logic_conditions_example.py --help
python3 fetch_logic_conditions_example.py --condition-index 0
python3 fetch_logic_conditions_example.py --all
python3 fetch_logic_conditions_example.py --tcp localhost:9000
```

**What it demonstrates:**
- Command-line argument parsing (serial/TCP, single/all)
- Pretty-printed output with proper formatting
- Operand type formatting
- Flag bitmask extraction
- Error handling and connection management
- Production-ready code structure

## 🚀 Quick Start

### 1. Understand How It Works

Read: **[mspapi2-dynamic-methods-explained.md](./mspapi2-dynamic-methods-explained.md)**

**Key concept:** mspapi2 uses a JSON schema (`msp_messages.json`) to dynamically handle ALL 249 MSP messages without hardcoding each one.

### 2. Learn to Discover Fields

Read: **[how-to-discover-msp-fields.md](./how-to-discover-msp-fields.md)**

**Key takeaway:** You never have to guess what fields a message has - use the introspection tools!

```python
# Quick example
from msp_introspection_tools import print_message_info
from mspapi2 import InavMSP

print_message_info(InavMSP.MSP_YOUR_MESSAGE)
# Shows: request fields, reply fields, types, enums, descriptions
```

### 3. Try the Examples

Start with the simple example:
```bash
python3 fetch_logic_condition_simple.py
```

Then explore the full example:
```bash
python3 fetch_logic_conditions_example.py --help
```

### 4. Apply the Pattern to Any Message

The **3-step pattern** works for ANY of the 249 MSP messages:

```python
from mspapi2 import MSPApi, InavMSP

with MSPApi(port="/dev/ttyACM0") as api:
    # Step 1: Pack request (use introspection to know fields!)
    request = api._pack_request(
        InavMSP.MSP_YOUR_MESSAGE,
        {"field1": value1, "field2": value2}
    )

    # Step 2: Send request
    info, reply = api._request(InavMSP.MSP_YOUR_MESSAGE, request)

    # Step 3: Process reply
    # reply is a dict with field names from schema
    print(reply)
```

## 📋 Documentation Structure

```
claude/developer/docs/mspapi2/
├── README.md (this file)
│
├── Core Documentation:
│   ├── mspapi2-dynamic-methods-explained.md  ← How it works
│   ├── how-to-discover-msp-fields.md         ← Finding field info
│   └── mspapi2-examples-README.md            ← Example guide
│
├── Tools:
│   └── msp_introspection_tools.py            ← Field discovery
│
└── Examples:
    ├── fetch_logic_condition_simple.py       ← Basic pattern
    └── fetch_logic_conditions_example.py     ← Full example
```

## 💡 Key Concepts

### Schema-Driven Design

Instead of hardcoding methods for each MSP message, mspapi2:
1. Loads `msp_messages.json` schema
2. Dynamically creates `InavMSP` enum with all message codes
3. Uses `MSPCodec` to pack/unpack ANY message based on schema
4. Provides `MSPApi` convenience methods for common operations

**Result:** Access to ALL 249 messages with minimal code!

### Three Levels of Access

1. **High-level convenience methods** (easiest)
   ```python
   api = MSPApi(port="/dev/ttyACM0")
   info, version = api.get_api_version()
   ```

2. **Dynamic codec** (any message)
   ```python
   request = api._pack_request(InavMSP.MSP_ANYTHING, data)
   info, reply = api._request(InavMSP.MSP_ANYTHING, request)
   ```

3. **Raw bytes** (full control)
   ```python
   serial = MSPSerial("/dev/ttyACM0", 115200)
   code, payload = serial.request(123, b'\x00\x01')
   ```

### Introspection Tools

**Never guess what fields a message has!** Use:

```python
from msp_introspection_tools import print_message_info
print_message_info(InavMSP.MSP_YOUR_MESSAGE)
```

This shows:
- Request field names and types
- Reply field names and types
- Which fields are enums
- Which fields are bitmasks
- Field descriptions and units

## 🔗 Related Documentation

- **mspapi2 Library README**: `../../mspapi2/README.md`
- **INAV MSP Schema**: `../../mspapi2/mspapi2/lib/msp_messages.json`
- **INAV Wiki**: Logic Conditions programming guide
- **Developer Guide**: `../README.md`

## 📦 Installation

```bash
cd /home/raymorris/Documents/planes/inavflight/mspapi2
pip install -e .
```

## ✨ Contributing

The library author welcomes PRs!
- GitHub: https://github.com/xznhj8129/mspapi2
- Extend the schema
- Add convenience methods to MSPApi
- Improve codec, transport, or server

---

**Questions?** See the documentation files above or check `../../mspapi2/README.md`
