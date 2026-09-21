# Major Version Bump (One-Time Setup for a New Major Version)

**Read this guide when:** this release is the first RC of a new major version (e.g. `10.0.0-RC1`). It does not apply to RC-to-RC releases, patch releases, or minor releases within an existing major version — those skip straight to [Phase 10](10-workflow-and-preparation.md).

**Read this before Phase 10.** It covers three one-time administrative steps a new major version needs, in order, plus the settings-migration profile that goes with it if the new major changes CLI settings.

---

## Why these are bundled together

All three steps below exist because of the same underlying fact: a new major version's version string gets set on a branch (`maintenance-X.x`) that stays alive and mutable for a long time afterward — through its own RC cycle, its eventual release, and possibly patch releases after that. Get any of these three out of order and something later silently clobbers or orphans something earlier. Do them in this order:

1. Reserve the previous major's next patch number (prevents a later hotfix from clobbering the new version string when forward-merged)
2. Create the maintenance branch for the major version *after* this one (gives new breaking work somewhere to go while this major stabilizes, instead of landing on the branch you're trying to freeze)
3. Set this major's own version string

---

## Step 1: Reserve the Previous Major's Patch Number

**The hazard:** once the new major's version number is set (e.g. `10.0.0` on `maintenance-10.x`), any later patch fix on the previous major's release branch (e.g. `release/9.1` → `9.1.1`) has to be merged forward into the new major's branch, per [Post-Release: Merging Changes Upward](10-workflow-and-preparation.md#️-post-release-merging-changes-upward-to-the-next-version). If that forward-merge happens *after* the new version was already set, it can carry the old branch's version-string commit along with it — silently overwriting the version you just set.

**Do this, in order, before setting the new major's version number:**

1. On the previous major's release branch (e.g. `release/9.1`), bump the patch level (e.g. to `9.1.2`) — even if there's no pending bug fix. This reserves the next patch number. **Check each repo's actual next-unused patch number rather than assuming firmware and configurator match** — they can drift (e.g. a configurator-only patch release uses up a number on that repo but not on firmware).
2. **Ensure a GitHub milestone exists for that patch version** on each repo, creating it first if missing (`gh api repos/<owner/repo>/milestones -f title=<version>`). A version-string bump PR with no milestone to attach to falls through the cracks of PR/milestone tracking.
3. Commit that patch-level bump.
4. Open a PR carrying it forward into the new major's branch, following the [forward-merge procedure](10-workflow-and-preparation.md#️-post-release-merging-changes-upward-to-the-next-version) — **never use GitHub's "Resolve conflicts" button** on that PR. Attach the milestone from step 2.
5. **Only after that PR merges**, proceed to Step 3 below and set the new major's own version number.

This ordering exists because a version bump landing on the new major's branch before the previous major's patch reservation is merged forward can get silently reverted by that later merge.

---

## Step 2: Create the Next Major's Maintenance Branch

Create the maintenance branch for the major version *after* the one you're releasing now — e.g. while cutting `10.0.0-RC1`, create `maintenance-11.x`.

**When:** at the first RC of the new major version — not at final. Once a version enters RC/stabilization, its own maintenance branch should take only fixes; new breaking work needs somewhere else to go, or it either destabilizes the RC or has nowhere to land.

**Create the branch** (off the new major's current tip):

```bash
COMMIT_SHA="<full-40-char-sha>"

# inav
gh api repos/iNavFlight/inav/git/refs -f ref="refs/heads/maintenance-11.x" -f sha="$COMMIT_SHA"

# inav-configurator
gh api repos/iNavFlight/inav-configurator/git/refs -f ref="refs/heads/maintenance-11.x" -f sha="$COMMIT_SHA"
```

**Create the matching GitHub milestone** for the new major version on both repos, if one doesn't already exist.

**Update the PR branch-suggestion workflow** on both repos (`.github/workflows/pr-branch-suggestion.yml`), which comments on PRs targeting `master` to suggest the right version branch. Update the branch names it mentions to the current compatible/breaking pair (e.g. `maintenance-10.x` compatible, `maintenance-11.x` breaking).

**Base this PR on the OLDEST actively-maintained branch, not the newest.** This is a CI/workflow-only change, and `master` only receives content via the normal forward-merge chain from older branches. A PR based on `maintenance-11.x` will never reach `master` or any branch older than it — base it on the oldest active branch instead (currently `release/9.1` for inav, `maintenance-9.x` for inav-configurator) so it flows forward through every branch as each does its routine forward-merge. See the "CI/workflow-only changes" exception in `.claude/skills/git-workflow/SKILL.md`'s base-branch table.

**Update `.claude/skills/git-workflow/SKILL.md`'s base-branch decision table** to match — that table is the single authoritative source for base-branch decisions; every other doc should point to it, not repeat it.

---

## Step 3: Set the New Major's Version String

Only after Step 1's forward-merge PR has actually merged. See the [Version Numbering](../README.md#version-numbering) reference for the exact commands (`CMakeLists.txt` for firmware, `npm version <X.Y.Z> --no-git-tag-version` for configurator).

**In the PR that sets this version string**, explicitly remind the maintainer of the required merge order in its description, since GitHub won't enforce it:

1. Merge Step 1's patch-reservation PR into the previous major's release branch first.
2. Merge Step 1's forward-merge PR carrying that patch bump into the new major's branch next.
3. Only then merge this PR.

A maintainer merging this PR out of order — before the patch reservation has landed and been forward-merged — recreates the exact hazard Step 1 exists to avoid.

---

## Settings-Migration Profile (Only If This Major Changes CLI Settings)

Configurator auto-migrates a user's CLI backup/settings across a major version bump using a JSON profile — e.g. `inav-configurator/js/migration/8_to_9.json` for the 8→9 jump. **This does not exist automatically; a developer must create it, and it must land before the release-candidate configurator build, not after.**

1. **Prerequisite: the freeze point, not the GitHub draft release.** The profile needs every feature/fix PR that's landing in this version to already be merged (so no settings get renamed/removed after the profile is written). **Do not wait for the GitHub draft release** ([Phase 60](60-creating-releases.md)) — that happens after configurator artifacts are already built and verified; a profile added that late means rebuilding.
2. **Assign to a developer role** (not Release Manager — see "Key Rule" in `claude/release-manager/CLAUDE.md`). Base the profile's `settingRenames`/`removed` content on the same diff `scripts/find-incompatible-settings.sh` produces for [Phase 50](50-changelog-and-notes.md)'s incompatible-settings report — same underlying data, two consumers (human-readable release notes + machine-readable migration profile). Cross-check against the draft release's auto-generated PR list ([Phase 60](60-creating-releases.md#open-the-draft-release-early-with-auto-generated-notes)) to confirm every settings-affecting PR is accounted for.
3. **Create `inav-configurator/js/migration/<old>_to_<new>.json`** (e.g. `9_to_10.json`), following the shape of the existing `8_to_9.json` (`fromVersion`, `toVersion`, `commandRenames`, `settingRenames`, `valueReplacements`, `removed`, `settingPatternMappings`, `warnings`).
4. **Wire it into `js/migration/migration_handler.js`** — `MIGRATION_PROFILES` is a hardcoded array; the new profile must be imported and appended, or it's silently never applied. Same class of gotcha as the WASM SITL static-import filename (see the [WASM SITL + Browser/PWA Build](wasm-sitl-pwa-build.md) guide).
5. **Land this in the same version-bump + SITL PR** ([Phase 10](10-workflow-and-preparation.md)'s Release Workflow step 4) so it ships in the same CI-built configurator artifacts as everything else for this release — don't split it into a separate later PR.

---

## Next Steps

Once Steps 1-3 above are done (and the migration profile is assigned, if applicable): proceed to [Phase 10: Workflow and Preparation](10-workflow-and-preparation.md) for the ordinary release process.
