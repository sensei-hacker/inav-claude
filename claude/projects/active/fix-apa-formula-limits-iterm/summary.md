# Project: Fix APA Formula - Limits, I-term Scaling, Default Disabled

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Fix / Safety Improvement
**Created:** 2026-01-02
**Estimated Effort:** 2-3 hours
**Milestone:** 9.1
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

## Overview

Fix three issues with Fixed Wing APA (Airspeed-based PID Attenuation) formula:
1. Change scaling limits from [0.3, 2.0] to [0.5, 1.5]
2. Reduce I-term scaling: use exponent (apa_pow - 100)/100 instead of apa_pow/100
3. Set apa_pow default to 0 (disabled by default)

## Problem

**Parent Analysis:** analyze-pitot-blockage-apa-issue (COMPLETED 2025-12-28)

The pitot blockage APA safety analysis identified issues with the APA implementation beyond sensor validation:
- **Asymmetric limits** [0.3, 2.0] have no physical justification, too wide range
- **I-term scaling** causes windup and overshoot (control theory issue)
- **Feature enabled by default** is unsafe given pitot failure risks

## Reference Documentation

**REQUIRED READING:**
📄 `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

Sections:
- "Issue 2: I-Term Scaling"
- "Issue 4: Asymmetric Limits"
- "Recommended Solution: Four-Issue Approach"

## Objectives

### 1. Change Limits to [0.5, 1.5]

**Current:** `tpaFactor = constrain(tpaFactor, 0.3, 2.0);`
**New:** `tpaFactor = constrain(tpaFactor, 0.5, 1.5);`

**Rationale:**
- Symmetric limits are more physically justified
- ±50% range is sufficient for aerodynamic compensation
- Reduces maximum gain increase from 200% to 150%
- Safer limits reduce impact of pitot failures

### 2. Reduce I-term Scaling (Compromise)

**Current:** All PIFF terms scaled by same tpaFactor (exponent 1.2)
**New:** I-term scaled with reduced exponent (apa_pow - 100)/100

**Rationale (compromise approach):**
- Full I-term scaling causes windup at low speeds, overshoot at high speeds
- But some I-term adaptation may be beneficial
- Compromise: Use exponent 0.2 instead of 1.2 (with apa_pow=120)
- P/D/FF get full aerodynamic scaling, I-term gets minimal scaling

### 3. Set apa_pow Default to 0

**Current:** default_value: 120
**New:** default_value: 0 (disabled)

**Rationale:**
- Feature should be opt-in for safety
- Requires working pitot sensor to be safe
- Users must understand pitot failure risks before enabling
- After fixes, users can safely set to 120 to enable

## Implementation

**Total code changes: ~3 lines**

### Change 1: Update Limits (pid.c)
```c
// Before
tpaFactor = constrainf(tpaFactor, 0.3f, 2.0f);

// After
tpaFactor = constrainf(tpaFactor, 0.5f, 1.5f);
```

### Change 2: Reduce I-term Scaling (pid.c)
```c
// Before
pidState[axis].P *= tpaFactor;
pidState[axis].I *= tpaFactor;
pidState[axis].D *= tpaFactor;
pidState[axis].FF *= tpaFactor;

// After - add itermFactor calculation
float itermFactor = powf(referenceAirspeed/(airspeed+0.01f),
                         (currentControlProfile->throttle.apa_pow - 100.0f)/100.0f);
itermFactor = constrainf(itermFactor, 0.5f, 1.5f);

pidState[axis].P *= tpaFactor;
pidState[axis].I *= itermFactor;  // Reduced scaling
pidState[axis].D *= tpaFactor;
pidState[axis].FF *= tpaFactor;
```

### Change 3: Default Disabled (settings.yaml)
```yaml
# Before
- name: apa_pow
  default_value: 120

# After
- name: apa_pow
  default_value: 0  # Disabled by default
  description: "Fixed Wing APA power. 0=disabled, 120=recommended. Requires validated pitot. Range [0-200]"
```

## Files to Modify

- `src/main/flight/pid.c` - Limits and I-term scaling
- `src/main/fc/settings.yaml` - Default value
- `docs/` - Document changes

## Success Criteria

- [ ] Limits changed to [0.5, 1.5]
- [ ] I-term NOT scaled
- [ ] P/D/FF still scaled
- [ ] apa_pow default set to 0
- [ ] Compiles successfully
- [ ] SITL tests pass
- [ ] Documentation updated

## Value

**Safety Improvements:**
- Safer limits reduce pitot failure impact
- I-term fix improves flight characteristics
- Default disabled prevents issues for new users

**Impact:**
- Simple changes (3 lines of code)
- Significant safety improvement
- Better control behavior
- Opt-in approach for safety

## User Impact

**Existing users upgrading from INAV 9.0:**
- APA will be DISABLED after upgrade (apa_pow = 0)
- Must manually set apa_pow = 120 to re-enable
- This is intentional for safety

**Users re-enabling APA:**
- Verify pitot sensor working
- Set apa_pow = 120
- Test carefully before flight
- Notice smoother behavior (I-term fix)

## Related

- Parent analysis: analyze-pitot-blockage-apa-issue (COMPLETED)
- Related task: implement-pitot-sensor-validation (separate longer task)
- GitHub issue: #11208
