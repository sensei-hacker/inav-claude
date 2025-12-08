---
description: Look up MSP protocol commands, packet formats, and implementations
triggers:
  - msp protocol
  - msp command
  - lookup msp
  - what is MSP_
  - find msp command
  - msp packet format
  - search msp
  - msp definition
---

# MSP Protocol Reference

Look up MultiWii Serial Protocol (MSP) command definitions, packet structures, and implementations in INAV.

## MSP Packet Structure

All MSP packets follow this format:

```
Header: '$' 'M' '<'/'>'  (3 bytes)
Size:   payload length   (1 byte)
Command: MSP command ID  (1 byte)
Data:   command payload  (0-255 bytes)
CRC:    checksum         (1 byte)
```

**Direction indicators:**
- `$M<` - Request (to flight controller)
- `$M>` - Response (from flight controller)

**Minimum packet size:** 6 bytes (for commands with no data payload)

## Finding MSP Commands

### In Firmware (C code)

MSP commands are defined in:
- **Command IDs:** `inav/src/main/msp/msp_protocol.h`
- **Command handlers:** `inav/src/main/msp/msp.c`
- **Serial processing:** `inav/src/main/msp/msp_serial.c`

**Search for command definitions:**
```bash
grep "MSP_COMMAND_NAME" inav/src/main/msp/msp_protocol.h
```

**Search for command handlers:**
```bash
grep -r "MSP_COMMAND_NAME" inav/src/main/msp/
```

### In Configurator (JavaScript)

MSP commands are used in:
- **MSP client:** `inav-configurator/src/js/msp/`
- **MSP definitions:** `inav-configurator/src/js/msp.js` or similar
- **Tab implementations:** `inav-configurator/src/js/tabs/`

**Search for MSP usage:**
```bash
grep -r "MSP_COMMAND_NAME" inav-configurator/src/js/
```

### In uNAVlib (Python MSP Library)

**IMPORTANT:** The **uNAVlib** library provides a Python MSP implementation for testing and automation.

**Location:** `uNAVlib/`

**Key features:**
- MSP packet encoding/decoding
- Command definitions and helpers
- Serial and TCP communication
- Useful for testing, scripting, and automation
- Can communicate with both real hardware and SITL

**Search for MSP in uNAVlib:**
```bash
grep -r "MSP_" uNAVlib/
find uNAVlib -name "*msp*.py"
```

**Using uNAVlib for testing:**
- Send MSP commands to flight controller
- Automate configuration tasks
- Test MSP communication performance
- Debug MSP protocol issues

See `claude/test_tools/inav/` for example scripts using uNAVlib.

## Common MSP Commands

| Command | ID | Purpose | Data Size |
|---------|-----|---------|-----------|
| MSP_IDENT | 100 | Board identification | 0 (request), 7 (response) |
| MSP_STATUS | 101 | Flight status | 0 (request), 11 (response) |
| MSP_ATTITUDE | 108 | Roll/pitch/yaw angles | 0 (request), 6 (response) |
| MSP_ALTITUDE | 109 | Altitude data | 0 (request), 10 (response) |
| MSP_ANALOG | 110 | Battery/current | 0 (request), 7 (response) |

## MSP Response Sizes

When investigating MSP issues, note that:
- Commands with `size=0` return no data payload (6-byte packet total)
- Most commands return small payloads (6-20 bytes typical)
- Large commands (settings, waypoints) can be 100+ bytes

## Debugging MSP

**Enable MSP debug logging in firmware:**

Edit `inav/src/main/msp/msp_serial.c` and add debug prints:
```c
fprintf(stderr, "[MSP_DEBUG] Command: %d, Size: %d\n", command, dataLen);
```

**Test MSP communication:**

Use the benchmark tools in `claude/test_tools/inav/`:
- `msp_benchmark_serial.py` - Test serial MSP
- `msp_benchmark_improved.py` - Test with detailed logging

Or use **uNAVlib** for interactive testing and automation.

## MSP Protocol Versions

- **MSP v1:** Original protocol (most common)
- **MSP v2:** Extended protocol with larger payloads and CRC32
- Check `msp_protocol.h` for version-specific commands

## Resources

- **Firmware MSP handlers:** `inav/src/main/msp/msp.c`
- **Protocol definitions:** `inav/src/main/msp/msp_protocol.h`
- **uNAVlib Python library:** `uNAVlib/` (for testing and automation)
- **Investigation notes:** `claude/msp_investigation_facts.md`
- **Test tools:** `claude/test_tools/inav/`

---

## Related Skills

- **sitl-arm** - Arm SITL using MSP protocol
- **build-sitl** - Build SITL firmware for MSP testing
- **find-symbol** - Find MSP command handlers and definitions in code
