# PR #11025 CRSF Telemetry Fix Validation Test

## Purpose

This test validates that the critical bugs in PR #11025 have been fixed. PR #11025 was reverted (via PR #11139) on the same day it was merged because it corrupted CRSF telemetry streams.

## What It Tests

The test checks for 5 critical issues:

1. **TEST 1: RPM Frame Scheduling** (BUG #1 - CRITICAL)
   - Buggy: Frames scheduled unconditionally (#ifdef only)
   - Fixed: Conditional scheduling (if ESC_SENSOR_ENABLED && motorCount > 0)
   - Impact: Malformed frames when ESC sensors disabled

2. **TEST 2: Temperature Frame Scheduling** (BUG #2 - CRITICAL)
   - Buggy: Frames scheduled unconditionally (#ifdef only)
   - Fixed: Conditional scheduling (if hasTemperatureSources)
   - Impact: Malformed frames when no temperature sensors

3. **TEST 3: Buffer Overflow Protection** (BUG #4 - HIGH)
   - Buggy: No bounds checking on temperature array (20 elements)
   - Fixed: Loop conditions include `tempCount < MAX_CRSF_TEMPS`
   - Impact: Buffer overflow if >20 temperature sources

4. **TEST 4: RPM Protocol Limit** (BUG #5 - HIGH)
   - Buggy: No limit on RPM values sent
   - Fixed: motorCount clamped to MAX_CRSF_RPM_VALUES (19)
   - Impact: Protocol violation if >19 motors configured

5. **TEST 5: MAX_CRSF_TEMPS Constant**
   - Checks for proper constant definition
   - Improves code maintainability

## Usage

```bash
# Test current code
cd inav
../claude/developer/test_pr11025_fix.sh

# Test specific commit
../claude/developer/test_pr11025_fix.sh e5bfe799c3

# Test buggy code (should fail)
../claude/developer/test_pr11025_fix.sh f8dc0bce93
```

## Expected Results

### Buggy Code (before fix)
```
❌ RESULT: FAIL - Bugs detected

Commit: f8dc0bce93
Fixes detected: 0
Bugs detected: 3
```

### Fixed Code (after fix)
```
✅ RESULT: PASS - Code is safe

Commit: e5bfe799c3 (or HEAD on fix-pr11025-crsf-telemetry branch)
Fixes detected: 3
Bugs detected: 0
```

## Exit Codes

- **0**: All fixes present (safe code)
- **1**: Bugs detected (unsafe code)
- **2**: Script error

## Integration

This test can be integrated into CI/CD pipelines to prevent regression:

```bash
# In CI pipeline
if ! ../claude/developer/test_pr11025_fix.sh HEAD; then
    echo "ERROR: PR #11025 bugs detected - blocking merge"
    exit 1
fi
```

## Files

- Test script: `claude/developer/test_pr11025_fix.sh`
- Investigation report: `claude/developer/sent/pr11025-root-cause-analysis.md`
- Fix commit: `e5bfe799c3` on branch `fix-pr11025-crsf-telemetry`

## Historical Context

**Timeline:**
- Nov 28, 2025: PR #11025 merged
- Nov 28, 2025: Users reported "lost all ESC telemetry sensors as well as alt and vspeed"
- Nov 28, 2025: PR #11139 immediately reverted changes
- Dec 18, 2025: Root cause analysis and fix implementation

**Root Cause:**
Unconditional frame scheduling + conditional frame writing = malformed frames

**Impact:**
Malformed CRSF frames corrupted the protocol stream, causing receivers to lose sync and ALL telemetry to stop working.
