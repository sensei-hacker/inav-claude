# GPS Test Script Investigation Notes

**Date:** 2025-11-29
**Task:** Investigate GPS recovery bug and verify fix for PR #11144

## Summary of Findings

### The Bug Mechanism (FULLY TRACED)

The bug in issue #11049 and #10893 works as follows:

1. **GPS is lost** → `onNewGPSData()` returns early, sets `isFirstGPSUpdate = true`
2. **GPS recovers** → First reading enters main block, but `if (!isFirstGPSUpdate)` is FALSE
3. **`lastUpdateTime` NOT updated** (line 261 is inside the skipped block) ← THE BUG
4. **Timeout check fails** → In `calculateCurrentValidityFlags()` line 482:
   ```c
   ((currentTimeUs - posEstimator.gps.lastUpdateTime) <= MS2US(INAV_GPS_TIMEOUT_MS))
   ```
   This fails because `lastUpdateTime` is stale (>1.5s old)
5. **`EST_GPS_XY_VALID` not set** → GPS corrections not applied
6. **EPH grows** → Eventually exceeds `max_eph_epv`
7. **Position becomes invalid** → `updateActualHorizontalPositionAndVelocity(false, false, ...)` called
8. **`estPosStatus = EST_NONE`** → Position estimate marked invalid

### The Cascade to Zero Distance (KEY FINDING)

From breadoven's comment: "home position is being constantly reset which is the only thing in the code that sets home distance to 0"

The cascade during RTH:
1. Position estimate becomes invalid (`EST_NONE`)
2. `homeDistance` is calculated from degraded position estimate
3. **If RTH is active and `homeDistance < min_rth_distance`** (navigation.c:1527):
   ```c
   if (posControl.homeDistance < navConfig()->general.min_rth_distance) {
       setHomePosition(&navGetCurrentActualPositionAndVelocity()->pos, ...);
       return NAV_FSM_EVENT_SWITCH_TO_RTH_LANDING;
   }
   ```
4. `setHomePosition()` sets `homeDistance = 0` at line 3227
5. **Drone thinks it's at home and starts landing!**

This explains issue #10893's symptom: "Drone behaves as if already at home point, initiating landing sequence"

### The Fix (commit 843f29d93)

Moves `posEstimator.gps.lastUpdateTime = currentTimeUs;` outside the `if (!isFirstGPSUpdate)` block, ensuring it's updated on EVERY valid GPS reading including the first one after recovery.

```diff
-                /* Indicate a last valid reading of Pos/Vel */
-                posEstimator.gps.lastUpdateTime = currentTimeUs;
             }

+            /* Indicate a last valid reading of Pos/Vel - must be updated even on
+             * first GPS reading after recovery to prevent position estimate from
+             * timing out and getting stuck at zero (fixes issue #11049) */
+            posEstimator.gps.lastUpdateTime = currentTimeUs;
```

## Test Scripts

Created `gps_rth_bug_test.py` in `test_tools/` that:
1. Arms the FC
2. Flies away from home (>100m)
3. Activates RTH mode
4. Simulates GPS loss for 5 seconds
5. Simulates GPS recovery
6. Monitors if homeDistance incorrectly becomes 0

## Key Code Locations

- **Bug location**: `navigation_pos_estimator.c:261` (line 261 in buggy version)
- **Timeout check**: `navigation_pos_estimator.c:482` in `calculateCurrentValidityFlags()`
- **Zero distance trigger**: `navigation.c:1527-1531` - RTH "close to home" logic
- **homeDistance = 0**: `navigation.c:3227` in `setHomePosition()`

## Related Issues

- **#11049**: Original bug report - distance/altitude stuck at zero after GPS recovery
- **#10893**: Related - home point lost after GPS failure, drone starts landing
- **#11144**: The fix PR (merged)

## Commits

- **Buggy:** 579daf118 (parent of fix)
- **Fixed:** 843f29d93 (the fix commit)

## GitHub Response Status

**FINAL UPDATE 2025-11-30**: Comprehensive SITL Testing Complete - Bug Does NOT Reproduce

### Final Test Results

After extensive testing with RTH mode active and various GPS loss durations:

| Version | Commit | RTH Mode | GPS Loss | Distance Before | Distance After | Result |
|---------|--------|----------|----------|-----------------|----------------|--------|
| Buggy | 579daf118 | Yes | 3s | 101m | 120m | PASS |
| Buggy | 579daf118 | Yes | 10s | 101m | 120m | PASS |
| Buggy | 579daf118 | No | 5s | 101m | 120m | PASS |
| Fixed | 843f29d93 | No | 5s | 101m | 120m | PASS |

**All tests pass - distance to home recovers correctly even with RTH mode active and extended GPS loss.**

### Test Configuration
- Travel speed: 0.7 degrees/hour = 39 INAV units per 50Hz update = ~21.6 m/s
- GPS loss durations: 3s, 5s, 10s tested
- Flight distance: ~100m from home before GPS loss
- HITL mode enabled for sensor bypass
- RTH mode on AUX2 (BOXNAVRTH = 8)

### Key Finding

**The bug does NOT reproduce in SITL testing** despite:
- RTH mode being active (required for the cascade to zero distance)
- 10 seconds GPS loss (well over the 1.5s timeout threshold)
- Using the exact buggy commit (579daf118)

### Why the Bug May Not Reproduce in SITL

1. **MSP GPS bypasses EPH/EPV handling**: MSP_SET_RAW_GPS doesn't send EPH/EPV values, so the position estimator may use default/ideal values
2. **HITL mode affects timing**: HITL mode may process sensor data synchronously
3. **Position estimator behavior**: SITL may maintain tighter position estimates
4. **No real IMU drift**: Without real accelerometer/gyro noise, position estimate stays stable during GPS loss
5. **Instant GPS recovery**: Our test sends GPS fixes at 50Hz - real GPS may have inconsistent fix quality on recovery

### Why the Fix is Still Valid

The code analysis clearly shows the bug mechanism:
1. `lastUpdateTime` is inside `if (!isFirstGPSUpdate)` block - not updated on first recovery reading
2. This causes `EST_GPS_XY_VALID` to fail the timeout check for one cycle
3. If `gps.eph` (also in the block) is high from GPS loss, GPS corrections are delayed
4. This can cascade to position estimate degradation in specific conditions

The fix correctly moves `lastUpdateTime` update outside the conditional block.

### Conclusion

- **Code analysis supports the fix** - bug mechanism is clearly visible in source code
- **SITL testing cannot reproduce** - likely due to MSP GPS and HITL mode differences
- **Real hardware testing needed** - to reproduce the bug conditions
- **The fix is correct** - prevents the one-cycle delay in lastUpdateTime update

## Previous Session Notes

### Script Versions
Located in `test_tools/`:
- `gps_test_v1.py` - raw socket, no arm, no distance query
- `gps_test_v2.py` - raw socket, queries distance but no arm
- `gps_test_v3.py` - uNAVlib, no arm (misleading results)
- `gps_test_v4.py` - uNAVlib, arms, flies away
- `gps_test_v5.py` - uNAVlib, proper SITL restart handling
- `gps_test_v6.py` - **FINAL** Main-thread RC/GPS, 0.7 deg/hour, works correctly
- `gps_rth_bug_test.py` - RTH-specific bug reproduction test

### Technical Details

**HITL Mode** (`MSP_SIMULATOR = 0x201F`):
- Version: 2
- Flags: `HITL_ENABLE = (1 << 0)`
- Bypasses sensor calibration requirements

**METERS_PER_UNIT**: 0.0111 (1 INAV unit = 1e-7 degrees ≈ 0.0111m at mid-latitudes)

**INAV_GPS_TIMEOUT_MS**: 1500ms (1.5 seconds)

### Build Notes

When building older commits with gcc-12+:
```bash
cmake -DSITL=ON -DCMAKE_C_COMPILER=gcc-11 -DCMAKE_CXX_COMPILER=g++-11 ..
```
