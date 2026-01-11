# Developer Guides - Context-Sensitive Checklists

These critical checklists provide **just-in-time information** - read them right before the operation they describe.

## When to Read Each Guide

| Operation | Read This File | Purpose |
|-----------|----------------|---------|
| **Starting any task** | `CRITICAL-BEFORE-CODE.md` | Lock files, branch creation, agent usage |
| **Before `git commit`** | `CRITICAL-BEFORE-COMMIT.md` | Git best practices, commit message rules |
| **Before creating PR** | `CRITICAL-BEFORE-PR.md` | Testing requirements, PR checklist, bot checks |
| **Before/during testing** | `CRITICAL-BEFORE-TEST.md` | Test-first approach, testing requirements |

## Integration Points

These guides should be read by:

- **Developer (you)** - Read `CRITICAL-BEFORE-CODE.md` when starting a task
- **`/start-task` skill** - Reads and enforces `CRITICAL-BEFORE-CODE.md`
- **`/git-workflow` skill** - Reads and enforces `CRITICAL-BEFORE-COMMIT.md`
- **`/create-pr` skill** - Reads and enforces `CRITICAL-BEFORE-PR.md`
- **`test-engineer` agent** - Has `CRITICAL-BEFORE-TEST.md` in its instructions

## Design Philosophy

**Problem:** 840-line README is overwhelming; critical rules get forgotten.

**Solution:** Context-sensitive checklists (< 50 lines each) read exactly when needed.

**Benefits:**
- Critical info delivered at the right moment
- No cognitive overload from reading everything upfront
- Each checklist is short, focused, and memorable
- Enforced by skills/agents that read them automatically

## File Sizes

All checklists are intentionally brief:
```bash
$ wc -l CRITICAL-*.md
  59 CRITICAL-BEFORE-CODE.md
  66 CRITICAL-BEFORE-COMMIT.md
 102 CRITICAL-BEFORE-PR.md
  97 CRITICAL-BEFORE-TEST.md
 324 total
```

Each file is focused and readable in under 2 minutes.
If any file grows beyond ~120 lines, it should be split or streamlined.
