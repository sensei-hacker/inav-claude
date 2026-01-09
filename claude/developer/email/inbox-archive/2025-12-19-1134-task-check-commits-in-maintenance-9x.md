# Task Assignment: Check if Incorrectly Merged Commits Are in maintenance-9.x

**Date:** 2025-12-19 11:34
**Project:** inav / inav-configurator
**Priority:** High
**Estimated Effort:** 1-2 hours

## Task

From your previous analysis, you identified PRs that were incorrectly merged to master instead of maintenance branches. Now check whether the commits from those PRs also ended up in the maintenance-9.x branch (either through cherry-picking or merge).

## PRs to Check

### Recent (Last 2 Weeks):
**Configurator:**
- PR #2463 - "Flight axis override test + idiot-proof mag alignment handling"

### Extended Period (Nov 20 - Dec 5):

**Firmware (10 PRs):**
- PR #11144 - "Maybe fix GPS recovery"
- PR #11143 - "Add JavaScript programming documentation"
- PR #11137 - "Normalize line endings in FLYSPARKF4V4"
- PR #11134 - "Add I2C compass driver for HUMMINGBIRD FC305"
- PR #11131 - "Update FlyingRC F4Wing Mini target"
- PR #11129 - "NEXUSX: USE_DSHOT_DMAR"
- PR #11127 - "NEXUSX: fix UART3/I2C2 resource conflict"
- PR #11122 - "Update references to control_profile"
- PR #11095 - "Dynamic Custom OSD Elements"
- PR #11092 - "New target: FlyingRC F4wing mini"

**Configurator (12 PRs):**
- PR #2442 - "transpiler: more tests"
- PR #2441 - "Fix analyzer/decompiler bugs"
- PR #2440 - "Fix undeclared variables in search.js"
- PR #2439 - "Add JavaScript Programming tab with transpiler"
- PR #2437 - "Fix 3D model loading in magnetometer tab"
- PR #2436 - "Restore checkMSPPortCount"
- PR #2434 - "Fix ESM conversion in search and logging tabs"
- PR #2433 - "STM32 DFU: Refactor and implement CLI-based reboot"
- PR #2432 - "Fix DFU flash cleanup callback"
- PR #2429 - "Cleanup old control_profile references"
- PR #2285 - "ESM modules & More"

## What to Do

For each PR, check if its commits are present in maintenance-9.x:

1. **Get the merge commit SHA for the PR** (from master)
2. **Check if that commit or its changes exist in maintenance-9.x**
3. **Report the status:**
   - ✅ In maintenance-9.x (already cherry-picked/merged)
   - ❌ NOT in maintenance-9.x (missing from 9.x releases)

## Method

You can use:
```bash
# Get commits from a PR merge
git log --oneline --grep="#11144" master

# Check if commit exists in maintenance-9.x
git branch -r --contains <commit-sha> | grep maintenance-9.x

# Or check if commit was cherry-picked (different SHA, same changes)
git log maintenance-9.x --oneline --grep="<search-term>"
```

## Success Criteria

- [ ] Checked all 23 PRs (10 firmware + 13 configurator)
- [ ] Documented which commits ARE in maintenance-9.x
- [ ] Documented which commits are MISSING from maintenance-9.x
- [ ] Provided summary table showing status of each PR
- [ ] Sent completion report with findings

## Why This Matters

If these commits are NOT in maintenance-9.x, they'll be missing from 9.x releases. We need to know:
- Which bug fixes are missing from 9.x
- Which features are missing from 9.x
- Whether we need to cherry-pick any important changes

---
**Manager**
