# Project: Fix Transpiler API Definition Mismatches

**Type:** Bug Fix (CRITICAL)
**Status:** ✅ Complete
**Completed:** 2025-11-23
**Target Version:** INAV Configurator 9.0.1
**Pull Request:** TBD
**Related Report:** `claude/manager/inbox/2025-11-23-transpiler-documentation-review-report.md`
**Priority:** CRITICAL - Causes incorrect code generation

## Overview

Fix critical bugs in transpiler API definitions where operand values don't match INAV firmware constants. This causes the transpiler to generate incorrect logic conditions that read/write wrong flight parameters.

## Motivation

### The Critical Bug

When users write JavaScript like:
```javascript
if (flight.yaw > 1800) {  // Check yaw angle
  // ...
}
```

The transpiler currently generates:
```
logic 0 1 -1 2 2 17 0 1800 0  // operand 17 = IS_ARMED, NOT YAW!
```

This reads `IS_ARMED` (value 17) instead of `YAW` (value 40), causing completely incorrect behavior.

### Root Cause

The `flight.js` API definition file was created before `inav_constants.js` was auto-generated from firmware. It contains hardcoded operand values that have drifted out of sync with actual INAV firmware constants.

### Impact

- Users' logic conditions will read/write wrong parameters
- Silent data corruption - no error messages
- Difficult to debug - behavior appears random
- Affects all flight parameter access in JavaScript programming

## Technical Approach

### Phase 1: Investigate and Document

1. **Verify the bug** - Confirm mismatches against firmware source
2. **Understand scope** - Identify all affected parameters
3. **Research firmware mapping** - Understand how operand values are defined in INAV firmware
4. **Document findings** - Create detailed analysis of each mismatch

### Phase 2: Design Fix Strategy

Two potential approaches to evaluate:

**Option A: Refactor to Use Constants (Recommended)**
```javascript
const { OPERAND_TYPE, FLIGHT_PARAM } = require('../../transpiler/inav_constants.js');

module.exports = {
  yaw: {
    inavOperand: {
      type: OPERAND_TYPE.FLIGHT,
      value: FLIGHT_PARAM.YAW  // Auto-synced with firmware
    }
  }
}
```

**Option B: Manual Fix and Validate**
- Manually update each value
- Add automated tests to catch future drift
- Risk: Could drift again

### Phase 3: Implementation

1. Choose fix strategy based on code investigation
2. Update all mismatched values
3. Add missing parameters (25+ identified)
4. Create validation tests
5. Test round-trip transpile/decompile

## Files to Modify

### Critical Files

- `bak_inav-configurator/js/transpiler/api/definitions/flight.js`
  - Fix: yaw (17 → 40)
  - Fix: heading (17 → 40)
  - Fix: isArmed (18 → 17)
  - Fix: isAutoLaunch (19 → 18)
  - Fix: isFailsafe (20 → 24)
  - Fix: gpsSats (9 → 8)
  - Fix: groundSpeed (11 → 9)
  - Investigate: flightTime, batteryRemainingCapacity, batteryPercentage
  - Add: 25+ missing parameters from firmware

### Reference Files

- `bak_inav-configurator/js/transpiler/transpiler/inav_constants.js`
  - Source of truth for operand values
  - Auto-generated from firmware
  - DO NOT MODIFY

### Supporting Files (may need updates)

- `bak_inav-configurator/js/transpiler/api/definitions/override.js`
  - Verify operand values are correct

- `bak_inav-configurator/js/transpiler/api/definitions/rc.js`
  - Verify operand values are correct

- `bak_inav-configurator/js/transpiler/api/definitions/waypoint.js`
  - Verify operand values are correct

- Other API definition files as investigation reveals

### Test Files (to create)

- `bak_inav-configurator/js/transpiler/tests/operand-validation.test.js` (NEW)
  - Validate API definitions against constants
  - Prevent future drift

## Testing Strategy

### Unit Tests

Create comprehensive validation tests:

```javascript
// Verify flight.js matches FLIGHT_PARAM constants
describe('API Operand Validation', () => {
  it('should match firmware constants', () => {
    const { FLIGHT_PARAM } = require('../transpiler/inav_constants');
    const flightDefs = require('../api/definitions/flight');

    // Test each parameter
    expect(flightDefs.yaw.inavOperand.value).toBe(FLIGHT_PARAM.YAW);
    expect(flightDefs.isArmed.inavOperand.value).toBe(FLIGHT_PARAM.IS_ARMED);
    // ... etc
  });
});
```

### Round-Trip Tests

```javascript
// Verify transpile -> decompile preserves meaning
const input = "if (flight.yaw > 1800) { override.vtx.power = 4; }";
const lc = transpile(input);
const output = decompile(lc);
// Verify yaw is still yaw, not isArmed
```

### Manual Testing

1. Test on actual INAV hardware
2. Verify logic conditions work as expected
3. Test all fixed parameters
4. Verify new parameters work

## Risks & Considerations

### High Risk Areas

- **Breaking Changes** - Fixing the bug may break existing user scripts that accidentally depend on wrong behavior
- **Firmware Compatibility** - Must verify operand values across INAV versions
- **Backwards Compatibility** - May need migration path for existing scripts

### Migration Strategy

Consider:
1. Add warnings when deprecated operand values are detected
2. Provide migration tool to fix existing scripts
3. Document breaking changes clearly
4. Coordinate with INAV firmware team

### Testing Requirements

- Test on multiple INAV firmware versions
- Test on different flight controller boards
- Verify decompiler shows correct values
- Check round-trip consistency

## Investigation Tasks

Before implementing fixes, thoroughly investigate:

1. **Verify against firmware source**
   - Check INAV firmware source code for operand definitions
   - Confirm `inav_constants.js` generation is correct
   - Verify values across firmware versions

2. **Understand operand type system**
   - Document OPERAND_TYPE values and meanings
   - Understand how type 2 (FLIGHT) works
   - Check if other operand types have issues

3. **Assess impact on existing scripts**
   - Are there user scripts depending on current (buggy) behavior?
   - Can we detect and warn about affected scripts?
   - Do we need a migration tool?

4. **Check for similar issues**
   - Do override.js, rc.js, etc. have same problems?
   - Are there other auto-generated constants to sync?
   - Are there other manually maintained mappings?

## Missing Parameters to Add

From firmware (FLIGHT_PARAM in inav_constants.js):

- SPEED_3D (10)
- AIR_SPEED (11)
- IS_ALTITUDE_CONTROL (19)
- IS_POSITION_CONTROL (20)
- IS_EMERGENCY_LANDING (21)
- IS_RTH (22)
- IS_LANDING (23)
- STABILIZED_ROLL (25)
- STABILIZED_PITCH (26)
- STABILIZED_YAW (27)
- HOME_DISTANCE_3D (28)
- CRSF_LQ_UPLINK (29)
- CRSF_SNR (30)
- LOITER_RADIUS (32)
- ACTIVE_PROFILE (33)
- BATT_CELLS (34)
- AGL_STATUS (35)
- AGL (36)
- RANGEFINDER_RAW (37)
- ACTIVE_MIXER_PROFILE (38)
- MIXER_TRANSITION_ACTIVE (39)
- FW_LAND_STATE (41)
- BATT_PROFILE (42)
- FLOWN_LOITER_RADIUS (43)
- CRSF_LQ_DOWNLINK (44)
- CRSF_RSSI_DBM (45)

Each needs:
- API property name
- Description
- Valid ranges
- Units
- Testing

## Related Issues/PRs

- Blocked by: None - Critical bug, start immediately
- Blocks: None - But high priority
- Related: Project `fix-transpiler-documentation` (complementary work)

## Notes

- This is a CRITICAL bug fix - prioritize over documentation
- Coordinate with INAV firmware team if needed
- Consider creating automated sync tool for future
- May need to update configurator UI if new parameters are exposed
