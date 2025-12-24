# Superseded Test Scripts Analysis

**Date:** 2025-12-07
**From:** Manager
**Purpose:** Identify obsolete test scripts in `inav/` directory that are superseded by better versions in `claude/test_tools/`

---

## Summary

**14 scripts found in `inav/` root directory**

**Superseded scripts:** 2 scripts have better versions in `claude/test_tools/`
**Development/iteration scripts:** 5 scripts are work-in-progress iterations
**Utility scripts:** 7 scripts are legitimate utilities (keep)

---

## Superseded Scripts (Recommend Removal)

### 1. `inav/test_telemetry_proper_timing.sh` ❌ SUPERSEDED

**Superseded by:** `claude/test_tools/inav/test_crsf_telemetry.sh`

**Analysis:**
- **Old version** (inav/): 66 lines, basic SITL startup and RC sender
- **New version** (claude/test_tools/): 380 lines, comprehensive automated test suite

**New version improvements:**
- ✅ 7-step automated workflow (verification, cleanup, config, testing)
- ✅ Validates SITL binary includes CRSF telemetry symbols (`nm` check)
- ✅ Automatically enables TELEMETRY feature via MSP
- ✅ Configures CRSF on UART2 automatically
- ✅ Mode-specific testing (baseline, pr11025, pr11100)
- ✅ Frame validation with expected frame detection
- ✅ Error detection and detailed failure reporting
- ✅ Cleanup and exit codes for CI integration
- ✅ Usage documentation and examples

**Old version limitations:**
- Manual SITL startup only
- No configuration automation
- No validation or error checking
- No cleanup
- Requires manual telemetry monitoring

**Recommendation:** DELETE `inav/test_telemetry_proper_timing.sh`

---

### 2. `inav/crsf_rc_sender.py` ❌ SUPERSEDED

**Superseded by:** `claude/developer/test_tools/crsf_rc_sender.py`

**Analysis:**
- **Old version** (inav/): 174 lines, send-only
- **New version** (claude/developer/test_tools/): 546 lines, bidirectional with validation

**New version improvements:**
- ✅ **Bidirectional communication** - sends RC frames AND receives telemetry
- ✅ **EdgeTX-compatible error detection** - CRC8 validation, frame structure checks
- ✅ **Connection retry logic** - auto-retry for up to 30s (handles SITL boot timing)
- ✅ **Telemetry frame parsing** - counts and validates all telemetry frame types
- ✅ **Error statistics** - tracks CRC errors, framing errors, buffer overflows
- ✅ **Stream health indicator** - EXCELLENT/GOOD/FAIR/POOR based on error rate
- ✅ **Frame validation** - LENGTH_TOO_SHORT, CRC_MISMATCH, FRAME_TOO_LARGE, etc.
- ✅ **Buffer overflow protection** - prevents unbounded memory growth
- ✅ **Sync recovery** - resynchronizes on stream corruption
- ✅ **Detailed documentation** - comprehensive usage examples and error types

**Old version limitations:**
- Send-only (no telemetry reception)
- No error detection
- No connection retry
- No validation
- No health monitoring
- Simple timeout on connection failure

**Recommendation:** DELETE `inav/crsf_rc_sender.py`

---

## Development/Iteration Scripts (Recommend Removal)

These are intermediate development versions that were superseded during testing iterations:

### 3. `inav/configure_crsf_complete.py` ⚠️ DEVELOPMENT ITERATION
- 6.0K, Dec 7 08:33
- Likely iteration of `configure_sitl_crsf.py`
- **Recommend:** DELETE (use `configure_sitl_crsf.py` instead)

### 4. `inav/configure_crsf_proper_sequence.py` ⚠️ DEVELOPMENT ITERATION
- 5.0K, Dec 7 09:24
- Another iteration attempting to fix sequence issues
- **Recommend:** DELETE (use `configure_sitl_crsf.py` instead)

### 5. `inav/setup_crsf_step_by_step.py` ⚠️ DEVELOPMENT ITERATION
- 4.0K, Dec 7 08:46
- Yet another iteration of CRSF setup
- **Recommend:** DELETE (use `configure_sitl_crsf.py` instead)

### 6. `inav/enable_telemetry_feature.py` ⚠️ DEVELOPMENT ITERATION
- 2.2K, Dec 6 20:39
- Subset functionality now in `test_crsf_telemetry.sh`
- **Recommend:** DELETE (integrated into main test script)

### 7. `inav/capture_frames.py` ⚠️ DEVELOPMENT ITERATION
- 2.5K, Dec 6 21:24
- Likely superseded by `crsf_rc_sender.py --show-telemetry`
- **Recommend:** DELETE (functionality in newer script)

---

## Legitimate Utility Scripts (Keep)

### 8. `inav/configure_sitl_crsf.py` ✅ MOVED
- **Purpose:** Configure CRSF on UART2 via MSP
- **Used by:** `claude/test_tools/inav/test_crsf_telemetry.sh` (line 163)
- **Status:** Moved to `claude/test_tools/inav/configure_sitl_crsf.py`
- **Recommendation:** MOVED (2025-12-07)

### 9. `inav/crsf_stream_parser.py` ✅ KEEP (Duplicate exists)
- **Purpose:** Parse and validate CRSF telemetry stream
- **Duplicate:** `claude/developer/test_tools/crsf_stream_parser.py` (identical, 227 lines)
- **Status:** Used for manual telemetry inspection
- **Recommendation:** KEEP one copy (either location), or keep both if used by different scripts

### 10. `inav/build.sh` ✅ KEEP
- **Purpose:** Standard INAV firmware build wrapper
- **Status:** Core utility script
- **Recommendation:** KEEP

### 11. `inav/build_docs.sh` ✅ KEEP
- **Purpose:** Build documentation
- **Status:** Core utility script
- **Recommendation:** KEEP

### 12. `inav/check_max_output_ports.sh` ✅ KEEP
- **Purpose:** Utility to check max output ports
- **Status:** Utility script
- **Recommendation:** KEEP

### 13. `inav/closest.sh` ✅ KEEP
- **Purpose:** Utility script (purpose unclear, but small and harmless)
- **Status:** Utility script
- **Recommendation:** KEEP

### 14. `inav/fake_travis_build.sh` ✅ KEEP
- **Purpose:** CI/CD testing utility
- **Status:** Utility script
- **Recommendation:** KEEP

---

## Recommendations Summary

### DELETE (7 scripts):
1. ❌ `inav/test_telemetry_proper_timing.sh` - Superseded by comprehensive test script
2. ❌ `inav/crsf_rc_sender.py` - Superseded by bidirectional version with error detection
3. ❌ `inav/configure_crsf_complete.py` - Development iteration
4. ❌ `inav/configure_crsf_proper_sequence.py` - Development iteration
5. ❌ `inav/setup_crsf_step_by_step.py` - Development iteration
6. ❌ `inav/enable_telemetry_feature.py` - Functionality integrated into test script
7. ❌ `inav/capture_frames.py` - Superseded by `crsf_rc_sender.py --show-telemetry`

### KEEP (7 scripts):
1. ✅ `inav/configure_sitl_crsf.py` - Active utility, used by test scripts
2. ✅ `inav/crsf_stream_parser.py` - Utility (note: duplicate exists in claude/developer/test_tools/)
3. ✅ `inav/build.sh` - Core build utility
4. ✅ `inav/build_docs.sh` - Documentation utility
5. ✅ `inav/check_max_output_ports.sh` - Utility
6. ✅ `inav/closest.sh` - Utility
7. ✅ `inav/fake_travis_build.sh` - CI utility

---

## Cleanup Command

```bash
# Remove superseded scripts
cd ~/Documents/planes/inavflight/inav
rm -f test_telemetry_proper_timing.sh
rm -f crsf_rc_sender.py
rm -f configure_crsf_complete.py
rm -f configure_crsf_proper_sequence.py
rm -f setup_crsf_step_by_step.py
rm -f enable_telemetry_feature.py
rm -f capture_frames.py

# Total disk space saved: ~31KB
```

---

## Additional Notes

### Duplicate Files

**`crsf_stream_parser.py` exists in TWO locations:**
- `inav/crsf_stream_parser.py` (227 lines)
- `claude/developer/test_tools/crsf_stream_parser.py` (227 lines, identical)

**Recommendation:** Keep `claude/developer/test_tools/crsf_stream_parser.py` (organized with other test tools), optionally delete `inav/crsf_stream_parser.py` to avoid confusion.

### Better Versions Location

All improved test scripts are now organized in:
- `claude/test_tools/inav/` - Main test scripts and utilities
- `claude/developer/test_tools/` - Developer-specific test utilities

This organization keeps the `inav/` root clean and separates testing infrastructure from firmware source code.

---

## CLEANUP COMPLETED - 2025-12-07 12:13

**Actions Taken:**
- ✅ Moved 7 superseded scripts to `claude/outdated_scripts_backup/inav/`
- ✅ Removed 1 exact duplicate (`crsf_stream_parser.py`)
- ✅ 6 legitimate utility scripts remain in `inav/`

**Files Moved to Backup:**
1. test_telemetry_proper_timing.sh
2. crsf_rc_sender.py
3. configure_crsf_complete.py
4. configure_crsf_proper_sequence.py
5. setup_crsf_step_by_step.py
6. enable_telemetry_feature.py
7. capture_frames.py

**Exact Duplicate Removed:**
- inav/crsf_stream_parser.py (kept claude/developer/test_tools/crsf_stream_parser.py)

**Remaining in inav/:**
- build.sh, build_docs.sh
- check_max_output_ports.sh, closest.sh, fake_travis_build.sh

**Moved to claude/test_tools/inav/:**
- configure_sitl_crsf.py (2025-12-07)

**Documentation:**
- Backup README: `claude/outdated_scripts_backup/README.md`
- Restoration instructions included

---

**Manager**
