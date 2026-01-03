# Projects Index

This file tracks all active and completed projects in the INAV codebase.

**Last Updated:** 2025-12-31

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

### 2026-01-02: APA Safety Implementation - Pitot Validation and Formula Fixes 📋

**Manager** - Implement Pitot Sensor Validation with GPS Sanity Checks
- **Objective:** Implement GPS-based pitot sensor validation with automatic fallback
- **Parent Analysis:** analyze-pitot-blockage-apa-issue (COMPLETED 2025-12-28)
- **Problem:** Pitot failures are common and currently make aircraft nearly unflyable
- **Solution:** Cross-validate pitot readings against GPS, automatic fallback to virtual airspeed, OSD warning
- **Implementation:**
  1. GPS-based sanity check algorithm
  2. Automatic fallback to virtual airspeed when pitot fails validation
  3. OSD warning display: "PITOT FAIL - VIRTUAL"
  4. Edge case handling (wind, takeoff/landing, hysteresis)
- **Type:** Safety Feature Implementation
- **Priority:** HIGH
- **Estimated Time:** 8-12 hours
- **Milestone:** 9.1 or 9.2
- **Assignment Email:** `claude/manager/sent/2026-01-02-0200-task-implement-pitot-sensor-validation.md`

**Manager** - Fix APA Formula: Limits, I-term Scaling, Default Disabled
- **Objective:** Fix three issues with APA formula implementation
- **Parent Analysis:** analyze-pitot-blockage-apa-issue (COMPLETED 2025-12-28)
- **Changes:**
  1. Change limits from [0.3, 2.0] to [0.5, 1.5] (safer, symmetric)
  2. Reduce I-term scaling: use exponent (apa_pow - 100)/100 instead of apa_pow/100 (compromise approach)
  3. Set apa_pow default to 0 (disabled by default, opt-in for safety)
- **Impact:** Simple changes (~7 lines) with significant safety improvement
- **Compromise:** I-term gets gentle scaling (exponent 0.2) instead of aggressive (1.2) or none
- **User Impact:** Users must manually set apa_pow=120 to re-enable after upgrade
- **Type:** Bug Fix / Safety Improvement
- **Priority:** HIGH
- **Estimated Time:** 2-3 hours
- **Milestone:** 9.1
- **Assignment Email:** `claude/manager/sent/2026-01-02-0205-task-fix-apa-formula-limits-iterm.md`

### 2025-12-31: Infrastructure Task - Reorganize Developer Directory Structure 📋

**Manager** - Reorganize Developer Directory Structure
- **Objective:** Improve organization of `claude/developer/` directory
- **Scope:** Audit current state, plan better structure, implement reorganization, update all documentation
- **Current Issues:** Structure in CLAUDE.md is "not great", may not match reality, files scattered
- **Tasks:**
  1. Survey actual directory contents and skill expectations
  2. Design realistic, useful organization structure
  3. Move files to appropriate locations, clean up clutter
  4. Update developer/CLAUDE.md, developer/INDEX.md, skills, and other docs
- **Principles:** Intuitive, matches actual usage, supports workflows, scales well, self-documenting
- **Type:** Infrastructure / Organization
- **Priority:** MEDIUM
- **Estimated Time:** 3-4 hours
- **Assignment Email:** `claude/manager/sent/2025-12-31-2345-task-reorganize-developer-directory.md`

### 2025-12-31: Implementation Task - Enable Galileo and Optimize GPS Update Rate 📋

**Manager** - Enable Galileo by Default and Optimize GPS Update Rate
- **Objective:** Implement top recommendations from u-blox GPS configuration analysis
- **Changes:**
  1. Enable Galileo by default on M8+ GPS receivers (clear benefit, no downsides)
  2. Optimize GPS update rate - investigate and consider lowering to 8Hz based on Jetrell's testing
- **Rationale:** Analysis shows Galileo provides equal/better accuracy with more satellites, 8Hz may be optimal balance
- **Implementation:**
  - settings.yaml: Change gps_ublox_use_galileo default to ON
  - gps_ublox.c: Potentially update default GPS rate (pending research)
  - Documentation updates
- **Research Required:** Find and document Jetrell's testing results on GPS update rates
- **Type:** Feature / Optimization (backward compatible)
- **Priority:** MEDIUM
- **Estimated Time:** 2-3 hours
- **Assignment Email:** `claude/manager/sent/2025-12-31-1530-task-enable-galileo-optimize-gps-rate.md`

### 2025-12-31: New Documentation Task - u-blox GPS Configuration Analysis 📋

**Manager** - Document u-blox GPS Configuration and Compare with ArduPilot
- **Objective:** Analyze INAV's u-blox GPS configuration choices and compare with ArduPilot
- **Scope:** GNSS constellations, navigation model, update rates, protocol, special features
- **Analysis:** Document why INAV makes specific choices using code and u-blox datasheets
- **Comparison:** Review ArduPilot's configuration and identify key differences
- **Deliverables:** Two analysis documents in `claude/developer/reports/`
- **Goal:** Provide recommendations for potential improvements
- **Type:** Local project documentation (no PR)
- **Priority:** MEDIUM
- **Estimated Time:** 4-6 hours
- **Assignment Email:** `claude/manager/sent/2025-12-31-1200-task-document-ublox-gps-configuration.md`

### 2025-12-28: Three Tasks Completed - Pitot APA Analysis, Issue #9912 Fix, macOS DMG Fix ✅

**Developer** - Pitot Blockage APA Analysis COMPLETED
- **Status:** ✅ Analysis complete, awaiting approval for implementation
- **Deliverable:** Comprehensive 11,800+ word analysis report
- **Findings:** Identified four distinct issues requiring solutions
  1. Pitot sensor validation with GPS sanity checks (8-12 hours)
  2. I-term scaling should be removed (15 minutes)
  3. Cruise speed reference - keep as-is
  4. Symmetric limits [0.67, 1.5] instead of [0.3, 2.0] (15 minutes)
- **Total implementation effort:** 10-12 hours for all four solutions
- **Report:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`
- **Mathematical analysis:** `claude/developer/investigations/apa_formula_analysis.py`
- **Next step:** Awaiting manager approval to proceed with implementation

**Developer** - Issue #9912 Fix COMPLETED
- **Status:** ✅ PR submitted and ready for review
- **PR:** https://github.com/iNavFlight/inav/pull/11215
- **Fix:** Added I-term stability check to servo autotrim
- **Implementation:** I-term rate-of-change tracking prevents autotrim during maneuvers
- **Testing:** SITL build verified, needs flight testing
- **Copilot review:** All 3 comments addressed
- **Note:** Needs "needs testing" label added manually (gh CLI API issue)

**Developer** - macOS DMG Fix COMPLETED
- **Status:** ✅ Verified working, ready for merge
- **PR:** https://github.com/iNavFlight/inav-configurator/pull/2508
- **Fix:** Corrected postPackage hook path for macOS app bundles
- **Result:** macOS DMG now correctly excludes Windows/Linux SITL binaries
- **Verification:** CI build artifacts confirmed fix working
- **Impact:** Reduces DMG size by ~5-6 MB
- **Iterations:** Two commits (first had path bug, second fixed .app bundle path)

### 2025-12-31: Email Processed and Tasks Updated 📬

**Manager** - Processed 8 inbox messages
- Archived all Dec 28 completion reports
- Updated project statuses in INDEX.md
- Inbox now empty

### 2025-12-29: New Tasks - Safety Issues, Blackbox Fix, BLE Debugging, UX Enhancements 📋

**Manager** - Fix Blackbox Zero Motors Bug
- **Problem:** Catastrophic decoder failures (207 frames) on fixed-wing with zero motors
- **Root cause:** I-frame uses `CONDITION(MOTORS)` instead of `CONDITION(AT_LEAST_MOTORS_1)`
- **Bug:** Writes motor[0] unconditionally when motorCount=0, creating spurious 0x00 byte
- **Impact:** Header declares 0 fields, I-frame writes 1 byte → mismatch → decoder fails
- **Fix:** Change one word at line 1079: `MOTORS` → `AT_LEAST_MOTORS_1`
- **Documentation:** `claude/test_tools/inav/gps/MOTORS_CONDITION_BUG.md`
- **Testing:** JHEMCUF435 fixed-wing, 207 failures → 3 failures (baseline)
- **Milestone:** 9.1
- **Priority:** MEDIUM
- **Estimated Time:** 1-2 hours
- **Assignment Email:** `claude/manager/sent/2025-12-29-1230-task-fix-blackbox-zero-motors-bug.md`

**Manager** - Investigate ESC Motor Spinup After Disarm (SAFETY CRITICAL)
- **Issue:** https://github.com/iNavFlight/inav/issues/10913
- **Problem:** Motors spin up several seconds after disarm - DANGEROUS
- **Likely cause:** EEPROM blocking prevents DSHOT signal → ESC reboots → motors spin during reboot
- **Context:** Issue #9441 - Pawel explained EEPROM save blocks FC from generating valid ESC frames
- **Task:** Investigate root cause, implement fix (likely: hold motor pins low during EEPROM save)
- **Safety impact:** User injury risk if near aircraft
- **Solutions:** (A) Force pins low during save, (B) Non-blocking EEPROM, (C) Defer save
- **Priority:** HIGH
- **Estimated Time:** 4-6 hours
- **Assignment Email:** `claude/manager/sent/2025-12-29-1225-task-investigate-esc-spinup-after-disarm.md`

**Manager** - Add BLE Debug Logging for Windows Connection Issue
- **Issue:** BLE connects but no data received on Windows (Sent: 27 bytes, Received: 0 bytes)
- **Device:** SYNERDUINO7-BT-E-LE
- **Problem:** Connection establishes, notifications start, but MSP requests timeout
- **Log:** `/home/raymorris/Downloads/inav-log.txt`
- **Task:** Add comprehensive logging around BLE write/read/notifications
- **Goal:** Diagnose why data isn't being received
- **Areas:** Data transfer, service discovery, connection setup, errors, timing
- **Priority:** MEDIUM-HIGH
- **Estimated Time:** 2-3 hours
- **Assignment Email:** `claude/manager/sent/2025-12-29-1220-task-add-ble-debug-logging.md`

**Manager** - Remember Last Save Directory in Configurator
- **Enhancement:** Make save dialogs default to last used directory
- **Problem:** Users must navigate to preferred directory every time they save
- **Scope:** All file save operations (blackbox logs, diffs, config exports)
- **Solution:** Store last save directory in settings, persist across restarts
- **Implementation:** Use Electron's `defaultPath` option with stored directory
- **Priority:** MEDIUM
- **Estimated Time:** 2-4 hours
- **Assignment Email:** `claude/manager/sent/2025-12-29-1215-task-remember-last-save-directory.md`

**Manager** - Add Easy Configurator Download Links
- **Enhancement:** Add prominent download links to main pages (README, wiki)
- **Problem:** Users must navigate Releases → scroll → Assets → expand to download
- **Solution:** Add direct link to `https://github.com/iNavFlight/inav-configurator/releases/latest`
- **Scope:** Add to `inav/README.md` and wiki home page
- **Benefits:** Saves users 3-4 clicks, better user onboarding
- **Priority:** MEDIUM
- **Estimated Time:** 1-2 hours
- **Assignment Email:** `claude/manager/sent/2025-12-29-1200-task-easy-configurator-download-links.md`

### 2025-12-28: New Tasks Assigned - Pitot Blockage APA Analysis, Issue #9912 Fix, Mac DMG Fix 📋

**Manager** - Analyze Pitot Blockage APA Safety Issue
- **Issue:** https://github.com/iNavFlight/inav/issues/11208
- **PDF:** `/home/raymorris/Downloads/pitot blockage sanity check.pdf`
- **Problem:** INAV 9's Fixed Wing APA increases PIFF gains by 200% below cruise speed
- **Safety Critical:** When pitot fails/blocks, aircraft becomes nearly unflyable
- **Failure scenario:** Pitot reads low → system thinks aircraft is slow → massively increases gains at actual cruise speed
- **Task:** Analyze code, evaluate suggested solutions, propose specific code changes
- **Solutions to evaluate:** (1) Don't increase gains below cruise, (2) Separate increase/decrease parameters, (3) Airspeed sanity checks
- **Type:** Analysis & Proposal (no implementation yet)
- **Priority:** MEDIUM-HIGH
- **Estimated Time:** 6-8 hours
- **Assignment Email:** `claude/manager/sent/2025-12-28-1230-task-analyze-pitot-blockage-apa-issue.md`

**Manager** - Implement Fix for Issue #9912 Auto-Trim
- **Follow-up to:** Developer's completed root cause analysis
- **Issue:** Continuous auto-trim during maneuvers
- **Root cause:** Missing I-term stability check (already identified)
- **Task:** Implement the fix with I-term rate-of-change detection
- **Important:** Mark PR with "needs testing" label (requires flight testing)
- **Priority:** MEDIUM-HIGH
- **Estimated Time:** 3-4 hours
- **Assignment Email:** `claude/manager/sent/2025-12-28-1105-task-implement-issue-9912-fix.md`

**Manager** - Fix Mac DMG Containing Windows Binaries
- **Issue:** macOS DMG includes Windows SITL binaries (cygwin1.dll, inav_SITL.exe)
- **Root cause:** afterCopy hook in forge.config.js not working on macOS builds
- **Task:** Fix hook to properly remove non-native SITL binaries
- **Priority:** MEDIUM
- **Estimated Time:** 2-3 hours
- **Assignment Email:** `claude/manager/sent/2025-12-28-1050-task-fix-mac-dmg-windows-binaries.md`

**Manager** - Add MSP Reboot Parameter for DFU Mode
- **Enhancement:** Add optional parameter to MSP_REBOOT to trigger DFU mode
- **Benefits:** Reliable programmatic DFU entry, no CLI timing issues
- **Testing:** Use mspapi2 for testing
- **Updates needed:** Skills documentation, USB Flashing.md
- **Priority:** MEDIUM
- **Estimated Time:** 4-6 hours
- **Assignment Email:** `claude/manager/sent/2025-12-28-1045-task-msp-reboot-dfu-mode.md`

**Manager** - Created check-pr-docs Skill
- **New skill:** Check pull requests for documentation compliance
- **Key feature:** Independently fetches and checks wiki commits
- **Matching:** Direct PR refs, author+time, topic/keywords
- **Tools:** Shell script for automated checking, Python script for interactive tagging
- **Purpose:** Ensure PRs include appropriate documentation

### 2025-12-27: GPS Test Tools Documentation Task Assigned 📋

**Manager** - Document GPS Testing Tools in README.md
- **Goal:** Create comprehensive README.md for `claude/test_tools/inav/gps/` directory
- **Purpose:** Main entry point documenting all 40+ GPS testing scripts and tools
- **Special focus:** test_motion_simulator.sh orchestration workflow
- **Scope:**
  - Overview of all scripts grouped by purpose
  - Quick start guide with common workflows
  - Detailed documentation for test_motion_simulator.sh
  - Reference existing specialized docs (README_GPS_BLACKBOX_TESTING.md, etc.)
  - Script reference table with dependencies
- **Benefits:** Easier onboarding, clear entry point, organized by use case
- **Priority:** MEDIUM
- **Estimated Time:** 2-3 hours
- **Assignment Email:** `claude/manager/sent/2025-12-27-task-document-gps-test-tools.md`

### 2025-12-26: Two New Tasks Assigned - 3D Auto-Fallback & GPS Fluctuation Investigation 📋

**Manager** - Reproduce Issue #11202: GPS Signal Fluctuation with Synthetic Data
- **Issue:** https://github.com/iNavFlight/inav/issues/11202
- **Problem:** GPS instability in INAV 6.0-9.0 - EPH spikes, HDOP fluctuations (2-5), reduced sat count
- **Key finding:** `gps_ublox_nav_hz` setting affects stability (10Hz bad, 6-9Hz better)
- **Regression:** INAV 6.0 more stable than 7.0+, version 7.0 defaults to 5Hz despite settings
- **Approach:** Create synthetic MSP GPS data using mspapi2 to reproduce the problem
- **Testing:** Simulate fluctuating satellites/HDOP at different nav_hz rates (5Hz, 6Hz, 9Hz, 10Hz)
- **Goal:** Isolate root cause, determine if firmware bug or GPS module limitation
- **Priority:** MEDIUM-HIGH
- **Estimated Time:** 6-8 hours
- **Assignment Email:** `claude/manager/sent/2025-12-26-task-reproduce-issue-11202-gps-fluctuation.md`

**Manager** - Implement 3D Hardware Acceleration Auto-Fallback
- **Goal:** Auto-detect WebGL/3D support failures and gracefully fall back
- **Current issue:** App probably crashes when 3D hardware acceleration fails
- **Approach:** Add inline capability tests, implement automatic fallback to 2D
- **Investigation:** Find what uses 3D (WebGL canvas, model viewer, etc.)
- **Impact:** Better UX for users on VMs, remote desktop, or systems without GPU
- **Priority:** MEDIUM
- **Estimated Time:** 4-6 hours
- **Assignment Email:** `claude/manager/sent/2025-12-26-task-3d-hardware-acceleration-auto-fallback.md`

### 2025-12-23: Five Projects Complete, Issue #9912 Analysis Progress ✅📊

**Developer** - BLUEBERRY PID Performance Investigation Complete
- **Manufacturer was WRONG:** gyroLuluApplyFn is NOT the bottleneck!
- **True culprit:** Dynamic Gyro Notch Filter adds ~110µs per PID cycle (FFT overhead)
- **LULU filter impact:** Only ~6µs (negligible)
- **Performance improvement:** 435µs → 320µs with dynamic notch OFF (-115µs!)
- **Remaining gap:** 66µs difference vs JHEMCU (320µs vs 254µs) - cause unknown
- **Recommendation:** Disable dynamic notch on BLUEBERRY boards
- **Documentation:** Updated investigation reports in `claude/developer/investigations/blueberry-pid/`

**Developer** - BLUEBERRY Configuration Fix Complete
- **PR #11199:** https://github.com/iNavFlight/inav/pull/11199
- **Dynamic notch:** Disabled by default in `config.c` (performance optimization)
- **DMA analysis:** AT32F43x has DMAMUX - sequential numbering is CORRECT!
- **Key discovery:** AT32F43x DMA architecture differs from STM32 (flexible assignment)
- **DMA option 7 skip:** Intentional to avoid ADC1 conflict
- **Build verification:** Both BLUEBERRYF435WING variants build successfully
- **Branch:** fix-blueberry-disable-dynamic-notch, Commit: b7bfdeed54

**Developer** - OMNIBUSF4 4-Way Target Split Complete
- **PR #11196:** https://github.com/iNavFlight/inav/pull/11196
- **Structure:** Split into 4 directories (DYSF4/, OMNIBUSF4/, OMNIBUSF4PRO/, OMNIBUSF4V3_SS/)
- **Verification:** All 9 targets build successfully, preprocessor output identical
- **Tools:** Created unifdef automation scripts for future splits
- **Status:** Ready for review and merge

**Developer** - Organize claude/developer/ Directory Complete
- **Reorganized:** 50+ loose files into logical structure
- **Directories:** docs/, scripts/, investigations/, reports/, archive/
- **Documentation:** Updated CLAUDE.md with directory structure, created comprehensive INDEX.md
- **Commits:** 2fe97a4, 7a7697d
- **Result:** Clean, navigable structure with clear organization

**Developer** - Issue #9912 Root Cause Analysis (Theory)
- **Task:** Create reproduction script
- **Progress:** Performed deep code analysis instead
- **Theory:** Missing I-term stability check in autotrim (servos.c:644)
- **Hypothesis:** Transient I-term during maneuver transitions incorrectly transferred to servo midpoints
- **Proposed Fix:** Add I-term rate-of-change stability check before transfer
- **Report:** `claude/developer/reports/issue-9912-autotrim-analysis.md`
- **Status:** Theory needs verification through reproduction or pilot testing
- **Next:** Either reproduce bug in SITL or have pilot test the proposed fix

**Developer** - New Project Started: OLED Auto-Detection
- **Goal:** Auto-detect OLED controller type (SSD1306, SH1106, SH1107, SSD1309)
- **Progress:** Detection algorithm implemented and compiling
- **Still Needed:** Handle different display widths (132px vs 128px) and aspect ratios
- **File:** `inav/src/main/drivers/display_ug2864hsweg01.c`
- **Reference:** Based on ss_oled library detection algorithm

### 2025-12-23: Two New Tasks Assigned 📋

**Manager** - Fix BLUEBERRYF435 Configuration (DMA + Disable Dynamic Notch) *(UPDATED)*
- **Context:** Board overloaded at 132.1% task load from performance investigation
- **Task 1:** Disable dynamic gyro notch filter by default (wing optimization)
- **Task 2:** Fix DEF_TIM DMA configuration (sequential numbers → "0")
- **Rationale:** Two-pronged approach to reduce CPU load
  - Dynamic notch unnecessary for wing aircraft
  - DMA conflicts could cause contention
- **Target Files:** `config.c` and `target.c`
- **Priority:** MEDIUM-HIGH (related to HIGH priority performance issue)
- **Estimated Time:** 1-2 hours
- **Assignment Email:** `claude/manager/sent/2025-12-23-0033-task-fix-blueberry-deftim-config.md`

**Manager** - Create Test Script to Reproduce Issue #9912
- **Issue:** https://github.com/iNavFlight/inav/issues/9912
- **Goal:** Automated test script to reproduce bug
- **Approach:** Use SITL in simulator mode if helpful
- **Deliverables:** Test script, config files, reproduction report
- **Value:** Baseline for testing fixes, regression testing capability
- **Estimated Time:** 3-5 hours
- **Assignment Email:** `claude/manager/sent/2025-12-23-0029-task-reproduce-issue-9912.md`

### 2025-12-22: New Investigation Assigned - gyroLulu Performance 📋
**Manager** - Investigate gyroLuluApplyFn Performance Bottleneck
- **Context:** BLUEBERRY435 vs JHEMCU performance difference investigation
- **Finding:** Manufacturer identified gyroLuluApplyFn as bottleneck
- **Clue:** Disabling interrupts didn't help (NOT an interrupt issue)
- **Task:** Analyze function to find what causes significant slowdown on BLUEBERRY435
- **Areas:** FPU differences, memory access, filter operations, debug code impact
- **Estimated Time:** 2-4 hours
- **Assignment Email:** `claude/manager/sent/2025-12-22-2259-task-investigate-gyrolulu-performance.md`

### 2025-12-22: One Task Completed, One In Progress ✅

**Developer** - mspapi2 Documentation Complete
- **Delivered:** Comprehensive user-focused documentation for mspapi2 library
- **Statistics:** 13 files, 2,281 lines of documentation
- **PR:** #1 submitted to upstream repository (xznhj8129/mspapi2)
- **Content:** Getting started, flight computer guide, field discovery, server setup, examples
- **Status:** Awaiting maintainer feedback

**Developer** - OMNIBUSF4 Target Split In Progress 🚧
- **Progress:** Analysis complete, implementation started
- **PR:** #11196 submitted to iNavFlight/inav
- **Current work:** Split from 1 directory (9 targets) into 4 directories
- **Structure:** DYSF4/ (2), OMNIBUSF4/ (1), OMNIBUSF4PRO/ (3), OMNIBUSF4V3_SS/ (3)
- **Status:** Still working on final implementation and verification

### 2025-12-22: Developer Directory Organization Assigned 📋
**Manager** - Organize claude/developer/ directory structure
- **Problem:** 50+ loose files at root level, unclear organization
- **Scope:** Organize docs/, investigations, reports, scripts into logical tree
- **Constraints:** DO NOT move email directories (inbox, sent, etc.)
- **Deliverables:** Clean directory tree + updated CLAUDE.md + INDEX.md
- **Estimated Time:** 2-3 hours
- **Assignment Email:** `claude/manager/sent/2025-12-22-0029-task-organize-developer-directory.md`

### 2025-12-21: Two Tasks Completed ✅

**Developer** - PR #2477 / #2491 Conflict Resolution Complete
- **Problem:** PR #2477 showed CONFLICTING status despite appearing to have no conflict
- **Finding:** Both PRs added same JavaScript translation keys with different Ukrainian wording
- **Resolution:** Updated PR #2477 to use PR #2491's Ukrainian translations for overlapping keys
- **Result:** PR #2477 now MERGEABLE (conflicts resolved)
- **Note:** Also merged upstream/maintenance-9.x to complete resolution

**Developer** - H743 USB MSC Investigation Complete
- **Result:** COULD NOT REPRODUCE bug on CORVON743V1 hardware
- **Testing:** All builds from git tags (8.0.0, 8.0.1, 9.0.0) work correctly
- **False Positive:** Initial failing test caused by uncommitted SPI bus speed changes
- **Recommendation:** Keep issue #10800 open, investigate official release binaries
- **Hypothesis:** Official 8.0.1 release binaries may not match the 8.0.1 git tag

### 2025-12-21: One Analysis Task Assigned 📋

**Manager** - Analyze Qodo Bot Comments on PR #2482
- **PR:** https://github.com/iNavFlight/inav-configurator/pull/2482
- **Issue:** Qodo comments apply to commits removed from PR during cleanup
- **Task:** Check if suggestions still apply to current maintenance-9.x
- **Evaluation:** Determine if suggestions are worth implementing
- **Outcome:** If yes, create new branch off maintenance-9.x for improvements
- **Estimated Time:** 1-2 hours
- **Assignment Email:** `claude/manager/sent/2025-12-21-1643-task-analyze-pr2482-qodo-comments.md`

**Manager** - Analyze OMNIBUSF4 Target Structure for Refactoring
- **Problem:** 9 targets in one directory with 290 lines of conditional compilation
- **Issue:** 4 targets differ ONLY by softserial pin configuration
- **Question 1:** Can we split into 2-3 logical target directories?
- **Question 2:** Can softserial work at runtime without separate builds?
- **Analysis:** Determine if S5/S6 motor pins can share with softserial dynamically
- **Estimated Time:** 3-4 hours
- **Assignment Email:** `claude/manager/sent/2025-12-21-1622-task-analyze-omnibusf4-target-split.md`

### 2025-12-18: USB MSC H743 Regression Investigation Assigned 📋
**Manager** - Investigate commit that broke USB MSC mode on H743 (REVISED)
- **Issue:** https://github.com/iNavFlight/inav/issues/10800
- **Problem:** USB MSC mode broken on H743 MCUs in 8.0.1, worked in 8.0.0
- **Symptoms:** No drive appears, Device Manager shows missing drivers (Code 28)
- **Approach:** Option 1: Investigate PR #10706 directly (suspected cause)
- **Approach:** Option 2: Manual search of 83 commits for USB/H743 changes
- **Approach:** Option 3: Proper git bisect (only if testing is possible)
- **Note:** Revised to clarify that bisect requires actual testing, not code guessing
- **Estimated Time:** 2-4 hours
- **Assignment Email:** `claude/manager/sent/2025-12-18-0135-task-investigate-usb-msc-h743-regression-REVISED.md`

### 2025-12-18: Two Quick Bug Fixes Completed ✅

**Developer** - I2C Speed Warning Bug Fixed (PR #2485)
- **Problem:** Warning appeared even at maximum I2C speed (800KHz)
- **Root Cause:** Async settings loading race condition
- **Fix:** Wait for settingsPromise before triggering validation
- **Qodo bot:** 2 suggestions addressed (error handling, trigger optimization)
- **PR #2485** (configurator) - Open, awaiting review
- **Time:** Already complete when assigned!

**Developer** - PR #11025 CRSF Telemetry Corruption Investigation & Fix Complete
- **Investigation:** Identified 5 critical bugs causing telemetry corruption
- **Root Cause:** Unconditional scheduling + conditional writing = malformed frames
- **Impact:** Malformed frames corrupted entire CRSF protocol stream
- **Fix Strategy:** Conditional scheduling (follows GPS/Battery pattern)
- **Implementation:** All 5 bugs fixed with buffer overflow protection
- **Test Suite:** Created automated test script
- **PR #11189** (firmware) - Submitted to upstream
- **Report:** Comprehensive root cause analysis delivered
- **Time:** ~4 hours (under 4-6h estimate)

### 2025-12-18: MSP Library Documentation Update Assigned 📋
**Manager** - Update documentation to reference mspapi2 instead of uNAVlib
- **Background:** Library author recommends using newer mspapi2 library
- **Scope:** Update 2 CLAUDE.md files, 3 skills, developer documentation
- **Changes:** Make mspapi2 primary recommendation, preserve uNAVlib as "older alternative"
- **Note:** PRs can be submitted to mspapi2 for improvements
- **Estimated Time:** 2-3 hours
- **Assignment Email:** `claude/manager/sent/2025-12-18-0115-task-update-msp-library-documentation.md`

### 2025-12-18: Max Battery Current Limiter Complete ✅
**Developer** - Feature documentation and UI completed
- **Discovery:** Feature already existed since INAV 3.0.0 (3 years!), just undocumented
- **Solution:** Documented existing advanced power/current limiting instead of implementing duplicate
- **Wiki:** Created comprehensive Battery-and-Power-Management user guide (250 lines)
- **Firmware Docs:** Added 149-line Power Limiting section to Battery.md
- **Configurator UI:** Added power limiting section to Configuration tab with 8 settings
- **PR #11187** (firmware docs) - Merged
- **PR #2482** (configurator UI) - Merged (after cleanup to remove unrelated files)
- **Result:** Better than requested - burst mode, PI controller, dual current/power limiting

### 2025-12-17: Three Transpiler Analysis Tasks Complete ✅
**Developer** - Transpiler code structure and improvement opportunities analyzed

**1. Transpiler AST Types Documentation:**
- Created comprehensive 22KB reference: `claude/developer/docs/transpiler-ast-types.md`
- Documents all Acorn AST nodes, operators, and INAV Logic Condition structures
- BNF notation with clear hierarchy
- Foundation for generic handler analysis

**2. Transpiler Code Structure Analysis:**
- Analyzed 8 largest files (520-1,199 lines)
- Found 28 long functions (5 critically long >100 lines)
- Recommended 2 file splits: decompiler.js and codegen.js
- Report: `claude/developer/reports/transpiler-code-structure-analysis.md`
- Estimated effort: ~12-16 hours total

**3. Generic Handler Opportunities:**
- Identified 5 legitimate simplification opportunities
- Avoided "combine for combining's sake" suggestions
- Report: `claude/developer/reports/transpiler-generic-handler-opportunities.md`
- Estimated effort: ~4-6 hours total

### 2025-12-16: Three New Projects Assigned 📋

**Manager** - Max Battery Current Limiter feature assigned
- **Feature:** `max_battery_current` setting to protect batteries from over-discharge
- **Scope:** Firmware setting + motor output limiting + OSD indicator + Configurator UI
- **Implementation:** Proportional motor output reduction when current exceeds limit
- **Branch:** From `maintenance-9.x`
- **Estimated Time:** 8-12 hours
- **Assignment Email:** `claude/manager/sent/2025-12-16-1845-task-max-battery-current-limiter.md`

**Manager** - PR #11025 Telemetry Corruption Investigation assigned
- **Investigation:** Root cause analysis of why airspeed/RPM/temperature telemetry caused corruption
- **Context:** PR #11025 merged and reverted same day (Nov 28) - broke all telemetry
- **Key clue:** "Invalid frame emission when no payload data existed"
- **Focus:** Sensor availability checks, frame scheduling, empty frame handling
- **Resources:** Developer has extensive CRSF test infrastructure and documentation
- **Estimated Time:** 4-6 hours
- **Assignment Email:** `claude/manager/sent/2025-12-16-1900-task-investigate-pr11025-telemetry-corruption.md`

**Manager** - I2C Speed Warning Bug Fix assigned
- **Bug:** Warning "This I2C speed is too low!" appears even at maximum I2C speed
- **Location:** `tabs/configuration.html` in configurator
- **Likely cause:** Incorrect validation condition (comparison operator or threshold)
- **Fix type:** Quick logic fix in validation code
- **Branch:** From `maintenance-9.x`
- **Estimated Time:** 1-2 hours
- **Assignment Email:** `claude/manager/sent/2025-12-16-1910-task-fix-i2c-speed-warning-bug.md`

### 2025-12-14: Extract Method Refactoring Tool Project Created 📋
**Manager** - New CLI tool project assigned to Developer (assignment updated after clarification)
- **Corrected understanding:** Extract Method refactoring (create functions from inline code), NOT function hoisting
- **Use case:** Extract 50-line switch case blocks into separate functions
- **Approach:** CLI tool using Acorn + Commander.js + compare-ast for verification
- **Key innovation:** Smart parameter/return detection + AST-proven equivalence
- **Timeline:** 3-4 weeks
- **CLI design:** analyze/preview/apply workflow, JSON output for Claude Code integration
- **Documentation:** Complete CLI spec with algorithms, tool evaluation, updated README

### 2025-12-14: Transpiler Scoped Hoisting Complete ✅
**Developer** - Major decompiler improvements
- Scoped hoisting eliminates "monstrosity" lines (70+ words → clean output)
- Variable name preservation through compile/decompile
- 25 test suites passing
- **PR #2474** (configurator) - Mergeable, CI running
- **PR #11178** (inav docs) - Open, awaiting review

### 2025-12-12: Three Items Completed ✅
- **fix-cli-align-mag-roll-invalid-name** - [PR #2463](https://github.com/iNavFlight/inav-configurator/pull/2463) MERGED
- **commit-internal-documentation-updates** - Commits `00088a3`, `6621d04` pushed
- **Cppcheck fixes** - [PR #11172](https://github.com/iNavFlight/inav/pull/11172) MERGED (2 critical bugs fixed)

### 2025-12-11: Transpiler Improvements Completed ✅
**Developer** - Multiple transpiler fixes and enhancements
- **CSE Mutation Bug:** Fixed cache invalidation after variable mutation (PR #2469 closed - needs resubmission)
- **Decompiler Refactor:** [PR #2472](https://github.com/iNavFlight/inav-configurator/pull/2472) **MERGED** ✅ - Structural AST analysis, ~370 lines dead code removed
- **CLI Clipboard:** Fixed disabled copy button (PR #2473 OPEN)
- **extractValue Dedup:** Shared module created, ~147 lines consolidated

### 2025-12-09: Cppcheck Analysis Phase 1 Complete ✅
**Developer** - Found 2 critical bugs in INAV firmware
- `sensors/temperature.c:101` - Buffer overflow (memset doubled size)
- `fc/config.h:66` - Integer overflow (`1 << 31` should be `1U << 31`)
- **PR:** [#11172](https://github.com/iNavFlight/inav/pull/11172) - **MERGED** ✅

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

### 🚧 feature-oled-auto-detection

**Status:** IN PROGRESS
**Type:** Feature Enhancement / Driver Improvement
**Priority:** MEDIUM
**Assignment:** 📝 Started by Developer
**Created:** 2025-12-23
**Assignee:** Developer
**Estimated Time:** 4-6 hours

Implement automatic OLED controller detection to eliminate manual configuration, supporting SSD1306, SH1106, SH1107, and SSD1309 controllers.

**Background:**
Developer started this work proactively and requested it be tracked as a project.

**Problem:**
Users currently need to manually configure which OLED controller type they have. Different controllers have different display dimensions and require different handling.

**Solution:**
Implement auto-detection algorithm based on ss_oled library that reads status register 0x00 to identify controller type.

**Progress So Far:**
- ✅ Added controller type enum (SSD1306, SH1106, SH1107, SSD1309)
- ✅ Implemented `detectOledController()` function
- ✅ Added LOG_ERROR debug messages for detection results
- ✅ Code compiles successfully (tested with YUPIF7 target)

**Still Needed:**
- Update drawing code to handle different display widths:
  - SSD1306: 128 pixels wide (standard)
  - SH1106: 132 pixels wide (requires +2 pixel X offset)
  - SH1107: 128x128 displays (different aspect ratio)
- Testing on real hardware with different controller types
- Documentation updates

**Benefits:**
- Eliminates user configuration step
- Prevents display issues from wrong controller selection
- Better user experience
- More robust detection than manual setting

**Files Modified:**
- `inav/src/main/drivers/display_ug2864hsweg01.c`

**Reference:**
- ss_oled library detection: https://github.com/bitbank2/ss_oled/blob/01fb9a53388002bbb653c7c05d8e80ca413aa306/src/ss_oled.cpp#L810

**Project Request:** `claude/manager/inbox/2025-12-22-2249-project-request-oled-detection.md`

---

### 📋 document-ublox-gps-configuration

**Status:** TODO
**Type:** Documentation / Analysis
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-31
**Assignee:** Developer
**Estimated Time:** 4-6 hours

Analyze and document INAV's u-blox GPS receiver configuration choices, compare with ArduPilot, and provide recommendations.

**Objectives:**
1. Document INAV's u-blox configuration (constellations, nav model, rates, protocol, features)
2. Reference u-blox datasheets to understand each choice and trade-offs
3. Analyze ArduPilot's u-blox configuration for comparison
4. Identify key differences and analyze implications
5. Provide actionable recommendations for INAV

**Configuration Areas:**
- **GNSS Constellations:** GPS, GLONASS, Galileo, BeiDou - which enabled?
- **Navigation Model:** Airborne <1g/<2g/<4g, or other models
- **Update Rates:** Position, measurement, navigation rates
- **Protocol:** NMEA vs UBX, message selection
- **Special Features:** SBAS, jamming detection, power modes

**Deliverables:**
- `claude/developer/reports/ublox-gps-configuration-analysis.md` - INAV configuration analysis
- `claude/developer/reports/ublox-gps-inav-vs-ardupilot.md` - Comparison and recommendations

**Value:**
- Better understanding of GPS configuration
- Informed decisions about future GPS improvements
- Reference for troubleshooting and optimization
- Knowledge base for community

**Note:** Local project documentation - no PR, analysis stays in reports/

**Assignment Email:** `claude/manager/sent/2025-12-31-1200-task-document-ublox-gps-configuration.md`

---

### 📋 implement-pitot-sensor-validation

**Status:** TODO
**Type:** Safety Feature Implementation
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2026-01-02
**Assignee:** Developer
**Estimated Time:** 8-12 hours
**Milestone:** 9.1 or 9.2
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

Implement GPS-based pitot sensor validation with automatic fallback to virtual airspeed when pitot readings are implausible or failed.

**Parent Analysis:** analyze-pitot-blockage-apa-issue (COMPLETED 2025-12-28)

**Problem:**
- INAV lacks proper airspeed sensor validation
- When pitot tubes fail/block, aircraft becomes nearly unflyable
- Current APA with blocked pitot: 200% gains at cruise speed
- Pitot failures are COMMON (mechanical, blockage, forgotten sock)

**Solution Components:**

1. **GPS-Based Sanity Checking**
   - Cross-validate pitot readings against GPS groundspeed
   - Account for wind (use wind estimator)
   - Detect implausible readings (e.g., 25 km/h when GPS shows 85 km/h)
   - Rate-of-change anomaly detection

2. **Automatic Fallback**
   - Use virtual airspeed when pitot fails validation
   - Seamless transition (no control glitches)
   - Continue validation to detect recovery

3. **Pilot Warning**
   - Display "PITOT FAIL - VIRTUAL" on OSD
   - Clear indication of sensor failure
   - Warning clears when pitot validates again

4. **Edge Case Handling**
   - Wind uncertainty (conservative margins)
   - Takeoff/landing (low airspeed edge cases)
   - Hysteresis (prevent oscillation)
   - GPS unavailable (fallback to existing behavior)

**Implementation Phases:**
- Phase 1: Core validation (4-5 hours)
- Phase 2: Automatic fallback (2-3 hours)
- Phase 3: OSD warning (1-2 hours)
- Phase 4: Edge cases (2-3 hours)
- Phase 5: Testing & docs (2-3 hours)

**Files to Modify:**
- `src/main/sensors/pitotmeter.c` - GPS sanity check
- `src/main/sensors/pitotmeter.h` - Failure state enum
- `src/main/flight/pid.c` - Use validated airspeed
- `src/main/io/osd.c` - Warning display
- Documentation

**Safety Impact:**
- Makes aircraft flyable when pitot fails
- Common failure mode now handled gracefully
- Automatic safety improvement
- Clear pilot awareness

**Reference:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

**Assignment Email:** `claude/manager/sent/2026-01-02-0200-task-implement-pitot-sensor-validation.md`

---

### 📋 fix-apa-formula-limits-iterm

**Status:** TODO
**Type:** Bug Fix / Safety Improvement
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2026-01-02
**Assignee:** Developer
**Estimated Time:** 2-3 hours
**Milestone:** 9.1
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

Fix three issues with Fixed Wing APA (Airspeed-based PID Attenuation) formula.

**Parent Analysis:** analyze-pitot-blockage-apa-issue (COMPLETED 2025-12-28)

**Three Simple Changes (3 lines of code):**

1. **Change Limits from [0.3, 2.0] to [0.5, 1.5]**
   - More physically justified (symmetric)
   - Reduces maximum gain increase from 200% to 150%
   - Safer if pitot fails
   - File: `src/main/flight/pid.c`

2. **Reduce I-term Scaling (Compromise Approach)**
   - Calculate separate `itermFactor` using exponent (apa_pow - 100)/100
   - Example: apa_pow=120 → I exponent=0.2, P/D/FF exponent=1.2
   - Provides minimal I-term adaptation without control theory issues
   - Compromise between full scaling (causes windup/overshoot) and no scaling
   - File: `src/main/flight/pid.c`

3. **Set apa_pow Default to 0 (Disabled)**
   - Change: `default_value: 120` → `default_value: 0`
   - Feature should be opt-in for safety
   - Requires working pitot sensor
   - Users set apa_pow=120 to enable
   - File: `src/main/fc/settings.yaml`

**Rationale from Analysis:**
- **Limits:** Asymmetric [0.3, 2.0] have no physical justification, too wide
- **I-term:** Full scaling causes windup at low speeds, overshoot at high speeds; reduced scaling is a compromise
- **Default:** Feature unsafe without validated pitot, should be opt-in

**User Impact:**
- Existing users: APA disabled after upgrade (must set apa_pow=120 to re-enable)
- This is intentional for safety
- Users with re-enabled APA will notice smoother behavior (I-term fix)

**Implementation:**
- Change 1: Update constrainf() limits (1 line)
- Change 2: Add itermFactor calculation and use for I-term (~5 lines)
- Change 3: Update default_value (1 line)
- Add explanatory comments
- Update documentation

**Testing:**
- Build test
- SITL with apa_pow=0 (disabled, default)
- SITL with apa_pow=120 (enabled, verify new limits)
- Verify I-term not scaling (debug logs)
- Mathematical verification

**Simple but Significant:**
- ~7 lines changed (limits, itermFactor calc, default)
- Major safety improvement
- Better control characteristics (reduced I-term issues)
- Clear opt-in approach

**Reference:** `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

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

Implement top recommendations from u-blox GPS configuration analysis: enable Galileo by default and optimize GPS update rate.

**Background:**
The u-blox GPS configuration analysis identified clear opportunities for improvement. This task implements the most impactful recommendations.

**Objectives:**

1. **Enable Galileo by Default (Clear Win)**
   - Change default: `gps_ublox_use_galileo` from OFF to ON
   - Benefits: Equal/better accuracy, more satellites, better HDOP, faster TTFF
   - No downsides, backward compatible (users can still disable)

2. **Optimize GPS Update Rate (Research Required)**
   - Current: 10Hz default on M7+
   - ArduPilot: 5Hz (noted M9N performance issues)
   - **Jetrell's testing:** Suggests 8Hz may be optimal
   - Need to find and document testing results before implementation

**Implementation Plan:**

Phase 1: Research (30 min)
- Find Jetrell's GPS update rate testing results
- Understand why 8Hz might be better than 10Hz
- Document findings

Phase 2: Enable Galileo (45 min)
- Edit settings.yaml: Change Galileo default to ON
- Verify implementation in code
- Test build
- Update documentation

Phase 3: GPS Rate Decision (45-60 min)
- Based on research, choose:
  - Option A: Change default to 8Hz for all M7+
  - Option B: Hardware-specific rates (8Hz M8/M9, 10Hz M10)
  - Option C: Keep 10Hz, document 8Hz option
- Implement if evidence supports change

Phase 4: Testing (30 min)
- Build verification (multiple targets)
- Hardware testing if available
- Verify defaults are correct

Phase 5: Pull Request
- Create PR with clear rationale
- Reference analysis document and Jetrell's testing
- Request community testing

**Files to Modify:**
- `inav/src/main/fc/settings.yaml` - Galileo default
- `inav/src/main/io/gps_ublox.c` - GPS rate (if changed)
- `docs/Gps.md` - Documentation

**Key Decision Point:**
GPS rate change requires evidence from Jetrell's testing. Don't change without understanding the rationale.

**Deliverables:**
- Code changes with Galileo enabled by default
- GPS rate optimization (if evidence supports it)
- Updated documentation
- Pull request with clear rationale
- Completion report documenting decisions made

**Value:**
- Improved GPS accuracy for all INAV users with M8+ receivers
- More satellites = better reliability and HDOP
- Optimal GPS update rate for performance/reliability balance
- Better defaults out-of-the-box

**Parent Project:** document-ublox-gps-configuration (analysis completed)

**Reference Document:** `claude/developer/reports/ublox-gps-inav-vs-ardupilot.md`

**Assignment Email:** `claude/manager/sent/2025-12-31-1530-task-enable-galileo-optimize-gps-rate.md`

---

### 📋 reorganize-developer-directory

**Status:** TODO
**Type:** Infrastructure / Organization
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-31
**Assignee:** Developer
**Estimated Time:** 3-4 hours

Analyze, plan, and implement better organization structure for `claude/developer/` directory, then update all documentation.

**Problem:**
- Current structure documented in `developer/CLAUDE.md` is "not great"
- Documentation may not match actual directory layout
- Files may be scattered or poorly organized
- No clear guidelines for where different types of files should go
- Skills may have expectations about locations that aren't met

**Objectives:**

1. **Audit Current State**
   - Survey actual files and directories
   - Review skill documentation about file organization
   - Review current documentation (CLAUDE.md, INDEX.md)
   - Identify what's working and what needs improvement

2. **Plan Better Structure**
   - Design realistic, useful organization
   - Match how work is actually done
   - Keep things neat, tidy, and easy to find
   - Consider reusable vs. task-specific files
   - Consider active vs. archived work

3. **Implement Organization**
   - Move files to new locations
   - Create necessary directories
   - Clean up clutter and duplicates
   - Ensure everything has a clear home

4. **Update Documentation**
   - Update `developer/CLAUDE.md` with new structure
   - Update `developer/INDEX.md` with comprehensive guide
   - Update skill documentation if needed
   - Update other internal docs with path references

**Design Principles:**
- Intuitive - easy to find things without reading docs
- Matches actual usage - reflects how work is actually done
- Supports workflows - makes common tasks easier
- Scales well - handles growth without becoming messy
- Self-documenting - directory names explain purpose

**Key Questions to Answer:**
- Where do reusable scripts go vs. task-specific scripts?
- How to organize active work vs. archived work?
- How to categorize different types of scripts (testing, build, analysis, investigation)?
- How to organize different types of documentation (guides, reference, reports)?
- Where do task working files go?

**Implementation Phases:**

1. Discovery (45 min) - Survey current state, review docs, identify issues
2. Planning (45 min) - Design structure, plan moves, plan documentation
3. Implementation (60 min) - Create directories, move files, update references
4. Documentation (45 min) - Update CLAUDE.md, INDEX.md, skills, other docs
5. Testing (15 min) - Verify locations, test workflows, test skills

**Files to Update:**
- `claude/developer/CLAUDE.md`
- `claude/developer/INDEX.md`
- `~/.claude/skills/*/SKILL.md` (if needed)
- Other docs with path references

**Deliverables:**
- Reorganized directory structure with all files in logical locations
- Updated documentation accurately reflecting structure
- Migration documentation (old → new paths)
- Completion report with before/after comparison

**Value:**
- Easier to find files and documentation
- Clear guidelines for where things go
- Reduced clutter and confusion
- Better productivity and workflow
- Easier for new developers (or AI instances) to navigate

**Note from Manager:**
> "When working on a task, keep the files you create neatly organized. Testing scripts should go in scripts_testing if they are reuseable. Other things should go in the appropriate task working directory. When creating Python scripts that you may need to re-use later, save them to an appropriately named file, with documentation at the top. Don't leave files littering random directories."

The new structure should make this guidance easier to follow.

**Assignment Email:** `claude/manager/sent/2025-12-31-2345-task-reorganize-developer-directory.md`

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

Fix blackbox logging bug causing catastrophic decoder failures (207 frames) on aircraft with zero motors.

**Problem:**
I-frame motor write uses `CONDITION(MOTORS)` (flag only) instead of `CONDITION(AT_LEAST_MOTORS_1)` (flag + count check), causing header/data mismatch on fixed-wing with servos only.

**The Bug:**
- Field definitions: `AT_LEAST_MOTORS_1` (requires motorCount >= 1)
- I-frame write: `MOTORS` (flag only)
- When motorCount=0, flag=true:
  - Header: 0 motor fields (correct)
  - I-frame: Writes motor[0] unconditionally (1 spurious byte)
  - Decoder expects frame marker, gets 0x00 → catastrophic failure

**The Fix:**
Change one word at line 1079:
```c
// From:
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_MOTORS)) {

// To:
if (testBlackboxCondition(FLIGHT_LOG_FIELD_CONDITION_AT_LEAST_MOTORS_1)) {
```

**Testing:**
JHEMCUF435 fixed-wing, motorCount=0:
- Before: 207 decoder failures
- After: 3 decoder failures (baseline)

**Documentation:** `claude/test_tools/inav/gps/MOTORS_CONDITION_BUG.md`

**Assignment Email:** `claude/manager/sent/2025-12-29-1230-task-fix-blackbox-zero-motors-bug.md`

---

### 📋 investigate-esc-spinup-after-disarm

**Status:** TODO
**Type:** Bug Investigation / Safety Issue
**Priority:** HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-29
**Assignee:** Developer
**Estimated Time:** 4-6 hours

**⚠️ SAFETY CRITICAL:** Investigate and fix dangerous motor spinup several seconds after disarm.

**Problem:**
Motors unexpectedly spin up after disarm - risk of injury if user is near aircraft.

**Issue #10913:** https://github.com/iNavFlight/inav/issues/10913

**Likely Root Cause (from Issue #9441):**
1. User disarms
2. EEPROM save triggered (stats, config)
3. EEPROM blocks CPU for 1-2 seconds
4. FC cannot generate valid DSHOT frames
5. ESC interprets as signal loss → reboots
6. **ESC spins motors during reboot sequence**

**Investigation Tasks:**
- Analyze EEPROM save timing on disarm
- Check motor output behavior during EEPROM blocking
- Investigate other potential causes
- Propose fix (likely: hold motor pins LOW during save)

**Proposed Solutions:**
- **Option A:** Force motor output pins LOW before EEPROM save (preferred - simple, safe)
- **Option B:** Make EEPROM save non-blocking (complex, long-term)
- **Option C:** Defer EEPROM save 5-10 seconds (simpler but risky)

**Safety Requirements:**
- Must prevent ANY motor spinup after disarm
- Must work across all ESC protocols (DSHOT, OneShot, PWM)
- Must be thoroughly tested

**Assignment Email:** `claude/manager/sent/2025-12-29-1225-task-investigate-esc-spinup-after-disarm.md`

---

### 📋 add-ble-debug-logging

**Status:** TODO
**Type:** Debugging / Logging Enhancement
**Priority:** MEDIUM-HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-29
**Assignee:** Developer
**Estimated Time:** 2-3 hours

Add comprehensive debug logging to BLE connection code to diagnose Windows issue where device connects but no data is received (Sent: 27 bytes, Received: 0 bytes).

**Problem:**
BLE device "SYNERDUINO7-BT-E-LE" connects successfully on Windows, notifications start, but MSP requests timeout due to receiving 0 bytes despite sending 27 bytes.

**Solution:**
Add detailed logging around:
- Data write operations (hex dump, timing)
- Data receive/notification handler
- Service/characteristic discovery
- Connection state changes
- Detailed error information

**Goal:**
Capture detailed logs to identify root cause before attempting fix.

**Assignment Email:** `claude/manager/sent/2025-12-29-1220-task-add-ble-debug-logging.md`

---

### 📋 remember-last-save-directory

**Status:** TODO
**Type:** UX Enhancement
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-29
**Assignee:** Developer
**Estimated Time:** 2-4 hours

Make file save dialogs default to the last directory used, eliminating repeated navigation for users saving multiple files.

**Problem:**
Save dialogs always default to system directories (Documents, Downloads). Users must navigate to their preferred location every time, which is tedious for common workflows like saving multiple blackbox logs.

**Solution:**
- Store last save directory in persistent settings
- Use Electron's `defaultPath` option with stored directory
- Apply to all save operations (blackbox, diffs, config exports)
- Handle edge cases (deleted directory, first use)

**Benefits:**
Significantly improves user experience for common workflows.

**Assignment Email:** `claude/manager/sent/2025-12-29-1215-task-remember-last-save-directory.md`

---

### 📋 easy-configurator-download-links

**Status:** TODO
**Type:** Documentation / UX Enhancement
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-29
**Assignee:** Developer
**Estimated Time:** 1-2 hours

Add prominent download links to main pages (README and wiki) pointing to latest configurator release.

**Problem:**
Users must navigate: Releases → scroll → Assets → expand to find downloads. This is 3-4 extra clicks for a common task.

**Solution:**
Add direct link to `https://github.com/iNavFlight/inav-configurator/releases/latest` (auto-redirects, Assets expanded).

**Scope:**
- Add download section to `inav/README.md`
- Add download section to wiki home page
- Link to both configurator and firmware releases

**Benefits:**
Better onboarding experience, saves users time.

**Assignment Email:** `claude/manager/sent/2025-12-29-1200-task-easy-configurator-download-links.md`

---

### 📋 implement-3d-hardware-acceleration-auto-fallback

**Status:** TODO
**Type:** Feature Enhancement / Error Handling
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-26
**Assignee:** Developer
**Estimated Time:** 4-6 hours

Implement automatic fallback when 3D hardware acceleration fails, instead of crashing or showing errors. Detect WebGL support at runtime and gracefully degrade to 2D alternatives.

**Background:**
inav-configurator has a setting to disable 3D hardware acceleration, but users without GPU support (VMs, remote desktop, older systems) may encounter crashes or errors when the app tries to use WebGL without checking if it's available.

**Current Problem:**
- App probably attempts to create WebGL contexts without checking for support
- Likely crashes or shows cryptic errors when 3D fails
- Users must manually find and enable the "disable 3D" setting

**Solution:**
Auto-detect 3D capability and fall back gracefully when not available.

**Implementation Steps:**

1. **Investigation Phase:**
   - Find existing "disable 3D hardware acceleration" setting
   - Identify all code locations using WebGL/3D rendering
   - Document what features are affected
   - Common locations: magnetometer calibration 3D view, model viewers

2. **Capability Detection:**
   - Add inline tests for WebGL context creation
   - Detect both full failure and partial/degraded support
   - Test before attempting to use 3D features

3. **Automatic Fallback:**
   - Provide 2D alternatives where possible
   - Show user-friendly message explaining fallback
   - No crashes or cryptic errors
   - Log details for debugging

**Benefits:**
- Improved UX for users without GPU support
- No crashes or cryptic errors
- No manual setting changes required
- Graceful degradation

**Location:** `claude/projects/implement-3d-hardware-acceleration-auto-fallback/`

**Assignment Email:** `claude/manager/sent/2025-12-26-task-3d-hardware-acceleration-auto-fallback.md`

---

### ✅ analyze-pitot-blockage-apa-issue

**Status:** COMPLETED
**Type:** Bug Analysis / Safety Issue
**Priority:** MEDIUM-HIGH
**Assignment:** ✅ Complete
**Created:** 2025-12-28
**Completed:** 2025-12-28
**Assignee:** Developer
**Actual Time:** ~8 hours
**GitHub Issue:** [#11208](https://github.com/iNavFlight/inav/issues/11208)

Analyze the dangerous behavior of INAV 9's Fixed Wing APA (Airspeed-based PID Attenuation) when pitot tube fails or becomes blocked, and propose specific code changes.

**Problem:**
INAV 9's new Fixed Wing APA feature creates a safety-critical issue:
- Above cruise speed: PIFF gains reduced by up to 70% (working as intended)
- Below cruise speed: PIFF gains increased by up to 200% (problematic)

**Dangerous Failure Mode:**
When pitot tube fails, gets blocked, or sock is left on:
1. Airspeed sensor reads very low (< 25 km/h)
2. Aircraft is actually at cruise speed (~85 km/h)
3. System thinks aircraft is slow → increases PIFF gains to 200%
4. Aircraft becomes nearly unflyable with over-driven control surfaces
5. Landing becomes extremely difficult/dangerous

**Safety Impact:**
CRITICAL - pitot failures are common (mechanical failure, blockage, forgotten sock). Current behavior makes aircraft nearly unflyable in these failure conditions.

**Task:**
1. Read GitHub issue #11208
2. Read PDF document: `/home/raymorris/Downloads/pitot blockage sanity check.pdf`
3. Locate and analyze APA implementation code
4. Evaluate suggested solutions:
   - Don't increase gains below cruise speed
   - Add separate increase/decrease parameters
   - Add airspeed sanity checks
5. Propose specific code changes with rationale
6. Create detailed analysis report

**Type:** Analysis & Proposal (no implementation yet)

**Deliverable:** Analysis report in `claude/developer/reports/issue-11208-pitot-blockage-apa-analysis.md`

**Location:** `claude/projects/analyze-pitot-blockage-apa-issue/`

**Assignment Email:** `claude/manager/sent/2025-12-28-1230-task-analyze-pitot-blockage-apa-issue.md`

**Completion Summary:**
- ✅ Comprehensive 11,800+ word analysis report completed
- ✅ Identified four distinct issues requiring separate solutions
- ✅ Mathematical analysis with Python visualization
- ✅ Specific code changes proposed with line numbers
- ✅ Implementation effort estimated: 10-12 hours total
- 🔄 **Status:** Analysis complete, awaiting approval for implementation phase

**Key Findings:**
1. Pitot sensor validation needed (GPS-based sanity checks) - 8-12 hours
2. I-term scaling should be removed (control theory issue) - 15 minutes
3. Cruise speed reference - keep as-is (no change)
4. Symmetric limits [0.67, 1.5] instead of [0.3, 2.0] - 15 minutes

---


### 📋 reproduce-issue-11202-gps-fluctuation

**Status:** TODO
**Type:** Bug Investigation / Testing / Root Cause Analysis
**Priority:** MEDIUM-HIGH
**Assignment:** ✉️ Assigned
**Created:** 2025-12-26
**Assignee:** Developer
**Estimated Time:** 6-8 hours

Analyze and attempt to reproduce GitHub issue #11202 (GPS signal fluctuation) using predictable synthetic MSP GPS data to isolate the root cause.

**Issue:** https://github.com/iNavFlight/inav/issues/11202

**Problem Summary:**
GPS signal instability affecting INAV 6.0-9.0 across multiple u-blox modules (M8, M9, M10):
- Recurring EPH (estimated position error) spikes in flight logs
- Wild HDOP fluctuations (2.0-5.0 instead of stable ~1.3)
- Reduced satellite acquisition (15-18 sats instead of 25+)
- Periodic positional corrections during navigation

**Key Finding:**
`gps_ublox_nav_hz` setting significantly affects performance:
- Default 10Hz with 4 constellations: Unstable, low sat count
- Reduced to 6Hz (M10) or 9Hz (M9): Improved sat count by 8-10, HDOP stable
- INAV 7.0 defaults to 5Hz despite user settings (regression?)

**Regression:**
INAV 6.0 demonstrated superior stability compared to 7.0+

**Investigation Approach:**

1. **Analyze the Issue:**
   - Understand EPH and HDOP metrics
   - Review GPS processing code in INAV
   - Compare 6.0 vs 7.0+ GPS handling
   - Identify what changed to cause regression

2. **Create Synthetic GPS Data:**
   - Use mspapi2 to send MSP_RAW_GPS messages
   - Simulate stable baseline (25 sats, HDOP 1.3)
   - Simulate problem pattern (15-18 sats, HDOP 2-5)
   - Test at different update rates (5Hz, 6Hz, 9Hz, 10Hz)

3. **Test Different nav_hz Settings:**
   ```bash
   set gps_ublox_nav_hz = 10  # Default, problematic
   set gps_ublox_nav_hz = 9   # M9 workaround
   set gps_ublox_nav_hz = 6   # M10 workaround
   set gps_ublox_nav_hz = 5   # INAV 7.0 default
   ```

4. **Compare INAV Versions:**
   - Test on 6.0 (stable), 7.0 (regression), 9.0 (current)
   - Identify code differences
   - Find root cause of regression

**Key Questions:**
- Why does nav_hz affect satellite acquisition?
- What causes EPH spikes and HDOP fluctuations?
- What changed between 6.0 and 7.0?
- Is this firmware bug or GPS module limitation?

**Synthetic Data Script Example:**
```python
import mspapi2
import time

fc = mspapi2.FlightController("/dev/ttyACM0")

# Simulate fluctuating GPS (the problem)
for i in range(100):
    if i % 10 < 5:
        # Stable period
        send_gps(sat_count=25, hdop=130)  # HDOP 1.3
    else:
        # Unstable period (EPH spike)
        send_gps(sat_count=16, hdop=450)  # HDOP 4.5
    time.sleep(0.1)  # 10Hz
```

**Code Locations to Check:**
- `src/main/io/gps.c` - Main GPS handling
- `src/main/io/gps_ublox.c` - u-blox specific code
- `src/main/navigation/navigation.c` - Position corrections
- EPH calculation and HDOP filtering
- Satellite filtering logic

**Safety Impact:**
- GPS instability affects navigation reliability
- RTH may behave unpredictably
- Position hold could drift
- Important for user safety

**Deliverables:**
1. Analysis report of the issue and GPS code
2. Synthetic GPS data generator script (Python/mspapi2)
3. Reproduction test results (reproducible or not)
4. Root cause analysis (if found)
5. Comparison across INAV versions
6. Proposed fixes or next investigation steps

**Success Criteria:**
- Understood the issue and GPS processing
- Created reusable synthetic GPS test script
- Tested multiple nav_hz settings and INAV versions
- Determined if issue is reproducible with synthetic data
- Identified potential root cause or next steps

**Assignment Email:** `claude/manager/sent/2025-12-26-task-reproduce-issue-11202-gps-fluctuation.md`

---

### 📋 document-gps-test-tools

**Status:** TODO
**Type:** Documentation
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-27
**Assignee:** Developer
**Estimated Time:** 2-3 hours

Create comprehensive README.md for the GPS testing tools directory to serve as the main entry point for understanding and using all scripts and tools.

**Background:**
The `claude/test_tools/inav/gps/` directory contains 40+ scripts for GPS testing, motion simulation, blackbox logging, and FC configuration. Several specialized README files exist (README_GPS_BLACKBOX_TESTING.md, BLACKBOX_SERIAL_WORKFLOW.md, etc.), but there's no main overview or entry point.

**Problem:**
- Hard to find the right tool for a specific task
- No quick start guide for common workflows
- test_motion_simulator.sh (orchestration script) lacks detailed documentation
- Unclear how scripts work together
- No reference table showing dependencies

**Solution:**
Create main README.md that:
- Provides quick start examples
- Groups scripts by purpose (motion simulation, testing, configuration, monitoring)
- Documents test_motion_simulator.sh workflow in detail
- References existing specialized documentation
- Includes script reference table
- Shows common use cases and workflows

**Special Focus - test_motion_simulator.sh:**
Orchestrates motion simulation testing by:
- Starting CRSF RC sender (keeps SITL active + receives telemetry)
- Starting GPS altitude injection via MSP
- Coordinating two processes on separate MSP connections
- Collecting and displaying results

Documentation should explain:
- How the orchestration works
- Why 3-second connection delay
- Process management and error handling
- Log file locations and interpretation
- Available profiles (climb, descent, hover, sine)

**Deliverables:**
1. `claude/test_tools/inav/gps/README.md` - Main entry point
2. Quick start guide with common examples
3. Comprehensive tool/script reference
4. Use case workflows
5. Script reference table with dependencies
6. Enhanced test_motion_simulator.sh documentation

**Benefits:**
- Easier onboarding for GPS testing
- Clear entry point for all tools
- Less time hunting for the right script
- Better understanding of available infrastructure
- Comprehensive reference for future work

**Assignment Email:** `claude/manager/sent/2025-12-27-task-document-gps-test-tools.md`

---

### 🚧 reproduce-issue-9912

**Status:** IN PROGRESS (Theory Identified, Needs Verification)
**Type:** Testing / Bug Reproduction / Root Cause Analysis
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned
**Created:** 2025-12-23
**Assignee:** Developer
**Estimated Time:** 3-5 hours (original), additional time for verification

**Issue:** https://github.com/iNavFlight/inav/issues/9912 - Continuous Auto Trim active during maneuvers

**Progress So Far:**
Developer performed deep code analysis and identified a **theory** for the root cause (not yet verified).

**Theory - Missing I-term Stability Check:**
- Location: `src/main/common/servos.c:644`
- Autotrim verifies flight conditions (level, centered sticks, low rotation)
- BUT fails to check if I-term is in **steady state**
- During maneuvers, I-term accumulates transient error
- When plane momentarily satisfies level-flight, transient I-term incorrectly transferred to servo midpoints

**Proposed Fix:**
Add I-term rate-of-change stability check before allowing trim transfer.

**Analysis Report:** `claude/developer/reports/issue-9912-autotrim-analysis.md`

**Still Needed (Theory Not Yet Verified):**
Theory needs verification through one of:
1. **SITL Reproduction:** Create test script to reproduce the bug
2. **Pilot Testing:** Have pilot test the proposed fix on real hardware
3. **Additional Analysis:** Further code investigation to confirm theory

**Next Steps:**
- Either create SITL reproduction script (original task goal)
- Or work with pilot/maintainers to test proposed fix
- Verify theory matches actual bug behavior before implementing fix

**Assignment Email:** `claude/manager/sent/2025-12-23-0029-task-reproduce-issue-9912.md`

---

### 📋 analyze-pr2482-qodo-comments

**Status:** TODO
**Type:** Code Quality Analysis
**Priority:** MEDIUM-LOW
**Assignment:** ✉️ Assigned
**Created:** 2025-12-21
**Assignee:** Developer
**Estimated Time:** 1-2 hours

Analyze qodo bot comments on PR #2482 that apply to commits removed from the PR. Determine if suggestions are still applicable to current maintenance-9.x and worth implementing.

**PR:** https://github.com/iNavFlight/inav-configurator/pull/2482

**Background:**
PR #2482 (power limiting UI) has qodo bot suggestions on commits that were removed during cleanup. The suggestions might still be valuable for the current codebase.

**Analysis Required:**
1. Review all qodo bot comments on PR #2482
2. Identify which comments apply to removed commits
3. Check if issues still exist in current maintenance-9.x
4. Evaluate each suggestion (applicable? good? worth it?)

**Deliverables:**
- List of qodo bot suggestions with status
- Evaluation of each suggestion (implement vs skip)
- If implementing: effort estimate and recommended approach
- Recommendation: create new branch or skip

**Assignment Email:** `claude/manager/sent/2025-12-21-1643-task-analyze-pr2482-qodo-comments.md`

**Location:** `claude/projects/analyze-pr2482-qodo-comments/`

---

### 📋 extract-method-tool

**Status:** TODO
**Type:** CLI Tool / Extract Method Refactoring
**Priority:** MEDIUM
**Assignment:** ✉️ Assigned (UPDATED 2025-12-14)
**Created:** 2025-12-14
**Assignee:** Developer
**Assignment Email:** `claude/manager/sent/2025-12-14-task-extract-method-tool-UPDATED.md`
**Estimated Time:** 3-4 weeks

Build a CLI tool for **Extract Method** refactoring - extracting inline code blocks into new functions (NOT hoisting existing functions).

**Use Case:** Extract 50-line switch case blocks into separate functions

**Workflow:**
1. User specifies line numbers to extract
2. Tool analyzes (parameters, return values, complexity)
3. Tool previews extraction
4. User confirms
5. Tool applies with AST-verified equivalence

**Key Features:**
- Smart parameter detection (variables used but not defined)
- Smart return value detection (variables modified and used after)
- Control flow transformation (break → return in switch cases)
- AST verification with compare-ast (proof of equivalence)
- JSON output for Claude Code integration

**Technology:**
- Acorn (parser - already available)
- Commander.js (CLI framework)
- recast (AST manipulation)
- compare-ast (semantic verification)
- ~600-800 lines of code

**CLI Interface:**
```
extract-method analyze <file> --lines 145-195
extract-method preview <file> --lines 145-195 --name handleSave
extract-method apply <file> --lines 145-195 --name handleSave
```

**Documentation:**
- `CLI_SPEC.md` - Complete CLI specification with algorithms
- `TOOL_EVALUATION.md` - Research on existing tools
- `README.md` - Project overview and use cases

**Location:** `claude/projects/js-function-hoisting-tool/` (will rename to extract-method-tool)

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

**Location:** `claude/projects/feature-auto-alignment-tool/`

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

**Location:** `claude/projects/remove-transpiler-backward-compatibility/`

**Related:** Developer request in `claude/manager/inbox-archive/2025-12-20-1903-project-request-remove-transpiler-backward-compatibility.md`

---


**Note:** Completed projects are archived to `claude/archived_projects/` to keep the active project list clean.


---

## Completed & Cancelled Projects

All completed and cancelled projects have been archived for reference.

**Total Completed:** 73 projects
**Total Cancelled:** 4 projects

**See:** [COMPLETED_PROJECTS.md](COMPLETED_PROJECTS.md) for full archive

**Query Tool:**
- `python3 project_manager.py list COMPLETE` - View completed projects
- `python3 project_manager.py list CANCELLED` - View cancelled projects
