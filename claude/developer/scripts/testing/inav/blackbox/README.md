# Blackbox Logging Tools

Tools for configuring, capturing, analyzing, and replaying INAV blackbox logs on SITL and physical flight controllers.

## Quick Start

```bash
# Configure SITL for FILE logging
config/configure_sitl_blackbox_file.py --port 5760 --rate-denom 2

# Enable BLACKBOX feature (REQUIRED!)
config/enable_blackbox_feature.py --port 5760

# Download blackbox from physical FC
config/download_blackbox_from_fc.py --port /dev/ttyACM0

# Replay blackbox to test position estimator
replay/replay_and_capture_blackbox.sh
```

## Directory Structure

| Directory | Purpose | Scripts |
|-----------|---------|---------|
| **[config/](config/)** | Blackbox configuration (enable, settings) | 11 scripts |
| **[replay/](replay/)** | Replay workflows | 2 scripts |
| **[analysis/](analysis/)** | Decode, analyze, create test logs | 3 scripts |
| **[docs/](docs/)** | Specialized blackbox documentation | 8 docs |

## Common Tasks

| I Want To... | Use This |
|--------------|----------|
| **Configure SITL blackbox (FILE)** | `config/configure_sitl_blackbox_file.py` |
| **Configure SITL blackbox (SERIAL)** | `config/configure_sitl_blackbox_serial.py` |
| **Enable BLACKBOX feature** | `config/enable_blackbox_feature.py` |
| **Download from FC flash** | `config/download_blackbox_from_fc.py` |
| **Erase FC flash** | `config/erase_blackbox_flash.py` |
| **Replay blackbox** | `replay/replay_and_capture_blackbox.sh` |
| **Decode frames** | `analysis/decode_blackbox_frames.py` |
| **Check log integrity / detect corruption (A/B compare builds)** | `analysis/check_blackbox_integrity.py` |

## Key Concepts

**Blackbox Modes:**
- **FILE** - Saves to .TXT files (SITL default, FC with SD card)
- **SERIAL** - Streams via MSP port
- **FLASH** - Saves to onboard flash (FC without SD)

**CRITICAL: BLACKBOX Feature Flag**
- Must enable BLACKBOX feature (bit 19) via `config/enable_blackbox_feature.py`
- Setting `blackbox_device` alone is **insufficient**!
- Blackbox will not log without feature enabled

**Logging Rates:**
- `blackbox_rate_denom = 1` - Every PID loop (1000Hz)
- `blackbox_rate_denom = 2` - Every other loop (500Hz) - **Recommended**
- `blackbox_rate_denom = 10` - Every 10th loop (100Hz)

## Documentation

**Complete workflows:** [docs/README_GPS_BLACKBOX_TESTING.md](../gps/docs/README_GPS_BLACKBOX_TESTING.md) - GPS+blackbox integration

**Blackbox-specific docs:** [docs/](docs/)
- [BLACKBOX_SERIAL_WORKFLOW.md](docs/BLACKBOX_SERIAL_WORKFLOW.md) - Serial logging
- [BLACKBOX_TESTING_PROCEDURE.md](docs/BLACKBOX_TESTING_PROCEDURE.md) - Test procedures
- [REPLAY_BLACKBOX_README.md](docs/REPLAY_BLACKBOX_README.md) - Replay workflow
- [REPLAY_WORKFLOW_LESSONS.md](docs/REPLAY_WORKFLOW_LESSONS.md) - Critical lessons
- And more... (see docs/README.md)

## Related Tools

- `../gps/workflows/run_gps_blackbox_test.sh` - GPS + blackbox integration workflow
- `../sitl/` - SITL configuration and utilities
- Blackbox decoder: `blackbox_decode` (external tool)

## Dependencies

- **mspapi2:** `pip3 install ~/Documents/planes/inavflight/mspapi2`
- **Blackbox decoder:** For decoding .TXT files to CSV

## Notes

**SITL vs Physical FC:**
- SITL: Default port 5760, blackbox saves to `build_sitl/*.TXT`
- Physical FC: Usually `/dev/ttyACM0`, blackbox on flash/SD

**Configuration Persistence:**
- SITL: Settings saved in `eeprom.bin`
- FC: Settings saved to EEPROM

---

**See subdirectory READMEs for detailed documentation on each tool category.**
