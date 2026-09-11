# Phase 1: Release Workflow and Preparation

**Read this guide when:** Starting a new release process

**Related guides:**
- Phase 2: [Downloading Artifacts](2-downloading-artifacts.md)
- Phase 3: [Verifying Artifacts](3-verifying-artifacts.md)
- Phase 4: [Building Locally](4-building-locally.md)
- Phase 5: [Changelog and Notes](5-changelog-and-notes.md)
- Phase 6: [Creating Releases](6-creating-releases.md)
- Phase 7: [Publishing Releases](7-publishing-releases.md)
- Phase 8: [Post-Release](8-post-release.md)
- [PG Validation](pg-validation.md) — not phase-numbered; run right after freeze, before Phase 2 (see Step 0.6 below)

---

## ⚠️ Step 0: Establish the Canonical Version String

**Do this BEFORE anything else, even before reading the rest of this guide.**

When the user announces a release, normalize to the canonical form and confirm it before proceeding:

```
X.Y.Z-rcN    (lowercase rc, hyphen-separated, no spaces)
```

| User says | Canonical form |
|-----------|---------------|
| `9.1.0 RC2` | `9.1.0-rc2` |
| `9.1.0-RC2` | `9.1.0-rc2` |
| `INAV 9.1 RC1` | `9.1.0-rc1` |
| `9.0.0 final` | `9.0.0` |
| `9.0.1` | `9.0.1` |

Respond: *"I'll use `9.1.0-rc2` as the version string for all filenames, tags, and directories — confirm?"*

Use this string **everywhere**: directory names, rename script argument, release tag, GitHub release title.

---

## ⚠️ Step 0 (New Major Versions Only): Reserve the Previous Major's Patch Number First

**Applies only when this release establishes a new major version's version string for the first time** (e.g. setting `10.0.0` on `maintenance-10.x`). Not needed for RC-to-RC releases or for patch releases within an existing major version.

**The hazard:** Once `maintenance-10.x`'s version number is set to `10.0.0`, any later patch fix on the previous major's release branch (e.g. `release/9.1` → `9.1.1`) has to be merged forward into `maintenance-10.x`, per [Post-Release: Merging Changes Upward](#️-post-release-merging-changes-upward-to-the-next-version) below. If that forward-merge happens *after* `10.0.0` was already set, it can carry the `9.1.x` branch's version-string commit along with it — silently overwriting the already-set `10.0.0` version number on `maintenance-10.x`.

**Do this, in order, before setting the new major's version number:**
1. On the previous major's release branch (e.g. `release/9.1`), bump the patch level (e.g. to `9.1.2`) — even if there's no pending bug fix. This reserves the next patch number.
2. Commit that patch-level bump.
3. Open a PR carrying it forward into the new major's branch (`maintenance-10.x`), following the [forward-merge procedure](#️-post-release-merging-changes-upward-to-the-next-version) below — **never use GitHub's "Resolve conflicts" button** on that PR.
4. **Only after that PR merges**, set the new major's own version number (e.g. `10.0.0`) on `maintenance-10.x`.

This ordering exists because a version bump landing on `maintenance-10.x` before the previous major's patch reservation is merged forward can get silently reverted by that later merge.

---

## ⚠️ Step 0.5: Lock the Repo Before Any Local Build/Validation

`inav/` and `inav-configurator/` are shared working directories — other roles (Developer) check out and commit to them concurrently. A build or PG-validation run in an unlocked checkout can have its `HEAD` moved out from under it mid-run, silently invalidating the result.

Before checking out a release branch locally (yourself or via the inav-builder agent) for anything that needs a pinned commit, acquire a lock with `claude/locks/lock_manager.py` — do not check or write lock files by hand:

```bash
REPO=$(python3 claude/locks/lock_manager.py acquire --task "<what you're building/verifying>" --branch <branch-name> --type firmware)
```

Use `--type configurator` for `inav-configurator/`. This tries `inav/`,
`inav2/`, `inav3/` in order, skips anything locked or unexpectedly dirty,
and prints the checkout to use (e.g. `inav2`) — build in `$REPO`, not
necessarily `inav/`. The script records `$CLAUDE_CODE_SESSION_ID`
automatically, so it doesn't have the "hand-written lock missing
SESSION_ID gets flagged as a different session" problem that hit the 9.1.1
release (2026-07-13).

If it exits non-zero, every candidate is locked or unexpectedly dirty —
investigate (see `claude/locks/README.md`) rather than forcing an
acquisition or building in a shared checkout you don't hold the lock on.

**Release the lock as soon as your build/verification is done:**
```bash
python3 claude/locks/lock_manager.py release "$REPO"
```
Don't hold it for the whole release process — only for the parts that
actually touch the shared checkout. It also warns if the checkout is left
dirty (e.g. build output) — clean that up so the next task can reuse it.
Full rules: `claude/locks/README.md`.

If a build must run unattended or for a while, prefer an isolated `git clone` to a scratch path over the shared checkout regardless — the lock protects against concurrent writers, but an isolated clone also avoids `HEAD` being reused for something else between your checkout and your verification.

---

## ⚠️ Step 0.6: Run PG Validation Now, Before Downloading Anything

Run [PG Validation](pg-validation.md) against the freeze commit **now** — before Phase 2's artifact downloads, not after. If it fails, you need a hotfix PR and a new freeze point, and there's no reason to spend time downloading/verifying artifacts or writing changelog notes for a commit that's about to be superseded.

```bash
cd inav
./cmake/validate-pg-for-release.sh
```

If it fails, see [PG Validation](pg-validation.md) for the fix procedure, then re-freeze and re-run this step before proceeding.

---

## Overview

This guide covers the complete release workflow and preparation steps you need to complete before starting artifact downloads and builds.

## Release Workflow

**IMPORTANT:** Verify builds BEFORE creating tags. Never tag a commit that hasn't been proven to build successfully.

```
1. Verify release readiness
   ├── All PRs merged to firmware repo
   ├── Version number updated in firmware (CMakeLists.txt)
   └── CI passing on firmware target commit

2. Configurator version bump PR
   ├── Create PR branch with version bump (package.json)
   ├── This PR will also receive SITL binaries in step 4
   └── Do NOT merge yet - wait for SITL update

3. Download firmware artifacts
   ├── Download firmware hex files from CI
   ├── Download SITL binaries from same CI run
   ├── Build Linux x64 SITL locally if needed (for glibc compatibility)
   └── This provides SITL binaries needed for configurator

4. Update SITL in configurator (same PR as step 2)
   ├── Add SITL binaries as additional commit to version bump PR
   ├── Wait for configurator CI to pass
   └── Merge the combined version bump + SITL PR

5. Download configurator artifacts
   ├── Download from CI run after combined PR merged
   ├── Verify macOS DMGs (no cross-platform contamination)
   ├── Verify Windows SITL (cygwin1.dll present)
   ├── Verify Linux SITL (glibc <= 2.35)
   └── Test SITL functionality

6. Generate changelog
   ├── List PRs since last tag
   ├── Categorize changes
   ├── **Identify incompatible settings** (./scripts/find-incompatible-settings.sh)
   └── Format release notes

7. Create tags and draft releases (ONLY after artifacts verified)
   ├── Create draft release for firmware (targeting verified commit)
   ├── Create tag + draft release tag for configurator (targeting verified commit)
   ├── Upload verified artifacts
   └── Add release notes

8. Review and publish
   ├── Final review of draft releases
   ├── Maintainer approval
   ├── Add tag to drafty release
   └── Publish releases

9. After publishing — merging changes upward (if applicable)
   └── See warning below before creating any PR
```

**Why this order matters:** If you tag first and then discover the build is broken, you have a tag pointing to a broken commit. By verifying artifacts first, you only tag commits that are proven to work.

---

## ⚠️ Post-Release: Merging Changes Upward to the Next Version

After publishing a 9.1 RC or final release, it is common to want to open a PR to carry those changes forward into `maintenance-10.x`. **Before doing that, read this warning and relay it to the user.**

**Say this to the user:**

> You're about to create a PR from `release/9.1` → `maintenance-10.x`. If GitHub shows a "Resolve conflicts" button for that PR, **do not click it**. GitHub's conflict resolver merges the entire base branch (`maintenance-10.x`) into your head branch (`release/9.1`) — the wrong direction. It will silently contaminate the 9.1 release branch with all of 10.x's newer development. The commit will look innocent ("Merge branch 'maintenance-10.x' into release/9.1") but is destructive.
>
> If there are conflicts, follow the procedure in `claude/developer/guides/merge-release-into-next-version.md` — it branches off `maintenance-10.x`, merges `release/9.1` into that branch (resolving conflicts there), and opens a PR back to `maintenance-10.x`. This keeps `release/9.1` completely unchanged.

This warning exists because this exact mistake has caused serious damage more than once.

---

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

---

## Pre-Release Checklist

⚠️ **Re-check this list at the actual freeze point, not from an earlier snapshot.** A list of "still-open" candidate PRs or "no blocker issues" compiled earlier in a long release session can go stale — PRs merge, issues get filed, mid-session. Re-run the actual `gh pr list`/`gh issue list` queries right before you rely on the results for milestone bookkeeping or freeze sign-off, don't reuse an earlier answer from the same session.

### Code Readiness

- [ ] All planned PRs merged
- [ ] CI passing on master branch
- [ ] No critical open issues blocking release
- [ ] Version numbers updated in both repositories
- [ ] SITL binaries updated in configurator
- [ ] **PG validation passed** (see [Step 0.6](#️-step-06-run-pg-validation-now-before-downloading-anything) above — run this before Phase 2, not after)

### Documentation

- [ ] Release notes drafted
- [ ] **Incompatible settings changes identified and added to release notes** (use scripts/find-incompatible-settings.sh)
- [ ] Breaking changes documented
- [ ] New features documented

### Artifact Verification

- [ ] Firmware hex files downloaded and renamed
- [ ] Configurator artifacts organized by platform (linux/, macos/, windows/)
- [ ] macOS DMG contents verified (no .exe files, correct architecture)
- [ ] **Windows SITL cygwin1.dll verified** (use scripts/verify-windows-sitl.sh)
- [ ] **Configurator SITL tested** (launch SITL, verify version matches firmware)

---

## Next Steps

Once you've verified release readiness:

**→ Proceed to [Phase 2: Downloading Artifacts](2-downloading-artifacts.md)**

