---
description: Disposition open PRs — decide merge/approve/comment/label/skip and set milestones; pre-scan activity
triggers:
  - triage prs
  - pr triage
  - pr disposition
  - disposition prs
  - assign milestones
  - pr milestones
  - scorecard triage
  - pr scorecard triage
  - triage scorecards
  - review ready prs
  - which prs are ready
  - walk through prs
  - pr review session
---

# PR Disposition Skill

Two modes, plus one separate backfill script:

| Mode | Question it answers | Script(s) | Order |
|------|---------------------|-----------|-------|
| **`activity`** | "What needs attention today?" | `fetch-activity-prs.sh` | most-recently-updated |
| **`disposition`** | "What's the next step toward merge?" | `scorecard-triage.sh`, `pr-scorecard.sh`, `update-pr.sh` | highest-score-first |

Two things are **separate processes, not modes of this skill**:

- **Merged-PR milestone backfill** — `claude/developer/scripts/triage/tag-maintenance-milestone.py`
  (retroactively set the milestone on already-merged PRs). See "Merged-PR Milestone Backfill" at the end.
- **Deeper code review** — the `/pr-review` skill + code-review/hardware agents, done by a
  **developer**. This skill may *recommend* "send this to a developer for code review", but it
  does **not** run that review and does not need to know how it works.

> **⚠️ Environment note:** `/tmp` is **not shared with subagents** in this harness — each
> command/subagent sees a fresh, ephemeral `/tmp`. Use the workspace tmp dir **`./tmp`** (a.k.a.
> `~/inavflight/tmp`, `$TMPDIR`) for anything another command or subagent must read back:
> prefetch output, caches, logs, cross-agent handoffs. The triage scripts write their caches to
> `./tmp/claude` and create that dir themselves, so a bare `mkdir -p ./tmp/claude` first is
> optional belt-and-suspenders. Never use `/tmp` in a path handed to these scripts or a subagent.

**Milestone status ≠ "has this PR been looked at."** `fetch-activity-prs.sh` (activity mode) shows
ALL open PRs regardless of milestone. Checking milestones is part of the disposition pass (below),
never a stand-in for "which PRs need review." (2026-09-13: drifted into a `no:milestone` search to
find "PRs we skipped," when the answer was already in that session's own NO-COMMENT bucket.)

---

## Milestone Criteria & Branch Validation (single source of truth)

The `disposition` mode and the merged-PR backfill script both consult these tables. They are
authoritative for branch→milestone mapping — do not restate a second, divergent copy anywhere else.

### Milestone Criteria

| Milestone | When to use |
|-----------|-------------|
| **9.1** | Straightforward bug fixes and compatible fixes/features with very little risk. Minimal code change, obvious correctness, backward-compatible with Configurator 9.0.0 and firmware 9.0.0. *(9.0.1 milestone is closed as of 2026-08 — its low-risk fixes now land in 9.1.)* |
| **9.1.1 / 9.1.2** | Patch releases on the 9.1 bugfix line — urgent hotfixes/regressions after 9.1 ships. |
| **10.0** | Breaking changes and coordinated firmware+configurator changes already in scope for 10.0. *(As of 2026-09 10.0 is in feature freeze — only critical fixes land here.)* |
| **10.1** | New features / significant non-breaking changes that arrive after the 10.0 feature freeze, especially features with no independent testing yet. |
| **11.0** | Next major after 10.1. Protocol/MSP cleanup that must wait for the following release cycle. |
| **Future** | Good idea but not prioritized for any current release. Large scope or speculative. |
| **Skip** | Don't assign a milestone now (add to skip file for later). |

### Branch Validation

**After selecting a milestone, verify the PR targets the correct base branch.** The single
authority for expected base branches is `.claude/skills/git-workflow/SKILL.md` ("Creating
Branches"). Current effective mapping:

| Milestone | Expected Base Branch |
|-----------|---------------------|
| **9.1 / 9.1.1 / 9.1.2** | inav: `release/9.1` — **temporary override active** (bugfix line) · configurator: `maintenance-9.x` |
| **10.0 / 10.1** | `maintenance-10.x` |
| **11.0** | `maintenance-10.x` (current 11.0 PRs, e.g. #9929, target this) |
| **Future** | any (no change needed) |

If the PR targets the wrong branch:
1. **Flag it to the user** in your analysis
2. Include `--base CORRECT_BRANCH` in the `update-pr.sh` call when applying changes

**Don't assume — ask if a branch/milestone mismatch is intentional.** The table above is the
default, not a hard rule. While inav's bugfix override is active, a 10.0-milestone fix can still
correctly target `release/9.1` (the path *into* `master`/`maintenance-10.x`) rather than
`maintenance-10.x` directly. (2026-09-13, PR #11886: retargeted `release/9.1` →
`maintenance-10.x` to match milestone 10.0 without asking; user reverted it — the branch was
already correct, milestone and base don't have to match here.) Check the git-workflow override
note before "fixing" a mismatch.

### Milestone Numbers (for API calls)

**iNavFlight/inav**
| Milestone | API Number |
|-----------|------------|
| 9.1 | 50 |
| 9.1.1 | 53 |
| 10.0 | 46 |
| 10.1 | 54 |
| 11.0 | 52 |
| Future | 18 |

> **9.0.1 (51) is CLOSED as of 2026-08** — do not assign it. Low-risk fixes go to 9.1.

**iNavFlight/inav-configurator**
| Milestone | API Number |
|-----------|------------|
| 9.0.1 | 36 |
| 9.1 | 35 |
| 9.1.1 | 38 |
| 9.1.2 | 39 |
| 10.0 | 37 |
| 10.1 | 40 |
| Future | 5 |

**Refreshing milestone numbers** (if milestones change):
```bash
gh api repos/iNavFlight/inav/milestones --jq '.[] | "\(.number) \(.title)"'
gh api repos/iNavFlight/inav-configurator/milestones --jq '.[] | "\(.number) \(.title)"'
```

---

## Mode 1: Activity Review — "What needs attention today?"

Use this at the START of a review session to avoid re-reading PRs that haven't changed.
A PR's **NO-COMMENT** classification (see table below) is the correct signal for "we haven't
weighed in yet" — regardless of whether it has a milestone.

The script defaults to **5 PRs per batch** (sorted by most-recently-updated). Process one batch,
then prefetch the next in the background while you review the current one — keeping context
window usage small and results appearing quickly.

### Streaming Workflow

**Step 1: Fetch first batch + prefetch next**

```bash
# Fetch current batch (foreground)
bash claude/developer/scripts/triage/fetch-activity-prs.sh iNavFlight/inav --months 6

# Prefetch next batch in background while you review
bash claude/developer/scripts/triage/fetch-activity-prs.sh iNavFlight/inav --months 6 --offset 5 \
    --output ./tmp/claude/prefetch-activity-inav.txt
```

Use the Bash tool with `run_in_background: true` for the prefetch call.

**Step 2: After reviewing and acting on the current batch**

Read the prefetched output (with the Read tool, not `cat`):
```bash
# Read: ./tmp/claude/prefetch-activity-inav.txt
```

Check if more PRs remain (a `MORE_PRS:` line at the end means there are more):
```bash
grep "^MORE_PRS:" ./tmp/claude/prefetch-activity-inav.txt
# Example output: MORE_PRS: next_offset=10 total=78
```

If more PRs exist, immediately start prefetching the next batch using `next_offset` from above.

### Activity Classifications

| Class | Meaning | Action |
|-------|---------|--------|
| **NEEDS-REVIEW** | New commits or comments since our last comment | Re-read and respond |
| **NO-COMMENT** | We've never commented or reviewed | First look needed |
| **WAITING ON OTHERS** | Our comment/review was the last activity | **Skip** — ball is in their court |
| **STALE** | No activity in 30+ days, never commented | Consider closing or pinging |

**For NEEDS-REVIEW, read every event since our last comment, not just the last one.** A trailing
bot comment can be the CI re-run *of* a fix an author already described earlier in the same gap —
reading only the tail misreads a real ready-to-merge signal as bot noise. (2026-09-13, PR #2725:
called "nothing to act on" from a tail SonarQube comment, missing the author's commit-by-commit
fix writeup right before it.)

**Key insight:** A PR in WAITING is one where we already made a request or comment and the
author hasn't responded. No need to re-read it. Focus time on NEEDS-REVIEW and NO-COMMENT.

**Auto-skip rule (2026-09-13):** a PR opened 6+ months ago with no substantive activity
(excluding our own questions/pings) can be skipped without a full re-review — note the age
and last-activity date in the skip file. Applies within NEEDS-REVIEW/NO-COMMENT too, not just
STALE.

**Quiet-period threshold = this session's own lookback, not a fixed number.** A 6-week
session uses ~60 days quiet; a session 48h later asking "updates in the last 3 days" uses
~3 days. Recompute each time from what was actually asked (the user's own stated window
already accounts for margin — don't add another on top), don't reuse the last value.

**Polluted branch history (2026-09-13):** if a PR's diff is far larger than its stated
purpose — hundreds+ of files/commits touching unrelated targets/docs/cmake — the branch has
picked up unrelated history (bad merge/rebase on the author's end), not a real intentional
change. Treat as **not reviewable as-is** (seen on #11723, #11932, #11870). **Never ask the
author, or one of our own developers, to rewrite history or force-push to fix it** — rewriting
shared history breaks the review process (invalidates comments tied to commit SHAs, breaks
others' local clones, hides what changed between review rounds). Instead: ask for a fresh PR
from a clean branch off current master, or have a developer extract just the intended change
into a new clean PR. Create a tracked project for this when the extraction is nontrivial.

### Options

```bash
# Larger batch for a longer session
bash claude/developer/scripts/triage/fetch-activity-prs.sh iNavFlight/inav --months 6 --batch-size 10

# Show PRs stale after only 14 days instead of default 30
bash claude/developer/scripts/triage/fetch-activity-prs.sh iNavFlight/inav --stale-days 14

# Use a different GitHub user
bash claude/developer/scripts/triage/fetch-activity-prs.sh iNavFlight/inav --our-user myusername

# Force-refresh cache
bash claude/developer/scripts/triage/fetch-activity-prs.sh iNavFlight/inav --no-cache
```

### How It Works

- **"Last activity"** = PR's `updated_at` (GitHub updates this on every push, comment, review,
  label change). Compared against our last comment/review date.
- **"Our last activity"** = most recent of: issue comment by us OR pull request review submitted by us.
- **"New commits after our comment"** = `updated_at > our_last_comment` even when no new comments.
  This catches the case where an author pushed a fix without commenting.
- **`--months N`** = only process PRs updated within the last N months; the script breaks early
  once the sorted list reaches older PRs, so it's fast even with many open PRs.
- **Limitation:** If our last comment was beyond the 100 most recent comments on a very active PR,
  we may be classified as NO-COMMENT. Check the PR directly in that case.
- **Limitation (found 2026-09-05):** `updated_at` is bumped by ANY metadata event — a label
  added/removed, milestone set, base branch changed — not just new comments. A PR can show
  NEEDS-REVIEW with an "activity by X" attribution that's actually months stale (X is just the
  most recent human commenter, not necessarily the cause of the bump). If the visible comments
  don't match a NEEDS-REVIEW flag, check
  `gh api repos/<owner>/<repo>/issues/<N>/timeline --jq '.[-6:]'` to see the real last event
  before trusting the classification.

---

## Mode 2: Open-PR Disposition — "What's the next step toward merge?"

For each open PR that has had recent activity (see Mode 1), decide the **single next action that
moves it one step closer to merged**: merge it, approve it, send it for code review, post a
question or comment, request a tester, label it, set its milestone — or skip it for now. This is a
disposition pass based on readiness signals, **not code review**. If the next step *is* a deeper
technical review, that's a hand-off ("send this to a developer for `/pr-review`") — this skill
does **not** run that review and does not need to know how it works.

First ask **"is it ready to merge?"** When it is, merge (or approve). When it isn't, name the next
step that unblocks it:
- **Ready to merge** → merge (or approve, if you're not a maintainer)
- **Needs code review first** → recommend a developer `/pr-review`
- **Question to ask** → post a comment (clarify intent, ask for a test, point at a failing check)
- **Needs testing** → find a tester / label `needs testing`
- **Needs work** → comment with the specific fix (open bot findings, review feedback, a rebase)
- **Not ready** → flag what specifically must change before revisiting

The score (0–100, from `/pr-scorecard`) refines that judgment and orders the queue. Milestone
assignment is one of the actions, not a separate pass.

### Usage

```
/pr-triage disposition [inav|configurator|both] [--after YYYY-MM-DD]
```

Default: both repos (inav first), PRs from the last 6 months. Pass `--after` to override.

### Preparation

```bash
mkdir -p ./tmp/claude
touch claude/local-data/triage/skip-inav.txt
touch claude/local-data/triage/skip-configurator.txt
```

### Main Loop

#### Step 1 — Get Next PR + Prefetch the One After

```bash
# Fetch current PR (foreground) — default window is 6 months
bash claude/developer/scripts/triage/scorecard-triage.sh \
    iNavFlight/inav \
    claude/local-data/triage/skip-inav.txt

# Or oldest-first (to avoid letting old PRs rot):
bash claude/developer/scripts/triage/scorecard-triage.sh \
    iNavFlight/inav \
    claude/local-data/triage/skip-inav.txt \
    --after 2025-10-01 --sort-oldest

# Immediately prefetch next in background
bash claude/developer/scripts/triage/scorecard-triage.sh \
    iNavFlight/inav \
    claude/local-data/triage/skip-inav.txt \
    --offset 1 \
    --output ./tmp/claude/prefetch-scorecard.txt
```

Use `run_in_background: true` on the prefetch call. If output is `NO_MORE_PRS`, that repo is
exhausted — move to the other repo or stop.

#### Step 2 — Run the Scorecard

Check the `CACHE_STATUS` line in the scorecard-triage output:

**If `CACHE_STATUS=fresh`:**
```bash
bash claude/developer/scripts/triage/pr-scorecard.sh iNavFlight/inav <PR_NUMBER>
```
Output contains `CACHE_HIT=true` — use the cached score/label directly. Do **not** re-run
`pr-scorecard-record.sh`.

**If `CACHE_STATUS=unscored` or `expired`:**
```bash
bash claude/developer/scripts/triage/pr-scorecard.sh iNavFlight/inav <PR_NUMBER>
# (add --force if status was expired)
```
Apply the scoring rubric from `/pr-scorecard` SKILL.md, then record:
```bash
bash claude/developer/scripts/triage/pr-scorecard-record.sh \
    iNavFlight/inav <PR_NUMBER> <SCORE> "<LABEL>" "<TITLE>" "<URL>"
```

#### Step 3 — Analyze

Beyond the scorecard output, check:

1. **What the PR does** - bug fix, feature, refactor, breaking change?
2. **Risk level** - How much code changes? How confident is correctness?
3. **Compatibility** - Does it break existing behavior for firmware or configurator users?
4. **Base branch** - Does it target the right branch for the suggested milestone?
5. **Testing status** - Labeled "needs testing"? Evidence of testing by someone other than the
   author? The PR description's testing section is NOT sufficient alone — external testing matters.
6. **Review status** - Has it been reviewed? Approved?
7. **Companion/paired PRs** - If it references a companion PR (firmware ↔ configurator) or
   depends on another PR, check that PR's real state before calling this one ready — a clean,
   reviewed PR can still block on an unfixed companion. Verify, don't just summarize.

**Cross-PR dependencies get a project, not just an email (2026-09-13):** if a developer task
blocks something else (e.g. "don't merge A until B's fixes land"), track it under `active/`,
naming the blocking relationship. An email alone can be forgotten.

**Always include the PR URL** (e.g., `https://github.com/iNavFlight/inav/pull/NNNN`).

**Link placement (manager convention, 2026-08-29):** in batch summaries, the PR number at the
**start of the headline** must be the clickable link — `**[#NNNN](https://github.com/iNavFlight/inav/pull/NNNN) — PR title**`.
The headline link is the only link for that PR.

**Unaddressed Qodo/bot findings (manager convention, 2026-09-04):** ask the author to read and
respond to the finding rather than the manager judging it right or wrong — Qodo is often wrong,
but the author should still be the one to decide. Substantive/technical bot findings that need a
human eye are a signal to *recommend a developer code review*, not to adjudicate here.

**Always check the most recent comments/commits (manager convention, 2026-09-05):** an older
flag (build failure, requested change, blocker) may already be resolved by later activity —
don't stop at the first blocking comment you find, confirm it's still current.

#### Step 4 — Check Milestone + Base Branch

If the milestone is wrong or missing, flag it with `⚠` in KEY SIGNALS and include setting it in
the suggested action. Use the **Milestone Criteria & Branch Validation** tables at the top of
this skill — the `MILESTONE CHECK` line in `pr-scorecard.sh` output is only a coarse hint, so
confirm against those tables before acting. A wrong/missing milestone is NOT a hard blocker but
should be fixed before merge.

Set milestone, base branch, and labels in a single `update-pr.sh` call:
```bash
bash claude/developer/scripts/triage/update-pr.sh iNavFlight/inav PR_NUMBER \
    --milestone MILESTONE_NUMBER \
    --base CORRECT_BRANCH \
    --add-label "New target"
```

**You MUST use `update-pr.sh`** for milestone/base/label — do not call `gh api`/`gh issue edit`
directly (the script handles API quirks reliably).

**The manager's `gh` token cannot merge PRs** (`gh pr merge` fails: "Resource not accessible by
personal access token"). Set milestone/labels/base as usual, then ask the user to merge — don't
attempt `gh pr merge` expecting it to work (2026-09-13).

#### Step 5 — Generate Suggested Disposition

| Condition | Suggested Action |
|-----------|-----------------|
| Hard blocker: draft | Skip — not ready |
| Hard blocker: merge conflicts | Comment: ask author to rebase |
| Hard blocker: CI failing | Comment: point to failing check |
| Hard blocker: changes requested | Comment: ask author to address review |
| Score 0–25 (Not Ready) | Comment: explain what's missing |
| Score 26–45 (Needs Work) | Comment: specific asks (testing, review, docs) |
| Score 46–65 (Promising) | Label `needs testing` OR comment requesting a tester |
| Score 66–80 (Looking Good) | Ask for one final confirmation, then it's merge-ready |
| Score 81–90 (Merge Candidate) | **Merge** (or Approve if you're not a maintainer) |
| Score 91–100 (Ready to Merge) | **Merge** |

For comment suggestions, be specific. Examples:
- "Could someone with the relevant hardware test this?"
- "Two open review threads need resolution before merge."
- "CI check `Build MATEKF405` is failing — please fix."
- "Looks good! I'll merge once the open review thread is closed."

**Needs a deeper technical review?** If a PR touches driver/register-level code or has substantive
bot findings that warrant a human code review, the disposition is *"send this to a developer for
`/pr-review`"* — create a tracked task/email to a developer. That review is a separate developer
process; this skill only recommends it.

#### Step 6 — Present to User

```
============================================================
PR #11220: Fix waypoint navigation calculation   [74/100 — Looking Good]
============================================================
https://github.com/iNavFlight/inav/pull/11220

Author: contributor123 (CONTRIBUTOR) | 52 days old
Labels: none | Base: maintenance-9.x

BLOCKERS: None

KEY SIGNALS
  ✓ CI: 12/12 checks passing
  ✓ Review: 1 member approval (sensei-hacker: APPROVED)
  ✓ Testing: 1 non-author confirmed testing
  ⚠ 2 open review threads not yet resolved
  ~ Scope: 180 lines, touches navigation subsystem

SUGGESTED: Comment asking reviewer to close the 2 open threads, then merge.

------------------------------------------------------------
[m]erge   [a]pprove   [c]omment   [l]abel   [s]kip   [q]uit
```

Key/symbol guide for KEY SIGNALS:
- `✓` = positive signal
- `⚠` = concern or soft blocker
- `✗` = hard blocker
- `~` = neutral/informational

**Always print the URL on its own line** so it's clickable in the terminal.

#### Step 7 — Wait for User Decision

| Input | Action |
|-------|--------|
| `m` or `merge` | Merge the PR (see below) |
| `a` or `approve` | Approve the PR |
| `c` or `comment <text>` | Post a comment (use suggested text if no text given) |
| `l` or `label <name>` | Add a label |
| `s`, `n`, or `skip` | Skip this PR for this session |
| `q` or `done` | End the session |

If the user types just `c` or `l` without text, prompt for the text/label.

#### Step 8 — Execute the Action

**Merge**
```bash
gh pr merge <PR_NUMBER> --repo iNavFlight/inav --squash --auto
```
Ask the user for merge strategy if not obvious: `--squash` (default), `--merge`, or `--rebase`.
If merge fails with a permission error (the manager token can't merge), ask the user to merge.

**Approve**
```bash
gh pr review <PR_NUMBER> --repo iNavFlight/inav --approve -b "Looks good to merge."
```

**Comment**
```bash
gh pr comment <PR_NUMBER> --repo iNavFlight/inav --body "Your comment here."
```

**Label**
```bash
gh api repos/iNavFlight/inav/issues/<PR_NUMBER>/labels \
    --method POST --field 'labels[]=needs testing'
```

**Milestone / base / labels** — via `update-pr.sh` (Step 4).

**Skip (no GitHub action — just add to the session skip file)**
```bash
echo "<PR_NUMBER>" >> claude/local-data/triage/skip-inav.txt
```

**Recommend developer review** — create a tracked task/email to a developer (a `/pr-review`
hand-off); do not run the review agents here.

#### Step 9 — Advance to Next PR

After any action (including skip):

1. Invalidate the PR list cache so merges/labels are reflected:
   ```bash
   rm -f ./tmp/claude/scorecard-pr-cache-*.json
   ```

2. Read the prefetched output:
   ```bash
   # Read: ./tmp/claude/prefetch-scorecard.txt
   ```

3. From the prefetch output, start fetching the scorecard for THAT PR:
   ```bash
   bash claude/developer/scripts/triage/pr-scorecard.sh \
       iNavFlight/inav <NEXT_PR_NUMBER> \
       --output ./tmp/claude/prefetch-scorecard-data.txt
   ```
   Use `run_in_background: true`.

4. While that runs, present the current prefetched PR to the user (go to Step 5).

5. Kick off the next `scorecard-triage.sh --offset 1` prefetch for the one after that.

Continue until: user says `q`/`done`, `NO_MORE_PRS`, or you switch repos.

### Configurator Repo

Replace `iNavFlight/inav` with `iNavFlight/inav-configurator` throughout. Use the skip file
`claude/local-data/triage/skip-configurator.txt`.

### Example Session

```
> /pr-triage disposition inav

============================================================
PR #11220: Fix waypoint navigation calculation   [74/100 — Looking Good]
============================================================
https://github.com/iNavFlight/inav/pull/11220

Author: contributor123 (CONTRIBUTOR) | 52 days old
Labels: none | Base: maintenance-9.x

BLOCKERS: None

KEY SIGNALS
  ✓ CI: 12/12 checks passing
  ✓ Review: 1 member approval (sensei-hacker: APPROVED)
  ✓ Testing: 1 non-author confirmed testing ("works on MATEKF405")
  ⚠ 2 open review threads not yet resolved
  ~ Scope: 180 lines, touches navigation subsystem

SUGGESTED: Comment asking the reviewer to close the 2 open threads.
           "Looks good! Once the 2 open review threads are closed this is merge-ready."

[m]erge  [a]pprove  [c]omment  [l]abel  [s]kip  [q]uit

> c

[Using suggested comment text]
Posted comment on PR #11220. Moving to next PR...

============================================================
PR #11189: Add new MATEKF405SE target   [91/100 — Ready to Merge]
...
SUGGESTED: Merge

[m]erge  [a]pprove  [c]omment  [l]abel  [s]kip  [q]uit

> m

Merging PR #11189 (squash)... Done.
Moving to next PR...
```

### Score Calibration

**"Needs Work" does not mean "don't merge."** The score reflects how many readiness signals are
present — it is a floor for discussion, not a hard gate.

A COLLABORATOR's 2-day-old bugfix with perfect CI can legitimately score 30/100 (no maturity, no
approvals yet) and still be the right call to merge. The score helps surface *what's missing* —
the maintainer decides whether that matters.

Use the score to guide questions:
- Low maturity + trusted author → fine to merge if the fix is obvious
- Low testing + core subsystem → wait for hardware confirmation
- Active unresolved review discussion → resolve before merging
- Low score across all categories → needs more time and engagement

---

## Testing Status Assessment

When analyzing testing, report one of:
- **Tested by others** - Comments show someone besides the author tested it
- **Author-tested only** - Only the PR author reports testing
- **Needs testing** - Labeled "needs testing" / "Testing Required" or no testing evidence
- **Untested** - No testing mentioned at all

## Labeling Inactive PRs

When a PR author has gone quiet (no response to our question, or no activity for months), apply the **Inactive** label — not "no response" or other improvised labels.

```bash
gh pr edit PR_NUMBER --repo iNavFlight/inav --add-label "Inactive"
```

This is the standard label the project uses for abandoned/unresponsive PRs.

## Related Skills

- **pr-scorecard** — Score a single PR in detail (the rubric used by the disposition mode)
- **pr-review** — Full code review (checkout, build, review bots). This is a **developer**
  process; the disposition mode recommends it as a hand-off but does not run it.
- **check-builds** — Deep-dive CI failure investigation

## Notes

- Draft PRs and PRs labeled "don't merge" (case-insensitive) are automatically excluded
- Skip files persist across sessions at `claude/local-data/triage/skip-*.txt` (gitignored local data)
- Always verify milestone numbers are current before starting a session
- If GitHub API calls fail with network errors, that's the sandbox — ask the user to approve the operation rather than disabling the sandbox (`api.github.com` is allowlisted, so failures usually mean something else is wrong)
- `CACHE_STATUS=fresh` means use cached score — no re-fetch, no re-record
- `CACHE_STATUS=unscored` or `expired` means fetch fresh and record
- The prefetch model keeps you from waiting between PRs
- Use `/pr-scorecard <N>` for the full detailed scorecard on any individual PR
- Disposition-mode default date window is **6 months**; pass `--after YYYY-MM-DD` to override

## Merged-PR Milestone Backfill (separate process)

Milestone assignment for **already-MERGED** PRs is handled by a separate script — retroactive
backfill of the release milestone onto merged PRs targeting a maintenance base branch. Run it as
its own step when release milestones need to be backfilled (e.g. after a release branch cut):

```bash
# Default: maintenance-10.x -> 10.0
python3 claude/developer/scripts/triage/tag-maintenance-milestone.py --dry-run
python3 claude/developer/scripts/triage/tag-maintenance-milestone.py

# Future release cycle
python3 claude/developer/scripts/triage/tag-maintenance-milestone.py --base maintenance-11.x --milestone 11.0
```
