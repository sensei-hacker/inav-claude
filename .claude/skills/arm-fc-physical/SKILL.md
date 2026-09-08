---
description: Arm physical flight controller via MSP and download blackbox logs
triggers:
  - arm fc
  - arm physical fc
  - download blackbox
  - blackbox from fc
---

# arm-fc-physical

**Arm a physical flight controller via MSP and download blackbox logs for analysis**

---

## When to Use This Skill

- Generate blackbox logs from physical FC for debugging
- Test firmware behavior without actual flight
- Capture sensor data for analysis
- Validate blackbox logging is working correctly

---

## Quick Start

### 1. Configure FC (One-Time Setup)

```bash
# Check FC status
~/.claude/skills/flash-firmware-dfu/fc-cli.py status /dev/ttyACM0

# Configure MSP receiver and arming
cd claude/developer/scripts/testing/inav/sitl
python3 configure_fc_msp_rx.py --port /dev/ttyACM0

# Configure blackbox — pick ONE depending on how you want to trigger logging:
cd ../blackbox/config
python3 configure_fc_blackbox.py --port /dev/ttyACM0 --rate-denom 100          # logs only while armed
python3 configure_blackbox_arm_controlled.py --port /dev/ttyACM0 --rate-denom 100  # same, arm-gated variant
# OR set blackbox_arm_control=-1 (via CLI) to log continuously from boot — see
# "Logging Without Arming" below; skips configure_fc_msp_rx.py entirely.

# Calibrate accelerometer via INAV Configurator (if needed)
```

**Directory note:** these scripts live under `claude/developer/scripts/testing/inav/`
in subdirectories by function (`sitl/`, `blackbox/config/`, `blackbox/analysis/`,
`gps/injection/`) — despite `sitl/` in the path, several of those scripts (this
one included) work against physical hardware too, not just SITL. Don't assume
a script only applies to SITL from its directory name; check its own docstring.

### 2. Generate Blackbox Log

**SAFETY: Remove propellers before arming!**

```bash
cd claude/developer/scripts/testing/inav/sitl

# Arm for 30 seconds (default)
python3 continuous_msp_rc_sender.py /dev/ttyACM0

# Arm for custom duration
python3 continuous_msp_rc_sender.py /dev/ttyACM0 --duration 60
```

**Avoid `arm_fc_physical.py`** (`claude/developer/scripts/testing/inav/sitl/arm_fc_physical.py`)
for this step — despite the name matching this skill, it arms via **HITL mode**,
which bypasses the blackbox subsystem entirely (see Common Issues below). It's
only useful for a quick "does MSP arming work at all" smoke test, never for
generating a log.

#### Logging Without Arming

If you don't need a realistic arm-triggered log — e.g. bench-testing the SD/flash
write path itself — set `blackbox_arm_control = -1` via CLI (`set blackbox_arm_control = -1`
then `save`, in the **same** CLI session — see the note under Common Issues about
settings reverting). This logs continuously from boot to power-off and sidesteps
every arming prerequisite (accel cal, RX config, ANGLE/CAL flags). Pair it with
`claude/developer/scripts/testing/inav/gps/injection/gps_inject_no_arming.py` if
you want synthetic GPS data flowing into the log without attempting to arm.

### 3. Download Log

`download_blackbox_from_fc.py` only works for `SPIFLASH` (`MSP_DATAFLASH_READ`).
For `SDCARD`, there's no MSP equivalent — reboot to USB mass-storage mode and
copy the files off instead:

```bash
python3 .claude/skills/flash-firmware-dfu/fc-cli.py msc /dev/ttyACM0
sleep 3   # auto-mounts on Ubuntu
lsblk   # confirm which device is the card — don't assume /dev/sdb
cp /media/$USER/<label>/logs/LOG*.TXT ./
udisksctl unmount -b /dev/sdb1   # unmount before FC leaves MSC mode; use the confirmed device
```

### 4. Decode and Analyze

```bash
# Decode log to CSV
blackbox_decode test_log.TXT

# Creates: test_log.01.csv, test_log.01.gps.csv
# View data
head -50 test_log.01.csv

# Or classify the log as CLEAN/SUSPECT/CORRUPT (missing frames, mid-file zero
# blocks, truncation, torn header) instead of eyeballing the CSV:
python3 claude/developer/scripts/testing/inav/blackbox/analysis/check_blackbox_integrity.py test_log.TXT
```

---

## Prerequisites

**Hardware:**
- Flight controller with USB connection
- FC appears as `/dev/ttyACM0` (or similar)
- **Propellers removed!**

**Software:**
```bash
pip3 install pyserial
pip3 install git+https://github.com/xznhj8129/mspapi2
```

**FC Configuration:**
1. Accelerometer calibrated (via Configurator)
2. MSP receiver configured (`rx_spi_protocol = MSP`)
3. ARM mode on AUX1 (range 1700-2100)
4. Blackbox enabled (`blackbox_device = SPIFLASH`)

---

## Common Issues

### FC Won't Arm

Check arming flags:
```bash
~/.claude/skills/flash-firmware-dfu/fc-cli.py status /dev/ttyACM0
```

Common blockers:
- **ACC** - Calibrate accelerometer via Configurator
- **CAL** - Wait 5+ seconds after boot
- **ANGLE** - Level FC or disable small_angle check
- **SETTINGFAIL** - Fix RX settings with configure script

### No Blackbox Data (0 bytes)

1. **HITL mode was used** - Use `continuous_msp_rc_sender.py` instead (never `arm_fc_physical.py` — see above)
2. **FC not armed** - Check arming flags
3. **Blackbox not configured** - Run `configure_fc_blackbox.py`
4. **Flash full** - Erase via Configurator
5. **SD card has no filesystem** - if `blackbox_device = SDCARD`, check `status`
   for `Filesystem: Fatal - no FAT MBR partitions`. The card is detected at the
   hardware level but won't accept writes until it's reformatted (single FAT32
   partition) on a computer — INAV can't format it in place unless the target
   defines `USE_USB_MSC` (most don't; check `target.h`).

### Settings Silently Not Taking Effect

Two real gotchas hit during hardware testing:

- **`configure_fc_blackbox.py` (and other scripts using `MSP2_COMMON_SET_SETTING`)
  print "✓" without confirming the write actually landed.** Always verify with
  `fc-cli.py "get <setting>"` after running one of these scripts — don't trust
  the script's own success message.
- **Changes made via separate `fc-cli.py` invocations can revert.** Each
  invocation opens and closes its own serial connection; an unsaved `set` from
  one invocation can be lost before a later invocation's `save` commits it.
  Combine `set` and `save` in a single invocation instead:
  `fc-cli.py $'set some_setting = 1\nsave' /dev/ttyACM0`.
- **`blackbox_rate_denom` may get silently overridden at boot.** INAV enforces
  a hard 1kHz cap on blackbox logging rate regardless of what you set
  (`fc_init.c`, `blackboxLooptime` check) — "run faster than 1kHz can cause UAV
  to drop dead when digital ESC protocol is used." On a board with a fast PID
  loop (e.g. ~2kHz), `rate_denom=1` gets silently raised to whatever the
  fastest allowed value is (e.g. `2`). Check the actual value with
  `fc-cli.py "get blackbox_rate_denom"` after reboot rather than assuming what
  you set stuck.
- **Two clients can't share the serial port.** If INAV Configurator (or any
  other tool) is already connected to the FC, MSP requests from your script
  will time out with no useful error. Check `ps aux | grep -i configurator`
  and disconnect it first.
- **CLI mode blocks MSP indefinitely, with no timeout.** If a tool enters CLI
  mode (`####`) and closes the connection without sending `exit`, the FC
  stays latched in CLI — any MSP arming script run afterward gets silently
  ignored (visible as the `CLI` arming-disabled flag). Fixed in `fc-cli.py`
  (now sends `exit` before closing); still, prefer MSP over CLI for routine
  checks when possible.
- **`blackbox_arm_control = -1` on SDCARD races SD-card mount at boot** —
  `blackboxStart()` can fire before AFATFS finishes mounting, and gives up
  permanently for that boot. Use arm-triggered logging (`= 0`, the default)
  instead.
- **A freshly-reformatted SD card can be slow to accept its first log** —
  AFATFS reserves free space (`FREESPAC.E`) before the `logs` dir exists;
  give it a few minutes if the first log never appears.

### Serial Port Permission Denied

```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

---

## Key Scripts

Scripts live under `claude/developer/scripts/testing/inav/` in subdirectories —
see the directory note in step 1 above; not everything under `sitl/` is
SITL-only.

- **`sitl/continuous_msp_rc_sender.py`** - Arm FC and send RC frames (physical FC; despite the dir name, does NOT use HITL)
- **`sitl/arm_fc_physical.py`** - Quick MSP-arm smoke test via HITL — do NOT use for blackbox logging (HITL bypasses it)
- **`sitl/configure_fc_msp_rx.py`** - Configure MSP receiver and ARM mode (formerly referenced here as `configure_fc_for_msp_arming.py`, which no longer exists)
- **`blackbox/config/configure_fc_blackbox.py`** - Configure blackbox settings (arm-gated logging)
- **`blackbox/config/configure_blackbox_arm_controlled.py`** - Same purpose, arm-gated variant
- **`blackbox/config/download_blackbox_from_fc.py`** - Download log via MSP
- **`blackbox/analysis/check_blackbox_integrity.py`** - Classify a downloaded log as CLEAN/SUSPECT/CORRUPT (missing frames, mid-file zero blocks, truncation, torn header); supports `--dir`/`--compare` for before/after A-B testing
- **`gps/injection/gps_inject_no_arming.py`** - Inject synthetic GPS data without arming; pairs with `blackbox_arm_control = -1` for log-from-boot testing

---

## Technical Details

**RC Frame Rate:** 50 Hz (matches CRSF standard)
**Download Speed:** ~2.5 KB/s (~20s for 50KB log)
**MSP Commands Used:**
- MSP_SET_RAW_RC (200) - Send RC channels
- MSP_DATAFLASH_SUMMARY (70) - Query flash status
- MSP_DATAFLASH_READ (71) - Download data

**RC Channel Mapping (AETR):**
- Channel 3: Throttle (1000=low, 1600=mid)
- Channel 5: AUX1 ARM (1000=disarm, 1800=arm)

---

## See Also

- **Detailed Guide:** `.claude/skills/arm-fc-physical/REFERENCE.md`
- **Flash Firmware:** `/flash-firmware-dfu`
- **Build Firmware:** `/build-inav-target`
- **Arm SITL:** `/sitl-arm`
- **MSP Protocol:** `/msp-protocol`
