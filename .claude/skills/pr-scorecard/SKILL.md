---
description: Score a pull request's merge-readiness based on CI status, reviews, testing evidence, maturity, and scope/risk
triggers:
  - pr scorecard
  - score pr
  - pr readiness
  - merge readiness
  - is this pr ready
  - ready to merge
  - scorecard
  - pr score
---

# PR Merge-Readiness Scorecard

Evaluate how ready a pull request is to merge, based on non-code signals:
CI results, review quality, testing evidence, maturity, and change scope/risk.
This is NOT a code review — it is a readiness assessment.

## Usage

```
/pr-scorecard <PR_NUMBER> [inav|configurator] [--force]
/pr-scorecard 11220
/pr-scorecard 11220 inav
/pr-scorecard 2500 configurator
/pr-scorecard 11220 inav --force     # bypass 14-day cache
/pr-scorecard --history              # show all scored PRs
/pr-scorecard --history inav         # show scored PRs for inav repo only
```

Default repo is `iNavFlight/inav`. Use `configurator` for `iNavFlight/inav-configurator`.

---

## Cache Behaviour

Once a PR is scored, the result is stored in
`claude/local-data/triage/pr-scorecard-history.json`.

- Re-running `/pr-scorecard` on the same PR within **14 days** returns the
  cached score immediately without any GitHub API calls.
- The output will include `CACHE_HIT=true` — display the cached result and stop.
- Pass `--force` to bypass the cache and re-score (e.g. after significant new
  activity on the PR).

---

## History View

To list all previously scored PRs:

```bash
bash claude/developer/scripts/triage/pr-scorecard-record.sh --list
bash claude/developer/scripts/triage/pr-scorecard-record.sh --list iNavFlight/inav
```

---

## Step 1 — Run the Data-Gathering Script

```bash
bash claude/developer/scripts/triage/pr-scorecard.sh iNavFlight/inav <PR_NUMBER>
# or
bash claude/developer/scripts/triage/pr-scorecard.sh iNavFlight/inav-configurator <PR_NUMBER>
# with --force to bypass cache:
bash claude/developer/scripts/triage/pr-scorecard.sh iNavFlight/inav <PR_NUMBER> --force
```

If the output contains `CACHE_HIT=true`, display the cached scorecard and **stop
here** — do not re-score, do not call the record script again.

If GitHub API calls fail on a fresh fetch with network errors, that's the sandbox
blocking the operation — not a network outage (`api.github.com` is in the sandbox
allowlist, so this should be rare). Do not disable the sandbox; ask the user to
approve the operation or run it manually.

When fetching fresh data, also run the `check-pr-bots` agent in parallel to
capture automated review issues that the script cannot detect:

```
Agent(check-pr-bots): "Check bot comments on PR #<NUMBER> in iNavFlight/inav"
```

**Bot findings must be checked for resolution before they are treated as open (2026-09-20).**
The scorecard's "CODE REVIEW" section now emits a resolution-aware count from GraphQL:

```
  Review threads (resolution-aware, GraphQL):
    Bot threads:  total=N resolved=R outdated=O OPEN=K
```

A bot (Qodo/Copilot/SonarCloud) finding is a **live blocker only when `OPEN > 0`** — i.e. the
thread is neither `isResolved` nor `isOutdated`. If the finding is `resolved` or `outdated`
(`OPEN == 0`), it has been acted on and must **not** be cited as an open bug — even though the
REST `pulls/{n}/comments` output still lists the comment. (Regression: configurator #2736 was
mis-bucketed as "2 open Qodo findings" when GraphQL showed 1 resolved + 1 open.) Also read the
*most recent* Qodo "Code Review" summary comment — a newer `Bugs (0)` supersedes older per-thread
findings.

---

## Step 2 — Check Hard Blockers

Before scoring, check for automatic disqualifiers. If any are present, the PR is
**Not Ready** regardless of score.

| Blocker | Source |
|---------|--------|
| PR is a draft | Script: HARD BLOCKERS section |
| Label: `don't merge`, `WIP`, `hold`, `do not merge` | Script: HARD BLOCKERS |
| Merge conflicts present (`mergeable_state: dirty`) | Script: HARD BLOCKERS |
| CI compile/build check failing | Script: CI / BUILD |
| Unresolved "Request Changes" review from any human | Script: CODE REVIEW |

If a hard blocker is present: report it clearly, skip full scoring, label **Not Ready**.

---

## Step 2b — Check Milestone

The script emits a `MILESTONE CHECK` section. It is a **coarse hint only** — do not
trust it as the correct milestone. Verify against the authoritative **Milestone
Criteria & Branch Validation** tables in `.claude/skills/pr-triage/SKILL.md` (the
single source of truth), and flag any mismatch as a warning (not a hard blocker —
wrong milestone does not block code readiness, but should be fixed before merge).

If the milestone is wrong or missing, note it in KEY SIGNALS with `⚠` and include
a suggested action: add the correct milestone label before merging.

---

## Step 3 — Score Each Category

### Category 1 — CI / Build  (max 25 points)

| Condition | Points |
|-----------|--------|
| All checks passing, none pending | 25 |
| All required checks passing (some skipped/neutral) | 20 |
| Checks still running (pending > 0) | 12 |
| 1 non-compile check failing | 8 |
| 2+ non-compile checks failing | 3 |
| Compile/build check failing | → Hard blocker, cap total at 0 |
| No CI checks present (no CI configured) | 10 (neutral) |

Apply **after** blockers: if merge conflicts, subtract 5.

---

### Category 2 — Code Review  (max 30 points)

| Condition | Points |
|-----------|--------|
| 2+ approvals from org members/collaborators | 30 |
| 1 approval from org member/collaborator | 20 |
| 2+ approvals from contributors (non-member) | 16 |
| 1 approval from contributor | 10 |
| Approvals only from first-timers or `NONE` association | 6 |
| No reviews at all | 0 |

Deductions (cumulative, applied to the score above):
- Each open human inline review thread: -3 (max -12)
- Unresolved "Request Changes": → Hard blocker, 0 for this category

**Author trust modifier** — add once, based on PR author's `author_assoc`:

| PR author association | Bonus |
|-----------------------|-------|
| OWNER or MEMBER | +8 |
| COLLABORATOR | +6 |
| CONTRIBUTOR | +3 |
| FIRST_TIME_CONTRIBUTOR, FIRST_TIMER, or NONE | +0 |

This reflects the implicit trust in a known contributor's judgment before external
review accumulates. A COLLABORATOR's unreviewed PR is meaningfully different from
a FIRST_TIMER's. The cap for this category remains 30.

**Note:** `author_assoc` values from most trusted to least:
`OWNER` > `MEMBER` > `COLLABORATOR` > `CONTRIBUTOR` > `FIRST_TIME_CONTRIBUTOR` > `FIRST_TIMER` > `NONE`

---

### Category 3 — Testing Evidence  (max 20 points)

Read the conversation comments in the script output. Look for explicit testing signals:
- Phrases: "tested", "works", "confirmed", "verified", "flight tested", "works on my",
  "tested on", "I can confirm", "flashed and tested"
- Who said it: non-author humans are meaningful; author self-reports count less

| Condition | Points |
|-----------|--------|
| 2+ non-author humans explicitly report testing | 20 |
| 1 non-author human explicitly reports testing | 13 |
| Non-author commented but no explicit test confirmation | 6 |
| Only the author describes testing (in description or comments) | 4 |
| `needs testing` or `Testing Required` label present | 0 (and flag it) |
| No testing evidence anywhere | 0 |

Deductions:
- `needs testing` / `Testing Required` label: -3 from whatever score earned above

---

### Category 4 — Maturity  (max 15 points)

| PR Age | Points |
|--------|--------|
| > 4 weeks old | 15 |
| 2–4 weeks old | 11 |
| 1–2 weeks old | 7 |
| 3–7 days old | 3 |
| < 3 days old | 0 |

Adjustments:
- Last updated > 3 months ago (stale): -5
- Last updated > 6 months ago (very stale): -8 instead
- Multiple review/revision cycles evident (commits > 3, reviews > 1 round): +3
- Commit count is very high (> 15) with no explanation (churn signal): -2

---

### Category 5 — Scope & Risk  (max 10 points)

Lower risk = higher score. This adjusts for how much scrutiny the change needs.

**Base score by size:**

| Lines changed | Files | Points |
|---------------|-------|--------|
| < 50 lines, ≤ 3 files | | 10 |
| 50–200 lines | | 8 |
| 200–500 lines | | 5 |
| 500–1000 lines | | 3 |
| > 1000 lines | | 1 |

**Risk deductions (cumulative):**

| Risk factor | Deduction |
|-------------|-----------|
| Touches core subsystems (PID, nav, IMU, sensors, FC) | -3 |
| Touches MSP protocol files | -3 |
| Touches settings/config defaults | -2 |
| Changes affect multiple unrelated subsystems | -2 |
| No test files included for a non-trivial change | -1 |
| File modified here is also target of a structural change in another open PR | -2 |

**Risk bonuses:**
- Simple fix clearly scoped to one thing: no deductions regardless of lines
- Test files included: +1

**Generated-file line count caveat:**
If the bulk of lines changed are in auto-generated or auto-updated files (JSON dumps,
`docs/Settings.md`, enum refs, checksum files), apply the **next smaller** size tier
and note it. E.g. a PR with 31K lines where 30K are regenerated JSON scores as
"200–500 lines" not "> 1000 lines". State the caveat explicitly in the Scope/Risk row.

**Task-rate note:**
If `src/main/fc/fc_tasks.c` is in the changed files, look up the task's
`desiredPeriod` value and note the actual Hz rate. PRs that move validation logic
from a hot loop (PID ~1000 Hz) to a dedicated task must recalculate numeric
thresholds accordingly — incorrect threshold recalculation is a common bug in
such refactors.

---

## Step 4 — Total Score and Label

Sum all five categories (max 100). Apply any blocker caps.

| Score | Label | Meaning |
|-------|-------|---------|
| Hard blocker present | **Not Ready** | Fix blockers before any other consideration |
| 0–25 | **Not Ready** | Significant gaps in review, testing, or CI |
| 26–45 | **Needs Work** | Promising but missing key signals |
| 46–65 | **Promising** | Good direction; needs more testing or review time |
| 66–80 | **Looking Good** | Most signals positive; minor gaps remain |
| 81–90 | **Merge Candidate** | Strong signals; ready for final maintainer decision |
| 91–100 | **Ready to Merge** | All signals green; low-risk, well-reviewed |

---

## Step 5 — Record the Score  ← MANDATORY after every fresh score

After computing the score, **always** call the record script to save it.
This prevents unnecessary re-scoring for 14 days.

```bash
bash claude/developer/scripts/triage/pr-scorecard-record.sh \
    <REPO> <PR_NUMBER> <SCORE> "<LABEL>" "<TITLE>" "<URL>"
```

Example:
```bash
bash claude/developer/scripts/triage/pr-scorecard-record.sh \
    iNavFlight/inav 11220 74 "Looking Good" \
    "Fix nav waypoint calculation" \
    "https://github.com/iNavFlight/inav/pull/11220"
```

Do NOT call the record script when returning a cache hit — the entry already exists.

---

## Step 6 — Output Format

Present the scorecard in this format:

```
## PR Scorecard: #<NUMBER> — <Title>
<URL>

### Hard Blockers
[None] or list each blocker

### Scores
| Category           | Score | Max | Notes |
|--------------------|-------|-----|-------|
| CI / Build         |    25 |  25 | All checks passing |
| Code Review        |    20 |  30 | 1 member approval; 2 open threads (-6) |
| Testing Evidence   |    13 |  20 | 1 non-author confirmed tested |
| Maturity           |    11 |  15 | 18 days old; 2 revision rounds |
| Scope / Risk       |     5 |  10 | 312 lines; touches navigation subsystem (-3) |
| **TOTAL**          | **74**|**100**| |

### Verdict: Looking Good (74/100)

### Key Positives
- ...

### Key Concerns
- ...

### Unaddressed Bot/Reviewer Issues
- (from check-pr-bots output, list only issues that are genuinely OPEN — `isResolved=false`
  AND `isOutdated=false` via GraphQL `reviewThreads`, not merely "a Qodo comment exists")

### Recommendation
One paragraph: what would move this from its current score to the next tier.
```

---

## Notes

- This skill is for **merge-readiness assessment**, not code correctness review
- Use `/pr-review` or the `inav-code-review` agent for code-quality review
- Use `/pr-triage` for open-PR disposition: deciding the single next-step action
  toward merge (merge, approve, comment, label, set milestone, or skip)
- The `check-pr-bots` agent finds specific bot-flagged issues not captured by this script
- If GitHub API calls hit network sandbox restrictions, ask the user to approve the operation — do not disable the sandbox (`api.github.com` is allowlisted, so failures usually mean something else is wrong)

---

## Related Skills

- **pr-review** — Full code review workflow (checkout, review bot suggestions, build check)
- **pr-triage** — Disposition open PRs: decide the next-step action (merge / approve /
  comment / label / set milestone / skip) and pre-scan recent activity; owns the
  authoritative milestone↔branch tables
- **check-builds** — Detailed CI build status investigation
- **check-pr-docs** — Check if PR includes required documentation updates

## Related Agents

- **check-pr-bots** — Fetch and display all bot review comments on a PR
