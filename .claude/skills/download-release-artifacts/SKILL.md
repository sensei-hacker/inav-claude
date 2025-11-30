---
description: Download firmware hex files and configurator builds for an INAV release
triggers:
  - download release artifacts
  - download release files
  - download firmware
  - download configurator builds
  - get release artifacts
  - fetch release files
---

# Download Release Artifacts

This skill downloads firmware hex files from inav-nightly and configurator builds from GitHub Actions CI.

## Step 1: Get Release Version

Ask the user for the release version (e.g., "9.0.0-RC2").

```
VERSION="<user-provided>"
```

## Step 2: Download Firmware Hex Files

### Find the matching nightly release:

```bash
gh release list --repo iNavFlight/inav-nightly --limit 10
```

### Verify the nightly matches the firmware commit:

```bash
cd inav
git log -1 --format="%h %s" HEAD
```

### Download hex files:

```bash
NIGHTLY_TAG="<matching-tag>"  # e.g., v9.0.0-20251129.175

mkdir -p claude/release-manager/downloads/firmware-${VERSION}
cd claude/release-manager/downloads/firmware-${VERSION}
gh release download ${NIGHTLY_TAG} --repo iNavFlight/inav-nightly --pattern "*.hex"
```

### Verify firmware download:

```bash
ls *.hex | wc -l  # Should be ~219 files
```

### Rename firmware files:

Remove the CI build suffix and add RC number if applicable:

```bash
# For RC releases (e.g., 9.0.0-RC2):
# Changes: inav_9.0.0_ZEEZF7_ci-20251129-0e9f842.hex -> inav_9.0.0_RC2_ZEEZF7.hex
RC_NUM="RC2"  # Set to empty string for final releases
for f in *.hex; do
  # Extract target name (between version and _ci-)
  target=$(echo "$f" | sed -E 's/inav_[0-9]+\.[0-9]+\.[0-9]+_(.*)_ci-.*/\1/')
  version=$(echo "$f" | sed -E 's/inav_([0-9]+\.[0-9]+\.[0-9]+)_.*/\1/')
  if [ -n "$RC_NUM" ]; then
    newname="inav_${version}_${RC_NUM}_${target}.hex"
  else
    newname="inav_${version}_${target}.hex"
  fi
  mv "$f" "$newname"
done
```

```bash
# Verify renamed files
ls *.hex | head -5
```

## Step 3: Download Configurator Builds

### Find the CI workflow run:

```bash
cd inav-configurator
gh run list --limit 10 --json databaseId,headBranch,status,conclusion
```

### Download artifacts:

```bash
RUN_ID="<run-id>"

mkdir -p claude/release-manager/downloads/configurator-${VERSION}
cd claude/release-manager/downloads/configurator-${VERSION}
gh run download ${RUN_ID} --repo iNavFlight/inav-configurator
```

### Flatten the directory (gh creates subdirs):

```bash
find . -mindepth 2 -type f -exec mv {} . \;
rm -rf */
```

### Verify configurator download:

```bash
ls -la  # Should have 14-15 files (deb, rpm, zip, dmg, msi for all platforms)
```

## Step 4: Report Summary

After downloading, report:
- Firmware: Number of hex files downloaded
- Configurator: List of packages downloaded
- Any missing or failed downloads

## Directory Structure

Downloads will be organized as:

```
claude/release-manager/downloads/
├── firmware-<version>/           # Hex files (flat)
│   ├── inav_9.0.0_MATEKF405.hex
│   └── ...
└── configurator-<version>/       # Configurator packages (flat)
    ├── INAV-Configurator_linux_x64_9.0.0.deb
    ├── INAV-Configurator_MacOS_x64_9.0.0.dmg
    └── ...
```

## Human Action Required

After downloads complete, the human must:
1. Verify file counts look reasonable
2. Upload files to the draft GitHub releases
3. Test at least one firmware and configurator build
4. Publish the releases
