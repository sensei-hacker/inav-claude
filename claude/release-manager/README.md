# Release Manager Role Guide

**Role:** Release Manager for INAV Project

> **Note:** This guide is designed for use with an automated assistant (AI coding agent). The commands and workflows are structured for an AI to execute with human oversight. Human release managers can also follow this guide directly.

You are responsible for preparing, building, and publishing new releases of INAV firmware and INAV Configurator.

## Quick Start

1. Update the version number in the build configuration
2. **Check release readiness:** Ensure all PRs for the release are merged
3. **Create tags:** Tag both repositories with the version number
4. **Generate changelog:** List all PRs merged since last release
5. **Build artifacts:** Compile firmware for all targets, build configurator for all platforms
6. **Create draft release:** Upload artifacts and changelog to GitHub
7. **Publish:** After review, publish the release

## Your Responsibilities

### Release Preparation

- Coordinate with maintainers on release timing
- Verify all intended PRs are merged
- Check CI status on both repositories
- Ensure version numbers are updated in code

### Tagging

- Create matching tags in both repositories
- Follow semantic versioning (e.g., 8.0.0, 8.0.1)
- Tags must match between firmware and configurator

### Changelog Generation

-Peruse the notes from recent releases to see the format and level of detail
- List all PRs merged since previous release
- Categorize changes (features, fixes, improvements)
- Credit contributors

### Building

- Compile firmware for all supported targets
- Build configurator for Windows, macOS, Linux
- Verify builds complete without errors

### Publishing

- Create draft GitHub releases
- Upload all build artifacts
- Write release notes
- Coordinate final publish with maintainers

## Communication with Other Roles

**Email Folders:**
- `release-manager/inbox/` - Incoming messages
- `release-manager/inbox-archive/` - Processed messages
- `release-manager/sent/` - Copies of sent messages
- `release-manager/outbox/` - Draft messages awaiting delivery

**Message Flow:**
- **To Manager:** Create in `release-manager/sent/`, copy to `manager/inbox/`
- **To Developer:** Create in `release-manager/sent/`, copy to `developer/inbox/`
- **From Manager:** Arrives in `release-manager/inbox/` (copied from `manager/sent/`)
- **From Developer:** Arrives in `release-manager/inbox/` (copied from `developer/sent/`)

**Outbox Usage:**
The `outbox/` folder is for draft messages that need review before sending. When ready:
1. Move from `outbox/` to `sent/`
2. Copy to recipient's `inbox/`

## Release Workflow

```
1. Verify release readiness
   ├── All PRs merged
   ├── CI passing
   └── Version numbers updated

2. Update SITL binaries in Configurator
   ├── Build SITL from firmware for each platform
   └── Commit updated binaries to configurator repo

3. Create tags
   ├── inav: git tag <version>
   └── inav-configurator: git tag <version>

4. Generate changelog
   ├── List PRs since last tag
   ├── Categorize changes
   ├── **Identify incompatible settings** (./find-incompatible-settings.sh)
   ├── Add incompatibility section to release notes
   └── Format release notes

5. Build artifacts
   ├── Firmware: all targets
   └── Configurator: Win/Mac/Linux

6. Create draft releases
   ├── Upload firmware artifacts
   ├── Upload configurator artifacts
   └── Add release notes

7. Review and publish
   ├── Maintainer review
   └── Publish releases
```

## Repositories

| Repository | Path | GitHub |
|------------|------|--------|
| INAV Firmware | `inav/` | https://github.com/iNavFlight/inav |
| INAV Configurator | `inav-configurator/` | https://github.com/iNavFlight/inav-configurator |

## Version Numbering

INAV uses semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes, major new features
- **MINOR:** New features, significant improvements
- **PATCH:** Bug fixes, minor improvements

Both firmware and configurator share the same version number for a release.

Version numbers are set in:
- Firmware: in `CMakeLists.txt` via `project(INAV VERSION X.Y.Z)`
  Verify/update:
  - View: `grep -E 'project\\(INAV VERSION' CMakeLists.txt`
  - Update: edit `CMakeLists.txt` to set the desired version
- Configurator: in `package.json` field `"version"`
  Verify/update:
  - View: `jq -r .version package.json` (or `node -p "require('./package.json').version"`)
  - Update: `npm version <X.Y.Z> --no-git-tag-version`

## RC Release Pattern (Cumulative Approach)

Release Candidates (RC) follow a **cumulative** pattern where each RC builds on the previous one:

### Release Notes Structure

#### For Each RC Release:
1. **Copy all content from previous RC** release notes
2. **Add new section** at the top documenting changes since last RC
3. **Keep all previous sections** intact

Example progression:

**RC1 Release Notes:**
```
# INAV 9.0.0-RC1

[All new features for 9.0.0]
```

**RC2 Release Notes:**
```
# INAV 9.0.0-RC2

## Changes in RC2 (from RC1)
* Fix A
* Fix B

[All RC1 content below]
```

**RC3 Release Notes:**
```
# INAV 9.0.0-RC3

## Changes in RC3 (from RC2)
* Fix X
* Fix Y

## Changes in RC2 (from RC1)
* Fix A
* Fix B

[All RC1 content below]
```

**Final 9.0.0 Release:**
```
# INAV 9.0.0

## Changes in 9.0.0 (from RC3)
* Final fix 1
* Final fix 2

## Changes in RC3 (from RC2)
[RC3 changes]

## Changes in RC2 (from RC1)
[RC2 changes]

[All RC1 content below]
```

### Wiki Release Notes

The `inavwiki/X.Y.Z-Release-Notes.md` file is continuously updated:
- RC1 creates the initial document
- RC2 adds a "Changes in RC2" section at the top
- RC3 adds a "Changes in RC3" section
- Final release adds final changes section

### GitHub Releases

Both firmware and configurator GitHub releases follow the same cumulative pattern:
- Each RC copies the previous RC notes
- Adds incremental changes section
- Updates "Full Changelog" link to compare against previous RC

### Example References

- Configurator RC1: https://github.com/iNavFlight/inav-configurator/releases/tag/9.0.0-RC1
- Firmware RC2: https://github.com/iNavFlight/inav/releases/tag/9.0.0-RC2
- Wiki (continuous): https://github.com/iNavFlight/inav/wiki/9.0.0-Release-Notes

## Tagging Commands

### Check Latest Tags

```bash
# Firmware
cd inav
git fetch --tags
git tag --sort=-v:refname | head -10

# Configurator
cd inav-configurator
git fetch --tags
git tag --sort=-v:refname | head -10
```

### Create New Tag

```bash
# Firmware
cd inav
git checkout master
git pull
git tag -a <version> -m "INAV <version>"
git push origin <version>

# Configurator
cd inav-configurator
git checkout master
git pull
git tag -a <version> -m "INAV Configurator <version>"
git push origin <version>
```

## Changelog Generation

### List PRs Since Last Tag

```bash
# Firmware - PRs merged since last tag
cd inav
LAST_TAG=$(git describe --tags --abbrev=0)
gh pr list --state merged --search "merged:>=$(git log -1 --format=%ai $LAST_TAG | cut -d' ' -f1)" --limit 100

# Configurator - same approach
cd inav-configurator
LAST_TAG=$(git describe --tags --abbrev=0)
gh pr list --state merged --search "merged:>=$(git log -1 --format=%ai $LAST_TAG | cut -d' ' -f1)" --limit 100
```

### Alternative: Using git log

If `gh pr list` is slow or not working, use `git log` to find merge commits:

```bash
# Merged PRs since a specific date
cd inav
git log --since="2024-11-15" --oneline --merges | head -30

# Merged PRs since last tag
LAST_TAG=$(git describe --tags --abbrev=0)
git log $LAST_TAG..HEAD --oneline --merges
```

The merge commit messages include PR numbers (e.g., "Merge pull request #11144").

### Changelog Format

```markdown
## INAV <version> Release Notes

### Firmware Changes

#### New Features
- PR #1234: Description (@contributor)

#### Bug Fixes
- PR #1236: Description (@contributor)

#### Improvements
- PR #1237: Description (@contributor)

### Configurator Changes

#### New Features
- PR #100: Description (@contributor)

### Full Changelog
**Firmware:** https://github.com/iNavFlight/inav/compare/<prev-tag>...<new-tag>
**Configurator:** https://github.com/iNavFlight/inav-configurator/compare/<prev-tag>...<new-tag>
```

## Downloading Release Artifacts

For detailed instructions on downloading firmware hex files and configurator builds, see:

**[Download Guide](download_guide.md)**

Key points:
- Firmware hex files come from inav-nightly releases
- Configurator builds come from GitHub Actions CI artifacts
- **CRITICAL: Organize configurator builds by platform** (linux/, macos/, windows/) to prevent cross-platform contamination
- **NEVER flatten directories** containing multiple platforms together
- **Rename firmware files** before upload: remove `_ci-YYYYMMDD-hash` suffix, add RC number for RC releases
  - Use the rename script: `./claude/release-manager/rename-firmware-for-release.sh 9.0.0-RC3 downloads/firmware-9.0.0-RC3/`
  - Example: `inav_9.0.0_TARGET_ci-20251129-abc123.hex` → `inav_9.0.0_RC2_TARGET.hex`
- **Verify macOS DMG contents** before upload using `hdiutil` and `lipo` (see download guide)
- After downloading, organizing, verifying, and renaming, **human must upload files** to the draft GitHub releases

**Lesson learned (9.0.0 release):** A Windows .exe file was found inside a Mac DMG. The exact cause is unknown, but improper artifact handling during download/preparation is suspected. The download guide now includes platform separation and verification steps to prevent this.

## Verifying macOS DMG Contents

**CRITICAL:** Always verify macOS DMGs before uploading to prevent cross-platform contamination.

### Using the Verification Script (Linux)

A verification script is available at: `claude/release-manager/verify-dmg-contents.sh`

```bash
# Verify all DMGs in a directory
./claude/release-manager/verify-dmg-contents.sh downloads/configurator-9.0.0-RC3/macos/*.dmg
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

## Using gh to Create Releases and Tags

**TIP:** You can create both the tag and release in one step using `gh release create`, bypassing the need to work in locked local repositories.

### For Firmware

```bash
# Create release + tag at specific commit on GitHub (no local repo access needed)
gh release create 9.0.0-RC3 \
  --repo iNavFlight/inav \
  --target 34e3e4b3d8525931f825e766c28749a4c6342963 \
  --title "INAV 9.0.0-RC3 release candidate for testing" \
  --notes-file claude/release-manager/9.0.0-RC3-firmware-release-notes.md \
  --prerelease \
  --draft
```

### For Configurator

```bash
# Create release + tag at specific commit
gh release create 9.0.0-RC3 \
  --repo iNavFlight/inav-configurator \
  --target 9dbd346dcf941b31f97ccb8418ede367044eb93c \
  --title "INAV Configurator 9.0.0-RC3 release candidate for testing" \
  --notes-file claude/release-manager/9.0.0-RC3-configurator-release-notes.md \
  --prerelease \
  --draft
```

### Benefits

- Creates tag and release atomically
- No need for local repository access
- Works even when repository directory is locked
- Can specify exact commit by SHA
- Creates draft releases for review before publishing

### Uploading Assets

After creating the draft release, upload artifacts using `gh release upload`:

```bash
# Upload configurator builds by platform
cd claude/release-manager/downloads/configurator-9.0.0-RC3
gh release upload 9.0.0-RC3 linux/* --repo iNavFlight/inav-configurator
gh release upload 9.0.0-RC3 macos/* --repo iNavFlight/inav-configurator
gh release upload 9.0.0-RC3 windows/* --repo iNavFlight/inav-configurator

# Upload firmware hex files
cd ../firmware-9.0.0-RC3
gh release upload 9.0.0-RC3 *.hex --repo iNavFlight/inav
```

## Building Firmware

### Using Nightly Builds

Pre-built firmware binaries are available from the nightly build system:

**Nightly Releases:** https://github.com/iNavFlight/inav-nightly/releases

To verify the nightly matches your release commit:

```bash
# Get latest commit on master
cd inav
git log -1 --format="%h %s" HEAD

# Compare with the nightly release description
# Nightly tags follow format: v9.0.0-YYYYMMDD.BUILD_NUMBER
```

The nightly builds include all targets and can be used directly for RC releases instead of building locally.

### Building Locally

#### Prerequisites

- ARM GCC toolchain
- CMake
- Make

### Build All Targets

```bash
cd inav

# Clean previous builds
rm -rf build

# Build all targets (this takes a long time)
mkdir build && cd build
cmake ..
make -j4

# Or build specific target
make MATEKF405
```

### Build Script (if available)

```bash
# Check for existing build scripts
ls -la inav/*.sh
ls -la inav/build_scripts/
```

### Output Location

Firmware hex files are output to: `build/bin/`

## Building Configurator

### Using GitHub Actions CI (Preferred)

Pull requests to the configurator repo automatically trigger CI builds for all platforms. Use these artifacts for releases instead of building locally.

1. Create/merge a PR (e.g., SITL update PR)
2. Wait for the CI workflow to complete
3. Go to the PR or commit's "Checks" tab
4. Download artifacts from the workflow run:
   - `INAV-Configurator_linux_x64`
   - `INAV-Configurator_macOS`
   - `INAV-Configurator_win_x64`

```bash
# Or use gh CLI to download artifacts from a workflow run
gh run download <run-id> --repo iNavFlight/inav-configurator

# Flatten directory structure
find . -mindepth 2 -type f -exec mv -t . {} +
# Remove the now-empty subdirectories
find . -mindepth 1 -type d -empty -delete
```

### Building Locally (Fallback)

Only build locally if CI is unavailable.

#### Prerequisites

- Node.js (check `.nvmrc` for version)
- npm

#### Build Commands

```bash
cd inav-configurator

# Install dependencies
npm install

# Build for all platforms
npm run dist

# Or build for specific platform
npm run dist:linux
npm run dist:mac
npm run dist:win
```

### Output Location

Configurator packages are output to: `dist/` or `release/`

## Updating SITL Binaries

SITL binaries must be updated before tagging the configurator. They are stored in:
```
inav-configurator/resources/public/sitl/
├── linux/
│   ├── inav_SITL
│   └── arm64/
│       └── inav_SITL
├── macos/
│   └── inav_SITL
└── windows/
    ├── inav_SITL.exe
    └── cygwin1.dll
```

### Download from Nightly

```bash
# Find matching nightly release
gh release list --repo iNavFlight/inav-nightly --limit 5

# Download SITL resources
curl -L -o /tmp/sitl-resources.zip \
  "https://github.com/iNavFlight/inav-nightly/releases/download/<tag>/sitl-resources.zip"
unzip /tmp/sitl-resources.zip -d /tmp/sitl-extract

# Copy to configurator
cd inav-configurator
cp /tmp/sitl-extract/resources/sitl/linux/inav_SITL resources/public/sitl/linux/
cp /tmp/sitl-extract/resources/sitl/linux/arm64/inav_SITL resources/public/sitl/linux/arm64/
cp /tmp/sitl-extract/resources/sitl/macos/inav_SITL resources/public/sitl/macos/
cp /tmp/sitl-extract/resources/sitl/windows/inav_SITL.exe resources/public/sitl/windows/

# Commit
git add resources/public/sitl/
git commit -m "Update SITL binaries for <version>"
```

### Building SITL (Fallback)

Only build manually if no matching nightly is available.

Use the `build-sitl` skill to build SITL for Linux:
```
/skill build-sitl
```

For releases, you need SITL binaries for all three platforms:
- **Linux:** Build using the skill or cmake commands on a Linux system
- **macOS:** Must be built on a macOS machine
- **Windows:** Cross-compile with mingw-w64 or build on Windows

### Notes

- The `cygwin1.dll` in the Windows folder is a runtime dependency; only update if the build toolchain changes
- SITL binaries are platform-specific and cannot be cross-used
- Linux arm64 binary added in 9.0.0 for ARM-based Linux systems (e.g., Raspberry Pi)
- Ensure the SITL version matches the firmware version being released
- Test the SITL binaries work before committing (run configurator and try SITL mode)
- The SITL PR triggers CI builds - use those artifacts for the configurator release

## Managing Release Assets

### Renaming Assets Without Re-uploading

You can rename release assets directly via the GitHub API without re-uploading:

```bash
# Get release ID and asset IDs
gh api repos/iNavFlight/inav/releases --jq '.[] | select(.draft == true) | {id: .id, name: .name}'
gh api repos/iNavFlight/inav/releases/RELEASE_ID/assets --paginate --jq '.[] | "\(.id) \(.name)"'

# Rename a single asset
gh api -X PATCH "repos/iNavFlight/inav/releases/assets/ASSET_ID" -f name="new-filename.hex"

# Bulk rename firmware assets (add RC number, remove ci- suffix)
gh api repos/iNavFlight/inav/releases/RELEASE_ID/assets --paginate --jq '.[] | "\(.id) \(.name)"' > /tmp/assets.txt
cat /tmp/assets.txt | while read -r id name; do
  target=$(echo "$name" | sed -E 's/inav_[0-9]+\.[0-9]+\.[0-9]+_(.*)_ci-.*/\1/')
  newname="inav_9.0.0_RC2_${target}.hex"
  gh api -X PATCH "repos/iNavFlight/inav/releases/assets/$id" -f name="$newname" --silent
done
```

**Important:** The GitHub API paginates results (30 per page by default). Always use `--paginate` when listing assets to get all of them.

### Deleting Release Assets

If a draft release has outdated assets that need to be replaced (e.g., from a previous upload attempt), delete them before uploading new ones:

```bash
# Delete an asset by ID
gh api -X DELETE "repos/iNavFlight/inav/releases/assets/ASSET_ID"
```

### Asset Naming Conventions

**Firmware (RC releases):**
- Pattern: `inav_<version>_RC<n>_<TARGET>.hex`
- Example: `inav_9.0.0_RC2_MATEKF405.hex`

**Firmware (final releases):**
- Pattern: `inav_<version>_<TARGET>.hex`
- Example: `inav_9.0.0_MATEKF405.hex`

**Configurator (RC releases):**
- Pattern: `INAV-Configurator_<platform>_<version>_RC<n>.<ext>`
- Example: `INAV-Configurator_linux_x64_9.0.0_RC2.deb`

**Configurator (final releases):**
- Pattern: `INAV-Configurator_<platform>_<version>.<ext>`
- Example: `INAV-Configurator_linux_x64_9.0.0.deb`

## Creating GitHub Releases

### Create Draft Release

```bash
# Firmware
cd inav
gh release create <version> --draft --title "INAV <version>" --notes-file release-notes.md
gh release upload <version> *.hex

# Configurator
cd inav-configurator
gh release create <version> --draft --title "INAV Configurator <version>" --notes-file release-notes.md
gh release upload <version> *.zip *.dmg *.exe *.AppImage *.deb *.rpm *.msi
```

### View/Edit Draft Release

```bash
# List releases
gh release list

# View release
gh release view <version>

# Edit release notes
gh release edit <version> --notes-file updated-notes.md
```

### Publish Release

```bash
# Publish (removes draft status)
gh release edit <version> --draft=false
```

## Artifact Download Timing

**IMPORTANT:** You can download CI artifacts for a specific commit BEFORE creating the release tag.

### How It Works

1. **Commits are immutable** - Once a commit exists, it has a unique SHA
2. **CI runs on commits** - GitHub Actions builds artifacts for each commit automatically
3. **Tags point to commits** - A tag is just a named pointer to a specific commit

### Workflow

```bash
# 1. Find the target commit
gh api repos/iNavFlight/inav-configurator/commits/HEAD --jq '.sha'
# Output: 9dbd346dcf941b31f97ccb8418ede367044eb93c

# 2. Find the CI run for that commit
gh run list --repo iNavFlight/inav-configurator --limit 20 --json headSha,databaseId | \
  jq '.[] | select(.headSha == "9dbd346dcf941b31f97ccb8418ede367044eb93c")'

# 3. Download artifacts from that CI run
gh run download <run-id> --repo iNavFlight/inav-configurator

# 4. Later, create tag pointing to that same commit
gh release create 9.0.0-RC3 \
  --repo iNavFlight/inav-configurator \
  --target 9dbd346dcf941b31f97ccb8418ede367044eb93c \
  --draft
```

### Benefits

- Download and verify artifacts while repositories are locked
- Organize and rename files in advance
- Verify DMG contents thoroughly
- Create releases when ready without rushing

### For Firmware

Firmware uses nightly builds instead of CI artifacts:

```bash
# 1. Get commit SHA
gh api repos/iNavFlight/inav/commits/HEAD --jq '{sha: .sha, date: .commit.committer.date}'

# 2. Find nightly build created after that commit
gh release list --repo iNavFlight/inav-nightly --limit 20

# 3. Download hex files from appropriate nightly
gh release download v9.0.0-20251207.178 --repo iNavFlight/inav-nightly --pattern "*.hex"
```

## Identifying Incompatible Settings Changes

**CRITICAL:** Before releasing a major version, identify any CLI settings that have been renamed or removed. These cause errors (shown in RED) when users load their old `diff all` into the new firmware.

### Why This Matters

When users upgrade from INAV 8.x to 9.x, they:
1. Export configuration with `diff all` from old version
2. Flash new firmware
3. Load their old diff into new CLI

If settings were renamed or removed, those lines will fail and show in RED. Users need to know about these incompatibilities upfront.

### How to Find Incompatible Changes

Compare `settings.yaml` between the previous stable release and the new release:

```bash
cd inav

# For major releases (e.g., 8.0.1 → 9.0.0)
git diff 8.0.1..9.0.0-RC3 -- src/main/fc/settings.yaml | grep -E "^[\+\-].*name:"

# Look for:
# - Lines starting with "-" = Settings removed or renamed
# - Lines starting with "+" = New settings or renamed-to names
```

### Creating the Incompatibility Report

Create a document listing:

1. **Renamed settings** - Show old name → new name
2. **Removed settings** - Explain why they were removed
3. **Migration instructions** - How users should update their diff

**Example:** `claude/release-manager/9.0.0-INCOMPATIBLE-SETTINGS.md`

### Where to Document

1. **Release notes** - Add "Incompatible Settings" section
2. **Wiki release notes** - Add to upgrade instructions
3. **Separate document** - For reference during user support

### Common Types of Changes

- **Renamed for clarity:** `controlrate_profile` → `use_control_profile`
- **Terminology changes:** `pid_profile` → `control_profile` (major refactoring)
- **Removed features:** `reboot_character` (legacy MSP method removed)
- **Value format changes:** `pwm2centideg` → `decadegrees` (unit change)

### Automation Script

Save as `claude/release-manager/find-incompatible-settings.sh`:

```bash
#!/bin/bash
# Find incompatible settings between two releases

if [ $# -ne 2 ]; then
    echo "Usage: $0 <old-version> <new-version>"
    echo "Example: $0 8.0.1 9.0.0-RC3"
    exit 1
fi

OLD=$1
NEW=$2

echo "=== Incompatible Settings: $OLD → $NEW ==="
echo ""

cd inav
git diff $OLD..$NEW -- src/main/fc/settings.yaml | \
  grep -E "^[\-].*name:" | \
  grep -v "^\-\-\-" | \
  sed 's/^-.*name: /REMOVED\/RENAMED: /'

echo ""
echo "=== Review git diff for context to determine renames vs removals ==="
```

### Release Notes Template for Incompatibilities

Add this section to **both firmware and configurator release notes** for major version releases:

```markdown
## ⚠️ Incompatible Settings Changes

The following CLI settings have been renamed or removed in INAV X.0. When loading an older `diff all`, these will show in RED:

**Renamed Settings:**
- `old_setting_name` → `new_setting_name` - Brief explanation
- `another_old_name` → `another_new_name` - Brief explanation

**Removed Settings:**
- `removed_setting` - Reason for removal / what replaced it

**Migration Instructions:**
1. Export configuration from old version: CLI → `diff all` → Save to file
2. Flash new firmware with **Full Chip Erase**
3. Edit your saved diff file and update the renamed settings
4. Load edited diff into new CLI

See full upgrade guide: https://github.com/iNavFlight/inav/wiki/X.0.0-Release-Notes
```

**How to generate this content:**
```bash
# From release-manager directory
./find-incompatible-settings.sh 8.0.1 9.0.0-RC3

# Review output and create the renamed/removed lists
# Use git diff to determine renames vs removals
git diff 8.0.1..9.0.0-RC3 -- src/main/fc/settings.yaml | less
```

## Testing Artifacts Before Publishing

**CRITICAL:** Always test at least one configurator build with SITL before publishing releases.

### Why Test SITL?

- SITL binaries must match the firmware version being released
- Ensures SITL can launch and connect properly
- Validates that SITL update PR was merged correctly
- Prevents releasing broken SITL functionality to users

### Quick SITL Test Procedure

1. **Extract and run the configurator** (use native platform build):
   ```bash
   # Linux example
   unzip INAV-Configurator_linux_x64_9.0.0.zip -d test-configurator
   cd test-configurator
   ./inav-configurator
   ```

2. **Launch SITL from Configurator:**
   - Open INAV Configurator
   - Click "Setup" tab or "Simulator"
   - Click "Start SITL" or similar button
   - Verify SITL process launches without errors

3. **Verify SITL connects:**
   - Check that configurator detects SITL as a connected device
   - Verify serial port/connection appears
   - Test basic connection (read FC config)

4. **Check SITL version matches firmware:**
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

## Pre-Release Checklist

### Code Readiness

- [ ] All planned PRs merged
- [ ] CI passing on master branch
- [ ] No critical open issues blocking release
- [ ] Version numbers updated in both repositories
- [ ] SITL binaries updated in configurator

### Documentation

- [ ] Release notes drafted
- [ ] **Incompatible settings changes identified and added to release notes** (use find-incompatible-settings.sh)
- [ ] Breaking changes documented
- [ ] New features documented

### Artifact Verification

- [ ] Firmware hex files downloaded and renamed
- [ ] Configurator artifacts organized by platform (linux/, macos/, windows/)
- [ ] macOS DMG contents verified (no .exe files, correct architecture)
- [ ] **Configurator SITL tested** (launch SITL, verify version matches firmware)

## Post-Release Tasks

- [ ] Announce release (Discord, forums, etc.)
- [ ] Update any pinned issues
- [ ] Monitor for critical bug reports
- [ ] Prepare hotfix if needed
- [ ] Update this document with any lessons learned

## Maintenance Branches

When releasing a new major version, create maintenance branches for both repositories:

### Branch Strategy

- **maintenance-X.x** - For bugfixes to version X (e.g., maintenance-9.x for 9.0.x releases)
- **maintenance-(X+1).x** - For breaking changes targeting the next major version
- **master** - Continues as the main development branch

### Creating Maintenance Branches

Create branches from the release commit in both repos:

```bash
# Using gh API (works with HTTPS remotes)
COMMIT_SHA="<full-40-char-sha>"

# inav
gh api repos/iNavFlight/inav/git/refs -f ref="refs/heads/maintenance-9.x" -f sha="$COMMIT_SHA"
gh api repos/iNavFlight/inav/git/refs -f ref="refs/heads/maintenance-10.x" -f sha="$COMMIT_SHA"

# inav-configurator
gh api repos/iNavFlight/inav-configurator/git/refs -f ref="refs/heads/maintenance-9.x" -f sha="$COMMIT_SHA"
gh api repos/iNavFlight/inav-configurator/git/refs -f ref="refs/heads/maintenance-10.x" -f sha="$COMMIT_SHA"
```

Or using git push (requires SSH remote):

```bash
git push upstream upstream/master:refs/heads/maintenance-9.x
git push upstream upstream/master:refs/heads/maintenance-10.x
```

### When to Create

Create maintenance branches when:
- Releasing a new major version (e.g., 9.0.0)
- First RC of a new major version is a good time

### Usage

- **X.x bugfixes** → PR to maintenance-X.x
- **Breaking changes** → PR to maintenance-(X+1).x
- **Non-breaking features** → PR to master

Lower version branches are periodically merged into higher version branches (e.g., maintenance-9.x → maintenance-10.x → master).

### Update PR Branch Suggestion Workflow

When creating new maintenance branches, update the GitHub Action that suggests version branches to contributors:

**Files to update:**
- `inav/.github/workflows/pr-branch-suggestion.yml`
- `inav-configurator/.github/workflows/pr-branch-suggestion.yml`

Update the branch names mentioned in the comment text (e.g., change `maintenance-9.x` and `maintenance-10.x` to the current version branches).

## Hotfix Releases

For critical bugs discovered after release:

1. Create hotfix branch from release tag
2. Cherry-pick or create fix
3. Tag as `X.Y.Z+1` (patch increment)
4. Build and release following normal process
5. Document as hotfix in release notes

## Files You Manage

### Your Workspace
- `claude/release-manager/` - Your working directory
- `claude/release-manager/releases/` - Release notes and changelogs

### Don't Modify Directly
- Source code (coordinate with developers)
- Build configurations (unless necessary for release)

## Tools You Use

### Command-line Tools
- **gh** - GitHub CLI for releases, PRs, issues
- **git** - Tagging, log viewing
- **Bash** - Build commands, scripts
- **7z** - DMG extraction and verification (Linux)
- **file** - Binary format verification

### Custom Scripts

**`claude/release-manager/verify-dmg-contents.sh`**
- Verifies macOS DMG files for cross-platform contamination
- Checks for Windows files (.exe, .dll, .msi)
- Validates Mach-O format and architecture
- Works on Linux using 7z extraction
- Does NOT modify original DMG files

Usage:
```bash
./claude/release-manager/verify-dmg-contents.sh downloads/configurator-9.0.0-RC3/macos/*.dmg
```

**`claude/release-manager/rename-firmware-for-release.sh`**
- Generic script for renaming firmware hex files
- Removes CI build suffix (`_ci-YYYYMMDD-hash`)
- Adds release version (supports RC and final releases)
- Works with any version number

Usage:
```bash
# For RC releases
./claude/release-manager/rename-firmware-for-release.sh 9.0.0-RC3 downloads/firmware-9.0.0-RC3/

# For final releases
./claude/release-manager/rename-firmware-for-release.sh 9.0.0 downloads/firmware-9.0.0/

# For patch releases
./claude/release-manager/rename-firmware-for-release.sh 9.0.1 downloads/firmware-9.0.1/
```

## Important Reminders

1. **Always tag both repos** - Firmware and configurator versions must match
2. **Draft first** - Create draft releases, review, then publish
3. **Test builds** - Verify at least one firmware and configurator build works
4. **Backup** - Keep local copies of release artifacts
5. **Communicate** - Coordinate with maintainers before publishing

## Quick Commands Reference

```bash
# Latest tags
git tag --sort=-v:refname | head -5

# PRs since tag
gh pr list --state merged --limit 50

# Create tag
git tag -a X.Y.Z -m "INAV X.Y.Z"

# Push tag
git push origin X.Y.Z

# Create draft release
gh release create X.Y.Z --draft --title "INAV X.Y.Z"

# Upload to release
gh release upload X.Y.Z file1 file2

# Publish release
gh release edit X.Y.Z --draft=false
```

## Public Release Documentation

A public version of this release guide is maintained at:
`inav/docs/development/release-create.md`

When updating this README with new procedures or lessons learned, also update the public documentation to keep them in sync.

---

# Useful Skills

The following skills are available to help with common release manager tasks:

## Release Artifact Management
- **download-release-artifacts** - Download firmware and configurator builds from CI
- **upload-release-assets** - Upload files to GitHub releases
- **remove-release-assets** - Remove old/incorrect assets from releases

## Git Operations
- **git-workflow** - Tag creation and branch management
- **check-builds** - Verify CI builds pass before release

## Communication
- **email** - Coordinate with manager and developers
- **communication** - Message templates and guidelines

---

## Summary

As Release Manager:
1. ✅ Create and push version tags
2. ✅ Generate changelogs from merged PRs
3. ✅ Build firmware and configurator
4. ✅ Create and upload GitHub releases
5. ✅ Coordinate release timing with maintainers
6. ❌ Don't modify source code directly (coordinate with developers)

**Remember:** Releases affect all INAV users. Double-check everything before publishing.
