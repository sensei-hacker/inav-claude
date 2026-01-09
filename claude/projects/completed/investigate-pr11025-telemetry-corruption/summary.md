# Project: Investigate PR #11025 Telemetry Corruption

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Investigation / Root Cause Analysis
**Created:** 2025-12-16
**Estimated Time:** 4-6 hours

## Overview

Investigate why PR #11025 (adding airspeed, RPM, and temperature telemetry) caused existing telemetry values to stop being received, leading to its revert the same day via PR #11139.

## Problem

**Background:**
- PR #11025 added CRSF telemetry support for:
  - Airspeed (frame 0x0A)
  - RPM (frame 0x0C)
  - Temperature (frame 0x0D)
- After merging, users reported losing "all esc telemetry sensors as well as alt and vspeed"
- Only receiver telemetry remained functional
- PR was reverted same day (November 28, 2025)

**Key Clue:**
- Code reviewer warned about "invalid frame emission when no payload data existed"
- This suggests empty or malformed frames corrupted the telemetry stream

**Impact:**
- Existing telemetry stopped working (altitude, vspeed, ESC sensors)
- CRSF protocol stream became corrupted
- Feature had to be completely reverted

## Objectives

1. Analyze the code changes in PR #11025
2. Identify why "invalid frame emission" corrupted the telemetry stream
3. Determine root cause (likely: sending frames when sensors unavailable)
4. Document the specific failure mechanism
5. Recommend fix strategy for future re-implementation

## Scope

**In Scope:**
- Code analysis of PR #11025 changes
- Understanding CRSF frame scheduling and sensor availability checks
- Identifying missing validation/checks that allowed corrupt frames
- Using existing CRSF test tools to understand the issue
- Documenting root cause and fix recommendations

**Out of Scope:**
- Implementing the fix (separate follow-up task)
- Testing on real hardware
- Re-implementing the feature

## Implementation Steps

1. Review PR #11025 code changes
   - Examine frame generation functions
   - Check sensor availability validation
   - Review frame scheduling logic
2. Compare with working telemetry frames (GPS, Battery, Attitude)
   - How do they check sensor availability?
   - What happens when sensor is missing?
3. Identify the bug
   - Missing sensor availability check?
   - Sending empty frames?
   - Incorrect frame length calculation?
4. Understand failure mechanism
   - How do empty/malformed frames corrupt CRSF stream?
   - Why did other telemetry stop working?
5. Document findings and recommend fix

## Success Criteria

- [ ] Root cause identified and documented
- [ ] Specific code issue pinpointed
- [ ] Failure mechanism explained (why it corrupted other telemetry)
- [ ] Fix strategy recommended
- [ ] Report delivered to manager

## Estimated Time

4-6 hours:
- PR code analysis: 1-2 hours
- CRSF protocol understanding: 1 hour
- Root cause identification: 1-2 hours
- Documentation and recommendations: 1 hour

## Priority Justification

HIGH priority - Understanding why this failed is critical before attempting to re-implement these important telemetry features. Users need airspeed, RPM, and temperature telemetry, but we must ensure it doesn't break existing functionality.

## Resources Available

**Developer has extensive CRSF testing infrastructure:**
- CRSF telemetry test tools in `claude/test_tools/inav/crsf/`
- Bidirectional RC/telemetry test scripts
- Frame parsing and validation tools
- Comprehensive test plan documentation
- MSP configuration automation

**Documentation:**
- `claude/developer/crsf-telemetry-test-plan.md`
- `claude/developer/crsf-telemetry-msp-config-guide.md`
- `claude/developer/crsf-telemetry-bidirectional-complete.md`
