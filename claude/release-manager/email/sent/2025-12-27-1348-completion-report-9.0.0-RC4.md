# Task Completed: INAV 9.0.0-RC4 Release Published

**Date:** 2025-12-27
**From:** Release Manager
**Type:** Completion Report

## Status: COMPLETED

## Summary

INAV 9.0.0-RC4 has been successfully released for both firmware and configurator.

## Release Links

- **Firmware:** https://github.com/iNavFlight/inav/releases/tag/9.0.0-RC4
- **Configurator:** https://github.com/iNavFlight/inav-configurator/releases/tag/9.0.0-RC4

## Release Details

| Component | Commit | Assets |
|-----------|--------|--------|
| Firmware | `2c9854d23b9cc22ccc7300d7e5cdecdf89e1b413` | 219 hex files |
| Configurator | `d0ded946dc6303ca9210a8932b90d208f8a08967` | 14 packages |

## Key Changes in RC4

### Firmware
- USB MSC fix for H743 boards
- Power limiting fix
- CRSF buffer overflow fix
- Puya PY25Q128HA flash support
- Airspeed TPA improvements

### Configurator
- MSP protocol decoder state corruption fix
- Serial port handle leak fix ("Cannot lock port" errors)
- Windows SITL path resolution fix
- Linux SITL glibc 2.34 compatibility
- JavaScript Programming improvements

## Process Improvements Documented

During this release, we identified and documented important CI workflow lessons:

1. **CI runs on PR creation, not merge** - artifacts from PR CI only contain that PR's changes
2. **Nightly builds required for complete artifacts** - added maintenance-9.x to nightly-build.yml
3. **Manual testing required before tagging** - added to release documentation

Related PRs:
- PR #11204: Add maintenance-9.x to nightly-build.yml
- PR #11205: Merge maintenance-9.x to master (inav)
- PR #2503: Merge maintenance-9.x to master (configurator)

## Verification Completed

- [x] Windows SITL tested (cygwin1.dll present, SITL runs)
- [x] Linux SITL tested (glibc 2.34, Ubuntu 22.04 compatible)
- [x] All 219 firmware hex files verified
- [x] All 14 configurator packages uploaded

## Archived

- Checklist archived to: `claude/release-manager/archived-checklists/9.0.0-RC4-MASTER-CHECKLIST-COMPLETED.md`

---
**Release Manager**
