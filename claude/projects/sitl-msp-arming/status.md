# SITL MSP Arming Project

## Status: IN PROGRESS - RC_LINK fixed, fixing channel order and remaining blockers

## Objective
Enable arming of INAV SITL via MSP protocol to support automated testing (specifically GPS recovery testing for issue #11049).

## Background
- SITL is the Software-In-The-Loop simulator for INAV
- GPS recovery test requires arming the FC to set home position
- MSP (MultiWii Serial Protocol) is used for flight controller communication
- uNAVlib Python library provides MSP interface

## Recent Progress (2025-11-28)

### Session 2: RC_LINK RESOLVED, Channel Order Fix In Progress

#### Issue 1: MSP Response Buffer Overflow - FIXED
**Problem**: MSP_SET_RAW_RC was being sent but RC link never established. MSP_RC queries returned "No data".

**Root cause**: MSP_SET_RAW_RC sends an acknowledgment response (code 200) that wasn't being consumed. This caused the socket receive buffer to fill up with unconsumed responses, desynchronizing the MSP parser.

**Fix applied**: Added `board.receive_msg()` calls after each `send_RAW_msg()`:
```python
def send_rc(board, ...):
    board.send_RAW_msg(MSP_SET_RAW_RC, data=data)
    # CRITICAL: Consume the acknowledgment response
    try:
        dataHandler = board.receive_msg()
        if dataHandler:
            board.process_recv_data(dataHandler)
    except:
        pass
```

**Result**: RC_LINK blocker now CLEARED! MSP_RC returns valid data.

#### Issue 2: Channel Order Wrong - FIX IN PROGRESS
**Problem**: After RC_LINK was fixed, new blockers appeared: THROTTLE and ARM_SWITCH. MSP_RC showed channels in wrong positions.

**Root cause**: INAV uses rcmap `{0, 1, 3, 2}` (AETR order) by default:
- Raw channel 0 → Logical Roll
- Raw channel 1 → Logical Pitch
- Raw channel 2 → Logical **Throttle** (NOT Yaw!)
- Raw channel 3 → Logical **Yaw** (NOT Throttle!)

The test script was sending in AERT order (logical), but MSP_SET_RAW_RC expects AETR (raw).

**Fix applied**: Changed channel order in `send_rc()` and `_send_loop()`:
```python
# OLD (wrong): channels = [roll, pitch, yaw, throttle, aux1, ...]
# NEW (correct): channels = [roll, pitch, throttle, yaw, aux1, ...]
```

### Session 1: uNAVlib Issue RESOLVED
The suspected uNAVlib library bug was actually a bug in sitl_arm_test.py.

**Root cause**: The test script accessed `dataHandler` as an object (using `dataHandler.data`) when it's actually a dict (should use `dataHandler['dataView']`).

**Fix applied**: Changed all occurrences to use proper dict access:
```python
data = dataHandler.get('dataView', []) if dataHandler else []
```

**Result**: MSP_RX_CONFIG now correctly returns 24 bytes, receiver type setting persists after reboot.

## Test Script
**Location:** `claude/developer/test_tools/sitl_arm_test.py`

The script performs:
1. Connects to SITL via TCP on port 5761
2. Sets receiver type to MSP (RX_TYPE_MSP = 2)
3. Configures ARM mode activation on AUX1 (channel 5) for range 1700-2100
4. Saves config and reboots FC
5. Reconnects and sends RC + GPS data
6. Attempts to arm with AUX1 high

## Current Blockers
After fixing RC_LINK and channel order, remaining blockers are:

```
armingDisableFlags: 0x00086200 (after RC_LINK fix, before channel order fix)
- ARMING_DISABLED_SENSORS_CALIBRATING (bit 9 = 0x200)
- ARMING_DISABLED_ACCELEROMETER_NOT_CALIBRATED (bit 13 = 0x2000)
- ARMING_DISABLED_ARM_SWITCH (bit 14 = 0x4000) - should clear with correct channel order
- ARMING_DISABLED_THROTTLE (bit 19 = 0x80000) - should clear with correct channel order
```

### Blocker Analysis

#### 1. ARMING_DISABLED_RC_LINK (bit 18 = 0x40000) - RESOLVED ✓
**Solution**: Consume MSP acknowledgment responses after each send to prevent buffer overflow.

#### 2. ARMING_DISABLED_THROTTLE (bit 19) - FIXING
**Cause**: Channel order was wrong. Yaw value (1500) was being sent in throttle position instead of throttle value (1000).
**Solution**: Use AETR raw channel order: `[roll, pitch, throttle, yaw, aux1...]`

#### 3. ARMING_DISABLED_ARM_SWITCH (bit 14) - FIXING
**Cause**: AUX1 value not reaching mode activation range due to channel order issues.
**Solution**: Same channel order fix should resolve this.

#### 4. ARMING_DISABLED_SENSORS_CALIBRATING (bit 9 = 0x200)
- SITL sensors may need time to calibrate after boot
- MSP_ACC_CALIBRATION (code 205) is called but may not work in SITL
- This flag clears when gyro/acc calibration completes

#### 5. ARMING_DISABLED_ACCELEROMETER_NOT_CALIBRATED (bit 13 = 0x2000)
- Related to sensor calibration
- ACC calibration may not take effect in SITL environment
- May need to investigate SITL-specific calibration handling

## Key Technical Details

### MSP Commands Used
| Code | Name | Purpose |
|------|------|---------|
| 44 | MSP_RX_CONFIG | Read receiver config |
| 45 | MSP_SET_RX_CONFIG | Set receiver type to MSP (2) |
| 68 | MSP_REBOOT | Reboot FC |
| 105 | MSP_RC | Read RC channel values |
| 150 | MSP_STATUS_EX | Query arming flags (16-bit) |
| 200 | MSP_SET_RAW_RC | Send RC channel values |
| 201 | MSP_SET_RAW_GPS | Inject GPS data |
| 205 | MSP_ACC_CALIBRATION | Calibrate accelerometer |
| 250 | MSP_EEPROM_WRITE | Save config |
| 0x2000 | MSP2_INAV_STATUS | Query full status including 32-bit arming flags |

### Receiver Types (from rx.h)
- RX_TYPE_NONE = 0
- RX_TYPE_SERIAL = 1
- RX_TYPE_MSP = 2
- RX_TYPE_SIM = 3 (alternative to try)

### Arming Flags (from runtime_config.h)
- ARMED = 1 << 2
- ARMING_DISABLED_SENSORS_CALIBRATING = 1 << 9
- ARMING_DISABLED_ACCELEROMETER_NOT_CALIBRATED = 1 << 13
- ARMING_DISABLED_RC_LINK = 1 << 18

### RC Channel Layout

**IMPORTANT**: There are two channel orderings in INAV:

1. **Logical channels** (what INAV uses internally, what MSP_RC returns):
   - Channel 0: Roll
   - Channel 1: Pitch
   - Channel 2: Yaw
   - Channel 3: Throttle
   - Channel 4: AUX1 (used for ARM mode)
   - Channels 5-15: AUX2-AUX12

2. **Raw channels** (what MSP_SET_RAW_RC expects, based on rcmap):
   - Default rcmap = `{0, 1, 3, 2}` (AETR)
   - Raw 0 → Logical Roll
   - Raw 1 → Logical Pitch
   - Raw 2 → Logical **Throttle** (NOT Yaw!)
   - Raw 3 → Logical **Yaw** (NOT Throttle!)
   - Raw 4+ → AUX channels (no remapping)

**For MSP_SET_RAW_RC, send in AETR order**: `[Roll, Pitch, Throttle, Yaw, AUX1, ...]`

### RC Values Used in Test
- RC_LOW = 1000
- RC_MID = 1500
- RC_HIGH = 2000
- ARM mode configured for AUX1 range 1700-2100

## Files Modified/Created

- `claude/developer/test_tools/sitl_arm_test.py` - Main test script (fixed dataHandler access)
- `claude/developer/test_tools/msp_debug.py` - Raw MSP protocol test tool
- `claude/developer/test_tools/unavlib_bug_test.py` - Library test script
- `cmake/sitl.cmake` - Removed `--no-warn-rwx-segments` linker flag

## Dependencies

- uNAVlib: `pip3 install git+https://github.com/xznhj8129/uNAVlib`
  - Python MSP library for flight controller communication

## Commands

```bash
# Start SITL (from inav/build directory)
cd inav/build
rm -f eeprom.bin
./bin/SITL.elf > /tmp/sitl.log 2>&1 &

# Run test
python3 claude/developer/test_tools/sitl_arm_test.py 5761

# Check SITL log for errors
cat /tmp/sitl.log
```

## Related Projects
- fix-gps-recovery-issue-11049 - This arming work is prerequisite for GPS recovery testing

## Investigation Plan for Next Session

### Priority 1: Fix ARMING_DISABLED_RC_LINK
1. **Check RC timeout behavior**
   - Look at `src/main/rx/rx.c` for `rxDataProcessingRequired` and `rxSignalReceived`
   - Determine how often MSP_SET_RAW_RC must be sent to maintain link
   - Current test sends RC data every 100ms during arm loop - may need faster rate

2. **Verify MSP RC processing**
   - Check `src/main/rx/msp.c` - `rxMspFrameReceive()`
   - Ensure MSP receiver is properly initialized for SITL
   - Look for any SITL-specific RX initialization

3. **Test continuous RC transmission**
   - Modify test to send MSP_SET_RAW_RC in a tighter loop (every 20ms)
   - Start sending RC data BEFORE checking arming status

### Priority 2: Fix Sensor Calibration Issues
1. **Check SITL gyro/acc simulation**
   - Look at `src/main/target/SITL/` for sensor simulation
   - Check if calibration is auto-completed or needs specific handling

2. **Alternative: Skip calibration checks**
   - Some SITL configurations may skip calibration
   - Check for `SIMULATOR` or `SITL` specific code paths

### Priority 3: Alternative Approaches
1. **Try RX_TYPE_SIM (3) instead of RX_TYPE_MSP (2)**
   - SITL may have better support for simulation receiver
   - Look at `src/main/rx/sim.c` if it exists

2. **Check SITL command line options**
   - SITL may have flags to pre-arm or skip checks
   - Look at `src/main/target/SITL/main.c`

## Test Output Reference (Last Run)

```
Connected! FC: INAV
API Version: 2.5.0
Initial arming flags: 0x00042200
  - ARMING_DISABLED_SENSORS_CALIBRATING
  - ARMING_DISABLED_ACCELEROMETER_NOT_CALIBRATED
  - ARMING_DISABLED_RC_LINK

[Step 1] Setting receiver type to MSP...
  Current RX config length: 24 bytes
  Current receiver type: 0
  Setting receiver type to MSP (2)

[Step 3] Reconnecting to FC after reboot...
  Receiver type after reboot: 2 (MSP)  <-- GOOD: Setting persists

[Step 4] Establishing RC link (sending RC + GPS data)...
  RC link should be established
  [DEBUG] MSP_RC: No data (packet_error=0)  <-- PROBLEM: RC not registering

[Step 6] Attempting to arm (AUX1 high, throttle low)...
  t=5.0s: Not armed (0x00042200). Blockers: [SENSORS_CALIBRATING, ACCELEROMETER_NOT_CALIBRATED, RC_LINK]

FAILED: FC did not arm
```
