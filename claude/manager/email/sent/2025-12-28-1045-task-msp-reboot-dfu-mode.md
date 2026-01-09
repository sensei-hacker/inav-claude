# Task Assignment: Add MSP Reboot Parameter for DFU Mode

**Date:** 2025-12-28 10:45
**Project:** MSP Reboot DFU Enhancement
**Priority:** MEDIUM
**Estimated Effort:** 4-6 hours
**Branch:** From `maintenance-9.x`

## Task

Add a parameter to the MSP reboot command to trigger DFU (Device Firmware Update) mode directly. Update documentation and related skills to reflect this new capability.

## Background

Currently, rebooting to DFU mode requires:
1. Serial command sequence: `####\r\n` → wait for CLI → `dfu\r\n`
2. Hardware button press during power-up
3. CLI command `dfu`

Adding MSP support would provide a cleaner, more reliable method for tools and scripts to trigger DFU mode programmatically.

## What to Do

### 1. Firmware Changes

**Use the /git-workflow skill** to manage branches:
```bash
/git-workflow
# Create feature branch from maintenance-9.x
```

**Add MSP reboot parameter:**
- Locate the MSP reboot command handler in `src/main/fc/fc_msp.c`
- Find MSP_REBOOT implementation
- Add an optional parameter to specify reboot type:
  - `0` or no parameter = normal reboot (backwards compatible)
  - `1` or specific value = reboot to DFU mode
- Ensure backwards compatibility with existing MSP clients

**Implementation guidance:**
- Check how other MSP commands handle optional parameters
- The reboot command may need to trigger the same sequence as the CLI `dfu` command
- Look at `src/main/fc/cli.c` for the `dfu` command implementation
- Ensure the DFU mode is properly entered before reboot

### 2. Testing with mspapi2

**Use mspapi2 to test the new functionality:**

```bash
cd ~/Documents/planes/inavflight/mspapi2

# Test normal reboot (backwards compatibility)
python3 -c "
from mspapi2 import MSPDevice
msp = MSPDevice('/dev/ttyACM0')
msp.connect()
# Send MSP_REBOOT with no parameter
msp.send_reboot()  # or however it's implemented
"

# Test DFU reboot
python3 -c "
from mspapi2 import MSPDevice
msp = MSPDevice('/dev/ttyACM0')
msp.connect()
# Send MSP_REBOOT with DFU parameter
msp.send_reboot(mode=1)  # or similar
"

# Verify device enters DFU mode
dfu-util -l
```

**Test both:**
- Normal reboot works (backwards compatibility)
- DFU reboot enters DFU mode successfully
- Device appears in `dfu-util -l` after DFU reboot

### 3. Update DFU Skills

Update the following skill files in `.claude/skills/flash-firmware-dfu/`:

**File: `.claude/skills/flash-firmware-dfu/SKILL.md`**

Add a new method section after line 68 (after the "####\r\n" method):

```markdown
### Method D: MSP Reboot Command

**Using MSP to reboot to DFU (requires INAV 9.x or later):**

```python
# Using mspapi2
from mspapi2 import MSPDevice

msp = MSPDevice('/dev/ttyACM0')
msp.connect()
msp.send_reboot(mode=1)  # Reboot to DFU mode
msp.disconnect()

# Wait a moment for reboot
import time
time.sleep(2)
```

This is the most reliable programmatic method as it:
- Doesn't require CLI prompt timing
- Works through the MSP protocol
- Is supported by configurator and tools
```

**Consider creating:** `.claude/skills/flash-firmware-dfu/reboot-to-dfu-msp.py`

A Python helper script using mspapi2:
```python
#!/usr/bin/env python3
"""Reboot flight controller to DFU mode using MSP"""
import sys
from mspapi2 import MSPDevice

if len(sys.argv) < 2:
    print("Usage: reboot-to-dfu-msp.py <device>")
    sys.exit(1)

device = sys.argv[1]
msp = MSPDevice(device)
msp.connect()
print(f"Rebooting {device} to DFU mode...")
msp.send_reboot(mode=1)
msp.disconnect()
print("Reboot command sent. Device should enter DFU mode.")
```

### 4. Update Documentation

**File: `inav/docs/USB Flashing.md`**

Update lines 69-78 to replace the old method with the proper sequence:

**Current content (lines 69-78):**
```markdown
Put the device into DFU mode by **one** of the following:

* Use the hardware button on the board
* Send a single 'R' character to the serial device, e.g. on POSIX OS using `/dev/ttyACM0` at 115200 baudrate.

```
stty 115200 < /dev/ttyACM0
echo -ne 'R' > /dev/ttyACM0
```
* Use the CLI command `dfu`
```

**Replace with:**
```markdown
Put the device into DFU mode by **one** of the following:

* **Hardware button:** Press and hold the DFU/BOOT button while plugging in USB
* **Serial CLI sequence:** Send `####\r\n`, wait for CLI prompt, then send `dfu\r\n`

```bash
# Enter CLI mode
echo -ne '####\r\n' > /dev/ttyACM0

# Wait for "CLI" prompt (important - don't skip!)
# Recommended: use a proper script that reads serial response

# Send DFU command
echo -ne 'dfu\r\n' > /dev/ttyACM0
```

**Note:** The simple single 'R' character method shown in older documentation is unreliable. The above sequence is required for proper CLI entry.

* **CLI command:** If already connected to CLI via configurator or terminal: type `dfu`
* **MSP command:** Use MSP_REBOOT with DFU parameter (INAV 9.x+) - most reliable programmatic method
```

**Key changes:**
- Remove the unreliable 'R' character method
- Show the proper `####\r\n` → wait → `dfu\r\n` sequence
- Add note about waiting for CLI prompt being important
- Mention the new MSP reboot method
- Make it clear which method is most reliable for scripts

### 5. Create Pull Request

**Use the /create-pr skill:**

```bash
/create-pr
```

**PR Title:** "Add MSP reboot parameter for DFU mode"

**PR Description template:**
```markdown
## Summary
- Add optional parameter to MSP_REBOOT command to trigger DFU mode
- Update USB Flashing documentation with proper serial sequence
- Add MSP reboot method as recommended approach for tools

## Changes
- Modified MSP_REBOOT handler to accept DFU mode parameter
- Updated `docs/USB Flashing.md` with correct CLI sequence
- Backwards compatible: no parameter = normal reboot

## Testing
- [x] Normal reboot works (backwards compatibility)
- [x] DFU reboot enters DFU mode successfully
- [x] Verified with mspapi2
- [x] Device appears in `dfu-util -l` after DFU reboot

## Motivation
Provides a reliable programmatic method for tools to trigger DFU mode without:
- Race conditions from CLI timing
- Manual hardware button presses
- Complex serial command sequences

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Success Criteria

- [ ] MSP reboot command accepts optional DFU mode parameter
- [ ] Backwards compatible: existing MSP clients still work
- [ ] DFU mode reboot tested successfully with mspapi2
- [ ] Normal reboot tested successfully (backwards compat)
- [ ] Device enters DFU mode and appears in `dfu-util -l`
- [ ] `.claude/skills/flash-firmware-dfu/SKILL.md` updated with MSP method
- [ ] Optional: Python helper script created using mspapi2
- [ ] `inav/docs/USB Flashing.md` lines 69-78 updated
- [ ] Documentation shows proper `####\r\n` → wait → `dfu\r\n` sequence
- [ ] Documentation mentions MSP reboot method
- [ ] PR created from `maintenance-9.x` branch
- [ ] PR description complete with testing checklist
- [ ] All builds passing in CI

## Files to Check

**Firmware:**
- `inav/src/main/fc/fc_msp.c` - MSP command handlers
- `inav/src/main/fc/cli.c` - CLI `dfu` command (reference implementation)
- `inav/src/main/msp/msp_protocol.h` - MSP message definitions

**Documentation:**
- `inav/docs/USB Flashing.md` - Lines 69-78 specifically
- `.claude/skills/flash-firmware-dfu/SKILL.md` - Add MSP method
- `.claude/skills/flash-firmware-dfu/reboot-to-dfu-msp.py` - New script (optional)

**Testing:**
- `~/Documents/planes/inavflight/mspapi2/` - Test with mspapi2 library

## Notes

**Branch:** Use `maintenance-9.x` base branch - this is backwards compatible enhancement

**MSP Protocol:** Ensure the parameter encoding follows INAV MSP conventions

**Backwards Compatibility Critical:** Existing MSP clients (configurator, etc.) send MSP_REBOOT with no parameter - this MUST still work as normal reboot.

**Testing Requirements:**
1. Build firmware for your test board
2. Flash with DFU
3. Test normal MSP reboot (no parameter)
4. Test DFU MSP reboot (with parameter)
5. Verify `dfu-util -l` shows device after DFU reboot

**Optional Enhancement:** If time permits, you could also update `reboot-to-dfu.py` to use the new MSP method when available, falling back to serial CLI method for older firmware.

**Documentation Style:** The USB Flashing.md file is user documentation - keep it clear and concise. The skill documentation can be more detailed for developer use.

---
**Manager**
