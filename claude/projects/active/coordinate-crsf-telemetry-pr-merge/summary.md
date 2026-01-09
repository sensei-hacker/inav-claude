# Project: Coordinate CRSF Telemetry PR Merge Strategy

**Status:** 📋 TODO
**Priority:** MEDIUM-HIGH
**Type:** Coordination / PR Management
**Created:** 2025-12-07
**Estimated Time:** 2-4 hours

## Overview

Coordinate with PR authors to resolve frame 0x09 conflict between two CRSF telemetry PRs and ensure smooth merge into INAV maintenance-9.x branch.

## Problem

Developer analysis (2025-12-06) identified a merge conflict between two CRSF telemetry pull requests:

**PR #11025** (gismo2004/inav:crsf_telem):
- Implements: Airspeed (0x0A), RPM (0x0C), Temperature (0x0D)
- **Frame 0x09:** Simple barometer altitude only (2 bytes)
- No legacy mode support

**PR #11100** (skydevices-tech/inav:crsf_baroaltitude_and_vario):
- Implements: Combined Baro/Vario (0x09) with 3 bytes
- Legacy mode toggle for backward compatibility
- Airspeed implementation removed (deferred to PR #11025)

**Conflict:** Both PRs use frame type 0x09 with different implementations
- PR #11025: Simple altitude (2 bytes)
- PR #11100: Combined altitude + vario (3 bytes)

## Objectives

1. Alert PR authors about the frame 0x09 conflict
2. Recommend merge strategy to upstream maintainers
3. Ensure test suite is ready for validation
4. Document final merge decision

## Scope

**In Scope:**
- Communication with PR authors (@gismo2004, @skydevices-tech)
- Coordination with INAV maintainers
- Merge strategy recommendation
- Test suite preparation for final validation
- Documentation of merge approach

**Out of Scope:**
- Writing code for either PR (authors handle their implementations)
- Making merge decisions (maintainers decide)
- Direct PR review (maintainers' responsibility)

## Background

### Research Completed (2025-12-06)

Developer successfully analyzed both PR branches:
- Fetched and examined both implementations
- Build tested against test suite
- Identified all frame types and implementations
- Created 38-test validation suite

### Key Findings

**Complementary Features (No Conflict):**
- ✅ Airspeed (0x0A): PR #11025 implements, PR #11100 deferred - RESOLVED
- ✅ RPM (0x0C): Only in PR #11025 - No conflict
- ✅ Temperature (0x0D): Only in PR #11025 - No conflict
- ✅ Legacy mode: Only in PR #11100 - No conflict

**Conflicting Feature:**
- ⚠️ Barometer (0x09): Different implementations in each PR

### Developer's Recommendation

**Merge Order:** PR #11100 first, then PR #11025

**Rationale:**
1. PR #11100's combined Baro/Vario is more feature-complete
2. Legacy mode is important for backward compatibility
3. PR #11025 can easily drop its simple baro implementation
4. All other features in PR #11025 remain valuable (Airspeed, RPM, Temp)

## Implementation Steps

### Phase 1: Communication (1-2 hours)

1. Contact PR #11025 author (@gismo2004)
   - Inform about frame 0x09 conflict
   - Explain PR #11100 has more complete baro implementation
   - Suggest removing frame 0x09 from PR #11025
   - Emphasize value of Airspeed/RPM/Temp contributions

2. Contact PR #11100 author (@skydevices-tech)
   - Confirm frame 0x09 approach is preferred
   - Coordinate on merge timing
   - Discuss integration with PR #11025 features

3. Contact INAV maintainers
   - Present conflict analysis
   - Recommend merge strategy
   - Offer test suite for validation

### Phase 2: Test Suite Preparation (1 hour)

1. Fix test suite compilation issues identified:
   - Add missing includes (`sensors/battery.h`, etc.)
   - Fix mock function signatures (`float` not `int32_t`)
   - Add conditional compilation for PR-specific features

2. Create PR-specific test variants:
   - Tests for PR #11025 features (Airspeed, RPM, Temp)
   - Tests for PR #11100 features (Baro/Vario, Legacy mode)
   - Combined integration tests

### Phase 3: Documentation (30-60 minutes)

1. Document merge strategy decision
2. Update test suite documentation
3. Create validation checklist for merged code

### Phase 4: Follow-up (30 minutes)

1. Monitor PR merge activity
2. Verify no conflicts during actual merge
3. Run final test validation
4. Close project when complete

## Success Criteria

- [x] Research complete (Developer completed 2025-12-06)
- [x] PR #11100 telemetry testing complete (2025-12-07 - VALIDATED)
- [x] PR #11100 code analysis complete (2025-12-07 - Sensor check issue identified)
- [ ] PR #11100 sensor availability testing complete (in progress)
- [ ] PR authors contacted and informed
- [ ] Merge strategy agreed upon
- [ ] Test suite ready for validation
- [ ] One or both PRs merged without conflicts
- [ ] Test suite validates merged code
- [ ] Documentation updated

## Communication Approach

**Tone:** Collaborative, helpful, technically accurate

**Key Messages:**
- Both PRs provide valuable features
- Conflict is minor and easily resolved
- Developer analysis shows clear merge path
- Test suite ready to validate quality
- Community benefits from all contributions

**Avoid:**
- Criticizing either implementation
- Dictating merge order (recommend only)
- Overstepping maintainer authority

## Estimated Time

**Total:** 2-4 hours

- Phase 1 (Communication): 1-2 hours
- Phase 2 (Test prep): 1 hour
- Phase 3 (Documentation): 30-60 minutes
- Phase 4 (Follow-up): 30 minutes

## Priority Justification

**MEDIUM-HIGH Priority**

**Why Important:**
- Two valuable PRs blocked by minor conflict
- Community contributions need coordination
- Test suite provides quality assurance
- Clean merge benefits all users

**Why Not Critical:**
- Neither PR is merged yet (no urgent deadline)
- Conflict is resolvable with simple coordination
- Features are enhancements, not bug fixes

**Timeline:** Should coordinate within 1-2 weeks to maintain PR momentum

## Related Links

- PR #11025: https://github.com/iNavFlight/inav/pull/11025
- PR #11100: https://github.com/iNavFlight/inav/pull/11100
- Developer Analysis: `claude/manager/inbox-archive/2025-12-06-1630-test-results-crsf-prs.md`
- Test Suite: `inav/src/test/unit/telemetry_crsf_unittest.cc` (created)

## Notes

- Developer created 38-test validation suite during analysis
- Both PR authors are active (recent commits)
- Airspeed duplication already resolved by PR #11100 author
- ExpressLRS CRSF protocol documentation available for reference

### Testing Updates (2025-12-07)

**PR #11100 Baseline Testing:** ✅ COMPLETE
- SITL build successful with CRSF telemetry enabled
- 534 telemetry frames received in 10 seconds (53.4 Hz)
- Frame 0x09 (Combined Baro/Vario) validated at ~9Hz
- All standard CRSF frames present (Attitude, Battery, Flight Mode, Vario)
- Stream health: EXCELLENT

**PR #11100 Code Analysis:** ✅ COMPLETE
- Identified missing runtime sensor availability check
- Frame 0x09 sent without verifying baro/GPS availability
- Potential risk of sending garbage data when sensors unavailable
- Manager guidance: Complete sensor availability testing before contacting PR author
- Developer proceeding with edge case testing (GPS disabled, sensor init delay)

**PR #11025 Testing:** ❌ BLOCKED
- Build failure: Missing `pwmRequestMotorTelemetry` function in `esc_sensor.c`
- Cannot test until PR author fixes build issue
- Recommendation: Contact author about build failure
