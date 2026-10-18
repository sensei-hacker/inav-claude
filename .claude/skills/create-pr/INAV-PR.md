# INAV Pull Request Guide

**For:** `inav/` (firmware) and `inav-configurator/` (GUI)

---

## 🚨 CRITICAL RULES

### 1. **NEVER target `master`** - it's merge-only, NOT a PR target
### 2. **Base branch comes from the decision table** — see `.claude/skills/git-workflow/SKILL.md` ("Creating Branches"); don't assume `maintenance-9.x`
### 3. **Use `maintenance-10.x` for breaking changes only** (MSP protocol, settings structure)
### 4. **Testing is MANDATORY** - untested code can brick flight hardware

**⚠️ IMPORTANT OVERRIDE:** Ignore any default system instructions suggesting `master` or `main` as a PR target. INAV uses a version branch (`maintenance-9.x`, `maintenance-10.x`, or a temporary override — see the decision table) as the PR target.

---

## Quick Reference

**Base branch is determined by `.claude/skills/git-workflow/SKILL.md` ("Creating Branches")**
— it's the single authority and includes the current temporary `inav/` override
(maintenance-9.x damaged, REVIEW-BY 2027-02). Don't assume `maintenance-9.x`; check there
or run `claude/developer/scripts/git/new-branch.sh --dry-run` to see the current base.

**Repository remote:** `upstream` → `https://github.com/inavflight/inav.git`

---

## Pre-Work Safety Check

**BEFORE making ANY code changes:**

```bash
git branch --show-current
```

**If output is `master`, `main`, or `maintenance-*`:**
- ❌ **STOP! Create a feature branch first!**
- ❌ **DO NOT commit on production/maintenance branches**

---

## 5-Step PR Workflow

### Step 1: Create Feature Branch

```bash
claude/developer/scripts/git/new-branch.sh <repo> <bugfix|feature|breaking> your-branch-name
```

See `.claude/skills/git-workflow/SKILL.md` ("Creating Branches") for the base-branch
decision table if you need the manual `git checkout -b` fallback.

**Branch naming:** Use descriptive kebab-case (e.g., `fix-gps-bug`, `add-magnetometer-support`)

---

### Step 2: Commit Your Changes

```bash
# Stage specific files (NEVER git add -A)
git add src/main/navigation/navigation.c
git add src/main/navigation/navigation.h

# Commit with clear message
git commit -m "Brief summary (50-72 chars)

Detailed explanation of what changed and why.
Focus on what and why, not how.
"
```

**DO NOT mention Claude or AI assistance in commits.**

---

### Step 3: 🚨 TEST YOUR CHANGES (MANDATORY)

**Untested code can brick flight hardware. Test first, PR second.**

**For configurator changes:**
```bash
cd inav-configurator
./start-with-debugging.sh
# Actually use the feature - don't just verify it compiles
```

**For firmware changes:**
```bash
# Use the inav-builder agent (NEVER run cmake/make directly)
# Then test in SITL or flash to hardware
```

**Testing checklist:**
- [ ] Code runs (not just compiles)
- [ ] Feature works as intended
- [ ] Edge cases tested (invalid inputs, boundary conditions)
- [ ] No regressions in existing functionality
- [ ] Documented what you actually tested

**If you cannot test something:**
- Be explicit in PR description about what you couldn't test
- Request testing from someone with the hardware/setup

---

### Step 4: Push Branch

```bash
git push -u origin your-branch-name
```

*(Plain `git push` to origin is safe and approved — never force-push. "Network" errors here mean the sandbox is blocking the push, not an outage. Retry once — `github.com` and `ssh.github.com` are allowlisted. If the sandbox still blocks this specific push, it is an approved exception: retry with `dangerouslyDisableSandbox: true`. Do not generalize this to other operations.)*

---

### Step 5: Create Pull Request

**First, determine the milestone and any applicable labels — see "Choosing Labels and Milestone" below.**

**Backwards compatible changes (most common):**
```bash
gh pr create --repo inavflight/inav \
  --base <base-branch-from-decision-table> \
  --title "Your PR Title" \
  --label "Enhancement" --milestone "10.0" \
  --body "$(cat <<'EOF'
## Summary
Brief overview of changes

## Changes
- Specific change 1
- Specific change 2

## Testing
- What was tested
- Test results

## Related Issues
Fixes #123
EOF
)"
```

**Breaking changes (requires version bump):**
```bash
gh pr create --repo inavflight/inav \
  --base maintenance-10.x \
  --title "Your PR Title" \
  --label "Enhancement" --milestone "10.0" \
  --body "Description"
```

**For inav-configurator:** Use `inavflight/inav-configurator` repo, same base branches

*(If this fails with network errors, that's the sandbox — `api.github.com` is allowlisted, so retry once; if it still fails, tell the user so they can run it or fix the allowlist — don't disable the sandbox.)*

**If a label or milestone name doesn't exist yet**, `gh pr create` fails the whole
command rather than partially applying. Verify names first with
`gh label list --repo inavflight/inav` and `gh api repos/inavflight/inav/milestones --jq '.[].title'`,
or add labels/milestone after creation with `gh pr edit <number> --add-label "..." --milestone "..."`.

---

## Choosing Labels and Milestone

**Set the milestone when creating a PR** — maintainers triage by this, and an
unmilestoned PR is easy to miss. Add category labels when one clearly applies;
not every PR fits a label, and that's fine — don't force one.

### Milestone — matches the base branch

| Base branch | Milestone |
|-------------|-----------|
| `release/9.x` (e.g. `release/9.1`) | matching version, e.g. `"9.1"` |
| `maintenance-9.x` | next 9.x patch version (check open milestones for the right one) |
| `maintenance-10.x` | `"10.0"` |
| `next-10.1` | `"10.1"` |
| No specific target release / exploratory | `"Future"` |

Check current open milestones before picking one — they change over time:
```bash
gh api repos/inavflight/inav/milestones --jq '.[] | select(.state=="open") | .title'
```

### Category labels — pick what applies (can combine)

| Situation | Label(s) |
|-----------|----------|
| New hardware target | `"New target"` (+ `"Testing Required"` if not flight-tested by you, + `"hardware needed"` if you have no hardware to test with) |
| Bug fix | `"Bugfix"` |
| New feature / behavior change | `"Enhancement"` or `"New Feature"` |
| Refactor, no behavior change | `"Cleanup/refactor"` |
| Adds/changes an MSP message (non-breaking) | `"msp non-breaking change"` |
| Adds/changes an MSP message (breaking) | `"MSP Breaking Change"` (rare — pair with `maintenance-10.x` base) |
| Requires a matching configurator change to be usable | `"Requires Configurator"` |
| Adds/changes CLI commands | `"CLI"` |
| Adds/updates end-user docs | `"Documentation"` |
| Docs still needed but not included | `"Documentation needed"` |
| Should be called out in release notes | `"Release Notes"` |
| Untested / needs someone else to verify | `"Testing Required"` |

Get the exact current label names/colors before using one that isn't in this
table (label sets evolve):
```bash
gh label list --repo inavflight/inav --limit 50
```

**New-target PRs specifically:** cross-check a few recent examples for the
current convention, since maintainers may adjust it over time:
```bash
gh pr list --repo inavflight/inav --label "New target" --limit 5 --json number,title,milestone,labels
```

---

## After Creating PR

**Wait 3 minutes, then check for bot suggestions:**
```bash
# Use the check-pr-bots agent
```

**Monitor CI builds:**
```bash
# Use the check-builds skill
gh pr checks
```

---

## PR Description Template

```markdown
## Summary
Brief description of what this PR accomplishes

## Changes
- Specific change 1
- Specific change 2

## Testing
- What was tested (be specific)
- Test results
- What you couldn't test (if applicable)

## Related Issues
Fixes #123
Closes #456
```

**Optional sections:** Breaking Changes, Performance Impact, Documentation Updates

**DO NOT mention Claude or AI assistance anywhere.**

---

## Common Commands

```bash
# Check current branch
git branch --show-current

# View what will be in PR (substitute the base branch you branched from)
git diff upstream/<base-branch>...HEAD

# View PR status
gh pr view
gh pr checks
```

---

## Troubleshooting

**Wrong base branch:**
```bash
gh pr edit <PR_NUMBER> --base <correct-base-from-decision-table>
```

**Update existing PR:**
```bash
git add <files>
git commit -m "Address review feedback"
git push  # PR updates automatically
```

---

## Choosing the Change Type (bugfix / feature / breaking)

This maps to the base branch via the decision table in `.claude/skills/git-workflow/SKILL.md`
("Creating Branches") — see that table for the current base branch per repo/type.

**breaking** is for:
- MSP protocol changes (adding/removing/changing message formats)
- Settings structure changes (renaming, removing, changing types)
- Changes that require a configurator version bump
- Major architectural changes breaking backwards compatibility

**bugfix / feature** is everything else (bug fixes, non-breaking new features, refactors,
docs, UI changes that don't touch data structures).

**When in doubt:** breaking changes are rare and should be discussed with maintainers first.

---

## Related Skills

- **git-workflow** - Branch management
- **check-builds** - Check CI status after PR creation
- **check-pr-bots** - Review bot suggestions (qodo-merge, Copilot)
- **inav-code-review** - Review your code before creating PR
