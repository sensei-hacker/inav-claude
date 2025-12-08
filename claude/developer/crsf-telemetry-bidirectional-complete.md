# CRSF Telemetry Bidirectional Testing - Complete

**Date:** 2025-12-07
**Status:** ✅ COMPLETED

---

## Summary

Successfully implemented bidirectional CRSF RC/telemetry testing for INAV SITL. The updated `crsf_rc_sender.py` script now handles both sending RC frames and receiving telemetry responses on the same TCP connection, matching real-world CRSF hardware behavior.

---

## Key Achievements

### 1. Identified TCP Connection Limitation

**Problem:** Attempted to use separate scripts for RC transmission and telemetry reception, which failed because TCP ports accept only ONE client connection.

**Discovery:** CRSF is inherently bidirectional - the transmitter and flight controller communicate over a single wire/connection.

**Documentation:** Created `TCP_CONNECTION_LIMITATION.md` explaining why two separate scripts cannot connect simultaneously.

### 2. Implemented Bidirectional Script

**Updated:** `claude/developer/test_tools/crsf_rc_sender.py`

**New Features:**
- Uses `select()` for non-blocking I/O
- Sends RC frames at configurable rate (default 50Hz)
- Reads and parses telemetry frames on same connection
- Counts telemetry by frame type (ATTITUDE, BATTERY, FLIGHT_MODE, etc.)
- Optional `--show-telemetry` flag for real-time frame display
- Comprehensive summary statistics

**Test Results:**
```
RC Frames Sent: 500 in 10.0 seconds (50.0 Hz avg)
Telemetry Received: 534 frames

Telemetry Frame Breakdown:
  ATTITUDE       :   90 frames
  BATTERY        :   89 frames
  FLIGHT_MODE    :   89 frames
  VARIO          :   89 frames
  UNKNOWN_0x09   :   88 frames
  UNKNOWN_0x0D   :   89 frames
```

### 3. Updated Documentation

**Updated Skills:**
- `.claude/skills/test-crsf-sitl/SKILL.md` - Complete rewrite of Step 3 and 4
  - Documents bidirectional approach
  - Shows new script options and expected output
  - Adds troubleshooting for "Connection Refused" error
  - Updates file locations and quick reference commands

**Cross-References Added:**
- `.claude/skills/build-sitl/SKILL.md` - Added "Related Skills" section
- `.claude/skills/sitl-arm/SKILL.md` - Added "Related Skills" section

**New Documentation:**
- `claude/developer/test_tools/TCP_CONNECTION_LIMITATION.md` - Comprehensive explanation of TCP constraints and solution

---

## Files Created/Modified

### New Files
```
claude/developer/test_tools/TCP_CONNECTION_LIMITATION.md
claude/developer/crsf-telemetry-bidirectional-complete.md (this file)
```

### Modified Files
```
claude/developer/test_tools/crsf_rc_sender.py
  - Added bidirectional I/O with select()
  - Added telemetry parsing and counting
  - Added --show-telemetry flag
  - Updated documentation header

.claude/skills/test-crsf-sitl/SKILL.md
  - Updated Step 3: Test CRSF RC and Telemetry (Bidirectional)
  - Updated Step 4: Verify Telemetry Output
  - Added troubleshooting section for TCP connection issues
  - Updated file locations
  - Updated quick reference commands

.claude/skills/build-sitl/SKILL.md
  - Added "Related Skills" section

.claude/skills/sitl-arm/SKILL.md
  - Added "Related Skills" section
```

---

## Technical Details

### TCP Connection Architecture

**Before (Broken):**
```
SITL Port 5761 <--- RC Sender Script
                <--- Telemetry Reader Script  ❌ Connection Refused
```

**After (Working):**
```
SITL Port 5761 <---> crsf_rc_sender.py (Bidirectional)
                     - Sends RC frames
                     - Receives telemetry frames
```

### CRSF Frame Types Identified

| Type | Name | Description |
|------|------|-------------|
| 0x07 | VARIO | Variometer data |
| 0x08 | BATTERY | Battery voltage/current |
| 0x09 | UNKNOWN | Barometer (frame type 0x09) |
| 0x0D | UNKNOWN | Unknown telemetry type |
| 0x1E | ATTITUDE | Roll/pitch/yaw |
| 0x21 | FLIGHT_MODE | Current flight mode string |

---

## Usage Examples

### Basic Testing (Summary Only)
```bash
cd ~/Documents/planes/inavflight/claude/developer/test_tools
python3 crsf_rc_sender.py 2 --rate 50 --duration 30
```

### With Telemetry Display
```bash
cd ~/Documents/planes/inavflight/claude/developer/test_tools
python3 crsf_rc_sender.py 2 --rate 50 --duration 30 --show-telemetry
```

### Continuous (Ctrl+C to stop)
```bash
cd ~/Documents/planes/inavflight/claude/developer/test_tools
python3 crsf_rc_sender.py 2 --rate 50 --show-telemetry
```

---

## Testing Workflow

1. **Build SITL** (use `build-sitl` skill)
   ```bash
   cd ~/Documents/planes/inavflight/inav
   mkdir build_sitl_crsf && cd build_sitl_crsf
   cmake -DSITL=ON .. && make -j$(nproc)
   ```

2. **Start SITL**
   ```bash
   ./bin/SITL.elf 2>&1 | tee /tmp/sitl.log &
   sleep 5
   ```

3. **Configure CRSF** (automated MSP script)
   ```bash
   cd ~/Documents/planes/inavflight/inav
   python3 configure_crsf_proper_sequence.py 5760
   sleep 10  # Wait for reboot
   ```

4. **Test Telemetry** (bidirectional)
   ```bash
   cd ~/Documents/planes/inavflight/claude/developer/test_tools
   python3 crsf_rc_sender.py 2 --rate 50 --duration 30 --show-telemetry
   ```

---

## Lessons Learned

1. **TCP Ports Are Exclusive**
   - Only one client can connect to a TCP server port
   - Must use bidirectional communication on single connection
   - This matches real hardware behavior (CRSF is bidirectional on one wire)

2. **CRSF Protocol Design**
   - RC and telemetry share same physical connection
   - Telemetry timing synchronized with RC reception
   - Flight controller sends telemetry between RC frames

3. **Python socket.select()**
   - Essential for non-blocking I/O with timeout
   - Allows sending RC at precise intervals while reading telemetry
   - Prevents blocking on recv() when no data available

4. **Frame Parsing**
   - CRSF frame structure: [Address][Length][Type][Payload][CRC8]
   - Length field = Type(1) + Payload(N) + CRC(1)
   - Total frame size = Length + 2 (for Address and Length bytes)

---

## Next Steps

**Potential Improvements:**
1. Decode telemetry payloads (GPS coordinates, battery voltage, etc.)
2. Add validation of telemetry values
3. Support variable channel values (not just 1500us midpoint)
4. Add frame rate statistics (telemetry frames per second)
5. Implement CRSF command injection (MSP passthrough, parameter sets)

**Testing:**
1. Test with different PR branches (AIRSPEED, RPM, TEMPERATURE frames)
2. Validate CRC calculations on all frame types
3. Test with external simulators (X-Plane, RealFlight)
4. Long-duration testing (hours) to detect memory leaks or timing drift

---

## References

- CRSF Specification: https://github.com/tbs-fpv/tbs-crsf-spec
- INAV SITL: `inav/docs/SITL/SITL.md`
- CRSF Implementation: `inav/src/main/telemetry/crsf.c`
- RC Reception: `inav/src/main/rx/crsf.c`

---

## Conclusion

The bidirectional CRSF testing solution is now complete and fully functional. This provides a reliable way to test CRSF telemetry changes in SITL without requiring separate RC sender and telemetry reader processes.

The implementation correctly mirrors real-world CRSF hardware behavior where bidirectional communication occurs over a single connection, making it an accurate testing environment for pull request validation.
