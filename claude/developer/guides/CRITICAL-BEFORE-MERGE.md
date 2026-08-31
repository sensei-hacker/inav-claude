# ⚠️ CRITICAL CHECKLIST - Read Before Resolving Merge Conflicts

## ⛔ FIRST: Check merge direction — and never use GitHub's web conflict resolver

**NEVER merge a higher version branch into a lower one.** Version branches are release snapshots in time:
- `release/9.x` = older release
- `maintenance-10.x` = newer release

Merging `maintenance-10.x` into `release/9.x` drags months of newer development into an old release branch. This has caused serious damage. If you think merging a higher version in will fix a compile error or conflict — it won't. Fix the specific lines surgically instead.

The legitimate direction is lower → higher (backporting a fix from 9.x up into 10.x).

### ⛔ Never use GitHub's web "Resolve conflicts" button on these PRs

GitHub's own documentation warns:

> "When you resolve a merge conflict on GitHub, the **entire base branch** of your pull request is merged into the head branch."

For a PR from `release/9.x` → `maintenance-10.x`, the base is `maintenance-10.x`. Clicking "Resolve conflicts" in the browser merges ALL of `maintenance-10.x` into `release/9.x` — exactly the contamination this rule exists to prevent. The resulting commit will be named "Merge branch 'maintenance-10.x' into release/9.1", which looks routine but is destructive.

**Always resolve conflicts locally** using the procedure in `guides/merge-release-into-next-version.md` — branch off the *target* (newer) branch, merge the older branch into it, resolve there, then open a PR from that branch into the target.

### ⛔ Pick your workflow BEFORE you run any git command

This guide contains **two different, incompatible workflows**. Picking the wrong one is
the exact mistake this section exists to prevent — see the near-miss below. Answer this
first:

**Is the PR's HEAD branch itself a version/release branch** — `release/9.x`,
`maintenance-9.x`, `maintenance-10.x`, or similar — rather than a topic/feature branch?

- **Yes** (a release→next-version sync PR, e.g. `release/9.1` → `maintenance-10.x`,
  including when both branches live directly on `iNavFlight/inav` with no fork
  involved): **STOP.** Do not use the "MERGE, Not Rebase" workflow below — it merges
  the base INTO the PR branch, which for this PR shape means merging
  `maintenance-10.x` into `release/9.1` and contaminating the release branch. Use
  `guides/merge-release-into-next-version.md` instead: branch off `maintenance-10.x`
  (the target), merge `release/9.1` into *that* new branch, resolve there, push a
  **new** branch, open a **new** PR into `maintenance-10.x`. `release/9.1` is never
  touched or pushed to.
- **No** (an ordinary topic/feature branch, typically on a contributor's fork, merging
  into a release/maintenance branch — e.g. `shota3527/their-branch` → `maintenance-9.x`):
  continue to "MERGE, Not Rebase" below. That workflow (merge base into the PR branch,
  push back to the PR branch) is correct and expected here, because a feature branch
  isn't a version snapshot — updating it in place doesn't contaminate anything.

**Why this needs its own callout:** version branches (`release/9.x`) and topic branches
(`shota3527/their-branch`) look identical in a `git checkout -b resolve-conflict-pr-XXXX
<head>` command — nothing about the workflow's syntax warns you if you picked the wrong
one. You have to check the branch's *identity* before typing the first command, not
partway through.

#### Real-world near-miss: PR #11759

PR #11759 was `release/9.1` → `maintenance-10.x`, both branches living directly on
`iNavFlight/inav` (no fork — the head wasn't some contributor's disposable copy, it was
the actual shared release branch everyone else's `release/9.1` bugfix PRs are based on).
An agent read this entire guide first, correctly recited the direction rule when asked
about it later, and then still ran:

```bash
# ❌ What actually happened: branched off the PR head, merged base into it —
# this is the "MERGE, Not Rebase" workflow's pattern, applied to a release-branch PR
git checkout -b resolve-conflict-pr-11759 upstream/release/9.1
git merge upstream/maintenance-10.x --no-ff   # merges the NEWER branch into the OLDER one
```

This is precisely the forbidden direction from the top of this section — it just wasn't
recognized as such in the moment, because the concrete, copy-pasteable workflow lower in
this doc doesn't check branch identity, and defaulting to "the workflow with actual git
commands in it" is the natural thing to do once you're past the reading stage. A
pre-tool-use hook that re-prints the direction-check reminder on every `git merge` caught
it before the commit was pushed, and the merge was aborted and redone starting from
`maintenance-10.x` instead. Don't rely on the hook catching it a second time — use the
self-check above *before* the first `git checkout -b`.

---

**STOP! Read this entire guide before touching any merge conflict.**

The most expensive mistake in merge work is taking a whole file or whole function
from one branch instead of applying only the *changes* that branch made.
This silently drops everything the other branch added — bugs that are invisible
in diffs and burn enormous debugging time to trace.

---

## MERGE, Not Rebase

> ⚠️ **Does not apply if the PR's HEAD branch is itself a version/release branch**
> (`release/9.x`, `maintenance-9.x`, `maintenance-10.x`, ...). If you haven't done the
> "Pick your workflow" self-check above yet, do that first — the commands below merge
> base INTO the PR branch, which is the forbidden direction when the PR branch is a
> release snapshot. This section is for ordinary topic/feature branches only.

> **Always resolve conflicts with `git merge`, never `git rebase`.**

**Why this matters:**
- Rebase rewrites the PR author's commit history (new SHAs) and requires `--force-with-lease` to push — which is blocked by project rules.
- A merge commit adds a *new* commit on top of the PR branch, preserving the author's commits exactly and pushing normally without force.

**The workflow:**
```bash
# Start from the PR branch (not from base)
git checkout -b resolve-conflict-pr-XXXX shota3527/their-branch

# Merge the base branch INTO the PR branch (creates a new merge commit)
git merge upstream/maintenance-9.x --no-ff -m "Merge upstream/maintenance-9.x to resolve conflicts with PR #XXXX"
# Resolve conflicts, then:
git add <files>
git commit --no-edit

# Push normally — no force needed
git push shota3527 HEAD:their-branch
```

**Never do this:**
```bash
# ❌ This rewrites history and requires force push
git rebase upstream/maintenance-9.x
```

**This includes `git pull`, not just `git rebase`/`git merge` directly.** `pull.rebase=true`
used to be set globally on this machine, so a routine-looking `git pull upstream
maintenance-10.x` silently rebased. On a feature branch whose `upstream` remote-tracking
ref was stale (or being fetched for the first time), the fork-point was miscalculated and
the rebase replayed ~114 unrelated upstream commits onto the branch — 79 commits, 179
files, on a shared PR branch, with other contributors' work re-committed under the wrong
identity, before anyone noticed. `pull.rebase` is now `false` globally, so plain `git pull`
merges — but an explicit `git pull --rebase` (or `git rebase` directly) on a pushed/shared
branch carries the exact same risk. Always `git fetch` + `git merge` to sync a branch with
upstream.

---

## The Core Rule: Apply Changes, Not Files

> **The goal is the best possible resulting code — combine the fixes, features, and
> improvements from BOTH branches. Making the conflict marker disappear is not the goal;
> it's a side effect of doing this correctly.**

> **Always apply a branch's DIFF to the other branch's files.
> Never replace a file (or a function) wholesale with a version from another branch.**

This applies at every level of granularity:
- ❌ `git show pr-branch:file.js > file.js` — copies entire file
- ❌ Copy-pasting an entire function from the PR into the base file
- ✅ Identify the specific lines the PR added/changed, apply only those edits

Copy-pasting a whole function has the exact same problem as copying a whole file:
it silently loses whatever the base branch added to that function after the PR diverged.

---

## Before Starting Any Merge

### 1. Identify the correct base and incoming branches

```bash
# Base = the branch being merged INTO (e.g. maintenance-9.x)
# Incoming = the PR branch (e.g. scavanger/tab-modules)
git log --oneline base-branch..incoming-branch  # What the PR adds
git log --oneline incoming-branch..base-branch  # What base added since divergence
```

**For a GitHub PR specifically, don't assume the base is `master`** — check it:
```bash
gh pr view <number> --repo <owner>/<repo> --json baseRefName --jq .baseRefName
```
A PR can be stacked on `maintenance-10.x`, another unmerged feature branch, etc.
Computing `git merge-base` against the wrong branch silently returns some other
unrelated common ancestor, pulling hundreds of unrelated files into every diff
and size/behavior comparison from then on — it doesn't error, it just gives you
the wrong "before" state.

### 2. Find the common ancestor

```bash
git merge-base incoming-branch base-branch
# This is the point where both branches diverged — the "before" state
```

### 3. For each conflicting file, understand BOTH sides

```bash
# What the PR changed in this file:
git diff $(git merge-base incoming base):path/to/file incoming-branch:path/to/file

# What the base added in this file since divergence:
git diff $(git merge-base incoming base):path/to/file base-branch:path/to/file
```

---

## Resolving Each Conflict

### For simple rename/refactor files (e.g. TABS.foo → fooTab)

1. Take the BASE BRANCH version of the file
2. Apply only the rename transformation (sed, python, or manual)
3. Do NOT copy the PR's version — it may be missing base-branch additions

```bash
# RIGHT: start from base, apply rename
git show base-branch:tabs/foo.js > tabs/foo.js
sed -i 's/TABS\.foo\./fooTab\./g' tabs/foo.js
```

### For files with logic additions on both sides

1. Take the BASE BRANCH version of the file as the starting point
2. Diff the PR to find exactly what it changed:
   ```bash
   git diff <common-ancestor> incoming-branch -- path/to/file
   ```
3. Apply only those specific hunks to the base file using Edit tool
4. Do NOT replace entire functions — find the specific lines that changed

### For conflict markers (<<<< ==== >>>>)

When merging base INTO the PR branch (the correct approach):
- `HEAD` = PR branch (the author's code)
- `Incoming` = base branch (maintenance-9.x)
- Resolution = base content + the PR's additions applied on top

---

## After Resolving

### Verify no features were silently dropped

```bash
# For each resolved file, diff against the base branch
# Lines starting with '-' are base-branch features we may have dropped
git diff base-branch HEAD -- path/to/file | grep "^-[^-]" | head -30

# A large number of '-' lines (beyond expected renames) is a red flag
```

### Check for missing imports/functions

```bash
# Find all function calls in the resolved files
# Verify each called function actually exists somewhere
grep -rn "GUI\.\|someModule\." tabs/ js/ --include="*.js" | \
  grep -v "node_modules" | \
  awk '{print $2}' | sort -u
```

### Run a syntax check before committing

```bash
for f in tabs/*.js js/*.js; do
  node --input-type=module < "$f" 2>&1 | grep "SyntaxError" && echo "ERROR in $f"
done
```

---

## Common Mistakes and Their Symptoms

| Mistake | Symptom |
|---------|---------|
| Used `git rebase` instead of `git merge` | Force push required — blocked by project rules; author's commits rewritten |
| Replaced entire file with PR version | Runtime errors for functions added by base branch after divergence |
| Replaced entire function | Same — missing logic added to that function by base branch |
| Resolved conflict by taking PR side only | Missing base-branch features in that code block |
| Kept conflict markers (`>>>>>>>`) | Parse/syntax error from bundler |
| Forgot to check `js/` files (not just `tabs/`) | `is not a function` errors for helper functions defined in main JS files |

---

## Self-Improvement: Lessons Learned

- **A whole-file conflict on a refactored file can hide a *moved* function — "take the base version" would silently drop the PR's change**: PR #11769's conflict in `telemetry/mavlink.c` looked like pure branch drift (base had rewritten the file), but the PR's `mavlinkParseRxStats()` had been *moved* to `fc/fc_mavlink.c` during the mavlink refactor, and the GENERIC radio case there still carried the pre-fix code. Resolving by taking the base's file would have merged the PR as a no-op. Before resolving a whole-file conflict as "drift", `git grep` the PR's changed function/symbol on the base branch to check whether it moved — if so, re-apply the PR's exact diff at the new location (verify against the PR's actual commits, not the task's summary of them).
- **A forked agent's completion report can be truncated mid-merge, not a full summary**: for a large multi-file merge (e.g. 34 conflicted files) handed off to a fork, the task-notification's `result` text is whatever the fork happened to be saying when its turn budget ran out — it can look like a normal in-progress remark ("Same pattern seen before...") with no indication the job stopped short. On PR #2448's conflict resolution, a fork resolved 28 of 34 files and never committed, but the notification gave no sign anything was incomplete. Always verify directly after any "completed" fork on a merge: `git status` for remaining `UU` files, `grep -rn '^<<<<<<<\|^=======\|^>>>>>>>'` across the tree, and `git log` for the expected commit — don't treat the notification text as proof the merge commit exists.
- **A code review of the conflict-resolution diff catches leftover half-converted call sites the resolution itself misses**: mechanical renames/API-swaps (e.g. `store.get/set` → `bridge.storeGet/storeSet`) are easy to apply file-by-file but easy to miss a call site in a large file — a full build only catches a *missing import*, not an *undefined global* left behind when the import was correctly removed but a few call sites weren't updated. Run `inav-code-review` against the resolution diff specifically (not just a build+syntax check) before treating a large conflict resolution as done; expect at least one more round of "still-leftover" fixes after the first review.
- **A clean conflict resolution on a long-stale branch can still fail CI on RAM/flash overflow, not just syntax**: merging months of accumulated base-branch growth into a feature branch that hasn't built since it diverged (PR #11708 last passed CI in July; the base picked up terrain nav, VTOL protection, etc. since then) can push an unconditionally-compiled static buffer over budget on the tightest targets, even though the conflict markers themselves resolved cleanly with zero dropped lines. Don't stop at "no conflict markers, build succeeds locally" — push and watch full CI (all hardware targets + unit tests), especially when the branch's last green run predates a large chunk of base-branch history.
- **Gating a static buffer by `MCU_RAM_SIZE` also requires updating any unit test that force-defines the surrounding feature macro**: the unit-test build never defines `MCU_RAM_SIZE` at all, so a `#if MCU_RAM_SIZE > N` gate silently evaluates false there too — same failure mode as forgetting to update `terrain_unittest.cc`'s explicit `USE_TERRAIN` definition when `USE_TERRAIN` itself gained a real gate. Check `src/test/unit/CMakeLists.txt` for a `set_property(SOURCE ... PROPERTY definitions ...)` line naming the feature whenever adding a compile-time RAM/flash gate around code a unit test exercises directly.

## Checklist

Before marking a merge complete:

- [ ] Every resolved file diffed against base branch — no unexpected `-` lines
- [ ] Syntax check passed on all modified JS files
- [ ] No remaining `<<<<<<<`, `=======`, `>>>>>>>` markers in any file
- [ ] All function calls resolve to actual definitions (no "is not a function" errors)
- [ ] App loads and all tabs render without console errors
- [ ] Connected FC: key new PR features tested manually
