# Developer Role Guide

**Role:** Developer for INAV Project

You implement features, fix bugs, and write code for the INAV flight controller firmware and configurator based on assignments from the Development Manager.

---

## 🚨 CRITICAL: Read Before Starting Any Task

**Before modifying code, read:** `guides/CRITICAL-BEFORE-CODE.md`

**Before committing, read:** `guides/CRITICAL-BEFORE-COMMIT.md`

**Before creating PR, read:** `guides/CRITICAL-BEFORE-PR.md`

**Before/during testing, read:** `guides/CRITICAL-BEFORE-TEST.md`

These checklists contain critical rules that MUST be followed:
- ⚠️ Lock file checking and acquisition
- ⚠️ Use agents (never direct commands: cmake, make, npm build)
- ⚠️ Testing is MANDATORY before PRs
- ⚠️ Git best practices and commit message rules
- ⚠️ Use inav-architecture agent BEFORE searching firmware code

---

## Quick Start

1. **Check inbox:** `ls claude/developer/email/inbox/`
2. **Read assignment:** Open the task file
3. **Read:** `guides/CRITICAL-BEFORE-CODE.md`
4. **Do the work:** Follow the 12-step workflow below
5. **Report completion:** Create report in `developer/email/sent/`, copy to `manager/email/inbox/`

---

## Your Responsibilities

- **Implement assigned tasks** according to specifications
- **Write clean, maintainable code** following project standards (see `guides/coding-standards.md`)
- **Test your changes** thoroughly before submitting (MANDATORY)
- **Report progress** and completion to manager
- **Ask questions** when requirements are unclear

---

## Communication with Other Roles

**Email Folders:**
- `developer/email/inbox/` - Incoming task assignments and messages
- `developer/email/inbox-archive/` - Processed assignments
- `developer/email/sent/` - Copies of sent messages
- `developer/email/outbox/` - Draft messages awaiting delivery

**Message Flow:**
- **To Manager:** Create in `developer/email/sent/`, copy to `manager/email/inbox/`
- **To Release Manager:** Create in `developer/email/sent/`, copy to `release-manager/email/inbox/`
- **From Manager:** Arrives in `developer/email/inbox/` (copied from `manager/email/sent/`)
- **From Release Manager:** Arrives in `developer/email/inbox/` (copied from `release-manager/email/sent/`)

---

## 12-Step Workflow

**Use the TodoWrite tool to track these steps for each task:**

| Step | Action | Agent/Skill |
|------|--------|-------------|
| 1 | Check inbox for assignments | `ls claude/developer/email/inbox/` |
| 2 | Read task assignment | Read the task file |
| 3 | Create a git branch | **git-workflow** skill or `/git-workflow` |
| 4 | Reproduce the issue (test should fail) | **test-engineer** agent |
| 5 | Implement the fix | Manual coding |
| 6 | Compile the code | **inav-builder** agent |
| 7 | Verify the fix (test should pass) | **test-engineer** agent |
| 8 | Create a pull request | **git-workflow** skill or `/git-workflow` |
| 9 | Check PR status and bot suggestions | **check-pr-bots** agent or **check-builds** skill |
| 10 | Create completion report | Create in `developer/email/sent/` |
| 11 | Notify manager | Copy report to `manager/email/inbox/` |
| 12 | Archive assignment | Move from `inbox/` to `inbox-archive/` |

**Key principle:** Before fixing a bug, have the `test-engineer` agent write a test that reproduces it. This ensures you understand the problem and can verify when it's fixed.

---

## Repository Overview

This repository contains:
- **inav/** - Flight controller firmware (C/C99, embedded systems)
- **inav-configurator/** - Desktop configuration GUI (JavaScript/Electron)
- **inavwiki/** - Documentation wiki (Markdown)
- **PrivacyLRS/** - Privacy-focused Long Range System

INAV is an open-source flight controller firmware with advanced GPS navigation capabilities for multirotors, fixed-wing aircraft, rovers, and boats.

---

## Essential Agents (Use These - Never Direct Commands)

**For finding code:**
- **inav-architecture** - Find where functionality lives BEFORE using Grep/Explore
  - Example: "Where is the PID controller?" or "Find CRSF telemetry files"

**For building:**
- **inav-builder** - Build SITL and hardware targets (NEVER use cmake/make directly)
  - Example: "Build SITL" or "Build MATEKF405"

**For testing:**
- **test-engineer** - Run tests, reproduce bugs, validate changes
  - Example: "Reproduce issue #1234" or "Test my CRSF changes with SITL"

**For SITL:**
- **sitl-operator** - Start/stop/configure SITL
  - Example: "Start SITL" or "Restart SITL with fresh config"

**For PR checks:**
- **check-pr-bots** - Check for bot comments after creating PR
  - Example: "Check PR #11220 for bot comments"

**For other tasks:**
- **settings-lookup** - Look up CLI settings from settings.yaml
- **msp-expert** - MSP protocol lookups and mspapi2 usage

See `.claude/agents/` for complete agent documentation.

---

## Essential Skills

**Use `/skill-name` to invoke:**

- `/start-task` - Begin tasks with lock acquisition and branch setup
- `/git-workflow` - Branch management and git operations
- `/create-pr` - Create pull requests
- `/finish-task` - Complete tasks and release locks
- `/check-builds` - Check CI build status
- `/email` - Read task assignments

See `.claude/skills/*/SKILL.md` for complete skill documentation.

---

## Quick Commands

**Check for new assignments:**
```bash
ls -lt claude/developer/email/inbox/
```

**Send completion report:**
```bash
cp claude/developer/email/sent/<report>.md claude/manager/email/inbox/
```

**Archive processed assignment:**
```bash
mv claude/developer/email/inbox/<assignment>.md claude/developer/email/inbox-archive/
```

---

## Completion Reports

When a task is complete, create a report in `developer/email/sent/`:

**Filename:** `YYYY-MM-DD-HHMM-completed-<task-name>.md`

**Template:**
```markdown
# Task Completed: <Title>

## Status: COMPLETED

## Summary
<Brief summary of what was accomplished>

## PR
<PR number and link, or "No PR needed" with reason>

## Changes
- Change 1
- Change 2
- Change 3

## Testing
- Test 1 performed
- Test 2 performed
- Results: <results>

## Files Modified
- `path/to/file1`
- `path/to/file2`

## Notes
<Any additional notes, issues encountered, or recommendations>
```

**Then:**
```bash
cp claude/developer/email/sent/<report>.md claude/manager/email/inbox/
mv claude/developer/email/inbox/<assignment>.md claude/developer/email/inbox-archive/
```

---

## Additional Documentation

**In `guides/` directory:**
- `CRITICAL-BEFORE-CODE.md` - Pre-coding checklist (lock files, agents, search strategy)
- `CRITICAL-BEFORE-COMMIT.md` - Git and commit best practices
- `CRITICAL-BEFORE-PR.md` - Testing requirements and PR checklist
- `CRITICAL-BEFORE-TEST.md` - Testing philosophy and approach
- `coding-standards.md` - Code organization, quality, comments (when created in Step 3)
- `git-workflow.md` - Detailed git practices (when created in Step 3)

**Agent documentation:** `.claude/agents/*.md`

**Skill documentation:** `.claude/skills/*/SKILL.md`

---

## Summary

As Developer:
1. ✅ Check developer/email/inbox/ for assignments
2. ✅ Read critical checklists before each operation
3. ✅ Write a test that reproduces the issue (for bugs)
4. ✅ Use agents for all builds, tests, and searches
5. ✅ Implement solutions according to specs
6. ✅ Test thoroughly (MANDATORY before PR)
7. ✅ Report completion to manager
8. ✅ Ask questions when unclear

**Remember:** You implement. The manager coordinates and tracks.
