# Arm Physical FC - Detailed Reference

Complete reference documentation for arming physical flight controllers and downloading blackbox logs.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Complete Workflow](#complete-workflow)
- [Configuration Scripts](#configuration-scripts)
- [Troubleshooting](#troubleshooting)
- [Technical Details](#technical-details)
- [Safety Notes](#safety-notes)

---

## Prerequisites

### Hardware Setup
1. Flight controller with USB connection
2. USB cable connected to development machine
3. FC appears as `/dev/ttyACM0` (or similar)

### Software Requirements
```bash
# Python dependencies
pip3 install pyserial
pip3 install git+https://github.com/xznhj8129/mspapi2

# Verify FC connection
ls -l /dev/ttyACM*
```

### FC Configuration Requirements

**CRITICAL**: The FC must be configured before arming:

1. **Accelerometer calibration** - FC must be level and calibrated
2. **MSP receiver** - `rx_spi_protocol = MSP`
3. **ARM mode on AUX1** - Configured to arm when AUX1 > 1700
4. **Blackbox logging** - `blackbox_device = SPIFLASH`, `blackbox_rate_denom = 100`

---

## Complete Workflow

### Step 1: Check FC Status

```bash
# Check if FC can be armed
~/.claude/skills/flash-firmware-dfu/fc-cli.py status /dev/ttyACM0
```

Look for "Arming disabled flags" - should ideally show only "CLI" when connected.

### Step 2: Calibrate Accelerometer (If Needed)

If status shows "ACC" flag:
1. Place FC on level surface
2. Open INAV Configurator
3. Go to Setup tab
4. Click "Calibrate Accelerometer"
5. Wait for completion

### Step 3: Configure FC for MSP Arming

Run the configuration script:
```bash
cd claude/developer/scripts/testing/inav/sitl
python3 configure_fc_msp_rx.py --port /dev/ttyACM0
```

(Not needed at all if you're going to use `blackbox_arm_control = -1` —
see "Logging Without Arming" in the main SKILL.md.)

Or configure manually via CLI:
```bash
# Set MSP receiver
set rx_spi_protocol = MSP
set min_check = 1100
set max_check = 1900
set rx_min_usec = 885
set rx_max_usec = 2115

# Configure ARM mode on AUX1 (range 1700-2100)
# This requires MSP commands - use script above
```

### Step 4: Configure Blackbox

```bash
cd claude/developer/scripts/testing/inav/blackbox/config
python3 configure_fc_blackbox.py --port /dev/ttyACM0 --rate-denom 100
# or, for an arm-gated variant of the same thing:
python3 configure_blackbox_arm_controlled.py --port /dev/ttyACM0 --rate-denom 100
```

Or via CLI — **send `set` and `save` in the same invocation** (a `set` from
one `fc-cli.py` call can be lost before a separate later call's `save`
commits it, since each call opens/closes its own serial connection):
```bash
fc-cli.py $'set blackbox_device = SPIFLASH\nset blackbox_rate_denom = 100\nsave' /dev/ttyACM0
```

To skip arming entirely and log continuously from boot instead:
```bash
fc-cli.py $'set blackbox_arm_control = -1\nsave' /dev/ttyACM0
```

### Step 5: Arm FC and Generate Log

**IMPORTANT**: Make sure propellers are removed or FC is in a safe location!

```bash
cd claude/developer/scripts/testing/inav/sitl

# Arm for 30 seconds at 50Hz (default)
python3 continuous_msp_rc_sender.py /dev/ttyACM0

# Arm for custom duration/rate
python3 continuous_msp_rc_sender.py /dev/ttyACM0 --duration 60 --rate 100
```

The script will:
1. Connect to FC
2. Wait 5 seconds (sensor stabilization, disarmed)
3. Arm the FC (throttle low)
4. Fly armed at mid-throttle for specified duration
5. Disarm and exit

**Do not substitute `arm_fc_physical.py`** (same directory) for this step —
it arms via HITL mode, which bypasses the blackbox subsystem (see "Why Not
Use HITL Mode" below). It's a quick MSP-arming smoke test only.

If you configured `blackbox_arm_control = -1` instead of arm-gated logging,
skip this step — the FC is already logging from boot. Optionally run
`claude/developer/scripts/testing/inav/gps/injection/gps_inject_no_arming.py`
to feed it synthetic GPS data while it logs.

### Step 6: Download Blackbox Log

```bash
cd claude/developer/scripts/testing/inav/blackbox/config

# Download to default filename
python3 download_blackbox_from_fc.py /dev/ttyACM0

# Download to specific file
python3 download_blackbox_from_fc.py /dev/ttyACM0 test_results/my_log.TXT
```

Download takes ~2-3 minutes for a typical log.

### Step 7: Decode Blackbox Log

```bash
cd claude/developer/scripts/testing/inav/blackbox/config
blackbox_decode test_results/my_log.TXT

# For an objective CLEAN/SUSPECT/CORRUPT verdict instead of eyeballing the CSV
# (useful for A/B firmware comparisons):
python3 ../analysis/check_blackbox_integrity.py test_results/my_log.TXT
```

This creates a CSV file with decoded data.

---

## Configuration Scripts

### sitl/configure_fc_msp_rx.py

Configures MSP receiver and ARM mode. (Formerly referenced in this doc as
`configure_fc_for_msp_arming.py` — that name no longer exists in the repo.)

**What it does**:
1. Sets receiver type to MSP (RX_TYPE_MSP = 2)
2. Configures ARM mode on AUX1 (range 1700-2100)
3. Sets valid RX channel limits
4. Saves and reboots

### blackbox/config/configure_fc_blackbox.py

Configures blackbox logging (arm-gated: logs only while armed).

**What it does**:
1. Sets `blackbox_device` (default SPIFLASH; pass `--device sdcard` for SD)
2. Sets `blackbox_rate_denom` (default 100; logs every Nth loop — but see
   "Blackbox Rate Settings" below, the firmware may silently raise this)
3. Saves configuration

**Caveat**: uses `MSP2_COMMON_SET_SETTING`, which this script does not verify
after writing. Its "✓" output means "the write was sent," not "the write took
effect." Confirm with `fc-cli.py "get <setting>"` afterward.

### blackbox/config/configure_blackbox_arm_controlled.py

Same purpose as `configure_fc_blackbox.py`, explicitly framed around
arm-gated logging (log only while armed, not continuously). Same MSP-verification
caveat applies.

### gps/injection/gps_inject_no_arming.py

Injects synthetic GPS MSP data without attempting to arm — for use alongside
`blackbox_arm_control = -1` when you want GPS fields populated in a
log-from-boot test but don't want to deal with arming prerequisites.

### sitl/arm_fc_physical.py

Arms via HITL mode for a quick "can it arm at all" MSP smoke test. **Not
usable for blackbox log generation** — HITL bypasses the blackbox subsystem
entirely (see "Why Not Use HITL Mode" below).

---

## Troubleshooting

### FC Won't Arm

**Check arming flags**:
```bash
~/.claude/skills/flash-firmware-dfu/fc-cli.py status /dev/ttyACM0
```

Common arming blockers:

| Flag | Meaning | Solution |
|------|---------|----------|
| ACC | Accelerometer not calibrated | Calibrate via Configurator |
| CAL | Sensors calibrating | Wait 5+ seconds after boot |
| RX | No RC link | Script sends RC - check connection |
| CLI | CLI mode active | Script connects/disconnects properly |
| SETTINGFAIL | Invalid settings | Check min_check, rx_min_usec values |
| ANGLE | FC not level | Level FC or disable small_angle check |

**Fix invalid RX settings**:
```bash
set min_check = 1100
set max_check = 1900
set rx_min_usec = 885
set rx_max_usec = 2115
save
```

**Check ARM mode configuration**:
```bash
# View mode ranges
~/.claude/skills/flash-firmware-dfu/fc-cli.py "aux" /dev/ttyACM0
```

Should show ARM on AUX1 with range 1700-2100.

### No Blackbox Data Logged (0 bytes)

**Common causes**:

1. **HITL mode enabled** - HITL bypasses blackbox!
   - Solution: Use `continuous_msp_rc_sender.py` (does NOT use HITL)
   - Do NOT use `arm_fc_physical.py` for this — it arms via HITL by design
   - Verify: Check script doesn't call MSP_SIMULATOR

2. **FC not actually armed**
   - Check arming flags with `status` command
   - Calibrate accelerometer if needed

3. **Blackbox not configured**
   ```bash
   set blackbox_device = SPIFLASH
   set blackbox_rate_denom = 100
   save
   ```

4. **Flash full**
   - Check with download script (shows "Used size")
   - Erase via Configurator if needed

### Download Script Shows Wrong Size

If download shows 16.7 MB (entire chip) instead of actual log size:
1. Reflash firmware (resets flash state)
2. Reconfigure blackbox
3. Generate fresh log

### Serial Port Permission Denied

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in for changes to take effect
```

### Port Busy / Already in Use

```bash
# Kill any processes using the port
sudo lsof /dev/ttyACM0
sudo kill <PID>

# Or force disconnect
pkill -9 -f "download_blackbox"
```

---

## Technical Details

### MSP Commands Used

| Code | Name | Purpose |
|------|------|---------|
| 70 | MSP_DATAFLASH_SUMMARY | Query flash status [flags:1, sectors:4, totalSize:4, usedSize:4] |
| 71 | MSP_DATAFLASH_READ | Read chunks [address:4, length:2] → [address:4, data:...] |
| 72 | MSP_DATAFLASH_ERASE | Erase entire flash chip |
| 200 | MSP_SET_RAW_RC | Send RC channels [ch1:2, ch2:2, ..., ch18:2] |
| 250 | MSP_EEPROM_WRITE | Save config to EEPROM |
| 68 | MSP_REBOOT | Reboot FC |

### RC Channel Mapping

INAV uses AETR mapping by default:
- Channel 1: Roll (1500 = center)
- Channel 2: Pitch (1500 = center)
- Channel 3: **Throttle** (1000 = low, 1600 = mid, 2000 = high)
- Channel 4: Yaw (1500 = center)
- Channel 5: AUX1 - ARM (1000 = disarm, 1800 = arm)
- Channels 6-18: Additional AUX channels (1500 = center)

### Why Not Use HITL Mode?

HITL (Hardware-In-The-Loop) mode:
- ✓ Bypasses sensor calibration requirements
- ✓ Allows quick arming for testing
- ✗ **Prevents blackbox logging** (HITL mode bypasses blackbox subsystem)
- ✗ Not realistic for flight testing

For blackbox testing, use real sensor calibration without HITL.

### Blackbox Rate Settings

`blackbox_rate_denom` controls logging frequency:
- `1` = Log every loop iteration (highest resolution, large files)
- `10` = Log every 10th iteration
- `100` = Log every 100th iteration (good for 30s+ flights)

For a 5-second nav cycle, use `rate_denom = 100` to ensure full cycle captured.

**Hard cap you can't configure around:** INAV enforces a maximum blackbox rate
of 1kHz regardless of what you set (`fc_init.c`, checked at every boot) —
"Do not allow blackbox to run faster than 1kHz. It can cause UAV to drop dead
when digital ESC protocol is used." If `rate_denom` would imply logging faster
than that given the board's actual PID loop rate, the firmware silently
overrides it: `rate_num = 1`, `rate_denom = ceil(1000 / looptime_us)`. In
practice this means `rate_denom = 1` only takes effect as written on a board
running at ≤1kHz PID rate; on a ~2kHz board it becomes `2` after reboot no
matter what you sent. If you need the true maximum sustainable rate for a
stress test, don't hardcode `1` — set it, reboot, then read back the actual
value with `fc-cli.py "get blackbox_rate_denom"`.

### Performance Notes

**Arming Script**:
- Target rate: 50 Hz (matches CRSF standard)
- Actual rate: ~70 Hz (depends on system load)
- CPU usage: Minimal (<5%)

**Download Script**:
- Speed: ~2.5 KB/s average
- 50 KB log: ~20 seconds
- 500 KB log: ~3-4 minutes
- 5 MB log: ~30+ minutes

**Chunk Size**:
- Current: 128 bytes (reliable)
- Larger chunks may timeout on some FCs
- Smaller chunks reduce speed

---

## Safety Notes

- **ALWAYS remove propellers** before arming on the bench
- Secure FC to prevent movement when armed
- Have a way to quickly disconnect power if needed
- Don't arm FC when connected via Configurator (conflicts)
- Be aware that ESCs may beep/initialize when armed

---

## Related Skills

- **flash-firmware-dfu** - Flash firmware to FC before testing
- **build-inav-target** - Build custom firmware for testing
- **sitl-arm** - Arm SITL (software simulator) via MSP
- **msp-protocol** - MSP protocol reference

---

## Example: Automated Test Loop

```bash
#!/bin/bash
# Run multiple test iterations
# continuous_msp_rc_sender.py: claude/developer/scripts/testing/inav/sitl/
# download_blackbox_from_fc.py: claude/developer/scripts/testing/inav/blackbox/config/
# check_blackbox_integrity.py: claude/developer/scripts/testing/inav/blackbox/analysis/

for i in {1..5}; do
    echo "=== Test $i of 5 ==="

    # Generate log
    python3 continuous_msp_rc_sender.py /dev/ttyACM0 --duration 30

    # Download
    python3 download_blackbox_from_fc.py /dev/ttyACM0 test_results/test_$i.TXT

    # Decode
    blackbox_decode test_results/test_$i.TXT

    # Or classify pass/fail objectively (useful when scripting an A/B comparison)
    python3 check_blackbox_integrity.py test_results/test_$i.TXT

    # Brief pause
    sleep 5
done

echo "✓ All tests complete"
```
