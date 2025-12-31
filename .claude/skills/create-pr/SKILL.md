---
description: Create pull requests for PrivacyLRS and INAV projects
triggers:
  - create pr
  - make pr
  - create pull request
  - submit pr
  - new pull request
---

# Pull Request Creation Workflow

Complete workflow for creating pull requests for PrivacyLRS and INAV projects.

## Important: Repository-Specific PR Targets

### PrivacyLRS
**PrivacyLRS is a separate fork/derivative project.**

```
Repository: sensei-hacker/PrivacyLRS (origin)
Remote: origin → ssh://git@github.com/sensei-hacker/PrivacyLRS
Base Branch: secure_01 (NOT master)
```

**PRs for PrivacyLRS work go to origin (sensei-hacker/PrivacyLRS), NOT upstream ExpressLRS.**

**IMPORTANT:** For PrivacyLRS, pull requests should branch from and target `secure_01`, NOT `master`. The secure_01 branch is the main development branch for PrivacyLRS.

### INAV (inav and inav-configurator)
```
Repository: inavflight/inav (upstream)
Remote: upstream → https://github.com/inavflight/inav.git
```

**PRs for INAV work go to upstream (inavflight/inav).**

**IMPORTANT:** For both `inav` and `inav-configurator` repositories:
- **Use `maintenance-9.x`** for changes that maintain compatibility between firmware and configurator
- **Use `maintenance-10.x`** for breaking changes (MSP protocol changes, incompatible with 9.x)
- **NEVER use `master`** unless specifically instructed to do so by the user
- The master branch is NOT for code development - only docs and CI/CD workflows

---

## 🚨 CRITICAL: NEVER WORK ON PRODUCTION BRANCHES

### ⚠️ MANDATORY Pre-Work Check (DO THIS FIRST - EVERY TIME)

**BEFORE making ANY code changes:**

1. **Check what branch you're on:**
   ```bash
   git branch --show-current
   ```

2. **If the output is `secure_01`, `master`, or `main`:**
   - ❌ **STOP! DO NOT MAKE ANY CHANGES!**
   - ❌ **DO NOT COMMIT!**
   - ❌ **DO NOT PUSH!**
   - ✅ **Create a feature branch first** (see Step 1 below)

3. **If you've already made changes or commits on a production branch:**
   - 🚨 **STOP IMMEDIATELY**
   - 🚨 **DO NOT PUSH**
   - 🚨 **Ask the user how to proceed**
   - Options: revert commit, create branch from current commit, force-reset

### Why This Matters

- Production branches (secure_01, master, main) should only be updated via PRs
- Direct commits bypass code review
- Direct pushes pollute the git history with mistakes
- You cannot undo a pushed commit (force push is absolutely forbidden)
- **This is a CRITICAL workflow violation**

---

## Standard PR Creation Process

### Step 1: Create a Feature Branch

**IMPORTANT:** Always work on a feature branch, NEVER directly on the base branch (secure_01 for PrivacyLRS, maintenance-9.x for INAV). Feature branches allow for proper PR review workflow.

**First, verify you're not already on a production branch:**
```bash
git branch --show-current
# Output should NOT be: secure_01, master, or main
# If it is, you're in the wrong place - create a feature branch!
```

**Branch Naming Conventions:**
- **PrivacyLRS:** Use descriptive names WITHOUT slashes (e.g., `encryption-test-suite`, `fix-counter-sync`)
- **INAV:** Follow project conventions (typically kebab-case)
- Avoid: `feature/name` or `bugfix/name` style with slashes for PrivacyLRS

**For PrivacyLRS:**
```bash
# Create branch from secure_01 (the base branch)
git checkout -b your-branch-name secure_01

# Or if you're already on secure_01
git checkout -b your-branch-name

# Examples of good branch names:
# - encryption-test-suite
# - fix-counter-sync
# - add-telemetry-support
```

**For INAV/inav-configurator:**
```bash
# Create branch from maintenance-9.x (backwards compatible changes)
git checkout -b your-branch-name upstream/maintenance-9.x

# Or for breaking changes requiring version bump
git checkout -b your-branch-name upstream/maintenance-10.x

```

### Step 2: Make Changes and Commit

```bash
# Stage specific files (NEVER use git add -A)
git add <file1> <file2>

# Commit with concise descriptive message
# Use gedit for human review of commit message
GIT_EDITOR="gedit" git commit --edit -m "Brief summary

Detailed description of what changed and why.

- Specific change 1
- Specific change 2
"
```

**Commit Message Guidelines:**
- First line: Brief summary (50-72 chars)
- Blank line
- Concise explanation
- DO NOT mention Claude or AI assistance. Avoid writing "Generated with [Claude Code]" or anything similar anywhere
- Focus on what and why, not how

### Step 2.5: 🚨 CRITICAL - Test Your Changes

**BEFORE pushing and creating a PR, you MUST test your code.**

```bash
# For configurator changes
cd inav-configurator
npm start
# Actually use the feature, verify it works

# For firmware changes
cd inav
./build.sh TARGETNAME
# Flash to hardware or test in SITL
```

**Testing Checklist:**
- [ ] Code actually runs (not just compiles)
- [ ] Feature works as intended
- [ ] Tested edge cases (invalid inputs, empty data, etc.)
- [ ] No regressions in existing functionality
- [ ] Documented what you tested

**DO NOT:**
- ❌ Create PR immediately after coding
- ❌ Claim you tested if you didn't
- ❌ Mark tasks complete without testing
- ❌ Assume it works because it compiles

**If you cannot test:**
- Be explicit in PR description about what you couldn't test
- Request testing from someone with the hardware/setup
- Only document what you actually verified

**Remember:** Untested code can brick flight hardware. Test first, PR second.

### Step 3: Push Branch

```bash
# Push new branch to remote
git push -u origin your-branch-name
```

### Step 4: Create Pull Request

#### For PrivacyLRS (origin repository):

```bash
gh pr create --repo sensei-hacker/PrivacyLRS \
  --base secure_01 \
  --title "Your PR Title" \
  --body "Concise PR description"
```

#### For INAV/inav-configurator (upstream repository):

```bash
# Normal case - target maintenance-9.x (backwards compatible)
gh pr create --repo inavflight/inav \
  --base maintenance-9.x \
  --title "Your PR Title" \
  --body "Concise PR description"

# Breaking changes - target maintenance-10.x
gh pr create --repo inavflight/inav \
  --base maintenance-10.x \
  --title "Your PR Title" \
  --body "Concise PR description"
```

#### Using heredoc for multi-line PR descriptions:

```bash
gh pr create --repo sensei-hacker/PrivacyLRS \
  --base secure_01 \
  --title "Your PR Title" \
  --body "$(cat <<'EOF'
## Summary
Brief overview of changes

## Changes
- Change 1
- Change 2

## Testing
How changes were tested, if relevant

## Related Issues
Fixes #123
EOF
)"
```

---

## PR Description Best Practices

A good PR description includes:

### Required Sections
1. **Summary** - What does this PR do?
2. **Changes** - Specific changes made

### Optional Sections
- **Breaking Changes** - If any
- **Related Issues** - Links to issues
- **Screenshots** - For UI changes
- **Testing** - How was it tested?
- **Performance Impact** - If relevant
- **Security Considerations** - For security changes

## Prohibited in PR description:
- DO NOT mention Claude or AI assistance. Avoid writing "Generated with [Claude Code]" or anything similar anywhere

### Example Template

```markdown
## Summary
Brief description of what this PR accomplishes

## Changes
- Specific change 1
- Specific change 2
- Specific change 3

## Testing
- Test 1 performed
- Test 2 performed
- Results: ...

## Related Issues
Closes #123
Related to #456
```

---

## Common Workflow Mistakes to Avoid

### ❌ Working Directly on Base Branch
**WRONG:**
```bash
git checkout secure_01
git cherry-pick abc123
git push origin secure_01
```

**RIGHT:**
```bash
git checkout secure_01
git checkout -b my-feature-branch
git cherry-pick abc123
git push -u origin my-feature-branch
gh pr create --repo sensei-hacker/PrivacyLRS --base secure_01
```

**Why:** Working directly on the base branch bypasses the PR review process and can cause issues with the repository state.

### ❌ Using Slashes in Branch Names (PrivacyLRS)
**WRONG:**
```bash
git checkout -b security/encryption-tests
git checkout -b feature/new-protocol
```

**RIGHT:**
```bash
git checkout -b encryption-tests
git checkout -b new-protocol
```

**Why:** All repos uses flat branch naming without directory-style slashes.

### ❌ Forgetting to Specify Base Branch
**WRONG:**
```bash
gh pr create --repo sensei-hacker/PrivacyLRS --title "My PR"
```

**RIGHT:**
```bash
gh pr create --repo sensei-hacker/PrivacyLRS --base secure_01 --title "My PR"
```

**Why:** Always explicitly specify the base branch to avoid targeting the wrong branch.

---

## Before Creating PR Checklist

**🚨 CRITICAL - Testing:**
- [ ] **Code has been ACTUALLY TESTED** (not just compiled)
- [ ] **Feature verified working** in running application
- [ ] **Edge cases tested** (invalid inputs, empty data, etc.)
- [ ] **No regressions** - existing features still work
- [ ] **Only claim what you actually tested** in PR description

**Code Quality:**
- [ ] Commit messages are clear and descriptive
- [ ] Only intended files are committed (review with `git status`)
- [ ] Code follows project standards

**PR Setup:**
- [ ] Branch is pushed to correct remote
- [ ] PR description is complete and accurate
- [ ] Targeting correct repository (origin for PrivacyLRS, upstream for INAV)
- [ ] Targeting correct base branch (maintenance-9.x for INAV, secure_01 for PrivacyLRS)

---

## Quick Reference Commands

```bash
# Check current branch
git branch --show-current

# View what will be in PR
# For PrivacyLRS
git diff secure_01...HEAD
# For INAV
git diff upstream/maintenance-9.x...HEAD

# Check which files are staged
git status

# View commit history
git log --oneline -10

# Check remotes
git remote -v

# View PR after creation
gh pr view

# View PR status and checks
gh pr status

# List your PRs
gh pr list --author "@me"
```

---

## Troubleshooting

### Wrong Repository Target
If you created PR on wrong repository:
```bash
# Close the incorrect PR
gh pr close <PR_NUMBER>

# Create new PR targeting correct repo
gh pr create --repo <correct-repo> ...
```

### Wrong Base Branch
If you created PR targeting wrong base branch:
```bash
# Edit PR to change base branch
gh pr edit <PR_NUMBER> --base maintenance-9.x
```

### Forgot to Push Branch
```bash
git push -u origin your-branch-name
```

### Need to Update PR
```bash
# Make changes
git add <files>
git commit -m "Update based on feedback"
git push

# PR updates automatically
```

### Change PR Description
```bash
gh pr edit <PR_NUMBER> --body "New description"
```

---

## Repository Quick Reference

| Project | PR Target | Base Branch | Use Case | Command |
|---------|-----------|-------------|----------|---------|
| **PrivacyLRS** | `sensei-hacker/PrivacyLRS` | `secure_01` | All code changes | `gh pr create --repo sensei-hacker/PrivacyLRS --base secure_01` |
| **INAV** | `inavflight/inav` | `maintenance-9.x` | Backwards compatible | `gh pr create --repo inavflight/inav --base maintenance-9.x` |
| **INAV** | `inavflight/inav` | `maintenance-10.x` | Breaking changes | `gh pr create --repo inavflight/inav --base maintenance-10.x` |
| **inav-configurator** | `inavflight/inav-configurator` | `maintenance-9.x` | Backwards compatible | `gh pr create --repo inavflight/inav-configurator --base maintenance-9.x` |
| **inav-configurator** | `inavflight/inav-configurator` | `maintenance-10.x` | Breaking changes | `gh pr create --repo inavflight/inav-configurator --base maintenance-10.x` |

**Remember:**
- Always double-check you're targeting the correct repository AND base branch before creating the PR!
- NEVER use master for code changes
- Use maintenance-9.x for backwards compatible changes (most common)
- Use maintenance-10.x for breaking changes (MSP protocol, settings format, etc.)

---

## Related Skills

- **git-workflow** - Branch management and git operations before creating PR
- **pr-review** - Review pull requests after creation
- **check-builds** - Check CI build status for your PR
- **start-task** - Start tasks with proper branch setup
- **finish-task** - Complete tasks before creating PR
- **privacylrs-test-runner** - Run tests before creating PrivacyLRS PR
- **test-privacylrs-hardware** - Hardware test before PrivacyLRS PR
