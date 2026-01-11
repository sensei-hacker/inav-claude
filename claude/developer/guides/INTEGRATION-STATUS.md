# Critical Checklist Integration Status

This document tracks which agents and skills have been integrated with the critical checklists.

## ✅ Completed Integrations

### Agents

| Agent | Checklist Reference | Status | Location |
|-------|---------------------|--------|----------|
| **test-engineer** | `CRITICAL-BEFORE-TEST.md` | ✅ Complete | `.claude/agents/test-engineer.md:11-23` |

### Skills

| Skill | Checklist Reference | Status | Location |
|-------|---------------------|--------|----------|
| **start-task** | `CRITICAL-BEFORE-CODE.md` | ✅ Complete | `.claude/skills/start-task/SKILL.md:15-25` |
| **git-workflow** | `CRITICAL-BEFORE-COMMIT.md` | ✅ Complete | `.claude/skills/git-workflow/SKILL.md:17-28` |
| **create-pr** | `CRITICAL-BEFORE-PR.md` | ✅ Complete | `.claude/skills/create-pr/SKILL.md:15-26` |

## 📋 Critical Checklists Created

All 4 critical checklists are created in `claude/developer/guides/`:

1. **CRITICAL-BEFORE-CODE.md** (59 lines)
   - Lock file checking
   - Lock acquisition
   - Branch creation
   - Agent usage requirements
   - Use inav-architecture before searching

2. **CRITICAL-BEFORE-COMMIT.md** (66 lines)
   - Never use `git add -A`
   - Human review of commit messages
   - No Claude/AI mentions
   - HEREDOC format for messages
   - Amend rules
   - Never skip hooks

3. **CRITICAL-BEFORE-PR.md** (102 lines)
   - Testing is MANDATORY
   - 5 required testing steps
   - PR creation checklist
   - Bot checking (wait 3 minutes)
   - PR description requirements

4. **CRITICAL-BEFORE-TEST.md** (97 lines)
   - Test-first approach (reproduce bug → fix → verify)
   - Testing requirements by project
   - Never assume tests are broken
   - Test organization
   - Agent usage

## How It Works

**Context-Sensitive Delivery:**
- Checklists are read **exactly when needed**, not upfront
- Each checklist is short (59-102 lines), focused, and memorable
- Agents and skills read them automatically via Read tool
- Developer reads them manually when starting tasks

**Example Flow:**

```
1. User assigns task
   ↓
2. Developer reads CRITICAL-BEFORE-CODE.md
   ↓
3. Developer uses /start-task (reads same checklist internally)
   ↓
4. Developer implements code
   ↓
5. Developer uses test-engineer agent (reads CRITICAL-BEFORE-TEST.md)
   ↓
6. Developer uses /git-workflow to commit (reads CRITICAL-BEFORE-COMMIT.md)
   ↓
7. Developer uses /create-pr (reads CRITICAL-BEFORE-PR.md)
   ↓
8. Developer waits 3 minutes, checks bots
```

## Benefits Achieved

**Problem Solved:**
- Old: 840-line README overwhelms, critical rules forgotten
- New: 59-102 line checklists delivered exactly when needed

**Advantages:**
- ✅ No cognitive overload
- ✅ Critical info at right moment
- ✅ Short, focused, memorable
- ✅ Automatically enforced by agents/skills
- ✅ Easy to update and maintain

## ✅ Step 2 Complete: README Streamlined

**Original README:** 840 lines
**Streamlined README:** 235 lines
**Reduction:** 73% (605 lines removed)

**What was kept in README.md:**
- Quick Start
- Responsibilities
- Communication/email system
- 12-step workflow table
- Critical checklist references (prominent at top)
- Repository overview (brief)
- Essential agents (brief list)
- Essential skills (brief list)
- Quick commands
- Completion report template
- Summary

**What was removed/moved:**
- ✂️ Detailed workflow steps (now in critical checklists)
- ✂️ Testing requirements (→ `CRITICAL-BEFORE-PR.md`)
- ✂️ Git best practices (→ `CRITICAL-BEFORE-COMMIT.md`)
- ✂️ Lock file procedures (→ `CRITICAL-BEFORE-CODE.md`)
- ✂️ Build details (use agents, brief reference only)
- ✂️ Firmware architecture details (use inav-architecture agent)
- ✂️ Detailed coding standards (→ will move to `guides/coding-standards.md` in Step 3)
- ✂️ Detailed agent descriptions (→ `.claude/agents/*.md`)
- ✂️ Testing philosophy (→ `CRITICAL-BEFORE-TEST.md`)

**Backup saved:** `README-ORIGINAL-840lines.md`

---

## ✅ Step 3 Complete: Detailed Content Moved to Guides

**New guide files created:**

1. **`guides/coding-standards.md`** (148 lines)
   - Code organization & structure
   - Code quality guidelines
   - Comment best practices (WHY not WHAT)
   - Testing theories
   - Avoiding over-engineering
   - INAV-specific guidelines

2. **`guides/git-workflow.md`** (299 lines)
   - Detailed git commit practices
   - Amend rules and verification
   - Branch management
   - PR best practices
   - Force push rules and dangers
   - Working directory safety

3. **`guides/debugging-guide.md`** (127 lines)
   - Serial printf debugging (with `/mwptools` reference)
   - Chrome DevTools MCP (with `/test-configurator` reference)
   - GDB for SITL debugging
   - When to use each tool
   - General debugging approach
   - References to relevant agents/skills

**Updates to critical checklists:**

1. **`CRITICAL-BEFORE-CODE.md`**
   - Added section #6: Debugging Tools Available
   - References `debugging-guide.md` for details

2. **`CRITICAL-BEFORE-COMMIT.md`**
   - Added section #7: Run Linter (if applicable)
   - Covers clang-tidy, eslint, shellcheck

**Total guide files now:** 9 files
- 4 critical checklists (context-sensitive)
- 3 detailed guides (reference material)
- 1 README (overview)
- 1 INTEGRATION-STATUS (tracking)

---

## Summary of Complete System

**Context-Sensitive Checklists** (read at specific moments):
- `CRITICAL-BEFORE-CODE.md` - Before modifying code
- `CRITICAL-BEFORE-COMMIT.md` - Before git commit
- `CRITICAL-BEFORE-PR.md` - Before creating PR
- `CRITICAL-BEFORE-TEST.md` - During testing

**Reference Guides** (consulted when needed):
- `coding-standards.md` - Code quality and organization
- `git-workflow.md` - Detailed git practices
- `debugging-guide.md` - Debugging tools and techniques

**All guides reference existing tools/skills:**
- `/mwptools` for CLI access
- `/test-configurator` for configurator debugging
- `inav-architecture` agent for finding code
- `inav-builder` agent for builds
- `sitl-operator` agent for SITL management
- `test-engineer` agent for testing
- `msp-expert` agent for MSP work

---

## Next Steps

**Pending:**
- [ ] Test the integration with an actual task
- [ ] Verify all cross-references work correctly

**Future Enhancements:**
- Consider adding pre-hooks that automatically read checklists
- Add completion verification to skills (did you check the bot comments?)
- Create quick-reference card (1-page summary)
- Consider `debugging-guide.md` expansion as more debugging info accumulates
