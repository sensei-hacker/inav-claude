# ⚠️ CRITICAL CHECKLIST - Read Before Testing

**Use this checklist when testing code changes:**

## Testing Philosophy

### Bug Fixes: Test-First Approach

**For bug fixes, ALWAYS:**
**Use a task list tool to track these steps.**
1. **First:** Write a test that REPRODUCES the bug (test should FAIL)
2. **Then:** Implement the fix
3. **Finally:** Run the test again (test should PASS)

**Why:** You can't verify a fix if you can't reproduce the problem.

Use `test-engineer` agent:
```
Prompt: "Reproduce issue #XXXX: [description of bug].
Expected: [expected behavior]. Actual: [actual behavior].
Relevant files: [file paths]
Save test to: claude/developer/workspace/[task-name]/"
```

### New Features: Test After Implementation

**Use a task list tool to track these steps.**
1. Implement the feature
2. Write tests that verify it works
3. Test edge cases and error conditions

---

## Testing Requirements by Project

### INAV Firmware Testing

**Use `inav-builder` agent to build:**
```
Prompt: "Build SITL"
```

**Use `sitl-operator` agent to run SITL:**
```
Prompt: "Start SITL"
```

**Use `test-engineer` agent to test:**
```
Prompt: "Test my changes with SITL.
Modified files: [list files]
Expected behavior: [what should happen]"
```

### INAV Configurator Testing

**Use `test-engineer` agent:**
```
Prompt: "Run configurator unit tests.
Modified files: [list files]"
```

**Or use `run-configurator` skill** for manual testing

---

## NEVER Assume Tests Are Broken

**If a test fails:**
- It means there IS work to be done
- Investigate why it failed
- Fix the issue (either code or test)
- NEVER ignore failing tests
- NEVER assume "that test was already broken"

---

## Test Organization

Save test files in task workspace:
```
claude/developer/workspace/[task-name]/
├── test_feature.py
├── test_data/
└── results.log
```

Where a test file may be useful in the future for other issues, save it in your library of test tools
---

## Agent Usage

**For all testing, use `test-engineer` agent:**
- It doesn't fix code (that's your job)
- It writes and runs tests only
- It validates your changes work correctly

---

**Testing complete? Document results in completion report.**

---

## Self-Improvement: Lessons Learned

When you discover something important about TESTING APPROACHES that will likely help in future sessions, add it to this section. Only add insights that are:
- **Reusable** - will apply to future testing tasks, not one-off situations
- **About testing** - test-first approach, debugging, reproduction, validation
- **Concise** - one line per lesson

Use the Edit tool to append new entries. Format: `- **Brief title**: One-sentence insight`

### Lessons

- **INAV debug mode enum offset**: debug.h enum values start at NONE=0; RATE_DYNAMICS=18 (not 17 as often assumed) because AUTOTUNE=17 precedes it - always count from the enum definition, not from memory.
- **SITL arming requires sensors-calibrated state**: After a fresh SITL reboot, sensors take ~5s to calibrate even with HITL; tests that arm immediately after HITL enable may fail with ARM_SWITCH; use sitl_arm_test.py first to establish a known-good armed state.
- **SITL failsafe persists across test runs**: Each test run that arms then stops RC leaves SITL in failsafe (ARMING_DISABLED_FAILSAFE_SYSTEM); subsequent arming attempts fail until SITL reboots or failsafe clears; reboot SITL between test runs.
- **MSP_RC returns axis-reordered channels not raw frame order**: With AETR rcmap [0,1,3,2], MSP_RC[2]=THROTTLE value means the physical input at raw[rcmap[THROTTLE=3]]=raw[2]; send RC frames in physical AETR order [ROLL,PITCH,THROTTLE,YAW,AUX1] not logical axis order.
- **SITL MSP_REBOOT does execvp restart (same PID)**: In SITL, MSP_REBOOT calls execvp() which replaces the process image but keeps the same PID; in-memory runtime state (ARMED, HITL) should reset but state from the closed EEPROM file persists; for guaranteed clean state use OS-level pkill+relaunch.
- **A test that mechanically rewrites a real file's import specifiers goes stale silently when the file gains a new import**: `tests/cli-tab-msp-polling.test.mjs` (inav-configurator) loads real production files and rewrites only the import lines it has explicit substitution rules for; when `tabs/cli.js` later gained `bridge`/`interval` imports, those two were left untouched and resolved against the test's temp directory instead of the project tree (`ERR_MODULE_NOT_FOUND`). The test's own `mustReplace()` guard only catches a *listed* pattern going missing, not an *unlisted* new import appearing — when a "rewrite real source, run it for real" test starts failing with a module-resolution error, check whether the target file simply grew an import the test doesn't know about yet, before assuming the test itself (or the surrounding environment) is broken.
- **$TMPDIR in this environment is inside the repo tree**: `tempfile.mkdtemp()`/`TemporaryDirectory()` resolve under `.../inavflight/tmp`, not `/tmp`. A fake `.git/FETCH_HEAD`-only directory there does NOT stop `git`'s upward directory search (an incomplete `.git` isn't treated as a repo boundary), so `git -C <temp-dir>` silently escapes to the real project repo instead of staying isolated. For tests that need an isolated git repo, either force `/tmp` explicitly or - safer - make the fixture a real `git init`'d repo with an actual commit, which genuinely stops the walk.
- **ARMING_DISABLED_RC_LINK only updated when DISARMED**: updateArmingStatus() skips all flag checks (including RC_LINK) when ARMED; to observe RC link loss via ARMING_DISABLED_RC_LINK in arming flags, the FC must be NOT ARMED.
- **Receiver type change needs reboot**: Setting receiver_type=MSP via MSP_SET_RX_CONFIG + EEPROM_WRITE takes effect on the NEXT boot; tests that arm immediately after changing receiver_type will fail with RC_LINK disabled; pre-configure EEPROM before the restart that the test will use.
- **SITL arm sequence needs 2s pre-arm with AUX1 LOW**: sitl_arm_test.py's proven pattern: send AUX1 LOW for 2 seconds (not 0.6s) while refreshing HITL every 0.1s; this clears ARM_SWITCH flag and SENSORS_CALIBRATING before raising AUX1 to arm.
- **Configurator UI features require manual end-to-end testing**: Unit tests of string/logic are insufficient — the Electron renderer lacks Node.js globals (e.g. `fs` is undefined); always exercise the actual feature in the running app before committing. For save dialogs: open the tab, trigger the action, verify the file on disk.
- **Native OS dialogs cannot be tested via Chrome DevTools MCP**: `showSaveDialog` / `showOpenDialog` open GTK/native dialogs that no browser automation tool can interact with; these must be tested manually by the user.
- **A background test-engineer agent needing sandbox-gated commands (e.g. `dangerouslyDisableSandbox` for SITL localhost networking) can silently stall on a permission prompt nobody is present to approve**: repeated `TaskOutput` polls will keep returning the same stale cached transcript with no indication it's blocked, which looks identical to "still running a long build." If a background agent shows zero progress across several polls spanning many minutes on what should be a quick step, suspect a stuck permission prompt before assuming it's just slow.
- **INAV `unit_test()` CMake requires a sibling `.h` for every `depends` entry**: `src/test/unit/CMakeLists.txt`'s `unit_test()` transforms each `.c` in a test's `depends` to its `.h` and errors if that header doesn't exist. A new `.c` without a sibling header (e.g. `mavlink_helpers.c`, whose header lives in vendored `lib/`) must be wired via the `extra_sources` property instead — same source list, no `.h` transform.
- **Unbound ELRS receivers auto-enter WiFi AP mode after ~60s without a transmitter signal**: an ELRS RX with no bound/active TX stops answering CRSF UART handshakes (bootloader sync, DEVICE_PING) once it drops into WiFi mode, which looks exactly like a passthrough/transport failure — even a control that previously passed will then return 0 bytes. An FC soft reboot does NOT power-cycle the RX, so the 60s timer keeps running across CLI-exit reboots; for repeatable ELRS passthrough tests, power-cycle the FC/USB between runs (or bind the RX to a live TX) so each attempt starts in a fresh normal-mode window. ELRS Configurator's own "Cannot detect RX target" is often this + a real baud/handshake bug compounding.
- **Verify JS mirrors of firmware algorithms with a diff harness, not by hand**: `outputMapping.js` re-implements `pwm_mapping.c`'s output-assignment algorithm, and eyeballing equivalence misses real divergences (an LED gate bug, conflicted-pad mis-previews). Drive the REAL JS module (bundled with the configurator's esbuild) with post-resolution flags generated by the C model (`simulate_pwm_roles.py`) and diff per-output — reusable harness at `claude/agents/target-developer/scripts/compare-js-c/`. Related: such JS/C duplications are version-coupling hazards, which is why maintenance-10.x replaced the JS path with the firmware-authoritative MSP2_INAV_OUTPUT_ASSIGNMENT API.
<!-- Add new lessons above this line -->
