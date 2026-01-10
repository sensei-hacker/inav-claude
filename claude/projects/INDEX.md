# Active Projects Index

This file tracks **active** projects only (TODO, IN PROGRESS, BACKBURNER).

**Last Updated:** 2026-01-09
**Active:** 15 | **Backburner:** 5

> **Completed projects:** See [completed/INDEX.md](completed/INDEX.md)
>
> **When completing a project:**
> 1. Move directory from `active/` to `completed/`
> 2. Remove entry from this file
> 3. Add entry to `completed/INDEX.md`

---

## Status Definitions

| Status | Description |
|--------|-------------|
| 📋 **TODO** | Project defined but work not started |
| 🚧 **IN PROGRESS** | Actively being worked on |
| ⏸️ **BACKBURNER** | Paused, will resume later |
| ❌ **CANCELLED** | Abandoned, not pursuing |


| Indicator | Meaning |
|-----------|---------|
| ✉️ **Assigned** | Developer has been notified via email |
| 📝 **Planned** | Project created but developer not yet notified |

---

## Active Projects

### 📋 esc-passthrough-bluejay-am32

**Status:** TODO | **Type:** Bug Fix / Feature Parity | **Priority:** HIGH
**Created:** 2026-01-09 | **Assignee:** Developer
**Branch:** From `maintenance-9.x`

ESC passthrough (4-way interface) works with Bluejay/AM32 in Betaflight but fails in INAV. Port fixes from Betaflight PRs #13287 (timeout handling) and #14214 (motor IO access).

**Key Issues:** Missing timeout handling in ReadByte(), outdated motor IO access method, narrow SILABS device detection, missing ESC reboot logic.

**Directory:** `active/esc-passthrough-bluejay-am32/`
**Assignment:** ✉️ Assigned - `manager/email/sent/2026-01-09-1900-task-esc-passthrough-bluejay-am32.md`

---

### 🚧 feature-oled-auto-detection

**Status:** IN PROGRESS
**Type:** Feature Enhancement
**Priority:** MEDIUM
**Assignment:** 📝 Started by Developer
**Created:** 2025-12-23
**Assignee:** Developer
**Estimated Time:** 4-6 hours

Auto-detect OLED controller type (SSD1306, SH1106, SH1107, SSD1309) to eliminate manual configuration.

**Progress:** Detection algorithm implemented and compiling. Still needs: display width handling for different controllers, hardware testing.

**File:** `inav/src/main/drivers/display_ug2864hsweg01.c`

**Project Request:** `claude/manager/inbox/2025-12-22-2249-project-request-oled-detection.md`

---

### 🚧 remember-last-save-directory

**Status:** AWAITING MERGE
**Type:** UX Enhancement
**Priority:** MEDIUM
**Assignment:** ✅ Implementation Complete
**Created:** 2025-12-29
**Assignee:** Developer
**PR:** [#2511](https://github.com/iNavFlight/inav-configurator/pull/2511) - Awaiting review/merge

Make file save dialogs default to the last directory used, eliminating repeated navigation for users saving multiple files.

**Solution:**
- Store last save directory in persistent settings
- Use Electron's `defaultPath` option with stored directory
- Apply to all save operations (blackbox, diffs, config exports)

**Assignment Email:** `claude/manager/sent/2025-12-29-1215-task-remember-last-save-directory.md`

---

### 📋 implement-pitot-sensor-validation

**Status:** TODO
**Type:** Safety Feature
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2026-01-02
**Assignee:** Developer
**Estimated Time:** 8-12 hours
**Milestone:** 9.1 or 9.2
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

Implement GPS-based pitot sensor validation with automatic fallback to virtual airspeed and OSD warning ("PITOT FAIL - VIRTUAL").

**Parent Analysis:** analyze-pitot-blockage-apa-issue (COMPLETED)

**Project Directory:** `active/implement-pitot-sensor-validation/`

**Assignment Email:** `claude/manager/sent/2026-01-02-0200-task-implement-pitot-sensor-validation.md`

---

### 📋 fix-apa-formula-limits-iterm

**Status:** TODO
**Type:** Bug Fix / Safety
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2026-01-02
**Assignee:** Developer
**Estimated Time:** 2-3 hours
**Milestone:** 9.1
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

Fix three APA formula issues: (1) Change limits [0.3,2.0]→[0.5,1.5], (2) Reduce I-term scaling, (3) Default apa_pow=0 (disabled). ~7 lines of code.

**Parent Analysis:** analyze-pitot-blockage-apa-issue (COMPLETED)

**Project Directory:** `active/fix-apa-formula-limits-iterm/`

**Assignment Email:** `claude/manager/sent/2026-01-02-0205-task-fix-apa-formula-limits-iterm.md`

---

### 📋 enable-galileo-optimize-gps-rate

**Status:** TODO
**Type:** Feature / Optimization
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-31
**Assignee:** Developer
**Estimated Time:** 2-3 hours

Implement top recommendations from u-blox GPS analysis: enable Galileo by default (clear win, no downsides) and optimize GPS update rate (research Jetrell's 8Hz findings).

**Project Directory:** `active/enable-galileo-optimize-gps-rate/`
**Reference Document:** `claude/developer/reports/ublox-gps-inav-vs-ardupilot.md`
**Assignment Email:** `claude/manager/sent/2025-12-31-1530-task-enable-galileo-optimize-gps-rate.md`

---

### 📋 fix-blackbox-zero-motors-bug

**Status:** TODO
**Type:** Bug Fix
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-29
**Assignee:** Developer
**Estimated Time:** 1-2 hours
**Milestone:** 9.1

Fix blackbox logging bug causing 207 decode failures on zero-motor aircraft. Simple one-word fix: change `CONDITION_MOTORS` to `CONDITION_AT_LEAST_MOTORS_1` at line 1079.

**Project Directory:** `active/fix-blackbox-zero-motors-bug/`
**Documentation:** `claude/developer/scripts/testing/inav/gps/MOTORS_CONDITION_BUG.md`
**Assignment Email:** `claude/manager/sent/2025-12-29-1230-task-fix-blackbox-zero-motors-bug.md`

---

### 🚧 investigate-esc-spinup-after-disarm

**Status:** IN PROGRESS - Investigation complete, implementation approach TBD
**Type:** Bug Investigation / Safety Issue
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-29
**Assignee:** Developer
**Estimated Time:** 4-6 hours

**⚠️ SAFETY CRITICAL:** Motors spin up several seconds after disarm due to EEPROM save blocking DSHOT frames, causing ESC reboot. Root cause identified; fix approach TBD.

**Issue #10913:** https://github.com/iNavFlight/inav/issues/10913
**Project Directory:** `active/investigate-esc-spinup-after-disarm/`
**Assignment Email:** `claude/manager/sent/2025-12-29-1225-task-investigate-esc-spinup-after-disarm.md`

---

### 📋 implement-3d-hardware-acceleration-auto-fallback

**Status:** TODO
**Type:** Feature Enhancement / Error Handling
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-26
**Assignee:** Developer
**Estimated Time:** 4-6 hours

Auto-detect WebGL support and gracefully fallback to 2D alternatives when 3D hardware acceleration unavailable (VMs, remote desktop, older systems).

**Project Directory:** `active/implement-3d-hardware-acceleration-auto-fallback/`
**Assignment Email:** `claude/manager/sent/2025-12-26-task-3d-hardware-acceleration-auto-fallback.md`

---

### 🚧 analyze-pitot-blockage-apa-issue

**Status:** IN PROGRESS (Analysis complete, implementation pending)
**Type:** Bug Analysis / Safety Issue
**Priority:** MEDIUM-HIGH
**Assignment:** ✅ Analysis Complete
**Created:** 2025-12-28
**Assignee:** Developer
**Actual Time:** ~8 hours (analysis phase)
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

Analyze the dangerous behavior of INAV 9's Fixed Wing APA (Airspeed-based PID Attenuation) when pitot tube fails or becomes blocked, and propose specific code changes.

**Analysis Completion Summary:**
- ✅ Comprehensive 11,800+ word analysis report completed
- ✅ Identified four distinct issues requiring separate solutions
- ✅ Mathematical analysis with Python visualization
- ✅ Specific code changes proposed with line numbers
- ✅ Implementation effort estimated: 10-12 hours total

**Key Findings:**
1. Pitot sensor validation needed (GPS-based sanity checks) - 8-12 hours
2. I-term scaling should be removed (control theory issue) - 15 minutes
3. Cruise speed reference - keep as-is (no change)
4. Symmetric limits [0.67, 1.5] instead of [0.3, 2.0] - 15 minutes

**Next Steps:** Implementation of recommended fixes

**Deliverable:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

**Location:** `active/analyze-pitot-blockage-apa-issue/`

**Assignment Email:** `claude/manager/sent/2025-12-28-1230-task-analyze-pitot-blockage-apa-issue.md`

---

### 📋 reproduce-issue-11202-gps-fluctuation

**Status:** TODO
**Type:** Bug Investigation
**Priority:** MEDIUM-HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-26
**Assignee:** Developer
**Estimated Time:** 6-8 hours
**GitHub Issue:** [#11202](https://github.com/iNavFlight/inav/issues/11202)

Investigate GPS signal instability (EPH spikes, HDOP fluctuations, reduced sat count) affecting INAV 6.0-9.0. Key finding: `gps_ublox_nav_hz` setting affects stability - 10Hz problematic, 6-9Hz better.

**Approach:** Create synthetic MSP GPS data with mspapi2 to isolate root cause.

**Investigation Directory:** `claude/developer/investigations/gps-fluctuation-issue-11202/`

**Assignment Email:** `claude/manager/sent/2025-12-26-task-reproduce-issue-11202-gps-fluctuation.md`

---


### 🚧 reproduce-issue-9912

**Status:** IN PROGRESS (Theory Identified, Needs Verification)
**Type:** Testing / Bug Reproduction / Root Cause Analysis
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-23
**Assignee:** Developer
**Estimated Time:** 3-5 hours + verification time

Continuous auto trim active during maneuvers. Theory: missing I-term stability check in `servos.c:644` allows transient I-term to be captured as trim. Needs SITL reproduction or pilot testing to verify.

**GitHub Issue:** [#9912](https://github.com/iNavFlight/inav/issues/9912)
**Project Directory:** `active/reproduce-issue-9912/`
**Analysis Report:** `claude/developer/reports/issue-9912-autotrim-analysis.md`
**Assignment Email:** `claude/manager/sent/2025-12-23-0029-task-reproduce-issue-9912.md`

---

### 📋 coordinate-crsf-telemetry-pr-merge

**Status:** TODO
**Type:** Coordination / PR Management
**Priority:** MEDIUM-HIGH
**Assignment:** 📝 Planned
**Created:** 2025-12-07
**Estimated Time:** 2-4 hours

Coordinate with PR authors to resolve frame 0x09 conflict between CRSF telemetry PRs #11025 and #11100.

**Problem:**
- Both PRs implement frame type 0x09 differently
- PR #11025: Simple barometer altitude (2 bytes)
- PR #11100: Combined baro + vario (3 bytes, more complete)
- Other features are complementary (Airspeed, RPM, Temp in #11025; Legacy mode in #11100)

**Solution:**
- Contact PR authors about conflict
- Recommend merge strategy: PR #11100 first (more complete baro), then #11025 (remove frame 0x09)
- Prepare test suite for validation
- Document merge approach

**Developer Analysis:** Complete (2025-12-06) - 38-test suite created, conflict identified

**Location:** `active/coordinate-crsf-telemetry-pr-merge/`

---

### 📋 privacylrs-fix-build-failures

**Status:** TODO
**Type:** Build Infrastructure / CI/CD Fix
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-02
**Assignee:** Developer
**Proposal Email:** `claude/security-analyst/sent/2025-12-02-0130-pr18-build-failures-unrelated.md`
**Assignment Email:** `claude/manager/sent/2025-12-02-0150-build-infrastructure-fix-assignment.md`
**Estimated Time:** 2-4 hours

**Objective:** Fix pre-existing build failures blocking PR #18 (Finding #1 fix) validation.

**Issues identified:**
1. Test suite missing `#include <stdio.h>` (native platform)
2. NimBLE-Arduino library conflicts (ESP32/ESP32S3 TX via UART)

**Scope:**
- Fix test_encryption.cpp compilation errors
- Resolve NimBLE library duplicate definition errors
- Verify all CI builds pass

**Estimated effort:** 2-4 hours

**Blocks:**
- PR #18 validation (Finding #1 fix)
- Future PRs to secure_01 branch

**Note:** Security Analyst to monitor PR #18 status after build fixes complete.

**Location:** `active/privacylrs-fix-build-failures/`

---

### 📋 sitl-wasm-phase1-configurator-poc

**Status:** TODO
**Type:** Research / POC Implementation
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-02
**Assignee:** Developer
**Estimated Time:** 15-20 hours

Build minimal SITL WebAssembly POC for PWA Configurator. Scope: WebSocket MSP, EEPROM via IndexedDB, config read/write. No simulator integration.

**Decision Point:** End of Week 1 - GO/STOP for Phase 3 (full implementation, 30-40h additional)

**Predecessor:** `active/investigate-sitl-wasm-compilation/` (research complete, CONDITIONAL GO)

**Assignment Email:** `claude/manager/sent/2025-12-02-0200-sitl-wasm-phase1-assignment.md`

---

### 📋 privacylrs-fix-finding1-stream-cipher-desync

**Status:** TODO → **Being addressed by privacylrs-complete-tests-and-fix-finding1**
**Type:** Security Fix / Bug Fix
**Priority:** CRITICAL
**Assignment:** 📝 Planned → **✉️ Assigned (via combined project)**
**Created:** 2025-11-30
**Assignee:** Security Analyst

**Note:** This standalone task is being addressed as Phase 2 of the combined project `privacylrs-complete-tests-and-fix-finding1`. See that project for current status and details.

**Reference:** Security Finding 1 (CRITICAL)
**Stakeholder Decision:** "Option 2, use the existing LQ counter"

**Location:** `active/privacylrs-fix-finding1-stream-cipher-desync/`

---

### 📋 privacylrs-fix-finding7-forward-secrecy

**Status:** TODO
**Type:** Security Enhancement / Cryptographic Protocol
**Priority:** MEDIUM
**Assignment:** 📝 Planned
**Created:** 2025-11-30
**Assignee:** Security Analyst (or Developer)

Implement ephemeral Diffie-Hellman key exchange using Curve25519 to provide forward secrecy, preventing master key compromise from exposing past communications.

**Key Tasks:**
- Design ECDH key exchange protocol integration
- Integrate Curve25519 library
- Implement key exchange handshake on TX and RX
- Derive session keys from ECDH shared secret + master key

**Reference:** Security Finding 7 (MEDIUM)
**Stakeholder Decision:** "Diffie-Hellman" (Curve25519)

**Location:** `active/privacylrs-fix-finding7-forward-secrecy/`

---

### 📋 privacylrs-fix-finding8-entropy-sources

**Status:** TODO
**Type:** Security Enhancement
**Priority:** MEDIUM
**Assignment:** 📝 Planned
**Created:** 2025-11-30
**Assignee:** Security Analyst (or Developer)

Implement robust entropy gathering that XORs multiple entropy sources (hardware RNG, timer jitter, ADC noise, RSSI) with dynamic detection and graceful fallback.

**Key Tasks:**
- Implement hardware capability detection
- Create wrappers for multiple entropy sources
- Implement XOR-based entropy mixing
- Test on multiple platforms with graceful fallback

**Reference:** Security Finding 8 (MEDIUM)
**Stakeholder Decision:** "Option 1 and 3. xor all available sources... use what is available, dynamically"

**Location:** `active/privacylrs-fix-finding8-entropy-sources/`

---

### ⏸️ settings-simplification

**Status:** BACKBURNER
**Type:** Feature / UX Improvement
**Priority:** MEDIUM
**Created:** 2026-01-07
**Estimated Effort:** 7-8 weeks (phased)

Reduce INAV configuration complexity by ~70% through automatic determination and consolidation of flight settings.

**Analysis Findings:**
- 19 auto-determinable settings (learn from flight data, constants)
- 47 settings → 12-14 consolidated primary settings
- ~48 unique settings can be eliminated or simplified

**Implementation Phases:**
1. Quick wins (~3 days): Battery chemistry presets, auto-link airspeed
2. Learning features (~3 weeks): Adaptive hover/cruise throttle
3. Profile systems (~2 weeks): Landing descent, throttle range
4. Advanced consolidations (~2 weeks)

**Value:** 70% reduction in configuration complexity, better new user experience.

**Analysis Documentation:** `claude/developer/investigations/inav-flight-settings/`

---

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

**Location:** `backburner/feature-add-function-syntax-support/`

---

### ⏸️ verify-gps-fix-refactor

**Status:** BACKBURNER
**Type:** Code Review / Refactoring
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-11-29
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-11-29-1030-task-verify-gps-fix-refactor.md`
**Related PR:** [#11144](https://github.com/iNavFlight/inav/pull/11144) (MERGED)
**Related Issue:** [#11049](https://github.com/iNavFlight/inav/issues/11049)

Verify the GPS recovery fix is complete and correct, answer reviewer's questions about why positions go to zero (not freeze), and refactor for code clarity/obviousness.

**Why Backburner:**
- PR already merged, awaiting user feedback
- Need more information from users before proceeding
- Code review/clarity work can wait for user reports

**Location:** `backburner/verify-gps-fix-refactor/`

---

### ⏸️ feature-auto-alignment-tool

**Status:** BACKBURNER
**Type:** Feature Enhancement
**Priority:** Medium
**Assignment:** ✉️ Assigned
**Created:** 2025-12-12
**Assignee:** Developer
**PR:** [#2158](https://github.com/iNavFlight/inav-configurator/pull/2158) (OPEN, "Don't merge")

Wizard-style tool that automatically detects and sets FC and compass alignment by having the user point north and lift the nose.

**Current State:**
- Basic implementation complete (Aug 2024)
- Video demo in PR
- Needs review/polish before merge

**Why Backburner:**
- Functional but needs polish
- Lower priority than bug fixes

**Location:** `backburner/feature-auto-alignment-tool/`

---

### ⏸️ remove-transpiler-backward-compatibility

**Status:** BACKBURNER
**Type:** Refactoring
**Priority:** LOW
**Assignment:** 📝 Planned (not yet assigned)
**Created:** 2025-12-28
**Scheduled For:** February 2026

Remove backward compatibility support from transpiler namespace refactoring, requiring users to use the fully namespaced `inav.` syntax.

**Background:**
Transpiler currently supports dual syntax for backward compatibility:
- New: `inav.gvar[0]`, `inav.rc[5]`, `inav.events.edge()`
- Old: `gvar[0]`, `rc[5]`, `edge()`

**Goal:**
Remove dual-path logic after 14-month migration period (Dec 2024 - Feb 2026).

**Scope:**
- Remove backward compatibility from parser.js
- Remove backward compatibility from codegen.js
- Remove backward compatibility from analyzer.js
- Remove backward compatibility from action_generator.js
- Update examples to use new syntax only

**Benefits:**
- Simpler codebase
- Clearer API (one way instead of two)
- Better maintainability
- Easier for new contributors

**Why Backburner:**
- Scheduled for February 2026
- Gives users 14 months migration time
- Decompiler already outputs new syntax only
- Not urgent, but planned

**Estimated Time:** 4-6 hours

**Location:** `backburner/remove-transpiler-backward-compatibility/`

**Related:** Developer request in `claude/manager/inbox-archive/2025-12-20-1903-project-request-remove-transpiler-backward-compatibility.md`

---


**Note:** Completed projects are archived to `claude/archived_projects/` to keep the active project list clean.


---

## Completed & Cancelled Projects

All completed and cancelled projects have been archived for reference.

**Total Completed:** 74 projects
**Total Cancelled:** 4 projects

**See:** [COMPLETED_PROJECTS.md](COMPLETED_PROJECTS.md) for full archive

**Query Tool:**
- `python3 project_manager.py list COMPLETE` - View completed projects
- `python3 project_manager.py list CANCELLED` - View cancelled projects
