# Task Assignment: Fix Skills Directory Structure

**Date:** 2025-11-29 11:15
**Priority:** Low
**Estimated Effort:** 10 minutes

## Task

Fix the `.claude/skills/` directory structure so Claude Code recognizes the skills.

## Background

Claude Code has two mechanisms:
- **Commands** (`.claude/commands/foo.md`) - Human-invoked via `/foo`
- **Skills** (`.claude/skills/foo/SKILL.md`) - Claude uses automatically when relevant

The current skills are flat `.md` files, but they need to be **directories** containing `SKILL.md`.

## Current (Wrong) Structure

```
.claude/skills/
  ├── build-sitl.md
  ├── sitl-arm.md
  ├── email.md
  ├── projects.md
  └── communication.md
```

## Required (Correct) Structure

```
.claude/skills/
  ├── build-sitl/
  │   └── SKILL.md
  ├── sitl-arm/
  │   └── SKILL.md
  ├── email/
  │   └── SKILL.md
  ├── projects/
  │   └── SKILL.md
  └── communication/
      └── SKILL.md
```

## What to Do

For each skill file:
```bash
cd .claude/skills

# For each .md file, create directory and rename
for f in *.md; do
  name="${f%.md}"
  mkdir -p "$name"
  mv "$f" "$name/SKILL.md"
done
```

## Success Criteria

- [ ] Each skill is in its own directory
- [ ] Each skill file is named `SKILL.md`
- [ ] Claude recognizes and uses the skills automatically

---
**Manager**
