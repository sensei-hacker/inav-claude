# Phase 6: Creating and Uploading Releases

**Read this guide when:** Artifacts are verified and release notes are ready

**Prerequisites:**
- Artifacts downloaded and verified (Phases 2-3)
- Release notes written (Phase 5)

**Related guides:**
- [Phase 1: Workflow and Preparation](1-workflow-and-preparation.md)
- [Phase 3: Verifying Artifacts](3-verifying-artifacts.md)
- [Phase 5: Changelog and Notes](5-changelog-and-notes.md)
- [Phase 7: Publishing Releases](7-publishing-releases.md)

---

## Overview

This guide covers creating tags, draft releases, and uploading assets on GitHub. Once assets are uploaded and verified, proceed to [Phase 7](7-publishing-releases.md) to publish and announce.

---

⚠️ **If `gh release create`/`upload`/`edit` returns 403 "Resource not accessible by personal access token":** same restricted-`GITHUB_TOKEN` issue as guide 2's branch-push section. The restriction is intentional. **Ask the human user before dropping it, every time** — see guide 2's warning; it applies here too, and a prior authorization elsewhere in the session doesn't carry over to release creation.

## Check Latest Tags

Before creating new tags, check what tags already exist:

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

---

## Creating Releases and Tags Using gh

**TIP:** You can create both the tag and release in one step using `gh release create`, bypassing the need to work in locked local repositories.

### Benefits

- Creates tag and release atomically
- No need for local repository access
- Works even when repository directory is locked
- Can specify exact commit by SHA
- Creates draft releases for review before publishing

⚠️ **"Atomically" only applies once published.** For a `--draft` release, GitHub does **not** push an actual Git tag ref into the repository yet — the draft just stores the target commitish and the intended tag name internally. `git ls-remote --tags` (or any clone) won't see the tag until the release is published. Don't be surprised that the tag "doesn't exist" while a draft is pending review — that's expected, not a bug.

## ⚠️ Configurator: Signed macOS Requires a Real Tag Push (verify via nightly first)

The signed + notarized macOS build is produced **only** by `.github/workflows/release.yml`, which triggers on a **tag push** matching `v*.*.*` or `*.*.*` (e.g. `9.1.3` or `v9.1.3`; RC tags like `9.1.3-rc1` also match). It calls `ci.yml` with `require_signing: true` — if the signing/notarization secrets are incomplete, the job **fails**.

This means the "draft with `--target`, no real tag until publish" pattern **cannot** produce signed macOS artifacts (a `--draft` release never creates a real tag, so `release.yml` never runs). A pushed tag is effectively immutable, so **don't tag blind** — dry-run the signing via the nightly first (it uses `secrets: inherit` and signs+notarizes whenever the full secret set is present):

1. Merge the version bump + SITL (and WASM SITL) PR — see Phase 1 step 4. This push to the maintenance branch triggers the nightly build automatically.
2. **Dry-run the signing via the nightly (no tag):** download the macOS artifact from that nightly release and check it:
   ```bash
   codesign --verify --deep --strict --verbose=2 "/path/to/INAV Configurator.app"
   xcrun stapler validate "/path/to/INAV Configurator.app"
   ```
   - **Both pass →** all six secrets + the cert/notarization pipeline are proven; proceed to tag.
   - **`codesign` fails →** signing secrets missing (`MACOS_CERT_P12`/`MACOS_CERT_PASSWORD`/`MACOS_SIGN_IDENTITY`).
   - **`codesign` passes but `stapler` fails →** notarization secrets missing (`APPLE_API_KEY_P8`/`APPLE_API_KEY_ID`/`APPLE_API_ISSUER`).

   Fix missing secrets (org/repo admin) **before** tagging — `release.yml` would have failed anyway.
3. **Push a real tag** to trigger `release.yml`:
   ```bash
   cd inav-configurator
   git fetch upstream --tags
   git tag 9.1.3            # or v9.1.3 — both patterns trigger release.yml
   git push upstream 9.1.3  # must land on iNavFlight/inav-configurator to trigger the official build
   ```
4. Wait for the `release.yml` run to finish (it builds every platform and **requires** signed + notarized macOS).
5. Download those artifacts — the signed macOS ones come from **this** run, not PR CI or nightly.
6. Create the GitHub Release referencing the now-existing tag.

**Firmware is unaffected** — hex files aren't signed, so it still uses `gh release create --draft --target <sha>`. Only the configurator is tag-first, and the nightly dry-run above is the pre-tag check that keeps that from being a blind-tag.

The authoritative write-up lives in `inav-configurator/CLAUDE.md` ("macOS Code Signing & Notarization" / "Cutting an official release"). Keep this guide in sync with it.

### Fallbacks if the nightly dry-run doesn't fire

If the nightly build doesn't trigger (e.g. the release branch isn't `maintenance-*`, or nightly is broken), use one of these instead of tagging blind:

**Preferred — `workflow_dispatch` (no tag, no cleanup).** Add `workflow_dispatch:` to `release.yml`'s `on:` block (a configurator source change — coordinate with Developer). Then trigger the exact `require_signing: true` build on any commit without a tag:
```bash
gh workflow run release.yml --repo iNavFlight/inav-configurator --ref <commit-sha>
```
This is the cleanest dry-run: the same fail-closed signing path as a real tag, with zero tags burned.

**Last resort — throwaway test tag.** Push a clearly-named test tag (it matches `*.*.*`, so it triggers `release.yml`), verify, then delete it:
```bash
cd inav-configurator
git fetch upstream --tags
git tag 10.0.0-sign-test
git push upstream 10.0.0-sign-test
# ... wait for release.yml, download + verify the signed macOS artifact ...
git push upstream --delete 10.0.0-sign-test   # clean up the test tag
```
Then push the real tag once it's confirmed good — `10.0.0-RC1` (uppercase `RC` + hyphen), **not** `10.0.0RC1`. The test tag points at the same commit, so its artifacts are the same files the real tag would produce (filenames come from `package.json` + the commit, not the tag name) — you can reuse them, but the real tag still has to exist. A `-sign-test` tag does **not** auto-create a GitHub Release.

### Choosing the Target Commit When the Branch Has Advanced

If new commits landed on the release branch after the CI artifacts were built, check whether those commits affect compiled firmware:

```bash
git log --oneline <ci-commit>..upstream/<release-branch>
git show --stat <each-new-commit>
```

- If every new commit only touches **non-compiled files** (docs, reference databases, CI scripts) → tag the current branch HEAD. Rebuilding from HEAD produces identical binaries, and tagging HEAD is conventional.
- If any new commit changes **firmware source code** (`.c`, `.h`, `CMakeLists.txt`, `settings.yaml`) → re-run CI on the new HEAD and download fresh artifacts before tagging.

### For Firmware

```bash
# Create release + tag at specific commit on GitHub (no local repo access needed)
gh release create 9.1.1-rc1 \
  --repo iNavFlight/inav \
  --target 34e3e4b3d8525931f825e766c28749a4c6342963 \
  --title "INAV 9.1.1-rc1 release candidate for testing" \
  --notes-file claude/release-manager/releases/9.1.1-rc1/9.1.1-rc1-firmware-release-notes.md \
  --prerelease \
  --draft
```

**Parameters explained:**
- `9.1.1-rc1` - The tag name
- `--target` - Specific commit SHA to tag
- `--title` - Release title shown on GitHub
- `--notes-file` - Path to release notes markdown file
- `--prerelease` - Mark as pre-release (for RC releases)
- `--draft` - Create as draft for review before publishing

### For Configurator

```bash
# Create release + tag at specific commit
gh release create 9.1.1-rc1 \
  --repo iNavFlight/inav-configurator \
  --target 9dbd346dcf941b31f97ccb8418ede367044eb93c \
  --title "INAV Configurator 9.1.1-rc1 release candidate for testing" \
  --notes-file claude/release-manager/releases/9.1.1-rc1/9.1.1-rc1-configurator-release-notes.md \
  --prerelease \
  --draft
```

### For Final Releases (Non-RC)

For final releases, omit the `--prerelease` flag:

```bash
gh release create 9.1.1 \
  --repo iNavFlight/inav \
  --target <commit-sha> \
  --title "INAV 9.1.1" \
  --notes-file claude/release-manager/releases/9.1.1/9.1.1-firmware-release-notes.md \
  --draft
```

---

## Uploading Assets to Draft Releases

After creating the draft release, upload artifacts using `gh release upload`:

### Upload Configurator Builds

Upload by platform to maintain organization:

```bash
# Upload configurator builds by platform
cd claude/release-manager/downloads/configurator-9.1.1-rc1

gh release upload 9.1.1-rc1 linux/* --repo iNavFlight/inav-configurator
gh release upload 9.1.1-rc1 macos/* --repo iNavFlight/inav-configurator
gh release upload 9.1.1-rc1 windows/* --repo iNavFlight/inav-configurator
```

### Upload the PWA Build (10.x+)

The browser-based PWA build is an additional configurator asset, built from `inav-configurator/dist-web/` (via `yarn web:build`). Upload it alongside the desktop packages:

```bash
cd claude/release-manager/downloads/configurator-9.1.1-rc1
gh release upload 9.1.1-rc1 <pwa-artifact> --repo iNavFlight/inav-configurator
```

⚠️ **Confirm the packaging format first.** As of 2026-09-16 there is no standardized zip/archive step for `dist-web/` (see the [WASM SITL + Browser/PWA Build](wasm-sitl-pwa-build.md) guide). Agree on the artifact name/format with maintainers before the release rather than inventing one on the fly.

⚠️ **The PWA must be built from the same release commit as the desktop artifacts** and must include the WASM SITL that was in place before CI ran. It is a separate asset — do not rebuild or modify the already-signed desktop artifacts to "add" the PWA.

### Upload Firmware Hex Files

```bash
# Upload firmware hex files
cd ../firmware-9.1.1-rc1
gh release upload 9.1.1-rc1 *.hex --repo iNavFlight/inav
```

**Note:** Files should already be renamed (CI suffix removed, RC number added) as per Phase 2.

---

## Asset Naming Conventions

Ensure assets follow these naming patterns:

### Firmware (RC releases)
- Pattern: `inav_<version>_RC<n>_<TARGET>.hex`
- Example: `inav_9.1.1_RC2_MATEKF405.hex`

### Firmware (final releases)
- Pattern: `inav_<version>_<TARGET>.hex`
- Example: `inav_9.1.1_MATEKF405.hex`

### Configurator (RC releases)
- Pattern: `INAV-Configurator_<platform>_<version>_RC<n>.<ext>`
- Example: `INAV-Configurator_linux_x64_9.1.1_RC2.deb`

### Configurator (final releases)
- Pattern: `INAV-Configurator_<platform>_<version>.<ext>`
- Example: `INAV-Configurator_linux_x64_9.1.1.deb`

---

## Managing Release Assets

### Renaming Assets Without Re-uploading

You can rename release assets directly via the GitHub API without re-uploading:

```bash
# Get release ID and asset IDs
gh api repos/iNavFlight/inav/releases --jq '.[] | select(.draft == true) | {id: .id, name: .name}'
gh api repos/iNavFlight/inav/releases/RELEASE_ID/assets --paginate --jq '.[] | "\(.id) \(.name)"'

# Rename a single asset
gh api -X PATCH "repos/iNavFlight/inav/releases/assets/ASSET_ID" -f name="new-filename.hex"
```

**Important:** The GitHub API paginates results (30 per page by default). Always use `--paginate` when listing assets to get all of them.

### Bulk Renaming Firmware Assets

If you uploaded files with the wrong naming pattern:

```bash
# Bulk rename firmware assets (add RC number, remove ci- suffix)
gh api repos/iNavFlight/inav/releases/RELEASE_ID/assets --paginate --jq '.[] | "\(.id) \(.name)"' > /tmp/assets.txt

cat /tmp/assets.txt | while read -r id name; do
  target=$(echo "$name" | sed -E 's/inav_[0-9]+\.[0-9]+\.[0-9]+_(.*)_ci-.*/\1/')
  newname="inav_9.1.1_RC2_${target}.hex"
  gh api -X PATCH "repos/iNavFlight/inav/releases/assets/$id" -f name="$newname" --silent
done
```

### Deleting Release Assets

If a draft release has outdated assets that need to be replaced (e.g., from a previous upload attempt), delete them before uploading new ones:

```bash
# Delete an asset by ID
gh api -X DELETE "repos/iNavFlight/inav/releases/assets/ASSET_ID"
```

---

## Managing Draft Releases

### List All Releases

```bash
# List releases (shows both draft and published)
gh release list --repo iNavFlight/inav --limit 10
gh release list --repo iNavFlight/inav-configurator --limit 10
```

### View Draft Release

```bash
# View release details
gh release view 9.1.1-rc1 --repo iNavFlight/inav
gh release view 9.1.1-rc1 --repo iNavFlight/inav-configurator
```

### Edit Release Notes

```bash
# Edit release notes after creating draft
gh release edit 9.1.1-rc1 --repo iNavFlight/inav \
  --notes-file claude/release-manager/releases/9.1.1-rc1/9.1.1-rc1-firmware-release-notes.md
```

---

## Alternative: Traditional Git Tagging (Required for Configurator Signed Builds)

For firmware you can still use `gh release create`. For the **configurator**, a real `git tag` + `git push` is now **required** to trigger the signed macOS build (see the section above) — it is not optional.

```bash
# Create tag locally
cd inav
git tag -a 9.1.1-rc1 -m "INAV 9.1.1-rc1"

# Push tag to GitHub
git push origin 9.1.1-rc1

# Then create release
gh release create 9.1.1-rc1 --draft --title "INAV 9.1.1-rc1" --notes-file release-notes.md
```

Using `gh release create` with `--target` remains the preferred path for **firmware** (it works even when repos are locked). For the **configurator**, push the tag explicitly (`git push upstream <tag>`) to trigger `release.yml`.

---

## Troubleshooting

### Release Creation Fails

**Error: "Reference already exists"**
- Tag already exists on GitHub
- Check: `git ls-remote --tags origin | grep 9.1.1-rc1`
- Solution: Delete tag if incorrect, or use existing tag

**Error: "Not found"**
- Commit SHA doesn't exist
- Check: `gh api repos/iNavFlight/inav/commits/<sha>`
- Solution: Verify commit SHA is correct and pushed

### Upload Fails

**Error: "release not found"**
- Release doesn't exist yet
- Solution: Create draft release first

**Error: "asset already exists"**
- File with same name already uploaded
- Solution: Delete old asset or rename new one

---

## Quick Reference Commands

```bash
# Create draft release with tag
gh release create <version> --repo <owner/repo> --target <commit> --draft --prerelease --notes-file <file>

# Upload assets
gh release upload <version> <files> --repo <owner/repo>

# View release
gh release view <version> --repo <owner/repo>

# List assets
gh api repos/<owner/repo>/releases/<id>/assets --paginate
```

---

## Checklist

- [ ] Latest tags checked
- [ ] Target commit SHA identified for firmware
- [ ] Target commit SHA identified for configurator
- [ ] Draft release created for firmware (with tag)
- [ ] Draft release created for configurator (with tag)
- [ ] Firmware hex files uploaded
- [ ] Configurator Linux builds uploaded
- [ ] Configurator macOS builds uploaded
- [ ] Configurator Windows builds uploaded
- [ ] Configurator PWA build uploaded (10.x+)
- [ ] Asset naming verified
- [ ] Release notes reviewed

---

⚠️ **Reminder for the human user before Phase 7:** Publish firmware first, then verify the release loads correctly in the Configurator's Firmware Flasher tab, **before** publishing the Configurator release itself. Do not manually publish Configurator ahead of that check — see [Phase 7](7-publishing-releases.md) for the full sequence.

---

## Next Steps

Once drafts are created and assets are uploaded:

**→ Proceed to [Phase 7: Publishing Releases](7-publishing-releases.md)**
