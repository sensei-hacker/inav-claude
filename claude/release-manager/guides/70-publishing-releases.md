# Phase 70: Publishing Releases

**Read this guide when:** Draft releases are created, assets are uploaded, and you're ready to make the release public

**Prerequisites:**
- Draft releases created for firmware and configurator (Phase 60)
- All assets uploaded and verified (Phase 60)

**Related guides:**
- [Phase 10: Workflow and Preparation](10-workflow-and-preparation.md)
- [Phase 60: Creating and Uploading Releases](60-creating-releases.md)
- [Phase 80: Post-Release](80-post-release.md)

---

## Overview

This guide covers publishing draft releases and announcing them to the community.

---

## Publishing Releases

> **🚨 AGENT RULE: Do NOT publish releases without explicit human instruction.**
>
> Publishing a release is irreversible and immediately public to all INAV users worldwide. The agent must never run `--draft=false` or any publish command on its own initiative. Wait until the human user explicitly says to publish (e.g., "publish the firmware release now"). "Maintainer approval obtained" is not sufficient — the human user in this session must give the direct instruction.

**Only publish after:**
- All assets uploaded and verified
- Release notes reviewed and approved
- Maintainer approval obtained
- Final SITL testing completed

### Publish Draft Release

**Publish firmware first, then verify before publishing configurator.**

```bash
# Step 1: Publish firmware release  (only run when user explicitly instructs)
gh release edit 9.0.0-rc3 --repo iNavFlight/inav --draft=false
```

#### Step 2: Verify Configurator Sees the Firmware Release

After publishing firmware, open INAV Configurator and go to the Firmware Flasher tab. Verify that the new firmware version appears in the release list. This confirms the GitHub release is properly formatted and discoverable by the configurator's firmware download logic.

**This step must be done by a human** - it requires running the configurator and visually confirming the release appears.

⚠️ **Do not manually publish the Configurator release until this check has passed.** Publishing Configurator before firmware is verified loadable risks shipping a Configurator build whose firmware flasher can't yet find the matching release.

```bash
# Step 3: Publish configurator release (only after firmware is verified in flasher)
gh release edit 9.0.0-rc3 --repo iNavFlight/inav-configurator --draft=false
```

**Note:** The human user must perform the final configurator publish step.

### Verify Published Releases

After publishing, verify on GitHub:

**Firmware:** https://github.com/iNavFlight/inav/releases
**Configurator:** https://github.com/iNavFlight/inav-configurator/releases

Check:
- Tag was created correctly
- All assets are present
- Release notes are correct
- Downloads work
- Configurator firmware flasher lists the new release

---

## Post-Publication Tasks

After publishing releases:

1. **Announce release** — see [Announcement Tips](#announcement-tips) below
   - Discord
   - Forums
   - Social media

2. **Monitor for issues**
   - Watch GitHub issues
   - Check Discord for user reports
   - Monitor RC feedback

3. **Update documentation**
   - Mark release as complete in project tracking
   - Update any pinned issues
   - Document any lessons learned

4. **Prepare for next RC or final release**
   - If RC, monitor feedback for next iteration
   - If final, prepare for potential hotfixes

---

## Announcement Tips

- **No emojis in either Discord or Facebook posts** — plain text/markdown headers only
- **Discord:** 2000-character limit — keep concise, use markdown
- **Facebook:** No markdown, supports images (1200x630 PNG recommended)
- Focus on top 5 features users care about most
- Include download link and upgrade warnings
- **Combined announcements:** Firmware and Configurator are always announced together in one post — users think of it as a single "INAV X.Y.Z" release. Exception: hotfixes that touch only one repo get a targeted announcement, not a combined one.
- **Link to the `/latest` release URL, not the specific version tag — for FINAL/stable releases only.** GitHub's `/latest` endpoint always resolves to the newest release *not* marked prerelease (verified 2026-09-24: with 10.0.0-RC1 published as a prerelease, `/latest` still pointed at the old `9.1.0`/`9.1.1` stable releases). **For an RC announcement, link the specific tag instead** — `/latest` would send readers to the wrong, older release:
  - **Firmware (final release):** https://github.com/iNavFlight/inav/releases/latest
  - **Configurator (final release):** https://github.com/iNavFlight/inav-configurator/releases/latest
  - **RC of either repo:** use `https://github.com/iNavFlight/<repo>/releases/tag/<exact-rc-tag>` instead.
- **Reference examples (emoji-free, current style):** `releases/9.1.0/9.1.0-announcement-discord.md`, `releases/9.1.0/9.1.0-announcement-facebook.txt`
- **Older examples contain emojis — don't copy that part of their style:** `releases/9.0.0/9.0.0-announcement-discord.md`, `releases/9.0.0/9.0.0-announcement-facebook.txt`, `releases/9.1.0-RC1/9.1.0-RC1-announcement-discord.md`, `releases/9.1.0-RC1/9.1.0-RC1-announcement-facebook.txt`

---

## Quick Reference Commands

```bash
# Publish release
gh release edit <version> --repo <owner/repo> --draft=false

# View release
gh release view <version> --repo <owner/repo>
```

---

## Checklist

- [ ] Release notes reviewed
- [ ] Maintainer approval obtained
- [ ] Firmware release published
- [ ] Configurator firmware verified in Firmware Flasher tab
- [ ] Configurator release published
- [ ] Releases verified on GitHub
- [ ] Announcement prepared and posted

---

## Next Steps

After publishing:

**→ Proceed to [Phase 80: Post-Release](80-post-release.md)** for the post-release checklist
