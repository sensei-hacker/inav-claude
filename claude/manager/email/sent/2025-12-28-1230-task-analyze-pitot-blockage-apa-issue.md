# Task Assignment: Analyze Pitot Blockage APA Safety Issue

**Date:** 2025-12-28 12:30
**Project:** analyze-pitot-blockage-apa-issue
**Priority:** MEDIUM-HIGH
**Estimated Effort:** 6-8 hours
**Type:** Analysis & Proposal

## Task

Analyze the dangerous behavior of INAV 9's Fixed Wing APA (Airspeed-based PID Attenuation) feature when pitot tube fails or becomes blocked, and propose specific code changes to address the safety issue.

## Background

**Issue:** https://github.com/iNavFlight/inav/issues/11208

A user reported that INAV 9's new Fixed Wing APA feature creates a critical safety issue:

**Normal Operation:**
- Above cruise speed (~85 km/h): PIFF gains reduced by up to 70% ✓
- Below cruise speed: PIFF gains increased by up to 200% ⚠️

**Dangerous Failure Mode:**
When pitot tube fails, gets blocked, or sock is left on:
1. Airspeed sensor reads very low (< 25 km/h)
2. Aircraft is actually at cruise speed (~85 km/h)
3. System thinks aircraft is slow → increases PIFF gains to 200%
4. Aircraft becomes nearly unflyable with massively over-driven control surfaces
5. Landing becomes extremely difficult/dangerous

**This is a SAFETY CRITICAL issue** - pitot failures are common (mechanical failure, blockage, forgotten sock).

## What to Do

### 1. Research Phase

**Read the GitHub issue:**
- Issue #11208: https://github.com/iNavFlight/inav/issues/11208
- Understand user's experience and failure scenario
- Note all suggested solutions
- Review graphs and images

**Read the PDF document:**
```bash
# Open this file and read thoroughly
/home/raymorris/Downloads/pitot blockage sanity check.pdf
```
- Extract technical details
- Note any additional analysis or suggestions
- Document proposed solutions

**Read wiki documentation:**
- https://github.com/iNavFlight/inav/wiki/PID-Attenuation-and-scaling#Fixedwing-APA
- Understand intended behavior and configuration

### 2. Code Analysis Phase

**Locate the APA implementation:**

```bash
cd inav

# Search for APA-related code
grep -r "apa_pow" src/
grep -r "fixedWingAPA" src/
grep -r "PIFF" src/

# Likely files:
# - src/main/flight/pid.c
# - src/main/fc/settings.yaml
# - src/main/sensors/pitotmeter.c
```

**Analyze the gain scaling logic:**
- Find the formula that scales PIFF gains
- Understand how `apa_pow` is used
- Determine why gains increase below cruise speed
- Calculate actual percentage ranges (confirm 200% claim)
- Identify cruise speed reference point

**Check for safety features:**
- Are there any airspeed sanity checks?
- Is there a minimum valid airspeed threshold?
- Does the code detect pitot blockage?
- Are there rate-of-change validations?
- Can other sensors (GPS) cross-validate airspeed?

**Trace failure scenarios:**
- What happens when pitot reads 0 km/h?
- What happens when pitot reads < 25 km/h at cruise speed?
- What happens on sudden airspeed drops?
- Are there any existing fail-safes?

### 3. Solution Evaluation Phase

The issue and PDF suggest several solutions. Evaluate each:

**Solution 1: Don't increase gains below cruise speed**
- Simply disable the gain increase for speeds below cruise
- Gains would only decrease (or stay at 100%) above cruise
- Simplest and safest approach

**Evaluate:**
- ✅ Pros: Simple, safe, prevents the issue entirely
- ❌ Cons: May reduce performance at very slow speeds (if gain increase was beneficial)
- Code complexity: Low (one conditional change)
- Backward compatibility: Affects existing users who may rely on current behavior

**Solution 2: Add separate increase/decrease parameters**
- Add `apa_increase` - maximum percentage for gain increase (default 0%)
- Add `apa_decrease` - maximum percentage for gain decrease (default 70%)
- `apa_pow` remains as the expo curve endpoint
- Users can disable increase by setting `apa_increase=0`

**Evaluate:**
- ✅ Pros: Maximum flexibility, users can choose behavior
- ❌ Cons: More complex, more settings to tune, users may misconfigure
- Code complexity: Medium (need UI/configurator changes)
- Backward compatibility: Need sensible defaults for migration

**Solution 3: Add airspeed sanity checks**
- Check if airspeed is below configured minimum aircraft speed
- Check for rate-of-change anomalies (sudden drops)
- Cross-validate with GPS groundspeed (if available)
- Only apply gain changes if airspeed data seems valid

**Evaluate:**
- ✅ Pros: Addresses root cause, could detect other issues too
- ❌ Cons: More complex, risk of false positives
- Code complexity: Medium-High
- Need to define "what is valid airspeed?"

**Consider hybrid approaches:**
- Combine no-increase with sanity checks
- Combine separate parameters with validation limits
- Layered safety (multiple checks)

### 4. Proposal Phase

**Create detailed analysis report:**

File: `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

**Report structure:**

```markdown
# Analysis: Pitot Blockage APA Safety Issue (#11208)

## Executive Summary
[One paragraph: problem, impact, recommendation]

## Problem Statement
[Detailed description of the safety issue]

## Current Implementation
### Code Location
[Where is the code?]

### Gain Scaling Formula
[Document the exact formula used]

### Behavior Analysis
[How it works above/below cruise speed]

## Failure Mode Analysis
[What happens when pitot fails?]

## Solution Evaluation

### Solution 1: No Gain Increase Below Cruise
[Detailed pros/cons analysis]

### Solution 2: Separate Parameters
[Detailed pros/cons analysis]

### Solution 3: Sanity Checks
[Detailed pros/cons analysis]

### Hybrid Approaches
[Any combined solutions]

## Recommended Solution
[Your recommendation with rationale]

## Proposed Code Changes

### Files to Modify
- File 1: path/to/file.c
- File 2: path/to/file.yaml

### Code Changes

#### Before (Current Code)
```c
// Current implementation
```

#### After (Proposed Changes)
```c
// Proposed implementation with comments
```

### New Settings (if applicable)
```yaml
# settings.yaml additions
```

## Testing Approach

### SITL Testing
[How to test in SITL]

### Hardware Testing
[What to test on real hardware]

### Test Scenarios
1. Normal operation
2. Pitot blocked
3. Pitot failure
4. Forgotten sock
5. ...

## Backward Compatibility

### Impact on Existing Users
[Who is affected and how?]

### Migration Path
[How do users upgrade?]

### Default Values
[What defaults for new settings?]

## References
- Issue #11208
- PDF: pitot blockage sanity check.pdf
- Wiki: PID Attenuation and scaling
- Related code files
```

**Make sure your report:**
- Provides specific code locations
- Shows actual code snippets (before/after)
- Recommends a specific solution with clear rationale
- Addresses safety concerns
- Considers all users (not just those with pitot sensors)
- Provides actionable implementation guidance

### 5. Deliver Report

Send completion report to manager with:
- Link to analysis report
- Brief summary of recommendation
- Estimated implementation effort if approved

## Success Criteria

- [ ] GitHub issue #11208 fully analyzed
- [ ] PDF document fully analyzed
- [ ] APA code located and understood
- [ ] Gain scaling formula documented
- [ ] All three solutions thoroughly evaluated
- [ ] Recommended solution chosen with clear rationale
- [ ] Specific code changes proposed (with code snippets)
- [ ] Safety concerns addressed
- [ ] Backward compatibility considered
- [ ] Testing approach defined
- [ ] Comprehensive analysis report created
- [ ] Completion report sent to manager

## Important Notes

**This is ANALYSIS ONLY - do not implement changes yet.**

The goal is to:
1. Understand the problem thoroughly
2. Evaluate all options objectively
3. Make a well-reasoned recommendation
4. Propose specific implementation details

If your recommendation is approved, a separate implementation task/PR will follow.

**Safety First:**
This affects flight safety in common failure conditions. Your analysis should prioritize fail-safe behavior over performance optimization.

**Be Thorough:**
Both the issue and PDF likely contain important details. Make sure to extract all relevant information.

**Consider All Cases:**
- Users with pitot sensors
- Users without pitot sensors
- Edge cases (GPS-only, indoor, etc.)
- Backward compatibility for existing tuned aircraft

**Ask Questions:**
If you need clarification on any aspect of the issue or expected analysis depth, ask before spending hours going down the wrong path.

---
**Manager**
