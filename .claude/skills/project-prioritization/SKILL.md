---
description: Prioritize claude/projects/active projects against a release cutoff (e.g. 10.0RC1) using feature/bug/effort/dependency rules
triggers:
  - prioritize projects
  - project priority
  - what needs to be done before rc1
  - before rc1
  - rc1 priority
  - priority list
  - sorted-ray
---

# Project Prioritization Skill

Rank `claude/projects/active/` projects against an upcoming release cutoff (e.g.
INAV 10.0RC1). Not a general "what's important" ranking — specifically answers
"what must happen before this cutoff vs. what can wait."

## Inputs

- The release cutoff being planned for (e.g. "10.0RC1").
- Optionally, a time window (e.g. "projects created in the last two weeks") —
  see "Finding creation date" below for the reliable way to do this.

## Finding creation date reliably

`claude/projects/INDEX.md` already carries a `**Created:** YYYY-MM-DD` line on
every active entry (all 97, verified 2026-09-15) plus a leading status emoji —
this is the reliable source, use it directly rather than touching individual
project directories:

```bash
python3 claude/manager/scripts/project_manager.py list                    # all active, with Created dates
python3 claude/manager/scripts/project_manager.py list TODO               # filter by status
python3 claude/manager/scripts/project_manager.py list --days 14          # created in the last 14 days
python3 claude/manager/scripts/project_manager.py list --since 2026-09-01 --until 2026-09-10
python3 claude/manager/scripts/project_manager.py show <slug>             # single project detail
python3 claude/manager/scripts/project_manager.py stats                   # counts by status/priority
```

`list` results are sorted newest-`Created`-first automatically. Every command
also writes its output to `/tmp/claude/project-manager-<command>.txt` (or a
path given via `--output`/`-o`) in addition to stdout — use the file to
copy-paste output, since the screen's files-changed sidebar makes that
unreliable directly from the terminal.

The status→emoji map (updated 2026-09-15) covers 📋 TODO, 🚧 IN_PROGRESS,
✅ COMPLETE, ⏸️ BACKBURNER, 🚫 BLOCKED, ❌ CANCELLED — `list BLOCKED` works.

`Priority`, `Assignee`, `Created`, and `Directory`/`Location` are now parsed
correctly regardless of position on the line (fixed 2026-09-15 — they used to
only match if they started their own line, which meant `Priority` always came
back `N/A` since `INDEX.md` packs them pipe-separated on one line). A related
parser bug was fixed at the same time: the project-header regex used a
character class over the status emoji, which silently failed to match ⏸️
BACKBURNER headers (two Unicode codepoints — a class can't match them as a
unit) and merged that project's fields into the *previous* project's block,
corrupting its `Created`/`Assignee`/`Priority`. Fixed by matching emoji via
alternation instead of a character class.

**Data-quality note, not a script bug:** `Priority` values in `INDEX.md` are
free text, not a fixed enum — besides `HIGH`/`MEDIUM`/`LOW` you'll see things
like `LOW-MEDIUM`, `LOW/MEDIUM`, and compound values like `HIGH (feature-2) /
MEDIUM (others)`. Don't filter/sort on exact string match; read each value
when it matters for a ranking decision.

Do NOT fall back to filesystem `mtime` on `active/*/summary.md` for dating —
`claude/projects/` is gitignored (no git history either) and bulk workspace
operations (a relocation commit, an INDEX.md sync pass) touch many unrelated
summary.md files at once, bumping mtime without any real change to the
project. This produced false "recently created" hits in practice
(2026-09-15: `fix-geozones-eeprom-save-91` and others showed a 09-13 mtime
from an unrelated relocation commit despite being created back in August —
`INDEX.md`'s own `Created` field was correct throughout). Only use mtime as a
last resort if `INDEX.md`'s field is somehow missing, and treat it strictly
as an upper bound requiring confirmation against the project file's own
`**Created:**` line.

## Before ranking: verify current status, don't trust the file at face value

A project's `summary.md`/`todo.md` can be stale even when a completion report
already exists — e.g. a developer's report gets processed into `INDEX.md` but
the project's own directory never gets updated to match (happened
2026-09-15 with `pr-review-11931-11484-11820`: two of three sub-items were
done and verified, but the project file still read "Status: TODO"). Before
assigning a priority:

1. Check `claude/manager/email/inbox-archive/` for a completion report matching
   the project slug or its PR numbers.
2. If one exists, verify its claims against live GitHub (`gh pr view --json
   state,mergedAt,...`) before trusting it — see the fabrication lesson in
   `.claude/agents/email-manager.md`. A report that checks out against live
   state is fine to act on; don't re-verify by hand what's already confirmed.
3. Update the project's own `summary.md`/`todo.md` to match reality *before*
   ranking it — a project that's actually 2/3 done should not be ranked as if
   all of it were open work.

## Ranking criteria

Apply in roughly this order — earlier factors dominate, effort and blocking
adjust within a tier.

### 1. New features are binary, not gradual

A brand-new feature (not a bug fix, not an existing feature's follow-up) does
not get a "do it in RC2 instead" option — a release branch typically doesn't
take new features after RC1, so the real choice is *this release* or *wait a
full cycle* (e.g. 10.0 → 10.1, ~6 months). Flag any such project explicitly
for a go/no-go decision rather than silently ranking it low — the cost of
silently deferring it is much higher than for a bug fix, and the person
prioritizing may not realize a "medium priority" ranking is actually a de
facto 6-month deferral.

Distinguish from: bug fixes, docs, tooling, investigations, and follow-ups to
already-shipped features — those *can* slip to a later point release or RC2
without the same all-or-nothing cost.

### 2. Bug severity

- **Flight-safety / major correctness bugs** (wrong sign conventions in
  control loops, silent data loss, anything that could cause a crash or
  incorrect in-flight behavior) — high priority for the cutoff.
- **Minor bugs** (cosmetic, narrow edge case, non-flight-affecting) — fine for
  the next point release after the cutoff.
- When unsure whether a bug is flight-relevant, read the project's own
  `summary.md` — most already state the safety implication (e.g. "feeds OSD
  remaining flight time," "silently loses motor remap").

### 3. Blocking / dependency — promotes priority regardless of the item's own size

If a project is a **dependency of other work** — another project's summary
names it as a blocker, or a PR can't merge until it lands — raise its
priority even if the item itself looks small or low-stakes in isolation.
Concretely, check for:

- Another active project's summary.md explicitly says "blocked on
  `<this-slug>`" or "waiting on `#NNNN`."
- A PR that's otherwise ready to merge is being held only by this item (as
  with #11820 blocking configurator #2718 in `pr-review-11931-11484-11820`).
- The project itself says it holds a lock, reserves a resource, or is a
  prerequisite step for something else in flight.

A quick, low-stakes task that's unblocking three other things outranks a
larger standalone task of similar intrinsic importance.

### 4. Effort — quick wins move up within a tier

Among projects of comparable importance, prefer the smaller `Estimated
Effort`/`Estimated Time` first. Don't let effort override severity or the
new-feature rule — it only breaks ties within a tier (e.g. two flight-relevant
bugs, pick the 1-3h one before the 4-8h one; don't use effort to justify
ranking a trivial doc fix above a flight-safety bug).

### 5. Flash/RAM optimization work — lower priority for RC-type cutoffs

Projects whose primary purpose is reducing or managing flash/RAM usage
(`ram-reduction-program`, `document-ram-flash-optimization-practices`, etc.)
don't block a release candidate on correctness grounds — deprioritize them
for the cutoff decision specifically, even if they're otherwise well-scoped
and ready. They're fine for a later point release.

## Output format

Present as tiers, most urgent first, each project with a one-line reason tied
to the criteria above:

```
Tier 1 — flight-relevant, resolve before <cutoff>
Tier 2 — new feature, needs an explicit go/no-go call now
Tier 3 — blocks other in-flight work
Tier 4 — fine to slip past <cutoff>
Tier 5 — explicitly out of scope / time-gated / no relevance to this cutoff
```

Call out Tier 2 items by name in prose, not just in the table — a silent
"medium priority" ranking hides the fact that missing the cutoff means a
~6-month wait.

## Related

- `claude/projects/INDEX.md` — source of truth for active/blocked/backburner projects
- `claude/projects/sorted-ray.txt` — separate flat manually-curated list; not
  auto-generated, needs periodic manual pruning against actual project
  directory locations (see the `projects` skill)
- `.claude/agents/email-manager.md` — fabrication lesson; verify completion
  reports against live GitHub before trusting them
