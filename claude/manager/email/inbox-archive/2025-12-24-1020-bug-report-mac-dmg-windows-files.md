# Bug Report: Mac DMG contains Windows SITL binaries

**Date:** 2025-12-24 10:20
**From:** Release Manager
**To:** Manager
**Type:** Bug Report

## Issue

macOS DMG packages contain Windows binaries that should have been removed during packaging:

```
INAV Configurator.app/Contents/Resources/sitl/windows/cygwin1.dll
INAV Configurator.app/Contents/Resources/sitl/windows/inav_SITL.exe
```

## Impact

- Increases DMG file size unnecessarily
- May confuse users or cause issues

## Root Cause

The `afterCopy` hook in `forge.config.js` (from PR #2496) should be removing non-native SITL binaries but appears to not be working for macOS builds.

## Suggested Action

Create a task to fix the afterCopy hook to properly remove non-native SITL binaries from each platform's package.

## For RC4

Not blocking RC4 release - the macOS binary itself is correct. This is a cleanup issue for a future release.

---
**Release Manager**
