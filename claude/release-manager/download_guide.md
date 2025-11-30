# Downloading Release Artifacts

This guide documents how to download firmware hex files and configurator builds for INAV releases.

## Directory Structure

After downloading, release artifacts should be organized as:

```
downloads/
├── <version>/                    # Firmware hex files (flat, renamed)
│   ├── inav_9.0.0_RC2_MATEKF405.hex
│   ├── inav_9.0.0_RC2_SPEEDYBEEF7V3.hex
│   └── ...
├── configurator-<version>/       # Configurator builds (flat)
│   ├── INAV-Configurator_linux_arm64_9.0.0.deb
│   ├── INAV-Configurator_linux_arm64_9.0.0.rpm
│   ├── INAV-Configurator_linux_arm64_9.0.0.zip
│   ├── INAV-Configurator_linux_x64_9.0.0.deb
│   ├── INAV-Configurator_linux_x64_9.0.0.rpm
│   ├── INAV-Configurator_linux_x64_9.0.0.zip
│   ├── INAV-Configurator_MacOS_arm64_9.0.0.dmg
│   ├── INAV-Configurator_MacOS_arm64_9.0.0.zip
│   ├── INAV-Configurator_MacOS_x64_9.0.0.dmg
│   ├── INAV-Configurator_MacOS_x64_9.0.0.zip
│   ├── INAV-Configurator_Win32_9.0.0.msi
│   ├── INAV-Configurator_Win32_9.0.0.zip
│   ├── INAV-Configurator_Win64_9.0.0.msi
│   └── INAV-Configurator_Win64_9.0.0.zip
└── download_guide.md             # This file
```

**IMPORTANT:** Both directories should be FLAT (no subdirectories). This makes it easier to upload files to GitHub releases.

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

for f in *.hex; do
  target=$(echo "$f" | sed -E 's/inav_[0-9]+\.[0-9]+\.[0-9]+_(.*)_ci-.*/\1/')
  version=$(echo "$f" | sed -E 's/inav_([0-9]+\.[0-9]+\.[0-9]+)_.*/\1/')
  if [ -n "$RC_NUM" ]; then
    mv "$f" "inav_${version}_${RC_NUM}_${target}.hex"
  else
    mv "$f" "inav_${version}_${target}.hex"
  fi
done
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

```bash
VERSION="9.0.0-rc2"
RUN_ID="12345678"  # From step 1

mkdir -p claude/release-manager/downloads/configurator-${VERSION}
cd claude/release-manager/downloads/configurator-${VERSION}
gh run download ${RUN_ID} --repo iNavFlight/inav-configurator
```

### 3. Flatten the Directory

The `gh run download` command creates subdirectories for each artifact. Flatten them:

```bash
# Move all files to root and remove subdirectories
find . -mindepth 2 -type f -exec mv {} . \;
rm -rf */

# Verify - should have 14-15 files
ls -la
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

After downloading and flattening, upload to the draft release:

```bash
# Upload firmware hex files
cd claude/release-manager/downloads/9.0.0-rc2
gh release upload 9.0.0-RC2 *.hex --repo iNavFlight/inav

# Upload configurator packages
cd claude/release-manager/downloads/configurator-9.0.0-rc2
gh release upload 9.0.0-RC2 * --repo iNavFlight/inav-configurator
```

## Human Action Required

After Claude downloads the artifacts:

1. **Verify the downloads** - Check file counts and sizes look reasonable
2. **Upload to draft releases** - Use the commands above or GitHub web UI
3. **Test at least one build** - Flash firmware and run configurator to verify they work
4. **Publish releases** - After verification, publish both releases
