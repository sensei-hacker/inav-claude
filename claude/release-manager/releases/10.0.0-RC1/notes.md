# 10.0.0-RC1 Release Notes-to-Self

Working notes for this release cycle. Not a deliverable — internal tracking only.

---

## OPEN: WASM SITL firmware — waiting on developer investigation

**Status as of 2026-09-20:** Ray has tasked a developer with investigating the WASM SITL situation. **Return to this before finalizing the WASM/PWA portion of the release plan.**

Two competing, unmerged firmware PRs, neither merged into `maintenance-10.x`:
- **PR #11282** (Scavanger, "New SITL TARGET: Webassembly") — targets `maintenance-10.x` (correct base), CI green, unreviewed, stale since 2026-05-23.
- **PR #11314** (Ray/sensei-hacker, `feature/wasm-sitl-squashed`) — targets `release/9.1` (wrong base for a new feature), author's own description frames it as "for comparison... Scavanger's implementation is probably better overall" — not intended to merge as-is.

Configurator side (PR #2729, browser/PWA build expecting a WASM SITL binary) already merged into `maintenance-10.x` on 2026-09-02, so the PWA build currently has no matching firmware WASM SITL to bundle.

**Unaffected:** native (non-WASM) SITL is fully present on `maintenance-10.x` already — this blocker is WASM-only, doesn't affect the rest of the release.

**Next step:** check with Developer/Manager on investigation status before scoping WASM/PWA into RC1 vs. deferring to RC2.

---

## OPEN: Settings-migration profile (9_to_10.json) — needs a developer

Configurator has no `js/migration/9_to_10.json` yet, and `migration_handler.js`'s `MIGRATION_PROFILES` array (currently `[profile_7_to_8, profile_8_to_9]`) needs the new one imported and appended or it's silently never applied.

**Prerequisite:** freeze point (all planned 10.0 PRs merged), not the GitHub draft release — see `guides/10-workflow-and-preparation.md`'s "Settings-Migration Profile" section for why waiting for the draft release would be too late.

**Content source:** `scripts/find-incompatible-settings.sh <9.1.0-or-later-tag> <10.0 freeze commit>` — same diff already needed for the release notes' incompatible-settings section (Phase 50).

**Owner:** developer role (Marc, per Ray, 2026-09-20) — Release Manager doesn't write configurator source.

**Land where:** same version-bump + SITL PR (Phase 10 workflow step 4), before the RC configurator CI build — not a separate later PR.

---

## Version-string reservation (Step 0, major-version-only)

Bumping the previous major's patch level on both repos before setting a `10.0.0` family version string on `maintenance-10.x`, per `guides/10-workflow-and-preparation.md` Step 0.

- Firmware: `release/9.1` next available patch is **9.1.1** (firmware has never shipped 9.1.1 — GH milestone "9.1.1" exists, no "9.1.2" milestone on the firmware repo). Reservation PR: https://github.com/iNavFlight/inav/pull/11981
- Configurator: `maintenance-9.x` next available patch is **9.1.2** (configurator already shipped 9.1.1 as a configurator-only patch on 2026-07-13 — GH milestones "9.1.1" and "9.1.2" both exist on the configurator repo). Reservation PR: https://github.com/iNavFlight/inav-configurator/pull/2780

These numbers differ from each other by design.

**Status (2026-09-20):** both reservation PRs opened, milestones attached, not yet merged. Still need, per repo, in order:
1. Merge the reservation PR above.
2. Forward-merge it into `maintenance-10.x` (branch off `maintenance-10.x`, merge the release/maintenance-9.x branch in, PR back — never GitHub's "Resolve conflicts" button).
3. Only then open the PR that sets the `10.0.0-rc1` version string on `maintenance-10.x`.

**When opening that 10.0.0-rc1 version-string PR:** its description must explicitly remind the maintainer of this same merge order (reservation PR → forward-merge PR → version-bump PR) — GitHub doesn't enforce merge sequencing, so a maintainer merging it early recreates the exact version-collision hazard this whole procedure exists to avoid. (Also now documented in `guides/10-workflow-and-preparation.md` Step 0.)
