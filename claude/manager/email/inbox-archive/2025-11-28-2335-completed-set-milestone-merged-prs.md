# Task Completed: Set Milestone 9.0 on Recently Merged PRs

## Status: COMPLETED

## Summary
Set milestone 9.0 on all 12 merged PRs that were missing it.

## PRs Updated

### inav-configurator (5 PRs)
| PR | Title | Status |
|----|-------|--------|
| #2437 | Fix 3D model loading in magnetometer tab | ✅ 9.0 |
| #2436 | Restore checkMSPPortCount and showMSPWarning functions | ✅ 9.0 |
| #2434 | Fix ESM conversion in search and logging tabs | ✅ 9.0 |
| #2433 | STM32 DFU: Refactor and implement CLI-based reboot | ✅ 9.0 |
| #2432 | Fix DFU flash: ensure cleanup callback runs on USB error | ✅ 9.0 |

### inav (7 PRs)
| PR | Title | Status |
|----|-------|--------|
| #11139 | Revert "[crsf] add temperature, RPM and AirSpeed telemetry" | ✅ 9.0 |
| #11137 | Normalize line endings to LF in FLYSPARKF4V4 | ✅ 9.0 |
| #11134 | Add I2C compass driver registration for HUMMINGBIRD FC305 | ✅ 9.0 |
| #11129 | NEXUSX: USE_DSHOT_DMAR, use TIM2 instead of TIM5 | ✅ 9.0 |
| #11095 | Dynamic Custom OSD Elements position changing | ✅ 9.0 |
| #11025 | [crsf] add temperature, RPM and AirSpeed telemetry | ✅ 9.0 |
| #10788 | Add flyspark target | ✅ 9.0 |

## Notes
- Used GitHub API directly (`gh api`) since `gh pr edit --milestone` had issues with deprecated Projects Classic
- All milestones verified after setting

---
**Developer**
