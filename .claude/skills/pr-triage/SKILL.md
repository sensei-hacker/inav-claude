---
description: Triage open PRs for merge readiness; assign milestones as part of that process
triggers:
  - triage prs
  - pr triage
  - milestone triage
  - assign milestones
  - pr milestones
---

# PR Triage Skill

Two modes: **initial triage** (milestone assignment, uses `fetch-next-pr.sh`) and **activity review** (ongoing follow-up, uses `fetch-activity-prs.sh`). Choose the right mode for the session.

---

## Mode 1: Activity Review — "What needs attention today?"

Use this at the START of a review session to avoid re-reading PRs that haven't changed.

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
    --output /tmp/claude/prefetch-activity-inav.txt
```

Use the Bash tool with `run_in_background: true` for the prefetch call.

**Step 2: After reviewing and acting on the current batch**

Read the prefetched output:
```bash
cat /tmp/claude/prefetch-activity-inav.txt
```

Check if more PRs remain (a `MORE_PRS:` line at the end means there are more):
```bash
grep "^MORE_PRS:" /tmp/claude/prefetch-activity-inav.txt
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

**Key insight:** A PR in WAITING is one where we already made a request or comment and the
author hasn't responded. No need to re-read it. Focus time on NEEDS-REVIEW and NO-COMMENT.

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

---

## Mode 2: Initial Milestone Triage — "Which unmilestoned PRs need a milestone?"

Systematically triage open PRs for merge readiness, working through them in date order (oldest first).

**Primary goal: decide if each PR is ready to merge.** Milestone assignment is a required step before merging, but the main triage question is merge readiness — code quality, testing, open issues, review status.

For each PR, lead with a **merge readiness verdict**:
- **Ready to merge** — code is good, tested, reviewed, no open blockers
- **Needs review** — no human review yet
- **Needs testing** — author-tested only, or labeled "needs testing"
- **Needs work** — open bot findings, review feedback, or known issues to resolve
- **Not ready** — major concerns; flag specifically what must be resolved

Milestone is part of the output but secondary to the readiness verdict.

## Usage

```
/pr-triage [inav|configurator|both] [after-date]
```

- Default repo: both (inav first, then configurator)
- Default after-date: 12 months ago from today

## Script Locations

```
claude/developer/scripts/triage/fetch-next-pr.sh   # Fetch next PR for triage
claude/developer/scripts/triage/update-pr.sh        # Set milestone, branch, labels
```

**IMPORTANT:** You MUST use `update-pr.sh` for all PR updates (milestones, base branches, labels).
Do NOT call `gh api` or `gh issue edit` directly — the script handles API quirks reliably.

## Milestone Criteria

| Milestone | When to use |
|-----------|-------------|
| **9.1** | Straightforward bug fixes and compatible fixes/features with very little risk. Minimal code change, obvious correctness, backward-compatible with Configurator 9.0.0 and firmware 9.0.0. *(9.0.1 milestone is closed as of 2026-08 — its low-risk fixes now land in 9.1.)* |
| **10.0** | Breaking changes. Would break compatibility with Configurator 9.0.0 or firmware 9.0.0, or requires coordinated firmware+configurator changes. |
| **11.0** | Next major after 10.0. Protocol/MSP cleanup that must wait for the following release cycle. |
| **Future** | Good idea but not prioritized for any current release. Large scope or speculative. |
| **Skip** | Don't assign a milestone now (add to skip file for later). |

## Branch Validation

**After selecting a milestone, verify the PR targets the correct base branch.**

| Milestone | Expected Base Branch |
|-----------|---------------------|
| **9.1** | `release/9.1` — **temporary override active** (bugfix line); verify in `.claude/skills/git-workflow/SKILL.md` ("Creating Branches") before relying on it |
| **10.0** | `maintenance-10.x` |
| **11.0** | `maintenance-10.x` (current 11.0 PRs, e.g. #9929, target this) |
| **Future** | any (no change needed) |

If the PR targets the wrong branch:
1. **Flag it to the user** in your analysis
2. Include `--base CORRECT_BRANCH` in the `update-pr.sh` call when applying changes

## Milestone Numbers (for API calls)

### iNavFlight/inav
| Milestone | API Number |
|-----------|------------|
| 9.1 | 50 |
| 10.0 | 46 |
| 11.0 | 52 |
| Future | 18 |

> **9.0.1 (51) is CLOSED as of 2026-08** — do not assign it. Low-risk fixes go to 9.1.

### iNavFlight/inav-configurator
| Milestone | API Number |
|-----------|------------|
| 9.0.1 | 36 |
| 9.1 | 35 |
| 10.0 | 37 |
| Future | 5 |

### Refreshing Milestone Numbers
If milestones change, refresh with:
```bash
gh api repos/iNavFlight/inav/milestones --jq '.[] | "\(.number) \(.title)"'
gh api repos/iNavFlight/inav-configurator/milestones --jq '.[] | "\(.number) \(.title)"'
```

## Workflow

### Step 1: Initialize

Skip files persist across sessions at:
```
claude/local-data/triage/skip-inav.txt
claude/local-data/triage/skip-configurator.txt
```

Ensure they exist:
```bash
touch claude/local-data/triage/skip-inav.txt
touch claude/local-data/triage/skip-configurator.txt
```

Also create a temp dir for prefetch output and PR list cache:
```bash
mkdir -p /tmp/claude
```

### Step 2: Fetch First PR + Prefetch Next

On the very first iteration, fetch the current PR and **immediately start prefetching the next one in the background**:

```bash
# Fetch current PR (foreground)
bash claude/developer/scripts/triage/fetch-next-pr.sh iNavFlight/inav YYYY-MM-DD claude/local-data/triage/skip-inav.txt

# Prefetch next PR in background (uses cached PR list, only fetches reviews/comments)
bash claude/developer/scripts/triage/fetch-next-pr.sh iNavFlight/inav YYYY-MM-DD claude/local-data/triage/skip-inav.txt --offset 1 --output /tmp/claude/prefetch-inav.txt
```

The script caches the PR list for 2 minutes, so the prefetch reuses it and only makes API calls for the next PR's reviews and comments.

Use the Bash tool with `run_in_background: true` for the prefetch call.

**IMPORTANT:** When reading prefetch results, use the Read tool on the `--output` file path (`/tmp/claude/prefetch-inav.txt` or `/tmp/claude/prefetch-configurator.txt`), NOT the task runner's output file. The script redirects all output to the `--output` file, so the task runner captures nothing.

### Step 3: Analyze and Suggest

After reading the script output, analyze:

1. **What the PR does** - bug fix, feature, refactor, breaking change?
2. **Risk level** - How much code changes? How confident is correctness?
3. **Compatibility** - Does it break existing behavior for firmware or configurator users?
4. **Base branch** - Does it target the right branch for the suggested milestone?
5. **Testing status**:
   - Is it labeled "needs testing" or "Testing Required"?
   - Do comments indicate testing by someone other than the author?
   - The PR description's testing section is NOT sufficient alone - external testing matters
6. **Review status** - Has it been reviewed? Approved?

Present your analysis with a **merge readiness verdict first**, then the suggested milestone. Flag testing concerns, open bot findings, and branch mismatches prominently.

**Always include the PR URL** (e.g., `https://github.com/iNavFlight/inav/pull/NNNN`) so the user can quickly open it.

**Link placement (manager convention, 2026-08-29):** in batch summaries, the PR number at the **start of the headline** must be the clickable link — `**[#NNNN](https://github.com/iNavFlight/inav/pull/NNNN) — PR title**`. Do NOT put the link somewhere else in the description body; the headline link is the only link for that PR.

### Step 4: User Confirms or Changes

Wait for user to confirm the milestone choice or specify a different one.

### Step 5: Apply Changes with update-pr.sh

Use `update-pr.sh` to set milestone, fix base branch, and add labels **in a single call**.
Build the arguments based on what's needed:

```bash
# Example: milestone + branch fix + new target label
bash claude/developer/scripts/triage/update-pr.sh iNavFlight/inav PR_NUMBER \
    --milestone MILESTONE_NUMBER \
    --base CORRECT_BRANCH \
    --add-label "New target"

# Example: just milestone (branch already correct, no label needed)
bash claude/developer/scripts/triage/update-pr.sh iNavFlight/inav PR_NUMBER \
    --milestone MILESTONE_NUMBER
```

Auto-tag: If the PR adds a new hardware target but is NOT labeled "New target", include `--add-label "New target"`.

After applying changes, **invalidate the cache** so the next prefetch gets fresh data:
```bash
rm -f /tmp/claude/pr-cache-*.json
```

Then **immediately read the prefetched output** and present it to the user:
```bash
cat /tmp/claude/prefetch-inav.txt  # or prefetch-configurator.txt
```

While the user reads the prefetched PR, **start prefetching the one after that** in the background:
```bash
bash claude/developer/scripts/triage/fetch-next-pr.sh iNavFlight/inav YYYY-MM-DD claude/local-data/triage/skip-inav.txt --offset 1 --output /tmp/claude/prefetch-inav.txt
```

### Step 7: Handle Skip

If the user says "skip", add the PR number to the skip file:
```bash
echo "PR_NUMBER" >> claude/local-data/triage/skip-inav.txt
# or
echo "PR_NUMBER" >> claude/local-data/triage/skip-configurator.txt
```

**Date every skip entry** (manager convention, 2026-08-29): always annotate
with `# PR - YYYY-MM-DD: <reason>` above the bare PR number. The date is
the "last looked" timestamp — a future session must be able to re-find any
PR whose activity is newer than its skip-date (e.g. read the PRs that have
updates AFTER the last time we looked at them). Keep the reason brief and
actionable (e.g. "awaiting author reply", "CI pending", "assigned to dev",
"MERGED").

Then invalidate cache and show prefetched PR as in Step 6.

### Step 8: Loop

Continue the cycle: show prefetched PR, prefetch next one, wait for user decision. Stop when:
- No more PRs to triage (script outputs `NO_MORE_PRS`)
- User says to stop
- Switching to the other repo

## Testing Status Assessment

When analyzing testing, report one of:
- **Tested by others** - Comments show someone besides the author tested it
- **Author-tested only** - Only the PR author reports testing
- **Needs testing** - Labeled "needs testing" / "Testing Required" or no testing evidence
- **Untested** - No testing mentioned at all

## Example Session

```
> /pr-triage inav

Fetching oldest untriaged PR for iNavFlight/inav (after 2025-02-07)...

============================================================
PR #11190: MSP: Add minimum power index to MSP_VTX_CONFIG
============================================================
URL:     https://github.com/iNavFlight/inav/pull/11190
Author:  sensei-hacker
Created: 2025-12-15
Base:    maintenance-9.x
Labels:  none
...

ANALYSIS:
- Adds one byte to MSP_VTX_CONFIG response
- Compatible change (older configurator ignores extra byte)
- Base branch: maintenance-9.x (correct for 9.1)
- Testing: Author-tested only, needs hardware VTX validation

SUGGESTION: 9.1
BRANCH: maintenance-9.x (correct)

> [user]: 9.1

Setting milestone 9.1 (50) on PR #11190... Done.
Fetching next PR...
```

## Labeling Inactive PRs

When a PR author has gone quiet (no response to our question, or no activity for months), apply the **Inactive** label — not "no response" or other improvised labels.

```bash
gh pr edit PR_NUMBER --repo iNavFlight/inav --add-label "Inactive"
```

This is the standard label the project uses for abandoned/unresponsive PRs.

## Notes

- PRs that already have a milestone are automatically excluded
- Draft PRs are automatically excluded
- PRs labeled "don't merge" (case-insensitive) are automatically excluded
- Once a milestone is set, the PR won't appear in subsequent fetches
- The skip file persists across sessions at `claude/local-data/triage/skip-inav.txt`
- Always verify milestone numbers are current before starting a session
