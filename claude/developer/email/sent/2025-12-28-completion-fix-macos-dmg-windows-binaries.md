# Task Completed: Fix Mac DMG Windows Binaries

**Date:** 2025-12-28
**From:** Developer
**Type:** Completion Report

## Status: COMPLETED ✓

## Summary
Fixed the `postPackage` hook in `forge.config.js` to properly remove non-native SITL binaries from macOS DMG packages.

## Problem
macOS DMG packages were including Windows SITL binaries (cygwin1.dll, inav_SITL.exe) that should have been removed by the build process, unnecessarily increasing package size.

## Root Cause Identified
The `postPackage` hook was using incorrect path for macOS app bundles:

- **Hook was looking at:** `<outputPath>/resources/sitl`
- **macOS actual location:** `<app>/Contents/Resources/sitl`
- **Windows/Linux location:** `<outputPath>/resources/sitl` ✓

macOS app bundles have a different structure (`App.app/Contents/Resources/`) compared to Windows/Linux flat packages. The hook couldn't find the SITL directory on macOS builds and failed silently.

## Solution Implemented
Modified `forge.config.js` to use platform-specific paths:

```javascript
const sitlPath = options.platform === 'darwin'
  ? path.join(outputPath, 'Contents', 'Resources', 'sitl')
  : path.join(outputPath, 'resources', 'sitl');
```

Also added console logging to help verify hook execution during builds.

## Changes Made

**File:** `inav-configurator/forge.config.js`

- Updated path construction for `sitlPath` to handle macOS app bundle structure
- Added platform detection for darwin (macOS)
- Added debug logging for build verification
- No changes to removal logic (already correct for all platforms)

## Pull Request

**PR:** https://github.com/iNavFlight/inav-configurator/pull/2508
**Branch:** `fix-macos-dmg-windows-binaries`
**Base:** `maintenance-9.x`
**Commit:** `204c08231`

## Testing

Logic verified for all platforms:
- ✓ macOS path construction: `<outputPath>/Contents/Resources/sitl`
- ✓ Windows/Linux path construction: `<outputPath>/resources/sitl`
- ✓ Console logging added for build verification
- ⚠️ Full testing requires macOS build environment (will be verified in next RC build)

**Expected results after next macOS build:**
- macOS DMG will ONLY contain `sitl/darwin/` directory
- Windows/Linux binaries will be removed correctly
- Build logs will show "Removing non-macOS SITL binaries (linux, windows)"

## Impact

- Reduces macOS DMG package size
- Removes confusing non-native binaries from macOS builds
- Makes macOS builds consistent with Windows/Linux builds
- No functionality changes - only affects packaged files

## Files Modified

- `inav-configurator/forge.config.js` - Fixed postPackage hook path handling

## Lock Released

✓ Released `inav-configurator.lock`

---
**Developer**
