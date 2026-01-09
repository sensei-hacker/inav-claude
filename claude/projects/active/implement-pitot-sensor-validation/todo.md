# Todo List: Implement Pitot Sensor Validation

## Phase 0: Blackbox Analysis of Real-World Failure (NEW - 2026-01-07)

- [ ] Download files from PR #11222 comment
  - [ ] Go to https://github.com/iNavFlight/inav/pull/11222
  - [ ] Find comment by **quadlawnmowerman-coder**
  - [ ] Download the diff file attached to the comment
  - [ ] Download blackbox log `LOG00002.TXT` attached to the comment
  - [ ] Save to `claude/developer/investigations/pitot-validation-pr11222/`

- [ ] Decode and analyze blackbox log
  - [ ] Run blackbox_decode on LOG00002.TXT
  - [ ] Extract airspeed-related fields (pitot, GPS groundspeed, wind estimates)
  - [ ] Identify time period where pitot failure occurred
  - [ ] Compare pitot airspeed vs GPS groundspeed during failure
  - [ ] Document discrepancy magnitude and patterns

- [ ] Determine why failure was not detected
  - [ ] Review current `pitotValidForAirspeed()` logic
  - [ ] Identify what checks exist vs what failed
  - [ ] Note specific thresholds that were not exceeded
  - [ ] Document gaps in current detection

- [ ] Replay/simulate airspeed data (if possible)
  - [ ] Use `/replay-blackbox` skill or related tools
  - [ ] Feed sensor data through proposed validation logic
  - [ ] Test detection algorithms against real failure data
  - [ ] Measure false positive/negative rates

- [ ] Create analysis report
  - [ ] Timeline of pitot failure in log
  - [ ] Data comparison (pitot vs GPS)
  - [ ] Root cause of missed detection
  - [ ] Recommended detection thresholds based on real data
  - [ ] Review quadlawnmowerman-coder's diff for insights

- [ ] Update implementation plan if needed
  - [ ] Refine algorithm based on analysis
  - [ ] Adjust thresholds based on real data
  - [ ] Update summary.md with findings

## Phase 1: Core Validation (4-5 hours)

- [ ] Read analysis document
  - [ ] Open `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`
  - [ ] Read "Solution 3: GPS-Based Airspeed Sanity Checks" section
  - [ ] Read "Recommended Solution - Issue 1: Pitot Sensor Validation"
  - [ ] Understand proposed algorithm
  - [ ] Note edge cases and considerations

- [ ] Understand current code
  - [ ] Read `src/main/sensors/pitotmeter.c:315-323`
  - [ ] Understand `pitotValidForAirspeed()` current implementation
  - [ ] Identify where to add GPS sanity check
  - [ ] Review airspeed calculation code

- [ ] Implement GPS sanity check function
  - [ ] Create `pitotPassesGpsSanityCheck()` function
  - [ ] Add GPS availability check
  - [ ] Implement groundspeed vs pitot comparison
  - [ ] Add wind estimator integration (if available)
  - [ ] Calculate expected airspeed range
  - [ ] Add margin for uncertainty
  - [ ] Return true/false for validation result

- [ ] Add failure state tracking
  - [ ] Define `pitotFailureState_e` enum
  - [ ] Add PITOT_FAIL_SANITY state
  - [ ] Add global failure state variable
  - [ ] Update state when sanity check fails
  - [ ] Clear state when validation passes

- [ ] Integrate into pitotValidForAirspeed()
  - [ ] Call GPS sanity check
  - [ ] Update failure state on fail
  - [ ] Return false if sanity check fails
  - [ ] Maintain existing checks

- [ ] Initial SITL testing
  - [ ] Build firmware with changes
  - [ ] Test normal flight (pitot working)
  - [ ] Simulate blocked pitot (low reading)
  - [ ] Verify sanity check detects failure

## Phase 2: Automatic Fallback (2-3 hours)

- [ ] Integrate into APA code
  - [ ] Find APA airspeed usage in `src/main/flight/pid.c`
  - [ ] Add validation check before using pitot airspeed
  - [ ] Use virtual airspeed when validation fails
  - [ ] Ensure seamless transition

- [ ] Test fallback behavior
  - [ ] SITL with blocked pitot scenario
  - [ ] Verify automatic switch to virtual airspeed
  - [ ] Check that APA uses correct airspeed
  - [ ] Verify gains are appropriate
  - [ ] Check for control glitches during transition

- [ ] Test recovery
  - [ ] Simulate pitot recovery (blocked → unblocked)
  - [ ] Verify validation detects recovery
  - [ ] Check smooth transition back to pitot
  - [ ] Ensure no oscillation between states

## Phase 3: OSD Warning (1-2 hours)

- [ ] Add OSD warning element
  - [ ] Locate OSD code (`src/main/io/osd.c`)
  - [ ] Add pitot failure warning display
  - [ ] Display "PITOT FAIL - VIRTUAL" text
  - [ ] Position appropriately on screen
  - [ ] Make prominent (blinking if possible)

- [ ] Implement warning logic
  - [ ] Check pitot failure state
  - [ ] Display warning when PITOT_FAIL_SANITY
  - [ ] Clear warning when pitot validates
  - [ ] Test in SITL OSD

- [ ] Test OSD display
  - [ ] SITL with blocked pitot
  - [ ] Verify warning appears
  - [ ] Verify warning clears on recovery
  - [ ] Check warning visibility/prominence

## Phase 4: Edge Cases and Polish (2-3 hours)

- [ ] Handle wind uncertainty
  - [ ] Check if wind estimator is available
  - [ ] Use conservative margins when wind unknown
  - [ ] Test in high wind scenarios
  - [ ] Verify no false positives

- [ ] Add hysteresis
  - [ ] Prevent rapid oscillation valid/invalid
  - [ ] Require sustained failure to trigger
  - [ ] Require sustained recovery to clear
  - [ ] Test hysteresis behavior

- [ ] Handle takeoff/landing
  - [ ] Low airspeed edge cases near stall
  - [ ] Consider minimum threshold for validation
  - [ ] Test takeoff and landing scenarios
  - [ ] Ensure safe behavior

- [ ] Add rate-of-change validation
  - [ ] Define maximum realistic airspeed change
  - [ ] Detect sudden unrealistic jumps
  - [ ] Track previous pitot reading
  - [ ] Test with realistic flight maneuvers

- [ ] Add parameters (if needed)
  - [ ] Consider settings.yaml entries
  - [ ] Enable/disable sanity check
  - [ ] Adjustable margin
  - [ ] Document parameters

## Phase 5: Testing and Documentation (2-3 hours)

- [ ] Comprehensive SITL testing
  - [ ] Scenario 1: Blocked pitot at cruise
  - [ ] Scenario 2: Pitot recovery
  - [ ] Scenario 3: Windy conditions
  - [ ] Scenario 4: Aggressive maneuvers
  - [ ] Scenario 5: Takeoff/landing
  - [ ] Document all test results

- [ ] Hardware testing (if available)
  - [ ] Cover pitot tube physically
  - [ ] Observe automatic fallback
  - [ ] Verify OSD warning
  - [ ] Test flight with blocked pitot
  - [ ] Verify aircraft remains controllable
  - [ ] Test recovery

- [ ] Regression testing
  - [ ] Verify no impact when pitot working normally
  - [ ] Check virtual airspeed still works without GPS
  - [ ] Ensure existing functionality unchanged
  - [ ] Test on multiple targets

- [ ] Update documentation
  - [ ] Update sensor documentation
  - [ ] Document pitot validation feature
  - [ ] Explain GPS sanity checking
  - [ ] Document OSD warning
  - [ ] Add troubleshooting section

- [ ] Code review preparation
  - [ ] Add clear code comments
  - [ ] Explain algorithm in comments
  - [ ] Document edge cases
  - [ ] Add references to issue #11208
  - [ ] Clean up any debug code

## Phase 6: Pull Request and Completion

- [ ] Create pull request
  - [ ] Write clear PR description
  - [ ] Reference GitHub issue #11208
  - [ ] Reference analysis document
  - [ ] Include test results
  - [ ] Request review

- [ ] Address code review
  - [ ] Respond to reviewer comments
  - [ ] Make requested changes
  - [ ] Re-test if needed
  - [ ] Update PR

- [ ] Completion report
  - [ ] Summary of implementation
  - [ ] Test results summary
  - [ ] Any issues encountered
  - [ ] Recommendations for users
  - [ ] Report to manager

## Notes

**Critical Safety Feature:**
- This makes aircraft flyable when pitot fails
- Pitot failures are common and dangerous
- Take time to get it right

**Conservative Approach:**
- Avoid false positives
- Use wide margins
- Only validate when GPS reliable
- Require sustained failures

**Testing is Critical:**
- Test all edge cases
- Hardware testing if possible
- Document all scenarios
- Ensure robust behavior
