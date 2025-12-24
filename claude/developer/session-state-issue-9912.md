# Session State: Issue #9912 Reproduction

**Date:** 2025-12-23
**Task:** Reproduce issue #9912 - Continuous Auto Trim active during maneuvers

## Current Status

Attempting to reproduce the bug using SITL but encountering configuration challenges.

## What's Been Done

1. **SITL Built:** `inav/build_sitl/` - working binary at `bin/SITL.elf`
   - Fixed linker issue by commenting out `--no-warn-rwx-segments` in `cmake/sitl.cmake` lines 67-70

2. **SITL Configured:**
   - FW_AUTOTRIM feature: ENABLED
   - Platform type: AIRPLANE
   - GPS: DISABLED (was causing hardware failure)
   - Servo mixer: smix 0 2 0 100 0 (servo 2 = roll), smix 1 3 1 100 0 (servo 3 = pitch)
   - Motor mixer: mmix 0 1.0 0.0 0.0 0.0
   - Aux mode: aux 0 0 0 1700 2100 (ARM on aux1 >1700)
   - Config saved to eeprom.bin

3. **Test Scripts Created:**
   - `build_sitl/test_autotrim_issue_9912.py` - custom MSP implementation (buggy)
   - `build_sitl/test_autotrim_mspapi2.py` - using mspapi2 library (better)

4. **Key Discovery:** Should use **mspapi2** library for MSP communication
   - TCP support: `MSPApi(tcp_endpoint="localhost:5760")`
   - Has `set_simulator()` and `set_rc_channels()` methods
   - Servo config via: `api._request(InavMSP.MSP_SERVO_CONFIGURATIONS)`

## Current Blockers

The aircraft won't arm. Current arming flags show:
- `ARMING_DISABLED_RC_LINK` (262144)
- `ARMING_DISABLED_INVALID_SETTING` (67108864)

Need to:
1. Fix RC_LINK issue (MSP RC data not being accepted properly)
2. Fix INVALID_SETTING (check CLI for invalid settings)

## mspapi2 Usage Examples

```python
from mspapi2 import MSPApi, InavMSP

with MSPApi(tcp_endpoint="localhost:5760") as api:
    # Get status
    info, status = api.get_inav_status()
    print(status['armingFlags'])

    # Send simulator data
    api.set_simulator(roll=0, pitch=0, yaw=0, acc=(0,0,1.0), gyro=(0,0,0))

    # Send RC channels
    api.set_rc_channels([1500, 1500, 1000, 1500, 2000, 1500, 1500, 1500])

    # Get servo midpoints
    info, servos = api._request(InavMSP.MSP_SERVO_CONFIGURATIONS)
    midpoints = [s['middle'] for s in servos]
```

## Bug Analysis (from code review)

**Root Cause Identified:** In `src/main/flight/servos.c:processContinuousServoAutotrim()`:
- The code checks I-term magnitude (>5) but NOT I-term stability
- During maneuver transitions, transient I-term gets incorrectly transferred to servo trim
- Missing check for rate-of-change of I-term before applying trim

**Relevant Code:** `src/main/flight/servos.c` lines 615-685

## Next Steps

1. Fix arming issues:
   - Check `set receiver_type = MSP` in CLI
   - Verify aux mode configuration
   - Check for invalid settings

2. Once armed, run test:
   - Level flight for 10 seconds (autotrim should stabilize)
   - 30° banked turn for 15+ seconds
   - Level off and check if servo midpoints changed incorrectly

3. Document results

## Files Modified

- `inav/cmake/sitl.cmake` - commented out linker flag
- `inav/build_sitl/test_autotrim_issue_9912.py` - test script
- `inav/build_sitl/test_autotrim_mspapi2.py` - mspapi2 test script
- `claude/developer/reports/issue-9912-autotrim-analysis.md` - code analysis

## SITL Running

Background task: b3a0a31
Output: `/tmp/claude/-home-raymorris-Documents-planes-inavflight/tasks/b3a0a31.output`
