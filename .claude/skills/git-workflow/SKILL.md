---
description: Common git operations including branch management and status checks
triggers:
  - create branch
  - switch branch
  - git status summary
  - new branch
  - checkout branch
  - git workflow
  - branch status
---

# Git Workflow Helper

Common git operations for working with INAV repositories.

## 🚨 Read Git Guidelines First

**Before any git commit operation, read:** `claude/developer/guides/CRITICAL-BEFORE-COMMIT.md`

This checklist covers:
- Never use `git add -A`
- Human review of commit messages
- Commit message format and best practices
- When to use (and not use) `--amend`
- Hook handling

**Read it now using the Read tool when performing commit operations.**

---

## ⚠️ CRITICAL: Git Safety Rules ⚠️

### Questions Are Not Commands

**When the user asks a question, ONLY answer the question.**
- Do NOT take any action (delete, push, modify, etc.)
- Do NOT "fix" things while explaining them
- Do NOT assume you know what action should follow
- WAIT for explicit instructions before doing anything

### Never Destroy Evidence During Investigation

**When investigating a problem or answering questions about repository state:**
- Do NOT delete branches, tags, or commits
- Do NOT push, force-push, or overwrite anything
- Do NOT "clean up" anything
- PRESERVE the current state so it can be examined
- The evidence is needed to understand and fix the problem

### Never Alter the Public Record

**Once something is pushed to a public/shared repository:**
- It becomes part of the permanent record
- Other developers around the world may have fetched it
- Altering it (force push, amend+push) creates problems for EVERYONE
- It breaks other developers' local repositories
- It corrupts CI/CD pipelines, PR references, and git history
- The damage is often irreversible and far-reaching

**Force pushing after a PR is merged corrupts GitHub's PR display:**
- GitHub's "Files changed" tab shows the diff between base and the CURRENT branch head
- If you force push after merge, the PR now shows DIFFERENT code than what was actually merged
- Example: PR #2496 actually merged an `afterCopy` hook, but after force push GitHub shows `postPackage`
- Anyone reviewing the PR history sees FALSE information about what was merged
- This makes debugging, auditing, and understanding project history impossible
- The merge commit in master contains the ORIGINAL code, but the PR display shows the AMENDED code
- This is a permanent corruption of the project's historical record

### Force Push Rules

**NEVER, EVER force push to master, main, or any shared branch:**

```bash
# ❌ ABSOLUTELY FORBIDDEN - NEVER DO THIS:
git push -f origin master
git push --force origin main
git push -f upstream master

# These commands DESTROY other people's work permanently
# They rewrite history and can cause unrecoverable data loss
```

**If a regular push is rejected:**
1. STOP immediately
2. Do `git pull` to merge remote changes
3. Or ask the user what to do
4. NEVER use force push to "fix" it

**Force push is ONLY acceptable:**
- On your own feature branches that nobody else uses
- When explicitly requested by the user
- NEVER on master/main/shared branches under any circumstances

## 🔒 Sandbox Restrictions

**Claude Code runs in a sandbox that restricts network access:**

- Git operations requiring network (fetch, pull, push) may fail with "Network is unreachable" or "Connection refused"
- This is NOT a network outage - it's the sandbox blocking unapproved network operations
- SSH to github.com (port 22) is in the allowed list but may require permission prompts
- If git fetch/pull/push fails, the user needs to approve the network operation or run it manually

**When you see network errors:**
1. Don't assume the network is down
2. Recognize it as a sandbox restriction
3. Ask the user if they want to approve the operation or handle it manually
4. The user can run git commands directly (unsandboxed) if needed

**One approved exception:** plain `git push` to origin (NEVER force-push). `github.com`
and `ssh.github.com` are in the sandbox allowlist, so pushes normally work sandboxed;
if the sandbox still blocks a push, retrying that one command with
`dangerouslyDisableSandbox: true` is approved. Do not generalize this to any other
operation — everything else follows the recognize-and-ask steps above.

## Repository Structure

The INAV project consists of **four standalone repositories**:
- `inav/` - Flight controller firmware (C/C99)
- `inav-configurator/` - Desktop GUI (JavaScript/Electron)
- `inavwiki/` - Documentation wiki (Markdown)
- `iNavFlight.github.io/` - Docusaurus documentation site (primary end-user docs)

Each repository has its own git history and must be managed independently.

### Docs Site Versioning (`iNavFlight.github.io/`)

The docs site (Docusaurus) versions its content by release. Discoverable
pointers so future projects don't rediscover it:

- **Current (unreleased) docs** → `iNavFlight.github.io/docs/`
- **Per-release snapshots** → `iNavFlight.github.io/versioned_docs/version-X.Y.Z/` (one dir per released INAV version)
- **Per-release sidebars** → `iNavFlight.github.io/versioned_sidebars/`
- **Version list** → `iNavFlight.github.io/versions.json` (newest first)

Adding a new release = snapshot `docs/` into `versioned_docs/version-X.Y.Z/` +
`versioned_sidebars/`, then add the version to `versions.json`. See the
`markdown2mdx-complete-pipeline` project for the conversion/versioning tooling.

## Creating Branches

### 🚨 CRITICAL: Always Specify Base Branch When Creating Branches — This Is the Single Authority

**This section is the single authoritative source for the {repo, change-type} → base-branch
decision.** Every other guide, skill, and README that mentions a base branch should point
here (or at the script below) instead of repeating the table. If you find a stale copy
elsewhere, that's a bug — fix it to be a pointer.

**NEVER create a branch without specifying the base branch** — branching from current HEAD
may include unrelated commits, WIP changes, or simply the wrong base, contaminating the PR.

### Use the script (preferred)

```bash
claude/developer/scripts/git/new-branch.sh <repo> <bugfix|feature|breaking> <branch-name> [--dry-run]
# repo: inav | inav-configurator | PrivacyLRS
```

It looks up the base branch below, refuses to run on a dirty tree, fetches the correct
remote, prints its reasoning, and creates the branch. Use `--dry-run` to preview first.

### Base-branch decision table

| Repo | Remote | Change type | Base branch | Notes |
|------|--------|-------------|-------------|-------|
| PrivacyLRS | `origin` | any | `secure_01` | Separate fork/derivative project |
| inav | `upstream` | bugfix | `release/9.1` | **TEMPORARY OVERRIDE** — `maintenance-9.x` is damaged. REVIEW-BY 2027-02: verify repair before reverting to `maintenance-9.x` |
| inav | `upstream` | feature | `maintenance-10.x` | Same temporary override as above |
| inav | `upstream` | breaking | `maintenance-10.x` | Matches the normal (non-override) rule |
| inav-configurator | `upstream` | bugfix | `maintenance-9.x` | **NOT** affected by the inav override — configurator's `maintenance-9.x` is fine |
| inav-configurator | `upstream` | feature | `maintenance-9.x` | Not affected by the inav override |
| inav-configurator | `upstream` | breaking | `maintenance-10.x` | MSP protocol / settings structure changes |
| iNavFlight.github.io | `upstream` | any | `master` | No maintenance branches — single default branch, feature-branch PRs |

**NEVER target PRs to master** - it receives merges only (maintenance-9.x → master → maintenance-10.x). This does not apply to `iNavFlight.github.io`, whose default branch *is* `master`.

### Manual fallback (only if the script can't be used)

```bash
git fetch <remote>
git checkout -b <branch-name> <remote>/<base-branch>
```
Substitute `<remote>` and `<base-branch>` from the table above. Then:
```bash
git push -u origin <branch-name>
```

### Create Branch from Specific Commit

```bash
# Create branch from specific commit
git checkout -b bugfix-123 <commit-hash>

# Or from a tag
git checkout -b new-feature v9.0.0
```

### Branch Naming Conventions

**PrivacyLRS:**
- Use flat naming WITHOUT slashes
- ✅ Good: `encryption-test-suite`, `fix-counter-sync`, `add-telemetry`
- ❌ Bad: `feature/encryption-tests`, `security/fixes`

**INAV:**
- Use kebab-case with descriptive names
- ✅ Good: `fix-telemetry-bug`, `feature-battery-limit`, `update-sitl-binary`
- Bug fixes: `fix-<description>`
- Features: `feature-<description>`

## Switching Branches

### Safe Branch Switching

Always check for uncommitted changes before switching:

```bash
# Check status first
git status

# If clean, switch branches
git checkout <branch-name>

# Or use switch
git switch <branch-name>
```

### Handling Uncommitted Changes

If you have uncommitted changes:

**Option 1: Stash changes**
```bash
git stash save "WIP: description of changes"
git checkout <branch-name>

# Later, restore changes
git stash pop
```

**Option 2: Commit changes**
```bash
git add .
git commit -m "WIP: save progress"
git checkout <branch-name>
```

**Option 3: Discard changes (careful!)**
```bash
git checkout -- .  # Discard all changes
git checkout <branch-name>
```

## Git Status Summary

### Quick Status Check

```bash
# Basic status
git status

# Short format
git status -s

# Show branch and tracking info
git status -sb
```

### Comprehensive Status

Get a complete picture of your repository:

```bash
# Branch information
echo "=== Current Branch ==="
git branch --show-current

# Status
echo "=== Working Tree Status ==="
git status

# Commits ahead/behind remote
echo "=== Remote Tracking ==="
git status -sb | head -1

# Recent commits
echo "=== Recent Commits ==="
git log --oneline -5

# Staged changes
echo "=== Staged Changes ==="
git diff --cached --stat

# Unstaged changes
echo "=== Unstaged Changes ==="
git diff --stat
```

## Branch Management

### List Branches

```bash
# Local branches
git branch

# Remote branches
git branch -r

# All branches with last commit
git branch -v

# All branches including remote
git branch -a
```

### Delete Branches

```bash
# Delete local branch (safe - only if merged)
git branch -d <branch-name>

# Force delete local branch
git branch -D <branch-name>

# Delete remote branch
git push origin --delete <branch-name>
```

### Rename Branch

```bash
# Rename current branch
git branch -m <new-name>

# Rename specific branch
git branch -m <old-name> <new-name>

# Update remote
git push origin -u <new-name>
git push origin --delete <old-name>
```

## Checking Branch Status

### Compare with Remote

```bash
# Fetch latest from remote
git fetch origin

# Check if branch is ahead/behind
git status

# See commits not pushed
git log origin/<branch-name>..<branch-name>

# See commits not pulled
git log <branch-name>..origin/<branch-name>
```

### Compare with Other Branches

```bash
# See commits in current branch not in master
git log master..HEAD

# See files changed between branches
git diff master..HEAD --stat

# Show branch divergence
git log --oneline --graph --all --decorate -10
```

## Working with Multiple Repositories

Since `inav/`, `inav-configurator/`, `inavwiki/`, and `iNavFlight.github.io/` are standalone repos:

### Check Status Across All Repos

```bash
# From project root
for repo in inav inav-configurator inavwiki iNavFlight.github.io; do
  if [ -d "$repo" ]; then
    echo "=== $repo ==="
    cd $repo
    git status -sb
    cd ..
    echo ""
  fi
done
```

### Create Matching Branches

If working on a feature that spans multiple repos, create each from its own correct
base — see the decision table above (inavwiki and `iNavFlight.github.io/` have no
maintenance branches; branch them from their default branch):

```bash
claude/developer/scripts/git/new-branch.sh inav <bugfix|feature|breaking> my-feature
claude/developer/scripts/git/new-branch.sh inav-configurator <bugfix|feature|breaking> my-feature
cd inavwiki && git checkout -b my-feature && git push -u origin my-feature
cd iNavFlight.github.io && git checkout -b my-feature && git push -u origin my-feature
```

### Updating the Harness Repo Itself

The root `inavflight/` repo (`claude/` and `.claude/`) is its own git repo. A
`SessionStart` hook (`.claude/hooks/check-framework-update.sh`) asks — roughly once a
month — whether to pull it. If you say yes, just run the pull the hook's own message
names: `origin` for this repo's own setup, or `upstream` if this checkout is a fork with
an `upstream` remote configured (that's where real framework updates land in that case;
`origin` would just be your own fork).

```bash
git pull --ff-only <remote> master
```

`--ff-only` refuses to create a merge commit if local and remote have diverged — if it
fails, stop and check `git status`/`git log` before doing anything else, rather than
force-merging over local changes. This is a single human-confirmed action each time the
hook asks; no automated enforcement is needed beyond that.

## Common Workflows

### Starting New Work

See "Creating Branches" above — use `new-branch.sh` or the manual fallback with the
correct base branch from the decision table. **Do not branch from `master`**; it's a
merge-only mirror, not a base.

### Updating a Branch with Its Base

Rebase or merge against the **same base branch you created from** (from the decision
table above) — not `master`:

```bash
git checkout my-feature
git fetch <remote>                   # upstream for inav/inav-configurator, origin for PrivacyLRS
git rebase <remote>/<base-branch>    # or: git merge <remote>/<base-branch>
```

### Switching Between Tasks

```bash
# Save current work
git stash save "WIP: current task description"

# Switch to other branch
git checkout other-branch

# Work on other task...

# Return to original branch
git checkout original-branch
git stash pop
```

## Troubleshooting

### Branch is Behind Remote

```bash
# Pull latest changes
git pull origin <branch-name>

# Or fetch and merge manually
git fetch origin
git merge origin/<branch-name>
```

### Branch Has Diverged

```bash
# View divergence
git status

# Option 1: Rebase your changes
git pull --rebase origin <branch-name>

# Option 2: Merge
git pull origin <branch-name>
```

### Accidentally Committed to Wrong Branch

```bash
# Move last commit to new branch
git checkout -b correct-branch
git checkout wrong-branch
git reset --hard HEAD~1
git checkout correct-branch
```

## Resources

- **Git basics:** `git --help`
- **Project workflow:** See `claude/manager/README.md` and `claude/developer/README.md`

---

## Related Skills

- **create-pr** - Create pull requests after committing changes
- **pr-review** - Review pull requests and check out PR branches
- **check-builds** - Check CI build status for branches and PRs
- **start-task** - Begin tasks with proper branch setup
- **finish-task** - Complete tasks with commits and cleanup
