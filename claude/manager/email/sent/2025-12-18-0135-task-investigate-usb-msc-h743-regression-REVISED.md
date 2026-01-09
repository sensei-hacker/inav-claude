# Task Assignment: Investigate USB MSC Mode Regression on H743 (REVISED)

**Date:** 2025-12-18 01:35 (REVISED)
**Project:** bisect-usb-msc-h743-regression
**Priority:** HIGH
**Estimated Effort:** 2-4 hours
**Branch:** Investigation only

## Task

Investigate and identify the commit that broke USB Mass Storage (MSC) mode on H743 microcontrollers between INAV versions 8.0.0 and 8.0.1.

## Background

**Issue:** https://github.com/iNavFlight/inav/issues/10800

Users report that USB MSC mode is broken on H743 flight controllers starting in version 8.0.1. It was working correctly in version 8.0.0.

**Symptoms:**
- No storage drive appears when MSC mode is entered
- Device Manager shows "Virtual COM Port in FS Mode" with missing drivers (Code 28)
- Only affects H743 MCUs (MATEK H743, AET H743-Wing, Holybro Kakute H743, GEPRC TAKER H743)
- Other platforms (F405, AT32, F765) work normally

**Suspected Cause:** Pull Request #10706

**Version Range:**
- Good: 8.0.0 (tag)
- Bad: 8.0.1 (tag)
- Commits between: 83 commits

## Important: Git Bisect Requires Testing

**Git bisect works by TESTING each commit**, not by guessing from code review. The bisect algorithm relies on real test results (good/bad) to efficiently narrow down the problem.

Since we don't have H743 hardware to test with, we have **three approach options**:

## Approach Options

### Option 1: Investigate Suspected PR #10706 (RECOMMENDED)

Start by investigating the suspected culprit directly:

**Steps:**
1. Review PR #10706: https://github.com/iNavFlight/inav/pull/10706
   - What changes were made?
   - Does it affect H743 USB code?
   - When was it merged? (between 8.0.0 and 8.0.1?)
2. Find the merge commit in the version range
3. Review the specific code changes for H743 USB/MSC
4. Analyze if this is the cause

**If PR #10706 is the culprit:**
- You've found it directly without bisect
- Analyze the changes and recommend fix

**If PR #10706 is NOT the culprit:**
- Move to Option 2

### Option 2: Manual Commit Review

Review commits between 8.0.0 and 8.0.1 looking for USB/H743 changes:

**Steps:**
```bash
cd inav
git log --oneline 8.0.0..8.0.1 > commits.txt
```

**Search for relevant commits:**
```bash
# Find USB-related commits
git log --oneline 8.0.0..8.0.1 --grep="USB\|MSC\|H743"

# Find commits that modified USB files
git log --oneline 8.0.0..8.0.1 -- '*usb*' '*msc*'

# Find commits that modified H743 target files
git log --oneline 8.0.0..8.0.1 -- 'src/main/target/*/target.h' | \
  xargs -I {} sh -c 'git show {} | grep -l H743 && echo {}'
```

**Review candidates:**
- Look at each USB/MSC/H743 related commit
- Analyze the diff: `git show <commit-sha>`
- Identify which one likely broke MSC mode

### Option 3: Proper Git Bisect (if we can build/test)

**Only use this if you can actually test each commit.**

This would require either:
- Building firmware for H743 target at each bisect point
- Having H743 hardware to test MSC mode
- Or a reliable code pattern that definitively identifies the bug

**Bisect steps (if testing is possible):**
```bash
cd inav
git bisect start
git bisect bad 8.0.1
git bisect good 8.0.0

# For each commit git presents:
# 1. Build for H743 target
# 2. Test MSC mode (or check for specific code pattern)
# 3. Mark: git bisect good/bad
# 4. Repeat until bisect finds first bad commit
```

**Don't use bisect if you're just guessing from code review** - that defeats the purpose and can lead to wrong conclusions.

## What to Do

**Recommended workflow:**

1. **Start with Option 1** - Investigate PR #10706
   - Review the PR thoroughly
   - Check if it matches the symptoms
   - Verify it was merged between 8.0.0 and 8.0.1

2. **If PR #10706 isn't conclusive**, use Option 2
   - Search for USB/MSC/H743 commits in the range
   - Review likely candidates manually
   - Identify the problematic commit

3. **Only use Option 3** (proper bisect) if:
   - You can build firmware for each commit
   - You have a reliable test method
   - You're not just guessing from code

## Analysis Focus

**What to look for in commits:**
- USB descriptor changes for H743
- MSC initialization code changes
- H743-specific USB configuration
- Conditional compilation changes affecting H743
- Device Manager / USB enumeration changes

**Key files to watch:**
- `src/main/drivers/usb_msc*` - MSC implementation
- `src/main/drivers/usb_core*` - USB core
- `src/main/target/*/target.h` - H743 targets
- `lib/main/STM32H7/` - H743 USB drivers
- Any USB descriptor or configuration files

## Deliverables

Once you've identified the problematic commit:

1. **Commit identification:**
   - SHA and commit message
   - Full diff of the change
   - Associated PR if applicable

2. **Root cause analysis:**
   - What was changed?
   - Why does it break H743 MSC mode?
   - Why doesn't it affect F4/F7?
   - Connection to user symptoms

3. **Fix recommendation:**
   - Should the commit be reverted?
   - Can it be fixed with conditional code?
   - What's the minimal fix needed?

4. **Report:**
   - Send findings to manager
   - Optionally post to issue #10800

## Success Criteria

- [ ] Problematic commit identified (via PR review or manual search)
- [ ] Root cause understood and documented
- [ ] Explanation of why it breaks H743 specifically
- [ ] Fix approach recommended
- [ ] Findings reported

## Notes

**Why not "bisect through code review"?**
- Git bisect requires actual testing, not guessing
- Without testing, it's just manual commit review
- "Guessing" at good/bad leads to wrong bisect results
- Better to investigate directly or search manually

**Most efficient approach:**
- Start with PR #10706 (suspected cause)
- If that's not it, search for USB/H743 commits
- Only use proper bisect if you can actually test

**Estimated Time:**
- Option 1 (PR investigation): 1-2 hours
- Option 2 (manual review): 2-3 hours
- Option 3 (proper bisect with testing): 3-5 hours

---
**Manager**
