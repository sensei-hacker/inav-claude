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

## Repository Structure

The INAV project consists of **three standalone repositories**:
- `inav/` - Flight controller firmware (C/C99)
- `inav-configurator/` - Desktop GUI (JavaScript/Electron)
- `inavwiki/` - Documentation (Markdown)

Each repository has its own git history and must be managed independently.

## Creating Branches

### Create a New Branch

```bash
# Create and switch to new branch
git checkout -b my-new-branch

# Or use switch (newer git)
git switch -c my-new-branch

# Push branch to remote
git push -u origin my-new-branch
```

### Create Branch from Specific Commit

```bash
# Create branch from specific commit
git checkout -b bugfix-123 <commit-hash>

# Or from a tag
git checkout -b new-feature v9.0.0
```

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

Since `inav/`, `inav-configurator/`, and `inavwiki/` are standalone repos:

### Check Status Across All Repos

```bash
# From project root
for repo in inav inav-configurator inavwiki; do
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

If working on a feature that spans multiple repos:

```bash
# Firmware
cd inav
git checkout -b my-feature
git push -u origin my-feature

# Configurator
cd ../inav-configurator
git checkout -b my-feature
git push -u origin my-feature

# Documentation
cd ../inavwiki
git checkout -b my-feature
git push -u origin my-feature
```

## Common Workflows

### Starting New Feature

```bash
# 1. Ensure you're on master and up to date
git checkout master
git pull origin master

# 2. Create feature branch
git checkout -b my-feature

# 3. Make changes and commit
git add <files>
git commit -m "Add: initial implementation"

# 4. Push to remote
git push -u origin my-feature
```

### Updating Feature Branch with Latest Master

```bash
# Option 1: Rebase (cleaner history)
git checkout my-feature
git fetch origin
git rebase origin/master

# Option 2: Merge (preserves history)
git checkout my-feature
git fetch origin
git merge origin/master
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
