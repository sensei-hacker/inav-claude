# Project: Improved Motor Wizard with DShot Beep Identification

**Status:** 📋 TODO
**Priority:** Medium
**Type:** Feature
**Created:** 2026-01-06
**Repositories:** inav-configurator, inav (firmware)

## Overview

Create a new, improved motor wizard that uses DShot beacon/beep commands to make individual motors beep, allowing users to identify motor positions by clicking on a visual diagram rather than manually selecting motor numbers from dropdowns.

## Problem

The current motor wizard in INAV Configurator (`tabs/mixer.html`) uses a dropdown-based approach where users must manually map motor positions (front-left, front-right, etc.) to motor numbers. This is error-prone and unintuitive. Users must spin up motors and visually identify which one is moving, then remember this when filling out the dropdown.

Betaflight has a superior approach using DShot beacon commands that make individual motors beep/chirp, allowing users to click on the corresponding position in a diagram. This is more intuitive and less error-prone.

## Objectives

1. **Firmware changes:** Add support for DShot beacon commands (DSHOT_CMD_BEACON1-5) to make individual motors beep
2. **MSP protocol:** Add MSP command to send DShot beacon commands to specific motors
3. **Configurator UI:** Create new wizard with interactive motor position clicking
4. **Confirmation phase:** After mapping all motors, cycle through and highlight positions while beeping to verify

## Scope

**In Scope:**
- Adding DSHOT_CMD_BEACON1-5 support to INAV firmware
- Adding MSP2_SEND_DSHOT_COMMAND or similar MSP command
- New motor wizard UI component in configurator
- Interactive SVG/PNG diagram for clicking motor positions
- Confirmation/verification phase
- i18n localization keys

**Out of Scope:**
- Changes to existing mixer logic
- Support for non-DShot protocols (feature requires DShot)
- Mobile/touch optimization

## Reference Implementation

### Betaflight Configurator
- `src/components/EscDshotDirection/EscDshotDirectionComponent.js` - Main wizard component
- `src/components/EscDshotDirection/EscDshotDirectionMotorDriver.js` - Motor control via MSP
- `src/components/EscDshotDirection/Body.html` - UI structure
- `src/js/utils/DshotCommand.js` - DShot command definitions

### Betaflight Firmware
- `src/main/drivers/dshot_command.h` - DShot command enum (BEACON1-5)
- `src/main/drivers/dshot_command.c` - Command execution logic
- `src/main/msp/msp_protocol_v2_betaflight.h` - MSP2_SEND_DSHOT_COMMAND (0x3003)
- `src/main/msp/msp.c:3572` - MSP command handler

### INAV Current State
- `inav/src/main/drivers/pwm_output.h:30-32` - Only has DSHOT_CMD_SPIN_DIRECTION_NORMAL/REVERSED
- `inav/src/main/drivers/pwm_output.c:399` - `sendDShotCommand()` function exists but limited
- `inav-configurator/tabs/mixer.html:216-279` - Current dropdown-based wizard
- `inav-configurator/tabs/mixer.js:594-656` - Wizard logic

### Motor Diagram Assets
- `inav-configurator/resources/motor_order/*.svg` - Existing motor position diagrams

## Implementation Steps

### Phase 1: Firmware - DShot Beacon Support
1. Add BEACON1-5 commands to `dshotCommands_e` enum in `pwm_output.h`
2. Update `getDShotCommandRepeats()` in `pwm_output.c` for beacon timing
3. Add ability to send command to individual motor (not all motors)

### Phase 2: Firmware - MSP Protocol
1. Add `MSP2_INAV_SEND_DSHOT_COMMAND` to `msp_protocol_v2_inav.h`
2. Implement handler in `fc_msp.c` following Betaflight's pattern
3. Handler accepts: command type, motor index, command list

### Phase 3: Configurator - DShot Command Support
1. Add DShot command codes to `js/msp/MSPCodes.js`
2. Add helper functions to send DShot commands via MSP
3. Create command queue mechanism similar to Betaflight

### Phase 4: Configurator - New Wizard UI
1. Create new motor wizard component/modal
2. Use existing motor order SVG assets
3. Interactive clicking on motor positions
4. Progress indicator showing current motor being identified
5. Audio feedback or visual cue when motor is beeping

### Phase 5: Wizard Logic
1. Cycle through motors one at a time (beep motor 1, wait for click...)
2. Map clicked position to motor index
3. Store mapping for mixer configuration
4. Confirmation phase: cycle through all positions, beep + highlight

### Phase 6: Integration
1. Replace or augment existing wizard trigger button
2. Check for DShot protocol requirement
3. Add proper error handling and user feedback
4. Add i18n keys for all new strings

## Success Criteria

- [ ] INAV firmware can send DShot beacon commands to individual motors
- [ ] MSP command exists to trigger motor beeps from configurator
- [ ] Wizard UI displays motor diagram and responds to clicks
- [ ] User can identify all motor positions by clicking where they hear beeping
- [ ] Confirmation phase correctly highlights and beeps each mapped motor
- [ ] Motor mapping is correctly applied to mixer configuration
- [ ] Works with quad, hex, and octo configurations
- [ ] Proper error handling when DShot not enabled

## Technical Notes

### DShot Beacon Commands
Standard DShot protocol defines commands 1-5 as beacon/beep commands with different tones:
- DSHOT_CMD_BEACON1 = 1
- DSHOT_CMD_BEACON2 = 2
- DSHOT_CMD_BEACON3 = 3
- DSHOT_CMD_BEACON4 = 4
- DSHOT_CMD_BEACON5 = 5

ESCs supporting DShot should respond to these with audible beeps.

### Per-Motor Commands
Unlike the current INAV implementation that sends commands to all motors, the new wizard needs to send beep commands to individual motors. This requires:
1. Firmware support for per-motor DShot command sending
2. MSP command that specifies target motor index

### Safety Considerations
- Motors must be stopped before sending DShot commands
- Aircraft must be disarmed
- User safety acknowledgment checkbox (like Betaflight)

## Dependencies

- Requires DShot-capable ESCs (most modern ESCs support this)
- Requires DShot protocol enabled in firmware
- Beacon commands are part of BLHeli_32/BLHeli_S spec
