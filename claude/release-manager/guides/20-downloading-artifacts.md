# Phase 20: Downloading Release Artifacts

**Read this guide when:** You're ready to download firmware and configurator artifacts for a release

**Prerequisites:** Phase 10 checklist completed (PRs merged, CI passing, version numbers updated)

**Related guides:**
- [Phase 10: Workflow and Preparation](10-workflow-and-preparation.md)
- [Phase 30: Verifying Artifacts](30-verifying-artifacts.md)

---

## Overview

This guide covers downloading firmware hex files from inav-nightly and configurator builds from GitHub Actions CI. Proper organization during download prevents cross-platform contamination.

---

## Key Principles

- **Firmware hex files** come from inav-nightly releases
- **Configurator builds** come from GitHub Actions CI artifacts
- **CRITICAL: Organize configurator builds by platform** (linux/, macos/, windows/) to prevent cross-platform contamination
- **NEVER flatten directories** containing multiple platforms together
- **Rename firmware files** before upload: remove `_ci-YYYYMMDD-hash` suffix, add RC number for RC releases

**Lesson learned (9.0.0 release):** A Windows .exe file was found inside a Mac DMG. The exact cause is unknown, but improper artifact handling during download/preparation is suspected. Platform separation and verification steps prevent this.

---

## Artifact Download Timing

**IMPORTANT:** You can download CI artifacts for a specific commit BEFORE creating the release tag.

### How It Works

1. **Commits are immutable** - Once a commit exists, it has a unique SHA
2. **CI runs on commits** - GitHub Actions builds artifacts for each commit automatically
3. **Tags point to commits** - A tag is just a named pointer to a specific commit

### Benefits

- Download and verify artifacts while repositories are locked
- Organize and rename files in advance
- Verify DMG contents thoroughly
- Create releases when ready without rushing

---

## Before You Download: Confirm a Build Actually Exists

Both repos' pre-release build workflows (`nightly-build.yml`) only trigger on `push` to a **hardcoded branch list** (typically `master` + one or two `maintenance-X.x` names). When a new `release/X.Y` or `maintenance-X.x` branch is cut, that list is not always updated — so commits merged there can silently produce zero build artifacts, even though every individual PR passed CI pre-merge.

**Before assuming artifacts exist, verify against the actual freeze commit:**
```bash
gh api repos/<owner>/<repo>/commits/<freeze-sha>/check-runs --jq '.check_runs | length'
```
If that's `0`, nothing has built this commit. Fix: open a PR merging the active branch into `master` (or whichever branch the workflow watches) — this triggers a real build. Follow the existing naming precedent in that repo's PR history (search closed PRs titled e.g. "Maintenance 9.x to master" or "Release/9.1 to master") rather than inventing a new pattern.

**If both branches already exist on `upstream`**, open the PR directly — don't create a synthetic local branch or push anything:
```bash
gh pr create --repo <owner>/<repo> --base master --head <active-branch> --title "..." --body "..."
```
(A local branch name containing "master" as a substring may also trip an unrelated local pre-push hook — another reason to skip local branch creation when it isn't needed.)

**If `git push` is denied (403) even to your own fork:** the `GITHUB_TOKEN` env var is pinning `gh`/git to a restricted fine-grained PAT. That restriction is deliberate — it exists to limit what an agent can do unchecked, not an accident to work around. Do **not** unset it and retry on your own initiative.

**Stop and ask the human user first, every time**, even if you've done it earlier in the same session. If they authorize it:
```bash
env -u GITHUB_TOKEN GH_TOKEN="" git push origin <branch>:<branch>
env -u GITHUB_TOKEN GH_TOKEN="" gh pr create ...
```
A prior "go ahead and push this branch" is not blanket approval to drop the PAT for everything afterward (wiki pushes, release creation, asset uploads, etc.) — each escalation is its own ask.

Report the missing-trigger gap to Developer so the workflow's branch list gets fixed permanently — this shouldn't need rediscovering every release.

---

## Downloading Firmware Artifacts

Firmware uses nightly builds instead of CI artifacts:

### Step 1: Get Target Commit SHA

```bash
# Get commit SHA from firmware repo
cd inav
gh api repos/iNavFlight/inav/commits/HEAD --jq '{sha: .sha, date: .commit.committer.date}'
```

### Step 2: Find Matching Nightly Build

```bash
# List recent nightly builds
gh release list --repo iNavFlight/inav-nightly --limit 20
```

Look for the nightly build created after your target commit date. Nightly tags follow format: `v9.0.0-YYYYMMDD.BUILD_NUMBER`

### Step 3: Download Firmware Hex Files

```bash
# Download all hex files from the nightly release
gh release download v9.0.0-20251207.178 --repo iNavFlight/inav-nightly --pattern "*.hex" -D downloads/firmware-9.0.0-rc3/
```

### Step 4: Download SITL Binaries

```bash
# Download SITL resources from the same nightly
gh release download v9.0.0-20251207.178 --repo iNavFlight/inav-nightly --pattern "sitl-resources.zip" -D downloads/sitl-9.0.0-rc3/

# Extract SITL binaries
cd downloads/sitl-9.0.0-rc3/
unzip sitl-resources.zip
```

The SITL binaries will be needed for the configurator (Phase 40: Building Locally).

### Step 5: Rename Firmware Files

Use the rename script to remove CI build suffixes and add RC numbers:

```bash
# For RC releases (use lowercase rc — required by Configurator firmware flasher)
./claude/release-manager/scripts/rename-firmware-for-release.sh 9.0.0-rc3 downloads/firmware-9.0.0-rc3/

# For final releases
./claude/release-manager/scripts/rename-firmware-for-release.sh 9.0.0 downloads/firmware-9.0.0/
```

**Example transformation:**
- Before: `inav_9.0.0_MATEKF405_ci-20251129-abc123.hex`
- After: `inav_9.0.0-rc3_MATEKF405.hex`

---

## Downloading Configurator Artifacts

Configurator builds come from GitHub Actions CI.

### Step 1: Find Target Commit

```bash
# Get commit SHA from configurator repo
cd inav-configurator
gh api repos/iNavFlight/inav-configurator/commits/HEAD --jq '.sha'
# Output: 9dbd346dcf941b31f97ccb8418ede367044eb93c
```

### Step 2: Find CI Run for That Commit

```bash
# Find the CI workflow run for the target commit
gh run list --repo iNavFlight/inav-configurator --limit 20 --json headSha,databaseId,status,conclusion | \
  jq '.[] | select(.headSha == "9dbd346dcf941b31f97ccb8418ede367044eb93c")'
```

Note the `databaseId` - this is your `<run-id>`.

### Step 3: Download Artifacts

**CRITICAL:** Download to separate directories by platform to prevent contamination.

⚠️ **The full artifact set is large (~2 GB across all platform installers) and can exceed a default 2-minute command timeout partway through.** If it times out, don't just re-run `gh run download <run-id>` bare — it will error with "file exists" on artifacts already extracted. Instead, check what's missing and download only those, by name, one at a time:
```bash
gh run download <run-id> --repo iNavFlight/inav-configurator -n "<exact-artifact-name>"
```
Get exact names from `gh api repos/<owner>/<repo>/actions/runs/<run-id>/artifacts --jq '.artifacts[].name'`.

```bash
# Create platform-specific directories
mkdir -p downloads/configurator-9.0.0-rc3/{linux,macos,windows}

# Download all artifacts from the CI run
gh run download <run-id> --repo iNavFlight/inav-configurator

# The download creates subdirectories, one per artifact:
# - INAV-Configurator_linux_x64/
# - INAV-Configurator_macOS/
# - INAV-Configurator_win_x64/
```

### Step 4: Organize by Platform

Move files to platform-specific directories:

```bash
# Move Linux builds
mv INAV-Configurator_linux_x64/* downloads/configurator-9.0.0-rc3/linux/

# Move macOS builds
mv INAV-Configurator_macOS/* downloads/configurator-9.0.0-rc3/macos/

# Move Windows builds
mv INAV-Configurator_win_x64/* downloads/configurator-9.0.0-rc3/windows/

# Remove empty artifact directories
rmdir INAV-Configurator_*
```

**NEVER** use commands like `find . -mindepth 2 -type f -exec mv -t . {} +` that flatten all files into one directory - this can mix Windows .exe files into macOS DMGs.

### Step 5: Verify Directory Structure

Your downloads should look like:

```
downloads/
├── firmware-9.0.0-rc3/
│   ├── inav_9.0.0-rc3_MATEKF405.hex
│   ├── inav_9.0.0-rc3_MATEKF411.hex
│   └── ... (all renamed hex files)
├── sitl-9.0.0-rc3/
│   └── resources/sitl/
│       ├── linux/
│       ├── macos/
│       └── windows/
└── configurator-9.0.0-rc3/
    ├── linux/
    │   ├── INAV-Configurator_linux_x64_9.0.0.AppImage
    │   ├── INAV-Configurator_linux_x64_9.0.0.deb
    │   └── INAV-Configurator_linux_x64_9.0.0.rpm
    ├── macos/
    │   ├── INAV-Configurator_macOS_arm64_9.0.0.dmg
    │   └── INAV-Configurator_macOS_x64_9.0.0.dmg
    └── windows/
        ├── INAV-Configurator_win_x64_9.0.0.exe
        ├── INAV-Configurator_win_x64_9.0.0.msi
        └── INAV-Configurator_win_x64_9.0.0.zip
```

---

## Known CI Issues

### macOS x64 build runs out of memory

The `macos-15-intel` GitHub Actions runner can hit a 2 GB V8 heap limit during webpack's JSON parse step. Symptoms: the macOS x64 artifact (DMG + ZIP) is missing while all other platform artifacts succeeded, and the CI run shows the `build-mac` job as failed.

The fix is `NODE_OPTIONS: --max-old-space-size=4096` on the `Build MacOS x64` step in `.github/workflows/ci.yml`. If you encounter this, raise a PR with that fix to the configurator repo, wait for CI to pass on that PR, and download the x64 artifacts from that separate CI run.

---

## Next Steps

Once artifacts are downloaded and organized:

**→ Proceed to [Phase 30: Verifying Artifacts](30-verifying-artifacts.md)**
