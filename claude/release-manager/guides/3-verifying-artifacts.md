# Phase 3: Verifying Release Artifacts

**Read this guide when:** After downloading artifacts, before creating releases

**Prerequisites:** Artifacts downloaded and organized by platform (Phase 2)

**Related guides:**
- [Phase 2: Downloading Artifacts](2-downloading-artifacts.md)
- [Phase 6: Creating Releases](6-creating-releases.md)

---

## Overview

This guide covers verification steps to ensure artifact quality before uploading to GitHub releases. These checks prevent critical issues like cross-platform contamination and missing dependencies.

---

## Verifying macOS DMG Contents

**CRITICAL:** Always verify macOS DMGs before uploading to prevent cross-platform contamination.

**Lesson learned (9.0.0 release):** A Windows .exe file was found inside a Mac DMG, breaking the macOS release.

### Using the Verification Script (Linux)

A verification script is available at: `claude/release-manager/scripts/verify-dmg-contents.sh`

```bash
# Verify all DMGs in a directory
./claude/release-manager/scripts/verify-dmg-contents.sh downloads/configurator-9.0.0-RC3/macos/*.dmg
```

**What it checks:**
- ✅ No Windows files (.exe, .dll, .msi)
- ✅ Valid Mach-O executable format
- ✅ Correct architecture (arm64 vs x86_64)
- ✅ Complete app bundle structure

**How it works:**
- Uses 7z to extract DMG to temporary directory
- Does NOT modify original DMG file
- Cleans up temp files after verification

### Manual Verification (macOS)

If on macOS, you can use native tools:

```bash
# Mount DMG read-only
hdiutil attach INAV-Configurator_MacOS_arm64_9.0.0.dmg -readonly -quiet

# Check for Windows files (should be zero)
find /Volumes/INAV-Configurator -name "*.exe" -o -name "*.dll" -o -name "*.msi" | wc -l

# Verify architecture
lipo -info "/Volumes/INAV-Configurator/INAV Configurator.app/Contents/MacOS/inav-configurator"

# Unmount
hdiutil detach /Volumes/INAV-Configurator -quiet
```

**Expected results:**
- Zero Windows files found
- Architecture matches DMG name (arm64 or x86_64)
- Executable is valid Mach-O format

### Verifying the macOS Code Signature

The release-ready macOS build is **code-signed + notarized** by `release.yml`; the nightly build signs+notarizes only when the full secret set is present (and is used as the pre-tag dry-run — see Phase 6). After downloading the release macOS artifact, confirm the signature is present and valid **before** uploading, and then leave the file untouched:

```bash
# Verify the signature on the app bundle (macOS only)
codesign --verify --deep --strict --verbose=2 "/path/to/INAV Configurator.app"

# Gatekeeper assessment (macOS only)
spctl --assess --type execute --verbose=4 "/path/to/INAV Configurator.app"

# Confirm the notarization ticket is stapled (macOS only)
xcrun stapler validate "/path/to/INAV Configurator.app"
```

- ✅ `codesign --verify` exits 0 and reports `valid on disk`
- ✅ `spctl --assess` accepts the app (no "damaged / unidentified developer" error)
- ✅ `xcrun stapler validate` confirms the notarization ticket is stapled

**Do not modify the `.app` or DMG after this check.** Re-zipping, re-bundling, or editing invalidates the signature. If a fix is needed, re-run the release CI — see Phase 1's [macOS Signing Sequencing](1-workflow-and-preparation.md#️-macos-signing-sequencing-critical).

---

## Verifying Windows SITL Files (cygwin1.dll)

**CRITICAL:** Windows SITL requires `cygwin1.dll` to run. Without it, users get "cygwin1.dll not found" errors and SITL fails to launch.

### Why This Matters

The Windows SITL binary (`inav_SITL.exe`) is built using Cygwin and requires the Cygwin runtime DLL to execute. This file must be bundled with the configurator.

### Using the Verification Script

A verification script is available at: `claude/release-manager/scripts/verify-windows-sitl.sh`

```bash
# Verify Windows configurator zip or extracted directory
./claude/release-manager/scripts/verify-windows-sitl.sh downloads/configurator-9.0.0-RC4/windows/INAV-Configurator_win_x64_9.0.0.zip
```

### Manual Verification

```bash
# For zip files - list contents and check for both required files
unzip -l INAV-Configurator_win_x64_9.0.0.zip | grep -E "(cygwin1.dll|inav_SITL.exe)"

# Expected output (both files must be present):
# Note: Packaged builds use resources/sitl/ (not resources/public/sitl/)
#    2953269  12-19-2024 01:41   resources/sitl/windows/cygwin1.dll
#    1517041  12-21-2024 17:25   resources/sitl/windows/inav_SITL.exe
```

### Path Differences

| Context | SITL Path |
|---------|-----------|
| Source repo | `resources/public/sitl/windows/` |
| Packaged builds | `resources/sitl/windows/` |

The `extraResource` config in `forge.config.js` copies `resources/public/sitl` to `resources/sitl` in packaged builds (see PR #2496).

### What to Check

- ✅ `cygwin1.dll` exists in `resources/sitl/windows/` (packaged) or `resources/public/sitl/windows/` (source)
- ✅ `inav_SITL.exe` exists in same directory
- ✅ File sizes are reasonable (cygwin1.dll ~2.9MB, inav_SITL.exe ~1.5MB)

### If cygwin1.dll is Missing

1. **DO NOT release** - Windows SITL will be broken
2. Check if the configurator repo has the file in `resources/public/sitl/windows/`
3. If missing from repo, obtain from a working Cygwin installation or previous release
4. Create PR to add/fix the file before proceeding with release

---

## Verifying Linux SITL (glibc Compatibility)

**CRITICAL:** Linux SITL binaries must support glibc versions in all non-EOL Ubuntu LTS releases.

### Why This Matters

- glibc is forward-compatible but NOT backward-compatible
- A binary compiled on Ubuntu 24.04 (glibc 2.39) will fail on Ubuntu 22.04 with errors like:
  ```
  /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.38' not found
  ```
- Users on older (but still supported) Ubuntu LTS releases would be unable to use SITL

### Current Requirements

| Period | Oldest Supported Ubuntu LTS | glibc Version |
|--------|----------------------------|---------------|
| 2025-2027 | Ubuntu 22.04.3 LTS | glibc 2.35 |

### How to Verify

```bash
# Check glibc version requirements of a binary
objdump -T downloads/sitl-9.0.0-RC3/resources/sitl/linux/inav_SITL | grep GLIBC | sed 's/.*GLIBC_//;s/ .*//' | sort -V | tail -1

# Expected output: 2.35 or lower
```

### If glibc Version is Too High

Build Linux x64 SITL locally on Ubuntu 22.04 LTS (see [Phase 4: Building Locally](4-building-locally.md)).

---

## Verifying the WASM SITL + PWA (10.x+)

The PWA build bundles an in-browser WASM build of SITL and is published alongside the desktop packages.

1. Confirm the WASM artifacts are present and versioned for this release:
   - `inav-configurator/js/web/WASM/inav_<firmware-version>_WASM.js` and `.wasm` exist and match the firmware being released
   - `js/web/SITL-Webassembly.js` imports that exact filename (no stale version string — see the WASM guide's "version-bump trap")
2. Build and smoke-test the PWA locally (`yarn web:build` → `yarn web:preview`), then open it in a real browser (not Electron): SITL tab → start WASM SITL → connect via the port picker's "SITL" entry. See the [WASM SITL + Browser/PWA Build](wasm-sitl-pwa-build.md) guide §4 for the full procedure and service-worker gotchas.
3. Verify the packaged PWA output (`dist-web/`) is the one uploaded — do not rebuild or edit it after the fact.

---

## Testing Artifacts Before Publishing

**CRITICAL:** A human must manually test configurator builds before uploading to the GitHub release. Automated verification (DMG checks, SITL file checks, glibc checks) catches structural issues but cannot validate that the application actually works.

### Human Testing Required (Before Upload)

Before uploading configurator artifacts to the draft release, a human tester must:

1. **Windows:** Extract the Win64 zip, launch the configurator, verify demo mode works and USB connection to an FC works
2. **Linux:** Extract the linux_x64 zip, launch the configurator, verify demo mode works and USB connection to an FC works
3. **macOS:** (if available) Open the DMG, launch the app, verify basic functionality

**Minimum:** Test on at least Windows and Linux with both demo mode and a real FC via USB.

This step cannot be performed by an AI agent - it requires a human with access to the operating system and hardware.

### SITL Testing

### Quick SITL Test Procedure

#### 1. Extract and Run the Configurator

Use your native platform build:

```bash
# Linux example
unzip INAV-Configurator_linux_x64_9.0.0.zip -d test-configurator
cd test-configurator
./inav-configurator
```

#### 2. Launch SITL from Configurator

- Open INAV Configurator
- Click "Setup" tab or "Simulator"
- Click "Start SITL" or similar button
- Verify SITL process launches without errors

#### 3. Verify SITL Connects

- Check that configurator detects SITL as a connected device
- Verify serial port/connection appears
- Test basic connection (read FC config)

#### 4. Check SITL Version Matches Firmware

- In configurator, check firmware version shown
- Should match the release version (e.g., 9.0.0-RC3)
- If mismatched, SITL binaries were not updated

### When to Test

- **After downloading artifacts** but before uploading to GitHub
- **After uploading to draft release** - can download from draft to verify
- **Before publishing release** - final check

### What Platforms to Test

**Minimum:**
- Test on your native platform (e.g., Linux x64)

**Ideal:**
- Test all three platforms (Linux, macOS, Windows)
- Test both architectures (x64 and arm64) if possible

**Reality:**
- At minimum, test the platform you're working on
- SITL is most critical to verify
- Other platform-specific issues rare after DMG verification

---

## Verification Checklist

Use this checklist before proceeding to Phase 6 (Creating Releases):

### Firmware Artifacts
- [ ] All hex files downloaded from inav-nightly
- [ ] Hex files renamed (CI suffix removed, RC number added if applicable)
- [ ] SITL binaries downloaded from nightly

### Configurator Artifacts
- [ ] All platforms downloaded from CI
- [ ] Files organized by platform (linux/, macos/, windows/)
- [ ] No directory flattening performed

### macOS Verification
- [ ] DMG contents verified (no .exe/.dll/.msi files)
- [ ] Architecture verified (arm64 vs x86_64 matches filename)
- [ ] Executable is valid Mach-O format
- [ ] Code signature verified (`codesign --verify` / `spctl --assess`) and artifact left unmodified

### Windows Verification
- [ ] cygwin1.dll present in resources/sitl/windows/
- [ ] inav_SITL.exe present in resources/sitl/windows/
- [ ] File sizes reasonable (~2.9MB and ~1.5MB)

### Linux Verification
- [ ] SITL glibc version ≤ 2.35 (verified with objdump)

### PWA / WASM SITL (10.x+)
- [ ] WASM artifacts in `js/web/WASM/` match the firmware version being released
- [ ] `js/web/SITL-Webassembly.js` imports the correct (non-stale) filename
- [ ] PWA built (`yarn web:build`) and smoke-tested in a real browser

### SITL Testing
- [ ] Configurator launches successfully
- [ ] SITL starts from configurator
- [ ] SITL connects to configurator
- [ ] SITL version matches firmware release version

### Post-Firmware-Publish Verification
- [ ] After publishing firmware release, open Configurator Firmware Flasher tab
- [ ] Enable "Show unstable releases"
- [ ] Verify the new firmware version appears in the release list
- [ ] Select a target whose name contains underscores (e.g., `MAMBAH743 2022B GYRO2`) and confirm it displays with spaces, not underscores — this validates that multi-word target names parse correctly
- [ ] Only then publish the configurator release

---

## Next Steps

Once all artifacts are verified:

**→ Proceed to [Phase 5: Changelog and Notes](5-changelog-and-notes.md)** (if not done yet)

OR

**→ Proceed to [Phase 6: Creating Releases](6-creating-releases.md)** (if changelog is ready)
