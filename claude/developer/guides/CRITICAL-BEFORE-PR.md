# ⚠️ CRITICAL CHECKLIST - Read Before Creating Pull Request

**STOP! Complete this checklist before running `gh pr create` or `/create-pr`:**

**Use a task list tool to track each step as you complete it.**

---

## Prerequisites

- ✅ Code written and tested
- ✅ Changes committed (following `CRITICAL-BEFORE-COMMIT.md`)
- ✅ Working on feature branch (NOT master/main/maintenance-*)

---

## 🚨 TESTING IS MANDATORY

**NEVER create a pull request without testing the code.**

### Required Testing Steps

1. **Code Must Compile**
   - Use **inav-builder** agent to verify build succeeds

2. **Code Must Actually Run**
   - Don't just verify it compiles
   - Actually execute and test the functionality
   - Use **test-engineer** agent or SITL for firmware changes

3. **Feature Must Work**
   - Test the specific feature/fix works as expected
   - Verify expected behavior occurs

4. **Test Edge Cases**
   - Try invalid inputs
   - Test with empty data
   - Test boundary conditions

5. **Verify No Regressions**
   - Check that existing functionality still works
   - Run related tests

### If Testing Isn't Possible

If you genuinely cannot test (no hardware, blocked dependencies):
1. **Be explicit in PR description** - state what you couldn't test and why
2. **Request testing** - ask for someone with hardware/setup to test
3. **Never claim "tested" if you didn't actually test**

**Remember:** Untested code can brick expensive flight hardware.

---

## 🚨 CODE REVIEW IS MANDATORY

**Use the `inav-code-review` agent before creating your PR.**

```
Task tool with subagent_type="inav-code-review"
Prompt: "Review changes in [files] - [brief description]"
```

**What the review checks:**
- Coding standards compliance
- Embedded systems safety (ISR safety, memory constraints, stack usage)
- INAV-specific patterns (PG system, scheduler, hardware abstraction)
- Common pitfalls (integer overflow, volatile misuse, race conditions)
- Over-engineering and unnecessary complexity
- Flight-critical code path safety

**Address issues found:**
- Fix CRITICAL issues (must fix before merge)
- Fix IMPORTANT issues (should fix before merge)
- Consider MINOR issues (nice to have)

---

## 🔍 Finalize End-User Documentation

**If you drafted user documentation before coding (see CRITICAL-BEFORE-CODE.md step 4):**

1. **Update the draft** in `claude/developer/workspace/[task-name]/draft-user-docs.md`
   - Verify it matches the actual implementation
   - Update examples and configuration steps if they changed
   - Ensure CLI/settings changes are accurate

2. **Add documentation to the codebase:**
   - Technical docs → `inav/docs/` (committed with PR)
   - End-user guides → `inavwiki/` (separate PR to wiki repo if needed)

3. **Mention in PR description:**
   - List which documentation files were added/updated
   - Or note "Documentation not needed (bug fix/target/refactor)"

---

## Creating the Pull Request

### 1. Review Changes

Determine your base branch from `.claude/skills/git-workflow/SKILL.md` ("Creating
Branches") — it's the single authority and includes any active temporary override.
**Never PR to master.**

Then review (substitute the base branch you actually branched from):
```bash
git status
git diff <base-branch>...HEAD
git log <base-branch>..HEAD
```

### 2. Verify All Changes Committed
```bash
git status  # Should show "nothing to commit, working tree clean"
```

If uncommitted changes exist, commit them first (see `CRITICAL-BEFORE-COMMIT.md`).

### 3. Push to Remote
```bash
git push -u origin branch-name
```

Plain `git push` to origin is safe and approved — never force-push. If the push fails
with "Network is unreachable" or "Connection refused", that's the sandbox blocking the
operation — NOT a network outage. Retry once (`github.com` and `ssh.github.com` are
allowlisted). If the sandbox still blocks this specific push, it is an approved
exception: retry with `dangerouslyDisableSandbox: true`. Do not generalize this to
other operations (see "Sandbox Restrictions" in the git-workflow skill).

### 4. Create PR

**⚠️ First, unset `GITHUB_TOKEN`/`GH_TOKEN` for this step only.** If either is set in the
environment, `gh` always prefers it over the credential from `gh auth login` — and the
`GITHUB_TOKEN` commonly present in this environment is a fine-grained PAT scoped to
specific repos/permissions, which typically lacks `Pull requests: write` on
`iNavFlight/inav` (you're a contributor there, not a maintainer). This produces
`GraphQL: Resource not accessible by personal access token (createPullRequest)`.
The default logged-in `gh auth login` credential (classic PAT, broader `repo`/`workflow`
scope) can create the PR. Unset just for this command, then restore for everything else
(releases, other API calls may rely on the fine-grained PAT's specific grants):

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh pr create --title "Title" --body "Description"
```

Use `/create-pr` skill or the command above.
IMPORTANT **Never open a pull request to the master branch**

**Set the milestone (and any applicable category label, e.g. "New target") when creating the PR** — see "Choosing Labels and Milestone" in `.claude/skills/create-pr/INAV-PR.md` for the current mapping.

**PR Description Requirements:**

**Include:**
- Summary of changes
- Testing performed (be specific - what did you test and what were the results)
- Code review performed (mention using inav-code-review agent)
- Related issue number (if applicable)

**Do NOT mention:**
- Claude or AI assistance
- "Generated by" statements

**Example:**
```markdown
## Summary
Fixes blackbox corruption when no motors are defined in the mixer.

## Changes
- Added motor count validation in blackbox logger
- Return early if motor count is zero

## Testing
- Built SITL target successfully
- Tested with custom mixer with 0 motors - no corruption
- Tested with standard quad mixer - blackbox works normally
- Verified existing blackbox functionality unchanged

## Code Review
Reviewed with inav-code-review agent - no critical issues found.

Fixes #1234
```

If `gh pr create` fails with network errors, that's the sandbox blocking an unapproved
network operation — NOT a network outage. Do not disable the sandbox. Ask the user to
approve the operation or run it manually (see "Sandbox Restrictions" in the git-workflow
skill).

---

## After Creating PR

**This is step 10 in the workflow. See `/check-builds` skill or `check-pr-bots` agent.**

Quick summary:
1. Wait 3 minutes for bots to analyze
2. Use **check-pr-bots** agent or **/check-builds** skill
3. Review and address bot suggestions
4. **PR to inav-claude?** If you saved reusable tooling or documentation and it may be useful to other users of inav-claude, ask the user if you should share that tooling by making a PR to upstream, https://github.com/sensei-hacker/inav-claude
---

## Self-Improvement: Lessons Learned

When you discover something important about PR CREATION AND TESTING that will likely help in future sessions, add it to this section. Only add insights that are:
- **Reusable** - will apply to future PR creation, not one-off situations
- **About PRs/testing** - testing requirements, PR workflow, bot checking, CI/CD
- **Concise** - one line per lesson

Use the Edit tool to append new entries. Format: `- **Brief title**: One-sentence insight`

### Lessons

- **Test all code paths, not just the happy path**: When refactoring code from one module to another, you must drive every branch of the extracted code — not just the path you happened to exercise. In the PR #2603 refactor, the backup path was tested but the entire post-flash restore flow (onFlashComplete, port polling, executeRestore, error dialog) was untested until we actually flashed the hardware FC. Static analysis (Qodo) caught four bugs in those untested paths that live testing missed.
- **Test before push, not after**: All five testing checklist items must be complete before `git push` and `gh pr create` — not during or after PR creation. Creating a PR signals the work is ready for review.
- **Fix conflicts in the existing PR's branch, don't create a duplicate PR**: When asked to fix merge conflicts in an existing PR, resolve them by pushing to that PR's head branch — not by creating a new branch and a new PR. A link to `/pull/NNNN/conflicts` means fix *that* PR.
- **Ask the user for explicit authorization before unsetting `GITHUB_TOKEN`/`GH_TOKEN` for any command, every time** — never do it unilaterally just because a prior turn approved it; approval doesn't carry forward. (This is about `gh pr create` specifically, needing `Pull requests: write`; a plain `git push` to your own `origin` only needs `Contents: write`, which `GITHUB_TOKEN` normally has — don't assume a PR-creation credential failure means push will fail too. The distinct push-permission failure mode is the next lesson, pushing to *someone else's* fork.)
- **A unit test proving one race is closed doesn't prove the symptom is gone**: a bug's reported symptom can have more than one independent root cause producing the identical output. After fixing and unit-testing the race the manager's analysis identified (`fix-cli-tab-msp-polling-leak`), live-testing on real hardware reproduced the same garbage anyway — a second, unrelated bug (a retry loop that never re-checked the same guard condition) was the other contributor. Live-test the actual reported symptom end-to-end before declaring a race-condition fix complete, even when an isolated unit test already passes.
- **Pushing to a contributor's fork can 403 even with `maintainer_can_modify: true`**: resolving conflicts in someone else's PR (e.g. PR #2593) and pushing the fix directly to their fork branch can fail with 403 even though the PR shows maintainer-edit access is enabled and the base-repo permission is admin-level — likely because the active `gh`/git credential is a fine-grained PAT whose scope doesn't cover third-party forks. Don't switch `gh auth` accounts to work around this (too invasive without explicit permission); instead push the resolved branch to `origin` (your own fork) and open a fresh PR. Prefer targeting the contributor's own fork/branch directly (e.g. `gh pr create --repo <contributor>/<repo> --base <their-branch> --head <your-fork>:<branch>`) rather than upstream — opening a PR doesn't need the push access that 403'd, so it sidesteps the problem cleanly, and it lets the contributor review/merge into their own branch first rather than the fix landing upstream without their input. On PR #2448 this was the user's explicit call after conflict resolution ("make a PR into scavanger's repo, so he and I can review") — ask rather than assume upstream is the right target when it's someone else's in-progress branch.
- **`gh run rerun` can 403 even when you own the PR**: "Resource not accessible by personal access token" blocks `gh run rerun <id> --failed`. If the failure looks like transient CI infra (e.g. "Service Unavailable" resolving action download info, not an actual code error), retrigger by pushing an empty commit instead: `git commit-tree <branch>^{tree} -p <branch> -m "..."` then `git push origin <sha>:refs/heads/<branch>`. This needs no local checkout, so it's safe to run even while every tracked repo checkout is locked by another session.
- **A prior "COMPLETED" report doesn't mean the PR is still green**: a completion report can be accurate at send time and still go stale — the CI run it was based on can fail afterward (infra outage, flaky runner) without anyone revisiting the PR. Before treating an old completion report as the end of the story, run `gh pr checks <PR>` and look at current state, not just the report text.
- **Use the actual generator for generated docs, don't hand-edit them**: for files produced by a script (e.g. `docs/development/msp/inav_enums.json`/`inav_enums_ref.md` via `gen_docs.sh`), fixing one stale entry by hand risks a subtle formatting/ordering mismatch from what the generator would produce, which surfaces as a spurious diff the next time someone regenerates. Run the real generator and accept whatever unrelated drift comes with it (the base branch had moved since the docs were last regenerated) rather than hand-patching just the one entry you know is wrong.
- **`gh pr create` from outside the checkout dir needs `--repo` AND a fork-qualified head**: run from the harness root (not inside `inav/`), `gh` won't infer the repo, and an unqualified `--head fix-branch` resolves against the BASE repo — cross-fork PRs fail with "No commits between release/9.1 and fix-branch" until you pass `--head owner:fix-branch` (e.g. `sensei-hacker:fix-branch`). Same for `gh pr view/checks`: always pass `--repo inavflight/inav` outside the checkout.
- **Verify against the live PR before trusting a "not yet posted" status note**: a todo/summary note can claim a fix comment was never posted (so it "survives only in a scratch checkout"), while `gh api repos/<owner>/<repo>/issues/<n>/comments` shows it has been live for weeks — as happened with the pr11756 PLL1/PLL2 fix. Check the PR's actual comment history first; it may turn a "preserve the diff" task into a "nothing to do" task.
- **Removing a debug call site doesn't remove the debug code**: a "clean up debug scaffolding" commit on the oled-auto-detection branch removed the call to a hardware-test-only function but left the 85-line function itself (still exported via the header, zero callers) plus an unrelated I2C address probe left in `detectOledController()` that ran on every boot and triggered a real bus reinit on the expected NAK. The mandatory pre-PR `inav-code-review` pass caught both. After any "remove debug scaffolding" commit, grep for the scaffolding's own name/symbols (not just its call site) to confirm zero remaining references before assuming it's gone.
<!-- Add new lessons above this line -->
