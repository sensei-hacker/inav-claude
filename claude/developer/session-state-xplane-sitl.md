# X-Plane SITL Testing Session State

**Date:** 2025-12-23
**Goal:** Test issue #9912 (autotrim) using X-Plane HITL with INAV SITL

## Current Status

### What's Working
1. **SITL running** in background (task b617f74) on ports 5760 and 5761
2. **Virtual joystick daemon** - successfully sends axis data to X-Plane
3. **X-Plane calibrated** with "INAV Virtual Joystick" selected
4. **RC daemon created** (`rc_daemon.py`, `rc_cmd.sh`) - sends RC directly via MSP
5. **MSP communication working** on port 5760 (verified FC_VARIANT, STATUS_EX)
6. **Autotrim enabled in HITL mode** - commented out the early return in `servos.c:687-692`

### Current Configuration
- SITL ports: 5760 (UART1), 5761 (UART2)
- RC daemon: Not running (was stopped)
- HITL plugin: Disconnected
- X-Plane: Running with NK FPVSurfwing aircraft

### Key Files Created/Modified
- `inav/build_sitl/xplane_scripts/rc_daemon.py` - MSP RC sender daemon
- `inav/build_sitl/xplane_scripts/rc_cmd.sh` - Safe wrapper script
- `inav/build_sitl/xplane_scripts/joystick_daemon.py` - Virtual joystick (evdev/uinput)
- `inav/build_sitl/xplane_scripts/joystick_cmd.sh` - Safe wrapper for joystick
- `inav/build_sitl/xplane_scripts/FIFO_NOTES.md` - FIFO blocking documentation
- `inav/src/main/flight/servos.c` - Autotrim HITL check commented out (lines 687-692)
- `claude/developer/docs/testing/xplane-sitl-testing.md` - Comprehensive testing guide

## Next Steps to Resume

1. **Start RC daemon:**
   ```bash
   cd inav/build_sitl/xplane_scripts
   ./rc_cmd.sh start 5760
   ```

2. **Reconnect HITL plugin in X-Plane:**
   - Plugins → INAV HITL → Link → Connect to Flight Controller

3. **Monitor status via port 5761:**
   ```python
   from mspapi2 import MSPApi, InavMSP
   with MSPApi(tcp_endpoint='localhost:5761') as api:
       info, status = api._request(InavMSP.MSP_STATUS_EX)
       print(f"Arming flags: {status.get('armingFlags')}")
   ```

4. **Arm the aircraft:**
   ```bash
   ./rc_cmd.sh arm
   ```

5. **Take off and test autotrim:**
   ```bash
   ./rc_cmd.sh takeoff
   ```

6. **During flight, monitor servo midpoints** to detect autotrim changes during turns

## Important Reminders

### CRITICAL - Blocking I/O Hazards
- **NEVER** write to FIFO without checking daemon is running
- **NEVER** use `jstest` or read from `/dev/input/*` devices
- **NEVER** send CLI commands (`#`) via netcat - locks port in CLI mode
- **ALWAYS** use wrapper scripts (`rc_cmd.sh`, `joystick_cmd.sh`)

### Before Killing SITL
1. Disconnect HITL plugin first (Plugins → INAV HITL → Disable)
2. Wait for disconnect
3. Then safe to kill SITL

### Port Allocation
| Port | UART | Intended Use |
|------|------|--------------|
| 5760 | UART1 | RC daemon (MSP_SET_RAW_RC) |
| 5761 | UART2 | HITL plugin OR monitoring |

## Issue Being Tested

**GitHub Issue #9912** - Autotrim bug where servo midpoints incorrectly change during banked turns.

**Test procedure:**
1. Fly level for 30+ seconds, note servo midpoints
2. Perform 30° bank turn for 15+ seconds
3. Level off, compare servo midpoints
4. Bug present if midpoints changed during turn

## Background Task

SITL is running as background task `b617f74`. Check output:
```bash
cat /tmp/claude/-home-raymorris-Documents-planes-inavflight/tasks/b617f74.output
```
