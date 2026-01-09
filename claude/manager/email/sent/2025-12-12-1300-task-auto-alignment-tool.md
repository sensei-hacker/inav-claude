# Task Assignment: Auto Alignment Tool

**Date:** 2025-12-12 13:00
**Project:** feature-auto-alignment-tool
**Priority:** Medium (Backburner)
**Estimated Effort:** 4-8 hours
**Branch:** From `maintenance-9.x`

## Task

Review, update, and polish PR #2158 (Auto Alignment Tool) for merge readiness.

## Background

PR #2158 implements a wizard-style tool that automatically detects and sets FC and compass alignment:
1. User points aircraft north
2. User lifts the nose
3. Tool reads accelerometer/magnetometer data
4. Tool calculates and sets correct alignment values

The PR was created Aug 2024 and has basic functionality but is labeled "Don't merge" - needs polish before it's ready.

## What to Do

1. **Review current PR state**
   - Check out branch and test current functionality
   - Identify what needs updating for maintenance-9.x compatibility

2. **Update and polish**
   - Rebase onto latest maintenance-9.x if needed
   - Fix any compatibility issues
   - Improve UI/UX and user guidance
   - Handle edge cases (no mag, inverted mounting, etc.)

3. **Test thoroughly**
   - Various FC mounting orientations
   - External compass scenarios
   - Error conditions

4. **Prepare for merge**
   - Remove "Don't merge" label when ready
   - Update PR description if needed

## Success Criteria

- [ ] Works for common FC mounting orientations
- [ ] Works for external compass alignment
- [ ] Clear user instructions during process
- [ ] Graceful error handling
- [ ] Rebased on maintenance-9.x
- [ ] PR ready for review/merge

## PR Reference

https://github.com/iNavFlight/inav-configurator/pull/2158

## Notes

This is a backburner task - work on it when higher priority items are complete.

---
**Manager**
