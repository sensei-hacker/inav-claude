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

## Self-Improvement: Lessons

Add concise, actionable one-liners (see `guides/README.md` Capture Rubric). State the
rule, not the story.

- **A build tool's fail-fast can hide N-1 other failures behind the first**: re-run with `-k 0`; check whether newly-visible failures are regressions or pre-existing.
- **A leaked macro has two failure classes, not one**: already-defined (collision → `#ifndef` guard) vs newly-defined (real behavior change → fix the dependent code); don't guard the latter.
- **A subagent's "it crashed" verdict is a hypothesis, not a fact** — reproduce with a minimal raw request/response probe before accepting a live-protocol failure diagnosis.
- **Fixing an implicit-agreement bug can recreate it one layer up** — re-scan new caches/keys/globals for *structural* uniqueness, against real data, not the synthetic repro.
- **A new wrapper that changes a wrapped API's return shape fails silently** — verify its return contract at runtime against the wrapped API.
- **A reporter's list of suspect sites is a hypothesis, not the audit scope** — verify the named sites, then ask "what else has this shape?"
- **A pairing cache goes stale unless intervening input invalidates it** — test non-adjacent variants, not just the adjacent repro that proved the bug.
- **Trace the code that sets a value before asserting its mechanism** — inference from the symptom is not root cause.
- **A UI color encodes semantics** — confirm what it means before redefining the condition that drives it.
- **Trace what runs synchronously before labeling something a "race"** — it can turn out to be deterministic, which changes how confidently you can explain the symptom's reliability.

<!-- Add new lessons above this line -->
