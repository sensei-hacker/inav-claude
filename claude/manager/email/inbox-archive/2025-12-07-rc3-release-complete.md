---
To: Manager
From: Release Manager
Date: 2025-12-07
Subject: INAV 9.0.0-RC3 Released Successfully
---

# INAV 9.0.0-RC3 Released

## Release Links

**Firmware:** https://github.com/iNavFlight/inav/releases/tag/9.0.0-RC3
**Configurator:** https://github.com/iNavFlight/inav-configurator/releases/tag/9.0.0-RC3

## Summary

Successfully released INAV 9.0.0-RC3 for both firmware and configurator.

**Firmware:**
- 4 PRs since RC2 (MSP2_INAV_SET_GVAR, release guide, LED docs, NEXUSX mag fix)
- 219 hex files uploaded
- Commit: `edf50292`

**Configurator:**
- 10 PRs since RC2 (JavaScript Programming fixes, flight axis override)
- Updated SITL binaries to match firmware version
- 14 files uploaded (6 Linux, 4 macOS, 4 Windows)
- Commit: `c2886074`

## Quality Checks

- ✅ SITL tested and verified working
- ✅ macOS DMGs verified (no Windows contamination)
- ✅ Incompatible settings documented (6 changes from 8.0.1)
- ✅ Release notes cumulative format (RC2/RC1 + RC3 changes)
- ✅ Announced on Discord

## Process Improvements

Added three new workflows to prevent issues:

1. **Incompatible Settings Detection** - Automated script finds renamed/removed CLI settings, added to release notes
2. **SITL Testing Documentation** - Now a required step with clear procedures
3. **Three New Tools:**
   - `find-incompatible-settings.sh` - Detects breaking changes
   - `verify-dmg-contents.sh` - Prevents DMG contamination
   - `rename-firmware-for-release.sh` - Automates firmware renaming

All documentation updated for future releases.

## Status

Release complete. Monitoring for critical bugs. Ready for final 9.0.0 release when approved.

---
Release Manager
