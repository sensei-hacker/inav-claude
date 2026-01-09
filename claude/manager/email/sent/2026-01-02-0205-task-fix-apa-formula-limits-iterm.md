# Task Assignment: Fix APA Formula - Limits, I-term Scaling, Default Disabled

**Date:** 2026-01-02 02:05
**Project:** fix-apa-formula-limits-iterm
**Priority:** HIGH
**Estimated Effort:** 2-3 hours
**Type:** Bug Fix / Safety Improvement
**Milestone:** 9.1
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

## Task

Fix three issues with the Fixed Wing APA (Airspeed-based PID Attenuation) formula:
1. Change scaling limits from [0.3, 2.0] to [0.5, 1.5]
2. Reduce I-term scaling: use exponent (apa_pow - 100)/100 instead of apa_pow/100
3. Set apa_pow default to 0 (disabled by default)

## Background

**Parent Analysis:** analyze-pitot-blockage-apa-issue (COMPLETED 2025-12-28)

The pitot blockage APA safety analysis identified multiple issues with the current APA implementation beyond just the sensor validation problem. These are simpler fixes that address control theory and practical safety concerns.

## Reference Documentation

**REQUIRED READING:**

📄 **Analysis Report:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

Read sections:
- "Issue 2: I-Term Scaling" - Control theory rationale
- "Issue 4: Asymmetric Limits" - Physical justification for symmetric limits
- "Recommended Solution: Four-Issue Approach"
- Current implementation code examples

**Key findings from analysis:**
- I-term scaling causes windup and overshoot (control theory issue)
- Asymmetric limits [0.3, 2.0] have no physical justification
- Feature should be disabled by default for safety (opt-in)

## Objectives

### 1. Change Scaling Limits to [0.5, 1.5]

**Current:**
```c
tpaFactor = constrain(tpaFactor, 0.3, 2.0);  // ±70% / ±100%
```

**New:**
```c
tpaFactor = constrain(tpaFactor, 0.5, 1.5);  // ±50% symmetric
```

**Rationale:**
- Symmetric limits are more physically justified
- 0.5-1.5 range provides ±50% adjustment (sufficient)
- Reduces maximum gain increase from 200% to 150%
- Safer limits reduce impact of pitot failures

### 2. Scale I-term Less Aggressively (Compromise Approach)

**Current Problem:**
```c
// All PIFF terms scaled the same - too aggressive for I-term
pidState[axis].P *= tpaFactor;
pidState[axis].I *= tpaFactor;  // <-- Scaled by full exponent (1.2)
pidState[axis].D *= tpaFactor;
pidState[axis].FF *= tpaFactor;
```

**New Approach (Reduced I-term Scaling):**
```c
// Calculate standard tpaFactor for P, D, FF
float tpaFactor = powf(referenceAirspeed/(airspeed+0.01f),
                       currentControlProfile->throttle.apa_pow/100.0f);
tpaFactor = constrainf(tpaFactor, 0.5f, 1.5f);

// Calculate reduced scaling for I-term using (apa_pow - 100)/100 exponent
// Examples:
//   apa_pow = 120 → I exponent = 0.2 (minimal scaling)
//   apa_pow = 100 → I exponent = 0.0 (no scaling)
//   apa_pow = 150 → I exponent = 0.5 (moderate scaling)
float itermFactor = powf(referenceAirspeed/(airspeed+0.01f),
                         (currentControlProfile->throttle.apa_pow - 100.0f)/100.0f);
itermFactor = constrainf(itermFactor, 0.5f, 1.5f);

// Apply different scaling to each term
pidState[axis].P *= tpaFactor;   // Full aerodynamic scaling
pidState[axis].I *= itermFactor; // Reduced scaling (compromise)
pidState[axis].D *= tpaFactor;   // Full aerodynamic scaling
pidState[axis].FF *= tpaFactor;  // Full aerodynamic scaling
```

**Rationale (Compromise Approach):**
- **Control theory concern:** Scaling I-term causes windup at low speeds, overshoot at high speeds
- **Practical concern:** Some I-term scaling may help with aerodynamic changes
- **Compromise:** Use reduced exponent (apa_pow - 100)/100 instead of apa_pow/100
- **Result:** With default apa_pow=120:
  - P/D/FF scaled by exponent 1.2 (aggressive)
  - I-term scaled by exponent 0.2 (gentle)
- **Benefit:** Reduces control theory issues while maintaining some adaptive behavior

### 3. Set apa_pow Default to 0 (Disabled)

**Current:**
```yaml
- name: apa_pow
  default_value: 120
  min: 0
  max: 200
```

**New:**
```yaml
- name: apa_pow
  default_value: 0       # Disabled by default
  min: 0
  max: 200
  description: "Fixed Wing APA power. 0=disabled, 120=default active curve. Enable only with validated pitot sensor. Range [0-200]"
```

**Rationale:**
- Feature should be opt-in for safety
- Requires working pitot sensor to be safe
- Users must understand pitot failure risks before enabling
- After fixes, users can safely set to 120 to enable

**Documentation Note:**
Add to docs: "To enable APA with recommended settings, set `apa_pow = 120`"

## Implementation

### File Locations

**Primary:**
- `src/main/flight/pid.c` - APA scaling application (around line 448)
- `src/main/fc/settings.yaml` - apa_pow default value

**Changes Required:**

### 1. Update pid.c - Change Limits

**Location:** `src/main/flight/pid.c:448` (approximately)

**Find:**
```c
float tpaFactor = powf(referenceAirspeed/(airspeed+0.01f), currentControlProfile->throttle.apa_pow/100.0f);
tpaFactor = constrainf(tpaFactor, 0.3f, 2.0f);
```

**Change to:**
```c
float tpaFactor = powf(referenceAirspeed/(airspeed+0.01f), currentControlProfile->throttle.apa_pow/100.0f);
tpaFactor = constrainf(tpaFactor, 0.5f, 1.5f);  // Changed from 0.3, 2.0
```

### 2. Update pid.c - Reduce I-term Scaling (Compromise)

**Find:** (in the same function, after tpaFactor calculation)
```c
pidState[axis].P *= tpaFactor;
pidState[axis].I *= tpaFactor;
pidState[axis].D *= tpaFactor;
pidState[axis].FF *= tpaFactor;
```

**Change to:**
```c
// Calculate reduced I-term scaling factor (compromise approach)
// Uses exponent (apa_pow - 100)/100 instead of apa_pow/100
// Example: apa_pow=120 → I exponent=0.2, P/D/FF exponent=1.2
float itermFactor = powf(referenceAirspeed/(airspeed+0.01f),
                         (currentControlProfile->throttle.apa_pow - 100.0f)/100.0f);
itermFactor = constrainf(itermFactor, 0.5f, 1.5f);

// Apply scaling with reduced I-term scaling
pidState[axis].P *= tpaFactor;
pidState[axis].I *= itermFactor;  // Reduced scaling (compromise)
pidState[axis].D *= tpaFactor;
pidState[axis].FF *= tpaFactor;
```

**Add comment explaining:**
```c
// Note: I-term uses reduced scaling (apa_pow-100)/100 instead of apa_pow/100
// Rationale: Full I-term scaling causes windup at low speeds and overshoot
// at high speeds. This compromise provides minimal I-term adaptation while
// avoiding control theory issues. P/D/FF get full aerodynamic scaling.
// See GitHub issue #11208 for detailed analysis.
```

### 3. Update settings.yaml - Default to 0

**Location:** `src/main/fc/settings.yaml` (search for apa_pow)

**Find:**
```yaml
- name: apa_pow
  description: "..."
  default_value: 120
  min: 0
  max: 200
```

**Change to:**
```yaml
- name: apa_pow
  description: "Fixed Wing APA (Airspeed-based PID Attenuation) power curve. 0=disabled (default), 120=recommended if enabled. Requires validated pitot sensor. Higher values = more aggressive scaling. Range [0-200]"
  default_value: 0       # Changed from 120 - disabled by default for safety
  min: 0
  max: 200
```

## Testing Requirements

### 1. Build Test
- Verify firmware compiles successfully
- Test multiple targets to ensure no issues

### 2. SITL Testing

**Scenario 1: APA Disabled (Default)**
```bash
# Default apa_pow = 0
# Expected: No gain scaling regardless of airspeed
# Expected: Aircraft flies normally
```

**Scenario 2: APA Enabled**
```bash
# Set apa_pow = 120
# Fly at various airspeeds
# Expected: Gains scale within [0.5, 1.5] range
# Expected: I-term NOT scaled (check PID values)
# Expected: Smoother behavior than before (no I-term issues)
```

**Scenario 3: Extreme Airspeeds**
```bash
# Set apa_pow = 120
# Fly very slow (stall speed)
# Expected: tpaFactor = 1.5 maximum (was 2.0)
# Expected: itermFactor = ~1.12 (gentle scaling)
# Fly very fast (dive)
# Expected: tpaFactor = 0.5 minimum (was 0.3)
# Expected: itermFactor = ~0.89 (gentle scaling)
```

### 3. Verify I-term Scaled Less than P/D/FF
```c
// Add debug logging in SITL
DEBUG_SET(DEBUG_PID, 0, pidState[FD_PITCH].I);  // Should scale gently
DEBUG_SET(DEBUG_PID, 1, pidState[FD_PITCH].P);  // Should scale more aggressively
DEBUG_SET(DEBUG_PID, 2, itermFactor);           // Should be closer to 1.0
DEBUG_SET(DEBUG_PID, 3, tpaFactor);             // Should vary more
```

### 4. Mathematical Verification

**With apa_pow=120, cruise=85 km/h, limits [0.5, 1.5]:**
- At 85 km/h: tpaFactor = 1.0 ✓
- At 56.7 km/h (0.67×cruise): tpaFactor = 1.5 ✓
- At 127.5 km/h (1.5×cruise): tpaFactor = 0.5 ✓
- Operational range: 0.67×cruise to 1.5×cruise

**Compare to old limits [0.3, 2.0]:**
- Old range: 0.45×cruise to 2.73×cruise (too wide)
- New range: 0.67×cruise to 1.5×cruise (appropriate)

## Files to Modify

1. **src/main/flight/pid.c**
   - Change limits from [0.3, 2.0] to [0.5, 1.5]
   - Remove I-term scaling
   - Add explanatory comments

2. **src/main/fc/settings.yaml**
   - Change apa_pow default from 120 to 0
   - Update description

3. **docs/** (appropriate file, maybe Tuning.md or Sensors.md)
   - Document that APA is disabled by default
   - Explain how to enable: set apa_pow = 120
   - Explain that working pitot sensor is required
   - Note the changes from INAV 9.0

## Success Criteria

- [ ] Limits changed to [0.5, 1.5]
- [ ] I-term NOT scaled with airspeed
- [ ] P/D/FF still scaled with airspeed
- [ ] apa_pow default set to 0
- [ ] Description updated to explain how to enable
- [ ] Code compiles successfully
- [ ] SITL tests pass
- [ ] Mathematical verification correct
- [ ] Documentation updated
- [ ] Pull request created

## Deliverables

1. **Code Changes**
   - Updated pid.c with new limits and I-term fix
   - Updated settings.yaml with default 0
   - Clear comments explaining changes

2. **Testing**
   - SITL test results
   - Mathematical verification
   - Debug logs showing I-term not scaled

3. **Documentation**
   - Updated docs explaining APA default disabled
   - Instructions for enabling (set apa_pow = 120)
   - Rationale for changes

4. **Pull Request**
   - Reference GitHub issue #11208
   - Reference analysis document
   - Explain all three changes
   - Include test results

5. **Completion Report**
   - Summary of changes
   - Test results
   - User impact notes

## Important Notes

### These are Simple But Important Fixes

**Limits change [0.3, 2.0] → [0.5, 1.5]:**
- One-line change
- Immediate safety improvement
- Reduces danger from pitot failures

**I-term scaling removal:**
- One-line change (comment out)
- Fixes control theory issue
- Improves flight characteristics

**Default to 0:**
- One-line change
- Major safety improvement (opt-in)
- Prevents issues for new users

**Total code changes: ~3 lines**
**Impact: Significant safety improvement**

### User Impact

**Existing users upgrading from INAV 9.0:**
- APA will be DISABLED after upgrade (apa_pow = 0)
- Must manually set apa_pow = 120 to re-enable
- This is intentional for safety
- Users should verify pitot sensor working before enabling

**New users:**
- APA disabled by default (safe)
- Can enable if they have working pitot sensor
- Clear documentation on how to enable

**Users with APA enabled and working:**
- Will notice smoother behavior (I-term fix)
- Slightly less aggressive scaling (new limits)
- Overall better flight characteristics

### Relationship to Pitot Validation

**These fixes are independent of pitot sensor validation:**
- Can be implemented separately
- Both are part of comprehensive fix for #11208
- Pitot validation is longer task (8-12 hours)
- This task is quick fix (2-3 hours)

**Together they provide complete solution:**
1. This task: Fix formula, make safer, disable by default
2. Pitot validation task: Detect failures, automatic fallback

## Migration Strategy

**settings.yaml change means:**
- All users get apa_pow = 0 on upgrade
- Users who want APA must manually enable
- Safest approach given pitot failure risks

**Add to release notes:**
```
IMPORTANT: Fixed Wing APA now disabled by default (apa_pow = 0)

To enable APA with improved formula:
1. Verify pitot sensor is working and validated
2. Set: apa_pow = 120
3. Test carefully before flight

Changes in INAV 9.1:
- APA scaling limits changed from [0.3, 2.0] to [0.5, 1.5] (safer)
- I-term no longer scaled with airspeed (better control)
- Default disabled for safety (opt-in feature)
```

## References

- **Analysis Document:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`
- **GitHub Issue:** https://github.com/iNavFlight/inav/issues/11208
- **Parent Project:** analyze-pitot-blockage-apa-issue (COMPLETED)
- **Related Task:** implement-pitot-sensor-validation (separate task)
- **Current Code:** `src/main/flight/pid.c:448` (approximate)
- **Settings:** `src/main/fc/settings.yaml`

---

**Manager**
