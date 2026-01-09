# Task Assignment: Improved Motor Wizard with DShot Beep Identification

**Date:** 2026-01-06 23:40
**Project:** improved-motor-wizard
**Priority:** Medium
**Estimated Effort:** 8-12 hours (multi-phase project)
**Branch:** From `maintenance-10.x` (both inav and inav-configurator)

## Task

Create a new, improved motor wizard for INAV Configurator that uses DShot beacon commands to make individual motors beep, allowing users to identify motor positions by clicking on a visual diagram.

## Background

The current motor wizard in the Mixer tab uses a clunky dropdown-based approach where users must manually map motor positions to motor numbers. This requires spinning motors, observing which one moves, then remembering this while filling out dropdowns.

Betaflight has a much better approach: they send DShot beacon commands to make individual motors beep (chirp), and the user simply clicks on the diagram position where they hear the sound. This is more intuitive, safer (no motor spinning), and less error-prone.

**Video/GIF reference of Betaflight's approach:**
https://oscarliang.com/wp-content/uploads/2023/01/betaflight-configurator-motor-order-animate-gif.webp

## What to Do

### Step 1: Study Reference Implementations

1. Watch the Betaflight wizard animation linked above
2. Study the existing INAV mixer wizard:
   - `inav-configurator/tabs/mixer.html` (lines 216-279)
   - `inav-configurator/tabs/mixer.js` (lines 594-656)

3. Study Betaflight's implementation thoroughly:
   - `betaflight-configurator/src/components/EscDshotDirection/EscDshotDirectionComponent.js`
   - `betaflight-configurator/src/components/EscDshotDirection/EscDshotDirectionMotorDriver.js`
   - `betaflight-configurator/src/components/EscDshotDirection/Body.html`
   - `betaflight-configurator/src/js/utils/DshotCommand.js`
   - `betaflight/src/main/drivers/dshot_command.h` (DSHOT_CMD_BEACON1-5)
   - `betaflight/src/main/msp/msp.c:3572` (MSP2_SEND_DSHOT_COMMAND handler)

### Step 2: Firmware Changes (inav)

1. **Expand DShot commands** in `src/main/drivers/pwm_output.h`:
   ```c
   typedef enum {
       DSHOT_CMD_MOTOR_STOP = 0,
       DSHOT_CMD_BEACON1 = 1,
       DSHOT_CMD_BEACON2 = 2,
       DSHOT_CMD_BEACON3 = 3,
       DSHOT_CMD_BEACON4 = 4,
       DSHOT_CMD_BEACON5 = 5,
       // ... existing commands
       DSHOT_CMD_SPIN_DIRECTION_NORMAL = 20,
       DSHOT_CMD_SPIN_DIRECTION_REVERSED = 21,
   } dshotCommands_e;
   ```

2. **Add per-motor command support** - The current `sendDShotCommand()` sends to all motors. Need ability to send to individual motors.

3. **Add MSP command** - Create `MSP2_INAV_SEND_DSHOT_COMMAND` (pick appropriate code from inav's reserved range). Handler in `fc_msp.c` should:
   - Accept motor index (or 255 for all)
   - Accept command type (blocking/inline)
   - Accept one or more commands
   - Check safety (must be disarmed)

### Step 3: Configurator Changes (inav-configurator)

1. **Add DShot command utilities:**
   - Add MSP code to `js/msp/MSPCodes.js`
   - Create command queue mechanism for proper timing
   - Create helper functions for motor beep commands

2. **Create new Motor Wizard UI:**
   - Can reuse existing motor diagram SVGs from `resources/motor_order/`
   - Display current motor diagram based on mixer preset
   - Make motor positions clickable
   - Show progress (which motor is currently beeping)
   - Safety warning with checkbox before starting

3. **Implement wizard flow:**
   - **Identification phase:** For each motor (1 to N):
     - Send beacon command to motor N
     - Wait for user to click a position on diagram
     - Record mapping: motor N → clicked position
   - **Confirmation phase:** After all motors mapped:
     - Cycle through each position on diagram
     - Highlight the position
     - Beep the mapped motor
     - User verifies correct mapping
   - **Apply:** Update mixer motor rules with new mapping

### Step 4: Integration

1. Add wizard button to Mixer tab (near existing wizard button)
2. Check if DShot protocol is enabled - show error if not
3. Require disarmed state
4. Apply motor mapping to `FC.MOTOR_RULES`

## Success Criteria

- [ ] INAV firmware accepts DShot beacon commands (1-5) for individual motors
- [ ] MSP command allows configurator to trigger motor beeps
- [ ] New wizard UI displays motor diagram with clickable positions
- [ ] Wizard correctly cycles through motors, sending beacon commands
- [ ] User clicks are correctly mapped to motor positions
- [ ] Confirmation phase highlights positions and beeps corresponding motors
- [ ] Motor mapping is correctly applied to mixer configuration
- [ ] Proper error handling when DShot not enabled
- [ ] Works with quad, hex, and octo configurations

## Files to Check

### INAV Firmware
- `src/main/drivers/pwm_output.h` - DShot command enum
- `src/main/drivers/pwm_output.c` - sendDShotCommand() function
- `src/main/msp/msp_protocol_v2_inav.h` - MSP protocol definitions
- `src/main/fc/fc_msp.c` - MSP command handlers

### INAV Configurator
- `tabs/mixer.html` - Existing wizard markup
- `tabs/mixer.js` - Existing wizard logic
- `js/msp/MSPCodes.js` - MSP command codes
- `js/msp/MSPHelper.js` - MSP encoding/decoding
- `resources/motor_order/*.svg` - Motor diagrams

### Betaflight Reference (study these)
- `betaflight-configurator/src/components/EscDshotDirection/` - Complete wizard implementation
- `betaflight/src/main/drivers/dshot_command.h` - DShot commands
- `betaflight/src/main/msp/msp.c:3572` - MSP handler

## Notes

1. **Safety:** Motor beacon commands should only work when disarmed. Include safety checkbox in UI.

2. **DShot requirement:** This feature only works with DShot protocol. PWM/Oneshot/Multishot do not support beacon commands.

3. **ESC compatibility:** DSHOT beacon commands are standard in BLHeli_S and BLHeli_32. Most modern ESCs support this.

4. **Timing:** Beacon commands need proper timing. Study Betaflight's command queue implementation.

5. **Branch note:** Use `maintenance-10.x` for both repos since this adds new MSP commands (breaking change for older configurator versions).

6. **Project documentation:** See `claude/projects/improved-motor-wizard/summary.md` and `todo.md` for full details.

---
**Manager**
