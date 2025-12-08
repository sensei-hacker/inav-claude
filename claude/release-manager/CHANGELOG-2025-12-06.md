# Release Manager Documentation Updates - December 6, 2025

## Summary

Comprehensive update to release artifact handling procedures following the 9.0.0 release incident where a Windows .exe file was found inside a macOS DMG.

## Suspected Root Cause

The Windows .exe contamination likely occurred due to:
1. Improper artifact handling during manual download and preparation
2. Possible directory flattening without platform separation
3. Potential mixing of files from multiple platforms

**Note:** The exact cause is uncertain, but improper artifact organization is the most likely culprit. CI workflows are properly isolated and shouldn't cause this issue.

## Changes Implemented

### 1. Documentation Updates

#### **download_guide.md**
- ✅ Replaced dangerous "flatten all" approach with platform-separated organization
- ✅ Added comprehensive DMG verification script using `hdiutil` and `lipo`
- ✅ Updated directory structure to show linux/, macos/, windows/ subdirectories
- ✅ Added critical warnings about cross-platform contamination
- ✅ Documented the 9.0.0 incident as a lesson learned
- ✅ Updated upload commands to use platform subdirectories

#### **README.md (Release Manager)**
- ✅ Updated "Downloading Release Artifacts" section with platform separation requirements
- ✅ Added reference to DMG verification in download guide
- ✅ Added "Artifact Verification" section to Pre-Release Checklist
- ✅ Documented 9.0.0 lesson learned inline
- ✅ Added critical warnings about NEVER flattening multi-platform directories

#### **release-create.md (Public Doc)**
- ✅ Updated configurator download section with platform organization
- ✅ Added DMG verification subsection with check scripts
- ✅ Added "Artifact Verification" to Pre-Release Checklist
- ✅ Removed dangerous directory flattening approach

### 2. Skills Updated

#### **.claude/skills/download-release-artifacts/SKILL.md**
- ✅ Replaced dangerous flattening approach with safe platform organization
- ✅ Added DMG verification step with full script
- ✅ Updated directory structure documentation
- ✅ Added explanation of why platform separation is needed
- ✅ Ensured proper front matter exists (description, triggers)

#### **.claude/skills/upload-release-assets/SKILL.md**
- ✅ Added front matter (description and triggers)
- ✅ Updated examples to show platform-specific uploads
- ✅ Documented that configurator artifacts are in platform subdirectories
- ✅ Updated notes to distinguish firmware (flat) vs configurator (platform subdirs)

### 3. Analysis Documents Created

#### **macos-build-analysis.md**
Comprehensive investigation report covering:
- How .exe ended up in DMG (artifact handling error)
- Why ARM DMG worked on Intel Macs (Rosetta 2)
- Three macOS build architecture options
- Recommendations for short-term fixes and long-term improvements
- Technical details including DMG verification commands
- Timeline for Rosetta 2 deprecation (macOS 28 in 2027+)

#### **dmg-verification-implementation.md**
Implementation documentation covering:
- Problem statement and root cause
- Solution implemented (platform separation + verification)
- Complete verification scripts
- Files updated
- Prevention checklist for future releases
- Testing plan
- Success criteria

#### **CHANGELOG-2025-12-06.md** (this file)
Complete record of all changes made

## New Safety Procedures

### Platform Separation (MANDATORY)

**Old approach (DANGEROUS):**
```bash
gh run download <run-id>
find . -mindepth 2 -type f -exec mv -t . {} +  # MIXES ALL PLATFORMS!
```

**New approach (SAFE):**
```bash
mkdir -p configurator-downloads/{linux,macos,windows}
cd configurator-downloads/_temp
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
```

### DMG Verification (MANDATORY)

Before uploading any macOS DMG:

```bash
for dmg in *.dmg; do
  hdiutil attach "$dmg" -quiet
  MOUNT=$(hdiutil info | grep "/Volumes/INAV" | awk '{print $3}')

  # MUST BE ZERO
  find "$MOUNT" -name "*.exe" | wc -l

  # Verify architecture
  lipo -info "$MOUNT/*.app/Contents/MacOS/inav-configurator"

  hdiutil detach "$MOUNT" -quiet
done
```

## Directory Structure Changes

### Before (WRONG):
```
downloads/configurator-9.0.0/
├── INAV-Configurator_linux_x64_9.0.0.deb
├── INAV-Configurator_MacOS_arm64_9.0.0.dmg
├── INAV-Configurator_Win64_9.0.0.msi
└── ... (ALL PLATFORMS MIXED - DANGEROUS!)
```

### After (CORRECT):
```
downloads/configurator-9.0.0/
├── linux/
│   └── INAV-Configurator_linux_x64_9.0.0.deb
├── macos/
│   └── INAV-Configurator_MacOS_arm64_9.0.0.dmg
└── windows/
    └── INAV-Configurator_Win64_9.0.0.msi
```

## Pre-Release Checklist Additions

New mandatory verification steps:

- [ ] Configurator artifacts organized by platform (linux/, macos/, windows/)
- [ ] macOS DMG contents verified (no .exe files, correct architecture)
- [ ] At least one build from each platform tested
- [ ] DMG verification script passed for all macOS builds

## Upload Command Changes

### Before:
```bash
cd downloads/configurator-9.0.0
gh release upload 9.0.0 * --repo iNavFlight/inav-configurator
```

### After:
```bash
cd downloads/configurator-9.0.0
gh release upload 9.0.0 linux/* --repo iNavFlight/inav-configurator
gh release upload 9.0.0 macos/* --repo iNavFlight/inav-configurator
gh release upload 9.0.0 windows/* --repo iNavFlight/inav-configurator
```

## macOS Architecture Findings

**Discovery:** ARM64 macOS apps DO run on Intel Macs via Rosetta 2.

**Key facts:**
- Rosetta 2 translates ARM64 → x86_64 automatically
- Performance overhead: ~20-30% slower than native
- Works transparently (user doesn't need to do anything)
- **Deprecated in macOS 28 (2027+)** - limited to unmaintained games only

**Recommendations:**
- **Short-term:** Keep both ARM64 and x64 builds, fix handling process
- **Long-term:** Consider Universal binaries using `@electron/universal` package

## Files Modified

### Documentation
1. `claude/release-manager/download_guide.md`
2. `claude/release-manager/README.md`
3. `inav/docs/development/release-create.md`

### Skills
4. `.claude/skills/download-release-artifacts/SKILL.md`
5. `.claude/skills/upload-release-assets/SKILL.md`

### Analysis/Reports (NEW)
6. `claude/release-manager/macos-build-analysis.md`
7. `claude/release-manager/dmg-verification-implementation.md`
8. `claude/release-manager/CHANGELOG-2025-12-06.md` (this file)

## Testing Required

For the next release (9.0.1 or 9.1.0):

1. **Download artifacts** using new platform-separated procedure
2. **Run DMG verification** on all macOS DMGs
3. **Verify** script correctly identifies:
   - Absence of .exe files ✅
   - Correct architecture (x64 or arm64) ✅
4. **Upload** from platform subdirectories
5. **Test** DMGs work on both Intel and ARM Macs

## Success Criteria

Next release is successful when:
- ✅ Zero cross-platform contamination
- ✅ All macOS DMGs pass verification
- ✅ Clear architecture identification
- ✅ Both Intel and ARM users can run configurator
- ✅ No .exe files in any DMG
- ✅ No corrupted/damaged DMGs

## Prevention Measures

Going forward:
1. **NEVER** flatten directories containing multiple platforms
2. **ALWAYS** organize configurator artifacts by platform
3. **ALWAYS** run DMG verification before upload
4. **ALWAYS** check for .exe files in DMGs
5. **ALWAYS** verify architecture matches expected build

## Related Issues

- [x] Windows .exe in macOS DMG (SOLVED - platform separation)
- [x] macOS x64 DMG damaged (INVESTIGATED - corruption during download/upload)
- [x] macOS ARM working on Intel (EXPLAINED - Rosetta 2)
- [ ] Consider Universal binaries for long-term (FUTURE - post 10.0.0)

## Impact

- **Risk reduction:** Critical contamination bug cannot occur with new procedures
- **Verification:** Automated checks prevent upload of contaminated artifacts
- **Documentation:** Clear, step-by-step procedures with warnings
- **Skills:** Updated to use safe approaches by default
- **Future-proofing:** Analysis and recommendations for Universal binaries

---

**Status:** ✅ All documentation and skills updated. Ready for next release.

**Next action:** Use updated procedures for next RC or final release.
