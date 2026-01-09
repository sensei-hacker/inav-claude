# Task Assignment: Create Test Script to Reproduce Issue #9912

**Date:** 2025-12-23 00:29
**Project:** inav (firmware) - Testing
**Priority:** Medium
**Estimated Effort:** 3-5 hours

## Task

Create a test script to reproduce the bug described in GitHub issue #9912. Use SITL in simulator mode if helpful.

**Issue:** https://github.com/iNavFlight/inav/issues/9912

## Objectives

1. **Understand the issue** - Read and analyze issue #9912 to understand:
   - What the bug is
   - Steps to reproduce
   - Expected vs actual behavior
   - Any specific conditions or configurations needed

2. **Design test approach** - Determine:
   - Can this be reproduced with SITL?
   - What simulator mode is needed (if any)?
   - What test inputs/scenarios are required?
   - How to verify the bug occurs?

3. **Create test script** - Develop:
   - Automated test script (Python/Bash)
   - SITL configuration if needed
   - Simulator setup if needed
   - Clear reproduction steps

4. **Verify reproduction** - Confirm:
   - Script reliably reproduces the issue
   - Bug behavior is clearly observable
   - Test output shows the problem

## Suggested Approach

### Option 1: SITL with Simulator
If the issue involves flight behavior, navigation, or sensors:
- Use SITL built with simulator support
- Configure appropriate simulator (RealFlight, X-Plane, or mock)
- Script the test scenario
- Monitor SITL output/state

### Option 2: SITL Standalone
If the issue can be reproduced without flight simulation:
- Use standalone SITL
- Send MSP commands to configure/trigger the issue
- Monitor behavior via MSP or CLI

### Option 3: Hardware Test
If SITL cannot reproduce the issue:
- Document why SITL is insufficient
- Create hardware test procedure instead

## Test Script Requirements

**The script should:**
- Be automated (minimal manual intervention)
- Have clear setup instructions
- Show clear pass/fail output
- Be reproducible (same result each run)
- Include cleanup (restore state after test)

**Script should output:**
- Test scenario description
- Steps being executed
- Expected behavior
- Actual behavior
- Pass/fail result

## Deliverables

1. **Test script** - Executable script to reproduce the issue
   - Location: `claude/developer/test_tools/` or appropriate location
   - Language: Python or Bash (your choice)
   - Documentation: README explaining usage

2. **Configuration files** - Any needed config files for SITL/simulator

3. **Report** - Brief report including:
   - Summary of issue #9912
   - Test approach chosen (SITL/simulator/hardware)
   - How the test reproduces the issue
   - Test output showing the bug
   - Any limitations or edge cases

## Success Criteria

- [ ] Read and understood issue #9912
- [ ] Determined best approach for reproduction
- [ ] Created automated test script
- [ ] Script successfully reproduces the issue
- [ ] Test output clearly shows the bug
- [ ] Documentation explains how to run the test
- [ ] Sent completion report

## Resources

**SITL Documentation:**
- Using SITL: Check existing SITL scripts in the project
- Simulator mode: `build-sitl` skill may be helpful
- MSP library: Use mspapi2 for MSP communication

**Testing Tools:**
- Existing test scripts in `claude/developer/test_tools/`
- CRSF/MSP testing infrastructure already available

## Notes

- **Use existing tools** where possible (mspapi2, existing test infrastructure)
- **Document limitations** if the issue can't be fully reproduced in SITL
- **Keep it simple** - Focus on reproducing the core issue, not every edge case
- **Make it reusable** - Script may be useful for regression testing after fix

## Why This Matters

Automated reproduction of bugs:
- Helps verify the bug exists
- Provides baseline for testing fixes
- Enables regression testing
- Documents the issue clearly
- May reveal root cause during investigation

---
**Manager**
