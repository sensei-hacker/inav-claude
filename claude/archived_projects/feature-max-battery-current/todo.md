# Todo List: Max Battery Current Limiter

## Phase 1: Firmware Implementation

- [ ] Research existing current sensor integration
  - [ ] Find current reading code location
  - [ ] Understand current sensor data flow
  - [ ] Identify motor mixer integration points
- [ ] Add setting to settings.yaml
  - [ ] Define `max_battery_current` in Battery group
  - [ ] Set appropriate min/max/default values
  - [ ] Add CLI documentation
- [ ] Implement current limiting logic
  - [ ] Add current monitoring in motor output path
  - [ ] Implement proportional scaling algorithm
  - [ ] Add hysteresis to prevent oscillation
  - [ ] Test for stability
- [ ] Add OSD element
  - [ ] Create "CURRENT LIMIT" indicator
  - [ ] Show current vs. limit percentage
  - [ ] Test OSD display

## Phase 2: Configurator Integration

- [ ] Update Battery tab UI
  - [ ] Add max_battery_current input field
  - [ ] Add help text/tooltip
  - [ ] Validate input range
  - [ ] Test UI functionality

## Phase 3: Testing & Validation

- [ ] SITL testing
  - [ ] Test with feature disabled (0)
  - [ ] Test with low limit (verify limiting activates)
  - [ ] Test with high limit (verify no limiting)
  - [ ] Verify smooth behavior (no oscillation)
- [ ] Real hardware testing (optional)
  - [ ] Test on bench with current sensor
  - [ ] Verify actual current limiting
  - [ ] Check for stability issues

## Phase 4: Documentation

- [ ] Update firmware documentation
  - [ ] Add setting description to docs
  - [ ] Explain behavior and use cases
  - [ ] Provide recommended values
- [ ] Update Configurator documentation
  - [ ] Screenshot of Battery tab
  - [ ] Configuration instructions

## Completion

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Create PR to maintenance-9.x
- [ ] Send completion report to manager
