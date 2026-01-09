# Task Assignment: Identify PRs Incorrectly Merged to Master

**Date:** 2025-12-19 01:08
**Project:** inav / inav-configurator
**Priority:** High
**Estimated Effort:** 1-2 hours

## Task
Check the PRs merged in the last two weeks and identify any that were merged to master instead of to a version branch.

## What to Do
1. Check both inav (firmware) and inav-configurator repositories
2. List PRs merged in the last two weeks to the master branch
3. For each PR, determine if it should have been merged to a version branch instead
4. Identify the pattern: what is the normal branching strategy?
5. Create a list of any PRs that were merged incorrectly
6. Document your findings

## Success Criteria
- [ ] Checked both repositories (inav and inav-configurator)
- [ ] Listed all PRs merged to master in the last two weeks
- [ ] Identified which (if any) should have gone to a version branch
- [ ] Documented the expected branching strategy
- [ ] Provided PR numbers, titles, and dates for any incorrect merges
- [ ] Sent completion report with findings

## Notes
- Use `gh pr list` to query merged PRs
- Check the base branch for each PR
- Consider looking at recent version branches to understand the pattern
- Two weeks ago = approximately 2025-12-05

---
**Manager**
