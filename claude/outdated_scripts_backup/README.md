# Outdated Scripts Backup

**Date:** 2025-12-07
**Action:** Cleanup of superseded test scripts from `inav/` directory
**Manager:** Development Manager

---

## Summary

**Scripts moved to backup:** 7 files
**Exact duplicates removed:** 1 file
**Total disk space:** ~33KB backed up

---

## Files Moved to Backup

### From `inav/` to `claude/outdated_scripts_backup/inav/`:

1. **`test_telemetry_proper_timing.sh`** (2.2KB, Dec 7 09:39)
   - **Superseded by:** `claude/test_tools/inav/test_crsf_telemetry.sh`
   - **Reason:** Old version (66 lines) replaced by comprehensive automated test suite (380 lines)
   - **Improvements in new version:**
     - 7-step automated workflow
     - Binary validation with `nm` symbol checking
     - Automatic TELEMETRY feature enablement
     - Mode-specific testing (baseline, pr11025, pr11100)
     - Frame validation and error reporting
     - Cleanup and CI integration

2. **`crsf_rc_sender.py`** (5.0KB, Dec 6 17:48)
   - **Superseded by:** `claude/developer/test_tools/crsf_rc_sender.py`
   - **Reason:** Old send-only version (173 lines) replaced by bidirectional version (545 lines)
   - **Improvements in new version:**
     - Bidirectional communication (sends RC + receives telemetry)
     - EdgeTX-compatible error detection (CRC8, frame validation)
     - Connection retry logic (30s timeout)
     - Telemetry frame parsing and statistics
     - Stream health indicator (EXCELLENT/GOOD/FAIR/POOR)
     - Error tracking and reporting

3. **`configure_crsf_complete.py`** (6.0KB, Dec 7 08:33)
   - **Reason:** Development iteration, superseded by `configure_sitl_crsf.py`

4. **`configure_crsf_proper_sequence.py`** (5.0KB, Dec 7 09:24)
   - **Reason:** Development iteration, superseded by `configure_sitl_crsf.py`

5. **`setup_crsf_step_by_step.py`** (4.0KB, Dec 7 08:46)
   - **Reason:** Development iteration, superseded by `configure_sitl_crsf.py`

6. **`enable_telemetry_feature.py`** (2.2KB, Dec 6 20:39)
   - **Reason:** Functionality integrated into `claude/test_tools/inav/test_crsf_telemetry.sh`

7. **`capture_frames.py`** (2.5KB, Dec 6 21:24)
   - **Reason:** Superseded by `crsf_rc_sender.py --show-telemetry`

---

## Exact Duplicates Removed

### Removed from `inav/` (exact copy exists in `claude/developer/test_tools/`):

1. **`crsf_stream_parser.py`** (227 lines)
   - **Kept version:** `claude/developer/test_tools/crsf_stream_parser.py`
   - **Reason:** Identical files (byte-for-byte match)
   - **Purpose:** Parse and validate CRSF telemetry stream
   - **Location rationale:** Test tools belong in claude/developer/test_tools/ for better organization

---

## Remaining Scripts in `inav/`

### Legitimate utility scripts (kept):

1. ✅ `build.sh` - Standard INAV firmware build wrapper
2. ✅ `build_docs.sh` - Documentation build utility
3. ✅ `configure_sitl_crsf.py` - **Moved to** `claude/test_tools/inav/configure_sitl_crsf.py`
4. ✅ `check_max_output_ports.sh` - Utility script
5. ✅ `closest.sh` - Utility script
6. ✅ `fake_travis_build.sh` - CI/CD testing utility

**Total:** 6 scripts remaining (all actively used)

---

## Better Versions Location

All improved test scripts are now organized in:
- **`claude/test_tools/inav/`** - Main test scripts and utilities
  - `test_crsf_telemetry.sh` - Comprehensive CRSF telemetry test suite
  - `quick_test_crsf.sh` - Quick CRSF validation
  - Various MSP benchmark tools

- **`claude/developer/test_tools/`** - Developer-specific test utilities
  - `crsf_rc_sender.py` - Bidirectional CRSF RC/telemetry tool with validation
  - `crsf_stream_parser.py` - CRSF frame parser and validator
  - `check_crsf_rx.py` - CRSF RX verification

---

## Restoration Instructions

If any backed-up script is needed:

```bash
# Restore a specific file
cp claude/outdated_scripts_backup/inav/<filename> inav/

# Restore all backed-up files
cp claude/outdated_scripts_backup/inav/* inav/
```

---

## Related Documentation

- **Analysis:** `claude/manager/SUPERSEDED_SCRIPTS_ANALYSIS.md`
- **Test Tools Guide:** `claude/test_tools/inav/README.md` (if exists)
- **Skills:**
  - `test-crsf-sitl` - CRSF telemetry testing workflow
  - `build-sitl` - SITL build instructions

---

## Notes

- All scripts in backup are functional but superseded by better implementations
- No data loss - all scripts safely backed up
- Cleanup improves repository organization and reduces confusion
- Development iterations retained for reference/forensics if needed

**Cleanup performed by:** Development Manager
**Date:** 2025-12-07 12:13
