# Task Assignment: BROTHERHOBBYF722 Merge Status & Cleanup

**Date:** 2025-12-07 16:00
**Priority:** LOW
**Estimated Effort:** 30-60 minutes
**Branch:** N/A (cleanup task)

## Task

Investigate whether the BROTHERHOBBYF722 target has been merged upstream, and clean up any related untracked files in our local repository.

## Background

There appear to be untracked files related to BROTHERHOBBYF722 in the repository. Need to determine:
1. Was this target merged upstream?
2. If so, when and in which PR?
3. What untracked files exist locally that should be cleaned up?

## What to Do

### 1. Check for Untracked Files

```bash
cd inav
git status | grep -i brotherhobby
git status | grep -i "F722"
```

Also check for any untracked target directories:
```bash
ls -la src/main/target/ | grep -i brother
find . -name "*BROTHERHOBBY*" -o -name "*brotherhobby*"
```

### 2. Check Upstream Status

```bash
# Check if target exists in upstream
git fetch upstream
git ls-tree -r upstream/master --name-only | grep -i brotherhobby
git ls-tree -r upstream/maintenance-9.x --name-only | grep -i brotherhobby

# Search for related PRs
gh pr list --repo iNavFlight/inav --state all --search "BROTHERHOBBYF722" --limit 20
gh pr list --repo iNavFlight/inav --state all --search "brotherhobby" --limit 20
```

### 3. Check Git Log

```bash
# See if there are commits related to this target
git log --oneline --all --grep="BROTHERHOBBY" | head -20
git log --oneline --all --grep="brotherhobby" | head -20
```

### 4. Determine Status

Based on findings, determine:
- **Merged:** Target exists in upstream branches
- **Not Merged:** Target only exists locally or in a PR
- **Pending PR:** PR exists but not yet merged

### 5. Clean Up Untracked Files

If files are untracked and either:
- Already merged upstream (duplicates)
- Abandoned work (no longer needed)
- Temporary/test files

Then clean them up:

```bash
# List what would be removed (dry run)
git clean -n -d | grep -i brotherhobby

# If safe, remove untracked files
git clean -f <specific-files>
```

**CAUTION:** Before deleting, verify the files are not:
- Work in progress that should be preserved
- Local modifications needed for testing
- Part of a pending PR

### 6. Report Findings

Report back with:
- What untracked files were found
- Upstream merge status (merged/not merged/pending)
- PR number if applicable
- What was cleaned up
- Any remaining items that need attention

## Success Criteria

- [ ] Identified all BROTHERHOBBYF722-related untracked files
- [ ] Determined upstream merge status
- [ ] Cleaned up unnecessary untracked files
- [ ] Documented what was found and done
- [ ] Completion report sent to Manager

## Notes

This is a housekeeping task to clean up the local repository. Take care not to delete anything that might be valuable or in-progress work.

If uncertain about any files, ask Manager before deleting.

---
**Manager**
