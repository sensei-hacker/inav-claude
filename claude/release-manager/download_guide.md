# Downloading Release Artifacts

This guide documents how to download firmware hex files and configurator builds for INAV releases.

## Directory Structure

After downloading, release artifacts should be organized as:

```
downloads/
├── <version>/                         # Firmware hex files (flat, renamed)
│   ├── inav_9.0.0_RC2_MATEKF405.hex
│   ├── inav_9.0.0_RC2_SPEEDYBEEF7V3.hex
│   └── ...
├── configurator-<version>/            # Configurator builds (ORGANIZED BY PLATFORM)
│   ├── linux/
│   │   ├── INAV-Configurator_linux_arm64_9.0.0.deb
│   │   ├── INAV-Configurator_linux_arm64_9.0.0.rpm
│   │   ├── INAV-Configurator_linux_arm64_9.0.0.zip
│   │   ├── INAV-Configurator_linux_x64_9.0.0.deb
│   │   ├── INAV-Configurator_linux_x64_9.0.0.rpm
│   │   └── INAV-Configurator_linux_x64_9.0.0.zip
│   ├── macos/
│   │   ├── INAV-Configurator_MacOS_arm64_9.0.0.dmg
│   │   ├── INAV-Configurator_MacOS_arm64_9.0.0.zip
│   │   ├── INAV-Configurator_MacOS_x64_9.0.0.dmg
│   │   └── INAV-Configurator_MacOS_x64_9.0.0.zip
│   └── windows/
│       ├── INAV-Configurator_Win32_9.0.0.msi
│       ├── INAV-Configurator_Win32_9.0.0.zip
│       ├── INAV-Configurator_Win64_9.0.0.msi
│       └── INAV-Configurator_Win64_9.0.0.zip
└── download_guide.md                  # This file
```

**CRITICAL:** Configurator builds MUST be organized by platform in separate subdirectories. This prevents cross-platform contamination (e.g., Windows .exe files ending up in macOS DMGs).

**Why platform separation is required:**
- In the 9.0.0 release, a Windows .exe file was found inside a Mac DMG
- The cause is uncertain, but flattening directories containing multiple platforms is a likely culprit
- Platform separation and verification ensure clean, verified builds for each OS

## Downloading Firmware Hex Files

Firmware hex files are available from the nightly build system.

### 1. Find the Latest Nightly Release

```bash
gh release list --repo iNavFlight/inav-nightly --limit 5
```

### 2. Create Directory and Download

```bash
VERSION="9.0.0-rc2"
NIGHTLY_TAG="v9.0.0-20251129.175"  # Use the tag from step 1

mkdir -p claude/release-manager/downloads/${VERSION}
cd claude/release-manager/downloads/${VERSION}
gh release download ${NIGHTLY_TAG} --repo iNavFlight/inav-nightly --pattern "*.hex"
```

### 3. Verify Download

```bash
ls *.hex | wc -l  # Should be ~219 files
```

### 4. Rename Firmware Files

Remove CI build suffix and add RC number for RC releases:

```bash
# Set RC_NUM for RC releases, or empty for final releases
RC_NUM="RC2"

# Check if any .hex files exist to avoid errors with the glob
if compgen -G "*.hex" > /dev/null; then
  for f in *.hex; do
    target=$(echo "$f" | sed -E 's/inav_[0-9]+\.[0-9]+\.[0-9]+_(.*)_ci-.*/\1/')
    version=$(echo "$f" | sed -E 's/inav_([0-9]+\.[0-9]+\.[0-9]+)_.*/\1/')
    if [ -n "$RC_NUM" ]; then
      mv "$f" "inav_${version}_${RC_NUM}_${target}.hex"
    else
      mv "$f" "inav_${version}_${target}.hex"
    fi
  done
else
  echo "No .hex files found to rename."
fi
```

This changes filenames from:
- `inav_9.0.0_MATEKF405_ci-20251129-0e9f842.hex`

To:
- RC release: `inav_9.0.0_RC2_MATEKF405.hex`
- Final release: `inav_9.0.0_MATEKF405.hex`

## Downloading Configurator Builds

Configurator builds are available from GitHub Actions CI artifacts.

### 1. Find the CI Workflow Run

Go to: https://github.com/iNavFlight/inav-configurator/actions

Or use CLI:
```bash
gh run list --repo iNavFlight/inav-configurator --limit 10
```

### 2. Download Artifacts

**IMPORTANT:** Keep each platform in separate subdirectories to prevent cross-platform contamination. Do NOT flatten directories containing multiple platforms.

```bash
VERSION="9.0.0-rc2"
RUN_ID="12345678"  # From step 1

# Create platform-specific directories
BASE_DIR="claude/release-manager/downloads/configurator-${VERSION}"
mkdir -p "${BASE_DIR}"/{linux,macos,windows}

# Download all artifacts to a temp directory first
cd "${BASE_DIR}"
mkdir -p _temp
cd _temp
gh run download ${RUN_ID} --repo iNavFlight/inav-configurator
```

### 3. Organize by Platform

**CRITICAL STEP:** Organize artifacts by platform to prevent mixing.

```bash
# Move Linux artifacts
find . -name "*linux*" -o -name "*_DEB" -o -name "*_RPM" | while read artifact; do
  find "$artifact" -type f -exec mv {} ../linux/ \;
done

# Move macOS artifacts
find . -name "*MacOS*" -o -name "*darwin*" -o -name "*_DMG" | while read artifact; do
  find "$artifact" -type f -exec mv {} ../macos/ \;
done

# Move Windows artifacts
find . -name "*Win*" -o -name "*_MSI" | while read artifact; do
  find "$artifact" -type f -exec mv {} ../windows/ \;
done

# Remove temp directory and empty subdirs
cd ..
rm -rf _temp

# Verify organization
echo "=== Linux artifacts ==="
ls -lh linux/
echo "=== macOS artifacts ==="
ls -lh macos/
echo "=== Windows artifacts ==="
ls -lh windows/
```

### 4. Verify macOS DMG Contents

**CRITICAL:** Before uploading macOS DMGs, verify they don't contain Windows executables.

```bash
cd macos/

# Check each DMG
for dmg in *.dmg; do
  echo "Verifying: $dmg"

  # Mount the DMG
  hdiutil attach "$dmg" -quiet

  # Find the volume name (should be INAV-Configurator)
  VOLUME=$(hdiutil info | grep "/Volumes/INAV" | awk '{print $1}')
  MOUNT_POINT=$(hdiutil info | grep "/Volumes/INAV" | awk '{print $3}')

  # Check for Windows executables (SHOULD BE NONE)
  echo "  Checking for .exe files..."
  EXE_COUNT=$(find "$MOUNT_POINT" -name "*.exe" 2>/dev/null | wc -l)
  if [ "$EXE_COUNT" -gt 0 ]; then
    echo "  ❌ ERROR: Found .exe files in macOS DMG!"
    find "$MOUNT_POINT" -name "*.exe"
  else
    echo "  ✓ No .exe files found"
  fi

  # Check architecture
  echo "  Checking architecture..."
  APP_PATH=$(find "$MOUNT_POINT" -name "*.app" -maxdepth 2 | head -1)
  if [ -n "$APP_PATH" ]; then
    BINARY="$APP_PATH/Contents/MacOS/inav-configurator"
    if [ -f "$BINARY" ]; then
      ARCH=$(lipo -info "$BINARY" 2>/dev/null | tail -1)
      echo "  Architecture: $ARCH"
    fi
  fi

  # Unmount
  hdiutil detach "$MOUNT_POINT" -quiet
  echo ""
done

cd ..
```

## Current Release Downloads

### 9.0.0-RC2

**Firmware:**
- Location: `downloads/9.0.0-rc2/`
- Source: https://github.com/iNavFlight/inav-nightly/releases/tag/v9.0.0-20251129.175
- Files: 219 hex files
- Downloaded: 2025-11-30

**Configurator:**
- Location: `downloads/configurator-9.0.0-rc2/`
- Source: GitHub Actions CI (commit 62045e3)
- Files: 15 packages (deb, rpm, zip, dmg, msi for all platforms)
- Downloaded: 2025-11-30

## Uploading to GitHub Release

After downloading, organizing, and verifying, upload to the draft release:

```bash
VERSION="9.0.0-rc2"
RELEASE_TAG="9.0.0-RC2"

# Upload firmware hex files
cd claude/release-manager/downloads/${VERSION}
gh release upload ${RELEASE_TAG} *.hex --repo iNavFlight/inav

# Upload configurator packages - BY PLATFORM
cd claude/release-manager/downloads/configurator-${VERSION}

# Upload Linux packages
gh release upload ${RELEASE_TAG} linux/* --repo iNavFlight/inav-configurator

# Upload macOS packages
gh release upload ${RELEASE_TAG} macos/* --repo iNavFlight/inav-configurator

# Upload Windows packages
gh release upload ${RELEASE_TAG} windows/* --repo iNavFlight/inav-configurator
```

## Human Action Required

After Claude downloads the artifacts:

1. **Verify the downloads** - Check file counts and sizes look reasonable
2. **Upload to draft releases** - Use the commands above or GitHub web UI
3. **Test at least one build** - Flash firmware and run configurator to verify they work
4. **Publish releases** - After verification, publish both releases
