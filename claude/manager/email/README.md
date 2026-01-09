# Manager Email System

This directory handles communication between roles (Manager, Developer, Release Manager).

## Directory Structure

```
email/
├── inbox/           # Incoming messages (unprocessed)
├── inbox-archive/   # Processed messages (for reference)
├── sent/            # Copies of messages you sent
└── outbox/          # Drafts awaiting delivery
```

## Handling Incoming Email

### 1. Check Inbox

```bash
ls -lt claude/manager/email/inbox/ | head
```

### 2. Process by Message Type

#### Completion Report (Project Complete)

**Indicators:** "COMPLETE", "completed", "finished" in status

**Actions:**
1. Read the full report
2. Verify work is complete (tests pass, PR created if needed)
3. **Update project tracking:**
   ```bash
   # Move project directory to completed/
   mv claude/projects/active/<project>/ claude/projects/completed/

   # Remove entry from INDEX.md
   # Add entry to completed/INDEX.md
   ```
4. Archive the email:
   ```bash
   mv claude/manager/email/inbox/<report>.md claude/manager/email/inbox-archive/
   ```

#### Partial Completion Report

**Indicators:** "IN PROGRESS", "Phase X complete", "partial"

**Actions:**
1. Read the report
2. Update project status in INDEX.md (e.g., "Phase 1 complete, Phase 2 in progress")
3. Update project's summary.md with progress notes
4. Archive the email

#### Status Update / Progress Report

**Indicators:** "status", "update", "progress"

**Actions:**
1. Read the report
2. Update project notes if significant
3. Archive the email

#### Question / Request for Guidance

**Indicators:** "question", "clarification", "decision needed"

**Actions:**
1. Read the question
2. Send guidance response (see Sending Email below)
3. Archive the original email

#### Bug Report / Issue Found

**Indicators:** "bug", "issue", "found problem"

**Actions:**
1. Read the report
2. Create new project if significant, or add to existing project's notes
3. Archive the email

### 3. Update Project Tracking

When processing completion reports, always update:

1. **Project directory location** (move to completed/ if done)
2. **INDEX.md** (remove if done, update status if partial)
3. **completed/INDEX.md** (add entry if project complete)
4. **Project counts** in both index files

## Sending Email

### To Developer

```bash
# 1. Create in sent/
# 2. Copy to developer inbox
cp claude/manager/email/sent/<message>.md claude/developer/email/inbox/
```

### To Release Manager

```bash
cp claude/manager/email/sent/<message>.md claude/release-manager/email/inbox/
```

## Message Templates

### Task Assignment

**Filename:** `YYYY-MM-DD-HHMM-task-<name>.md`

```markdown
# Task Assignment: <Title>

**Date:** YYYY-MM-DD
**Project:** <project-name>
**Priority:** HIGH | MEDIUM | LOW
**Estimated Effort:** X-Y hours
**Branch:** From maintenance-9.x (or as appropriate)

## Task

<Clear description>

## Background

<Context>

## What to Do

1. Step 1
2. Step 2

## Success Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Project Directory

`active/<project-name>/`

---
**Manager**
```

### Guidance Response

**Filename:** `YYYY-MM-DD-HHMM-guidance-<topic>.md`

```markdown
# Guidance: <Topic>

**Regarding:** <reference to original question>

## Answer

<Your guidance>

## Rationale

<Why this approach>

---
**Manager**
```

## Quick Reference

| Incoming Message | Action | Archive? |
|-----------------|--------|----------|
| Complete | Move project to completed/, update indexes | Yes |
| Partial complete | Update INDEX.md status | Yes |
| Progress update | Note if significant | Yes |
| Question | Send guidance | Yes |
| Bug report | Create/update project | Yes |

## Important Rules

1. **Always archive processed emails** - Don't delete, move to inbox-archive/
2. **Update INDEX.md immediately** - Keep project status current
3. **Don't forget completed/INDEX.md** - Add completed projects there
4. **Include PR info** - Always note PR numbers in completions
