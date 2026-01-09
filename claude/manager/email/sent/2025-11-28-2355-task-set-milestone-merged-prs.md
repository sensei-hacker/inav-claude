# Task Assignment: Set Milestone 9.0 on Recently Merged PRs

**Date:** 2025-11-28 23:55
**Project:** Release Management
**Priority:** Medium
**Estimated Effort:** 15 minutes

## Task

Set the milestone to "9.0" on all PRs merged in the last 3 days that don't already have it set.

## PRs Needing Milestone Update

### inav-configurator (5 PRs missing milestone)

| PR | Title |
|----|-------|
| #2437 | Fix 3D model loading in magnetometer tab |
| #2436 | Restore checkMSPPortCount and showMSPWarning functions in ports tab |
| #2434 | Fix ESM conversion in search and logging tabs |
| #2433 | STM32 DFU: Refactor and implement CLI-based reboot protocol |
| #2432 | Fix DFU flash: ensure cleanup callback runs on USB error |

### inav (7 PRs missing milestone)

| PR | Title |
|----|-------|
| #11139 | Revert "[crsf] add temperature, RPM and AirSpeed telemetry" |
| #11137 | Normalize line endings to LF in src/main/target/FLYSPARKF4V4 |
| #11134 | Add I2C compass driver registration for HUMMINGBIRD FC305 |
| #11129 | NEXUSX: USE_DSHOT_DMAR, use TIM2 instead of TIM5 |
| #11095 | Dynamic Custom OSD Elements position changing by companion computer |
| #11025 | [crsf] add temperature, RPM and AirSpeed telemetry |
| #10788 | Add flyspark target |

## Already Have 9.0 Milestone (no action needed)

### inav-configurator
- #2429 - Cleanup old references that should have been `control_profile`

### inav
- #11143 - Add JavaScript programming documentation
- #11131 - Update FlyingRC F4Wing Mini target
- #11122 - Update references to that should be control_profile
- #11032 - MSP2 message exposing 3D attitude, position, and velocity
- #10740 - target: Add JHEMCU F435 AIO target board support

## Commands to Run

```bash
# inav-configurator PRs
gh pr edit 2437 --repo iNavFlight/inav-configurator --milestone "9.0"
gh pr edit 2436 --repo iNavFlight/inav-configurator --milestone "9.0"
gh pr edit 2434 --repo iNavFlight/inav-configurator --milestone "9.0"
gh pr edit 2433 --repo iNavFlight/inav-configurator --milestone "9.0"
gh pr edit 2432 --repo iNavFlight/inav-configurator --milestone "9.0"

# inav PRs
gh pr edit 11139 --repo iNavFlight/inav --milestone "9.0"
gh pr edit 11137 --repo iNavFlight/inav --milestone "9.0"
gh pr edit 11134 --repo iNavFlight/inav --milestone "9.0"
gh pr edit 11129 --repo iNavFlight/inav --milestone "9.0"
gh pr edit 11095 --repo iNavFlight/inav --milestone "9.0"
gh pr edit 11025 --repo iNavFlight/inav --milestone "9.0"
gh pr edit 10788 --repo iNavFlight/inav --milestone "9.0"
```

## Success Criteria

- [ ] All 12 PRs have milestone set to 9.0
- [ ] Verify with `gh pr view <number> --json milestone`
- [ ] Report back with confirmation

---
**Manager**
