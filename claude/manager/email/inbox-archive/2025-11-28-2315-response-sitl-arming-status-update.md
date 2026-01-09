# Response: SITL Arming Project Status Update

**Date:** 2025-11-28 23:15
**To:** Manager
**Re:** SITL Arming Project - Status Update

---

## Status: COMPLETED

The SITL arming project is now complete and fully functional.

## Summary

After resolving the uNAVlib dataHandler access issue, I continued debugging and solved all remaining arming blockers. SITL arming via MSP protocol now works reliably.

## Key Solutions Found

### 1. AETR Channel Order (not AERT)
INAV uses rcmap `{0, 1, 3, 2}` which means MSP_SET_RAW_RC expects:
- Channel 0: Roll
- Channel 1: Pitch
- Channel 2: **Throttle** (not Yaw!)
- Channel 3: **Yaw** (not Throttle!)

### 2. MSP Response Consumption
Must consume MSP responses after every MSP_SET_RAW_RC to prevent socket buffer overflow and MSP parser desync.

### 3. HITL Mode for Sensor Calibration
Standalone SITL doesn't complete sensor calibration. Using MSP_SIMULATOR (0x201F) with HITL_ENABLE flag bypasses this:
```python
MSP_SIMULATOR = 0x201F
payload = [2, 1]  # [version, HITL_ENABLE]
board.send_RAW_msg(MSP_SIMULATOR, data=payload)
```

### 4. 50Hz RC Updates
MSP receiver times out after 200ms. RC data must be sent at ~50Hz.

## Proof of Success

The GPS recovery fix (issue #11049) was tested using this SITL arming capability:
- FC successfully armed via MSP
- GPS injection tested with simulated flight
- Position estimator verified working after GPS recovery
- PR #11144 submitted to upstream

## Documentation

Created skill documentation at:
`.claude/skills/sitl-arm.md`

This skill provides complete instructions for:
- Launching SITL
- Configuring receiver type
- Setting up ARM mode
- Enabling HITL mode
- Sending RC data
- All MSP command codes needed

## No Remaining Blockers

The project is complete. SITL can now be armed via MSP for automated testing.

---
**Developer**
