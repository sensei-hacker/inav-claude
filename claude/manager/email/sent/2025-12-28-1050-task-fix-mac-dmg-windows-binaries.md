# Task Assignment: Fix Mac DMG Containing Windows Binaries

**Date:** 2025-12-28 10:50
**Project:** Configurator Build Fix
**Priority:** MEDIUM
**Estimated Effort:** 2-3 hours
**Branch:** From `maintenance-9.x`

## Task

Fix the `afterCopy` hook in the Electron Forge configuration so that macOS DMG packages don't include Windows SITL binaries.

## Background

**Bug Report from Release Manager (Dec 24):**

The macOS DMG packages currently contain Windows SITL binaries that should have been removed:
```
INAV Configurator.app/Contents/Resources/sitl/windows/cygwin1.dll
INAV Configurator.app/Contents/Resources/sitl/windows/inav_SITL.exe
```

**Impact:**
- Unnecessarily increases DMG file size
- May confuse users
- Inconsistent with intended behavior

**Root Cause:**
The `afterCopy` hook in `forge.config.js` (added in PR #2496) is supposed to remove non-native SITL binaries but isn't working correctly for macOS builds.

## What to Do

### 1. Investigate Current Hook

**File:** `inav-configurator/forge.config.js`

Look for the `afterCopy` hook that was added in PR #2496:
- Review how it identifies the target platform
- Check how it determines which SITL binaries to remove
- Identify why it's not working on macOS builds

### 2. Reproduce the Issue

Build the macOS DMG and verify the issue:

```bash
cd inav-configurator

# Build macOS DMG (if on macOS)
npm run make -- --platform=darwin

# Check contents of DMG
# Mount the DMG and inspect:
# INAV Configurator.app/Contents/Resources/sitl/

# Verify issue: windows/ directory should NOT exist in macOS build
```

### 3. Fix the Hook

**Expected behavior:**
- **macOS build:** Should ONLY contain `sitl/darwin/` (remove `windows/` and `linux/`)
- **Windows build:** Should ONLY contain `sitl/windows/` (remove `darwin/` and `linux/`)
- **Linux build:** Should ONLY contain `sitl/linux/` (remove `darwin/` and `windows/`)

**Check for:**
- Platform detection correctness
- Path handling (macOS vs Windows path separators)
- Timing of hook execution (are SITL files copied after hook runs?)
- Directory removal logic (permissions, recursion)

**Common issues to check:**
```javascript
// Check platform detection
console.log('Platform:', process.platform);  // darwin, win32, linux

// Ensure paths are correct
const sitlPath = path.join(appPath, 'resources', 'sitl');

// Remove non-native platforms
const platformsToRemove = process.platform === 'darwin'
  ? ['windows', 'linux']
  : process.platform === 'win32'
  ? ['darwin', 'linux']
  : ['darwin', 'windows'];
```

### 4. Test the Fix

**Test all platforms:**

```bash
# macOS
npm run make -- --platform=darwin
# Verify: Only sitl/darwin/ exists

# Windows (if available)
npm run make -- --platform=win32
# Verify: Only sitl/windows/ exists

# Linux (if available)
npm run make -- --platform=linux
# Verify: Only sitl/linux/ exists
```

**For each platform, check:**
1. Package builds successfully
2. Only native SITL binaries are included
3. Non-native SITL directories are removed
4. SITL functionality works (test in configurator)

### 5. Create Pull Request

**Use the /create-pr skill:**

```bash
/create-pr
```

**PR Title:** "Fix afterCopy hook to remove non-native SITL binaries from macOS builds"

**PR Description template:**
```markdown
## Summary
Fix the `afterCopy` hook in `forge.config.js` to properly remove non-native SITL binaries from all platform builds, particularly macOS.

## Problem
macOS DMG packages were including Windows SITL binaries (cygwin1.dll, inav_SITL.exe) that should have been removed.

## Changes
- Fixed platform detection in afterCopy hook
- Ensured proper removal of non-native SITL directories
- [Describe specific fix made]

## Testing
- [x] macOS build: Only contains sitl/darwin/
- [x] Windows build: Only contains sitl/windows/ (if tested)
- [x] Linux build: Only contains sitl/linux/ (if tested)
- [x] SITL functionality verified in configurator

## Impact
- Reduces package size
- Removes confusing non-native binaries
- Makes builds consistent across platforms
```

## Success Criteria

- [ ] Investigated why afterCopy hook isn't working on macOS
- [ ] Identified root cause of the issue
- [ ] Fixed the hook to properly remove non-native binaries
- [ ] macOS DMG verified: NO windows/ directory present
- [ ] macOS DMG verified: ONLY darwin/ directory present
- [ ] SITL functionality tested in macOS configurator
- [ ] Windows/Linux builds tested if possible
- [ ] PR created from `maintenance-9.x` branch
- [ ] PR description complete with testing details
- [ ] CI builds passing

## Files to Check

**Primary:**
- `inav-configurator/forge.config.js` - The afterCopy hook

**Reference:**
- PR #2496 - Original PR that added the hook
- `inav-configurator/package.json` - Build scripts
- `inav-configurator/resources/sitl/` - SITL binaries source

**Testing:**
- Build output DMG files
- Mounted DMG contents verification

## Notes

**Branch:** Use `maintenance-9.x` as base branch

**Not Urgent:** This isn't blocking releases, but should be fixed for the next RC/release

**Platform Availability:** If you only have access to one platform (e.g., Linux), focus on:
1. Fixing the hook logic
2. Testing that the logic correctly identifies which directories to remove
3. Document in PR what platforms were tested
4. Request testing on other platforms in PR description

**Debugging Tips:**
```javascript
// Add logging to afterCopy hook to debug
console.log('afterCopy running for platform:', process.platform);
console.log('App path:', appPath);
console.log('SITL path:', sitlPath);
console.log('Removing platforms:', platformsToRemove);
```

**DMG Inspection (macOS):**
```bash
# Mount DMG
hdiutil attach INAV-Configurator-9.0.0-RC4.dmg

# Check contents
ls -la "/Volumes/INAV Configurator/INAV Configurator.app/Contents/Resources/sitl/"

# Should only see: darwin/

# Unmount
hdiutil detach "/Volumes/INAV Configurator"
```

---
**Manager**
