# X-Plane 12 SITL Testing Guide

Guide for testing INAV firmware bugs using X-Plane 12's realistic physics simulation.

## Overview

X-Plane 12 provides physically accurate flight simulation, making it ideal for reproducing flight-related bugs like autotrim issues, navigation problems, and servo behavior during maneuvers.

**Why X-Plane over MSP Injection:**
- Realistic aerodynamics and physics
- Proper sensor data (IMU, GPS, baro, mag)
- Accurate flight dynamics during turns/maneuvers
- Visual feedback of aircraft behavior

## Prerequisites

**Note:** X-Plane 12 can take 2-3 minutes to fully start up and load scenery.

### Software Required
1. **X-Plane 12** (or X-Plane 11 demo for basic testing)
   - X-Plane 11 demo: https://www.x-plane.com/desktop/try-it/older/ (15-minute sessions)
   - X-Plane 12: https://www.x-plane.com/

2. **INAV SITL** - Built from source with simulator support

3. **INAV-X-Plane-HITL Plugin** (recommended)
   - https://github.com/RomanLut/INAV-X-Plane-HITL
   - Includes NK FPV Surfwing aircraft model

4. **FlyWithLua NG+** (optional, for slew mode)
   - For X-Plane 12: FlyWithLua NG+
   - Enables mid-air positioning

## Installation

### 1. Install INAV-X-Plane-HITL Plugin

```bash
# Download latest release from GitHub
# Extract Aircraft.zip to X-Plane installation directory
# Remove old installation first:
rm -rf "X-Plane 12/Aircraft/Extra Aircraft/NK_FPVSurfwing/"
```

### 2. Build INAV SITL

```bash
cd inav
mkdir -p build_sitl
cd build_sitl
cmake -DSITL=ON ..
make -j4
```

### 3. Configure X-Plane

In X-Plane Settings:
- **Settings → General → Flight models per frame**: Set to **10**
- **Settings → Network**: Enable "Accept incoming connections"
- Note the UDP port under "Port we receive on" (default: 49000)

## Starting a Test Flight

### Method 1: HITL Plugin (Recommended)

1. **Start SITL in configurator-only mode:**
   ```bash
   cd inav/build_sitl
   ./bin/SITL.elf
   ```

2. **Launch X-Plane 12**
   - Select "INAV Surfwing" aircraft
   - Choose any airport/location

3. **Connect the plugin:**
   - Menu: Plugins → INAV HITL → Link → Connect to Flight Controller
   - Plugin auto-detects serial port (TCP localhost:5760)

4. **For mid-air start (Slew Mode):**
   - Install FlyWithLua NG+ and SlewMode plugin
   - Use `flightwusel/SlewMode/Toggle` command
   - Position aircraft at desired altitude
   - Disable slew mode to begin normal flight

### Method 2: Direct SITL Connection

```bash
# Start SITL with X-Plane interface
./bin/SITL.elf --sim=xp --simip=127.0.0.1 --simport=49000 \
    --chanmap=M01-01,S01-03,S03-02,S04-04
```

## X-Plane REST API (Advanced)

X-Plane 12.1.1+ includes a REST API at `http://localhost:8086/api/v2/`:

```python
import requests

# Read dataref
r = requests.get('http://localhost:8086/api/v2/datarefs/sim/flightmodel/position/latitude')
lat = r.json()['value']

# Write dataref
requests.put('http://localhost:8086/api/v2/datarefs/sim/cockpit2/controls/flap_ratio',
             json={'value': 0.5})
```

**Useful datarefs:**
- `sim/flightmodel/position/latitude` - Aircraft latitude
- `sim/flightmodel/position/longitude` - Aircraft longitude
- `sim/flightmodel/position/elevation` - Altitude (meters)
- `sim/flightmodel/position/true_phi` - Roll (degrees)
- `sim/flightmodel/position/true_theta` - Pitch (degrees)
- `sim/flightmodel/position/true_psi` - Yaw/Heading (degrees)

## Testing Issue #9912 (Autotrim Example)

### CRITICAL: HITL Mode Cannot Test Autotrim

**Autotrim is DISABLED in HITL mode!** The HITL plugin sets `SIMULATOR_MODE_HITL` flag which
causes the autotrim code to return early without running (`servos.c:689`).

**You MUST use native X-Plane mode** (`--sim=xp`) instead of the HITL plugin to test autotrim.
Native mode sets `SIMULATOR_MODE_SITL` which does NOT disable autotrim.

**Requirements for native mode:**
- Physical joystick connected to X-Plane
- Joystick axes mapped to cowl flaps (see channel mapping below)
- Start SITL with: `./bin/SITL.elf --sim=xp --simip=127.0.0.1 --simport=49000`
- DO NOT enable the HITL plugin

### Test Procedure

1. **Configure INAV:**
   - Platform: AIRPLANE
   - Enable feature: FW_AUTOTRIM
   - Servo mixer: Standard airplane config

2. **Establish baseline:**
   - Fly level for 30+ seconds
   - Note servo midpoints (via Configurator or MSP)
   - Autotrim should stabilize

3. **Perform banked turn:**
   - Execute 30° bank turn for 15+ seconds
   - Continue turning (180°+ total)

4. **Check results:**
   - Level off quickly
   - Compare servo midpoints to baseline
   - Bug present if midpoints changed during turn

### Monitoring Script

```python
#!/usr/bin/env python3
"""Monitor servo midpoints during X-Plane flight."""
from mspapi2 import MSPApi, InavMSP
import time

with MSPApi(tcp_endpoint="localhost:5760") as api:
    while True:
        info, servos = api._request(InavMSP.MSP_SERVO_CONFIGURATIONS)
        midpoints = [s['middle'] for s in servos[:4]]
        print(f"Servo midpoints: {midpoints}")
        time.sleep(1)
```

## Joystick Channel Mapping

| INAV Channel | X-Plane Axis |
|--------------|--------------|
| Roll         | Roll         |
| Pitch        | Pitch        |
| Throttle     | Cowl Flap 1  |
| Yaw          | Yaw          |
| AUX1 (CH5)   | Cowl Flap 2  |
| AUX2 (CH6)   | Cowl Flap 3  |
| AUX3 (CH7)   | Cowl Flap 4  |
| AUX4 (CH8)   | Cowl Flap 5  |

## Critical: Stopping SITL Safely

**IMPORTANT:** Killing SITL while the HITL plugin is connected will freeze X-Plane!

**Before killing/restarting SITL:**
1. In X-Plane: **Plugins → INAV-X-Plane-HITL → Disable**
2. Wait for plugin to disconnect
3. Now safe to kill SITL
4. After SITL restarts, re-enable the plugin

**Note:** The HITL plugin does not expose REST API commands for connect/disconnect - must use X-Plane's plugin menu.

Helper script: `inav/build_sitl/disconnect_xplane_hitl.py`

## RC Input with HITL Plugin

The HITL plugin sends sensor data (attitude, GPS, etc.) to SITL but reads RC input from X-Plane's joystick system (`sim/joystick/joy_mapped_axis_value`). Without a physical joystick, SITL stays in FAILSAFE.

**Workaround - MSP RX:**
1. Add `#define USE_RX_MSP` to `src/main/target/SITL/target.h`
2. Rebuild SITL
3. Set `receiverType = 2` (MSP) via MSP or CLI
4. Send RC via `MSP_SET_RAW_RC` from Python script
5. HITL provides sensors, MSP provides RC

Helper script: `inav/build_sitl/configure_msp_rx.py`

## Virtual Joystick Daemon (Alternative to Physical Joystick)

For automated testing or when no physical joystick is available, use the virtual joystick daemon.

**Location:** `inav/build_sitl/xplane_scripts/`

### Safe Usage - IMPORTANT!

**ALWAYS use the safe wrapper script to prevent lockups!**

The daemon uses a FIFO (named pipe) for communication. Writing to a FIFO blocks forever if no reader exists. The wrapper script prevents this.

```bash
cd inav/build_sitl/xplane_scripts

# Start daemon (kills any existing, creates FIFO, verifies startup)
./joystick_cmd.sh start

# Check status BEFORE sending commands
./joystick_cmd.sh status

# Send commands safely (timeout-protected)
./joystick_cmd.sh calibrate    # Full axis sweep for X-Plane calibration
./joystick_cmd.sh center       # Center all sticks
./joystick_cmd.sh axis 0 16000 # Set roll axis
./joystick_cmd.sh axis 2 -32768  # Throttle min (required before arm)
./joystick_cmd.sh axis 4 32767   # AUX1 (arm) high

# Stop daemon
./joystick_cmd.sh stop
```

### NEVER Do This (Will Lock Up!)

```bash
# WRONG - blocks forever if daemon not running or FIFO deleted
echo "calibrate" > /tmp/inav_joystick_cmd   # DO NOT DO THIS!
```

### Axis Mapping

| Axis | Function | Neutral | Low | High |
|------|----------|---------|-----|------|
| 0 | Roll | 0 | -32768 | 32767 |
| 1 | Pitch | 0 | -32768 | 32767 |
| 2 | Throttle | -32768 | -32768 | 32767 |
| 3 | Yaw | 0 | -32768 | 32767 |
| 4 | AUX1 (ARM) | -32768 | -32768 | 32767 |
| 5 | AUX2 | 0 | -32768 | 32767 |

### X-Plane Calibration Workflow

1. Start daemon: `./joystick_cmd.sh start`
2. Verify status: `./joystick_cmd.sh status`
3. In X-Plane: Settings → Joystick → Select "INAV Virtual Joystick"
4. Run calibration sweep (10+ seconds):
   ```bash
   for i in 1 2 3 4 5; do ./joystick_cmd.sh calibrate; sleep 2; done
   ```
5. Center and hold for 30 seconds:
   ```bash
   ./joystick_cmd.sh center && sleep 30
   ```
6. In X-Plane: Click "Done" to save joystick selection
7. Verify axes mapped to: Roll, Pitch, Yaw, Cowl Flap 1 (throttle), Cowl Flap 2 (AUX1)

**IMPORTANT:** If joystick daemon restarts, X-Plane may switch to a different joystick.
Reselect "INAV Virtual Joystick" and click "Done" after any daemon restart.

### Confirmed Working Configuration

**Joystick Daemon → X-Plane chain works when:**
- Daemon running: `./joystick_cmd.sh status` shows RUNNING
- FIFO exists at `/tmp/inav_joystick_cmd`
- Virtual joystick visible: `cat /proc/bus/input/devices | grep -A5 "INAV Virtual"`
- X-Plane has "INAV Virtual Joystick" selected (click Done after selecting!)
- Axes move in X-Plane joystick settings when commands sent

**Test the chain:**
```bash
# Send movements while watching X-Plane joystick settings
./joystick_cmd.sh axis 0 -30000  # Roll left
sleep 1
./joystick_cmd.sh axis 0 30000   # Roll right
sleep 1
./joystick_cmd.sh center
```

See `inav/build_sitl/xplane_scripts/FIFO_NOTES.md` for FIFO lockup prevention details.

### HITL RC Input Issue (RX_TYPE_SIM)

**Known issue:** With `RX_TYPE_SIM`, HITL plugin RC forwarding requires RSSI > 0.
The serial_proxy code (`src/main/target/SITL/serial_proxy.c:548`) only sets RC values if rssi > 0.
If HITL doesn't send MSP_ANALOG with RSSI, RC input is silently ignored.

**Workaround:** Use `RX_TYPE_MSP` and send RC via MSP_SET_RAW_RC from a script.

## Troubleshooting

### X-Plane frozen
- Killed SITL without disconnecting HITL plugin first
- Solution: Force-quit X-Plane, restart, reconnect plugin after SITL is running

### SITL in FAILSAFE with RC_LINK error
- HITL plugin needs joystick for RC input
- Solution: Use MSP RX workaround above, or connect a joystick

### No connection to X-Plane
- Check UDP port in X-Plane network settings
- Verify firewall allows UDP 49000
- Use `--simport` to match X-Plane's port

### Aircraft not responding
- Verify SITL is receiving data (check console output)
- Confirm channel mapping matches aircraft type
- Check that ARM switch is configured

### Sensors not updating
- Select "FAKE" sensor type in Configurator
- Verify X-Plane is sending data (check Network settings)

### Virtual joystick command hangs
- **Cause:** Writing to FIFO with no reader blocks forever
- **Solution:** Always use `joystick_cmd.sh` wrapper script
- **Recovery:** Ctrl+C to kill blocked process, then `./joystick_cmd.sh start`

### Virtual joystick not seen by X-Plane
- Run `./joystick_cmd.sh start` and verify "Daemon started" message
- Check status: `./joystick_cmd.sh status`
- Run calibration: `./joystick_cmd.sh calibrate`
- In X-Plane, rescan joysticks in Settings → Joystick

### MSP requests timing out
- **Cause:** UART port stuck in CLI mode
- **How it happens:** Sending `#` character to a UART port enters CLI mode, which disables MSP on that port
- **NEVER** use netcat/echo to send CLI commands to SITL ports - CLI mode cannot be exited without reboot
- **Solution:** Restart SITL (disconnect HITL first to avoid X-Plane freeze)

## UART Port Management - CRITICAL

SITL binds TCP ports for serial UARTs:
- **UART1:** Port 5760
- **UART2:** Port 5761

### Rules to Avoid Problems

1. **NEVER send CLI commands (`#`) via netcat/echo** - this permanently locks the port in CLI mode until SITL restart

2. **Always use MSP library (mspapi2)** for configuration, not CLI:
   ```python
   from mspapi2 import MSPApi, InavMSP
   with MSPApi(tcp_endpoint='localhost:5761') as api:
       info, result = api._request(InavMSP.MSP_FEATURE)
       # Use 'featureMask' not 'features'
       features = result['featureMask']
   ```

3. **HITL plugin uses one UART** (typically UART2/5761) - keep another free for MSP monitoring

4. **If a port gets stuck in CLI mode:**
   - Disconnect HITL plugin first (Plugins → INAV HITL → Disable)
   - Kill SITL: `pkill -f SITL.elf`
   - Restart SITL
   - Reconnect HITL

### Recommended Port Allocation
| Port | UART | Use |
|------|------|-----|
| 5760 | UART1 | MSP monitoring/control (mspapi2) |
| 5761 | UART2 | HITL plugin |

## Blocking I/O Hazards - CRITICAL

**Operations that will BLOCK FOREVER and lock up your session:**

1. **Writing to FIFO with no reader:**
   ```bash
   # WRONG - blocks forever
   echo "cmd" > /tmp/inav_joystick_cmd
   ```
   **Solution:** Use `joystick_cmd.sh` wrapper with timeout

2. **Reading from device files:**
   ```bash
   # WRONG - blocks waiting for input events
   cat /dev/input/js0
   jstest /dev/input/js0
   ```
   **Solution:** Don't read from input devices; use non-blocking tools or skip

3. **CLI commands to SITL:**
   ```bash
   # WRONG - enters CLI mode, port becomes unresponsive to MSP
   echo "#" | nc localhost 5760
   ```
   **Solution:** Use mspapi2 library for all SITL communication

4. **Any read from pipe/socket with no writer:**
   ```bash
   # WRONG - blocks if nothing is writing
   cat /proc/PID/fd/X
   ```

**Recovery:** Ctrl+C or kill the blocked process from another terminal.

## Related Resources

- [INAV SITL Documentation](../../../inav/docs/SITL/SITL.md)
- [X-Plane Integration](../../../inav/docs/SITL/X-Plane.md)
- [INAV-X-Plane-HITL Plugin](https://github.com/RomanLut/INAV-X-Plane-HITL)
- [X-Plane Web API](https://developer.x-plane.com/article/x-plane-web-api/)
- [SlewMode Plugin](https://github.com/jonaseberle/xplane-plugin-SlewMode)
