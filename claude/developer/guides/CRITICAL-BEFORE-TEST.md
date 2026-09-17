# ⚠️ CRITICAL CHECKLIST - Read Before Testing

> **Workflow:** steps 5, 8 of 17 → `WORKFLOW.md`.

**Use this checklist when testing code changes:**

## Testing Philosophy

### Bug Fixes: Test-First Approach

**For bug fixes, ALWAYS:**
**Use a task list tool to track these steps.**
1. **First:** Write a test that REPRODUCES the bug (test should FAIL)
2. **Then:** Implement the fix
3. **Finally:** Run the test again (test should PASS)

**Why:** You can't verify a fix if you can't reproduce the problem.

**For configurator/UI-only changes with no unit-testable seam** (wizard flows, save
dialogs, rendering), drive an already-running Configurator — debug mode, connected to a
test FC — via CDP (Chrome DevTools Protocol) or similar: open the tab → trigger the
action → verify the result persisted (reconnect, or check the file on disk). If you can't
drive it, ask the user for manual assistance. This check is mandatory before PR. Running
the existing test suite is a *regression* check, not the reproduction.

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

## Self-Improvement: Lessons

Add concise, actionable one-liners (see `guides/README.md` Capture Rubric). State the
rule, not the story. Reference facts (SITL/MSP quirks) go at the bottom.

#### Testing Methodology

- **A "rewrite real source, run it" test goes stale when the target gains a new import**: on `ERR_MODULE_NOT_FOUND`, check whether the target file grew an import the test's rewrite rules don't know, before blaming the test/env.
- **`$TMPDIR` here resolves inside the repo tree, not `/tmp`**: for tests needing an isolated git repo, make the fixture a real `git init`'d repo (with a commit) or force `/tmp`.
- **Native OS dialogs can't be tested via Chrome DevTools MCP**: `showSaveDialog`/`showOpenDialog` are GTK/native — test those manually.
- **A background test-engineer agent can silently stall on an unapproved permission prompt**: zero progress across several polls on a quick step = suspect a stuck prompt, not a slow build.
- **INAV `unit_test()` CMake requires a sibling `.h` for every `depends` entry**: a `.c` whose header lives in vendored `lib/` must be wired via `extra_sources`, not `depends`.
- **Verify JS mirrors of firmware algorithms with a diff harness, not by hand**: drive the real JS module and diff against the C model (harness at `claude/agents/target-developer/scripts/compare-js-c/`).
- **A hand-copied reproduction is a last-ditch fallback, not the default**: first extract the logic into a dependency-free `.c`/`.h` and link the real file into the test; hand-copy only when that's impractical — and a hand-copy still beats no test.

#### SITL / MSP / Hardware Reference Notes

- **INAV debug mode enum starts at NONE=0** (RATE_DYNAMICS=18, not 17) — count from the enum, not memory.
- **SITL arming needs sensors-calibrated state** (~5s after reboot even with HITL); establish armed state first.
- **SITL failsafe persists across runs** — reboot SITL between test runs.
- **MSP_RC returns axis-reordered channels, not raw frame order** — with AETR map [0,1,3,2], send RC frames in physical AETR order, not logical axis order.
- **SITL MSP_REBOOT execvp-restarts (same PID)** — in-memory state resets but the closed EEPROM file persists; for clean state, pkill+relaunch.
- **ARMING_DISABLED_RC_LINK only updates when DISARMED** — to observe RC-link loss in flags, the FC must not be armed.
- **Receiver type change needs reboot** — takes effect next boot.
- **SITL arm needs 2s pre-arm with AUX1 LOW** (not 0.6s) while refreshing HITL, before raising AUX1.
- **Unbound ELRS RX auto-enters WiFi AP after ~60s** — power-cycle FC/USB between passthrough tests (soft reboot doesn't reset the RX).
- **inav-configurator JS/HTML edits need no build/flash** — Electron loads source directly; only build when adding new files.
- **Verify a sign convention against the variable's real consumer** — `pitch >0` means opposite things in nav target vs estimated attitude.

<!-- Add new lessons above this line -->
