# Update: macOS DMG Fix - Found and Fixed Path Issue

**Date:** 2025-12-28 23:00
**To:** Manager
**From:** Developer
**Type:** Task Update
**Related PR:** https://github.com/iNavFlight/inav-configurator/pull/2508

## Status Update

I verified my initial fix using CI build artifacts and **discovered it didn't work**. Found the bug, fixed it, and pushed an update.

## What I Found

After checking the CI-built macOS DMG, I discovered the Windows/Linux SITL binaries were still present - the hook wasn't removing them.

### Root Cause

My initial fix used the wrong path for macOS app bundles - I was missing the `.app` directory in the path:

**❌ Initial fix (WRONG):**
```
<outputPath>/Contents/Resources/sitl
```

**✅ Correct path:**
```
<outputPath>/INAV Configurator.app/Contents/Resources/sitl
```

### Evidence from CI Build Logs

```
postPackage: Checking SITL path for darwin: .../INAV Configurator-darwin-x64/Contents/Resources/sitl
postPackage: SITL path not found, skipping
```

The hook couldn't find the SITL directory because it was looking in the wrong place!

### Verified from DMG Contents

Downloaded CI artifact and inspected it:
```bash
7z l INAV-Configurator_MacOS_x64_9.0.0.dmg | grep sitl
```

**Result:** All three directories still present:
- ❌ `sitl/windows/` (with cygwin1.dll and inav_SITL.exe)
- ❌ `sitl/linux/`
- ✓ `sitl/macos/`

## Fix Applied

**Second commit: `d28fa437f`**

Changed the path construction to dynamically find the `.app` bundle:

```javascript
if (options.platform === 'darwin') {
  // Find the .app directory dynamically
  const appBundles = fs.readdirSync(outputPath).filter(f => f.endsWith('.app'));
  sitlPath = path.join(outputPath, appBundles[0], 'Contents', 'Resources', 'sitl');
}
```

This approach:
- Finds any `.app` directory in outputPath
- Constructs the correct full path including the .app bundle name
- Works regardless of app name changes

## Current Status

- ✅ Updated fix pushed to PR
- ⏳ CI is rebuilding (will take ~4 minutes)
- 🔍 Will verify new CI build when complete

## Next Steps

1. **Wait for CI rebuild** (~4 min)
2. **Download new macOS DMG artifact**
3. **Verify Windows/Linux directories are removed**
4. **Update Release Manager** with verification results

## Lessons Learned

- Always verify fixes with actual build artifacts
- macOS app bundles have complex structure: `<dir>/<Name>.app/Contents/Resources/`
- The app name ("INAV Configurator.app") != executable name ("inav-configurator")
- CI builds are valuable for immediate verification

## Timeline

- 21:48 - Initial fix committed and pushed
- 21:50 - CI completed first build
- 22:56 - Downloaded and inspected artifacts - **found bug**
- 23:00 - Second fix committed and pushed
- 23:01 - CI rebuilding now

---
**Developer**
