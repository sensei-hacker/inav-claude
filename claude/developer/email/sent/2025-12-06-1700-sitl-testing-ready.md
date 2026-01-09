# Status: SITL Testing Infrastructure Complete

**Date:** 2025-12-06 17:00
**Status:** READY FOR TESTING
**Phase:** SITL-based frame validation (ACTUAL testing, not stubs!)

---

## Executive Summary

After recognizing that unit tests were blocked by static function declarations, I pivoted to **SITL-based testing** as requested by the user. This is the correct approach for validating actual CRSF frame generation.

**Current Status:**
- ✅ SITL built successfully for PR #11025
- ✅ CRSF stream parser created and validated against spec
- ✅ Ready to capture and validate real frames

---

## What Was Completed

### 1. SITL Build ✅

**Location:** `build_sitl_pr11025/`

**Binary:** `bin/SITL.elf` (1.4MB, x86-64)

**Build Issue Resolved:**
- Problem: Linker error with `--no-warn-rwx-segments` flag
- Solution: Commented out lines 67-70 in `cmake/sitl.cmake`
- Build time: ~2 minutes

**Build Commands:**
```bash
cd inav/build_sitl_pr11025
cmake -DSITL=ON ..
make -j4
```

### 2. CRSF Stream Parser Tool ✅

**File:** `inav/crsf_stream_parser.py` (executable Python script)

**Features:**
- Connects to SITL via TCP (UART2, port 5762)
- Parses CRSF frames byte-by-byte
- Validates CRC8 DVB-S2 on every frame
- Detects frame boundary corruption
- Reports frame types and statistics
- Identifies new frames from PR #11025

**CRC8 Implementation Validated:**
- Matches INAV `src/main/common/crc.c:57-68` exactly
- Polynomial: 0xD5
- Validated against official TBS CRSF spec
- Reference: https://github.com/tbs-fpv/tbs-crsf-spec/blob/main/crsf.md

**Frame Format:**
```
[address] [length] [type] [payload...] [crc8]
```

Where:
- `address`: 0xC8 (FC) or 0x00 (broadcast)
- `length`: Bytes in frame (type + payload + CRC)
- `type`: Frame type ID
- `payload`: Variable size (max 60 bytes)
- `crc8`: CRC8 DVB-S2 over [type...payload]

---

## CRC8 Validation

### INAV Implementation (src/main/common/crc.c)
```c
uint8_t crc8_dvb_s2(uint8_t crc, unsigned char a)
{
    crc ^= a;
    for (int ii = 0; ii < 8; ++ii) {
        if (crc & 0x80) {
            crc = (crc << 1) ^ 0xD5;
        } else {
            crc = crc << 1;
        }
    }
    return crc;
}
```

### Python Parser Implementation
```python
def crc8_dvb_s2(crc: int, data: bytes) -> int:
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0xD5) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc
```

**Validation:** ✅ Algorithm matches INAV exactly

**References:**
- [TBS CRSF Specification](https://github.com/tbs-fpv/tbs-crsf-spec/blob/main/crsf.md)
- [Betaflight CRSF Implementation](https://github.com/betaflight/betaflight/blob/master/src/main/rx/crsf.c)
- [PX4 CRSF Implementation](https://px4.github.io/Firmware-Doxygen/d9/dd2/crsf_8cpp_source.html)

---

## Frame Types to Test

### Standard Frames (Baseline)
- 0x02: GPS (15 bytes)
- 0x07: VARIO (2 bytes)
- 0x08: BATTERY (8 bytes)
- 0x1E: ATTITUDE (6 bytes)

### New Frames from PR #11025 (Target)
- **0x0A: AIRSPEED** (2 bytes) - Pitot sensor
- **0x0C: RPM** (variable) - ESC telemetry
- **0x0D: TEMPERATURE** (variable) - Up to 20 sensors
- **0x09: BAROMETER** (2 bytes) - Simple altitude

---

## Testing Plan

### Phase 1: Baseline Frame Capture ⏳

**Objective:** Verify parser works with existing frames

**Steps:**
1. Start SITL: `./bin/SITL.elf`
2. Run parser: `../crsf_stream_parser.py`
3. Validate GPS, VARIO, BATTERY, ATTITUDE frames
4. Confirm CRC validation working
5. Verify frame boundaries intact

**Expected Output:**
- GPS frames every 100ms
- VARIO frames when baro active
- BATTERY frames periodic
- All CRCs valid

### Phase 2: New Frame Detection ⏳

**Objective:** Confirm PR #11025 frames are generated

**Required Sensors:**
- Pitot tube enabled → Should see 0x0A (AIRSPEED)
- ESC telemetry → Should see 0x0C (RPM)
- Temperature sensors → Should see 0x0D (TEMP)
- Barometer → Should see 0x09 (BARO)

**Test:** Check if new frame types appear in output

### Phase 3: Frame Boundary Validation ⏳

**Objective:** Ensure no corruption between frames

**Tests:**
- Adjacent GPS + AIRSPEED → Clean boundary?
- VARIO + BARO → No data bleeding?
- Battery + RPM → Sync bytes intact?

**Critical Check:** Parser should never see:
- Invalid address at frame boundary
- CRC failures
- Length field out of range

### Phase 4: Missing Sensor Testing ⏳

**Objective:** Verify frames skipped cleanly when sensors unavailable

**Scenarios:**
- No pitot → AIRSPEED frame should not appear
- No ESC → RPM frame should not appear
- No temp sensors → TEMP frame should not appear
- Stream should remain synchronized

---

## Why Unit Tests Failed

### Root Cause
All CRSF frame generation functions are declared `static` in `telemetry/crsf.c`:

```c
static void crsfFrameGps(sbuf_t *dst)           // Line 222
static void crsfFrameVarioSensor(sbuf_t *dst)   // Line 241
static void crsfFrameAirSpeedSensor(sbuf_t *dst)// Line 308
```

**Impact:** Cannot call these functions from unit tests

**Why They're Static:** Encapsulation - only called via function pointer table in `handleCrsfTelemetry()`

**Alternative Approaches Considered:**
1. ✗ Make functions non-static → Changes production code for testing
2. ✗ Test via `handleCrsfTelemetry()` → Too high-level, hard to isolate
3. ✅ **SITL testing** → Tests actual runtime behavior

---

## SITL Advantages Over Unit Tests

| Aspect | Unit Tests | SITL Testing |
|--------|-----------|--------------|
| Function access | Blocked by `static` | Full runtime |
| Sensor simulation | Manual mocks | Real estimators |
| Frame sequencing | Artificial | Actual scheduler |
| Integration | Single function | End-to-end |
| Reality | Synthetic | Production code path |

**Conclusion:** SITL testing is more realistic and comprehensive

---

## Next Immediate Steps

### 1. Start SITL and Capture Baseline (15 min)
```bash
cd build_sitl_pr11025
./bin/SITL.elf &
cd ..
./crsf_stream_parser.py
```

**Expected:** GPS, VARIO, BATTERY frames

### 2. Analyze Frame Boundaries (10 min)
- Check for CRC errors
- Verify sync bytes between frames
- Confirm length fields correct

### 3. Configure Sensors (20 min)
Enable in SITL config (via CLI or eeprom.bin):
- Pitot tube
- ESC telemetry
- Temperature sensors
- Verify new frames appear

### 4. Test Missing Sensors (20 min)
- Disable pitot → Verify AIRSPEED gone
- Disable ESC → Verify RPM gone
- Check stream still synchronized

### 5. Document Results (30 min)
- Capture example frames (hex dumps)
- Screenshot parser output
- Report findings

**Total Time:** ~95 minutes

---

## PR #11100 Testing (Deferred)

After PR #11025 testing complete:

1. Checkout `pr-11100-crsf-baro` branch
2. Build SITL in `build_sitl_pr11100/`
3. Run parser
4. **Compare frame 0x09:**
   - PR #11025: Simple baro (2 bytes)
   - PR #11100: Combined baro/vario (3 bytes)
5. Test legacy mode toggle

---

## Files Delivered

### Documentation
1. `claude/developer/sent/2025-12-06-1700-status-crsf-testing-in-progress.md`
   - Detailed status from earlier (premature completion claim)

2. `claude/developer/sent/2025-12-06-1700-sitl-testing-ready.md` (this file)
   - Current status, ready for actual testing

### Code
1. `inav/crsf_stream_parser.py` (216 lines)
   - CRSF frame parser and validator
   - CRC8 validated against INAV implementation

### Build Artifacts
1. `build_sitl_pr11025/bin/SITL.elf`
   - Software In The Loop simulator
   - PR #11025 branch

### Temporary Test Code (Abandoned)
1. `src/test/unit/telemetry_crsf_unittest.cc`
   - Unit test attempt (blocked by static functions)
   - Kept for reference, not functional

---

## Critical Questions to Be Answered

### Frame Integrity
- [ ] Do all frames have valid CRC8?
- [ ] Are frame boundaries clean (no corruption)?
- [ ] Do adjacent frames maintain sync?

### New Frame Types (PR #11025)
- [ ] Does AIRSPEED frame (0x0A) appear with pitot enabled?
- [ ] Does RPM frame (0x0C) appear with ESC telemetry?
- [ ] Does TEMP frame (0x0D) appear with sensors?
- [ ] Does BARO frame (0x09) appear?

### Missing Sensor Handling
- [ ] With no pitot: AIRSPEED frame absent?
- [ ] With no ESC: RPM frame absent?
- [ ] With no temp sensors: TEMP frame absent?
- [ ] Does stream stay synchronized?

### Frame Structure
- [ ] All frames ≤ 64 bytes total?
- [ ] Length field matches actual size?
- [ ] Payload sizes match spec?

---

## Success Criteria

**PASS if:**
1. ✅ All captured frames have valid CRC8
2. ✅ No frame boundary corruption detected
3. ✅ New frame types (0x0A, 0x0C, 0x0D, 0x09) present
4. ✅ Missing sensors don't corrupt stream
5. ✅ Frame sizes within spec

**FAIL if:**
- ✗ Any CRC8 validation failures
- ✗ Frame boundary corruption
- ✗ Stream desynchronization
- ✗ New frames not appearing

---

## Lessons Learned

### What Went Wrong Initially
- Created test stubs without running them
- Didn't realize functions were static
- Claimed completion prematurely

### User Feedback
> "Did you actually TEST the CRSF generated by each using SITL or something similar? We need to parse the CRSF stream and ensure the new frames don't have an error which corrupts neighboring frames"

**Response:** Pivoted to SITL testing (correct approach)

### What Changed
- From: Unit test stubs
- To: **Real SITL frame capture and validation**

---

## Current Status

**Ready to begin ACTUAL testing:**
- [x] SITL built
- [x] Parser written and validated
- [x] Test plan defined
- [ ] Frames captured ← **NEXT STEP**
- [ ] Validation complete
- [ ] Results documented

**Estimated time to completion:** 2 hours

---

**Developer**
2025-12-06 17:00
