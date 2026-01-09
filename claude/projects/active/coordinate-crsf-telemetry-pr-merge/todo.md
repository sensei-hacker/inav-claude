# Todo List: Coordinate CRSF Telemetry PR Merge Strategy

## Phase 1: Communication

### Contact PR Authors

- [ ] Draft message to PR #11025 author (@gismo2004)
  - [ ] Explain frame 0x09 conflict discovered
  - [ ] Present analysis findings (simple baro vs combined baro/vario)
  - [ ] Recommend removing frame 0x09 from PR #11025
  - [ ] Emphasize value of Airspeed/RPM/Temp contributions
  - [ ] Link to developer analysis report
  - [ ] Suggest coordination with PR #11100

- [ ] Draft message to PR #11100 author (@skydevices-tech)
  - [ ] Inform about frame 0x09 analysis
  - [ ] Confirm combined Baro/Vario approach is preferred
  - [ ] Acknowledge airspeed deferral to PR #11025
  - [ ] Discuss merge timing coordination
  - [ ] Link to developer analysis report

- [ ] Draft message to INAV maintainers
  - [ ] Present conflict analysis summary
  - [ ] Recommend merge strategy (PR #11100 first, then #11025)
  - [ ] Offer test suite for validation
  - [ ] Provide technical rationale
  - [ ] Link to full developer analysis

### Post Messages

- [ ] Post comment on PR #11025
- [ ] Post comment on PR #11100
- [ ] Tag INAV maintainers for visibility
- [ ] Monitor for responses

## Phase 2: Test Suite Preparation

### Fix Compilation Issues

- [ ] Add missing header includes
  - [ ] `#include "sensors/battery.h"`
  - [ ] `#include "sensors/barometer.h"`
  - [ ] `#include "sensors/pitotmeter.h"`
  - [ ] `#include "sensors/esc_sensor.h"`
  - [ ] `#include "sensors/temperature.h"`

- [ ] Fix mock function signatures
  - [ ] Change `getEstimatedActualPosition()` return type to `float`
  - [ ] Update all navigation mock functions
  - [ ] Verify battery config types

- [ ] Add conditional compilation
  - [ ] `#ifdef CRSF_LEGACY_MODE` for PR #11100 features
  - [ ] Separate PR-specific tests

### Create Test Variants

- [ ] Create `telemetry_crsf_pr11025_unittest.cc`
  - [ ] Airspeed frame tests
  - [ ] RPM frame tests
  - [ ] Temperature frame tests

- [ ] Create `telemetry_crsf_pr11100_unittest.cc`
  - [ ] Combined Baro/Vario tests
  - [ ] Legacy mode toggle tests
  - [ ] GPS altitude mode switching tests

- [ ] Create `telemetry_crsf_combined_unittest.cc`
  - [ ] Integration tests for both PRs merged
  - [ ] Frame scheduler tests
  - [ ] Full telemetry sequence tests

### Verify Build

- [ ] Build test suite against PR #11025 branch
- [ ] Build test suite against PR #11100 branch
- [ ] Document expected results for each

## Phase 3: Documentation

- [ ] Document agreed merge strategy
  - [ ] Merge order decision
  - [ ] Coordination timeline
  - [ ] PR author agreements

- [ ] Update test suite documentation
  - [ ] Test coverage matrix
  - [ ] Build instructions
  - [ ] Expected pass/fail results

- [ ] Create validation checklist
  - [ ] Pre-merge validation steps
  - [ ] Post-merge verification
  - [ ] Regression testing items

- [ ] Document in project summary
  - [ ] Final merge approach
  - [ ] PR author responses
  - [ ] Maintainer decisions

## Phase 4: Follow-up & Closure

- [ ] Monitor PR merge activity
  - [ ] Check for PR #11100 merge
  - [ ] Check for PR #11025 rebase/update
  - [ ] Verify no merge conflicts

- [ ] Run validation tests
  - [ ] Test against merged code
  - [ ] Verify all frame types working
  - [ ] Check legacy mode functionality

- [ ] Final documentation
  - [ ] Update project status to COMPLETED
  - [ ] Archive to `archived_projects/`
  - [ ] Send completion report to Manager
  - [ ] Update INDEX.md

## Completion Checklist

### Communication Complete
- [ ] All PR authors contacted
- [ ] Maintainers informed
- [ ] Merge strategy agreed
- [ ] Coordination documented

### Test Suite Ready
- [ ] Compilation issues fixed
- [ ] PR-specific tests created
- [ ] Integration tests created
- [ ] Build verification complete

### Documentation Complete
- [ ] Merge strategy documented
- [ ] Test suite documented
- [ ] Validation checklist created

### Project Closure
- [ ] PRs merged successfully
- [ ] Tests validate merged code
- [ ] No conflicts or regressions
- [ ] Completion report sent
- [ ] Project archived

---

## Notes

**Developer provided:**
- Complete analysis of both PRs (2025-12-06)
- 38-test validation suite
- Build test results
- Frame implementation details
- Clear merge recommendation

**Manager decides:**
- When to contact PR authors
- Communication approach/tone
- Escalation to maintainers if needed

**Success = Both PRs merged cleanly with all features working**
