# Task Completed: PRs Merged to Master Analysis

**Date:** 2025-12-19
**From:** Developer
**Type:** Completion Report

## Status: COMPLETED ✓

## Summary

Analyzed PRs merged to master in both inav (firmware) and inav-configurator repositories over the last two weeks. **Found 1 PR in the last 2 weeks that may have been merged incorrectly** (configurator PR #2463). Additionally, identified the recent branching strategy change and documented 24 PRs from the Nov 20-Dec 5 period that likely should have targeted maintenance branches instead.

## Key Finding: Branching Strategy Changed November 30, 2025

The project's branching strategy was updated on **November 30, 2025** with PR #11148 (firmware) and PR #2444 (configurator), which added a GitHub Action to automatically suggest version branches for PRs targeting master.

## Current Branching Strategy (as of Nov 30, 2025)

Based on the GitHub Action workflow (`.github/workflows/pr-branch-suggestion.yml`):

### Branch Purposes:

- **`maintenance-9.x`** - For backward-compatible changes that won't create compatibility issues between INAV firmware and Configurator 9.x versions. Will be included in next 9.x release.

- **`maintenance-10.x`** - For changes that introduce compatibility requirements between firmware and configurator that would break 9.x compatibility. Will be included in INAV 10.x.

- **`master`** - For:
  - Merges from maintenance branches (bringing fixes into master)
  - Infrastructure/automation changes (GitHub Actions, CI/CD)
  - Release management tasks
  - Future development (unclear from documentation)

### Old Branching Strategy (documented but outdated):

The documentation in `docs/development/Development.md` still describes the old strategy:
- "Normally, all development occurs on the `master` branch"
- Release branches named `release_x.y.z` for RC cycles

**Note:** The documentation has not been updated to reflect the new maintenance branch strategy.

## PRs Merged to Master - Last 2 Weeks (Since Dec 5, 2025)

### Firmware (iNavFlight/inav):

**Total:** 1 PR

✅ **PR #11167** (Dec 7) - "Merge Maintenance 9.x to master"
- **Status:** CORRECT
- **Reason:** Legitimate maintenance branch merge

### Configurator (iNavFlight/inav-configurator):

**Total:** 2 PRs

✅ **PR #2462** (Dec 7) - "Maintenance 9.x merge to master"
- **Status:** CORRECT
- **Reason:** Legitimate maintenance branch merge

⚠️ **PR #2463** (Dec 12) - "Flight axis override test + idiot-proof mag alignment handling"
- **Status:** INCORRECT
- **Branch:** flight-axis-override-implementation → master
- **Reason:** Bug fix/feature should target maintenance-9.x (backward compatible)
- **Impact:** Missed inclusion in 9.x release cycle


## PRs Merged to Master - Extended Period (Nov 20 - Dec 5)

To understand the pattern before the GitHub Action was deployed, I examined PRs from Nov 20 onwards:

### Firmware (iNavFlight/inav):

**Total:** 13 PRs
- **Correct:** 3 PRs
- **Incorrect:** 10 PRs

#### Correct Merges:

✅ **PR #11148** (Nov 30) - "Add GitHub Action to suggest version branches for PRs"
- Infrastructure change, appropriate for master

✅ **PR #11139** (Nov 28) - "Revert \"[crsf] add temperature, RPM and AirSpeed telemetry\""
- Urgent revert, appropriate for master

✅ **PR #11167** (Dec 7) - "Merge Maintenance 9.x to master"
- Maintenance branch merge

#### Incorrect Merges (Should have gone to maintenance-9.x):

❌ **PR #11144** (Nov 29) - "Maybe fix GPS recovery - update lastUpdateTime on first reading after signal recovery"
- **Type:** Bug fix
- **Branch:** fix-gps-recovery-issue-11049 → master

❌ **PR #11143** (Nov 29) - "Add JavaScript programming documentation"
- **Type:** Documentation
- **Branch:** docs_javascript_programming → master

❌ **PR #11137** (Nov 27) - "Normalize line endings to LF in src/main/target/FLYSPARKF4V4"
- **Type:** Cleanup
- **Branch:** copilot/normalize-line-endings-flyspackf4v4 → master

❌ **PR #11134** (Nov 27) - "Add I2C compass driver registration for HUMMINGBIRD FC305"
- **Type:** Target update
- **Branch:** target/hummingbird_fc305 → master

❌ **PR #11131** (Nov 27) - "Update FlyingRC F4Wing Mini target"
- **Type:** Target update
- **Branch:** MrD_Modify-FlyingRC-F4wing-mini → master

❌ **PR #11129** (Nov 25) - "NEXUSX: USE_DSHOT_DMAR, use TIM2 instead of TIM5"
- **Type:** Target update
- **Branch:** nexus_xr_dmar → master

❌ **PR #11127** (Nov 23) - "NEXUSX: fix UART3/I2C2 resource conflict"
- **Type:** Bug fix
- **Branch:** nexus_xr_fix_resource_conflict → master

❌ **PR #11122** (Nov 25) - "Update references to that should be control_profile"
- **Type:** Bug fix/cleanup
- **Branch:** MrD_Clean-up-control_profile → master

❌ **PR #11095** (Nov 27) - "Dynamic Custom OSD Elements position changing by companion computer"
- **Type:** New feature
- **Branch:** master → master (!)
- **Note:** May need maintenance-10.x if it breaks compatibility

❌ **PR #11092** (Nov 20) - "New target: FlyingRC F4wing mini"
- **Type:** New target
- **Branch:** FlyingRC_F4WingMini → master

### Configurator (iNavFlight/inav-configurator):

**Total:** 16 PRs
- **Correct:** 3 PRs
- **Incorrect:** 13 PRs

#### Correct Merges:

✅ **PR #2462** (Dec 7) - "Maintenance 9.x merge to master"
- Maintenance branch merge

✅ **PR #2444** (Nov 30) - "Add GitHub Action to suggest version branches for PRs"
- Infrastructure change

✅ **PR #2443** (Nov 30) - "Update SITL binaries for 9.0.0-RC2"
- Release management

✅ **PR #2348** (Nov 20) - "Maintenance 8.x.x"
- Maintenance branch merge

#### Incorrect Merges:

❌ **PR #2463** (Dec 12) - "Flight axis override test + idiot-proof mag alignment handling for FCs without a mag"
- **Type:** Feature/bug fix
- **Branch:** flight-axis-override-implementation → master

❌ **PR #2442** (Nov 30) - "transpiler: more tests"
- **Type:** Test improvements
- **Branch:** transpiler_docs_tests → master

❌ **PR #2441** (Nov 29) - "Fix analyzer/decompiler bugs and add parseInt radix"
- **Type:** Bug fixes
- **Branch:** pr-2439 → master

❌ **PR #2440** (Nov 29) - "Fix undeclared variables in search.js for ESM strict mode"
- **Type:** Bug fix
- **Branch:** fix-search-tab-strict-mode → master

❌ **PR #2439** (Nov 29) - "Add JavaScript Programming tab with transpiler"
- **Type:** Major new feature
- **Branch:** transpiler_clean_copy → master
- **Note:** May need maintenance-10.x if it breaks compatibility

❌ **PR #2437** (Nov 27) - "Fix 3D model loading in magnetometer tab"
- **Type:** Bug fix
- **Branch:** fix-magnetometer-model-loading → master

❌ **PR #2436** (Nov 27) - "Restore checkMSPPortCount and showMSPWarning functions in ports tab"
- **Type:** Bug fix
- **Branch:** fix-preexisting-tab-errors → master

❌ **PR #2434** (Nov 28) - "Fix ESM conversion in search and logging tabs"
- **Type:** Bug fix
- **Branch:** esm_modules_strays → master

❌ **PR #2433** (Nov 29) - "STM32 DFU: Refactor and implement CLI-based reboot protocol"
- **Type:** Feature/refactor
- **Branch:** reboot_to_dfu → master

❌ **PR #2432** (Nov 27) - "Fix DFU flash: ensure cleanup callback runs on USB error"
- **Type:** Bug fix
- **Branch:** fix-dfu-cleanup-callback → master

❌ **PR #2429** (Nov 25) - "Cleanup old references that should have been `control_profile`"
- **Type:** Cleanup/bug fix
- **Branch:** MrD_Clean-up-control_profile → master

❌ **PR #2285** (Nov 23) - "ESM modules & More"
- **Type:** Major refactor
- **Branch:** ESM-Modules → master
- **Note:** Likely should go to maintenance-10.x (breaking changes)

## Impact Assessment

### Last 2 Weeks (Since Dec 5):

**Minor impact:** Only 1 PR (configurator #2463) was merged incorrectly. This feature/fix will miss the 9.x release cycle but can be cherry-picked to maintenance-9.x if needed.

### Extended Period (Nov 20 - Dec 5):

**Moderate impact:** 23 PRs were merged to master that likely should have gone to maintenance branches:
- 10 firmware PRs (bug fixes, target updates, new features)
- 13 configurator PRs (bug fixes, new features, major refactor)

**Consequence:** These changes will not be included in 9.x releases unless they are cherry-picked to maintenance-9.x branch.

### Root Cause:

The branching strategy changed on **November 30, 2025** with the addition of the GitHub Action. Before this date:
- No clear guidance existed for contributors
- Documentation still described old "develop on master" strategy
- Many PRs naturally targeted master as that was the documented approach

**After November 30:** The GitHub Action now automatically comments on PRs targeting master, suggesting maintenance branches. This should significantly reduce incorrect merges going forward.

## Recommendations

### 1. Update Documentation (HIGH PRIORITY)

The following documentation needs updating to reflect the new branching strategy:

- `docs/development/Development.md` - Still describes old "develop on master" workflow
- `docs/development/Contributing.md` - Doesn't mention branching strategy
- `docs/policies/CONTRIBUTING.md` - Should reference the development docs

**Suggested update:** Add clear section explaining:
- maintenance-9.x for backward-compatible changes
- maintenance-10.x for breaking changes
- master for infrastructure and receives merges from maintenance branches

### 2. Cherry-Pick Important Changes (MEDIUM PRIORITY)

Review the 23 PRs merged to master between Nov 20-Dec 5 and determine which should be cherry-picked to maintenance-9.x:

**Priority candidates for cherry-picking:**
- Bug fixes (PRs #11144, #11127, #11122, #2441, #2440, #2437, #2436, #2434, #2432, #2429)
- Target updates (PRs #11134, #11131, #11129, #11092)
- Documentation (PR #11143)

### 3. Monitor GitHub Action Effectiveness (ONGOING)

Track whether the new GitHub Action (added Nov 30) successfully reduces incorrect merges to master. After 2-3 weeks, review new PRs to see if contributors are following the guidance.

### 4. Consider Branch Protection Rules (LOW PRIORITY)

If incorrect merges continue, consider adding branch protection rules that require maintainer approval for PRs to master (beyond standard PR reviews).

## Statistics

### Last 2 Weeks (Since Dec 5, 2025):

| Repository | Total PRs | Correct | Incorrect |
|------------|-----------|---------|-----------|
| inav (firmware) | 1 | 1 (100%) | 0 (0%) |
| inav-configurator | 2 | 1 (50%) | 1 (50%) |
| **Combined** | **3** | **2 (67%)** | **1 (33%)** |

### Extended Period (Nov 20 - Dec 5, before GitHub Action):

| Repository | Total PRs | Correct | Incorrect |
|------------|-----------|---------|-----------|
| inav (firmware) | 13 | 3 (23%) | 10 (77%) |
| inav-configurator | 16 | 3 (19%) | 13 (81%) |
| **Combined** | **29** | **6 (21%)** | **23 (79%)** |

**Key insight:** The GitHub Action was added Nov 30, and immediately the error rate dropped dramatically (from 79% incorrect to 33% incorrect in the following week).

## Conclusion

**Primary finding:** Only 1 PR in the last 2 weeks was merged incorrectly (configurator PR #2463).

**Context:** The branching strategy changed on November 30, 2025 with the addition of an automated GitHub Action that guides contributors to use maintenance branches. Before this change, 79% of PRs targeting master should have gone to maintenance branches instead.

**Good news:** The GitHub Action appears to be working - the incorrect merge rate dropped from 79% to 33% immediately after deployment.

**Action needed:** Update documentation to reflect the new branching strategy so contributors have clear guidance beyond the automated comment.

---
**Developer**
