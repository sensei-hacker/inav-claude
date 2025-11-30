# Projects Index

This file tracks all active and completed projects in the INAV codebase.

**Last Updated:** 2025-11-30 10:30

---

## Status Definitions

| Status | Description |
|--------|-------------|
| 📋 **TODO** | Project defined but work not started |
| 🚧 **IN PROGRESS** | Actively being worked on |
| ✅ **COMPLETED** | Finished and merged |
| ⏸️ **BACKBURNER** | Paused, will resume later |
| ❌ **CANCELLED** | Abandoned, not pursuing |

## Assignment Status

| Indicator | Meaning |
|-----------|---------|
| ✉️ **Assigned** | Developer has been notified via email |
| 📝 **Planned** | Project created but developer not yet notified |

---

## Active Projects

### 🚧 create-inav-claude-repo

**Status:** IN PROGRESS
**Type:** Repository Setup / Documentation
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-30
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-30-0300-task-create-inav-claude-repo.md`

Create public repository `inav-claude` under github.com/sensei-hacker with Claude workflow infrastructure files (skills, role guides, project templates, test tools). Excludes email content, downloads, and logs. Must sanitize paths and check for secrets before committing.

**Location:** N/A (repository creation task)

---

### 🚧 fix-search-tab-tabnames-error

**Status:** IN PROGRESS
**Type:** Bug Fix
**Priority:** High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-29
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-29-1100-task-fix-search-tab-tabnames-error.md`

Search tab throws `ReferenceError: tabNames is not defined` at line 9. Missing import after ESM conversion.

**Location:** `claude/projects/fix-search-tab-tabnames-error/`

---

### 🚧 fix-transpiler-empty-output

**Status:** IN PROGRESS
**Type:** Bug Fix
**Priority:** High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-29
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-29-1000-task-fix-transpiler-empty-output.md`
**Branch:** transpiler_clean_copy
**Related PR:** [#2439](https://github.com/iNavFlight/inav-configurator/pull/2439)

JavaScript transpiler produces empty output for valid if-statement chains with chained && conditions. Decompiler works correctly but transpiling the output back produces nothing.

**Location:** `claude/projects/fix-transpiler-empty-output/`

---

### 🚧 fix-decompiler-condition-numbers

**Status:** IN PROGRESS
**Type:** Bug Fix
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-29
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-29-1045-task-fix-decompiler-condition-numbers.md`
**Branch:** transpiler_clean_copy
**Related PR:** [#2439](https://github.com/iNavFlight/inav-configurator/pull/2439)

Decompiler generates `// Condition can be read by logicCondition[N]` comments with wrong condition numbers. Shows first condition in chain instead of the terminal/last condition.

**Location:** `claude/projects/fix-decompiler-condition-numbers/`

---

### 🚧 verify-gps-fix-refactor

**Status:** IN PROGRESS
**Type:** Code Review / Refactoring
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-29
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-29-1030-task-verify-gps-fix-refactor.md`
**Related PR:** [#11144](https://github.com/iNavFlight/inav/pull/11144) (MERGED)
**Related Issue:** [#11049](https://github.com/iNavFlight/inav/issues/11049)

Verify the GPS recovery fix is complete and correct, answer reviewer's questions about why positions go to zero (not freeze), and refactor for code clarity/obviousness.

**Location:** `claude/projects/verify-gps-fix-refactor/`

---

### ✅ transpiler-clean-copy

**Status:** COMPLETED
**Type:** Feature / PR Submission
**Priority:** High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**PR:** [#2439](https://github.com/iNavFlight/inav-configurator/pull/2439)
**PR Status:** Open - awaiting upstream review
**Branch:** transpiler_clean_copy

JavaScript Programming transpiler feature - clean branch created from master with all transpiler code. PR submitted, bot suggestions reviewed and fixed.

**Location:** `claude/archived_projects/transpiler-clean-copy/`

---

### ✅ docs-javascript-programming

**Status:** COMPLETED
**Type:** Documentation
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Branch:** docs_javascript_programming (inav repo)
**PR:** [#11143](https://github.com/iNavFlight/inav/pull/11143)
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2345-report-pr11143-bot-review-updated.md`

JavaScript programming documentation PR submitted. Bot suggestions reviewed - one fix applied (commit aa662ecad).

**Location:** `claude/archived_projects/docs-javascript-programming/`

---

### ✅ review-pr2439-bot-suggestions

**Status:** COMPLETED
**Type:** Code Review / Bug Fix
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1940-task-review-pr-2439-suggestions.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2330-completed-pr2439-bot-suggestions-review.md`
**PR:** [#2439](https://github.com/iNavFlight/inav-configurator/pull/2439)

Reviewed all 11 bot suggestions. Fixed nested if handling, added missing operators to optimizer. Removed ~350 lines of dead code. All 92 tests pass.

**Location:** `claude/archived_projects/review-pr2439-bot-suggestions/`

---

### ✅ consolidate-role-directories

**Status:** COMPLETED
**Type:** Cleanup / Organization
**Priority:** High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1950-task-consolidate-role-directories.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2325-completed-consolidate-role-directories.md`

Merged root-level claude-developer/, claude-manager/, claude-release-manager/ directories into claude/ subdirectories. Duplicates removed.

**Location:** N/A (workspace cleanup)

---

### ✅ investigate-pr2434-build-failures

**Status:** COMPLETED
**Type:** Bug Fix / CI Investigation
**Priority:** High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1210-task-investigate-pr2434-build-failures.md`
**PR:** [#2434](https://github.com/iNavFlight/inav-configurator/pull/2434)
**PR Status:** MERGED

Fixed ESM conversion issues in search and logging tabs. PR merged to upstream.

**Location:** `claude/archived_projects/investigate-pr2434-build-failures/`

---

### ✅ review-pr2433-bot-suggestions

**Status:** COMPLETED
**Type:** Code Review / Bug Fix
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-28
**Completed:** 2025-11-29
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1200-task-review-pr2433-bot-suggestions.md`
**PR:** [#2433](https://github.com/iNavFlight/inav-configurator/pull/2433)

Reviewed automated bot suggestions from PR #2433 (STM32 DFU reboot protocol refactor).

**Location:** `claude/archived_projects/review-pr2433-bot-suggestions/`

---

### ✅ fix-gps-recovery-issue-11049

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** Medium-High
**Assignment:** ✉️ Assigned
**Created:** 2025-11-26
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-26-1145-task-fix-gps-recovery-issue-11049.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-gps-recovery-fix-completed.md`
**GitHub Issue:** [#11049](https://github.com/iNavFlight/inav/issues/11049)
**PR:** [#11144](https://github.com/iNavFlight/inav/pull/11144)
**PR Status:** Open - submitted, awaiting review

Fixed bug where altitude and distance-to-home values get stuck at zero after GPS signal loss and recovery.

**Fix:** Moved `posEstimator.gps.lastUpdateTime` update outside `if (!isFirstGPSUpdate)` block.

**Location:** `claude/archived_projects/fix-gps-recovery-issue-11049/`

---

### ✅ sitl-msp-arming

**Status:** COMPLETED
**Type:** Testing Infrastructure / Research
**Priority:** Medium
**Assignment:** Developer-initiated
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2315-response-sitl-arming-status-update.md`
**Related To:** fix-gps-recovery-issue-11049

Enabled arming of INAV SITL via MSP protocol for automated testing.

**Key Solutions:**
- AETR channel order (not AERT) - Throttle on channel 2
- MSP response consumption to prevent buffer overflow
- HITL mode (MSP_SIMULATOR 0x201F) for sensor calibration bypass
- 50Hz RC updates to prevent timeout

**Documentation:** `.claude/skills/sitl-arm.md`

**Location:** `claude/archived_projects/sitl-msp-arming/`

---

### ✅ github-issues-review

**Status:** COMPLETED
**Type:** Research / Triage
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-26
**Completed:** 2025-11-26
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-26-1015-task-review-github-issues.md`
**Completion Report:** `claude/manager/inbox/2025-11-26-1130-report-github-issues-review.md`
**PR Status:** No PR needed (research task)

Review last 25 open issues on both INAV GitHub repositories (configurator and firmware) and identify actionable bugs we can fix.

**Deliverable:** Summary report with prioritized list of recommended issues to fix.

**Result:** Identified 6 actionable issues + 2 hardware support requests. Issue #11049 assigned as first task from this review.

**Time:** ~1-2 hours

---

## Backburner Projects

### ⏸️ feature-add-function-syntax-support

**Status:** BACKBURNER
**Type:** Feature Enhancement
**Priority:** Medium-High
**Assignment:** 📝 Planned (not yet assigned)
**Created:** 2025-11-24

Add transpiler support for traditional JavaScript function syntax: `function() {}` and `function name() {}`.

**Problem:**
Transpiler currently only supports arrow function syntax `() => {}`. Users familiar with traditional JavaScript can't use `function() {}` syntax.

**Solution:**
Extend parser, analyzer, and codegen to recognize and transpile traditional function syntax.

**Scope:**
- Anonymous functions: `on.always(function() { ... })`
- Named function declarations: `function checkYaw() { return flight.yaw > 1800; }`
- Function references: `edge(checkYaw, ...)`
- Function expressions: `const fn = function() { ... }`

**Estimated Time:** ~6-8 hours

**Why Backburner:**
- Wait for ESM refactor to complete
- Not critical (arrow functions work)
- Medium-high priority but after refactor

**Location:** `claude/projects/feature-add-function-syntax-support/`

---

### ⏸️ investigate-automated-testing-mcp

**Status:** BACKBURNER
**Type:** Research / Infrastructure
**Priority:** Low
**Assignment:** 📝 Planned (not yet assigned)
**Created:** 2025-11-23

Investigate MCP servers for automated testing of INAV Configurator Electron app.

**Key Goals:**
- Evaluate Electron MCP server
- Evaluate Circuit MCP
- Compare with traditional testing approaches
- Create proof-of-concept if promising

**Why Backburner:**
- Exploratory research project
- Transpiler work takes priority

**Location:** `claude/projects/investigate-automated-testing-mcp/`

---

## Completed Projects (Archived)

**Note:** Completed projects are archived to `claude/archived_projects/` to keep the active project list clean.

### ✅ fix-decompiler-chained-conditions

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** High
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1930-task-fix-decompiler-lower-than-error.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2230-completed-decompiler-chained-conditions-fix.md`
**Branch:** transpiler_clean_copy
**Commit:** 42d1febd
**PR Status:** On feature branch (PR #2439)

Fixed "Unknown operation 3 (Lower Than) in action" error and chained condition handling in decompiler.

**Issues Fixed:**
- `isActionOperation()` was incomplete - added all action operations
- Activator chains only collected direct children, not grandchildren
- Chained conditions without actions produced no output

**Time:** ~2 hours

**Location:** `claude/archived_projects/fix-decompiler-chained-conditions/`

---

### ✅ copy-transpiler-to-new-branch

**Status:** COMPLETED
**Type:** Git Operations / PR Submission
**Priority:** Medium
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1910-task-copy-transpiler-to-new-branch.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2030-completed-copy-transpiler-to-new-branch.md`
**Branch:** transpiler_clean_copy
**PR:** [#2439](https://github.com/iNavFlight/inav-configurator/pull/2439)
**PR Status:** Open - submitted, awaiting review

Created clean branch from master with transpiler code and submitted PR.

**Time:** ~1 hour

**Location:** `claude/archived_projects/copy-transpiler-to-new-branch/`

---

### ✅ move-js-docs-to-new-branch

**Status:** COMPLETED
**Type:** Documentation / Git Operations
**Priority:** Medium
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-28-1920-task-move-js-docs-to-new-branch.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-2036-completed-move-js-docs-to-new-branch.md`
**Branch:** docs_javascript_programming (inav repo)
**Commit:** cefce84c3
**PR Status:** Ready for PR submission

Created dedicated branch for JavaScript programming documentation with flattened structure.

**Time:** ~30 minutes

**Location:** `claude/archived_projects/move-js-docs-to-new-branch/`

---

### ✅ reboot-to-dfu-feature

**Status:** COMPLETED
**Type:** Feature / Bug Fix
**Priority:** Medium
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-1923-completed-reboot-to-dfu.md`
**Branch:** reboot_to_dfu
**PR Status:** Ready for PR submission

DFU reboot feature with IPC listener memory leak fix. Replaces "R" command with "# dfu" for reliable DFU entry.

**Changes:**
- 6 commits on reboot_to_dfu branch
- Fixed IPC listener memory leak causing CRC errors
- Added upfront DFU device check

**Time:** ~3-4 hours

**Location:** `claude/archived_projects/reboot-to-dfu-feature/`

---

### ✅ fix-preload-foreach-error-v2

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** High
**Created:** 2025-11-28
**Completed:** 2025-11-28
**Assignee:** Developer
**Completion Report:** `claude/manager/inbox-archive/2025-11-28-1845-completed-fix-preload-foreach-error.md`
**PR Status:** Local changes, ready for review

Fixed IPC listener memory leak that caused forEach errors when connection objects were garbage collected.

**Root Cause:** IPC listeners accumulated without cleanup; stale callbacks fired on destroyed objects.

**Fix:** Added off* methods to preload.js and removeIpcListeners() to connection classes.

**Time:** ~2 hours

**Location:** `claude/archived_projects/fix-preload-foreach-error-v2/`

---

### ✅ pmw3901-opflow-sensor

**Status:** COMPLETED
**Type:** Feature / Driver Implementation
**Priority:** Medium
**Created:** 2025-11-26
**Completed:** 2025-11-26
**Assignee:** Developer
**Completion Report:** `claude/manager/inbox-archive/2025-11-26-1046-completed-pmw3901-opflow-sensor.md`
**Branch:** add-pmw3901-opflow-sensor
**Commit:** 0274083f0
**PR Status:** Awaiting decision on upstream submission

Implemented native PMW3901 optical flow sensor support over SPI in INAV firmware.

**Files Added:**
- `src/main/drivers/opflow/opflow_pmw3901.c`
- `src/main/drivers/opflow/opflow_pmw3901.h`

**Note:** No hardware testing performed (no PMW3901 available).

**Time:** ~4 hours

**Location:** `claude/archived_projects/pmw3901-opflow-sensor/`

---

### ✅ setup-code-indexes-for-claude

**Status:** COMPLETED
**Type:** Development Tooling / Infrastructure
**Priority:** Medium
**Created:** 2025-11-25
**Completed:** 2025-11-26
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-25-2340-task-setup-code-indexes-for-claude.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-26-completed-setup-code-indexes.md`
**PR Status:** No PR needed (local tooling enhancement)

Setup code navigation indexes (ctags) to improve Claude Code's codebase understanding.

**Phase 1 Results:**
- Generated ctags for both codebases (firmware: 460K entries, configurator: 40K entries)
- Researched Claude Code - no native ctags support exists
- Created `/find-symbol` slash command for manual lookup
- Updated documentation (CLAUDE.md, claude/INDEXING.md)
- Added tags to .gitignore in both projects

**Key Finding:** ctags works well for C firmware but poorly for ES6+ JavaScript. Claude's built-in Grep/Glob tools are sufficient for most code navigation.

**Recommendation:** Phase 2 NOT recommended - additional complexity without proportional benefit.

**Time:** ~1.5 hours

**Location:** `claude/archived_projects/setup-code-indexes-for-claude/`

---

### ✅ implement-configurator-test-suite

**Status:** COMPLETED
**Type:** Infrastructure / Testing
**Priority:** Medium
**Created:** 2025-11-25
**Completed:** 2025-11-26
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-25-2030-task-implement-configurator-test-suite.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-26-0115-completed-implement-configurator-test-suite.md`
**PR:** #2435 (Open - submitted, awaiting review/merge)
**PR Link:** https://github.com/iNavFlight/inav-configurator/pull/2435

Implemented automated test suite for INAV Configurator with comprehensive testing infrastructure.

**Solution:**
- **Vitest** for unit/integration tests (native ESM support, Vite integration)
- **Playwright** for E2E Electron testing
- **SITL helper** for managing real firmware in tests

**Results:**
- **42 reliable tests implemented:**
  - 37 unit tests (helpers.js: 19, bitHelper.js: 18)
  - 5 integration tests (real SITL MSP protocol validation)
- Removed 46 questionable tests (testing mocks or reimplementations)
- All config files in tests/ directory for clean root

**Test Commands:**
- `npm test` - Run all tests
- `npm run test:watch` - Watch mode
- `npm run test:coverage` - Coverage report
- `npm run test:e2e` - E2E tests

**Documentation:**
- tests/README.md with setup instructions
- SITL integration test guide

**Notes:**
- Focused on reliable, useful tests only
- SITL integration tests require building SITL binary
- Clean, maintainable testing infrastructure

**Time:** ~13-19 hours (as estimated)

**Location:** `claude/archived_projects/implement-configurator-test-suite/`

---

### ✅ fix-preexisting-tab-errors

**Status:** COMPLETED
**Type:** Bug Fix / Technical Debt
**Priority:** Low
**Created:** 2025-11-25
**Completed:** 2025-11-26
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-25-2353-task-fix-preexisting-tab-errors.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-26-completed-fix-preexisting-tab-errors.md`
**Additional Report:** `claude/manager/inbox-archive/2025-11-26-0829-completed-fix-preexisting-tab-errors.md`
**PRs:** #2436 (Ports tab fix), #2437 (Magnetometer 3D model fix)
**PR Status:** Both Open - awaiting review/merge
**PR Links:**
- https://github.com/iNavFlight/inav-configurator/pull/2436
- https://github.com/iNavFlight/inav-configurator/pull/2437

Fixed two pre-existing JavaScript console errors discovered during MSP optimization testing.

**Issue 1: Ports Tab - checkMSPPortCount undefined**

**Root Cause:**
- Functions `checkMSPPortCount()` and `showMSPWarning()` were lost during merge conflict resolution
- Originally added in commit 92ee3431, lost in commits 8ccf4f83 and 895c526c

**Fix:**
- Restored both functions to `tabs/ports.js`

**Issue 2: Magnetometer Tab - modelUrl undefined & 3D model not loading**

**Root Cause:**
- Dynamic import at line 740 destructures as `{default: model}` but code used undefined `modelUrl`
- `model.add()` calls were incorrect - `model` is the URL string, not the THREE.js scene object

**Fix:**
- Changed `loader.load(modelUrl, ...)` to `loader.load(model, ...)`
- Changed `model.add(gps)` to `modelScene.add(gps)`
- Changed `model.add(fc)` to `modelScene.add(fc)`

**Verification:**
- User confirmed 3D model did not load before fix
- 3D model loads correctly after fix

**Results:**
- Both console errors resolved
- Ports tab functionality restored
- Magnetometer 3D model now loads correctly
- Both tabs tested and working

**Time:** ~15-30 minutes (as estimated)

**Discovery:** Found during Phase 1 of optimize-tab-msp-communication project

**Location:** `claude/archived_projects/fix-preexisting-tab-errors/`

---

### ✅ preserve-variable-names-decompiler

**Status:** COMPLETED
**Type:** Feature Enhancement
**Priority:** High
**Created:** 2025-11-24
**Completed:** 2025-11-25
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2040-task-preserve-variable-names.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-25-1530-status-preserve-variable-names-complete.md`
**Branch:** programming_transpiler_js
**Commit:** 9ee7ce93
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Implemented variable name preservation between configurator sessions.

**Solution:**
- Built variable map extraction from VariableHandler
- Integrated settingsCache for storage/retrieval
- Updated decompiler to reconstruct variable names
- Created 3 new test files

**Results:**
- let variables appear with original names after reload
- var variables show names instead of gvar[N]
- Graceful fallback when variable map missing
- All tests passing, manual testing verified

**Time:** ~6-8 hours

**Location:** `claude/archived_projects/preserve-variable-names-decompiler/`

---

### ✅ investigate-dma-usage-cleanup

**Status:** COMPLETED
**Type:** Research / Analysis / Documentation
**Priority:** Medium
**Created:** 2025-11-24
**Completed:** 2025-11-24
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2020-task-investigate-dma-usage.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-dma-investigation-complete.md`
**PR Status:** No PR needed (documentation/research project)

Analyzed INAV firmware DMA usage and created comprehensive documentation.

**Deliverables:**
- `inav/docs/development/DMA-USAGE.md` - 500+ line comprehensive guide
- Research notes comparing with Betaflight's DMA cleanup work
- Identified improvement opportunities (resource validation, SPI DMA implementation)

**Key Findings:**
- INAV lacks consistent resource validation (unlike Betaflight PR #10895)
- SPI currently uses polling mode, not DMA (performance opportunity)
- Documented platform differences (F4/F7/H7/AT32)

**Time:** ~10 hours

**Location:** `claude/archived_projects/investigate-dma-usage-cleanup/`

---

### ✅ refactor-transpiler-core-files

**Status:** COMPLETED (Phases 1, 2 & 3)
**Type:** Refactoring / Code Quality
**Priority:** Medium-High
**Created:** 2025-11-24
**Completed:** 2025-11-25
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2030-task-refactor-transpiler-core.md`
**Completion Reports:**
- Phase 1: `claude/manager/inbox-archive/2025-11-25-refactor-transpiler-helpers-complete.md`
- Phase 2: `claude/manager/inbox-archive/2025-11-25-refactor-transpiler-phase2-FINAL.md`
- Phase 3: `claude/manager/inbox-archive/2025-11-25-1605-status-refactor-transpiler-phase3-complete.md`
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Comprehensive refactoring with helper extraction, modular class architecture, and shared utilities.

**Phase 1 Results:**
- Extracted 6 helper methods across 4 files
- Made 95 code replacements
- Reduced by 185 lines (5.1%)

**Phase 2 Results:**
- Created 6 focused helper classes (1,508 lines)
- Removed 803 lines from main files (22% reduction!)
- Largest method: 251 lines → 73 lines (-71%)

**Phase 3 Results:**
- Created shared API mapping utility (181 lines)
- Removed 135 more lines from main files
- **Combined Phases 2+3: 938 lines removed (25.7% reduction!)**

**Final File Sizes:**
- codegen.js: 1,283 → 767 lines (-40%)
- analyzer.js: 855 → 654 lines (-24%)
- decompiler.js: 965 → 679 lines (-30%)
- parser.js: 616 lines (optimal)

**Helper Modules Created (7 total):**
- condition_generator.js (273 lines)
- expression_generator.js (224 lines)
- action_generator.js (251 lines)
- property_access_checker.js (194 lines)
- condition_decompiler.js (296 lines)
- action_decompiler.js (270 lines)
- api_mapping_utility.js (181 lines)

**All 51+ tests passing** ✅

**Time:** ~12-14 hours total (all phases)

**Location:** `claude/archived_projects/refactor-transpiler-core-files/`

---

### ✅ move-transpiler-docs-to-inav-repo

**Status:** COMPLETED
**Type:** Documentation / Repository Organization
**Priority:** High
**Created:** 2025-11-24
**Completed:** 2025-11-25
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2035-task-move-transpiler-docs.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-25-1015-completion-move-transpiler-docs.md`
**Branches:** nexus_xr (INAV), programming_transpiler_js (configurator)
**Commits:**
- INAV (nexus_xr): d7d12b893, 85da6120a
- configurator (programming_transpiler_js): cb93f57c, b5f158c9
**PR Status:** On feature branches, awaiting PRs

Moved transpiler documentation to INAV repository and added cross-links.

**Changes:**
- Moved `docs/` from inav-configurator to `inav/docs/javascript_programming/`
- Added cross-links in Programming Framework.md
- Added cross-links in JAVASCRIPT_PROGRAMMING_GUIDE.md
- Copied TESTING_GUIDE.md to tests directory

**Time:** ~2.5 hours

**Location:** `claude/archived_projects/move-transpiler-docs-to-inav-repo/`

---

### ✅ rebase-squash-transpiler-branch

**Status:** COMPLETED
**Type:** Git Operations / Branch Management
**Priority:** Medium
**Created:** 2025-11-24
**Completed:** 2025-11-25
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2025-task-rebase-squash-transpiler.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-25-rebase-transpiler-complete.md`
**PR Status:** No PR needed (git preparation work - script created but not executed)

Created git rebase script to squash 37 commits into 5 focused commits.

**Result:** 37 commits → 5 commits
- Group 1: Initial transpiler implementation (8 commits)
- Group 2: Core transpiler features (16 commits)
- Group 3: ESM module conversion (7 commits)
- Group 4: JavaScript variables support (4 commits)
- Group 5: Auto-insert INAV import (1 commit)
- Dropped: c8d1e78b (duplicate column fix - belongs on master)

**Deliverables:**
- `rebase-script.txt` - Ready-to-use rebase script
- `RATIONALE.md` - Detailed documentation

**Time:** ~1.5 hours

**Location:** `claude/archived_projects/rebase-squash-transpiler-branch/`

---

### ✅ fix-duplicate-active-when-column

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** Low
**Created:** 2025-11-24
**Completed:** 2025-11-24
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-2010-task-fix-duplicate-column.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-fix-duplicate-column-complete.md`
**Branch:** fix-duplicate-active-when-column
**Commit:** c9676a53
**PR Status:** Committed to separate branch, not on programming_transpiler_js (may need PR or inclusion in master)

Fixed duplicate "Active When" column in Programming tab.

**Files Modified:**
- tabs/programming.html (column order)
- js/logicCondition.js (matching td order)

**Time:** ~15 minutes

**Location:** `claude/archived_projects/fix-duplicate-active-when-column/`

---

### ✅ fix-require-error-onboard-logging

**Status:** COMPLETED
**Type:** Bug Fix
**Priority:** High
**Created:** 2025-11-25
**Completed:** 2025-11-25
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-25-1700-task-fix-require-error-onboard-logging.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-25-2250-status-fix-require-error-complete.md`
**PR:** #2434 (Open - submitted, awaiting review/merge)
**PR Link:** https://github.com/iNavFlight/inav-configurator/pull/2434

Fixed "Uncaught ReferenceError: require is not defined" error during tab switching.

**Root Cause:**
- Error was in `tabs/search.js`, not onboard_logging.js as stack trace suggested
- Search tab was never converted from CommonJS to ESM

**Changes:**
- `tabs/search.js`: Convert require() to ESM imports, replace path.join with dynamic import
- `js/configurator_main.js`: Change search tab loading from require() to import().then()
- `tabs/logging.js`: Add missing store import, use window.electronAPI.appendFile()
- `js/main/main.js`: Add appendFile IPC handler
- `js/main/preload.js`: Expose appendFile in electronAPI

**Result:**
- Tab switching works without errors
- Complete ESM conversion for search and logging tabs
- PR submitted and ready for review

**Time:** ~1-2 hours (as estimated)

**Location:** `claude/archived_projects/fix-require-error-onboard-logging/`

---

### ✅ feature-add-parser-tab-icon

**Status:** COMPLETED
**Type:** UI Enhancement
**Priority:** Low
**Created:** 2025-11-24
**Completed:** 2025-11-25
**Completed By:** Human (external contributor)
**PR Status:** Unknown (completed externally)

Added a visual icon to the JavaScript Programming (parser) tab in the configurator.

**Time:** ~1-2 hours

**Location:** `claude/archived_projects/feature-add-parser-tab-icon/`

---

### ✅ feature-auto-insert-inav-import

**Status:** COMPLETED
**Completed:** 2025-11-24
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-auto-insert-inav-import-complete.md`
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Auto-insert `import * as inav from 'inav';` if missing from user code.

**Location:** `claude/archived_projects/feature-auto-insert-inav-import/`

---

### ✅ fix-programming-tab-save-lockup

**Status:** COMPLETED
**Completed:** 2025-11-24
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-1850-completion-fix-save-lockup.md`
**Branch:** programming_transpiler_js
**Commit:** 808c5cbc
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Fixed bug where "save to flight controller" caused configurator lockup.

**Location:** `claude/archived_projects/fix-programming-tab-save-lockup/`

---

### ✅ fix-stm32-dfu-reboot-protocol

**Status:** COMPLETED
**Type:** Bug Fix / Refactoring
**Priority:** Medium
**Created:** 2025-11-24
**Completed:** 2025-11-24
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-24-1720-task-fix-stm32-dfu-reboot.md`
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-1840-completion-fix-stm32-dfu-reboot.md`
**Branch:** reboot_to_dfu
**PRs:** #2432 (DFU cleanup callback fix), #2433 (STM32 DFU refactor + new protocol)
**PR Status:** Open - submitted, awaiting review/merge
**PR Links:**
- https://github.com/iNavFlight/inav-configurator/pull/2432
- https://github.com/iNavFlight/inav-configurator/pull/2433

Updated STM32 reboot protocol from legacy 'R' command to CLI-based DFU sequence.

**Location:** `claude/archived_projects/fix-stm32-dfu-reboot-protocol/`

---

### ✅ feature-javascript-variables

**Status:** COMPLETED
**Completed:** 2025-11-24
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-javascript-variables-complete.md`
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Added JavaScript `let`, `const`, and `var` variable support to transpiler.

**Location:** `claude/archived_projects/feature-javascript-variables/`

---

### ✅ merge-branches-to-transpiler-base

**Status:** COMPLETED
**Completed:** 2025-11-24
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-merge-to-programming-transpiler-complete.md`
**Branch:** programming_transpiler_js
**PR Status:** No PR needed (internal branch merge operation)

Merged ESM refactor and JavaScript variables features into programming_transpiler_js branch.

**Location:** `claude/archived_projects/merge-branches-to-transpiler-base/`

---

### ✅ refactor-commonjs-to-esm

**Status:** COMPLETED
**Completed:** 2025-11-24
**Completion Report:** `claude/manager/inbox-archive/2025-11-24-esm-conversion-complete.md`
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Converted all CommonJS to ESM syntax across transpiler, tabs, and configurator.

**Location:** `claude/archived_projects/refactor-commonjs-to-esm/`

---

### ✅ improve-transpiler-error-reporting

**Status:** COMPLETED
**Completed:** 2025-11-23
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Fixed silent transpiler failures - all errors now visible to users.

**Location:** `claude/archived_projects/improve-transpiler-error-reporting/`

---

### ✅ fix-transpiler-api-mismatches

**Status:** COMPLETED
**Completed:** 2025-11-23
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Fixed critical operand value mismatches and transpiler bugs.

**Location:** `claude/archived_projects/fix-transpiler-api-mismatches/`

---

### ✅ fix-transpiler-documentation

**Status:** COMPLETED
**Completed:** 2025-11-23
**Completion Report:** `claude/manager/inbox-archive/2025-11-23-documentation-complete.md`
**Branch:** programming_transpiler_js
**PR Status:** On feature branch, awaiting PR (PR #2431 was closed without merging)

Fixed documentation to accurately reflect current transpiler code state.

**Location:** `claude/archived_projects/fix-transpiler-documentation/`

---

## Cancelled Projects

### ❌ implement-pmw3901-opflow-driver

**Status:** WONTFIX
**Type:** Feature / Driver Implementation
**Priority:** Medium
**Created:** 2025-11-26
**Cancelled:** 2025-11-26
**Status Report:** `claude/manager/inbox-archive/2025-11-26-1003-status-implementing-pmw3901-opflow.md`

Add native PMW3901 optical flow sensor support over SPI to INAV firmware.

**Reason for Cancellation:**
- Exploratory work only, not proceeding with implementation

**Location:** `claude/projects/implement-pmw3901-opflow-driver/`

---

### ❌ optimize-tab-msp-communication

**Status:** CANCELLED
**Type:** Performance Optimization
**Priority:** Medium-High
**Created:** 2025-11-25
**Cancelled:** 2025-11-25
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-25-1650-task-optimize-tab-msp-communication.md`
**Cancellation Report:** `claude/manager/inbox-archive/2025-11-25-2255-status-msp-optimization-update.md`

Investigation into MSP communication optimization in configurator tabs.

**Reason for Cancellation:**
- Investigation found minimal opportunities for improvement on Configurator side
- Another developer already working on MSP improvements in INAV firmware itself
- No significant duplicate or unnecessary requests identified
- Effort better spent elsewhere

**Work Done:**
- Phase 1 investigation completed
- MSP communication patterns analyzed
- Pre-existing bugs identified (documented separately in fix-preexisting-tab-errors)

**Outcome:**
- Project not proceeding per developer recommendation
- Focus shifted to firmware-level MSP improvements
- Configurator MSP usage already reasonably efficient

**Location:** `claude/archived_projects/optimize-tab-msp-communication/`

---

### ❌ fix-preload-foreach-error

**Status:** CANCELLED
**Type:** Bug Fix
**Priority:** High
**Created:** 2025-11-26
**Cancelled:** 2025-11-26
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-26-0108-task-fix-preload-foreach-error.md`
**Status Report:** `claude/manager/inbox-archive/2025-11-26-0210-paused-fix-preload-foreach-error.md`

Investigated preload.mjs forEach error but could not reproduce.

**Original Error:**
```
preload.mjs:25 Uncaught Error: Cannot read properties of undefined (reading 'forEach')
    at IpcRenderer.emit (VM24 node:events:519:28)
    at Object.onMessage (VM117 renderer_init:2:13350)
```

**Investigation Results:**
- Error location was misleading (line 25 is IPC callback registration)
- Found real bugs in `addOnReceiveCallback` across three connection files (pushing to wrong array)
- These bugs were the same ones already fixed in PR #2433 (fix-stm32-dfu-reboot-protocol)
- Error cannot be reproduced after reverting to original code
- `_onReceiveErrorListeners` is properly declared in base class

**Reason for Cancellation:**
- Error is non-reproducible
- May have been transient or environment-specific
- Related bugs already fixed in PR #2433 (submitted before this task was created)
- Without reproducible steps, cannot proceed with fix

**Recommendation:**
- Close task unless error reappears with reproduction steps
- The addOnReceiveCallback bugs should be fixed by PR #2433

**Outcome:**
- Investigation completed but no fix needed (error non-reproducible)
- May have already been resolved by concurrent work on PR #2433

**Location:** `claude/archived_projects/fix-preload-foreach-error/`

---

## Project Summary Statistics

- **Total Projects:** 47
- **Active:** 6
- **Backburner:** 2
- **Completed (Archived):** 36
- **Cancelled:** 3

---

## Quick Reference

### By Status

- ⏸️ **BACKBURNER:** feature-add-function-syntax-support, investigate-automated-testing-mcp
- 🚧 **IN PROGRESS:** create-inav-claude-repo, fix-search-tab-tabnames-error, fix-transpiler-empty-output, fix-decompiler-condition-numbers, verify-gps-fix-refactor
- ✅ **RECENTLY COMPLETED:** review-pr2433-bot-suggestions, transpiler-clean-copy (PR #2439), consolidate-role-directories, docs-javascript-programming (PR #11143), review-pr2439-bot-suggestions, investigate-pr2434-build-failures (PR #2434 MERGED), sitl-msp-arming, fix-gps-recovery-issue-11049 (PR #11144)
- ✅ **COMPLETED (archived):** github-issues-review, setup-code-indexes-for-claude, implement-configurator-test-suite, fix-preexisting-tab-errors, fix-require-error-onboard-logging, preserve-variable-names-decompiler, investigate-dma-usage-cleanup, refactor-transpiler-core-files, move-transpiler-docs-to-inav-repo, rebase-squash-transpiler-branch, fix-duplicate-active-when-column, feature-add-parser-tab-icon, feature-auto-insert-inav-import, fix-programming-tab-save-lockup, fix-stm32-dfu-reboot-protocol, feature-javascript-variables, merge-branches-to-transpiler-base, refactor-commonjs-to-esm, improve-transpiler-error-reporting, fix-transpiler-api-mismatches, fix-transpiler-documentation
- ❌ **CANCELLED:** implement-pmw3901-opflow-driver, optimize-tab-msp-communication, fix-preload-foreach-error

### By Assignment

- ✉️ **ASSIGNED (active):** create-inav-claude-repo, fix-search-tab-tabnames-error, fix-transpiler-empty-output, fix-decompiler-condition-numbers, verify-gps-fix-refactor
- 🔧 **DEVELOPER-INITIATED (completed):** sitl-msp-arming
- ✉️ **ASSIGNED (completed):** github-issues-review, setup-code-indexes-for-claude, implement-configurator-test-suite, fix-preexisting-tab-errors, fix-require-error-onboard-logging, preserve-variable-names-decompiler, investigate-dma-usage-cleanup, refactor-transpiler-core-files, move-transpiler-docs-to-inav-repo, rebase-squash-transpiler-branch, fix-duplicate-active-when-column, feature-auto-insert-inav-import, fix-programming-tab-save-lockup, fix-stm32-dfu-reboot-protocol, feature-javascript-variables, merge-branches-to-transpiler-base, refactor-commonjs-to-esm, improve-transpiler-error-reporting, fix-transpiler-api-mismatches, fix-transpiler-documentation
- ✉️ **ASSIGNED (cancelled):** optimize-tab-msp-communication, fix-preload-foreach-error
- 👤 **EXTERNAL (completed):** feature-add-parser-tab-icon
- 📝 **PLANNED:** feature-add-function-syntax-support, investigate-automated-testing-mcp

### By Priority

- **HIGH (active):** fix-search-tab-tabnames-error, fix-transpiler-empty-output
- **MEDIUM (active):** fix-decompiler-condition-numbers, verify-gps-fix-refactor
- **MEDIUM-HIGH (backburner):** feature-add-function-syntax-support
- **LOW (backburner):** investigate-automated-testing-mcp
- **HIGH (completed):** fix-require-error-onboard-logging, preserve-variable-names-decompiler, move-transpiler-docs-to-inav-repo, merge-branches-to-transpiler-base, fix-transpiler-documentation
- **MEDIUM (completed):** github-issues-review
- **MEDIUM-HIGH (completed):** refactor-transpiler-core-files, fix-programming-tab-save-lockup
- **MEDIUM (completed):** setup-code-indexes-for-claude, implement-configurator-test-suite, investigate-dma-usage-cleanup, rebase-squash-transpiler-branch, refactor-commonjs-to-esm, improve-transpiler-error-reporting, fix-stm32-dfu-reboot-protocol, feature-javascript-variables
- **LOW (completed):** fix-preexisting-tab-errors, fix-duplicate-active-when-column, feature-add-parser-tab-icon, feature-auto-insert-inav-import
- **CRITICAL (completed):** fix-transpiler-api-mismatches
- **HIGH (cancelled):** fix-preload-foreach-error
- **MEDIUM-HIGH (cancelled):** optimize-tab-msp-communication

### By Type

- **Repository Setup / Documentation (Active):** create-inav-claude-repo
- **Bug Fix (Active):** fix-search-tab-tabnames-error, fix-transpiler-empty-output, fix-decompiler-condition-numbers
- **Code Review / Refactoring (Active):** verify-gps-fix-refactor
- **Feature (Backburner):** feature-add-function-syntax-support
- **Research (Backburner):** investigate-automated-testing-mcp
- **Research / Triage (Completed):** github-issues-review
- **Development Tooling / Infrastructure (Completed):** setup-code-indexes-for-claude
- **Infrastructure / Testing (Completed):** implement-configurator-test-suite
- **Research/Analysis (Completed):** investigate-dma-usage-cleanup
- **Refactoring (Completed):** refactor-transpiler-core-files, refactor-commonjs-to-esm
- **Documentation (Completed):** move-transpiler-docs-to-inav-repo, fix-transpiler-documentation, improve-transpiler-error-reporting
- **Git Operations (Completed):** rebase-squash-transpiler-branch, merge-branches-to-transpiler-base
- **Bug Fix (Completed):** fix-require-error-onboard-logging, fix-duplicate-active-when-column, fix-programming-tab-save-lockup, fix-transpiler-api-mismatches, fix-stm32-dfu-reboot-protocol
- **Bug Fix / Technical Debt (Completed):** fix-preexisting-tab-errors
- **Feature (Completed):** preserve-variable-names-decompiler, feature-auto-insert-inav-import, feature-javascript-variables
- **UI Enhancement (Completed):** feature-add-parser-tab-icon
- **Bug Fix (Cancelled):** fix-preload-foreach-error
- **Performance Optimization (Cancelled):** optimize-tab-msp-communication

---

## Updating This Index

When project status changes:

1. Update the **Last Updated** date at the top
2. Move projects between sections as needed
3. Update status emoji and text
4. Update progress notes
5. Update statistics section
6. Commit changes

### Status Change Workflow

**Creating a new project:**
- Add to appropriate section (usually TODO or BACKBURNER)
- Set "Assignment" to 📝 Planned
- Add "Created" date

**Assigning a project to developer:**
- Send email via `claude/manager/sent/`
- Update "Assignment" to ✉️ Assigned
- Add link to assignment email
- Developer should have copy in `claude/developer/inbox/`

**Starting a project:**
- Move from TODO/BACKBURNER to IN PROGRESS
- Add "Started" date
- Add assignee
- Ensure ✉️ Assigned status (send email if not already sent)

**Completing a project:**
- Move to Completed Projects section
- Add "Completed" date
- Archive project directory to `claude/archived_projects/`
- Archive completion report to `claude/manager/inbox-archive/`
- Keep brief summary

**Pausing a project:**
- Move to BACKBURNER
- Note reason for pause
- Note what's blocking if applicable

**Cancelling a project:**
- Move to Cancelled Projects section
- Add "Cancelled" date
- Note reason for cancellation

---

## Notes

- Active projects have a corresponding directory in `claude/projects/`
- Completed projects are moved to `claude/archived_projects/`
- Each project directory should contain `summary.md` and `todo.md`
- Update this index whenever project status changes
- Completion reports are archived to `claude/manager/inbox-archive/`
