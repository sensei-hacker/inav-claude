# ⚠️ CRITICAL CHECKLIST - Read Before Testing

**Use this checklist when testing code changes:**

## Testing Philosophy

### Bug Fixes: Test-First Approach

**For bug fixes, ALWAYS:**
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

<!-- Add new lessons above this line -->
