# Task: Fix Critical Transpiler API Operand Mismatches

**Priority:** CRITICAL
**Estimated Complexity:** Complex
**Assigned Date:** 2025-11-23

## Context

Excellent work completing the documentation project! Now it's time to tackle the **critical bug** you discovered in your audit: API operand value mismatches that cause incorrect code generation.

**Project Location:** `claude/projects/fix-transpiler-api-mismatches/`

This is a high-priority bug fix that affects user code correctness. When users write JavaScript to control their aircraft, the transpiler is currently generating logic conditions with wrong operand values, causing their code to read/write incorrect flight parameters.

## The Critical Bug (Reminder)

Users writing this:
```javascript
if (flight.yaw > 1800) {  // Check yaw angle
  // ...
}
```

Currently get this generated:
```
logic 0 1 -1 2 2 17 0 1800 0  // operand 17 = IS_ARMED, NOT YAW!
```

This reads `IS_ARMED` instead of `YAW` (which should be operand 40)!

## Your Task

Work through the project systematically following the TODO checklist in `claude/projects/fix-transpiler-api-mismatches/todo.md`.

### Phase 1: Investigation & Analysis (START HERE)

**Critical first steps:**

1. **Verify the bug exists**
   - Set up the test environment in `bak_inav-configurator/`
   - Create a test case with `flight.yaw`
   - Run it through the transpiler
   - Confirm it generates operand value 17 (wrong) instead of 40

2. **Understand the root cause**
   - Examine `js/transpiler/api/definitions/flight.js`
   - Compare with `js/transpiler/transpiler/inav_constants.js`
   - Document all mismatches you find
   - Understand why they're out of sync

3. **Research the fix strategy**
   - Evaluate whether to refactor to use constants vs manual fix
   - Test if constants can be imported (check for circular dependencies)
   - Create a proof-of-concept with one parameter
   - Recommend the best approach

**Deliverable for Phase 1:**
Send me a status report with:
- Bug verification results (with evidence)
- Complete list of all operand mismatches found
- Recommended fix strategy with rationale
- Any blockers or concerns

## Key Focus Areas

### 7 Critical Mismatches to Fix

| Parameter | Current (Wrong) | Correct Value |
|-----------|-----------------|---------------|
| yaw | 17 | 40 |
| heading | 17 | 40 |
| isArmed | 18 | 17 |
| isAutoLaunch | 19 | 18 |
| isFailsafe | 20 | 24 |
| gpsSats | 9 | 8 |
| groundSpeed | 11 | 9 |

### 25+ Missing Parameters to Add

From `inav_constants.js` FLIGHT_PARAM:
- SPEED_3D, AIR_SPEED, IS_RTH, IS_LANDING
- CRSF telemetry parameters
- AGL/rangefinder parameters
- Profile/mixer parameters
- And more (see project summary.md)

### Validation System to Create

Must prevent this from happening again:
- Automated tests comparing API defs to constants
- Round-trip transpile/decompile tests
- CI/CD integration

## Important Guidelines

### Investigation First, Then Fix

**DO NOT jump straight to fixing!** This is a critical bug affecting user safety. We need to:
1. Fully understand the problem
2. Verify against actual INAV firmware
3. Design the right solution
4. Get approval before implementing

### Check Other API Files Too

Don't assume only `flight.js` has this problem. Check:
- `override.js`
- `rc.js`
- `waypoint.js`
- Any other definition files

### Consider Backwards Compatibility

Think about:
- Are there existing user scripts with this bug?
- Do we need a migration tool?
- Should we warn users about the fix?
- Breaking change communication strategy

### Testing is Critical

This bug was silent (no errors). Your fix must include:
- Automated validation tests
- Round-trip verification
- Real-world testing on SITL
- Documentation of test results

## Phased Approach

Follow the TODO checklist phases:

**Phase 1: Investigation** (Do this now)
- Verify bug
- Understand scope
- Research fix strategy
- Send status report

**Phase 2: Design** (After approval)
- Detailed implementation plan
- Test strategy
- Migration approach

**Phase 3: Implementation** (After design approval)
- Fix critical mismatches
- Add missing parameters
- Verify other API files

**Phase 4: Testing**
- Create automated tests
- Round-trip verification
- Manual testing

**Phase 5: Documentation & PR**

## Communication

**Send status reports after each phase:**
- Investigation findings → `claude/manager/inbox/`
- Design proposal → Ask for approval
- Implementation progress → Regular updates
- Testing results → Final report

**Ask questions immediately if:**
- You find something unexpected
- Firmware values don't make sense
- You need clarification on approach
- You discover additional issues

## Success Criteria

This project is done when:
- [ ] All 7 critical mismatches are fixed
- [ ] All 25+ missing parameters are added
- [ ] Automated validation tests exist and pass
- [ ] Round-trip tests verify correctness
- [ ] Other API files verified/fixed
- [ ] Documentation updated
- [ ] PR created and merged

## Resources

**Project Files:**
- `claude/projects/fix-transpiler-api-mismatches/summary.md` - Complete project overview
- `claude/projects/fix-transpiler-api-mismatches/todo.md` - Detailed task checklist

**Code Location:**
- `bak_inav-configurator/js/transpiler/api/definitions/flight.js` - Primary file to fix
- `bak_inav-configurator/js/transpiler/transpiler/inav_constants.js` - Source of truth

**Reference:**
- Your audit report: `claude/manager/inbox/2025-11-23-transpiler-documentation-review-report.md`
- INAV firmware repository (may need to reference)

## Timeline Expectations

This is complex and critical. Take the time needed to:
- Investigate thoroughly
- Design the right solution
- Test comprehensively
- Document properly

Quality over speed. This affects user safety.

## Next Steps

1. Read the project summary and TODO
2. Set up test environment
3. Begin Phase 1: Investigation
4. Send status report when Phase 1 is complete

This is important work. Users are relying on the transpiler to generate correct code for their aircraft. Let's make sure we get this right.

Good luck!

---

**Manager Note:** This is our highest priority bug fix. The documentation is now clean, so you can focus fully on this critical issue.
