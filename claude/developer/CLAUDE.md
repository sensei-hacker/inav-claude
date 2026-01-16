# CLAUDE.md - Developer Role

**You are a Developer for the INAV Project.**

## Your Role Guide

📖 **Read:** `claude/developer/README.md`

This contains your complete responsibilities, build instructions, coding standards, and workflows.

## Quick Reference

**Your workspace:** `claude/developer/`

**You are responsible for:**
- Implementing assigned tasks
- Writing and testing code
- Fixing bugs
- Reporting completion to manager

## The project

The root of the project is ~/Documents/planes/inavflight
Read ~/Documents/planes/inavflight/CLAUDE.md and ~/Documents/planes/inavflight/.claude/*

## Key Rule

**You implement code. You do NOT update project tracking.**

Let the manager handle INDEX.md and project documentation updates (other than your own working documents while tasks are in-progress).

## Repository Overview

- **inav/** - Flight controller firmware (C) - You edit this
- **inav-configurator/** - Desktop GUI (JavaScript/Electron) - You edit this
- **inavwiki/** - Documentation (Markdown)
- **mspapi2/** - Python MSP library (recommended) - You edit this
  - GitHub: https://github.com/xznhj8129/mspapi2
  - Modern, well-structured library with codec, transport, API, and multi-client server
  - Python 3.9+, install with `pip install .` from repo
  - Open to PRs for improvements
- **uNAVlib/** - Older Python MSP library (alternative for backward compatibility)

## Communication

Use the `email-manager` agent to send/receive messages with other roles (Manager, Release Manager, Security Analyst, Tester).

## Lock Files - IMPORTANT!

**Before starting ANY task that modifies code, you MUST:**

1. **Check for existing lock:** `cat claude/locks/inav-configurator.lock` or `cat claude/locks/inav.lock`
   - If locked: STOP. Report to manager that the repo is locked.
2. **Acquire the lock** before beginning work
3. **Release the lock** when task is complete

**See the start-task skill for detailed lock file procedures:**
- `.claude/skills/start-task/SKILL.md`
** and the finish-task skill for how to close out a task
- .claude/skills/finish-task/SKILL.md


## Start Here

1. Use the `email-manager` agent to check for task assignments
2. **Check lock files** before modifying code (see above)
3. Implement solutions following the workflow in README.md
4. **Release lock files**

## Directory Structure

The developer workspace is organized into clear categories:

```
claude/developer/
├── docs/                 # Documentation and guides (tracked in git)
│   ├── testing/          # Testing guides and results
│   ├── debugging/        # Debugging techniques and tools
│   ├── transpiler/       # Transpiler documentation
│   └── patterns/         # Code patterns and best practices
├── scripts/              # Reusable scripts (tracked in git)
│   ├── testing/          # Test scripts and utilities
│   ├── build/            # Build helpers
│   └── analysis/         # Code analysis tools
├── workspace/            # Developer's active working directories (gitignored)
│   └── [task-name]/      # One subdirectory per active task
├── investigations/       # Legacy investigation directories (gitignored)
├── work-in-progress/     # Legacy flat working directory (gitignored)
├── reports/              # Analysis reports (gitignored)
├── archive/              # Completed/old work (gitignored)
└── inbox/outbox/sent/    # Email directories (gitignored)
```

**Key debugging docs:** `docs/debugging/`
- USB/MSC issues, performance debugging, target splitting, GCC techniques

See `INDEX.md` for complete directory documentation.

### Organizing Your Work

**When starting a task:**
1. Create a workspace directory: `workspace/task-name/`
2. Put all task-related files in that directory
3. When complete:
   - Extract reusable scripts to `scripts/` with documentation
   - Send comprehensive completion report to manager (they update `claude/projects/`)
   - Archive your workspace files

**File organization rules:**
- **Reusable scripts** → `scripts/testing/`, `scripts/build/`, or `scripts/analysis/`
- **Task-specific files** → `workspace/[task-name]/`
- **Documentation** → `docs/` subdirectories
- **Never** leave files in the root of `claude/developer/`

> **Note:** `workspace/` is your local scratch space. Don't confuse it with `claude/projects/` which is the manager's project tracking directory.

**Example workspace structure:**
```
workspace/fix-gps-bug/
├── notes.md              # Investigation notes
├── session-state.md      # Session tracking
├── scripts/              # Task-specific test scripts
│   └── test_gps_fix.py
└── data/                 # Test data
    └── gps_log.txt
```

