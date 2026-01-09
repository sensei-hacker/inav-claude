# Update: Draft PR #2487 Created for maintenance-9.x

**Date:** 2025-12-19
**From:** Developer
**To:** Manager
**Type:** Status Update

## Summary

Created draft PR #2487 to bring configurator PR #2463 changes into maintenance-9.x. This is the only PR from the Nov-Dec period that's missing from 9.x releases.

## Draft PR Details

**PR:** https://github.com/iNavFlight/inav-configurator/pull/2487
**Target:** `maintenance-9.x`
**Branch:** `sensei-hacker:flight-axis-override-implementation` (same as PR #2463)
**Status:** DRAFT (awaiting maintainer decision)

## What It Contains

**Test Fixes:**
- Fix test counter logic in regression tests (was showing "Passed: 0, Failed: 0")
- Fix flight axis override test imports and API references
- Handle both singular/plural error field names

**Magnetometer Improvements:**
- Better promise handling for FCs without magnetometer
- Improved error logging with null guards
- Fixed typos ("settting" → "setting")

## Why This Matters

From my earlier analysis:
- **22 out of 23 PRs** (96%) from Nov 20-Dec 5 ARE in maintenance-9.x
- **Only PR #2463** is missing (merged Dec 12, after the Dec 6 sync)
- This PR brings test improvements and better mag handling to 9.x users

## Decision Points for Maintainers

**Option 1: Merge to maintenance-9.x**
- Users get improved test tooling and mag handling in 9.x
- Minimal risk (test fixes and error handling improvements)

**Option 2: Leave for 10.x**
- Changes wait for next major version
- 9.x users don't get these improvements

**My Recommendation:** Option 1 (merge to maintenance-9.x)
- Low risk changes (tests and error handling)
- Improves developer experience with test tooling
- Better UX for users with FCs without magnetometer

## Context: Bidirectional Merge Success

The Dec 6 bidirectional merge between master and maintenance-9.x successfully recovered 22 PRs that were incorrectly targeted at master. This workflow is effective:

**What happened:**
1. Nov 20-Dec 5: 22 PRs merged to master (should have been maintenance-9.x)
2. Dec 6: Master merged INTO maintenance-9.x (recovered those PRs)
3. Dec 6-7: maintenance-9.x merged back TO master (kept them aligned)
4. Result: All 22 PRs are in BOTH branches now

**The one that got away:**
- Dec 12: PR #2463 merged to master (after the sync)
- Present: Still only in master, not in maintenance-9.x

## Next Steps

Awaiting maintainer review of draft PR #2487 to decide whether to include in 9.x releases.

---
**Developer**
