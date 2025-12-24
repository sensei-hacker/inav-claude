# X-Plane SITL Testing

Test INAV firmware with X-Plane 12's realistic physics simulation for reproducing flight-related bugs.

## Quick Start

### Prerequisites Check

1. X-Plane 12 (or X-Plane 11 demo) installed
2. INAV-X-Plane-HITL plugin installed
3. FlyWithLua NG+ with SlewMode (for mid-air start)

### Start Testing Session

1. **Start SITL:**
   ```bash
   cd inav/build_sitl
   ./bin/SITL.elf
   ```

2. **Launch X-Plane 12:**
   - Select INAV Surfwing aircraft
   - Choose location/airport

3. **Connect plugin:**
   - Plugins → INAV HITL → Link → Connect to Flight Controller

4. **Position aircraft (optional):**
   - Enable slew mode: `flightwusel/SlewMode/Toggle`
   - Position at desired altitude
   - Disable slew mode

5. **Monitor via mspapi2:**
   ```python
   from mspapi2 import MSPApi
   with MSPApi(tcp_endpoint="localhost:5760") as api:
       info, status = api.get_inav_status()
       print(status)
   ```

## Starting Mid-Air

X-Plane doesn't have built-in mid-air start. Options:

1. **Slew Mode Plugin** (recommended):
   - Install FlyWithLua NG+ for X-Plane 12
   - Install SlewMode plugin from GitHub
   - Toggle with `flightwusel/SlewMode/Toggle`

2. **Save/Load Situation:**
   - Fly to altitude, File → Save Situation
   - Load situation to resume at that position

3. **Final Approach:**
   - Select 3NM or 10NM final approach from airport menu

## Configuration

### SITL Command Line (Alternative to HITL plugin)

```bash
./bin/SITL.elf --sim=xp \
    --simip=127.0.0.1 \
    --simport=49000 \
    --chanmap=M01-01,S01-03,S03-02,S04-04
```

### X-Plane Settings

- Settings → General → Flight models per frame: **10**
- Settings → Network → Accept incoming connections: **Enabled**
- Note UDP port (default 49000)

### Joystick Mapping

| INAV | X-Plane |
|------|---------|
| Roll | Roll |
| Pitch | Pitch |
| Throttle | Cowl Flap 1 |
| Yaw | Yaw |
| AUX1-4 | Cowl Flap 2-5 |

## X-Plane REST API

Available at `http://localhost:8086/api/v2/` (X-Plane 12.1.1+):

```python
import requests

# Read aircraft position
r = requests.get('http://localhost:8086/api/v2/datarefs/sim/flightmodel/position/latitude')

# Set control surface
requests.put('http://localhost:8086/api/v2/datarefs/sim/cockpit2/controls/yoke_roll_ratio',
             json={'value': 0.5})
```

## Critical: Stopping SITL Safely

**IMPORTANT:** Killing SITL while the HITL plugin is connected will freeze X-Plane!

**Before killing/restarting SITL:**
1. In X-Plane: **Plugins → INAV-X-Plane-HITL → Disable**
2. Wait for plugin to disconnect
3. Now safe to kill SITL
4. After SITL restarts, re-enable the plugin

Helper script: `inav/build_sitl/disconnect_xplane_hitl.py`

## Virtual Joystick Daemon

For automated testing without a physical joystick, use the virtual joystick daemon.

**IMPORTANT:** Always use the safe wrapper script to prevent lockups from FIFO blocking.

### Safe Wrapper Script

Location: `inav/build_sitl/xplane_scripts/joystick_cmd.sh`

```bash
# Start daemon
./joystick_cmd.sh start

# Check status (verify running before sending commands!)
./joystick_cmd.sh status

# Send commands safely (includes timeout protection)
./joystick_cmd.sh calibrate    # Full axis sweep for X-Plane calibration
./joystick_cmd.sh center       # Center all sticks
./joystick_cmd.sh axis 0 16000 # Set roll axis
./joystick_cmd.sh axis 2 -32768  # Throttle min
./joystick_cmd.sh axis 4 32767   # AUX1 (arm) high

# Stop daemon
./joystick_cmd.sh stop
```

### Axis Mapping

| Axis | Function | Range |
|------|----------|-------|
| 0 | Roll | -32768 to 32767 |
| 1 | Pitch | -32768 to 32767 |
| 2 | Throttle | -32768 to 32767 |
| 3 | Yaw | -32768 to 32767 |
| 4 | AUX1 (ARM) | -32768 to 32767 |
| 5 | AUX2 | -32768 to 32767 |

### FIFO Safety Warning

**NEVER** write directly to `/tmp/inav_joystick_cmd` - this can block forever!
- If daemon isn't running, writes block indefinitely
- If FIFO was deleted while daemon runs, daemon can't receive commands
- Always use `joystick_cmd.sh` which checks state and uses timeout

See `inav/build_sitl/xplane_scripts/FIFO_NOTES.md` for detailed lockup prevention.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| X-Plane frozen | Killed SITL without disconnecting HITL - must restart X-Plane |
| No connection | Check UDP port 49000, firewall |
| No RC input | Verify joystick calibration in X-Plane |
| Sensors not working | Set sensor types to "FAKE" in Configurator |
| Aircraft unresponsive | Check channel mapping, ARM switch |
| SITL in FAILSAFE | HITL plugin needs joystick for RC input (see MSP RX workaround) |
| Joystick command hangs | Use `joystick_cmd.sh` wrapper, never write to FIFO directly |
| Virtual joystick not seen | Run `./joystick_cmd.sh start`, check status before calibrating |

## Full Documentation

See: `claude/developer/docs/testing/xplane-sitl-testing.md`

## Related Skills

- **build-sitl** - Build SITL firmware
- **msp-protocol** - MSP communication with SITL
- **sitl-arm** - Arm SITL for testing

## Resources

- [INAV-X-Plane-HITL Plugin](https://github.com/RomanLut/INAV-X-Plane-HITL)
- [X-Plane Web API](https://developer.x-plane.com/article/x-plane-web-api/)
- [SlewMode Plugin](https://github.com/jonaseberle/xplane-plugin-SlewMode)
