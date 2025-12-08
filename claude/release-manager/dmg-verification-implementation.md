# DMG Verification Implementation - Documentation Update

**Date:** 2025-12-06
**Release Manager:** Implementation of safeguards to prevent 9.0.0 DMG issue

## Problem Statement

During the 9.0.0 release:
1. A Windows .exe file was found inside a macOS DMG
2. The Mac x64 DMG was corrupted/damaged
3. The Mac ARM64 DMG worked on both ARM and Intel Macs (via Rosetta 2)

## Suspected Root Cause

The Windows .exe in Mac DMG issue was likely caused by one or more of:
- Downloading all CI artifacts to a single directory
- Flattening the directory structure without platform separation
- Mixing Windows, macOS, and Linux files together during manual handling
- Improper artifact organization before DMG creation

**Note:** The exact cause is uncertain, but these are the most likely scenarios based on investigation.

## Solution Implemented

### 1. Platform Separation During Download

**Old approach (DANGEROUS):**
```bash
gh run download <run-id>
find . -mindepth 2 -type f -exec mv -t . {} +  # MIXES ALL PLATFORMS!
```

**New approach (SAFE):**
```bash
mkdir -p configurator-downloads/{linux,macos,windows}
cd configurator-downloads
mkdir _temp && cd _temp
gh run download <run-id>

# Organize by platform
find . -name "*linux*" | while read artifact; do
  find "$artifact" -type f -exec mv {} ../linux/ \;
done

find . -name "*MacOS*" | while read artifact; do
  find "$artifact" -type f -exec mv {} ../macos/ \;
done

find . -name "*Win*" | while read artifact; do
  find "$artifact" -type f -exec mv {} ../windows/ \;
done

cd .. && rm -rf _temp
```

### 2. DMG Verification Script

Added verification script to check DMG contents before upload:

```bash
cd macos/
for dmg in *.dmg; do
  echo "Verifying: $dmg"

  # Mount the DMG
  hdiutil attach "$dmg" -quiet
  MOUNT_POINT=$(hdiutil info | grep "/Volumes/INAV" | awk '{print $3}')

  # Check for Windows executables (SHOULD BE NONE)
  EXE_COUNT=$(find "$MOUNT_POINT" -name "*.exe" 2>/dev/null | wc -l)
  if [ "$EXE_COUNT" -gt 0 ]; then
    echo "  ❌ ERROR: Found .exe files in macOS DMG!"
    find "$MOUNT_POINT" -name "*.exe"
  else
    echo "  ✓ No .exe files found"
  fi

  # Check architecture
  BINARY="$MOUNT_POINT/*.app/Contents/MacOS/inav-configurator"
  ARCH=$(lipo -info "$BINARY" 2>/dev/null)
  echo "  Architecture: $ARCH"

  # Unmount
  hdiutil detach "$MOUNT_POINT" -quiet
done
```

## Files Updated

### 1. download_guide.md
**Changes:**
- ✅ Updated directory structure to show platform separation
- ✅ Added WARNING about cross-platform contamination
- ✅ Documented the 9.0.0 incident as a lesson learned
- ✅ Replaced dangerous "flatten" step with platform-organized approach
- ✅ Added comprehensive DMG verification script
- ✅ Updated upload commands to use platform subdirectories

**New directory structure:**
```
configurator-<version>/
├── linux/
│   └── [Linux packages]
├── macos/
│   └── [macOS packages]
└── windows/
    └── [Windows packages]
```

### 2. Release Manager README.md
**Changes:**
- ✅ Updated key points in "Downloading Release Artifacts" section
- ✅ Added critical warnings about platform separation
- ✅ Added reference to DMG verification in download guide
- ✅ Added "Artifact Verification" section to Pre-Release Checklist
- ✅ Documented the 9.0.0 lesson learned

**New checklist items:**
```
### Artifact Verification
- [ ] Firmware hex files downloaded and renamed
- [ ] Configurator artifacts organized by platform (linux/, macos/, windows/)
- [ ] macOS DMG contents verified (no .exe files, correct architecture)
- [ ] At least one build from each platform tested
```

### 3. inav/docs/development/release-create.md (Public Doc)
**Changes:**
- ✅ Updated configurator download section with platform separation
- ✅ Added DMG verification subsection
- ✅ Added "Artifact Verification" to Pre-Release Checklist
- ✅ Replaced dangerous flattening approach with safe organization

## Verification Commands Reference

### Check for .exe files in DMG:
```bash
hdiutil attach "INAV-Configurator_MacOS_x64_9.0.0.dmg"
find /Volumes/INAV-Configurator/ -name "*.exe"
# Should return NOTHING
hdiutil detach /Volumes/INAV-Configurator/
```

### Check DMG architecture:
```bash
hdiutil attach "INAV-Configurator_MacOS_x64_9.0.0.dmg"
lipo -info "/Volumes/INAV-Configurator/INAV Configurator.app/Contents/MacOS/inav-configurator"
# Expected outputs:
# x64 build:    "Non-fat file: ... is architecture: x86_64"
# ARM64 build:  "Non-fat file: ... is architecture: arm64"
# Universal:    "Architectures in the fat file: ... are: x86_64 arm64"
hdiutil detach /Volumes/INAV-Configurator/
```

## Prevention Checklist for Future Releases

Before uploading configurator builds to GitHub release:

- [ ] Artifacts are organized in platform subdirectories (linux/, macos/, windows/)
- [ ] NO flattening of multi-platform directories was performed
- [ ] DMG verification script was run on all macOS DMGs
- [ ] No .exe files found in any DMG
- [ ] Architecture verified for each DMG (x64 vs arm64)
- [ ] At least one DMG tested by mounting and launching the app

## Additional Findings: macOS Architecture

**Research finding:** macOS ARM64 builds DO work on Intel Macs via Rosetta 2.

**Why the ARM DMG worked on Intel:**
- Rosetta 2 automatically translates ARM64 → x86_64
- Performance overhead: ~20-30% slower than native x64
- Transparent to the user (no special action needed)

**Rosetta 2 Timeline:**
- 2025-2027: Fully supported
- macOS 27 (2027): Last version with full support
- macOS 28+ (2027+): Limited to unmaintained games only

**Long-term recommendation:** Consider implementing Universal binaries using `@electron/universal` package.

## Testing Performed

All verification scripts have been added to documentation. Testing required on next release:

1. Download configurator artifacts using new platform-separated approach
2. Run DMG verification script on all macOS DMGs
3. Verify script correctly identifies:
   - Absence of .exe files
   - Correct architecture (x64 or arm64)
4. Upload artifacts from platform subdirectories
5. Verify uploaded DMGs work correctly on both Intel and ARM Macs

## Success Criteria

For the next release, success is:
- ✅ Zero cross-platform contamination (no .exe in DMG)
- ✅ All macOS DMGs pass verification script
- ✅ Clear architecture identification (x64 vs arm64)
- ✅ Both Intel and ARM Mac users can run the configurator

## Related Documents

- [macOS Build Analysis](macos-build-analysis.md) - Detailed investigation of the 9.0.0 issues
- [Download Guide](download_guide.md) - Complete guide with verification scripts
- [Release Manager README](README.md) - Updated with new procedures

---

**Status:** ✅ Documentation complete. Ready for next release validation.
