# Project: Max Battery Current Limiter

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature Enhancement
**Created:** 2025-12-16
**Estimated Time:** 8-12 hours

## Overview

Implement a max_battery_current setting that reduces motor output when the current exceeds the configured threshold. This protects the battery from damage due to excessive discharge current.

## Problem

Currently, INAV has no mechanism to limit battery current draw. High current draw can:
- Damage battery cells (exceed C-rating)
- Cause voltage sag leading to ESC/FC brown-outs
- Reduce battery lifespan
- Create safety hazards (overheated batteries)

## Objectives

1. Add `max_battery_current` setting (configurable via CLI/Configurator)
2. Monitor real-time battery current from current sensor
3. Reduce motor output proportionally when current exceeds limit
4. Provide smooth, predictable behavior (no abrupt throttle cuts)
5. Log current limiting events for pilot awareness

## Scope

**In Scope:**
- New CLI setting: `max_battery_current` (milliamps, 0 = disabled)
- Current monitoring integration with existing current sensor code
- Motor output scaling when limit exceeded
- OSD notification when limiting is active
- Configurator UI integration (Battery tab)

**Out of Scope:**
- Current sensor calibration/validation (use existing sensors)
- Different limiting strategies (this implements proportional reduction)
- Per-motor limiting (applies to all motors equally)

## Implementation Steps

1. Add setting to `fc/settings.yaml` (Battery group)
2. Implement current monitoring in motor mixer code
3. Add proportional scaling algorithm when threshold exceeded
4. Add OSD element for current limiting status
5. Test with SITL simulation
6. Update Configurator Battery tab UI
7. Update documentation

## Success Criteria

- [ ] Setting configurable via CLI (`set max_battery_current = 50000`)
- [ ] Motor output reduces smoothly when current exceeds limit
- [ ] No oscillation or instability during limiting
- [ ] OSD shows when limiting is active
- [ ] Configurator UI allows configuration
- [ ] SITL tests pass with feature enabled/disabled
- [ ] Documentation updated

## Estimated Time

8-12 hours:
- Firmware implementation: 4-6 hours
- Configurator UI: 2-3 hours
- Testing & validation: 2-3 hours

## Priority Justification

MEDIUM priority - Safety and battery protection feature that many users will benefit from, but not blocking critical issues.
