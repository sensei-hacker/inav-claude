# Repository Locks

This directory contains lock files to prevent multiple developers from working in the same repository simultaneously.

**Use `claude/locks/lock_manager.py` to acquire and release locks — see
"How to Use" below.** Don't hand-write lock files or `rm` them directly:
the script enforces the exact format the lock-check hook
(`.claude/hooks/deterministic_checks.py`) expects, and it runs the
dirty-checkout sanity check automatically (see "Dirty-checkout policy"
below) before handing out a lock.

## Lock Files

- `inav.lock` - Locks the firmware repository (`inav/`)
- `inav2.lock` - Locks the second firmware worktree/clone (`inav2/`), if present
- `inav3.lock` - Locks the third firmware worktree/clone (`inav3/`), if present
- `inav-configurator.lock` - Locks the configurator repository (`inav-configurator/`)
- `inav-configurator2.lock` - Locks the second configurator worktree/clone (`inav-configurator2/`), if present

Some setups only have a single `inav/` checkout — in that case only `inav.lock`
applies. If `inav2/` and/or `inav3/` exist as separate worktrees/clones, they
allow parallel firmware tasks and use their own numbered lock file. Likewise
`inav-configurator2/`, if present, allows a second parallel configurator task.
Each lock file governs only its matching directory; holding `inav.lock` does
not block work in `inav2/` or `inav3/`, and holding `inav-configurator.lock`
does not block work in `inav-configurator2/`.

## Rules

1. **One developer per directory** - Only one developer can hold a lock on a given repo directory (`inav/`, `inav2/`, `inav3/`, `inav-configurator/`, `inav-configurator2/`) at a time
2. **Parallel work allowed** - A developer can work in `inav2/` while another works in `inav/`, `inav3/`, `inav-configurator/`, or `inav-configurator2/`
3. **Check before starting** - `lock_manager.py acquire` tries `inav.lock`, then `inav2.lock`, then `inav3.lock` in order and returns whichever checkout it locked
4. **Release when done** - `lock_manager.py release <repo>` when task is complete

## How to Use

### Acquiring a Lock (Developer)

```bash
REPO=$(python3 claude/locks/lock_manager.py acquire --task <task-name> --branch <branch-name> --type firmware)
```

This tries `inav`, `inav2`, `inav3` in order (or `inav-configurator`, then
`inav-configurator2`, with `--type configurator`), skipping anything locked or unexpectedly dirty, and
prints the name of the checkout it locked (e.g. `inav2`) to stdout — that's
the directory to `cd` into and branch from. Diagnostics for skipped
candidates go to stderr.

If every candidate is locked or dirty, the script exits non-zero and prints
why for each one. **Do not work around this by force-acquiring or hand-editing
a lock file** — investigate (per "Dirty-checkout policy" below) or report to
the manager that all checkouts are busy.

### Releasing a Lock (Developer)

```bash
python3 claude/locks/lock_manager.py release inav2
```

Refuses to release a lock held by a different session unless you pass
`--force` (only after confirming with the user/manager it's safe). Include
in your completion report which lock you released, e.g. "Released
inav2.lock".

### Checking Status

```bash
python3 claude/locks/lock_manager.py status
```

Shows every repo's lock state, and for unlocked firmware/configurator
checkouts, whether the working tree is actually clean.

### Manager Responsibilities

- Include lock acquisition in task assignments
- Verify locks are released in completion reports
- Resolve conflicts if two tasks need same repo

## Dirty-Checkout Policy

An absent lock file doesn't guarantee an idle tree — a session can leave a
checkout on an unfamiliar branch with uncommitted changes without a lock
file to show for it (e.g. after releasing its lock slightly early, or never
acquiring one in the first place). This is a real, observed failure mode,
not just a hypothetical: `inav2/` was found sitting on branch
`shrink-ledstrip-dma-buffer` with 20+ untracked files and no `inav2.lock` at
all. So `acquire` runs `git status --porcelain` on any unlocked candidate
before handing it out, and **skips it instead of acquiring** if the tree
isn't clean — uncommitted changes on an unfamiliar branch might be someone
else's real, unfinished work.

If `acquire` reports a candidate as dirty, don't just proceed anyway or
discard what's there. Check `claude/developer/email/sent/` for a completion
report matching that branch/task name to determine whether it's genuinely
abandoned or still in progress.

**Exception — the `claude/`/`.claude/` tripwire dirs:** every firmware
checkout has a root-owned `claude/` directory (containing a `CLAUDE.md` that
says "wrong directory, go up one level") to catch an agent that mistakes the
firmware checkout for the harness root. Some checkouts also carry the
Claude Code session config `.claude/`. Neither belongs to any task's WIP —
if one shows up as the *only* thing making a candidate dirty, check whether
it's simply missing from that checkout's `.git/info/exclude` (compare
against a checkout where it's already excluded, e.g. `inav3`) rather than
digging for a completion report. `claude/` is often root-owned and can't be
moved/deleted by the session user — excluding it locally is the fix, not
removal.

The opposite failure — a lock file left in place well after its task
actually finished — also happens regularly (see
`claude/developer/workspace/stale-locks-investigation/findings.md` for a
real example of three simultaneously-stuck locks, none of which were caused
by a power-cycle crash — each was a mundane handoff gap, like a completion
report never sent). `acquire` cannot distinguish a stale lock from a live
one; a lock file that looks suspiciously old is a cue to investigate
(check `claude/developer/email/sent/` for that task's completion report)
before asking to have it released, not a reason to `release --force` it
yourself.

## Lock File Format

```
LOCKED_BY: Developer
TASK: <project-name or task description>
LOCKED_AT: YYYY-MM-DD HH:MM
BRANCH: <branch-name>
SESSION_ID: <$CLAUDE_CODE_SESSION_ID>
```

`SESSION_ID` is the acquiring session's `$CLAUDE_CODE_SESSION_ID` environment
variable. `lock_manager.py` reads this automatically; only pass `--session`
to override it. This format is load-bearing: the lock-check hook
(`.claude/hooks/deterministic_checks.py`) parses it directly to decide
whether a write into a locked repo is this session's own work (silently
allowed) or another session's (asks for confirmation) — do not change the
field names or `KEY: value` shape without updating that hook too.

## Manual Fallback

If the script is unavailable for some reason, the lock file can be
hand-written in the format above — but you must then also run the
dirty-checkout check (`git status --porcelain`, `git branch --show-current`)
yourself before writing the lock, per "Dirty-checkout policy" above. Prefer
fixing/using the script over reverting to this path.
