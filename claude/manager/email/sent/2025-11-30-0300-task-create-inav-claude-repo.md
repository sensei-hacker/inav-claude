# Task: Create inav-claude Repository

**Date:** 2025-11-30
**To:** Developer
**From:** Manager
**Priority:** Medium
**Type:** Repository Setup / Documentation

---

## Objective

Create a new public repository `inav-claude` under https://github.com/sensei-hacker and upload the Claude workflow infrastructure files.

---

## Repository Details

- **GitHub Account:** sensei-hacker
- **Repository Name:** inav-claude
- **Visibility:** Public (or as preferred)
- **Description:** "Claude Code workflow infrastructure for INAV development"

---

## Files to Include

### From `claude/` directory:
- `README.md`
- `COMMUNICATION.md`
- `INDEXING.md`
- `manager/README.md`
- `manager/CLAUDE.md`
- `developer/README.md`
- `developer/CLAUDE.md`
- `developer/test_tools/` - All test scripts (important testing utilities)
- `developer/test_tools/UNAVLIB.md`
- `release-manager/README.md`
- `release-manager/download_guide.md`
- `projects/INDEX.md`
- `archived_projects/` - All project summaries and documentation (todo.md, summary.md, etc.)
- `locks/README.md`

### From root `inavflight/` directory:
- `CLAUDE.md` (the main role-selection file)
- `.claude/settings.local.json`
- `.claude/skills/` - All skill files (build-sitl, communication, email, finish-task, projects, sitl-arm, start-task)

### From role subdirectories:
- `developer/.claude/settings.local.json`
- `manager/.claude/settings.local.json`

---

## Files to EXCLUDE

1. **Downloads:** `*/downloads/*` (binary firmware .hex files)
2. **Email content:** All files in:
   - `*/inbox/*`
   - `*/outbox/*`
   - `*/sent/*`
   - `*/inbox-archive/*`
   - `*/completed/*`
3. **Log files:** `*.log`
4. **Temp/work files:**
   - `*.pyc`, `__pycache__/`
   - Work-in-progress investigation notes (e.g., `work_in_progress/*.md`, `work-in-progress/*.md`)
5. **Session-specific files:**
   - `developer/distance_to_home_zero_conditions.md`
   - `developer/gps_test_investigation_notes.md`
   - `developer/script_versions.txt`
   - `developer/extract_json.py`
   - `developer/MSPy.log`

---

## IMPORTANT Security Notes

1. **NO SECRETS:** Do NOT commit any:
   - API keys
   - Passwords
   - Authentication tokens
   - Private credentials
   - `.env` files with secrets

2. **NO FULL PATHS:** Before committing, sanitize all files to remove full paths like `/home/raymorris/...`. Replace with relative paths like:
   - `claude/` instead of `claude/`
   - `inav/` instead of `inav/`
   - Use `$PROJECT_ROOT` or similar placeholder if absolute reference needed

3. **Review each file** before committing to ensure no personal information is exposed.

---

## Suggested Directory Structure for Repo

```
inav-claude/
├── README.md                    # Main overview (from claude/README.md)
├── CLAUDE.md              # Role selection file (from root)
├── COMMUNICATION.md
├── INDEXING.md
├── .claude/
│   ├── settings.local.json
│   └── skills/
│       ├── build-sitl/SKILL.md
│       ├── communication/SKILL.md
│       ├── email/SKILL.md
│       ├── finish-task/SKILL.md
│       ├── projects/SKILL.md
│       ├── sitl-arm/SKILL.md
│       └── start-task/SKILL.md
├── manager/
│   ├── README.md
│   ├── CLAUDE.md
│   └── .claude/settings.local.json
├── developer/
│   ├── README.md
│   ├── CLAUDE.md
│   ├── .claude/settings.local.json
│   └── test_tools/
│       ├── UNAVLIB.md
│       ├── gps_recovery_test.py
│       ├── gps_rth_bug_test.py
│       ├── gps_rth_test.py
│       ├── gps_test_v*.py
│       ├── msp_debug.py
│       ├── msp_rc_debug.py
│       ├── sitl_arm_test.py
│       └── unavlib_bug_test.py
├── release-manager/
│   ├── README.md
│   └── download_guide.md
├── projects/
│   └── INDEX.md
├── archived_projects/
│   └── [project summaries...]
└── locks/
    └── README.md
```

---

## Steps

1. Create the repository on GitHub
2. Clone locally
3. Copy files according to include/exclude lists above
4. **Sanitize all paths** - remove `/home/raymorris/...` references
5. **Check for secrets** - grep for API keys, passwords, tokens
6. Review and organize directory structure
7. Create initial commit
8. Push to GitHub
9. Report back with repository URL

---

## Deliverable

Report back with:
- Repository URL
- List of files included
- Any issues encountered
- Confirmation that paths were sanitized and no secrets included

---

*Task assigned by Manager*
