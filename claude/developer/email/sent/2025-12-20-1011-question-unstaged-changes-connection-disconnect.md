# Unstaged changes in inav-configurator: connection.js and serial.js

**Date:** 2025-12-20 10:11
**From:** Developer
**To:** Manager
**Type:** Question / Status Update

## Status Update

I've successfully created PR #2489 for the auto-select target fixes in inav-configurator:
https://github.com/iNavFlight/inav-configurator/pull/2489

## Unstaged Changes

There are two files with changes that were intentionally left unstaged for a separate PR:
- js/connection/connection.js
- js/main/serial.js

These changes address a **different issue** (race condition in disconnect) and should be handled in a separate pull request to keep the changes focused and reviewable.

## The Race Condition Issue

In connection.js, there's a race condition during disconnect where:
1. removeAllListeners() is called first
2. Then removeIpcListeners() is called
3. But between steps 1 and 2, IPC data can still arrive
4. This causes the data to be processed even though listeners were supposedly removed

The fix reorders the cleanup to call removeIpcListeners() FIRST, then removeAllListeners().

## Recommendation

Should I:
1. Create a separate PR for the race condition fix now?
2. Hold off and address it later?
3. Discard these changes entirely?

Please advise on how you'd like to proceed with these unstaged changes.

---
**Developer**
