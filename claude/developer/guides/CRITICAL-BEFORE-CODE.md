# ⚠️ CRITICAL CHECKLIST - Read Before Modifying Any Code

> **Workflow:** steps 3, 4, 6 of 17 → `WORKFLOW.md`.

**STOP! Complete this checklist before making ANY code changes:**

**Use a task list tool to track each step as you complete it.**

## 0. Read Coding Standards

**Read `claude/developer/guides/coding-standards.md` before writing any code.**
General instinct ("explain why, not what") isn't enough on its own — this repo
has specific rules beyond that default, including: never write
discovery-narrative comments or docs ("used to be X", "this used to fail
because Y") — describe only the current state and current rationale; history
belongs in the commit message, not the code or guide text.
Comments are for the rare case where the code itself would be confusing — keep them short and skip them entirely when the code is already clear.

## 1. Acquire a Lock

**This applies before ANY `git checkout`/`switch` or build in any of the
firmware checkouts or `inav-configurator/` — including read-only
investigation or build-comparison tasks that never intend to commit.**
Checking out a branch mutates the shared working tree regardless of whether
you plan to write code; a lock check gated only on "am I about to commit"
arrives too late.

**Use `claude/locks/lock_manager.py` to check and acquire — do not read or
write lock files by hand:**

```bash
REPO=$(python3 claude/locks/lock_manager.py acquire --task <task-name> --branch <branch-name> --type firmware)
```

Pass `--type configurator` for `inav-configurator/` work. On success it
prints the checkout to use (e.g. `inav2`) — that's up to three parallel
firmware checkouts (`inav/`, `inav2/`, `inav3/`), separate working trees
where a lock on one does not block another. On failure it exits non-zero
and explains why every candidate was skipped (locked by another session, or
unexpectedly dirty). **STOP and report to the manager rather than forcing an
acquisition** — do not hand-write a lock file or proceed into a locked or
dirty directory.

See `claude/locks/README.md` for the full design: lock file format, the
dirty-checkout sanity check the script runs automatically before handing out
an unlocked checkout, and what to do if a candidate turns out to be dirty or
a lock looks stale.

**Remember:**
- Hold the lock through the whole push lifecycle (including follow-up fixes); re-acquire before any post-release push.
- Use the real session id (`--session "$DSH_SESSION_ID"` where `$CLAUDE_CODE_SESSION_ID` is absent), never a placeholder.
- Preserve deliverables and remove scratch dirs *before* releasing — a released checkout is someone else's from that moment.
- Adding a parallel checkout dir touches more than `lock_manager.py` (hooks, `new-branch.sh`, permissions yaml, README) — grep the tree for the sibling name.
- Tell subagents the exact safe path when a lock is held elsewhere — they don't inherit your lock discipline.

## 2. Create Git Branch
The branch MUST be created off of the correct version branch — never off master.

```bash
claude/developer/scripts/git/new-branch.sh <repo> <bugfix|feature|breaking> <branch-name>
```

See `.claude/skills/git-workflow/SKILL.md` ("Creating Branches") for the current
base-branch decision table (including any active temporary override) and the manual
fallback if the script can't be used.

**Remember:**
- Confirm you're on the correct branch before working — a lock-handed-out checkout may sit on a prior task's branch.
- Peek at another ref with `git show <ref>:<path>` (read-only); `git checkout <other-ref> -- .` silently reverts local commits ahead of that ref.
- Harness-only tasks (`.claude/`, `claude/`) commit straight to `master` — branches belong in the project repos.
- The base-branch table above is the single authority, even when a task email says otherwise.

## 3. Plan End-User Documentation (If Needed)

**Evaluate if your planned change needs end-user documentation:**

- ✅ **New features** → Draft documentation NOW (before coding)
- ✅ **Behavior changes** → Draft documentation NOW
- ℹ️ **Bug fixes** → Generally no docs needed
- ℹ️ **New targets** → Generally no docs needed
- ℹ️ **Refactoring** → Only if user-facing behavior changes

**If documentation is needed:**

1. **Draft the user documentation NOW** (before implementing)
   - Write it in `claude/developer/workspace/[task-name]/draft-user-docs.md`
   - Describe the feature from the user's perspective
   - Include examples, configuration steps, and any CLI/settings changes

2. **Use this as a design review:**
   - **If the draft docs are complex** → Feature design may be too complex
   - **If hard to explain clearly** → User experience needs simplification
   - **If requires many steps** → Consider streamlining the workflow

3. **This draft will be updated later:**
   - After implementation, update the draft to match actual behavior
   - Then add to `inav/docs/` and/or `inavwiki/` before PR

## 4. Check for Specialized Agents

**Before starting implementation, check if specialized agents apply:**

| Task involves... | Use this agent FIRST |
|------------------|----------------------|
| MSP protocol work | **msp-expert** - Message formats, mspapi2 usage |
| Settings/CLI parameters | **settings-lookup** - Setting names, defaults, valid values |
| Finding firmware code | **inav-architecture** - Locates subsystems before Grep |
| Target configuration issues | **target-developer** - Flash overflow, DMA conflicts, gyro detection, pin mapping |
| SITL operations | **sitl-operator** - Start/stop/configure SITL |
| Building firmware/configurator | **inav-builder** - ALL builds (never cmake/make/npm directly) |
| Testing/validation | **test-engineer** - Reproduce bugs, run tests |

**Pattern matching:**
- Task mentions "MSP" → use **msp-expert**
- Task mentions "setting" or CLI → use **settings-lookup**
- Need to find code location → use **inav-architecture**
- Task mentions "target", "flash overflow", "DMA conflict", "gyro detection" → use **target-developer**
- Need to build anything → use **inav-builder**

## 5. Use Agents - NEVER Direct Commands

**❌ NEVER:**
- `cmake ..`
- `make TARGETNAME`
- `npm start` (for builds)
- Direct Grep on `inav/src/` without agent guidance

**✅ ALWAYS:**
- Use `inav-builder` agent for ALL builds
- Use `test-engineer` agent for ALL testing
- Use `inav-architecture` agent BEFORE searching firmware code

**Remember:**
- Use `fc-flasher` for hardware flashing, never `dfu-util` directly (STM32H7 fails DFU exit).
- Tell a lookup agent the exact checkout path when multiple worktrees coexist.
- `git status`/`git log -- <path>` before "extending" a named script — it may already be done, uncommitted.
- Tell fresh subagents explicitly to skip CLAUDE.md's role-selection question.

## 6. Before Searching Firmware Code

**❌ NEVER:** Start with `Grep` or `Explore` on `inav/src/`

**✅ ALWAYS:** Ask `inav-architecture` agent first:
```
"Where is [functionality I need to find]?"
```

The agent will tell you exactly which files/directories to look at. THEN use Grep/Read on those specific locations.

## 7. Debugging Tools Available

When investigating bugs or understanding code behavior:

1. **Serial printf debugging** - Use DEBUG macros in firmware code (via `/mwptools` for CLI)
2. **Chrome DevTools MCP** - For configurator debugging (via `/test-configurator`)
3. **GDB** - For SITL debugging (`gdb inav/build_sitl/bin/SITL.elf`)

See `guides/debugging-guide.md` for detailed usage instructions.

---

**Once this checklist is complete, proceed with your task.**

---

## 8. When committing code
1. *Do NOT mention Claude in commit messages* - Do NOT put "Co-Authored-By: Claude Sonnet 4.6" or similar in a commit message
2. *Read claude/developer/guides/CRITICAL-BEFORE-COMMIT.md*

## Self-Improvement: Lessons

Add concise, actionable one-liners (see `guides/README.md` Capture Rubric). State the
rule, not the story.

- **Fix blockers, don't route around them**: if a build fails on an unrelated error, fix that error rather than simulating the linker.
- **Check for an existing upstream fix first**: `gh pr list`/web-search before implementing from a plan — cherry-pick a better existing fix rather than re-deriving it.
- **Fixing on a lower branch? Check the higher branch for the same pattern**: `git show upstream/<higher>:<path>`; flag the backport in the completion report.
- **Security-critical code: fewer knobs, shorter functions** — don't add a knob/parameter unless something concrete needs it.
- **"Live in production" ≠ authorize importing as-is**: evaluate every hunk; flag credentials, no-op auth checks, or always-success endpoints for explicit confirmation.
- **Verify bot review comments by tracing the code, don't dismiss them** — they're often real, non-obvious bugs.
- **Verify a doc's "no callers" claim yourself** — a disabled call site still changes remove-vs-implement.
- **A diagnosis naming one call site may miss a sibling** — grep the file for other reads of the same data before assuming the fix is complete.
- **`git diff <a> <b> --stat` is the wrong measure for PR retargeting**: use `git log <target>..<branch>` or merge-base — a two-tree diff includes unrelated history.
- **Build test state via real functions, not hand-fabricated memory** — a test pinned to today's implementation is no better than hashing the file.
- **"Verify PR N" means test and report on N, not re-implement its diff as your own PR** — review, test, and comment instead.

<!-- Add new lessons above this line -->
