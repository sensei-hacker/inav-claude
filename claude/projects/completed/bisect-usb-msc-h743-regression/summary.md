# Project: Bisect USB MSC Mode Regression on H743

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Investigation / Git Bisect
**Created:** 2025-12-18
**Estimated Time:** 3-5 hours

## Overview

Use git bisect to find the commit that broke USB Mass Storage (MSC) mode on H743 microcontrollers between INAV versions 8.0.0 and 8.0.1.

## Problem

**Issue:** https://github.com/iNavFlight/inav/issues/10800

**Symptoms:**
- USB MSC mode fails to display a storage drive on H743 MCUs
- Device Manager shows "Virtual COM Port in FS Mode" with missing drivers (Code 28)
- Problem started in version 8.0.1, was working in 8.0.0

**Affected Hardware:**
- H743 microcontrollers (MATEK H743, AET H743-Wing, Holybro Kakute H743, GEPRC TAKER H743)
- Other platforms (F405, AT32, F765) work normally

**Suspected Cause:** Pull Request #10706

## Objectives

1. Use git bisect to find the exact commit that broke USB MSC mode
2. Identify the code change that caused the regression
3. Document the root cause
4. Recommend a fix or provide findings to maintainers
5. Test the bisect result if possible (optional, may require H743 hardware)

## Scope

**In Scope:**
- Git bisect between tags 8.0.0 and 8.0.1 (83 commits)
- Code analysis of the problematic commit
- Documentation of findings
- Review of suspected PR #10706

**Out of Scope:**
- Implementing the fix (separate task after root cause identified)
- Testing on real H743 hardware (unless available)
- Fixing other USB-related issues

## Implementation Steps

1. **Setup bisect**
   - Start git bisect between 8.0.0 (good) and 8.0.1 (bad)
   - Understand the commit range (~83 commits, ~7 bisect steps)

2. **Define test criteria**
   - How to identify if MSC mode is broken in a commit
   - Code patterns to look for (H743-specific USB code)
   - Review PR #10706 as suspected culprit

3. **Run bisect**
   - Mark commits as good/bad based on code analysis
   - Focus on USB MSC, H743, and Device Manager related changes
   - Track the bisect process

4. **Analyze result**
   - Identify the first bad commit
   - Review the diff for that commit
   - Understand what changed and why it broke H743
   - Connect to PR #10706 if relevant

5. **Document findings**
   - Create report with commit SHA, diff, and analysis
   - Explain the root cause
   - Recommend fix approach
   - Post findings to issue #10800

## Success Criteria

- [ ] Git bisect completed successfully
- [ ] First bad commit identified with SHA
- [ ] Code change analyzed and understood
- [ ] Root cause documented
- [ ] Findings reported to manager
- [ ] Optional: Findings posted to GitHub issue #10800

## Estimated Time

3-5 hours:
- Setup and research: 30 minutes
- Git bisect execution: 1-2 hours (~7 bisect steps)
- Code analysis: 1-1.5 hours
- Documentation: 30-60 minutes

## Priority Justification

HIGH priority - This is a confirmed regression affecting multiple popular H743 flight controllers. USB MSC mode is critical for accessing blackbox logs. Issue has been confirmed and assigned to a maintainer, so finding the root cause will help with the fix.

## Resources

**Issue:** https://github.com/iNavFlight/inav/issues/10800

**Documentation:** https://github.com/iNavFlight/inav/blob/master/docs/USB_Mass_Storage_(MSC)_mode.md

**Suspected PR:** https://github.com/iNavFlight/inav/pull/10706

**Version Range:**
- Good: 8.0.0 (tag)
- Bad: 8.0.1 (tag)
- Commits to bisect: 83

**Bisect Command:**
```bash
cd inav
git bisect start
git bisect bad 8.0.1
git bisect good 8.0.0
# Then mark each commit as good/bad based on code analysis
```

## Notes

**USB MSC Mode Background:**
- Allows flight controllers to mount as USB storage devices
- Enables direct access to blackbox logs via file system
- Activated via CLI command `msc`
- Should present as storage device after 10-15 seconds

**H743 Specifics:**
- STM32H743 microcontroller family
- Popular in modern flight controllers
- Different USB implementation than F4/F7 series

**Testing Without Hardware:**
- Bisect can be done through code analysis
- Look for H743-specific USB changes
- Review Device Manager / USB descriptor changes
- Check for conditional compilation changes affecting H743

**Follow-up:**
- After finding the commit, a fix implementation task may be needed
- Results should be shared with issue #10800 and maintainer bkleiner
