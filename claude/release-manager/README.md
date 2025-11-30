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

The version number is set here:
inav/CMakeLists.txt:54:project(INAV VERSION 8.0.1)
and here:
inav-configurator/package.json:5 - "version": "9.0.0"

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
- PR #1235: Description (@contributor)

#### Bug Fixes
- PR #1236: Description (@contributor)

#### Improvements
- PR #1237: Description (@contributor)

### Configurator Changes

#### New Features
- PR #100: Description (@contributor)

#### Bug Fixes
- PR #101: Description (@contributor)

### Target Updates
- New target: TARGETNAME
- Updated: TARGETNAME

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
- **Keep download directories FLAT** (no subdirectories) for easy upload to GitHub releases
- **Rename firmware files** before upload: remove `_ci-YYYYMMDD-hash` suffix, add RC number for RC releases
  - Example: `inav_9.0.0_TARGET_ci-20251129-abc123.hex` → `inav_9.0.0_RC2_TARGET.hex`
- After downloading and renaming, **human must upload files** to the draft GitHub releases

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
make -j$(nproc)

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

**IMPORTANT:** This step must be done BEFORE tagging the configurator repository.

The SITL (Software In The Loop) simulator binaries are tracked directly in the Configurator repository. They must be updated to match the firmware version being released.

### SITL Binary Locations

The binaries are committed to:
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

### Downloading SITL from Nightly (Preferred)

If a matching nightly build exists, download the pre-built SITL binaries instead of building:

1. Go to https://github.com/iNavFlight/inav-nightly/releases
2. Find the release matching your firmware commit (verify with `git log -1 --format="%h %s"`)
3. Download `sitl-resources.zip` from the release assets
4. Extract and copy to the configurator:

```bash
cd inav-configurator

# Create a branch for the PR
git checkout -b update-sitl-<version>

# Download and extract (zip contains resources/sitl/ structure)
curl -L -o /tmp/sitl-resources.zip "https://github.com/iNavFlight/inav-nightly/releases/download/<nightly-tag>/sitl-resources.zip"
unzip /tmp/sitl-resources.zip -d /tmp/sitl-extract

# Copy binaries to configurator (note: zip has resources/sitl/, target is resources/public/sitl/)
cp /tmp/sitl-extract/resources/sitl/linux/inav_SITL resources/public/sitl/linux/
mkdir -p resources/public/sitl/linux/arm64
cp /tmp/sitl-extract/resources/sitl/linux/arm64/inav_SITL resources/public/sitl/linux/arm64/
cp /tmp/sitl-extract/resources/sitl/macos/inav_SITL resources/public/sitl/macos/
cp /tmp/sitl-extract/resources/sitl/windows/inav_SITL.exe resources/public/sitl/windows/

# Commit and push
git add resources/public/sitl/
git commit -m "Update SITL binaries for <version>"
git push -u origin update-sitl-<version>

# Create PR (this triggers CI builds for configurator artifacts)
gh pr create --repo iNavFlight/inav-configurator --title "Update SITL binaries for <version>"
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

# Upload artifacts
gh release upload <version> build/bin/*.hex

# Configurator
cd inav-configurator
gh release create <version> --draft --title "INAV Configurator <version>" --notes-file release-notes.md

# Upload artifacts
gh release upload <version> dist/*.zip dist/*.dmg dist/*.exe dist/*.AppImage
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

## Pre-Release Checklist

### Code Readiness

- [ ] All planned PRs merged
- [ ] CI passing on master/main branch
- [ ] No critical open issues blocking release
- [ ] Version numbers updated in:
  - [ ] Firmware: `src/main/build/version.h`
  - [ ] Configurator: `package.json`
- [ ] SITL binaries updated in configurator (must be done before tagging)

### Documentation

- [ ] Release notes drafted
- [ ] Breaking changes documented
- [ ] New features documented
- [ ] Wiki updated (if needed)

### Testing

- [ ] Key features tested
- [ ] Configurator connects to firmware
- [ ] No regression in critical functionality

## Post-Release Tasks

- [ ] Announce release (Discord, forums, etc.)
- [ ] Update any pinned issues
- [ ] Monitor for critical bug reports
- [ ] Prepare hotfix if needed

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

- **9.x bugfixes** → PR to maintenance-9.x, cherry-pick to master if applicable
- **Breaking changes for 10.x** → PR to maintenance-10.x
- **Non-breaking features** → PR to master

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

- **gh** - GitHub CLI for releases, PRs, issues
- **git** - Tagging, log viewing
- **Bash** - Build commands, scripts
- **Read** - View files, configs
- **Write** - Create release notes, changelogs

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

## Summary

As Release Manager:
1. ✅ Create and push version tags
2. ✅ Generate changelogs from merged PRs
3. ✅ Build firmware and configurator
4. ✅ Create and upload GitHub releases
5. ✅ Coordinate release timing with maintainers
6. ❌ Don't modify source code directly (coordinate with developers)

**Remember:** Releases affect all INAV users. Double-check everything before publishing.
