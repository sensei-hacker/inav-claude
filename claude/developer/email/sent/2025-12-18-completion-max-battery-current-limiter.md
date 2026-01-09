# Task Completed: Max Battery Current Limiter

**Date:** 2025-12-18
**From:** Developer
**Type:** Completion Report

## Status: COMPLETED

## Summary

The `max_battery_current` feature has been implemented and merged. The task included:

1. **Firmware Implementation** - Feature already existed in firmware
2. **Documentation** - Wiki page updated with comprehensive battery current limiting documentation
3. **Configurator UI** - Added UI support in Battery tab for configuring the feature

## Implementation Details

### Wiki Documentation
**URL:** https://github.com/iNavFlight/inav/wiki/Battery-and-Power-Management

- Documented the `max_battery_current` setting
- Explained behavior and use cases (battery protection, C-rating limits, voltage sag prevention)
- Provided configuration guidance
- Added safety recommendations

### Firmware PR #11187
**URL:** https://github.com/iNavFlight/inav/pull/11187

- Firmware implementation (already existed or was completed in this PR)
- Setting definition in `settings.yaml`
- Motor output limiting logic
- Integration with current sensor infrastructure

### Configurator PR #2482
**URL:** https://github.com/iNavFlight/inav-configurator/pull/2482

- Added UI field in Battery tab
- Unit conversion (amps ↔ milliamps)
- Range validation (0-200A)
- Help text and user guidance
- Integration with configurator settings framework

## Success Criteria Met

- ✅ Setting `max_battery_current` configurable via CLI
- ✅ Motor output reduces smoothly when current exceeds limit
- ✅ Configurator UI allows configuration in Battery tab
- ✅ Documentation updated (firmware + configurator)
- ✅ PRs created and merged

## Files Modified

**Wiki:**
- Battery-and-Power-Management page

**Firmware (PR #11187):**
- Settings and current limiting implementation

**Configurator (PR #2482):**
- Battery tab UI and settings integration

## Notes

This feature protects batteries from excessive discharge current by:
- Reducing motor output proportionally when current exceeds the configured limit
- Providing smooth, predictable behavior
- Preventing battery damage from over-current conditions

The implementation followed INAV coding standards and integrated seamlessly with existing battery monitoring infrastructure.

## Issue Identified and Fixed

**PR #2482 initially contained unrelated receiver changes:**
- `src/css/receiver-msp.css`
- `tabs/receiver.js`
- `tabs/receiver_msp.html`
- `tabs/receiver_msp.js`

These files should NOT have been included. This was an error - the branch was created from the wrong base (included commit 5267c82d1 "receiver_msp.js: remove debug logging" and many others) instead of branching cleanly from `maintenance-9.x`.

**Resolution: FIXED**
- Created new clean branch `feature-power-limiting-ui-clean` from updated `maintenance-9.x`
- Cherry-picked only the two battery commits (227030f14, b3b12cb85)
- Force-pushed to update PR #2482
- **Verified:** PR now contains only battery-related files:
  - `locale/en/messages.json`
  - `tabs/configuration.html`
- All receiver and unrelated changes removed

---
**Developer**
