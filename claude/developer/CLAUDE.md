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

## Email System

- **Inbox:** `claude/developer/inbox/`
- **Outbox:** `claude/developer/outbox/` (drafts awaiting delivery)
- **Sent:** `claude/developer/sent/` (delivered messages)
- **Archive:** `claude/developer/inbox-archive/`

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

You communicate with:
- **Manager** - Completion reports, status updates, questions, blockers
- **Release Manager** - Build issues, hotfix needs
- **Tester** - Bug reproduction, test results (future)

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

1. Check your inbox: `ls claude/developer/inbox/`
2. Read task assignments
3. **Check lock files** before modifying code (see above)
4. Implement solutions
5. Report completion to manager
6. **Release lock files**

## Directory Structure

The developer workspace is organized into clear categories:

```
claude/developer/
├── docs/                 # Documentation and guides
│   ├── testing/          # Testing guides and results
│   ├── debugging/        # Debugging techniques and tools
│   ├── transpiler/       # Transpiler documentation
│   └── patterns/         # Code patterns and best practices
├── scripts/              # Reusable scripts
│   ├── testing/          # Test scripts
│   ├── build/            # Build helpers
│   └── analysis/         # Code analysis tools
├── investigations/       # Project-specific investigations (gitignored)
├── reports/              # Analysis reports (gitignored)
├── archive/              # Completed/old work (gitignored)
└── inbox/outbox/sent/    # Email directories
```

**Key debugging docs:** `docs/debugging/`
- USB/MSC issues, performance debugging, target splitting, GCC techniques

See `INDEX.md` for complete directory documentation.

## Build Commands

```bash
# Firmware
cd inav && ./build.sh TARGETNAME

# Configurator
cd inav-configurator && npm install && npm start

# Tests
cd inav-configurator && npm test
```
