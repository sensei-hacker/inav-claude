# GitHub Actions Workflow Gotchas

Non-obvious GitHub Actions semantics discovered while building the RAM/flash
size-diff PR comment feature (`.github/workflows/ci-size-report.yml` and
friends). These cost real debugging time because they contradict a natural
mental model ("the workflow file that ran is the one that's in effect") and
because GitHub's own docs don't call most of them out prominently.

## Which copy of a workflow file actually runs

Different trigger types resolve to different copies of the workflow YAML,
and mixing this up silently breaks a feature without any error:

- **`workflow_run` and `schedule`**: always use the copy of the *listening*
  workflow file on the repository's **default branch** — regardless of which
  branch the triggering event actually happened on. Confirmed via
  `gh repo view <owner>/<repo> --json defaultBranchRef`. A `workflow_run`
  listener you just edited on a feature branch will not take effect until it
  reaches the default branch (`master` here), full stop.
- **`push`, `pull_request`, `workflow_call`**: use the copy of the file on
  whatever ref actually triggered them. This means a multi-branch feature
  (e.g. one that needs to fire on `master`, `release/9.1`, AND
  `maintenance-10.x`) needs its `push`-triggered workflow file *merged
  separately into every one of those branches* — merging it into `master`
  does nothing for pushes to `release/9.1`. Concretely bit us: adding a
  branch to a `push: branches:` list on `master` only affected pushes to
  `master`; `maintenance-10.x` kept running its own stale copy that didn't
  list itself, so pushes there never fired the workflow at all, for weeks.

**Rule of thumb:** for a `workflow_run`-triggered feature split across
multiple files, figure out which of those files are `push`/`workflow_call`
triggered (need to land on every branch that should trigger them) vs.
`workflow_run`/`schedule` triggered (only need to land on the default
branch, no matter what triggered the underlying run).

## `branches:` filters

A `branches:` list containing **only** negative (`!`-prefixed) patterns is
invalid and matches **nothing** — not "everything except the excluded ones."
Per GitHub's docs: "If you define a branch with the `!` character, you must
also define at least one branch without the `!` character. If you only want
to exclude branches, use `branches-ignore` instead." A workflow with only
negative patterns will simply never run via that trigger, with no error
anywhere — confirm via `gh run list --workflow <file> --event push` showing
zero results forever, not via reading the YAML.

## `workflow_call` and `github.event_name`

Inside a workflow invoked via `uses: ./.github/workflows/x.yml`
(`workflow_call`), `github.event_name` reports `'workflow_call'` — **not**
the event that triggered the *calling* workflow (e.g. `'push'`). A step
gated on `if: github.event_name == 'push'` will never run when the workflow
is reached this way, even though `github.ref_name` still correctly reflects
the real branch. Gate on the negative instead when you mean "not a PR build"
(e.g. `if: github.event_name != 'pull_request'`) rather than trying to
enumerate every way the workflow can be legitimately invoked.

## Reusable-workflow (`workflow_call`) runs don't get their own listing

A job that does `uses: ./.github/workflows/x.yml` does **not** produce a
separate standalone `gh run list --workflow x.yml` entry for `x.yml`'s own
name — only the calling workflow shows up. A `workflow_run` listener
targeting the *called* workflow's name will never see these invocations.
Listen for the *calling* workflow's name instead.

## Don't gate on the aggregate `workflow_run.conclusion` for multi-job workflows

`github.event.workflow_run.conclusion` reflects the **whole** triggering
run, including any unrelated jobs in it. If that run also has a job doing
something unrelated (e.g. publishing a separate release using a token that
can expire), that job's failure drags the overall conclusion to `failure`
even when the job you actually care about (and whose artifacts you need)
succeeded completely. This silently starves anything gated on
`conclusion == 'success'` — e.g. a baseline-publishing step that never
fires because a nightly-release-upload job elsewhere in the same run keeps
failing on a stale token. If you only care about one job's outcome, query it
directly instead: `gh api repos/{repo}/actions/runs/{run_id}/jobs --jq
'.jobs[] | select(.name == "<job name>") | .conclusion'` (note reusable-
workflow job names are prefixed `"<caller job name> / <callee job id>"`).

## Two different workflow *files* can share the same `name:`, and `workflow_run` can't tell them apart

A `workflow_run` listener matches on the triggering workflow's `name:` field,
not its file path. Nothing stops two separate `.yml` files from declaring the
identical `name:` — a common intentional pattern for satisfying one required
branch-protection check with either a real, expensive workflow (gated by
`paths:`) or a cheap stub (gated by the exact `paths-ignore:` complement),
so exactly one of them runs per PR. But a `workflow_run` listener gated only
on `if: github.event.workflow_run.name == '<Name>'` fires for *either* one,
even though the stub never produces the jobs/artifacts the listener expects
— it isn't an unrelated failing job dragging down `conclusion` (see the
section above), it's a wholly different, much smaller workflow silently
substituting for the real one, still reporting overall `conclusion: success`.
Found via `gh api repos/{repo}/actions/runs/{run_id} --jq
'{workflow_id, path, name}'` — two runs with the identical reported `name`
had different `path`/`workflow_id`. Disambiguate by checking for the
specific job/artifact you actually need (same fix as the aggregate-conclusion
gotcha), or gate on `workflow_id` directly if the two files' identity is
otherwise indistinguishable.

## Debugging technique

For all of the above, `gh run list --workflow <file> --event <event>`
(showing zero matching runs ever) and `gh run view <id> --json jobs` (showing
per-job conclusions, not just the aggregate) were what actually surfaced the
root cause each time — reading the YAML alone did not reveal any of these
behaviors.
