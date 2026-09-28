# Phase 50: Changelog and Release Notes

**Read this guide when:** Ready to generate changelogs and write release notes

**Note:** This can be done in parallel with artifact download/verification

**Related guides:**
- [Phase 10: Workflow and Preparation](10-workflow-and-preparation.md) - RC Release Pattern
- [Phase 60: Creating Releases](60-creating-releases.md)

---

## Overview

This guide covers generating changelogs from merged PRs, identifying incompatible settings changes, and writing release notes.

---

## Changelog Generation

### Start From the Draft Release's Auto-Generated Notes

Per [Phase 60](60-creating-releases.md#open-the-draft-release-early-with-auto-generated-notes), open each repo's draft release right after freeze with `--generate-notes` — this is the primary source list of merged PRs. Rewrite it in user-facing terms for the final notes; don't manually re-derive the PR list if the draft already has it.

### List PRs Since Last Tag (if a draft wasn't opened yet)

#### Using gh pr list

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

#### ⚠️ Verify Each PR Is on the Correct Branch

Before including a PR in release notes, confirm it is actually merged into the release branch (e.g., `maintenance-9.x`), not only into a future branch (`maintenance-10.x`). PRs sometimes target the wrong branch or get cherry-picked, and a PR description alone is not reliable.

```bash
# Confirm a PR's merge commit exists on the release branch
git log upstream/maintenance-9.x --oneline | grep <short-sha>

# Or check all recent merge commits on the branch
git log upstream/maintenance-9.x --oneline --merges | head -30
```

If a PR is not in that output, it is not part of this release — exclude it from the release notes regardless of what the PR description says.

#### Alternative: Using git log

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

### Fix/Feature Counts for Summary Notes and Social Posts

The short release-body notes and Discord/Facebook announcements should state the total number of fixes and the total number of new features/enhancements **since the last stable release** (not since the last RC). Use:

```bash
./claude/release-manager/scripts/count-fixes-and-features.sh ../../inav 9.0.1 upstream/release/9.1 iNavFlight/inav
./claude/release-manager/scripts/count-fixes-and-features.sh ../../inav-configurator 9.0.1 upstream/maintenance-9.x iNavFlight/inav-configurator
```

It's a title-keyword heuristic, not a precise audit — check the "Excluded" list it prints and adjust the old-tag/new-ref args to match this release's actual last-stable tag and branch.

### What Not to List as a Configurator Highlight

"SITL binary updated to match firmware" is **not** a highlight — every release updates the bundled SITL, it's routine and not user-facing news. If the Phase 20 SITL PR is the only configurator change worth mentioning in a given cycle, look for an actual feature/UI improvement to headline instead (e.g., "LED tab improvements") rather than manufacturing a highlight out of housekeeping.

### Reviewing Recent Releases for Style

Before writing release notes, review recent releases to match the format and level of detail:

```bash
# View recent releases
gh release list --repo iNavFlight/inav --limit 5
gh release list --repo iNavFlight/inav-configurator --limit 5

# View specific release notes
gh release view 9.0.0-RC2 --repo iNavFlight/inav
```

---

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

### Using the Automation Script

Save as `claude/release-manager/scripts/find-incompatible-settings.sh`:

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

Run it:

```bash
# From release-manager directory
./scripts/find-incompatible-settings.sh 8.0.1 9.0.0-RC3

# Review output and create the renamed/removed lists
# Use git diff to determine renames vs removals
cd inav
git diff 8.0.1..9.0.0-RC3 -- src/main/fc/settings.yaml | less
```

### Creating the Incompatibility Report

Create a document listing:

1. **Renamed settings** - Show old name → new name
2. **Removed settings** - Explain why they were removed
3. **Migration instructions** - How users should update their diff

**Example:** `claude/release-manager/releases/9.1.0/9.1.0-INCOMPATIBLE-SETTINGS.md`

### Where to Document

1. **Release notes** - Add "Incompatible Settings" section
2. **Wiki release notes** - Add to upgrade instructions
3. **Separate document** - For reference during user support
4. **Major versions only:** this same renamed/removed data is also the input for Configurator's settings-migration profile (`js/migration/<old>_to_<new>.json`) — see [05-major-version-bump.md's Settings-Migration Profile section](05-major-version-bump.md#settings-migration-profile-only-if-this-major-changes-cli-settings). That's a developer task, not a release-notes task, but hand them this output rather than making them re-derive it.

### Common Types of Changes

- **Renamed for clarity:** `controlrate_profile` → `use_control_profile`
- **Terminology changes:** `pid_profile` → `control_profile` (major refactoring)
- **Removed features:** `reboot_character` (legacy MSP method removed)
- **Value format changes:** `pwm2centideg` → `decadegrees` (unit change)

---

## Release Notes Template for Incompatibilities

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
1. **Backup Config** (Firmware Flasher tab) before flashing
2. Flash new firmware with **Full Chip Erase**
3. **Restore Config** (same tab) after flashing — this is what runs Configurator's automatic settings-migration tool, if one exists for this version jump
4. If you use the manual CLI `diff all` path instead, none of the above gets auto-migrated — you must hand-edit the renamed/removed settings yourself

See full upgrade guide: https://github.com/iNavFlight/inav/wiki/X.0.0-Release-Notes
```

⚠️ **Don't claim the CLI `diff all` path triggers automatic migration — confirmed false, 10.0.0-RC1 (2026-09-24).** Verified against source: `MigrationHandler.migrateBackupData` is only called from `js/backup_restore.js`, wired into the Firmware Flasher tab's Backup Config/Restore Config buttons; `tabs/cli.js` has no migration reference at all. Our first draft of 10.0.0-RC1's release notes got this wrong and had to be corrected before publishing — check this again if a future release's migration profile changes how it's wired in.

---

## RC Release Notes Pattern

### RC Stability Disclaimer (prepend to every RC's notes)

Ray added this to the top of 10.0.0-RC1's published firmware notes (2026-09-23) and asked that future RCs use similar text. Adapt the bracketed parts per release; keep the structure:

```markdown
This is [the first Release Candidate for INAV 10.0, a new major version / Release Candidate N for INAV X.Y].
This build contains significant new features first seen in this release. A release candidate is for testing out the new features prior to the stable release planned for [target month/quarter]. If you prefer a more reliable version and want bug fixes only, choose the latest release in the [X.Y-1.x] series instead.
```

For RC releases, follow the **cumulative** pattern (see [Phase 10: Workflow and Preparation](10-workflow-and-preparation.md#rc-release-pattern-cumulative-approach) for details).

**Key points:**
- Each RC copies all content from previous RC
- Adds new section at top documenting changes since last RC
- Keeps all previous sections intact

**Example for RC3:**

```markdown
# INAV 9.0.0-RC3

## Changes in RC3 (from RC2)
* Fix X
* Fix Y

## Changes in RC2 (from RC1)
* Fix A
* Fix B

[All RC1 content below]
```

---

## Final Release Notes Pattern

**For final/stable releases** (e.g., 9.0.0, not RC), use a **summary** pattern instead of listing each individual RC:

**Key points:**
- List changes from last RC to final (e.g., "Changes in 9.0.0 since RC4")
- Provide a high-level summary of ALL changes since the last stable release
- Do NOT include individual RC sections (RC4, RC3, RC2, RC1)
- Users care about what's new since the last stable, not the RC progression

**Example for 9.0.0 final:**

```markdown
# INAV 9.0.0

This is the stable 9.0.0 release. For complete details, see the [9.0.0 Release Notes Wiki](https://github.com/iNavFlight/inav/wiki/9.0.0-Release-Notes).

---

## Changes in 9.0.0 (since RC4)

### New Features
- Feature added after RC4

### Bug Fixes
- Fix added after RC4

---

## ⚠️ Important Upgrade Information

### Flashing Notes
- **Full chip erase REQUIRED** when upgrading from 8.x
- Back up your configuration with `diff all` before flashing

### Incompatible Settings Changes
[List any renamed/removed settings]

---

## Highlights of INAV 9.0

- **JavaScript Logic Conditions** - Full programming capability
- **Enhanced Navigation** - Improved altitude control
- **OSD Customization** - New elements and layouts
- **Expanded Hardware Support** - 32+ new targets
[Summary of key features across ALL RCs since 8.0.1]

---

**Full Changelog:** https://github.com/iNavFlight/inav/compare/8.0.1...9.0.0
```

**Why this format?**
- Cleaner and more user-friendly
- End users don't need the RC-by-RC progression
- Focuses on what matters: changes since last stable release
- Highlights section provides quick overview

**What NOT to include:**
- ❌ "Changes in RC4 (from RC3)"
- ❌ "Changes in RC3 (from RC2)"
- ❌ "Changes in RC2 (from RC1)"
- ❌ "RC1 Key Features"

These sections were useful during the RC testing phase, but for the final release, users just want a summary of what's new.

---

## Patch Release Notes Pattern (x.y.1, x.y.2, etc.)

**For patch releases** (e.g., 9.0.1, 9.0.2), each release carries forward the full story of the major version:

**Structure:**
1. **"Changes since x.y.0"** - What's new in this specific patch (bugs fixed, targets added)
2. **Upgrade instructions** - Simple path from previous patch, full path from previous major
3. **"Major Changes in x.x Since (previous major)"** - Combined section covering ALL changes in the major version series

**How to construct:**
1. Copy the x.y.0 release notes as your base
2. Merge the "Changes in x.y.0 (since last RC)" section INTO the "Major Changes" section - producing one combined list of everything new in x.y vs the previous major version
3. Prepend a new "Changes since x.y.0" section with the patch-specific changes

**Why this format:**
- Users upgrading from 9.0.0 → 9.0.1 see exactly what changed at the top
- Users upgrading from 8.x → 9.0.1 get the full picture of INAV 9.x below
- Each release is self-contained - no need to read previous release notes

**Configurator compatibility note:** The configurator release notes should say "intended to be used with INAV 9 firmware" (major version only), not "INAV 9.0.1 firmware". Firmware and configurator are compatible within a major version.

**Example:** See `claude/release-manager/releases/9.1.1/9.1.1-firmware-release-notes.md`

---

## Where to Save Release Notes

Create separate files for firmware and configurator, inside a per-release-cycle folder under `releases/` (one folder per tag — RC and final each get their own):

```
claude/release-manager/releases/9.1.0-RC3/
├── 9.1.0-RC3-firmware-release-notes.md
└── 9.1.0-RC3-configurator-release-notes.md
```

These files will be used when creating releases in Phase 60. These are **short** GitHub-release-body notes — they don't need the full detail the wiki page carries; link to the wiki for that.

### Wiki Release Notes (separate, fuller detail)

Each major/minor release also gets a fuller wiki page, maintained independently of the short release-body notes above:

- **Firmware:** `inavwiki/<version>-Release-Notes.md`, wiki page at `https://github.com/iNavFlight/inav/wiki/<version>-Release-Notes` (local checkout: `inavwiki/`, remote `upstream` = `iNavFlight/inav.wiki.git`)
- **Configurator:** `INAV-Configurator-<major>.<minor>-Release-Notes.md` on the *configurator's own* wiki, `https://github.com/iNavFlight/inav-configurator/wiki/INAV-Configurator-<major>.<minor>-Release-Notes` — there is no local checkout by default; clone `https://github.com/iNavFlight/inav-configurator.wiki.git` to a scratch path if you need it

A draft of these pages is often started early (e.g., at RC1) and won't include PRs merged afterward — always check `git log` for what's actually landed since the page was last touched before treating it as current. Update both pages with what's new since the last edit as part of this phase, not just the short release-body notes.

⚠️ `inavwiki/` is a shared checkout — `git pull` can trigger a rebase against unrelated in-progress content and leave it conflicted. If that happens, `git rebase --abort` immediately rather than resolving conflicts in files you don't own.

---

## Release Notes Checklist

- [ ] Changelog generated for firmware (list of PRs)
- [ ] Changelog generated for configurator (list of PRs)
- [ ] PRs categorized (features, fixes, improvements)
- [ ] Contributors credited
- [ ] **Incompatible settings identified** (for major versions)
- [ ] Incompatible settings section added to release notes
- [ ] RC cumulative pattern followed (if applicable)
- [ ] Release notes saved to files
- [ ] Full changelog links prepared

---

## Next Steps

Once release notes are complete:

**→ Proceed to [Phase 60: Creating Releases](60-creating-releases.md)**
