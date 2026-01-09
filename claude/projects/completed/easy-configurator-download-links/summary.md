# Project: Easy Configurator Download Links

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Documentation Enhancement
**Created:** 2025-12-29
**Estimated Effort:** 1-2 hours

## Overview

Add prominent download links to make INAV Configurator easier to find and download.

## Problem

Current user experience requires too many steps:
1. Land on main page
2. Find "Releases" link
3. Scroll to find "Assets"
4. Click "Assets" to expand
5. Choose download file

This is cumbersome for a common user task.

## Solution

Add prominent links to `https://github.com/iNavFlight/inav-configurator/releases/latest` which:
- Automatically points to latest release
- Shows Assets section expanded
- Works for all platforms

## Objectives

1. Add download section to `inav/README.md`
2. Add download section to wiki home page
3. Link to both configurator and firmware
4. Make it easy to find (prominent placement)
5. Test all links work correctly

## Scope

**In Scope:**
- Adding download links to README.md
- Adding download links to wiki (Home.md or main page)
- Linking to both configurator and firmware releases
- Clear user instructions
- PR for README changes
- Wiki commit

**Out of Scope:**
- Automation/workflows (not needed)
- Badges (not needed)
- Changes to release process
- Asset file renaming

## Implementation Steps

1. Review current README.md structure
2. Add download section to README.md
3. Review wiki structure (find main page)
4. Add download section to wiki
5. Test all links
6. Create PR for README
7. Commit wiki changes

## Success Criteria

- [ ] Download links added to README.md
- [ ] Download links added to wiki
- [ ] Links point to `/releases/latest`
- [ ] Both configurator and firmware linked
- [ ] Links tested and working
- [ ] Assets show expanded
- [ ] PR created for README
- [ ] Wiki updated

## Files to Modify

**Primary:**
- `inav/README.md` - Add download section
- `inavwiki/Home.md` (or main wiki page) - Add download section
- `inavwiki/_Sidebar.md` (optional) - Consider adding to sidebar

## Expected Deliverables

1. PR for README.md changes
2. Wiki commit with download links
3. Tested, working links

## Priority Justification

MEDIUM priority because:
- Improves user experience significantly
- Common user frustration
- Quick win (1-2 hours)
- Low risk
- However: Not urgent, not blocking other work

## Notes

**Keep it simple:**
Just add the `/releases/latest` link prominently. No need for complex automation or dynamic version numbers.

**User journey:**
Users need both configurator and firmware, so link to both.

**Two repositories:**
- Configurator: https://github.com/iNavFlight/inav-configurator
- Firmware: https://github.com/iNavFlight/inav

## Related

- INAV Configurator releases
- INAV firmware releases
- User onboarding experience
