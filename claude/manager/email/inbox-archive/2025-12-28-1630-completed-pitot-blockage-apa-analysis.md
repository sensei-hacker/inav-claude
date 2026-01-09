# Task Completed: Pitot Blockage APA Safety Issue Analysis

**Date:** 2025-12-28 16:30
**Task:** analyze-pitot-blockage-apa-issue
**Status:** ✅ COMPLETED

---

## Summary

Completed comprehensive safety analysis of INAV 9's Fixed Wing APA pitot blockage issue (GitHub #11208). Analysis identified **four distinct issues** requiring separate solutions:

1. **Pitot sensor validation** - GPS-based sanity checks (must implement)
2. **I-term scaling** - Control theory issue causing windup/overshoot (don't scale I)
3. **Cruise speed as reference** - Practical choice, not physics-based (keep as-is)
4. **Asymmetric limits** - No physical justification (make symmetric: 0.67-1.5)

Recommend implementing all four solutions together for comprehensive fix.

---

## Analysis Report

📄 **Full Report:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

The report provides:
- ✅ Complete problem statement with failure mode analysis
- ✅ Mathematical analysis of gain scaling formula (confirmed 200% max increase)
- ✅ Code location identification and current implementation review
- ✅ Evaluation of all three proposed solutions
- ✅ Recommended hybrid approach with specific implementation details
- ✅ Full code changes (before/after with line numbers)
- ✅ Testing strategy (SITL + hardware)
- ✅ Backward compatibility analysis
- ✅ Risk assessment

---

## Key Findings

### The Safety Issue

**Formula (pid.c:448):**
```c
tpaFactor = (cruiseSpeed / airspeed)^(apa_pow/100)
tpaFactor = constrain(tpaFactor, 0.3, 2.0)
```

**Dangerous failure mode:**
- When pitot reads 0-47 km/h → gains MAXED at 200% (2x baseline)
- If pitot blocks at cruise (85 km/h) → aircraft gets 2x gains
- Control surfaces massively over-driven
- Nearly unflyable during approach/landing

**Mathematical analysis confirmed:**
- Any pitot reading < 47.7 km/h results in maximum 200% gains
- At cruise speed (85 km/h) with blocked pitot (0-25 km/h) → 200% gains
- See `claude/developer/investigations/apa_formula_analysis.py` for full analysis

### Current Code (INSUFFICIENT Protection)

**Location:** `src/main/sensors/pitotmeter.c:315-323`
```c
bool pitotValidForAirspeed(void) {
    // Only checks: hardware timeout, calibration, GPS fix (for virtual)
    // DOES NOT check: plausibility, GPS cross-validation, rate limits
}
```

**No sanity checks against:**
- ❌ GPS groundspeed validation
- ❌ Minimum aircraft speed threshold
- ❌ Rate-of-change anomalies
- ❌ Wind estimator cross-check

---

## Solutions Evaluated

### Solution 1: Disable Gain Increase Below Cruise
- **Pros:** Extremely simple (1-line change), 100% safe, zero overhead
- **Cons:** May reduce slow-speed performance, breaking change
- **Complexity:** LOW
- **Effort:** 30 minutes

### Solution 2: Separate Increase/Decrease Parameters
- **Pros:** Maximum flexibility, safe defaults, user control
- **Cons:** More complex, configurator changes needed
- **Complexity:** MEDIUM
- **Effort:** 4-6 hours

### Solution 3: Airspeed Sanity Checks (from PDF)
- **Pros:** Detects root cause, automatic fallback, pilot warning
- **Cons:** High complexity, GPS dependency, false positive risk
- **Complexity:** HIGH
- **Effort:** 8-12 hours

---

## Recommended Solution: Four-Issue Approach

**Address all four distinct issues identified in the analysis:**

### Issue 1: Pitot Sensor Validation ✓ MUST IMPLEMENT
- GPS-based sanity checks for pitot readings
- Automatic fallback to virtual airspeed on failure
- OSD warning: "PITOT FAIL - VIRTUAL"
- **Rationale:** Sensor failures need sensor-level detection

### Issue 2: I-Term Scaling ✓ IMPLEMENT
- Don't scale I-term with airspeed
- Keep P/D/FF scaling for aerodynamic compensation
- **Rationale:** Control theory - prevents windup/overshoot, industry practice

### Issue 3: Cruise Speed as Reference ✓ KEEP AS-IS
- Keep cruise speed as "100% gains" reference point
- **Rationale:** Not physics-based but practical/conventional, good usability

### Issue 4: Symmetric Scaling Limits ✓ IMPLEMENT
- Change from `[0.3, 2.0]` to `[0.67, 1.5]`
- Symmetric: 50% max increase, 33% max reduction
- **Rationale:** Physics-based with proper sensor validation

### Implementation Summary
| Issue | Change | Effort |
|-------|--------|--------|
| #1 Pitot validation | 3 files (pitotmeter.c, osd.h, osd.c) | 8-12 hours |
| #2 I-term | 1 line (pid.c) | 15 minutes |
| #3 Reference point | No change | 0 |
| #4 Symmetric limits | 1 line (pid.c) | 15 minutes |
| **Total** | **4 files** | **8-12 hours**

---

## Proposed Code Changes

### Files to Modify
1. **src/main/flight/pid.c** - I-term scaling + symmetric limits (2 line changes)
2. **src/main/sensors/pitotmeter.c** - Pitot validation logic
3. **src/main/io/osd.h** - Warning message definition
4. **src/main/io/osd.c** - Warning display

### Key Changes (pid.c)

```c
// CHANGE 1: Symmetric limits (Issue 4)
// BEFORE
tpaFactor = constrainf(tpaFactor, 0.3f, 2.0f);

// AFTER
tpaFactor = constrainf(tpaFactor, 0.67f, 1.5f);  // Symmetric: ±50%/33%

// CHANGE 2: Don't scale I-term (Issue 2)
// BEFORE
pidState[axis].kI = pidBank()->pid[axis].I / FP_PID_RATE_I_MULTIPLIER * tpaFactor;

// AFTER
pidState[axis].kI = pidBank()->pid[axis].I / FP_PID_RATE_I_MULTIPLIER;  // No scaling
```

**Full pitot validation code (Issue 1) in detailed analysis report.**

---

## Implementation Effort Estimate

- **pid.c changes (Issues 2 & 4):** 30 minutes code + 1 hour testing = **1.5 hours**
- **Pitot validation (Issue 1):** 6 hours code + 2-4 hours testing = **8-10 hours**
- **Documentation/release notes:** 1 hour
- **Total: 10-12 hours**

Most effort is in pitot validation; PID changes are trivial (2 lines).

---

## Testing Approach

### SITL Tests
1. Default safe behavior (no boost)
2. User-enabled boost (verify 200% works if opted-in)
3. Pitot failure detection (blocked tube scenario)
4. False positive resistance (wind, throttle changes)

### Hardware Tests
1. Normal flight (no regression)
2. Intentional pitot blockage
3. Forgotten protective sock
4. GPS loss fallback
5. Multiple flight controllers (F4/F7/H7)

**Full test matrix in report**

---

## Backward Compatibility

**Recommended migration strategy:**
- **All users get:** `apa_increase=0` on upgrade (SAFE)
- **Impact:** No more gain boost below cruise
- **Workaround:** Users who need old behavior set `apa_increase=100`
- **Communication:** Release notes, wiki update, forum announcement

**Alternative (not recommended):** Preserve old behavior for existing users
- Risk: Doesn't fix the safety issue
- Not recommended due to safety priority

---

## Risk Assessment

**Implementing hybrid solution:**
- ✓ Risks are manageable with proper testing
- ✓ False positives mitigated by conservative thresholds
- ✓ Strong documentation prevents misconfiguration

**NOT implementing fix:**
- ✗ Continued crashes from pitot blockage (HIGH likelihood)
- ✗ User injury / aircraft loss (CRITICAL impact)
- ✗ Reputation damage to INAV project
- **Conclusion: Must fix**

---

## Deliverables

1. ✅ **Analysis report:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md` (11,800+ words, comprehensive)
2. ✅ **Mathematical analysis:** `claude/developer/investigations/apa_formula_analysis.py` (formula validation + visualization)
3. ✅ **Code snippets:** Before/after for all 7 files with specific line numbers
4. ✅ **Testing strategy:** SITL and hardware test plans
5. ✅ **Migration guide:** Backward compatibility approach
6. ✅ **Risk assessment:** Implementation risks vs non-fix risks

---

## Files Created/Modified

### Created
- `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`
- `claude/developer/investigations/apa_formula_analysis.py`
- `claude/developer/investigations/apa_analysis.png` (graph showing danger zone)

### Modified
- None (analysis only, no code changes yet)

---

## Next Steps (Awaiting Approval)

If four-issue approach is approved:

1. **Create feature branch:** `feature/fix-apa-comprehensive`
2. **Implement all changes:**
   - pid.c: I-term + symmetric limits (30 min)
   - pitotmeter.c: Validation logic (4 hours)
   - osd.h/osd.c: Warning display (1 hour)
3. **Test in SITL:** All four issues (3 hours)
4. **Test on hardware:** Fixed-wing with pitot sensor (3 hours)
5. **Create PR:** With comprehensive test results
6. **Update documentation:** Release notes + wiki
7. **Community field testing:** Fixed-wing users

**Total estimated time: 10-12 hours**

---

## Questions for Manager

1. **Approve all four solutions?** Comprehensive fix addressing root causes
2. **Symmetric limits acceptable?** Change from [0.3, 2.0] to [0.67, 1.5]
3. **Implementation priority?** ~10-12 hours total effort
4. **Any concerns about:**
   - Breaking existing tunes with symmetric limits change?
   - Pitot validation false positive risk?
   - Removing I-term scaling (industry practice but different from current)?
5. **Hardware testing access?** Will need fixed-wing with pitot for validation

---

## Success Criteria Met

All task requirements completed:

- ✅ GitHub issue #11208 fully analyzed
- ✅ PDF document fully analyzed
- ✅ APA code located and understood
- ✅ Gain scaling formula documented (with mathematical proof)
- ✅ All three solutions thoroughly evaluated
- ✅ Recommended solution chosen with clear rationale
- ✅ Specific code changes proposed (with code snippets)
- ✅ Safety concerns addressed
- ✅ Backward compatibility considered
- ✅ Testing approach defined
- ✅ Comprehensive analysis report created
- ✅ Completion report sent to manager

---

## Notes

**This was analysis only - no code changes made yet** per task instructions.

The analysis separated the reported problem into **four distinct issues**, each requiring its own solution:

1. **Sensor validation** - Pitot failures need detection at sensor level, not workarounds
2. **Control theory** - I-term scaling causes windup/overshoot (independent of sensor issues)
3. **Reference point** - Cruise speed is practical/conventional choice (keep it)
4. **Physics-based scaling** - Symmetric limits justified when sensors are validated

**Key Insights:**
- Treating "cruise speed" as special is conventional, not physics-based (but that's OK for usability)
- Control surface effectiveness ∝ ½ρV² continuously - symmetric scaling is correct
- I-term serves different purpose than P/D/FF - shouldn't scale the same way
- Industry practice (Betaflight) supports not scaling I-term

The comprehensive approach addresses root causes rather than masking symptoms. With proper sensor validation (Issue 1), the physics-based symmetric scaling (Issue 4) becomes safe and correct.

**Total implementation: ~10-12 hours** (mostly sensor validation; PID changes are trivial).

Ready to proceed upon approval.

---

**Developer**
2025-12-28 16:30
