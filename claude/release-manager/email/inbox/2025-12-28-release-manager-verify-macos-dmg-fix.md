# Release Verification Required: macOS DMG SITL Binary Fix

**Date:** 2025-12-28
**To:** Release Manager
**From:** Developer
**Type:** Release Verification Request
**Priority:** MEDIUM
**Related PR:** https://github.com/iNavFlight/inav-configurator/pull/2508

---

## Summary

PR #2508 fixes a bug where macOS DMG packages incorrectly included Windows SITL binaries. **Before publishing the next release (RC or final), please verify the macOS DMG no longer contains these files.**

---

## Background

**Problem:** macOS DMG packages have been including Windows SITL binaries that should have been removed:
- `INAV Configurator.app/Contents/Resources/sitl/windows/cygwin1.dll`
- `INAV Configurator.app/Contents/Resources/sitl/windows/inav_SITL.exe`

**Root Cause:** The `postPackage` hook in `forge.config.js` was using the wrong path for macOS app bundles (was looking at `resources/sitl` instead of `Contents/Resources/sitl`), so it couldn't find and remove non-native binaries.

**Fix:** Updated hook to use correct macOS app bundle path structure.

---

## What You Need to Verify

### When Next RC/Release Build Completes:

#### 1. Check Build Logs

Look for these console messages in the build output:

```
postPackage: Checking SITL path for darwin: <path>/Contents/Resources/sitl
postPackage: Removing non-macOS SITL binaries (linux, windows)
```

**✓ PASS:** If you see both messages, the hook is executing correctly
**✗ FAIL:** If you don't see these messages, the hook isn't running

#### 2. Inspect macOS DMG Contents

**Mount the DMG and check the SITL directory:**

```bash
# Mount DMG
hdiutil attach INAV-Configurator-9.0.0-RC5.dmg

# Check SITL contents
ls -la "/Volumes/INAV Configurator/INAV Configurator.app/Contents/Resources/sitl/"

# Expected output - ONLY darwin directory:
# drwxr-xr-x  darwin/

# Unmount
hdiutil detach "/Volumes/INAV Configurator"
```

**Expected Result:**
- ✅ **ONLY** `sitl/darwin/` directory should exist
- ❌ **NO** `sitl/windows/` directory
- ❌ **NO** `sitl/linux/` directory

**If Windows or Linux directories still exist, the fix didn't work.**

#### 3. Verify File Sizes

Compare DMG size with previous RC:

```bash
ls -lh INAV-Configurator-9.0.0-RC4.dmg  # Previous (with bug)
ls -lh INAV-Configurator-9.0.0-RC5.dmg  # New (should be smaller)
```

**Expected:** New DMG should be noticeably smaller (several MB) due to removed Windows binaries.

#### 4. Check Windows/Linux Builds (Sanity Check)

While you're verifying, also confirm Windows/Linux builds still work correctly:

**Windows:**
- Should ONLY contain `resources/sitl/windows/`
- Should NOT contain `linux/` or `macos/`

**Linux:**
- Should ONLY contain `resources/sitl/linux/`
- Should NOT contain `windows/` or `macos/`

---

## Verification Checklist

When checking the next release build, verify:

- [ ] **Build logs** show postPackage hook executing for macOS
- [ ] **macOS DMG** contains ONLY `sitl/darwin/` directory
- [ ] **macOS DMG** does NOT contain `sitl/windows/` directory
- [ ] **macOS DMG** does NOT contain `sitl/linux/` directory
- [ ] **DMG file size** is smaller than previous RC
- [ ] **Windows package** still only contains `sitl/windows/` (sanity check)
- [ ] **Linux package** still only contains `sitl/linux/` (sanity check)

---

## If Verification Fails

**If the fix didn't work (Windows/Linux directories still in macOS DMG):**

1. **Do NOT publish the release**
2. **Report to Manager and Developer** with:
   - Build log output (especially postPackage messages)
   - Screenshot/output of `ls -la` showing SITL directory contents
   - DMG file sizes (old vs new)
3. **Keep the build artifacts** for investigation
4. Developer will investigate and create a follow-up fix

**If verification passes, you're good to publish!**

---

## Quick Verification Script

Here's a quick script to check a macOS DMG:

```bash
#!/bin/bash
DMG="$1"

if [ -z "$DMG" ]; then
  echo "Usage: $0 <path-to-dmg>"
  exit 1
fi

echo "Mounting $DMG..."
hdiutil attach "$DMG" -quiet

echo -e "\n=== SITL Directory Contents ==="
ls -la "/Volumes/INAV Configurator/INAV Configurator.app/Contents/Resources/sitl/" || echo "ERROR: SITL directory not found!"

echo -e "\n=== Checking for unwanted directories ==="
if [ -d "/Volumes/INAV Configurator/INAV Configurator.app/Contents/Resources/sitl/windows" ]; then
  echo "❌ FAIL: windows/ directory found (should not exist)"
else
  echo "✅ PASS: No windows/ directory"
fi

if [ -d "/Volumes/INAV Configurator/INAV Configurator.app/Contents/Resources/sitl/linux" ]; then
  echo "❌ FAIL: linux/ directory found (should not exist)"
else
  echo "✅ PASS: No linux/ directory"
fi

if [ -d "/Volumes/INAV Configurator/INAV Configurator.app/Contents/Resources/sitl/darwin" ]; then
  echo "✅ PASS: darwin/ directory exists (expected)"
else
  echo "❌ FAIL: darwin/ directory not found (should exist)"
fi

echo -e "\nUnmounting..."
hdiutil detach "/Volumes/INAV Configurator" -quiet

echo -e "\nDone!"
```

Save as `verify_dmg_sitl.sh`, make executable, and run:
```bash
chmod +x verify_dmg_sitl.sh
./verify_dmg_sitl.sh INAV-Configurator-9.0.0-RC5.dmg
```

---

## Why This Matters

**User Impact:**
- Smaller DMG download size
- Cleaner package without confusing non-native binaries
- Consistency across platforms

**Not Critical But Important:**
- This won't break functionality (SITL still works)
- But it's been wrong in previous releases
- Good to fix before final 9.0.0 release
- Shows attention to quality

---

## Questions?

If you have questions about verification or the fix doesn't work, contact:
- **Developer** (for technical questions)
- **Manager** (for release coordination)

Thank you for verifying this fix!

---
**Developer**
