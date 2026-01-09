# Task Assignment: Add Easy Configurator Download Links

**Date:** 2025-12-29 12:00
**Project:** easy-configurator-download-links
**Priority:** MEDIUM
**Estimated Effort:** 1-2 hours
**Type:** Documentation Enhancement

## Task

Make INAV Configurator downloads easier to find by adding prominent download links to the main project pages.

## Problem

**Current user experience is poor:**
1. User lands on main page (README or wiki)
2. User has to find "Releases" link
3. User scrolls down to find "Assets" section
4. User clicks "Assets" to expand
5. User finally sees download files

**This is too many steps** for a common user task (downloading the configurator).

## Solution

Add a prominent link to: **https://github.com/iNavFlight/inav-configurator/releases/latest**

This URL automatically:
- Points to the latest release
- Shows the Assets section expanded
- Works for all platforms

## What to Do

### 1. Add Download Link to README.md

**Location:** `inav/README.md`

**Add a prominent downloads section** near the top of the README (after the intro, before detailed documentation).

**Suggested wording:**
```markdown
## Download INAV Configurator

**Get the latest version:** [INAV Configurator Downloads](https://github.com/iNavFlight/inav-configurator/releases/latest)

Choose your platform (Windows, macOS, or Linux) from the Assets section.

**Looking for firmware?** [INAV Firmware Releases](https://github.com/iNavFlight/inav/releases)
```

**Notes:**
- Keep it simple and clear
- Explain that users select their platform from Assets
- Also link to firmware releases (users need both)
- Adapt wording to match README's existing style

### 2. Add Download Link to Wiki

**Location:** `inavwiki/Home.md` (or appropriate main page)

**Add similar download section** to the wiki home page.

**Placement:** Near the top, in a clearly visible section.

**Suggested wording:**
```markdown
## Downloads

**INAV Configurator:** [Download latest version](https://github.com/iNavFlight/inav-configurator/releases/latest) (Windows, macOS, Linux)

**INAV Firmware:** [Download latest firmware](https://github.com/iNavFlight/inav/releases/latest)
```

**Consider:**
- Wiki might have different formatting/structure than README
- Should match wiki's existing style
- May want to add to sidebar as well (check `_Sidebar.md`)

## Implementation Steps

1. **Check current README.md**
   - Review structure and style
   - Identify best location for download section
   - Keep it prominent but not disruptive

2. **Update README.md**
   - Add download section
   - Link to both configurator and firmware
   - Keep wording clear and simple

3. **Check wiki structure**
   - Find main page (likely Home.md)
   - Check existing sections and style
   - Check if there's a sidebar (_Sidebar.md)

4. **Update wiki**
   - Add download section to main page
   - Consider adding to sidebar for easy access
   - Match wiki's formatting conventions

5. **Test the links**
   - Verify configurator link works
   - Verify firmware link works
   - Confirm Assets section shows expanded

6. **Create PR for README**
   - For README: Create PR against main inav repo
   - Use clear commit message
   - Explain the user experience improvement

7. **Update wiki**
   - For wiki: Commit directly to wiki repo (or create PR if that's the workflow)
   - Use clear commit message

## Success Criteria

- [ ] Download link added to `inav/README.md`
- [ ] Download link added to wiki home page
- [ ] Links tested and working
- [ ] Both configurator and firmware links included
- [ ] Links easy to find (prominent placement)
- [ ] Clear instructions for users (select platform from Assets)
- [ ] PR created for README changes
- [ ] Wiki updated (direct commit or PR)
- [ ] Links verified to show Assets expanded

## Important Notes

**Two Separate Repositories:**
- **Configurator:** https://github.com/iNavFlight/inav-configurator
- **Firmware:** https://github.com/iNavFlight/inav
- Users need BOTH (configurator to flash firmware to flight controller)

**Make both easy to find** - users often need both.

**Wiki Repository:**
- Wiki is at `inavwiki/` in your workspace
- May need to pull latest before editing
- Check if wiki has its own contribution guidelines
- Verify which page is the main landing page (Home.md, Welcome.md, etc.)

**Consider User Journey:**
Think about what a new user needs:
1. Download configurator
2. Download firmware
3. Flash firmware to board

Your download section should guide them to both resources.

**Keep It Simple:**
The goal is to save users 3-4 clicks. A simple prominent link is all that's needed.

---
**Manager**
