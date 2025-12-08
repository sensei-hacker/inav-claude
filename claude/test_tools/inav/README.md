# INAV Test Tools

Consolidated test tools for INAV firmware and configurator development.

**Last updated:** 2025-12-07 (Consolidation from developer/test_tools/)

---

## Directory Structure

```
claude/test_tools/inav/
├── crsf/              # CRSF protocol testing and debugging
├── msp/               # MSP protocol tools
│   ├── benchmark/     # Performance benchmarking
│   ├── mock/          # Mock responders for testing
│   └── debug/         # Debugging utilities
├── gps/               # GPS and navigation testing
│   ├── historical/    # Older test versions (archived)
│   └── test_results/  # Test output logs
├── sitl/              # SITL-specific test tools
├── docs/              # Documentation
└── usb_throughput_test.py  # USB performance testing
```

---

## CRSF Tools (crsf/)

### Main Test Infrastructure

**test_crsf_telemetry.sh** - Comprehensive CRSF telemetry testing workflow
- Automated 7-step test process
- Supports multiple test modes (baseline, pr11025, pr11100)
- Verifies SITL build, enables telemetry, captures frames
- **Usage:** `./test_crsf_telemetry.sh [build_dir] [test_mode]`

**quick_test_crsf.sh** - Quick build-test cycle helper
- Options: `-r` (rebuild), `-c` (clean), `-s` (skip test)
- Streamlines development workflow
- **Usage:** `./quick_test_crsf.sh [-r|-c|-s]`

**configure_sitl_crsf.py** - SITL CRSF configuration via MSP
- Configures CRSF on UART2 for SITL testing
- Sets up RX protocol and serial ports

### Debugging Utilities

**crsf_rc_sender.py** - RC channel sender for SITL
- Sends CRSF RC frames to keep FC armed
- Supports configurable update rate
- **Usage:** `python3 crsf_rc_sender.py [uart_port] --rate [hz]`

**crsf_stream_parser.py** - Telemetry frame parser
- Captures and decodes CRSF telemetry frames
- Displays frame types and statistics
- **Usage:** `python3 crsf_stream_parser.py [uart_port]`

**analyze_frame_0x09.py** - Altitude/vario frame analyzer
- Analyzes CRSF frame 0x09 (altitude, vario)
- Validates data ranges and correlations
- **Usage:** `python3 analyze_frame_0x09.py [capture_file]`

**test_telemetry_simple.py** - Simple telemetry test
- Lightweight telemetry capture tool
- **Usage:** `python3 test_telemetry_simple.py [uart_port]`

---

## MSP Tools (msp/)

### Benchmark (msp/benchmark/)

Performance testing tools for MSP protocol:

- **msp_benchmark.py** - Basic MSP benchmark
- **msp_benchmark_improved.py** - Enhanced benchmark with stats
- **msp_benchmark_ident_only.py** - MSP_IDENT only benchmark
- **msp_benchmark_serial.py** - Serial-specific benchmarking
- **test_mock_benchmark.sh** - Mock responder benchmark test
- **run_comparison_test.sh** - Comparison test runner

### Mock (msp/mock/)

Mock responders for testing MSP clients:

- **msp_mock_responder.py** - TCP mock responder
- **msp_mock_responder_tcp.py** - TCP-specific mock

### Debug (msp/debug/)

MSP debugging utilities:

- **msp_debug.py** - General MSP protocol debugging
- **msp_rc_debug.py** - MSP RC command debugging

---

## GPS Tools (gps/)

### Current Tools

**gps_test_v6.py** - Latest GPS testing tool
- Most recent version of GPS test suite
- Comprehensive GPS functionality testing

**gps_rth_test.py** - Return-to-home testing
- Tests RTH behavior and GPS recovery
- Configurable GPS loss scenarios

**gps_rth_bug_test.py** - RTH bug reproduction
- Reproduces specific RTH bugs for verification
- Documents bug behavior

**gps_recovery_test.py** - GPS recovery testing
- Tests GPS signal recovery scenarios
- Validates failsafe behavior

**inject_gps_altitude.py** - GPS altitude injection
- Injects GPS altitude data into SITL
- For altitude-specific testing

**simulate_altitude_motion.py** - Altitude motion simulator
- Simulates realistic altitude changes
- Tests altitude hold and climbing

**test_motion_simulator.sh** - Motion simulation test wrapper
- Automated motion simulation tests

### Historical (gps/historical/)

Archived older versions for reference:
- gps_test_v1.py through gps_test_v5.py

### Test Results (gps/test_results/)

Archived test output logs from GPS bug testing:
- buggy_*.log - Test results showing bug behavior
- fixed_test.log - Test results after fixes

---

## SITL Tools (sitl/)

**sitl_arm_test.py** - SITL arming test
- Tests FC arming via MSP
- Verifies arming conditions

**unavlib_bug_test.py** - uNAVlib bug testing
- Tests for uNAVlib library issues

---

## Documentation (docs/)

**README.md** - This file

**BUILDING_SITL.md** - SITL build instructions
- How to build SITL with CRSF support
- Troubleshooting build issues

**TCP_CONNECTION_LIMITATION.md** - TCP limitations in SITL
- Documents TCP connection constraints
- Workarounds for testing

**UNAVLIB.md** - uNAVlib documentation
- Python MSP library documentation
- API reference

**2025-11-25-test-instructions.md** - Historical test instructions

---

## Other Tools

**usb_throughput_test.py** - USB performance testing
- Tests USB serial throughput
- Benchmarks communication speed

---

## Usage Examples

### CRSF Telemetry Testing

```bash
# Full test with PR #11025 changes
cd ~/Documents/planes/inavflight/claude/test_tools/inav/crsf
./test_crsf_telemetry.sh build_sitl_pr11025 pr11025

# Quick rebuild and test
./quick_test_crsf.sh -r

# Manual testing with tools
python3 crsf_rc_sender.py 2 --rate 50 &  # Keep FC armed
python3 crsf_stream_parser.py 2           # Watch telemetry
```

### MSP Benchmarking

```bash
cd ~/Documents/planes/inavflight/claude/test_tools/inav/msp/benchmark
python3 msp_benchmark_improved.py
./run_comparison_test.sh
```

### GPS Testing

```bash
cd ~/Documents/planes/inavflight/claude/test_tools/inav/gps
python3 gps_test_v6.py
python3 gps_rth_test.py --loss-duration 5.0
```

---

## Migration Notes

**2025-12-07:** Consolidated test tools from two locations:
- Moved from `claude/developer/test_tools/` → `claude/test_tools/inav/`
- Organized into functional subdirectories
- Fixed cross-directory dependencies
- Archived historical versions

**Benefits:**
- Single source of truth for all INAV test tools
- Clear organization by functional area
- No cross-directory dependencies
- Role-agnostic (accessible to all roles)
- Easier discovery and maintenance

---

## Contributing

When adding new test tools:

1. **Choose the right directory:**
   - CRSF-related → `crsf/`
   - MSP-related → `msp/benchmark/`, `msp/mock/`, or `msp/debug/`
   - GPS/navigation → `gps/`
   - SITL-specific → `sitl/`
   - Documentation → `docs/`

2. **Make tools executable:**
   ```bash
   chmod +x your_tool.py
   chmod +x your_script.sh
   ```

3. **Update this README** with tool description and usage

4. **Use relative paths** when referencing other tools in the same tree

---

## Related Documentation

- Developer Guide: `claude/developer/README.md`
- CRSF Testing Status: `claude/developer/2025-12-07-crsf-telemetry-testing-status.md`
- Test Infrastructure: `claude/test_tools/inav/docs/`

---

**Maintained by:** INAV Development Team
**Location:** `claude/test_tools/inav/`
