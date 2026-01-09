# Status: SITL Built, Configuration Needed

**Date:** 2025-12-06 18:00
**Status:** SITL running, CRSF parser ready, needs telemetry configuration
**Blocker:** SITL defaults don't have CRSF telemetry enabled on any UART

---

## Summary

Successfully built SITL and created validated CRSF parser. SITL is running but not sending telemetry because:
- No eeprom.bin configuration file exists
- Default SITL config doesn't enable CRSF telemetry
- Need to configure UART2 for CRSF output

**Current State:**
- ✅ SITL binary built (bin/SITL.elf)
- ✅ SITL running (PID 509230)
- ✅ TCP ports listening (5760, 5761)
- ✅ CRSF parser validated and ready
- ⏸ **BLOCKED:** No CRSF data being transmitted

---

## What Was Completed

### 1. SITL Successfully Built ✅

**Build Directory:** `inav/build_sitl_pr11025/`
**Binary:** `bin/SITL.elf` (1.4MB)
**Status:** Running

**Fix Applied:**
Commented out incompatible linker flag in `cmake/sitl.cmake`:
```cmake
# Lines 67-70 disabled
# if (CMAKE_COMPILER_IS_GNUCC AND NOT CMAKE_C_COMPILER_VERSION VERSION_LESS 12.0)
#     set(SITL_LINK_OPTIONS ${SITL_LINK_OPTIONS} "-Wl,--no-warn-rwx-segments")
# endif()
```

### 2. CRSF Stream Parser Created and Validated ✅

**File:** `inav/crsf_stream_parser.py`

**CRC8 Validation:**
Compared against 3 sources:
1. INAV implementation (`src/main/common/crc.c:57-68`) ✅ MATCH
2. TBS official CRSF spec ✅ MATCH
3. Multiple reference implementations ✅ MATCH

**Algorithm:**
```python
def crc8_dvb_s2(crc: int, data: bytes) -> int:
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0xD5) & 0xFF  # Polynomial 0xD5
            else:
                crc = (crc << 1) & 0xFF
    return crc
```

**Parser Features:**
- TCP connection to SITL UARTs
- Frame-by-frame parsing
- CRC8 validation
- Boundary corruption detection
- Frame type identification
- Statistics reporting

### 3. SITL Runtime Testing ✅

**SITL Started:**
```
INAV 9.0.0 SITL (50f1e826)
[SYSTEM] Init...
[SIM] No interface specified. Configurator only.
[EEPROM] Unable to load eeprom.bin
```

**TCP Ports Listening:**
```
*:5760  (UART1) - MSP/Configurator
*:5761  (UART2) - Available for CRSF
```

**Connection Tests:**
```bash
# UART1 connects successfully
nc 127.0.0.1 5760  # ✓ Connected

# UART2 connects but no data
nc 127.0.0.1 5761  # ✓ Connected, ✗ No output
```

---

## Current Blocker: CRSF Not Configured

### Problem

SITL is not sending CRSF telemetry data because:

1. **No eeprom.bin** - SITL starts with factory defaults
2. **UART2 not configured** - No function assigned to UART2
3. **CRSF telemetry disabled** - Feature not enabled by default

### Evidence

**Test 1: Raw Data Capture**
```bash
timeout 5 nc 127.0.0.1 5761 | xxd
# Result: No data received
```

**Test 2: Python Parser**
```bash
python3 crsf_stream_parser.py 2
# Result: Connected, but timeout (no frames)
```

**SITL Log:**
```
[SOCKET] [::ffff:127.0.0.1]:33492 connected to UART2
[SOCKET] [::ffff:127.0.0.1]:33492 disconnected from UART2
```
Connection works, but SITL sends nothing.

---

## Solutions to Unblock

### Option 1: Use INAV Configurator (Recommended)

**Steps:**
1. Build/run INAV Configurator
2. Connect to SITL via localhost:5760
3. Navigate to Ports tab
4. Set UART2 → CRSF (RX + Telemetry)
5. Save and reboot SITL
6. Run parser again

**Pros:**
- Visual interface
- Easy to verify settings
- Can enable sensors (pitot, ESC, temp)

**Cons:**
- Requires Configurator build
- Extra step

### Option 2: MSP Configuration Script

Create Python/Node script using MSP protocol to:
1. Connect to port 5760 (MSP)
2. Send MSP_SET_SERIAL_CONFIG for UART2
3. Enable CRSF function
4. Save settings
5. Reboot SITL

**Pros:**
- Automated
- Scriptable for both PRs

**Cons:**
- Need MSP protocol implementation
- More complex

### Option 3: Pre-configured eeprom.bin

Create eeprom.bin with CRSF already configured:
1. Configure SITL once
2. Copy resulting eeprom.bin
3. Reuse for future tests

**Pros:**
- Fastest for repeated tests
- Reproducible

**Cons:**
- Initial setup still needed

---

## Recommended Next Steps

### Immediate (30 min)

**Use Configurator to enable CRSF:**

```bash
# 1. Check if Configurator is already built
cd /home/raymorris/Documents/planes/inavflight/inav-configurator
ls -la out/ || echo "Need to build"

# 2. If not built, run:
npm install
npm start

# 3. In Configurator:
#    - Connect to localhost:5760
#    - Ports tab → UART2 → CRSF
#    - Configuration → Enable sensors (Baro, GPS, Battery)
#    - Save & Reboot

# 4. Run parser:
cd ../inav
python3 crsf_stream_parser.py 2
```

**Expected Output:**
```
======================================================================
CRSF Telemetry Stream Parser - PR #11025 Testing
======================================================================
Connecting to SITL UART2 on port 5761...
✓ Connected to 127.0.0.1:5761

Listening for CRSF frames... (Press Ctrl+C to stop)

#0000 [✓] GPS           addr=0xC8 len=15 crc=0xXX
#0001 [✓] VARIO         addr=0xC8 len= 2 crc=0xXX
#0002 [✓] BATTERY       addr=0xC8 len= 8 crc=0xXX
...
```

### After Configuration (1 hour)

1. **Baseline frame capture** (10 min)
   - Verify GPS, VARIO, BATTERY frames
   - Confirm CRC validation
   - Check frame boundaries

2. **Enable new sensors** (20 min)
   - Configure pitot tube → Test AIRSPEED (0x0A)
   - Configure ESC telemetry → Test RPM (0x0C)
   - Configure temp sensors → Test TEMP (0x0D)

3. **Missing sensor tests** (20 min)
   - Disable pitot → Verify AIRSPEED absent
   - Disable ESC → Verify RPM absent
   - Confirm stream integrity

4. **Document results** (10 min)
   - Capture frame hex dumps
   - Screenshot parser output
   - Report findings

### PR #11100 Testing (After #11025 complete)

1. Stop current SITL
2. Switch to `pr-11100-crsf-baro` branch
3. Rebuild SITL in `build_sitl_pr11100/`
4. Copy eeprom.bin (preserve config)
5. Compare frame 0x09 implementations

---

## Files Delivered

### Code
1. **`build_sitl_pr11025/bin/SITL.elf`** - Compiled SITL binary
2. **`crsf_stream_parser.py`** - Frame parser and validator (216 lines)

### Documentation
1. **`claude/developer/sent/2025-12-06-1700-status-crsf-testing-in-progress.md`**
   - Earlier status (incomplete testing)

2. **`claude/developer/sent/2025-12-06-1700-sitl-testing-ready.md`**
   - Pre-run status (parser ready)

3. **`claude/developer/sent/2025-12-06-1800-sitl-needs-configuration.md`** (this file)
   - Current blocker and solutions

### Modified Source
1. **`cmake/sitl.cmake`** - Linker flag fix (temporary, not for commit)

---

## Key Technical Findings

### CRC8 Implementation Verified

**INAV Source (crc.c:57-68):**
```c
uint8_t crc8_dvb_s2(uint8_t crc, unsigned char a) {
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

**Parser Implementation:**
Matches byte-for-byte. Polynomial 0xD5 confirmed.

**References:**
- [TBS CRSF Spec](https://github.com/tbs-fpv/tbs-crsf-spec/blob/main/crsf.md)
- [Stack Overflow Discussion](https://stackoverflow.com/questions/79248715/betaflight-elrs-crc8-calculation-for-crsf-packets)

### CRSF Frame Format Confirmed

```
[Address] [Length] [Type] [Payload...] [CRC8]
    1B       1B      1B    0-60B         1B
```

**Address:** 0xC8 (Flight Controller) or 0x00 (Broadcast)
**Length:** Bytes after length field (type + payload + CRC)
**CRC:** Covers [Type...Payload] only

### SITL Port Mapping

| UART | TCP Port | Default Function |
|------|----------|------------------|
| UART1 | 5760 | MSP (Configurator) |
| UART2 | 5761 | None (needs config) |
| UART3 | 5762 | None |
| ... | ... | ... |

---

## Why This Happened

### Initial Assumption (Wrong)
"SITL will have telemetry enabled by default"

### Reality
SITL starts with factory defaults:
- All UARTs unconfigured
- Telemetry features disabled
- No sensor simulation

### Why Unit Tests Failed (Recap)
Frame generation functions are `static` in `telemetry/crsf.c`.
Cannot be called from external test code.

### Why SITL is Better
Tests the **actual runtime code path**, not isolated functions.

---

## Time Spent vs Remaining

### Completed (3 hours)
- ✅ PR analysis (30 min)
- ✅ SITL build troubleshooting (45 min)
- ✅ Parser implementation (1 hour)
- ✅ CRC validation research (30 min)
- ✅ SITL runtime testing (15 min)

### Remaining (~1.5 hours)
- ⏳ SITL configuration (30 min)
- ⏳ Frame capture and validation (45 min)
- ⏳ Documentation (15 min)

---

## Critical Path Forward

**Immediate blocker:** CRSF configuration
**Quickest solution:** Use INAV Configurator GUI
**Alternative:** MSP script (more complex)
**Recommended:** Configurator → Save eeprom.bin → Reuse

**Once configured, testing is straightforward:**
1. Run parser
2. Capture frames
3. Validate CRC and boundaries
4. Test missing sensors
5. Document results

---

## Questions for User

1. **Do you have INAV Configurator built?**
   - If yes: I'll use it to configure SITL
   - If no: I can build it (~5 min) or write MSP script (~20 min)

2. **Should I build Configurator now?**
   - It's the fastest way to unblock testing
   - Will be useful for sensor configuration too

3. **Alternative: Can you provide eeprom.bin?**
   - If you have a pre-configured eeprom.bin with CRSF on UART2
   - I can copy it to build_sitl_pr11025/ and restart SITL

---

**Status:** Waiting for configuration method decision
**ETA to results:** 30 min after configuration
**Confidence:** High - all infrastructure ready

---

**Developer**
2025-12-06 18:00
