# Root Cause Analysis: From Symptoms to Systemic Fixes

**When to use this:** When you discover a bug, failing test, or unexpected behavior.

---

## The Problem with Symptom Fixes

**Surface-level fix (❌ Insufficient):**
```
Symptom: Feature X doesn't work
→ Add missing rule/config for X
→ Move on
→ Feature Y fails silently next week
→ Same fix cycle repeats
```

**Root cause fix (✅ Comprehensive):**
```
Symptom: Feature X doesn't work
→ Why? (Documentation/implementation mismatch)
→ Why not detected? (Silent failure = no error reporting)
→ What else might fail? (All similar features)
→ Fix systematically (Error reporting in all agents)
→ Prevent future occurrence (Update guidelines/templates)
```

---

## The Root Cause Analysis Framework

### Level 1: What Failed? (Symptom)
**What** you observe.

**Example:** ScheduleWakeup tool isn't allowed

**Next:** Ask "Why?"

---

### Level 2: Why Did It Fail? (Immediate Cause)
**Why** the symptom occurred.

**Example:** Configuration system uses 3 split files, but agent documentation referenced 1 non-existent file

**Clue that you found it:** You can explain the failure in terms of the system's design

**Next:** Ask "Why wasn't this detected?"

---

### Level 3: Why Wasn't It Detected? (Systemic Cause)
**Why** the failure persisted unnoticed.

This is often the **most important question**. If a bug is invisible, it can hide for months.

**Example:** Agent failed silently without reporting errors to user

**Common systemic causes:**
- ❌ Silent failures (no error reporting)
- ❌ No validation (changes not checked)
- ❌ Incomplete tests (missing edge cases)
- ❌ No monitoring (no visibility into failures)
- ❌ Documentation drift (docs out of sync with code)

**Next:** Ask "What else might have this same vulnerability?"

---

### Level 4: What Else Might Fail? (Systemic Risk)
**What other systems** share the same vulnerability.

This transforms a one-bug fix into a system-wide improvement.

**Example:** 
- ❌ Permissions agent could fail silently
- ❌ All other agents could fail silently
- ❌ All future agents would inherit the same problem
- ❌ Bugs in other agents might already be hidden

**Result of fixing this level:**
- Fix 13 existing agents
- Fix agent template
- Fix agent-builder guidelines
- Prevent unknown bugs in future agents

---

## The Four-Question Framework

When you find any bug, ask these in order:

1. **What failed?** → Identify the symptom
2. **Why?** → Find the immediate cause
3. **Why wasn't it detected?** → Find the systemic cause
4. **What else might fail the same way?** → Find the scope of the fix

---

## Real-World Example: ScheduleWakeup Bug

### Question 1: What Failed?
```
Permission request for ScheduleWakeup tool was denied
Expected: Auto-allow
Actual: Prompted user
```

### Question 2: Why?
```
No rule exists for ScheduleWakeup tool
→ Check rule file...
→ Rule file references non-existent tool_permissions.yaml
→ Actual system uses 3 split files
→ Documentation ≠ Implementation
```

### Question 3: Why Wasn't This Detected?
```
Agent tried to add rule
→ No validation after edit
→ Failed silently (no error reported)
→ No one knew the fix didn't work
→ Bug persisted 4+ months
```
**This is the critical discovery.** Silent failures are worse than loud failures.

### Question 4: What Else Might Fail?
```
All agents could fail silently
→ No error reporting in any agent
→ No explicit "fail loudly" requirement
→ Future agents would inherit the problem
→ Multiple unknown bugs could be hiding

Solution: Add error handling to ALL agents
Result: Fixes 13 existing agents + future agents
```

---

## Levels of Fixes

When you identify a bug, choose your fix level:

### Level 1: Symptom Fix (1-line change)
**Fix the immediate problem only.**

✅ **Use when:** The bug is isolated and won't recur elsewhere
❌ **Use when:** Multiple systems could have the same issue

**Example:** Just add the ScheduleWakeup rule (insufficient)

---

### Level 2: Cause Fix (Documentation/code update)
**Fix the broken design or documentation.**

✅ **Use when:** The design is flawed or out of date
✅ **Use when:** Other systems might have the same issue

**Example:** Fix documentation to reference split files correctly

---

### Level 3: Systemic Fix (Update guidelines and templates)
**Fix the root cause AND prevent recurrence.**

✅ **Use when:** You discover a gap in error handling, validation, or oversight
✅ **Use when:** The vulnerability affects multiple systems
✅ **Use when:** Future systems would inherit the problem

**Example:** Add error handling requirement to all agents + agent template

---

## How to Recognize You've Found the Real Problem

You've likely found it when you can answer "Yes" to:

- [ ] It explains the original symptom clearly
- [ ] It explains why the bug wasn't detected
- [ ] It reveals a vulnerability in other systems
- [ ] Fixing it would prevent similar bugs elsewhere
- [ ] The fix is more valuable than just handling the symptom

---

## The Cascading Benefit

When you fix systemically, improvements cascade:

```
Fix the immediate problem
↓
Reveals why it wasn't detected
↓
Reveals systemic vulnerability
↓
Fix affects not just this bug, but entire system
↓
Prevents unknown future bugs
↓
Improves architecture
```

**Example cascade:**
```
ScheduleWakeup rule
→ Documentation mismatch
→ Silent failure mechanism
→ Update all 13 agents
→ Update agent template
→ Update agent-builder
→ Prevent future failures
→ Improve system transparency
```

---

## Practical Steps

When debugging any issue:

1. **Write it down** - Describe the symptom
2. **Ask "Why?"** - Find the immediate cause
3. **Ask "Why not detected?"** - Find the systemic cause
4. **Ask "What else?"** - Identify the scope
5. **Decide fix level** - 1-line symptom fix vs. systemic fix
6. **Implement comprehensively** - Fix at the level you decided
7. **Document learning** - Add to lessons learned

---

## References

**Related guides:**
- `debugging-guide.md` - Tools and techniques for debugging
- `CRITICAL-BEFORE-CODE.md` - Before implementing fixes

**Related documentation:**
- `claude/developer/guides/` - All developer guidelines
- `.claude/agents/permissions-manager.md` - Example of systemic fix

---

## Self-Improvement: Lessons Learned

When you discover something important about ROOT CAUSE ANALYSIS that will help in future sessions, add it to this section. Only add insights that are:
- **Reusable** - will apply to future debugging, not one-off situations
- **About methodology** - problem-solving approach, not specific bugs
- **Concise** - one line per lesson

Use the Edit tool to append new entries. Format: `- **Brief title**: One-sentence insight`

### Lessons

- **Silent failures are catastrophic** (2026-07-01): A bug that fails silently can hide for months because no one knows it happened. When analyzing bugs, always ask "Why wasn't this detected?" - that often reveals the real problem.
- **A build tool's fail-fast default can hide N-1 other failures behind the first one** (2026-07-22): `ninja`'s default `-k 1` stops scheduling new work at the first failure, so a "test" job that's been red for a while may only ever have shown you the *first* broken target — fixing it can unmask several more, unrelated, pre-existing failures that were never actually reached. Before assuming a fix makes a suite fully green, re-run with `-k 0` (or equivalent) to see the whole picture, and check whether newly-visible failures are regressions from your change or were already broken (compare against the unmodified base commit) before folding them into your fix's scope.
- **Macro leaking into a translation unit has two distinct failure classes needing different fixes** (2026-07-22): when a shared header starts exposing production macros to code that didn't expect them, distinguish (a) the macro was *already defined* elsewhere (via `-D` or an earlier header) and now collides — fixable with an `#ifndef` guard, harmless by construction since presence-only flags don't have competing values — from (b) the macro is *newly, singly* defined and legitimately changes compiled behavior (e.g. widens a type, enables a code path referencing unlinked symbols) — an `#ifndef` guard is a no-op here since nothing preceded it, and the real fix has to address the actual behavior change (update dependent code, exclude the enabled path for the affected build, etc). Misdiagnosing (b) as (a) and reaching for a guard wastes a cycle finding out it didn't help.

- **Fix level matters** (2026-07-01): A one-line symptom fix feels fast but leaves the systemic vulnerability. Systemic fixes take longer but prevent unknown future bugs. Prefer systemic fixes when you discover a design gap.

- **Cascading benefits** (2026-07-01): When you fix a systemic issue, improvements affect systems you didn't know were vulnerable. Fixing error handling in the permissions agent revealed that all agents could fail silently.
- **A fix for an implicit-agreement bug can silently recreate the same bug one layer up** (2026-08-02): When a bug's root cause is "two things silently assume they agree about a key/ordering/value without that agreement being enforced," the fix itself often introduces a *new* implicit-agreement mechanism instead of removing the pattern entirely — e.g. `settings.rb`'s `check_conditions()`/`resolve_types()` disagreed because one was position-independent and one wasn't; the first fix made both position-dependent, but `check_conditions()`'s internal cache was still keyed by condition *string* (a non-unique key across positions), reintroducing the exact same "assumed-unique key that isn't" failure one level up — caught by an automated reviewer, not by the author. After any such fix, explicitly re-scan the new code for the same shape (new caches/keys/globals — are they *structurally* guaranteed unique, or just unique in today's data?) before considering it done, and check against real project data, not just the synthetic repro that proved the original bug.

- **A wrapper that changes a wrapped API's return shape fails silently at every call site**: PR #2448's new `js/bridge.js` abstraction rewired local file reads, but its Electron `readFile()` returned `.toString()` of the IPC result object (yielding `"[object Object]"`) instead of the result's `data` field — breaking the flasher's local-hex load ("corrupted" error). It surfaced only when a user actually loaded a local file, because build/rendering smoke tests never exercised the feature. When a new abstraction wraps an API, verify its return contract against the wrapped API at runtime (this one was caught by comparing `window.electronAPI.readFile(...)` output with `bridge.readFile(...)` output in the live app).
- **A reporter's list of suspect sites is a hypothesis, not the audit scope** (2026-08-20): auditing the six MSP handlers a security researcher flagged (#11672) found all six correctly bounded, and "no bug found" was very nearly the final answer. The actual defect was in an *adjacent* code path the reporter never listed — `mspProcessSensorCommand` computes the payload size, explicitly discards it (`UNUSED(dataSize)`), and hands a raw pointer to handlers that cast it to a 52-byte packed struct. It surfaced only because a follow-up question ("is there a compile-time way to prevent this class?") forced a look at how *other* code in the same family handles the same problem. When a report names specific locations, verify them, then separately ask "what else has this shape?" — an outside reporter greps for a pattern signature (here, unsafe `sbufRead*` calls) and will systematically miss instances that use a *different* mechanism to commit the same error (here, a struct cast with no reads at all). Reporting the named list clean, without that second pass, is an accurate answer to the wrong question.
- **A pairing cache goes stale unless intervening input invalidates it** (2026-08-31): when a fix detects mutually-exclusive pairs (e.g. enum-doc generator's `#ifdef X`/`#ifndef X` sibling branches sharing a value base), the "last closed sibling" cache must be cleared whenever an enumerator is parsed between the two blocks — otherwise a later opposite-polarity block wrongly reuses the earlier branch's base (`A, #ifdef X B, #endif, C=10, #ifndef X D` emitted D=1 instead of 11). Only *adjacent* blocks are alternates; test the non-adjacent variant of every pairing pattern, not just the adjacent repro that proves the bug (Qodo caught this; the author's synthetic tests all used adjacent blocks).
<!-- Add new lessons above this line -->
