# PR-Triage Skills Consolidation — Resume Plan

**Created:** 2026-09-19 (manager session, during PR triage)
**Status:** ✅ COMPLETE 2026-09-19

**Done:**
- Wrote one combined 3-mode `.claude/skills/pr-triage/SKILL.md` (activity / milestone / disposition); deleted `.claude/skills/pr-scorecard-triage/`.
- Unified skip files → `claude/local-data/triage/skip-scorecard-*.txt` (skill + `scorecard-triage.sh` header + `.claude/hooks/tool_permissions_bash.yaml` echo rule).
- Fixed `/tmp` → `./tmp` in `fetch-activity-prs.sh`, `fetch-next-pr.sh`, `scorecard-triage.sh` (cache paths + header examples), and moved their `mkdir` before the `--output` redirect so they self-create the dir. (`tag-maintenance-milestone.py` had no `/tmp` to fix.)
- Single source of truth: kept pr-triage's override-aware branch→milestone tables as a shared reference; removed the stale "April 2026" table (it lived in the deleted scorecard skill); disposition mode now references the shared tables.
- Generalized `tag-maintenance-milestone.py` with `--base` / `--milestone` args.

**Left as-is (out of scope / note):**
- `pr-scorecard.sh`'s `MILESTONE CHECK` is a coarse hint (still mentions "10.1"); disposition mode now instructs to confirm against the shared tables instead.
- Other `/tmp/claude` uses in unrelated tooling (SITL scripts, `project_manager.py`, historical docs/emails) are not part of this triage consolidation.

---

## Goal

Fold `pr-triage` and `pr-scorecard-triage` into **one** "open-PR triage" skill,
and keep the genuinely-distinct process — **marking milestones on already-MERGED
PRs** — as its own small skill/step (already tooled as
`claude/developer/scripts/triage/tag-maintenance-milestone.py`).

## Why

The two skills overlap heavily (both enumerate open PRs and produce
skip/comment/label/milestone dispositions). They differ only in ordering,
scoring, and whether they actually merge. The one thing neither open-PR skill
does — retroactive milestone backfill on merged PRs — is already handled by
`tag-maintenance-milestone.py`.

## Current files

- `.claude/skills/pr-triage/SKILL.md` — 2 modes: **activity review** (Mode 1) + **milestone triage** (Mode 2). Holds the authoritative branch→milestone table (release/9.1 override, configurator breaking→maintenance-10.x, etc.). Persistent skip files `claude/local-data/triage/skip-*.txt`.
- `.claude/skills/pr-scorecard-triage/SKILL.md` — scored disposition (0–100) → merge/approve/comment/label. Ephemeral `/tmp/claude/skip-scorecard-*.txt`. Stale "milestone policy (April 2026)" 2-row table.
- `.claude/skills/pr-scorecard/SKILL.md` — single-PR scorecard. **Keep.**
- `.claude/skills/pr-review/SKILL.md` — full code review (checkout/build/bots). **Keep, distinct.**
- Scripts: `claude/developer/scripts/triage/{fetch-activity-prs.sh, fetch-next-pr.sh, update-pr.sh, scorecard-triage.sh, pr-scorecard.sh, pr-scorecard-record.sh, tag-maintenance-milestone.py}`.

---

## Steps (do in order)

1. **Write one combined `pr-triage/SKILL.md`** with three modes:
   - `activity` — what needs attention now (NEEDS-REVIEW / NO-COMMENT / WAITING / STALE), most-recently-updated.
   - `milestone` — branch→milestone correctness, oldest-first (today's pr-triage Mode 2).
   - `disposition` — scorecard → merge/approve/comment/label, highest-score-first (today's pr-scorecard-triage).
   Then **delete `pr-scorecard-triage/SKILL.md`** (or leave a one-line pointer to pr-triage).

2. **Unify skip files.** Point `scorecard-triage.sh` and the disposition mode at
   `claude/local-data/triage/skip-scorecard-*.txt` (persistent), **not** `/tmp/claude`.

3. **Fix `/tmp` → `./tmp`.** `scorecard-triage.sh` and `tag-maintenance-milestone.py`
   (its docs/examples) still use `/tmp/claude`. Replace with `./tmp/claude`
   (see CLAUDE.md "Critical Environment Facts" + pr-triage SKILL.md note).
   Reminder: the scripts redirect to `--output` *before* their own `mkdir`, so
   `mkdir -p ./tmp/claude` must run first.

4. **Single source of truth for branch→milestone table.** Keep pr-triage's
   override-aware table as authoritative; delete the stale "milestone policy
   (April 2026)" table in pr-scorecard-triage and reference pr-triage from the
   disposition mode instead.

5. **Generalize `tag-maintenance-milestone.py`** to accept `--base` and
   `--milestone` args (currently hardcoded `maintenance-10.x` → `10.0`), so it
   works for future release cycles.

## Other drift to reconcile while editing

- `fetch-activity-prs.sh` sort bug **ALREADY FIXED 2026-09-19**: the
  list-issue-comments endpoint ignores `sort=created&direction=desc`; added
  `| sort_by(.date) | reverse` in jq (matches reviews handling).
- `/tmp` vs `./tmp` is documented in `CLAUDE.md` (auto-loaded) + `pr-triage`
  SKILL.md + `TOOL-LOCATIONS.md` — but **not yet** in the scorecard skill/scripts.

---

## Current PR-triage session state (to resume after compaction)

- Window: PRs **updated in last 9 days** (cutoff `2026-09-10`).
- Skip files updated 2026-09-19 (firmware↔configurator cross-referenced):
  - `skip-inav.txt` → added **#11947** (SRXL2 ESC, pairs configurator #2770, awaits @RobertoD91) and **#11933** (second-gyro blackbox, pairs #2768, on hold flight test).
  - `skip-configurator.txt` → added **#2770** (pairs #11947); **#2768** already present (pairs #11933).
- Full one-at-a-time analyses done: inav #11905 (regression → "Fix needed - don't merge"), #11837 (ours, MZTC), #11969 (TPA refactor), #11947 (SRXL2); configurator #2768, #2770.
- Skipped/on-hold: #11905/#11837/#11969 (needs discussion/work), #2738/#2751/#2745 (pending author), #2717 + #11972 (merged), #11968 (closed).
- **Next up when resuming:** the user's chosen "full analysis one-at-a-time" set is configurator **#2774** (MrScothh), **#2750, #2743** (Raffi1202). Start with **#2774**.
