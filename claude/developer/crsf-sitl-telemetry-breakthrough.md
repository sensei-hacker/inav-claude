# CRSF Telemetry in SITL - Complete Solution

**Date:** 2025-12-06
**Status:** ✅ SOLVED
**Context:** Testing CRSF telemetry frames from PR #11025

---

## Problem Summary

CRSF telemetry was not working in SITL despite:
- CRSF RX being properly configured
- CRSF RC frames being received successfully
- UART2 listening on port 5761
- Previous configuration via Configurator completing without errors

---

## Root Cause Analysis

SITL disables CRSF telemetry at **TWO separate levels**, both of which must be enabled:

### Level 1: Compile-Time Disable
**File:** `src/main/target/SITL/target.h:97`
**Code:** `#undef USE_TELEMETRY_CRSF`

**Effect:**
- Prevents `initCrsfTelemetry()` from being compiled into the binary
- Removes all CRSF telemetry code from SITL build
- CRSF RX still works (different compilation flag)

**Verification:**
```bash
# Before fix:
nm bin/SITL.elf | grep initCrsfTelemetry
# (no output)

# After fix:
nm bin/SITL.elf | grep initCrsfTelemetry
00000000000d01bb T initCrsfTelemetry
```

### Level 2: Runtime Disable
**File:** `src/main/fc/fc_init.c:608`
**Code:**
```c
#ifdef USE_TELEMETRY
    if (feature(FEATURE_TELEMETRY)) {
        telemetryInit();
    }
#endif
```

**Effect:**
- Even with telemetry compiled, `telemetryInit()` is NEVER called
- FEATURE_TELEMETRY (bit 10 = 0x400) is disabled by default in SITL
- No telemetry initialization occurs at runtime

**Detection:**
Added debug logging showed:
```
# WITHOUT feature flag:
[CRSF INIT] SUCCESS: Serial port opened
(no telemetry messages - telemetryInit() never called)

# WITH feature flag:
[CRSF INIT] SUCCESS: Serial port opened
[TELEMETRY] telemetryInit() called
[CRSF TELEM] initCrsfTelemetry: enabled=1
[CRSF TELEM] Calling crsfRxSendTelemetryData
```

---

## Complete Solution

### Step 1: Enable Compile-Time Support

Edit `src/main/target/SITL/target.h`:

```diff
-#undef USE_TELEMETRY_CRSF
+// #undef USE_TELEMETRY_CRSF  // ENABLED FOR TESTING PR #11025
 #undef USE_TELEMETRY_IBUS
```

### Step 2: Build SITL

```bash
cd /home/raymorris/Documents/planes/inavflight/inav
mkdir build_sitl_pr11025
cd build_sitl_pr11025
cmake -DSITL=ON ..
make -j4
```

### Step 3: Enable Runtime Feature Flag

**Option A: Using Python Script (Automated)**

Created: `/home/raymorris/Documents/planes/inavflight/inav/enable_telemetry_feature.py`

```bash
# Start SITL first
cd /home/raymorris/Documents/planes/inavflight/inav/build_sitl_pr11025
./bin/SITL.elf &

# Enable telemetry feature
cd ../inav
python3 enable_telemetry_feature.py
```

**Script functionality:**
1. Connects to SITL via MSP (TCP:5760)
2. Reads current feature mask via `MSP_FEATURE`
3. Sets bit 10 (FEATURE_TELEMETRY = 0x400)
4. Sends new feature mask via `MSP_SET_FEATURE`
5. Saves to EEPROM via `MSP_EEPROM_WRITE`
6. Reboots SITL via `MSP_REBOOT`

**Example output:**
```
Connecting to SITL...
✓ Connected to SITL
Getting current feature mask...
Current features: 0x20400806
Enabling TELEMETRY feature...
New features: 0x20400C06
Saving to EEPROM...
Rebooting SITL...
✓ TELEMETRY feature enabled. Wait 15 seconds for SITL to restart...
```

**Option B: Using Configurator (Manual)**
1. Connect to SITL (TCP:5760)
2. Configuration tab → Enable "TELEMETRY" checkbox
3. Save and Reboot

---

## Debugging Process

### Tools Used

1. **SD() Debug Macro**
   - File: `src/main/build/debug.h:85-89`
   - Only active in SITL builds
   - Usage: `SD(fprintf(stderr, "[TAG] message\n"))`

2. **Added Debug Logging To:**
   - `src/main/rx/crsf.c` - CRSF RX initialization
   - `src/main/telemetry/crsf.c` - CRSF telemetry init
   - `src/main/telemetry/telemetry.c` - General telemetry init

3. **Binary Analysis:**
   ```bash
   nm bin/SITL.elf | grep -i telemetry
   nm bin/SITL.elf | grep -i crsf
   ```

### Investigation Steps

1. **Initial observation:** No telemetry output despite CRSF RX working
2. **Found:** `initCrsfTelemetry()` exists in binary (compile-time OK)
3. **Discovered:** No `[TELEMETRY]` log messages (runtime problem)
4. **Traced:** `telemetryInit()` called from `fc_init.c:608`
5. **Found:** Guarded by `if (feature(FEATURE_TELEMETRY))`
6. **Solution:** Enable FEATURE_TELEMETRY flag via MSP

---

## Key Files Modified

### Debug Logging Added (Temporary)

**src/main/rx/crsf.c:**
```c
#ifdef SITL_BUILD
#include <stdio.h>
#endif

SD(fprintf(stderr, "[CRSF INIT] crsfInit() called\n"));
SD(fprintf(stderr, "[CRSF INIT] Found port config, identifier=%d\n", portConfig->identifier));
SD(fprintf(stderr, "[CRSF INIT] SUCCESS: Serial port opened\n"));
SD(fprintf(stderr, "[CRSF RX] First byte: 0x%02X\n", c));
```

**src/main/telemetry/crsf.c:**
```c
#ifdef SITL_BUILD
#include <stdio.h>
#endif
#include "build/debug.h"

SD(fprintf(stderr, "[CRSF TELEM] initCrsfTelemetry: enabled=%d\n", crsfTelemetryEnabled));
SD(fprintf(stderr, "[CRSF TELEM] handleCrsfTelemetry called, enabled=%d\n", crsfTelemetryEnabled));
SD(fprintf(stderr, "[CRSF TELEM] Calling crsfRxSendTelemetryData\n"));
```

**src/main/telemetry/telemetry.c:**
```c
#ifdef SITL_BUILD
#include <stdio.h>
#endif

SD(fprintf(stderr, "[TELEMETRY] telemetryInit() called\n"));
SD(fprintf(stderr, "[TELEMETRY] About to call initCrsfTelemetry()\n"));
SD(fprintf(stderr, "[TELEMETRY] initCrsfTelemetry() returned\n"));
```

### Permanent Changes

**src/main/target/SITL/target.h:97**
```c
// #undef USE_TELEMETRY_CRSF  // ENABLED FOR TESTING PR #11025
```

---

## Tools Created

### enable_telemetry_feature.py

**Location:** `/home/raymorris/Documents/planes/inavflight/inav/enable_telemetry_feature.py`

**Purpose:** Automatically enable FEATURE_TELEMETRY in SITL via MSP

**Dependencies:**
- uNAVlib (MSP library)
- Python 3

**Usage:**
```bash
# Ensure SITL is running
python3 enable_telemetry_feature.py
```

**Key Implementation Details:**
- Uses MSPy with context manager: `with MSPy(device="5760", use_tcp=True) as board:`
- Parses raw MSP_FEATURE response from `dataView` field
- Converts 4-byte little-endian feature mask
- Preserves existing features, only sets bit 10

---

## Verification

### Success Indicators

1. **Compile-time verification:**
   ```bash
   nm bin/SITL.elf | grep initCrsfTelemetry
   # Should output: 00000000000d01bb T initCrsfTelemetry
   ```

2. **Runtime verification in logs:**
   ```
   [CRSF INIT] SUCCESS: Serial port opened
   [TELEMETRY] telemetryInit() called
   [TELEMETRY] About to call initCrsfTelemetry()
   [CRSF TELEM] initCrsfTelemetry: enabled=1
   [TELEMETRY] initCrsfTelemetry() returned
   [CRSF TELEM] handleCrsfTelemetry called, enabled=1
   [CRSF TELEM] Calling crsfRxSendTelemetryData
   ```

3. **Feature mask check:**
   - Before: `0x20400806` (bit 10 = 0)
   - After: `0x20400C06` (bit 10 = 1)

---

## Lessons Learned

1. **Dual-level disables are easy to miss**
   - Compile-time flags alone aren't sufficient
   - Runtime feature flags can silently disable functionality

2. **Debug logging is invaluable**
   - SD() macro made SITL debugging straightforward
   - fprintf(stderr) output appears immediately in logs

3. **MSP protocol quirks**
   - MSPy requires context manager (`with` statement)
   - Response data in `dataView` field, not processed attributes
   - Need to parse raw bytes manually

4. **SITL-specific limitations**
   - Many features disabled by default for simplicity
   - Not all real-world configs apply to SITL
   - Documentation often assumes real hardware

---

## Testing Next Steps

With telemetry now functional, can proceed to:

1. Send CRSF RC frames via `crsf_rc_sender.py`
2. Capture telemetry frames via `crsf_stream_parser.py`
3. Validate new frames from PR #11025:
   - 0x09 BAROMETER
   - 0x0A AIRSPEED
   - 0x0C RPM
   - 0x0D TEMPERATURE

---

## References

- Skill: `.claude/skills/test-crsf-sitl/SKILL.md`
- Previous findings: `claude/developer/crsf-sitl-testing-findings.md`
- CRSF spec: https://github.com/tbs-fpv/tbs-crsf-spec
- INAV source:
  - `src/main/telemetry/crsf.c`
  - `src/main/rx/crsf.c`
  - `src/main/fc/fc_init.c`
  - `src/main/target/SITL/target.h`
