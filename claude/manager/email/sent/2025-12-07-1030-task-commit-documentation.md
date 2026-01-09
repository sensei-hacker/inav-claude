# Task Assignment: Commit Internal Documentation Updates

**Date:** 2025-12-07 10:30
**Project:** commit-internal-documentation-updates
**Priority:** MEDIUM
**Estimated Effort:** 30-60 minutes
**Branch:** master

## Task

Review, stage, commit, and push all accumulated updates to internal Claude workspace documentation, skills, test scripts, and tooling.

## Background

The git repository has many uncommitted changes to internal documentation:
- **Modified:** 25 files (skills, role docs, project tracking)
- **Untracked:** 50+ files (research docs, test tools, new skills)

These represent valuable work from recent projects:
- INAV 9.0.0-RC3 release documentation
- CRSF telemetry PR analysis
- PrivacyLRS research and security findings
- New test tools and automation scripts
- Updated skill definitions and role guides

This documentation should be committed to preserve the work and make it available for future reference.

## What to Do

### 1. Review All Changes

**Check what's modified:**
```bash
git status
git diff --stat
git diff .claude/ claude/
```

**Key areas to review:**
- `.claude/skills/*/SKILL.md` - Skill definitions
- `claude/*/README.md` - Role documentation
- `claude/projects/INDEX.md` - Project tracking (updated today!)
- Research documents in `claude/developer/`, `claude/release-manager/`, `claude/security-analyst/`
- Test tools in `claude/test_tools/` and `claude/developer/test_tools/`

**Check for sensitive information:**
- No API keys, tokens, or passwords
- No absolute paths with usernames (if unavoidable, verify they're generic)
- No private repository credentials

### 2. Stage Files for Commit

**Stage by category:**

```bash
# Skills
git add .claude/skills/

# Role documentation
git add claude/developer/README.md claude/developer/CLAUDE.md
git add claude/manager/README.md
git add claude/release-manager/README.md claude/release-manager/download_guide.md
git add claude/security-analyst/README.md claude/security-analyst/CLAUDE.md

# Project tracking
git add claude/projects/INDEX.md
git add claude/projects/coordinate-crsf-telemetry-pr-merge/

# Research and analysis
git add claude/developer/*.md
git add claude/release-manager/*.md
git add claude/release-manager/*.sh
git add claude/security-analyst/*.md

# Test tools
git add claude/test_tools/
git add claude/developer/test_tools/
```

**Review staged files:**
```bash
git status
git diff --cached --stat
```

### 3. Exclude Certain Files

**DO NOT commit:**
- Submodules: `PrivacyLRS/`, `inav/`, `inav-configurator/`, `uNAVlib/`, `*-blackbox-log-viewer/`
- Temporary test files at root (evaluate if valuable):
  - `serial_printf_debugging.md`
  - `test_align_mag.py`
  - `test_cli_mag.sh`
- System errors: `"c -l|"` (appears to be filesystem error)

**If root-level test files are valuable:**
- Consider moving to `claude/test_tools/` or `claude/developer/test_tools/`
- Then commit from new location

### 4. Create Commit

**Commit message format:**
```
Docs: Update internal documentation and tooling

Updates to Claude workspace documentation, skills, and research:

Skills:
- Update 16 skill definitions with latest procedures
- Add new skills: create-pr, privacylrs-test-runner, test-crsf-sitl,
  test-privacylrs-hardware

Role Documentation:
- Update developer, manager, release-manager, security-analyst guides
- Add CRSF telemetry testing procedures
- Add RC3 release documentation

Project Tracking:
- Update INDEX.md with recent activity (RC3 release, Issue #2453, etc.)
- Add coordinate-crsf-telemetry-pr-merge project

Research & Analysis:
- CRSF telemetry PR analysis and testing status
- SITL websocket feasibility research
- PrivacyLRS Finding #5 investigation documents
- RC3 release planning and checklists

Test Tools:
- Add CRSF telemetry test scripts
- Add release manager automation tools (find-incompatible-settings.sh,
  verify-dmg-contents.sh, rename-firmware-for-release.sh)
- Add CRSF frame analysis tools

All changes are internal documentation and tooling only, no source code
changes included.
```

**Create the commit:**
```bash
git commit -m "$(cat <<'EOF'
[paste commit message above]
EOF
)"
```

### 5. Push to Repository

```bash
git push origin master
```

**Verify:**
```bash
git log --oneline -1
git status
```

### 6. Report Completion

Send completion report to Manager:
- Filename: `claude/developer/sent/2025-12-07-HHMM-documentation-commit-complete.md`
- Include: Number of files committed, commit hash, any excluded files

## Success Criteria

- [ ] All modified skills committed
- [ ] All modified role documentation committed
- [ ] Updated INDEX.md committed
- [ ] New project directory committed
- [ ] Research documents committed
- [ ] Test tools and scripts committed
- [ ] No sensitive information committed
- [ ] No submodules committed
- [ ] Meaningful commit message created
- [ ] Changes pushed successfully
- [ ] Completion report sent to Manager

## Notes

**Alternative Approach:**
You could create multiple smaller commits by category if you prefer:
1. Skills updates
2. Role documentation
3. Project tracking
4. Research documents
5. Test tools

However, a single comprehensive commit is acceptable for internal documentation updates.

**Files to Evaluate:**
- Root-level test files (`test_*.py`, `test_*.sh`) - Move to appropriate location before committing
- `serial_printf_debugging.md` - Keep or delete based on value
- `"c -l|"` - This appears to be an error, should probably be deleted

**Important:**
This is ONLY internal documentation and tooling. No source code changes should be included in this commit.

---
**Manager**
