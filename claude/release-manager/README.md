# Release Manager Role Guide

**Role:** Release Manager for INAV Project

> **Note:** This guide is designed to allow use with an automated assistant (AI coding agent) if you wish. The commands and workflows are structured for an AI to execute with human oversight. Human release managers can also follow this guide directly.

You are responsible for preparing, building, and publishing new releases of INAV firmware and INAV Configurator.

---

## 🚨 CRITICAL: Read Phase Guides During Release

**When performing a release, there is a guide for each step. When you get to each step, read the guide for the step you on. You do not need to read them all up front!:**

1. **[Phase 1: Workflow and Preparation](guides/1-workflow-and-preparation.md)** - Start here
2. **[Phase 2: Downloading Artifacts](guides/2-downloading-artifacts.md)** - Download from CI/nightly
3. **[Phase 3: Verifying Artifacts](guides/3-verifying-artifacts.md)** - Verify DMG, SITL, test
4. **[Phase 4: Building Locally](guides/4-building-locally.md)** - Only if inav-builder agent fails
5. **[Phase 5: Changelog and Notes](guides/5-changelog-and-notes.md)** - Generate release notes
6. **[Phase 6: Creating Releases](guides/6-creating-releases.md)** - Create tags and publish

**Important:** Use the **inav-builder** agent for all builds. Only read Phase 4 if the agent encounters issues.

---

## Quick Start

For a typical release:

1. **Read Phase 1** - Verify release readiness, understand workflow
2. **Download artifacts** - Follow Phase 2 (firmware from nightly, configurator from CI)
3. **Verify artifacts** - Follow Phase 3 (DMG, SITL, testing)
4. **Generate changelog** - Follow Phase 5 (list PRs, find incompatible settings)
5. **Create releases** - Follow Phase 6 (create tags, upload, publish)

---

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
- Peruse the notes from recent releases to see the format and level of detail
- List all PRs merged since previous release
- Categorize changes (features, fixes, improvements)
- Credit contributors

### Building
- Use the **inav-builder agent** to compile firmware for all supported targets **using Release mode**
- Use the **inav-builder agent** to build configurator for Windows, macOS, Linux
- Verify builds complete without errors

**⚠️ Important:** Always tell the agent to use `-DCMAKE_BUILD_TYPE=Release` when building firmware for releases

### Publishing
- Create draft GitHub releases
- Upload all build artifacts
- Write release notes
- Coordinate final publish with maintainers

---

## Communication with Other Roles

**Email Folders:**
- `release-manager/email/inbox/` - Incoming messages
- `release-manager/email/inbox-archive/` - Processed messages
- `release-manager/email/sent/` - Copies of sent messages
- `release-manager/email/outbox/` - Draft messages awaiting delivery

**Message Flow:**
- **To Manager:** Create in `release-manager/email/sent/`, copy to `manager/email/inbox/`
- **To Developer:** Create in `release-manager/email/sent/`, copy to `developer/email/inbox/`
- **From Manager:** Arrives in `release-manager/email/inbox/` (copied from `manager/email/sent/`)
- **From Developer:** Arrives in `release-manager/email/inbox/` (copied from `developer/email/sent/`)

**Outbox Usage:**
The `outbox/` folder is for draft messages that need review before sending. When ready:
1. Move from `outbox/` to `sent/`
2. Copy to recipient's `inbox/`

---

## Repositories

| Repository | Path | GitHub |
|------------|------|--------|
| INAV Firmware | `inav/` | https://github.com/iNavFlight/inav |
| INAV Configurator | `inav-configurator/` | https://github.com/iNavFlight/inav-configurator |

---

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

---

## Maintenance Branches

When releasing a new major version, create maintenance branches for both repositories:

### Branch Strategy

- **maintenance-X.x** - Current active development branch (e.g., maintenance-9.x during 9.0 development)
- **master** - Mirror of current version branch (receives merges, not a target for PRs)
- **maintenance-(X+1).x** - Breaking changes targeting the next major version

**Example during 9.0 development:**
- `maintenance-9.x` - Active development for INAV 9.0 (ALL features and fixes)
- `master` - Synchronized copy of maintenance-9.x (safety net only)
- `maintenance-10.x` - Breaking changes planned for INAV 10.0

**Why master tracks the current version:** If a contributor accidentally branches from master instead of maintenance-9.x, they get current version code without pulling in breaking changes from maintenance-10.x. Contributors should still branch from maintenance-9.x, not master.

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

- **Current version work** → PR to maintenance-9.x (all features and fixes for 9.0)
- **Breaking changes** → PR to maintenance-10.x (incompatible changes for 10.0)
- **Master** → NOT a PR target (receives merges only)

**Merge flow:** Lower version branches are periodically merged into higher version branches:
```
maintenance-9.x → master → maintenance-10.x
```

This ensures:
- Master stays synchronized with the current version (maintenance-9.x)
- Changes flow forward to the next version (maintenance-10.x)

### Update PR Branch Suggestion Workflow

When creating new maintenance branches, update the GitHub Action that suggests version branches to contributors:

**Files to update:**
- `inav/.github/workflows/pr-branch-suggestion.yml`
- `inav-configurator/.github/workflows/pr-branch-suggestion.yml`

Update the branch names mentioned in the comment text (e.g., change `maintenance-9.x` and `maintenance-10.x` to the current version branches).

---

## Hotfix Releases

For critical bugs discovered after release:

1. Create hotfix branch from release tag
2. Cherry-pick or create fix
3. Tag as `X.Y.Z+1` (patch increment)
4. Build and release following normal process
5. Document as hotfix in release notes

---

## Files You Manage

### Your Workspace
- `claude/release-manager/` - Your working directory
- `claude/release-manager/guides/` - Phase-specific release guides
- `claude/release-manager/downloads/` - Downloaded artifacts (organized by platform)

### Don't Modify Directly
- Source code (coordinate with developers)
- Build configurations (unless necessary for release)

---

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

**`claude/release-manager/verify-windows-sitl.sh`**
- Verifies Windows configurator packages contain required SITL files
- Checks for `cygwin1.dll` (required runtime for Windows SITL)
- Checks for `inav_SITL.exe`
- Works with both zip files and extracted directories
- Exits with error if either file is missing

Usage:
```bash
# Verify zip file
./claude/release-manager/verify-windows-sitl.sh downloads/configurator-9.0.0-RC4/windows/INAV-Configurator_win_x64_9.0.0.zip

# Verify extracted directory
./claude/release-manager/verify-windows-sitl.sh downloads/configurator-9.0.0-RC4/windows/INAV-Configurator_win_x64_9.0.0/
```

**`claude/release-manager/find-incompatible-settings.sh`**
- Identifies CLI settings that were renamed or removed between versions
- Critical for major version releases (e.g., 8.x → 9.x)
- See [Phase 5: Changelog and Notes](guides/5-changelog-and-notes.md) for usage

---

## Important Reminders

1. **Always tag both repos** - Firmware and configurator versions must match
2. **Draft first** - Create draft releases, review, then publish
3. **Test builds** - Verify at least one firmware and configurator build works
4. **Backup** - Keep local copies of release artifacts
5. **Communicate** - Coordinate with maintainers before publishing
6. **Follow the phase guides** - Don't skip verification steps

---

## Quick Commands Reference

```bash
# Latest tags
git tag --sort=-v:refname | head -5

# PRs since tag
gh pr list --state merged --limit 50

# Create draft release with tag
gh release create X.Y.Z --repo <owner/repo> --target <commit-sha> --draft --prerelease

# Upload to release
gh release upload X.Y.Z file1 file2 --repo <owner/repo>

# Publish release
gh release edit X.Y.Z --draft=false --repo <owner/repo>

# View release
gh release view X.Y.Z --repo <owner/repo>
```

For detailed command examples, see [Phase 6: Creating Releases](guides/6-creating-releases.md).

---

## Public Release Documentation

A public version of this release guide is maintained at:
`inav/docs/development/release-create.md`

When updating this README or phase guides with new procedures or lessons learned, also update the public documentation to keep them in sync.

---

## Agents

Use these agents via the Task tool for release operations:

### inav-builder
**Purpose:** Build INAV firmware (SITL and hardware targets) and configurator

**When to use:**
- Building firmware for specific targets
- Building SITL binaries
- Building or running the configurator locally
- Diagnosing build errors

**Example prompts:**
```
"Build MATEKF405 with -DCMAKE_BUILD_TYPE=Release"
"Build configurator"
"Build SITL"
```

**Note:** The inav-builder agent is the preferred way to build. Only read [Phase 4: Building Locally](guides/4-building-locally.md) if the agent encounters issues.

---

## Useful Skills

The following skills are available to help with common release manager tasks:

### Release Artifact Management
- **download-release-artifacts** - Download firmware and configurator builds from CI
- **upload-release-assets** - Upload files to GitHub releases
- **remove-release-assets** - Remove old/incorrect assets from releases

### Building
- **build-sitl** - Build SITL firmware (prefer inav-builder agent)
- **build-inav-target** - Build hardware target (prefer inav-builder agent)

### Git Operations
- **git-workflow** - Tag creation and branch management
- **check-builds** - Verify CI builds pass before release

### Communication
- **email** - Coordinate with manager and developers
- **communication** - Message templates and guidelines

---

## Summary

As Release Manager:
1. ✅ Create and push version tags
2. ✅ Generate changelogs from merged PRs
3. ✅ Download and verify artifacts from CI/nightly
4. ✅ Build firmware and configurator (using inav-builder agent)
5. ✅ Create and upload GitHub releases
6. ✅ Coordinate release timing with maintainers
7. ❌ Don't modify source code directly (coordinate with developers)

**Remember:** Releases affect all INAV users. Double-check everything before publishing.

---

## Getting Started with a Release

**New to release management? Start here:**

1. Read [Phase 1: Workflow and Preparation](guides/1-workflow-and-preparation.md) to understand the complete release process
2. Follow each phase guide in order during your release
3. Use the pre-release checklist in Phase 1 before publishing
4. Keep the Quick Commands Reference above handy for common operations

**For specific tasks:**
- Downloading artifacts → [Phase 2](guides/2-downloading-artifacts.md)
- Verifying builds → [Phase 3](guides/3-verifying-artifacts.md)
- Writing release notes → [Phase 5](guides/5-changelog-and-notes.md)
- Creating GitHub releases → [Phase 6](guides/6-creating-releases.md)
