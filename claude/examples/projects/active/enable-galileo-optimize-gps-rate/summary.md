# Project: Enable Galileo by Default and Optimize GPS Update Rate

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature / Optimization
**Created:** 2025-12-31
**Estimated Effort:** 2-3 hours

## Overview

Implement the top recommendations from the u-blox GPS configuration analysis to improve GPS performance and accuracy.

## Problem

The u-blox GPS configuration analysis revealed two clear opportunities:

1. **Galileo disabled by default** - Missing out on improved accuracy and more satellites
2. **GPS update rate may not be optimal** - Jetrell's testing suggests 8Hz may be better than current 10Hz

## Objectives

1. **Enable Galileo by default on M8+ receivers**
   - Simple setting change in settings.yaml
   - Clear benefit with no downsides
   - Backward compatible (users can still disable)

2. **Optimize GPS update rate**
   - Research Jetrell's testing results
   - Determine if 8Hz is better than 10Hz
   - Implement optimal rate based on evidence

## Scope

**In Scope:**
- Change Galileo default setting to ON
- Research GPS update rate testing
- Implement GPS rate optimization if evidence supports it
- Update documentation
- Create pull request
- Hardware testing if available

**Out of Scope:**
- Other GPS configuration changes (GLONASS, BeiDou)
- Navigation model changes
- Message configuration changes
- Multi-frequency support (L1+L2)

## Background

From the analysis document (`claude/developer/reports/ublox-gps-inav-vs-ardupilot.md`):

### Galileo Benefits
- Equal or better accuracy than GPS
- Typically +8 satellites visible
- Better HDOP (dilution of precision)
- Faster time-to-first-fix
- Improved accuracy in interference/multipath
- Modern receivers (M8+) have supported since 2016
- **No known downsides**

### GPS Update Rate
- INAV current: 10Hz
- ArduPilot: 5Hz (noted M9N performance issues above 5Hz)
- **Jetrell's testing:** Suggests 8Hz may be optimal
- Need to understand why 8Hz might be better

## Implementation Approach

### Phase 1: Enable Galileo (Clear Win)
```yaml
# In settings.yaml
- name: gps_ublox_use_galileo
  default_value: ON  # Changed from OFF
```

### Phase 2: Research GPS Rate
1. Find Jetrell's testing results
2. Understand the evidence
3. Make informed decision

### Phase 3: Implement GPS Rate (If Supported)
Options:
- Change default to 8Hz for all M7+
- Hardware-specific rates (8Hz for M8/M9, 10Hz for M10)
- Keep 10Hz, document 8Hz option

### Phase 4: Test and PR
- Build verification
- Hardware testing if available
- Pull request with clear rationale

## Success Criteria

- [ ] Galileo enabled by default on M8+ receivers
- [ ] Jetrell's testing findings researched and documented
- [ ] GPS rate decision made with clear rationale
- [ ] Code compiles successfully
- [ ] Documentation updated
- [ ] Pull request created and submitted
- [ ] Hardware testing performed (if possible)

## Value

**Benefits:**
- Improved GPS accuracy for all INAV users
- More satellites = better reliability and HDOP
- Faster time-to-first-fix
- Optimal GPS update rate for best performance/reliability balance

**Audience:**
- All INAV users with M8+ GPS receivers (majority of current hardware)
- New users will get better defaults out-of-the-box

## Priority Justification

MEDIUM priority because:
- Clear benefit based on analysis
- Low risk (backward compatible)
- Reasonable effort (2-3 hours)
- Improves user experience for majority of users
- Based on comprehensive research

## Notes

**Galileo is straightforward** - clear evidence, no downsides, simple change.

**GPS rate needs investigation** - don't blindly change without understanding Jetrell's findings.

**Both changes are backward compatible** - users can revert via CLI if needed.

**Request community testing** - different GPS hardware may behave differently.

## Related

- Parent analysis: document-ublox-gps-configuration (COMPLETED)
- Analysis document: `claude/developer/reports/ublox-gps-inav-vs-ardupilot.md`
- INAV GPS code: `inav/src/main/io/gps_ublox.c`
- GPS settings: `inav/src/main/fc/settings.yaml`
