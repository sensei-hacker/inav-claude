# Email: Key ExpressLRS Commits for Dual-Band Support

**Date:** 2025-12-05 17:20
**To:** Manager, Security Analyst
**From:** Developer
**Subject:** Specific ExpressLRS Commits to Port for Issue #13 Dual-Band Support

---

## Summary

Identified the **specific commits** from ExpressLRS that need to be ported/adapted for PrivacyLRS dual-band support.

**Key finding:** Only **3 main commits** are required for basic dual-band build support, plus the full LR1121 driver.

---

## Critical Commits (Must-Have)

### 1. Build System Fix - Allow 2400 Domain for LR1121

**Commit:** `c49f9fae7c1e9b69df60134eb7956ab1e225327b`
**Date:** December 24, 2024
**Author:** Paul Kendall (@pkendall64)
**PR:** [#3007](https://github.com/ExpressLRS/ExpressLRS/pull/3007)
**File:** `src/python/build_flags.py`
**Priority:** ⭐⭐⭐ CRITICAL - This fixes Issue #13!

**What it does:**
- Separates SX127X (900MHz only) from LR1121 (dual-band capable)
- Allows LR1121 to use ISM_2400 regulatory domain
- Keeps SX127X restricted to 900MHz domains only
- Enables dual-band builds without errors

**Code Change:**
```python
# BEFORE (blocks LR1121 + 2400):
if '-DRADIO_SX127X=1' in build_flags or '-DRADIO_LR1121=1' in build_flags:
    if '-DRADIO_SX127X=1' in build_flags and \
        (fnmatch.filter(build_flags, '*-DRegulatory_Domain_ISM_2400') or
         fnmatch.filter(build_flags, '*-DRegulatory_Domain_EU_CE_2400')):
        print_error('Regulatory_Domain 2400 not compatible with RADIO_SX127X/RADIO_LR1121')

# AFTER (allows LR1121 + ISM_2400):
# SX127X validation (still blocks 2400)
if '-DRADIO_SX127X=1' in build_flags:
    if (fnmatch.filter(build_flags, '*-DRegulatory_Domain_ISM_2400') or
         fnmatch.filter(build_flags, '*-DRegulatory_Domain_EU_CE_2400')):
        print_error('Regulatory_Domain_*_2400 not compatible with RADIO_SX127X')

# LR1121 validation (only blocks EU_CE_2400, allows ISM_2400!)
if '-DRADIO_LR1121=1' in build_flags:
    if fnmatch.filter(build_flags, '*-DRegulatory_Domain_EU_CE_2400'):
        print_error('Regulatory_Domain_EU_CE_2400 not compatible with RADIO_LR1121')
```

**Why this matters:**
- This single commit fixes the build error in Issue #13
- Without this, DBR4/Nomad firmware cannot be compiled
- Must be ported first!

---

### 2. LR1121 Driver - Gemini Xrossband

**Commit:** `b4ad5ce9595125f1ffeec767c6a288a40b384a26`
**Date:** February 20, 2024
**Authors:** Jye Smith (@JyeSmith), Paul Kendall (@pkendall64)
**PR:** [#2540](https://github.com/ExpressLRS/ExpressLRS/pull/2540)
**Files:** Entire `src/lib/LR1121Driver/` directory + targets
**Priority:** ⭐⭐⭐ CRITICAL - The actual driver!

**What it does:**
- Complete LR1121 radio driver implementation
- Dual-band simultaneous transmission (Gemini mode)
- Frequency hopping for both 900MHz and 2.4GHz
- Power management for dual transceivers
- All LoRa modes (250Hz, 200Hz Full, 150Hz, 100Hz Full, 50Hz)
- Gemini modes (X150Hz, X100Hz Full)

**Sub-commits in PR #2540 (58 total):**

**Essential commits:**
- `65801c2` - Initial LR1121 driver with SF6 compatibility
- `fcd9268` - TX target configuration
- `f50b81c` - **Working 900MHz + 2.4GHz combined** (KEY COMMIT!)
- `81b9cf4` - Gemini TX implementation
- `3497bd8` - Dual-band power management arrays
- `96d2b88` - "adds ALL THE MODES" - comprehensive LoRa modes

**Files to port:**
```
src/lib/LR1121Driver/
├── LR1121_Regs.h          # Register definitions
├── LR1121_hal.cpp/h       # Hardware abstraction
├── LR1121.cpp/h           # Main driver
├── LR1121_Gemini.cpp/h    # Dual-band Gemini logic
└── devLR1121.cpp/h        # Device interface
```

**Target files:**
```
targets/unified.ini         # LR1121 unified targets
targets/namimnorc_2400.ini  # DBR4 target definition
```

---

### 3. LBT Support for LR1121 (Optional but Recommended)

**Commit:** `2b6a608e53c59abe24200a3901580d00fe99a429`
**Date:** June 28, 2025
**Author:** Paul Kendall (@pkendall64)
**PR:** [#3267](https://github.com/ExpressLRS/ExpressLRS/pull/3267)
**File:** `src/python/build_flags.py`, `src/lib/LR1121Driver/`
**Priority:** ⭐⭐ HIGH - Required for EU compliance

**What it does:**
- Listen-Before-Talk (LBT) for EU_868 regulatory compliance
- Extracts EnableLBT functionality for LR1121
- Required for legal operation in Europe

**Why this matters:**
- EU regulations REQUIRE LBT on 868MHz
- Without this, PrivacyLRS would be illegal in EU
- Should be included from the start

---

## Additional Commits (Nice-to-Have)

### 4. US433 Regulatory Domains

**Included in:** ExpressLRS 3.4.0 release
**Date:** February 2024
**Files:** `src/python/build_flags.py`, domain definitions
**Priority:** ⭐ MEDIUM - Expands frequency options

**What it does:**
- Adds US433 and US433-Wide regulatory domains
- US433: 8 hops in 4.75MHz (433.25-438MHz)
- US433-Wide: 20 hops in 14.5MHz (423.5-438MHz)
- Enables multi-user 433MHz operation without interference

**Why this matters:**
- More frequency band options
- Better for privacy (less common band)
- Gemini 433MHz support

---

### 5. UnifiedConfiguration.py Dual-Band Detection

**Part of:** LR1121 driver PR #2540
**File:** `src/python/UnifiedConfiguration.py`
**Priority:** ⭐⭐ HIGH - Required for configurator

**What it does:**
```python
if frequency == 'dual':
    for k in jmespath.search(...'tx_2400'..., targets):
        if '_LR1121_' in k['firmware']:
            products.append(k)
    for k in jmespath.search(...'tx_900'..., targets):
        if '_LR1121_' in k['firmware']:
            products.append(k)
```

**Why this matters:**
- Enables configurator to detect dual-band hardware
- Automatically populates LR1121 targets
- Required for user-friendly builds

---

## Implementation Priority Order

### Phase 1: Fix Build Error (Issue #13) - 2-4 hours

**Port these commits:**
1. ✅ `c49f9fae` - Build flags fix (MUST HAVE)

**Result:** DBR4 firmware builds without error

**Test:**
```bash
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DRegulatory_Domain_FCC_915" \
  pio run -e Unified_ESP32_2400_TX_via_UART
```

Should succeed without "not compatible" error.

---

### Phase 2: Add LR1121 Driver - 8-16 hours

**Port these commits:**
1. ✅ `b4ad5ce9` - Full LR1121 driver (PR #2540)
2. ✅ `2b6a608e` - LBT support (EU compliance)

**Port these files:**
- `src/lib/LR1121Driver/` (entire directory)
- Target definitions (DBR4, Nomad, etc.)
- UnifiedConfiguration.py dual-band logic

**Result:** Working dual-band transmission

**Test:**
- Build for DBR4 target
- Flash to hardware
- Test 2.4GHz transmission
- Test 900MHz transmission
- Test Gemini X150Hz mode (simultaneous)

---

### Phase 3: Encryption Integration - 4-8 hours

**PrivacyLRS-specific work:**
1. Integrate ChaCha20 encryption with dual-band
2. Ensure counter synchronization across both bands
3. Test encrypted packets on both frequencies
4. Verify no counter desync issues

**Result:** Encrypted dual-band operation

---

### Phase 4: Testing & Documentation - 4-6 hours

**Test scenarios:**
1. Range testing (2.4GHz vs 900MHz vs Gemini)
2. Interference testing (WiFi-heavy environment)
3. Encryption verification
4. EU LBT compliance testing

**Documentation:**
- Build instructions for dual-band
- Hardware compatibility list
- Regulatory domain guide

**Result:** Production-ready dual-band support

---

## Total Effort Estimate

**Minimum (Phase 1 only):** 2-4 hours - Just fix build error
**Full Implementation (Phases 1-4):** 18-34 hours - Complete dual-band support

---

## Commit Verification Links

All commits verified at ExpressLRS repository:

1. [Commit c49f9fa - Allow 2400 domain for LR1121](https://github.com/ExpressLRS/ExpressLRS/commit/c49f9fae7c1e9b69df60134eb7956ab1e225327b)
2. [PR #2540 - Gemini Xrossband LR1121 Driver](https://github.com/ExpressLRS/ExpressLRS/pull/2540)
3. [Commit b4ad5ce - LR1121 Driver merge](https://github.com/ExpressLRS/ExpressLRS/commit/b4ad5ce9595125f1ffeec767c6a288a40b384a26)
4. [PR #3267 - LBT Support](https://github.com/ExpressLRS/ExpressLRS/pull/3267)
5. [Release 3.4.0 - Full release notes](https://github.com/ExpressLRS/ExpressLRS/releases/tag/3.4.0)

---

## Files Changed Summary

**Python build system:**
- `src/python/build_flags.py` - Regulatory domain validation
- `src/python/UnifiedConfiguration.py` - Dual-band detection

**Driver code:**
- `src/lib/LR1121Driver/` - Entire new directory (~2000+ lines)
- `src/lib/FHSS/` - Frequency hopping updates for dual-band

**Target definitions:**
- `targets/unified.ini` - LR1121 unified targets
- `targets/namimnorc_2400.ini` - DBR4/Nomad targets

**Total LOC estimate:** ~3000-4000 lines (mostly driver code)

---

## Quick Start for Phase 1

**To immediately fix Issue #13:**

**File:** `PrivacyLRS/src/python/build_flags.py`

**Find this block (around line 138):**
```python
if '-DRADIO_SX127X=1' in build_flags or '-DRADIO_LR1121=1' in build_flags:
    # disallow setting 2400s for 900
    if '-DRADIO_SX127X=1' in build_flags and \
        (fnmatch.filter(build_flags, '*-DRegulatory_Domain_ISM_2400') or
         fnmatch.filter(build_flags, '*-DRegulatory_Domain_EU_CE_2400')):
        print_error('Regulatory_Domain 2400 not compatible with RADIO_SX127X/RADIO_LR1121')
```

**Replace with:**
```python
# SX127X is 900MHz only - block 2400 domains
if '-DRADIO_SX127X=1' in build_flags:
    if (fnmatch.filter(build_flags, '*-DRegulatory_Domain_ISM_2400') or
         fnmatch.filter(build_flags, '*-DRegulatory_Domain_EU_CE_2400')):
        print_error('Regulatory_Domain_*_2400 not compatible with RADIO_SX127X')

# LR1121 is dual-band capable - only block EU_CE_2400 (LBT conflict)
if '-DRADIO_LR1121=1' in build_flags:
    if fnmatch.filter(build_flags, '*-DRegulatory_Domain_EU_CE_2400'):
        print_error('Regulatory_Domain_EU_CE_2400 not compatible with RADIO_LR1121')
```

**Test build:**
```bash
cd PrivacyLRS/src
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DRegulatory_Domain_FCC_915" \
  pio run -e Unified_ESP32_2400_TX_via_UART
```

**Expected:** Build succeeds ✅ (no compatibility error!)

---

## Recommendation

**Start with Phase 1 immediately:**
- 2-4 hour effort
- Fixes Issue #13 build error
- Can be done this week
- Low risk (just validation logic change)

**Then evaluate Phase 2:**
- Requires hardware ($30 for DBR4)
- Requires testing time
- Higher effort but high value

**Manager:** Please advise on priority and hardware budget approval.

---

## Bottom Line

**Key commits identified:** 3 critical, 2 optional
**Minimum fix (Phase 1):** Single commit `c49f9fa` - 2-4 hours
**Full dual-band (Phases 1-4):** 18-34 hours total
**Hardware needed:** RadioMaster DBR4 (~$30)
**Issue #13 status:** Can be resolved with Phase 1 only

**All commits verified and linked above. Ready to begin implementation.**

---

**Developer**
2025-12-05 17:20
