# Task Assignment: Max Battery Current Limiter

**Date:** 2025-12-16 18:45
**Project:** feature-max-battery-current
**Priority:** MEDIUM
**Estimated Effort:** 8-12 hours
**Branch:** From `maintenance-9.x`

## Task

Implement a `max_battery_current` setting that reduces motor output when the battery current exceeds the configured threshold. This protects batteries from excessive discharge current.

## Background

Users have requested a way to limit battery current draw to:
- Prevent exceeding battery C-rating
- Avoid voltage sag and brown-outs
- Extend battery lifespan
- Improve safety

This feature should integrate with existing current sensor infrastructure and provide smooth, predictable motor output reduction when the limit is exceeded.

## What to Do

### 1. Firmware Implementation (inav/)

**Add setting:**
- Location: `src/main/fc/settings.yaml`
- Group: Battery
- Name: `max_battery_current`
- Type: uint32 (milliamps)
- Range: 0 (disabled) to 200000 (200A)
- Default: 0 (disabled)

**Implement current limiting:**
- Find current sensor reading location
- Identify motor mixer/output code location
- Add current monitoring logic
- Implement proportional motor output scaling when current > limit
- Add hysteresis to prevent oscillation (e.g., activate at 100%, release at 90%)
- Ensure smooth behavior (no abrupt throttle cuts)

**Add OSD element:**
- Create "CURRENT LIMIT" indicator
- Show when limiting is active
- Optional: show current vs. limit percentage

**Files to check:**
- `src/main/fc/settings.yaml` (setting definition)
- `src/main/sensors/current.c` (current sensor reading)
- `src/main/flight/mixer.c` or `src/main/flight/pid.c` (motor output)
- `src/main/io/osd.c` (OSD element)

### 2. Configurator Integration (inav-configurator/)

**Update Battery tab:**
- Add input field for `max_battery_current`
- Unit: Amps (convert to/from milliamps)
- Range validation: 0-200A
- Help text explaining feature
- Position near existing current sensor configuration

**Files to check:**
- Battery tab HTML/JavaScript files
- Settings framework integration

### 3. Testing

**SITL Testing:**
- Test with feature disabled (0)
- Test with low limit (verify limiting activates)
- Test with high limit (verify no limiting)
- Verify smooth behavior (no oscillation)
- Check OSD indicator works

**Optional hardware testing:**
- Bench test with current sensor if available

### 4. Documentation

**Update docs:**
- Add setting description
- Explain behavior and recommended values
- Add Configurator screenshot if needed

## Success Criteria

- [ ] Setting `max_battery_current` configurable via CLI
- [ ] Motor output reduces smoothly when current exceeds limit
- [ ] No oscillation or instability during limiting
- [ ] OSD shows when limiting is active
- [ ] Configurator UI allows configuration in Battery tab
- [ ] SITL tests pass with feature enabled/disabled
- [ ] Documentation updated (firmware + configurator)
- [ ] PR created to `maintenance-9.x` branch

## Files to Check

**Firmware:**
- `src/main/fc/settings.yaml`
- `src/main/sensors/current.c` or `current.h`
- `src/main/flight/mixer.c`
- `src/main/io/osd.c`

**Configurator:**
- Battery tab files (check tabs/ directory)
- Settings framework integration

## Notes

- Use existing current sensor infrastructure (don't reimplement current reading)
- Motor output reduction should be proportional and smooth
- Consider adding a minimum throttle threshold (e.g., don't limit below 10% throttle)
- Hysteresis prevents oscillation (activate at 100%, release at 90-95%)
- This is a safety feature - conservative implementation preferred
- Branch from `maintenance-9.x` (compatible with INAV 9.x configurator)

## Implementation Approach

1. Research existing current sensor code first
2. Plan the limiting algorithm (proportional scaling)
3. Implement firmware setting and logic
4. Add OSD element for feedback
5. Test with SITL thoroughly
6. Add Configurator UI
7. Create PR with complete implementation

**Questions?** Send a message if you need clarification or find issues during implementation.

---
**Manager**
