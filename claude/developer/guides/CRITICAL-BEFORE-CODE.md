# ⚠️ CRITICAL CHECKLIST - Read Before Modifying Any Code

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

## 3. Create Git Branch
The branch MUST be created off of the correct version branch — never off master.

```bash
claude/developer/scripts/git/new-branch.sh <repo> <bugfix|feature|breaking> <branch-name>
```

See `.claude/skills/git-workflow/SKILL.md` ("Creating Branches") for the current
base-branch decision table (including any active temporary override) and the manual
fallback if the script can't be used.

## 4. Plan End-User Documentation (If Needed)

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

## 5. Check for Specialized Agents

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

## 6. Before Searching Firmware Code

**❌ NEVER:** Start with `Grep` or `Explore` on `inav/src/`

**✅ ALWAYS:** Ask `inav-architecture` agent first:
```
"Where is [functionality I need to find]?"
```

The agent will tell you exactly which files/directories to look at. THEN use Grep/Read on those specific locations.

## 6. Debugging Tools Available

When investigating bugs or understanding code behavior:

1. **Serial printf debugging** - Use DEBUG macros in firmware code (via `/mwptools` for CLI)
2. **Chrome DevTools MCP** - For configurator debugging (via `/test-configurator`)
3. **GDB** - For SITL debugging (`gdb inav/build_sitl/bin/SITL.elf`)

See `guides/debugging-guide.md` for detailed usage instructions.

---

**Once this checklist is complete, proceed with your task.**

---

## 7. When committing code
1. *Do NOT mention Claude in commit messages* - Do NOT put "Co-Authored-By: Claude Sonnet 4.6" or similar in a commit message
2. *Read claude/developer/guides/CRITICAL-BEFORE-COMMIT.md*

## Self-Improvement: Lessons Learned

When you discover something important about PRE-CODING SETUP that will likely help in future sessions, add it to this section. Only add insights that are:
- **Reusable** - will apply to future pre-coding setup, not one-off situations
- **About setup/preparation** - lock files, branches, agent usage, search strategy
- **Concise** - one line per lesson

Use the Edit tool to append new entries. Format: `- **Brief title**: One-sentence insight`

### Lessons

#### Locks & Checkouts

- **Hold the lock for the whole life of any push, including a follow-up fix after the task's own completion report already went out**: releasing the lock and later pushing "just one more commit" to the same branch defeats the lock's entire purpose (preventing uncoordinated concurrent writes to a shared checkout) even if no other agent happened to grab it in between. If more work on a branch turns up after you've released its lock, re-acquire the lock first, push, then release again — don't push through an unlocked checkout.
- **Use a real session id in lock files, never a placeholder string**: writing something like `SESSION_ID: developer-session` instead of the actual `$CLAUDE_CODE_SESSION_ID` causes the "is this repo locked by a different session" hook check to false-positive on every subsequent command touching that repo, generating a spurious approval prompt each time — fix immediately with `Edit` if caught after the fact, since the friction compounds across the session. In harnesses without that env var (e.g. DSH), pass the real identifier explicitly instead: `lock_manager.py acquire --session "$DSH_SESSION_ID"`.
- **A released lock can be re-acquired within seconds — preserve deliverables and remove your scratch *while you still hold it***: after releasing inav2.lock, another session immediately acquired inav2 and staged 1,951 files for its own merge work; any post-release git operation on that checkout would have stepped on their in-flight state. Copy artifacts out of the checkout and `rm -rf` your `build-*` scratch dirs *before* `release`, and treat a released checkout as someone else's from that moment on.
- **Adding a new parallel checkout directory (e.g. `inav-configurator2`) touches more than `lock_manager.py`**: it must also be added to `.claude/hooks/deterministic_checks.py`'s `_LOCKABLE_REPOS`, `claude/developer/scripts/git/new-branch.sh` (repo validation list + `DECISION_REPO` mapping), `.claude/hooks/tool_permissions_bash.yaml`'s branch-creation-blocking rule (both the `cd`-detection and cwd-detection regexes — a name like `inav-configurator2` won't match a `(inav-configurator)(/|$)` pattern since `2` isn't `/` or end-of-string), and `claude/locks/README.md`. Grep the whole `.claude/` and `claude/locks/` tree for the sibling repo's name (e.g. `inav2`) when adding a new one — don't rely on the one file whose comment says "keep in sync," it's not the only place that needs it.
- **Subagents don't inherit your lock discipline — tell them the safe path explicitly**: an `inav-code-review` run, asked only to review a diff file, went looking for surrounding source context on its own and created a `git worktree`/added a remote directly inside `inav/` while it was locked by a different session's task. No harm resulted (worktree adds are additive; the other session's checked-out branch was untouched), but it was luck, not design. When delegating any agent that might read repo state beyond a supplied diff/file path while a repo lock is held by another session, explicitly tell it which repo/path is safe to touch (e.g. a second clone like `inav2/`) — don't assume it will infer the lock exists or avoid the locked one.

#### Branches & Task State

- **Be sure you are on the correct branch before starting work**: a lock-handed-out checkout was already sitting on a branch from a prior, unrelated task (`fix-configurator-ci-macos-arm64-oom`), which turned out to have its own open PR (#2706) for a different fix. A commit went onto it before checking — caught before pushing (`gh pr list --head <branch>` would have caught it sooner), but a checked-out branch being handed to you doesn't mean it's the right one for this task.
- **`git checkout <other-ref> -- .` on a branch with local commits ahead of that ref silently reverts them in the index/working tree**: used to compare current file content against another ref (e.g. "does this bug pre-exist on upstream/X?") while staying on your working branch, it stages a full reversion of everything your branch has ahead of that ref — a `git stash pop` afterward then layers new edits on top of the reverted state, not on your actual fix. Use `git show <ref>:<path>` (read-only, prints to stdout, touches nothing) or a separate worktree/checkout instead when you need to peek at another ref without disturbing HEAD. If it happens anyway, `git reset --hard HEAD` recovers cleanly (commits are untouched, only the index/working tree needed fixing).
- **Harness-only tasks (`.claude/`, `claude/`) skip branch creation**: A guardrail hook blocks `git checkout -b` in the root `inavflight/` repo — branches belong in the project repos (`inav/`, `inav-configurator/`, etc.). For tasks that only touch harness config/docs, commit straight to `master`, matching existing harness commit history.

#### Delegating to Agents

- **Always use fc-flasher agent for hardware flashing**: Never invoke `dfu-util` directly. STM32H7 boards silently fail DFU exit with raw dfu-util ("can't detach"), leaving the FC stuck. The fc-flasher agent uses the known-good script that handles all STM32 variants correctly.
- **Tell a lookup agent exactly which checkout to read, especially with multiple worktrees in the repo root**: asked to look up code in `inav2/`, the `msp-expert` agent instead read and reported from an unrelated untracked `inav-pr11756-review/` directory sitting in the repo root, guessing it was "the active working copy" — it happened to contain the same file, so the answer was still correct, but nothing forced that. When several `inav*`/ad hoc review checkouts coexist, state the exact path in the prompt rather than trusting the agent to infer the right one.
- **Check `git status`/`git log` on a task's named tool/script file before "extending" it**: a project's assignment email said a script "does not yet model X, needs extending" based on a report written days earlier. The extension already existed, fully implemented with its own self-tests — a prior session had written it but never committed it (the file was still untracked in `git status`). Re-implementing from the stale report would have duplicated real work and likely diverged from it. Five seconds of `git status`/`git log -- <path>` before writing new code in an assigned-but-possibly-already-done tool file would have caught this immediately either way.

#### Engineering Judgment

- **Fix blockers, don't route around them**: If goal X is blocked by small problem Y, fix Y first — don't pivot to complex workarounds (e.g. if a build fails due to an unrelated compile error in another file, fix that error rather than trying to analyze LTO bitcode object files to simulate what the linker would have produced). We build correct solutions, not workarounds.
- **Check for an existing upstream fix before implementing from a project plan**: Even when a manager-written summary already sketches an implementation, search open upstream PRs touching the same file/symptom (`gh pr list`/`gh api ...pulls` search, or a quick web check of the issue tracker) before writing new code. A pre-written plan can be superseded by someone else's already-tested fix with a cleaner design; cherry-picking that commit (crediting the original author) beats re-deriving a divergent implementation.
- **When fixing a bug in release/9.x, check maintenance-10.x for the same code pattern**: the two branches commonly share the same buggy lines (e.g. the ADS-B recalc-before-ttl order existed verbatim in both); `git show upstream/maintenance-10.x:<path>` is a 5-second check that turns a single fix into a fix-plus-backport-flag in the completion report, instead of the 10.x bug surfacing later as a separate issue.
- **In security-critical code, prefer fewer configuration knobs and shorter functions over flexibility**: during a setuid TOTP validator rewrite, the user repeatedly cut things back — rejected an env-var override for a path (env vars are attacker-influenced in some contexts and add a second code path to audit), rejected getpwnam()-based path defaults when the real deployment didn't use home directories, and rejected threading an extra out-parameter through a helper when the caller could just check for the condition directly. Stated principle: "complexity is the enemy of security." When writing auth/validation code, default to the fewest inputs, the fewest branches, and functions short enough to read top-to-bottom in one pass — don't add a knob or parameter unless something concrete needs it.
- **"It's live in production" is not authorization to import a change as-is**: when syncing a repo against a diff pulled from a real server, evaluate every hunk on its own merits rather than reproducing it verbatim. Skip commented-out dead code and one-off debugging hacks (a hardcoded email redirect for one account, a send-suppression rule for one address) — they add confusion, not capability. Separately, flag anything that introduces or preserves a live credential, a disabled/no-op auth check, or an endpoint that unconditionally reports success, for explicit user confirmation before merging — regardless of whether it's commented out or actively running. Being real and being safe are different questions.
- **A bot review comment (Qodo, CodeRabbit, etc.) deserves the same trace-through-the-code verification as a human's, not a dismissal**: two Qodo comments on an upstream PR claimed (1) a refused MSP write's `callback(false)` gets ignored by existing save-chain callbacks, so the save silently "succeeds" and the FC reboots anyway, and (2) one write code's naming pattern slips past the write-classifier regex. Both were confirmed correct by actually reading the callback chain (`tabs/failsafe.js`'s `savePhaseTwo()` takes no params, ignores the arg) and running the regex against every MSPCodes name in `node -e`. Cheap to verify, and both were real, non-obvious bugs a text-only review would likely have missed.

<!-- Add new lessons above this line -->
