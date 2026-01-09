# Project: Analyze Pitot Blockage APA Issue and Propose Solutions

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Bug Analysis / Feature Enhancement
**Created:** 2025-12-28
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)
**Estimated Effort:** 6-8 hours

## Overview

Analyze the Fixed Wing APA (Airspeed-based PID Attenuation) feature in INAV 9.x to address dangerous behavior when pitot tube fails or becomes blocked, causing excessive PIFF gain increases.

## Problem

INAV 9's new Fixed Wing APA feature has a critical safety issue:

**Normal Operation:**
- Above cruise speed: PIFF gains reduced by up to 70% (good)
- Below cruise speed: PIFF gains increased by up to 200% (questionable)

**Failure Mode:**
When pitot tube fails, gets blocked, or sock is left on:
1. Airspeed reads very low (< 25 km/h)
2. At actual cruise speed (~85 km/h), system thinks aircraft is slow
3. PIFF gains increase to 200%
4. Aircraft becomes nearly unflyable
5. Landing with 200% gains is extremely difficult

**Safety Impact:** CRITICAL - pitot failure is common (blockage, forgot to remove sock, mechanical failure)

## Objectives

1. Read and understand GitHub issue #11208
2. Review PDF document: `/home/raymorris/Downloads/pitot blockage sanity check.pdf`
3. Locate and analyze the Fixed Wing APA implementation code
4. Evaluate suggested solutions from issue and PDF
5. Propose specific code changes with rationale
6. Create detailed analysis report

## Scope

**In Scope:**
- Analysis of current APA implementation
- Pitot blockage detection logic (if any)
- PIFF gain scaling behavior above/below cruise speed
- Evaluation of suggested solutions:
  - Option 1: Don't increase gains below cruise speed
  - Option 2: Add separate parameters for increase/decrease percentages
  - Option 3: Add airspeed sanity checks before applying gain changes
- Safety considerations and failure modes
- Backward compatibility concerns

**Out of Scope:**
- Implementation (analysis only, no code changes yet)
- Testing on hardware (analysis and proposal only)
- Changes to airspeed sensor drivers
- General PID tuning improvements

## Implementation Steps

### Phase 1: Research & Understanding

1. Read GitHub issue #11208 completely
   - Understand user's experience and failure mode
   - Note all suggested solutions
   - Review attached graphs/images

2. Read PDF document thoroughly
   - Extract technical details
   - Note any additional suggestions or analysis
   - Understand proposed solutions

3. Find and read relevant wiki documentation
   - https://github.com/iNavFlight/inav/wiki/PID-Attenuation-and-scaling#Fixedwing-APA

### Phase 2: Code Analysis

4. Locate the Fixed Wing APA implementation
   - Search for `apa_pow` setting
   - Find PIFF gain scaling code
   - Identify cruise speed reference point
   - Find where airspeed is read and used

5. Analyze current behavior
   - Understand the gain scaling formula
   - Identify how `apa_pow` controls the curve
   - Determine why gains increase below cruise speed
   - Check if any sanity checks exist

6. Identify safety issues
   - What happens on pitot failure?
   - What happens on pitot blockage?
   - What happens if sock left on?
   - Are there any existing protections?

### Phase 3: Solution Evaluation

7. Evaluate Suggestion 1: No gain increase below cruise speed
   - Pros and cons
   - Impact on flight performance
   - Code complexity
   - Backward compatibility

8. Evaluate Suggestion 2: Separate increase/decrease parameters
   - Pros and cons
   - Code changes required
   - UI/configurator impact
   - User complexity

9. Evaluate Suggestion 3: Airspeed sanity checks
   - What checks make sense?
   - Min airspeed threshold
   - Rate of change detection
   - Pitot blockage indicators
   - Integration with existing checks

10. Consider hybrid solutions
    - Combine multiple approaches
    - Layered safety approach

### Phase 4: Report Creation

11. Create detailed analysis report including:
    - Summary of current behavior
    - Detailed problem description
    - Code location and analysis
    - Evaluation of each suggested solution
    - Recommended solution with rationale
    - Specific code changes proposed
    - Testing approach
    - Backward compatibility considerations

## Success Criteria

- [ ] GitHub issue #11208 fully read and understood
- [ ] PDF document fully read and understood
- [ ] APA implementation code located and analyzed
- [ ] Current gain scaling behavior documented
- [ ] All suggested solutions evaluated
- [ ] Safety issues identified and documented
- [ ] Recommended solution chosen with rationale
- [ ] Specific code changes proposed (pseudo-code or actual)
- [ ] Comprehensive analysis report created
- [ ] Report delivered to manager

## Files to Investigate

**Primary (expected):**
- `src/main/flight/pid.c` - PID controllers and gain scaling
- `src/main/fc/settings.yaml` - `apa_pow` and related settings
- `src/main/sensors/pitotmeter.c` - Airspeed sensor readings
- `src/main/navigation/navigation.c` - Cruise speed reference
- `src/main/flight/servos.c` - Fixed-wing control surfaces

**Search keywords:**
- `apa_pow`
- `fixedWingAPA`
- `PIFF`
- `airspeed`
- `pitot`
- `TPA` (Throttle PID Attenuation - older mechanism)

## Key Questions to Answer

1. **Current Implementation:**
   - What is the exact formula for gain scaling?
   - What is the cruise speed reference point?
   - How is `apa_pow` used in the calculation?
   - What is the actual percentage range (reported as 200% increase)?

2. **Failure Detection:**
   - Are there any existing airspeed sanity checks?
   - Is there a minimum valid airspeed threshold?
   - Does the code detect pitot blockage?
   - Are there other sensors that could validate airspeed?

3. **Solution Options:**
   - Which solution best balances safety and functionality?
   - Can we detect pitot failure reliably?
   - Should gains ever increase below cruise speed?
   - What's the migration path for existing users?

4. **Safety Considerations:**
   - What are all the failure modes?
   - How can we make it fail-safe?
   - Should there be a setting to disable gain increases entirely?
   - Should there be a maximum gain increase limit?

## Expected Deliverables

**Analysis Report:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

**Report Contents:**
1. Executive summary
2. Current behavior analysis
3. Problem statement and safety concerns
4. Code analysis (locations, formulas, flow)
5. Evaluation of suggested solutions
6. Recommended solution
7. Proposed code changes (detailed pseudo-code or actual code snippets)
8. Testing recommendations
9. Backward compatibility analysis
10. References (issue, PDF, wiki)

## Priority Justification

MEDIUM-HIGH priority because:
- **Safety critical:** Pitot failure is common and current behavior is dangerous
- **User reported:** Real-world problem with detailed failure description
- **INAV 9.x new feature:** Recently introduced, good time to fix
- **Well documented:** User provided detailed analysis and suggestions
- However: Analysis only, not implementation, so not CRITICAL
- Requires careful analysis before making changes

## Notes

**This is an ANALYSIS project, not an implementation project.**

The goal is to:
1. Understand the problem thoroughly
2. Evaluate all options
3. Make a well-reasoned recommendation
4. Propose specific code changes

A separate implementation project/PR will follow if the analysis recommends changes.

**Safety First:**
This affects flight safety in failure conditions. The analysis should prioritize fail-safe behavior over performance optimization.

**Consider All Users:**
Some users may have tuned their aircraft assuming the current behavior. Any changes should consider backward compatibility or provide migration guidance.

**PDF Document:**
The PDF likely contains additional technical analysis or diagrams. Make sure to extract all relevant information from it.

## Related

- INAV 9.x Fixed Wing APA feature
- Wiki: https://github.com/iNavFlight/inav/wiki/PID-Attenuation-and-scaling#Fixedwing-APA
- Issue #11208: https://github.com/iNavFlight/inav/issues/11208
