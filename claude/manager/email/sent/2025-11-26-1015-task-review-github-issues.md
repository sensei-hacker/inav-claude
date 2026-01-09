# Task Assignment: Review GitHub Issues for Actionable Bugs

**Date:** 2025-11-26 10:15
**Project:** github-issues-review
**Priority:** Medium
**Estimated Effort:** 1-2 hours
**Branch:** N/A (research task)

## Task

Review the last 25 open issues on both INAV GitHub repositories and identify any that we can likely fix in the code.

## Repositories to Check

1. **inav-configurator:** https://github.com/iNavFlight/inav-configurator/issues
2. **inav firmware:** https://github.com/iNavFlight/inav/issues

## What to Do

1. Use `gh issue list --limit 25 --state open` for each repository
2. For promising issues, read the full issue with `gh issue view <number>`
3. Categorize issues into:
   - **Actionable bugs** - Clear bugs we can likely fix
   - **Feature requests** - New functionality (note but lower priority)
   - **Support questions** - Not code fixes
   - **Needs more info** - Can't act without reproduction steps
   - **Complex/risky** - Would require significant effort or deep expertise

## Deliverable

Send a summary report to manager with:

1. **Recommended issues to fix** - Issues that are:
   - Clear bug reports with reproduction steps
   - Likely fixable within a few hours
   - In areas we've worked on before (configurator tabs, MSP, settings, UI)

2. **For each recommended issue include:**
   - Issue number and title
   - Brief description of the problem
   - Affected files (if identifiable)
   - Estimated effort (low/medium/high)
   - Why it's a good candidate

3. **Issues to skip** - Brief list with reasons

## Success Criteria

- [ ] Reviewed 25 issues from inav-configurator
- [ ] Reviewed 25 issues from inav firmware
- [ ] Identified actionable bugs vs other issue types
- [ ] Provided prioritized list of recommended fixes
- [ ] Sent summary report to manager

## Notes

- Focus on configurator issues first (JavaScript) as we have more context there
- Firmware issues (C) are fine too if they're straightforward
- Don't spend too long on any single issue - this is triage, not deep investigation
- If an issue looks promising but needs investigation, note it as such

---
**Manager**
