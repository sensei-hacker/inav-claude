# Task Assignment: Create GitHub Action for PR Branch Suggestion

**Date:** 2025-11-30 12:00
**Priority:** Medium
**Estimated Effort:** 1-2 hours

## Task

Create a GitHub Action that automatically comments on new Pull Requests targeting the `master` branch, suggesting that contributors consider targeting `maintenance-9.x` or `maintenance-10.x` branches instead.

## Background

We have multiple maintenance branches that allow fixes and features to be backported to older INAV versions. Many contributors target `master` by default when their changes could benefit users on maintenance releases. This action will help guide contributors to the appropriate branch.

## What to Do

1. Create a new GitHub Action workflow that triggers when a PR is opened targeting `master`

2. The action should automatically add a comment to the PR with the following guidance:

   - If the contributor's change will **NOT** create a compatibility issue with existing INAV 9.x firmware and Configurator, they should consider targeting the `maintenance-9.x` branch instead

   - If there **IS** a compatibility issue (the change requires both firmware and configurator updates that break compatibility with 9.x), they should consider targeting the `maintenance-10.x` branch instead

3. The comment should be informational/suggestive, not blocking - contributors can still merge to master if that's the appropriate target

## Suggested Comment Content

Something like:

> **Branch Targeting Suggestion**
>
> You've targeted the `master` branch with this PR. Please consider if a maintenance branch might be more appropriate:
>
> - **`maintenance-9.x`** - If your change is backward-compatible and won't create compatibility issues between INAV firmware and Configurator 9.x versions
>
> - **`maintenance-10.x`** - If your change introduces compatibility requirements between firmware and configurator that would break 9.x compatibility
>
> If `master` is the correct target for this change, no action is needed.

## Success Criteria

- [ ] GitHub Action triggers on new PRs targeting master
- [ ] Helpful comment is added automatically
- [ ] Action uses appropriate GitHub token permissions
- [ ] Does not block PR workflow

## Notes

- This should be created in the inav repository (and possibly also inav-configurator)
- Use GitHub's built-in `GITHUB_TOKEN` for permissions
- Consider using the `pull_request` event with `types: [opened]`

---
**Manager**
