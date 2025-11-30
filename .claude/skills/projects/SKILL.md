---
description: View and manage project status from INDEX.md
triggers:
  - check projects
  - project status
  - list projects
  - active projects
  - show projects
  - what projects
---

# Project Status Skill

View and manage INAV project tracking.

## Project Index Location

`claude/projects/INDEX.md`

## Quick Commands

### View All Active Projects

```bash
grep -A 20 "^## Active Projects" claude/projects/INDEX.md
```

### View Project Statistics

```bash
grep -A 6 "^## Project Summary Statistics" claude/projects/INDEX.md
```

### View Projects by Status

```bash
# Active/In Progress
grep "🚧" claude/projects/INDEX.md

# Backburner
grep "⏸️" claude/projects/INDEX.md

# Completed
grep "✅" claude/projects/INDEX.md
```

### View Specific Project

Read the project's summary.md:
```bash
cat claude/projects/{project-name}/summary.md
```

### View Project Todo

```bash
cat claude/projects/{project-name}/todo.md
```

## Project Locations

- **Active projects:** `claude/projects/{name}/`
- **Archived projects:** `claude/archived_projects/{name}/`
- **Master index:** `claude/projects/INDEX.md`

## Status Definitions

| Status | Emoji | Meaning |
|--------|-------|---------|
| TODO | 📋 | Defined but not started |
| IN PROGRESS | 🚧 | Actively being worked on |
| COMPLETED | ✅ | Finished and merged |
| BACKBURNER | ⏸️ | Paused, will resume later |
| CANCELLED | ❌ | Abandoned |

## Assignment Status

| Indicator | Meaning |
|-----------|---------|
| ✉️ Assigned | Developer notified via email |
| 📝 Planned | Created but not yet assigned |
| 🔧 Developer-initiated | Created by developer |

## For Managers Only

When updating projects:
1. Update the project entry in INDEX.md
2. Update statistics section
3. Update Quick Reference sections (By Status, By Assignment, By Priority, By Type)
4. Update the "Last Updated" date at top
