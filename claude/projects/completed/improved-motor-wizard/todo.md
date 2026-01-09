# Todo List: Improved Motor Wizard

## Phase 1: Research & Planning

- [ ] Review Betaflight wizard animation (https://oscarliang.com/wp-content/uploads/2023/01/betaflight-configurator-motor-order-animate-gif.webp)
- [ ] Study existing INAV mixer wizard implementation
- [ ] Study Betaflight EscDshotDirection component in detail
- [ ] Identify all required firmware changes
- [ ] Identify all required configurator changes
- [ ] Create detailed implementation plan

## Phase 2: Firmware - DShot Command Support

- [ ] Add DSHOT_CMD_BEACON1-5 to dshotCommands_e enum in pwm_output.h
- [ ] Update getDShotCommandRepeats() for beacon command timing
- [ ] Modify sendDShotCommand() to support per-motor commands (not just all motors)
- [ ] Add motor index parameter to DShot command sending
- [ ] Test beacon commands work on physical hardware

## Phase 3: Firmware - MSP Protocol

- [ ] Define MSP2_INAV_SEND_DSHOT_COMMAND in msp_protocol_v2_inav.h
- [ ] Implement MSP handler in fc_msp.c
  - [ ] Parse motor index
  - [ ] Parse command type (blocking vs inline)
  - [ ] Parse command sequence
  - [ ] Execute DShot commands
- [ ] Add safety checks (disarmed, motors stopped)
- [ ] Test MSP command via CLI or simple test

## Phase 4: Configurator - MSP Support

- [ ] Add MSP2_INAV_SEND_DSHOT_COMMAND to MSPCodes.js
- [ ] Create DshotCommand.js utility (like Betaflight)
- [ ] Create command queue mechanism for proper timing
- [ ] Add helper functions for sending motor commands
- [ ] Test MSP communication with firmware

## Phase 5: Configurator - UI Component

- [ ] Create new MotorWizard component directory
- [ ] Create HTML template with:
  - [ ] Safety warning and checkbox
  - [ ] Motor diagram display area
  - [ ] Progress indicator
  - [ ] Motor position buttons/clickable areas
  - [ ] Start/Stop/Confirm buttons
- [ ] Create CSS styles
- [ ] Create JavaScript component class
- [ ] Wire up i18n localization

## Phase 6: Wizard Logic Implementation

- [ ] Implement wizard state machine:
  - [ ] Initial state (safety warning)
  - [ ] Identification state (beeping motor, waiting for click)
  - [ ] Confirmation state (verifying mapping)
  - [ ] Complete state (apply mapping)
- [ ] Cycle through motors one at a time
- [ ] Send beacon command to current motor
- [ ] Detect and record user clicks on diagram
- [ ] Build motor position mapping
- [ ] Implement confirmation phase:
  - [ ] Highlight motor position on diagram
  - [ ] Beep corresponding motor
  - [ ] Cycle through all positions

## Phase 7: Integration

- [ ] Add wizard trigger button to mixer tab
- [ ] Check DShot protocol is enabled before allowing wizard
- [ ] Show appropriate error if DShot not configured
- [ ] Apply motor mapping to mixer rules
- [ ] Test with different frame types (quad, hex, octo)

## Phase 8: Polish & Documentation

- [ ] Add all i18n translation keys
- [ ] Test error handling scenarios
- [ ] Ensure proper cleanup on wizard close
- [ ] Add user-facing documentation/help text
- [ ] Code review and cleanup

## Completion

- [ ] All features working correctly
- [ ] Tests passing
- [ ] Code reviewed
- [ ] PR created for firmware changes
- [ ] PR created for configurator changes
- [ ] Send completion report to manager
