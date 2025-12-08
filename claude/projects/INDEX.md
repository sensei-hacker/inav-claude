# Projects Index

This file tracks all active and completed projects in the INAV codebase.

**Last Updated:** 2025-12-08 14:30

---

## Status Definitions

| Status | Description |
|--------|-------------|
| 📋 **TODO** | Project defined but work not started |
| 🚧 **IN PROGRESS** | Actively being worked on |
| ✅ **COMPLETED** | Finished and merged |
| ⏸️ **BACKBURNER** | Paused, will resume later |
| ❌ **CANCELLED** | Abandoned, not pursuing |


| Indicator | Meaning |
|-----------|---------|
| ✉️ **Assigned** | Developer has been notified via email |
| 📝 **Planned** | Project created but developer not yet notified |

---

## Recent Activity (Last 7 Days)

### 2025-12-07: INAV 9.0.0-RC3 Released ✅
**Release Manager** - Successfully released RC3 for firmware and configurator
- Firmware: 219 hex files (commit `edf50292`)
- Configurator: 14 platform packages (commit `c2886074`)
- All quality checks passed, SITL verified
- Process improvements: 3 new automation tools created

### 2025-12-06: Issue #2453 Verification Complete ✅
**Developer** - All 5 JavaScript Programming bugs resolved in PR #2460 (MERGED)
- IntelliSense contamination fixed
- Unsaved changes dialog fixed
- Outdated API references fixed
- Override property access fixed
- Editor freeze resolved (cannot reproduce)

### 2025-12-08: PR #11100 Rebased for Clean Merge ✅
**Developer** - Successfully rebased PR #11100 onto latest maintenance-9.x
- **Branch:** `pr-11100-crsf-baro` rebased onto `edf50292e7`
- **Conflicts resolved:** docs/Settings.md, settings.yaml, telemetry.c
- **Build:** SITL compiles successfully
- **Ready for:** Force-push to update PR

### 2025-12-07: CRSF Telemetry Testing Progress 📊
**Developer** - PR #11100 baseline testing complete, code analysis reveals sensor check issue
- **PR #11100:** ✅ Telemetry validated (534 frames, frame 0x09 working correctly)
- **Code Analysis:** ⚠️ Missing runtime sensor availability check (may send garbage data)
- **PR #11025:** ❌ Build failure blocks testing (`pwmRequestMotorTelemetry` missing)
- **Next:** Complete sensor availability edge case testing before contacting PR author

### 2025-12-06: CRSF Telemetry PR Analysis Complete 📊
**Developer** - Analyzed PRs #11025 and #11100 for merge conflicts
- **Finding:** Frame 0x09 conflict identified (simple baro vs combined baro+vario)
- **Finding:** Airspeed duplication resolved (PR #11100 deferred to #11025)
- **Recommendation:** Merge PR #11100 first, then rebase #11025
- Test suite created: 38 tests for validation

### 2025-12-05: PrivacyLRS Dual-Band Research Complete 📊
**Developer** - Analyzed ExpressLRS dual-band implementation for Issue #13
- **Finding:** Build system blocks LR1121 dual-band (3-line fix identified)
- **Finding:** 3 critical commits needed from ExpressLRS
- **Recommendation:** APPROVE implementation (privacy benefits, 0.11% CPU overhead)
- **Estimate:** 18-34 hours for full dual-band support

---

## Active Projects

### 📋 commit-internal-documentation-updates

**Status:** TODO
**Type:** Documentation / Internal Tooling
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-07
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-12-07-1030-task-commit-documentation.md`
**Estimated Time:** 30-60 minutes

Commit and push accumulated internal documentation, skills, test scripts, and tooling updates.

**Changes to commit:**
- 16 modified skill definitions
- 4 new skills (create-pr, privacylrs-test-runner, test-crsf-sitl, test-privacylrs-hardware)
- Updated role documentation (developer, manager, release-manager, security-analyst)
- Updated INDEX.md with recent activity
- Research documents (CRSF telemetry, SITL websocket, PrivacyLRS findings)
- Test tools and automation scripts
- RC3 release documentation

**Excludes:** Submodules, temporary files, source code

**Location:** `claude/projects/commit-internal-documentation-updates/`

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

**Location:** `claude/projects/coordinate-crsf-telemetry-pr-merge/`

---

### 📋 fix-cli-align-mag-roll-invalid-name

**Status:** TODO
**Type:** Bug Fix / CLI
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-02
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-12-02-2200-task-cli-align-mag-roll-invalid-name.md`
**Estimated Time:** 2-4 hours

Fix CLI bug where `set align_mag_roll = <value>` returns "Invalid name" error, preventing external magnetometer configuration.

**Problem:**
- Command `set align_mag_roll = 900` fails with "Invalid name"
- Prevents external mag alignment configuration
- Critical for navigation accuracy

**Likely causes:**
- Conditional compilation (`USE_MAG` not defined for target)
- Settings generation issue
- CLI parsing bug

**Impact:** HIGH - prevents critical compass configuration, affects navigation

**Location:** `claude/projects/fix-cli-align-mag-roll-invalid-name/`

---

### 📋 fix-javascript-clear-unused-conditions

**Status:** TODO
**Type:** Bug Fix / Data Integrity
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-02
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-12-02-2155-task-clear-unused-logic-conditions.md`
**Estimated Time:** 1-2 hours

Fix data integrity bug in JavaScript Programming tab where saving a transpiled script doesn't clear pre-existing logic conditions that are not part of the new script.

**Problem:**
- User has 20 logic conditions on FC
- Writes JavaScript generating 10 conditions
- Saves to FC
- **BUG:** FC has 10 new + 10 stale conditions (should be only 10 new)

**Solution:**
- Track previously-occupied slots at load
- Clear unused slots at save
- Only send necessary conditions (smart approach)

**Impact:** HIGH - stale logic conditions could cause unexpected flight behavior

**Location:** `claude/projects/fix-javascript-clear-unused-conditions/`

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

**Location:** `claude/projects/privacylrs-fix-build-failures/`

---

### 📋 sitl-wasm-phase1-configurator-poc

**Status:** TODO
**Type:** Research / POC Implementation
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-02
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-12-02-0200-sitl-wasm-phase1-assignment.md`
**Estimated Time:** 15-20 hours

Build minimal SITL WebAssembly proof-of-concept that works inside PWA Configurator.

**Scope:** **Configurator-only** - No simulator support needed

**Objective:** Prove browser SITL can connect to Configurator and enable firmware configuration.

**Key Features:**
- WebSocket MSP communication (single client, Configurator only)
- EEPROM persistence via IndexedDB
- Configuration read/write functionality
- Stable operation (>100 Hz loop rate)

**Explicitly Out of Scope:**
- External simulator integration (RealFlight/X-Plane)
- TCP server (WebSocket only)
- Multi-client support
- Advanced features (CLI, logging, etc.)

**Implementation Plan:**
- Day 1: Emscripten build setup (4-5h)
- Day 2: WebSocket MSP (4-5h)
- Day 3: EEPROM persistence (3-4h)
- Day 4: Integration testing (3-4h)
- Day 5: Technical report (1-2h)

**Success Criteria:**
- Configurator connects via WebSocket
- Configuration read/write works
- Configuration persists across page reload
- Performance >100 Hz, <100ms MSP latency
- Stable operation (5+ minutes no crashes)

**Decision Point:** End of Week 1 - GO/STOP for Phase 3 (full implementation)

**Phase 3 Preview (if successful):** 30-40h for production build, optimizations, documentation

**Total Effort (Phase 1 + Phase 3):** 45-60 hours

**Predecessor:** investigate-sitl-wasm-compilation (research complete, CONDITIONAL GO approved)

**Location:** `claude/projects/sitl-wasm-phase1-configurator-poc/`

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

**Location:** `claude/projects/privacylrs-fix-finding1-stream-cipher-desync/`

---

### 📋 privacylrs-implement-chacha20-upgrade

**Status:** TODO
**Type:** Security Enhancement / Implementation
**Priority:** MEDIUM-HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-02
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-12-02-0240-chacha20-upgrade-assignment.md`
**Estimated Time:** 30 minutes - 2 hours

Implement ChaCha20 upgrade from Finding #5 analysis.

**Objective:** Upgrade PrivacyLRS encryption from ChaCha12 to ChaCha20 (RFC 8439 standard)

**Implementation:** Simple two-line change
- `rx_main.cpp:63`: Change `ChaCha cipher(12)` → `ChaCha cipher(20)`
- `tx_main.cpp:36`: Change `ChaCha cipher(12)` → `ChaCha cipher(20)`

**Benefits:**
- RFC 8439 standards compliance
- Industry best practice alignment (WireGuard, TLS 1.3, OpenSSH)
- Stronger security margin
- Improved audit-ability and user trust

**Performance impact:** <0.2% CPU (negligible)

**Testing:** Optional full testing on ESP32/ESP8285/ESP32S3

**Predecessor:** privacylrs-fix-finding5-chacha-benchmark (analysis complete)

**Location:** `claude/projects/privacylrs-implement-chacha20-upgrade/`

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

**Location:** `claude/projects/privacylrs-fix-finding7-forward-secrecy/`

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

**Location:** `claude/projects/privacylrs-fix-finding8-entropy-sources/`

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

**Location:** `claude/projects/verify-gps-fix-refactor/`

---


**Note:** Completed projects are archived to `claude/archived_projects/` to keep the active project list clean.


---

## Completed & Cancelled Projects

All completed and cancelled projects have been archived for reference.

**Total Completed:** 55 projects
**Total Cancelled:** 4 projects

**See:** [COMPLETED_PROJECTS.md](COMPLETED_PROJECTS.md) for full archive

**Query Tool:**
- `python3 project_manager.py list COMPLETE` - View completed projects
- `python3 project_manager.py list CANCELLED` - View cancelled projects
