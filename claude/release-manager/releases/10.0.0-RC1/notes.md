# 10.0.0-RC1 Release Notes-to-Self

Working notes for this release cycle. Not a deliverable — internal tracking only.
Updated 2026-09-24 — release cycle is complete except the public announcement (drafted, posting held for Ray's review).

---

## FINAL STATUS (2026-09-24)

Both releases are **published and live**:
- Firmware: https://github.com/iNavFlight/inav/releases/tag/10.0.0-rc1 (`86a0441c`, unchanged all cycle)
- Configurator: https://github.com/iNavFlight/inav-configurator/releases/tag/10.0.0-rc1 (`ce5b9733`, after 3 fix rounds — see Lessons Learned)

Ray confirmed Configurator's Firmware Flasher tab correctly discovers/loads the new firmware. Completion report sent to Manager 2026-09-24. `master` sync checked on both repos — healthy, no action needed (by design, `master` only fast-forwards to a new major at final stable release, not RC1).

**Only remaining step:** public Discord/Facebook announcement. Drafted at `10.0.0-RC1-announcement-{discord.md,facebook.txt}`; Ray is reviewing before posting (as of 2026-09-24, not yet posted). Once posted, this release cycle is fully closed — no further tracking needed here beyond that.

---

## Lessons Learned (apply to RC2 and future releases)

### Three real bugs found in configurator this cycle — process takeaways, not just bug reports

1. **macOS SITL contamination** (recurrence of a 9.0.0-era bug) — `forge.config.js`'s SITL-pruning hook checked for a path before it existed on the macOS packaging step specifically, silently no-op'ing. Both DMGs shipped with Windows/Linux SITL binaries bundled in. **Takeaway:** `guides/30-verifying-artifacts.md` already documents the "9.0.0 lesson learned" DMG-contents check — that check is not a one-time-fixed problem, it needs to actually run every release. It also had a script bug (`verify-dmg-contents.sh` reports false negatives on 7z's benign outer-wrapper error) that almost hid this — always manually extract and inspect if the script says "failed."
2. **Linux x64 SITL glibc regression** — the CI runner's glibc isn't pinned and drifted upward (2.35→2.38), which would have broken SITL for most current Linux users. **Takeaway:** guides now say to build Linux x64 SITL locally, unconditionally, every release, done early (with the version-bump PR) — not treated as conditional or discovered late in artifact verification.
3. **Stale firmware-version-acceptance bounds** — hardcoded min/max firmware version strings were leftover from the 9.x cycle and got missed in the 10.0.0 version bump; Configurator would have rejected the matching firmware outright. **Takeaway:** this class of bug (hardcoded values that should derive from the app's own version) is exactly what self-correcting derivation (e.g. `semver.major()` off the app's own version) prevents for future cycles — worth checking for similar hardcoded-version patterns elsewhere if doing a pre-release audit in future cycles.

All three were caught by the Release Manager's own verification steps (DMG extraction, glibc check, SITL launch+MSP query), not by CI — CI was green throughout. **Don't treat a green CI run as sufficient for a major-version release; the documented Phase 60 verification steps exist precisely because CI doesn't catch these.**

### Process/tooling bugs fixed this cycle

- `validate-pg-for-release.sh` has two false-positive modes (doesn't understand 4-bit PG-version wraparound; compares against a dev-time reference DB instead of the last shipped tag) — **not fixed in code, still open, worth a developer ticket.**
- `count-fixes-and-features.sh` aborted entirely if any single candidate PR number failed to resolve (e.g. noise like `#1`/`#2` extracted from unrelated commit-message text) — fixed to skip implausible numbers and continue past individual failures.
- `verify-dmg-contents.sh`'s 7z-exit-code false negative — documented as a known issue in `guides/30-verifying-artifacts.md`, not yet fixed in the script itself.
- Release-manager guide corrections made this cycle based on things that turned out to be documented wrong: asset naming conventions for both firmware (`inav_X.Y.Z-rcN_TARGET.hex`, verified against the Configurator's actual filename-parsing regex, not against inconsistent historical precedent) and configurator (no RC marker in the filename at all, verified against actual past releases); the `/latest` release URL only working for final releases, never RCs (GitHub's `/latest` ignores prereleases — confirmed it still pointed at old 9.1.0/9.1.1 while our prerelease RC was live).
- **New infra gap found, not yet fixed:** `inav-configurator`'s `release.yml` (the tag-triggered signed-build pipeline, `require_signing: true`) never actually engages for any tag push because no tag-protection ruleset exists matching `v*.*.*`/`*.*.*` — its job silently skips. Not a problem this cycle (branch-push CI already had working signing, confirmed via logs), but the hard-fail-on-bad-signing guarantee `release.yml` is supposed to provide doesn't currently exist for any release. Emailed the Manager to open a project for this.

### Process discipline that worked and should continue

- **Release Manager Key Rule held throughout:** every real bug found (PG version-wraparound false positive, `forge.config.js` hook timing, glibc regression, version-acceptance bounds) was reported and handed to a developer, never fixed directly. All came back clean.
- **Ask before dropping `GITHUB_TOKEN`, every time** — did this consistently after an early-cycle lapse (see git history of this file if needed); no further lapses.
- **Verify against source, not precedent or draft documentation, when they conflict.** Caught real discrepancies this cycle by reading actual code/diffs instead of trusting: a script's raw output (PG validation, fix/feature counts), a wiki draft's claim (`nav_fw_wp_turn_smoothing`'s real rename target), and our own first-draft release notes (CLI paste does NOT trigger settings migration — only Backup/Restore Config buttons do, confirmed via `js/backup_restore.js`).
- **Ask before publishing, every time** — agent never runs `--draft=false`; Ray gave direct instruction for firmware, and configurator was published by Ray directly via the GitHub GUI.

---

## RESOLVED — kept for brief history, no action needed

<details>
<summary>Configurator commit history this cycle (3 supersedes, all fixed)</summary>

`96d12ff5` (original version-bump+SITL PR #2793, macOS contamination bug) → `335538f2` (PR #2797 fixed contamination, glibc regression found) → `b084db8d` (PR #2799 fixed glibc, version-acceptance bounds found stale) → `ce5b9733` (PR #2800 fixed version bounds — final, published).
</details>

<details>
<summary>WASM SITL firmware — deferred to RC2</summary>

Two competing unmerged firmware PRs (#11282, #11314) were never reconciled; Ray decided WASM/PWA is out of scope for RC1 regardless, revisit for RC2. Native SITL unaffected.
</details>

<details>
<summary>Settings-migration profile, version-string reservation — merged early in cycle</summary>

`inav-configurator#2784` (migration profile), `inav#11981`/`inav-configurator#2780` (version-string reservation patches), `inav#12006`/`inav-configurator#2793` (actual 10.0.0 version bumps) — all merged and forward-merged correctly, verified via `gh api compare` ancestry checks. Full detail in `10.0.0-RC1-release-plan.md` Phase 0.5.
</details>

<details>
<summary>PG Validation — 2 false alarms, confirmed non-issues</summary>

`osdConfig_t` (4-bit version wraparound 15→0, not a regression) and `batteryMetersConfig_t` (version only needs to reflect delta vs. last shipped release, not every dev commit). Full reasoning in `10.0.0-RC1-release-plan.md` Phase 20.
</details>

<details>
<summary>Nightly-publish credentials broken (non-blocking, developer has it)</summary>

Both repos' "Build nightly-release" step fails with `Bad credentials` — publish-only, doesn't affect actual build jobs. Already an assigned developer task.
</details>
