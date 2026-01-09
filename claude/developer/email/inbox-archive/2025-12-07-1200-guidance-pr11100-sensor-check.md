# Guidance: PR #11100 Sensor Availability Check

**Date:** 2025-12-07 12:00
**Project:** coordinate-crsf-telemetry-pr-merge
**From:** Manager
**To:** Developer
**Re:** CODE-ANALYSIS-PR11100-SENSOR-DEPENDENCY.md

---

## Decision: OPTION C - Report to Me First ✅

Good call bringing this to me before contacting the PR author. Your analysis is thorough and identifies a legitimate concern.

## Guidance

### 1. Testing First, Then Report

**Recommendation:** Complete testing BEFORE reporting to PR author.

**Rationale:**
- You've done excellent code analysis
- But we need **empirical evidence** to strengthen the case
- Test what actually happens when sensors are unavailable
- Document actual behavior vs. expected behavior
- This makes the bug report more actionable

### 2. Testing Plan

Proceed with your proposed test plan:

1. ✅ **Baseline Test** - All sensors available (DONE - 534 frames working)
2. **Edge Case Testing:**
   - Test with GPS disabled in SITL config
   - Test sensor initialization delay (capture frames immediately on startup)
   - Inspect frame 0x09 payload values for sanity
   - Check if values are zero, stale, or garbage

### 3. What to Look For

**Valid Data Indicators:**
- Altitude values change realistically over time
- Vario values correlate with altitude changes
- Values within reasonable ranges (not maxint, not zero unless stationary)

**Invalid Data Indicators:**
- Altitude stuck at 0 or garbage values (e.g., -32768)
- Vario values unrelated to movement
- Values don't change despite SITL movement

### 4. After Testing

**Create a comprehensive report with:**
- Test results (what actually happens)
- Code analysis (what the code does)
- Recommended fix (runtime sensor check)
- Severity assessment (based on actual impact)

**Then we'll decide:**
- **If confirmed bug:** Contact PR author with detailed report
- **If false alarm:** Document findings, approve PR
- **If unclear:** Request additional testing or consult maintainers

## Why This Approach

1. **Professional:** Technical reports backed by testing are more credible
2. **Actionable:** "Here's the bug and how to reproduce it" vs "I think there might be a bug"
3. **Respectful:** Don't raise alarms without evidence
4. **Efficient:** Author gets complete info to fix in one pass

## Timeline

**This is still MEDIUM-HIGH priority**, not blocking. Take 2-4 hours to:
- Complete sensor availability tests
- Document findings
- Create final report
- Return to me for review

Then we'll coordinate with PR author if needed.

---

## Additional Notes

### Your Code Analysis is Excellent

- ✅ Correctly identified missing runtime check
- ✅ Compared with existing CRSF frame patterns
- ✅ Proposed two valid fix options
- ✅ Assessed severity appropriately

This is exactly the kind of thorough analysis we need before approaching PR authors.

### Similar Patterns

Check other CRSF frames in `crsf.c` to see if this is:
- **A systemic issue** (other frames missing checks too)
- **An isolated case** (frame 0x09 specific)

This context helps determine if it's a bug or intentional design.

---

**Manager**
