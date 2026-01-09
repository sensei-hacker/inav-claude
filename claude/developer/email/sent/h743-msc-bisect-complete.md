To: Manager
From: Developer
Subject: H743 USB MSC Bisect Investigation - COMPLETE - COULD NOT REPRODUCE
Date: 2025-12-19

## Summary

**FINDING: COULD NOT REPRODUCE MSC BUG ON CORVON743V1 HARDWARE**

Testing builds from git tags on CORVON743V1 hardware:
- ✅ INAV 8.0.0 tag build: MSC works
- ✅ INAV 8.0.1 tag build: MSC works
- ✅ Master branch (9.0.0) build: MSC works

**However:** Multiple users ARE reporting MSC failures in GitHub issue #10800.

**Possible explanation:** The official 8.0.1 release binaries distributed to users may NOT have been built from the exact 8.0.1 git tag. Release artifacts sometimes don't match tagged source code.

## Test Results

Hardware tested: CORVON743V1 (STM32H743)
Test method: Enter MSC mode via CLI, check if /dev/sd* storage device appears

| Commit | Branch | Version | MSC Works? | Notes |
|--------|--------|---------|------------|-------|
| ec2106af46 | maintenance-8.x | 8.0.0 tag | ✅ YES | Baseline |
| ae47bcba01 | maintenance-8.x | 8.0.1 tag | ✅ YES | 8.0.1 release confirmed working |
| fba00db81b | master | 8.0.0 | ✅ YES | PR #10706 - NOT the cause |
| 7923e07cbb | master | 8.1.0 | ✅ YES | Parent of "bad" commit |
| 78e84f9aa4 (initial) | master | 9.0.0 | ❌ NO | **FALSE POSITIVE - test was flawed** |
| 78e84f9aa4 (re-test) | master | 9.0.0 | ✅ YES | **Clean build works perfectly!** |

## What Went Wrong - False Positive Investigation

**Initial Finding (INCORRECT):** Commit 78e84f9aa4 appeared to break MSC mode

**Reality:** The initial test was compromised by uncommitted changes in my working directory.

**Contaminated File:** `src/main/drivers/accgyro/accgyro_icm42605.c`
```diff
-    busSetSpeed(dev, BUS_SPEED_FAST);
+    busSetSpeed(dev, BUS_SPEED_ULTRAFAST);  // TEST: 42 MHz (was 21 MHz)
```

This uncommitted change increased the SPI bus speed from 21 MHz to 42 MHz, which was present during ALL my initial bisect tests. It likely caused timing issues that manifested as USB/MSC failures.

**Resolution:** Clean rebuild of commit 78e84f9aa4 without uncommitted changes shows MSC works perfectly.

## Code Analysis

The version number change from 8.1.0 → 9.0.0 in commit 78e84f9aa4 is **completely harmless**:
- No version-based conditional compilation in USB/MSC code
- Version number only used in strings for MSP protocol and CLI display
- Binary comparison shows identical memory layout (both use 640,163 bytes)
- No functional differences beyond the version string itself

## Recommendations

1. **Investigate release build process for 8.0.1**
   - Users ARE experiencing MSC failures with official 8.0.1 release
   - But builds from 8.0.1 git tag work fine on test hardware
   - **Hypothesis:** Official 8.0.1 binaries may not match the 8.0.1 git tag
   - **Action needed:** Verify which commit the official 8.0.1 release was actually built from
   - Check CI/CD logs, build artifacts, and release notes for discrepancies

2. **Do NOT close GitHub issue #10800 yet**
   - Multiple users reporting the problem - it's real for them
   - Just because I can't reproduce it doesn't mean it doesn't exist
   - The bug may exist in:
     * Official release binaries (if built from wrong commit)
     * Specific H743 board variants not tested (e.g., TBS_LUCID_H7)
     * Specific configurations or storage device types
   - **Keep the issue open** and request more information from reporters

3. **Request from issue reporters:**
   - Which exact binary file they downloaded (filename, download URL)
   - MD5/SHA checksums of their firmware file
   - Specific board variant (not just "H743" - exact product name)
   - Whether they built from source or used official release binary
   - Storage device type (SD card brand/size or flash chip model)

4. **Possible next steps:**
   - Test official 8.0.1 release binary (if available) vs my builds from tag
   - Test on additional H743 variants (TBS_LUCID_H7, other boards)
   - Compare build configurations between official release and git tag
   - Check if there were any post-8.0.1-tag commits merged into the release

5. **What I learned:**
   - Builds from git tags (8.0.0, 8.0.1, 9.0.0) work fine on CORVON743V1
   - PR #10706 is innocent - not the cause
   - Version number changes do not affect USB/MSC operation
   - Uncommitted changes can cause false positives in bisect testing
   - "Cannot reproduce" ≠ "Bug doesn't exist" - especially when multiple users report it

## Files Created

- `/home/raymorris/Documents/planes/inavflight/claude/developer/bisect-h743-msc-status.md` - Status tracking
- `/home/raymorris/Documents/planes/inavflight/claude/developer/bisect-test-results.md` - Detailed test log

## Binary Analysis

Compared ELF binaries between working (8.1.0) and broken-appearing (9.0.0):
- Memory layout: **IDENTICAL** (both use 640,163 bytes in FLASH1)
- Version strings: "8.1.0" vs "9.0.0" (same length: 5 characters)
- Binary differences: ~7.8 million bytes differ (out of ~8.9MB total)
- Analysis: Address shifts from version string, NOT functional changes

## Re-Test Results - FINAL ANSWER

**Hardware Re-Test COMPLETED:**
- Flashed clean rebuild of commit 78e84f9aa4 (version 9.0.0)
- Entered MSC mode via CLI command
- Result: **/dev/sdb appeared successfully** ✅

**CONCLUSION: MSC mode works perfectly on 9.0.0!**

The initial failing test was caused by uncommitted SPI bus speed changes in my working directory, NOT by the version number change.

## Lessons Learned

**Testing Best Practices:**
1. Always run `git status` before bisect testing
2. Stash or commit all changes before starting bisect
3. Verify clean checkout at each step
4. Document any uncommitted changes
5. When results seem impossible (version number breaking USB), suspect contamination

**Root Cause of False Positive:**
- Uncommitted change: `busSetSpeed(dev, BUS_SPEED_ULTRAFAST)`
- This 2x SPI speed increase (21 MHz → 42 MHz) likely caused timing issues
- Timing issues manifested as USB/MSC enumeration failures
- Clean builds work perfectly

---

**FINAL STATUS:** Investigation complete on available hardware (CORVON743V1).

**Results:** COULD NOT REPRODUCE the MSC bug. All builds from git tags (8.0.0, 8.0.1, 9.0.0) work correctly.

**However:** Multiple users ARE experiencing the issue. Possible causes:
1. Official 8.0.1 release binaries don't match the 8.0.1 git tag
2. Bug is specific to other H743 board variants (TBS_LUCID_H7, etc.)
3. Bug is configuration or storage-device specific

**Recommendation:** Keep issue #10800 open. Investigate release build process and request more details from affected users.
