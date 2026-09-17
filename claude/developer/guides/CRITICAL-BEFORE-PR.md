# ⚠️ CRITICAL CHECKLIST - Read Before Creating Pull Request

> **Workflow:** steps 9, 11, 12 of 17 → `WORKFLOW.md`.

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

**If you drafted user documentation before coding (see CRITICAL-BEFORE-CODE.md step 3):**

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

**This is step 12 of 17 — see `WORKFLOW.md` (then continue with steps 13–17).**

Quick summary:
1. Wait 3 minutes for bots to analyze
2. Use **check-pr-bots** agent or **/check-builds** skill
3. Review and address bot suggestions
4. **PR to inav-claude?** If you saved reusable tooling or documentation and it may be useful to other users of inav-claude, ask the user if you should share that tooling by making a PR to upstream, https://github.com/sensei-hacker/inav-claude
---

## Self-Improvement: Lessons

Add concise, actionable one-liners (see `guides/README.md` Capture Rubric). State the
rule, not the story.

- **Test all code paths, not just the happy path** — drive every branch of refactored/extracted code; static analysis catches what live testing misses.
- **A unit test closing one race doesn't prove the symptom is gone** — live-test the actual reported symptom end-to-end; it may have a second independent cause.
- **Fix conflicts by pushing to the existing PR's head branch, not a new PR** — a `/pull/NNNN/conflicts` link means fix *that* PR.
- **Ask the user before unsetting `GITHUB_TOKEN`/`GH_TOKEN`, every time** — approval doesn't carry forward; a plain `git push` to your own fork doesn't need it.
- **Pushing to a contributor's fork can 403 even with `maintainer_can_modify: true`** — open a PR against their branch from your fork instead of switching `gh auth`.
- **`gh run rerun` can 403 on your own PR** — retrigger CI by pushing an empty commit: `git commit-tree <branch>^{tree} -p <branch> -m "..."` + `git push origin <sha>:refs/heads/<branch>`.
- **A prior "COMPLETED" report can go stale** — run `gh pr checks <PR>` before trusting it.
- **Use the real generator for generated docs, don't hand-edit** — hand-patching causes spurious diffs on next regen.
- **`gh pr create/view/checks` outside the checkout needs `--repo` and a fork-qualified `--head owner:branch`**.
- **Verify against the live PR before trusting a "not yet posted" note** — check `gh api repos/<owner>/<repo>/issues/<n>/comments`.
- **Removing a debug call site doesn't remove the debug code** — grep for the scaffolding's own symbols; the pre-PR `inav-code-review` pass catches leftovers.
- **SonarCloud gates on ≤3% duplication of *new* configurator code** — factor shared setup into a helper up front rather than discovering the gate after push.

<!-- Add new lessons above this line -->
