# Email: Issue #13 Analysis - Dual-Band Support for PrivacyLRS

**Date:** 2025-12-05 17:10
**To:** Manager, Security Analyst
**From:** Developer
**Subject:** Issue #13 Research Complete - Dual-Band Support Analysis & Recommendation

---

## Summary

Completed research on [Issue #13](https://github.com/sensei-hacker/PrivacyLRS/issues/13) regarding dual-band receiver (DBR4) build failures.

**Finding:** ExpressLRS has implemented dual-band support via **LR1121 Gemini Xrossband** technology, but there are **build system limitations** we need to address for PrivacyLRS.

**Recommendation:** Dual-band support is **VALUABLE for PrivacyLRS** - worth implementing with modifications.

---

## Issue #13 Background

**Problem Reported:**
- RadioMaster DBR4-TD dual-band receiver (2.4 GHz + 868/900 MHz) build fails
- Error: "Regulatory_Domain 2400 not compatible with RADIO_SX127X/RADIO_LR1121"
- Users cannot build firmware that supports both bands simultaneously

**Hardware Context:**
- DBR4 has **2x LR1121 transceivers** (true dual-band hardware)
- **4 antennas** (2x 2.4GHz, 2x 868/915MHz)
- Weight: 2.7g without antennas / 5.3g with antennas
- Cost: ~$30 USD

---

## How ExpressLRS Implements Dual-Band

### Gemini Xrossband Technology

**PR #2540** ([Link](https://github.com/ExpressLRS/ExpressLRS/pull/2540)) merged Feb 20, 2024, implements LR1121 dual-band support:

**Key Features:**
1. **Simultaneous transmission** on 2.4GHz AND 868/900MHz
2. **Reduced packet loss** - redundant transmission on both bands
3. **Gemini modes:** X150Hz and X100Hz Full (dual-band packet rates)
4. **Automatic band switching** for optimal performance

**Hardware Requirements:**
- **2x LR1121 chips required** (one cannot switch bands fast enough)
- Each chip handles one frequency band
- Coordinated transmission for redundancy

**Performance:**
- X150Hz: 150 packets/sec on BOTH bands simultaneously
- X100Hz Full: 100 packets/sec with full 16-channel resolution
- "Slightly better" range than SX127x at 200Hz
- "Noticeably better" at 100Hz

---

## Current Build System Limitation

### The Root Cause

**File:** `src/python/build_flags.py`

**Problematic Code:**
```python
if '-DRADIO_SX127X=1' in build_flags or '-DRADIO_LR1121=1' in build_flags:
    # disallow setting 2400s for 900
    if '-DRADIO_SX127X=1' in build_flags and \
        (fnmatch.filter(build_flags, '*-DRegulatory_Domain_ISM_2400') or
         fnmatch.filter(build_flags, '*-DRegulatory_Domain_EU_CE_2400')):
        print_error('Regulatory_Domain 2400 not compatible with RADIO_SX127X/RADIO_LR1121')
```

**Problem:** The check treats LR1121 the SAME as SX127x (900MHz only), but **LR1121 supports dual-band!**

---

## ExpressLRS Solution Approach

### UnifiedConfiguration.py Handling

**File:** `src/python/UnifiedConfiguration.py`

**Dual-Band Detection:**
```python
if frequency == 'dual':
    for k in jmespath.search(...'tx_2400'..., targets):
        if '_LR1121_' in k['firmware']:
            products.append(k)
    for k in jmespath.search(...'tx_900'..., targets):
        if '_LR1121_' in k['firmware']:
            products.append(k)
```

**Approach:**
1. Check if device is LR1121-based (`_LR1121_` in firmware name)
2. If yes, allow `frequency = 'dual'` configuration
3. Generate BOTH 2.4GHz and 900MHz build targets
4. Handle regulatory domains separately for each band

---

## Privacy Benefits of Dual-Band

### Why Dual-Band Enhances Privacy

**1. Interference Resistance:**
- 2.4GHz band: Crowded with WiFi, Bluetooth, etc.
- 868/900MHz: Less congested, better penetration
- **Dual transmission:** If one band is jammed/interfered, other maintains link

**2. Anti-Detection:**
- Frequency hopping across TWO different bands
- Harder to detect/track with single-band scanners
- More complex signal fingerprinting required

**3. Redundancy:**
- Packet sent on BOTH bands simultaneously
- Reduces retransmissions (which create patterns)
- Lower latency (no waiting for retry)

**4. Location Privacy:**
- Band selection based on local environment
- Automatic switching reduces predictable patterns
- Better obstacle penetration (900MHz) for urban areas

---

## PrivacyLRS-Specific Considerations

### Encryption Impact

**ChaCha20 Performance:** 3.52 μs per packet (0.088% CPU)

**Dual-Band Impact:**
- **Encrypting twice:** 7.04 μs total (still only 0.18% CPU at 150 Hz!)
- With 6.67ms between packets (150 Hz), this is **NEGLIGIBLE**

**CPU Budget at X150Hz (dual-band):**
- Available per packet: 6,667 μs (6.67 ms)
- ChaCha20 x2: 7.04 μs
- **Percentage used: 0.11%** (99.89% idle!)

**Conclusion:** Encryption overhead is **NOT a concern** for dual-band!

---

## Implementation Requirements

### Changes Needed for PrivacyLRS

**1. Build System Updates:**

**File:** `src/python/build_flags.py`

**Change:**
```python
# OLD (blocks LR1121 + 2400):
if '-DRADIO_SX127X=1' in build_flags or '-DRADIO_LR1121=1' in build_flags:
    if '-DRADIO_SX127X=1' in build_flags and \
        (fnmatch.filter(build_flags, '*-DRegulatory_Domain_ISM_2400') ...):
        print_error('Regulatory_Domain 2400 not compatible with RADIO_SX127X/RADIO_LR1121')

# NEW (allow LR1121 + dual regulatory):
if '-DRADIO_SX127X=1' in build_flags:
    # Only SX127x is 900-only; LR1121 supports dual-band
    if (fnmatch.filter(build_flags, '*-DRegulatory_Domain_ISM_2400') ...):
        print_error('Regulatory_Domain 2400 not compatible with RADIO_SX127X (900MHz only)')
```

**2. Regulatory Domain Configuration:**

Add support for **dual regulatory domains**:
- Primary: 900MHz domain (e.g., FCC_915, EU_868)
- Secondary: 2.4GHz domain (ISM_2400, EU_CE_2400)

**3. Gemini Mode Integration:**

Add packet rate modes:
- X150Hz: 150 Hz dual-band Gemini mode
- X100Hz Full: 100 Hz with full channels

**4. Encryption Handling:**

Ensure ChaCha20 encrypts packets for BOTH bands:
```cpp
// Pseudo-code
void sendDualBandPacket(uint8_t *data) {
    uint8_t encrypted[PACKET_SIZE];

    // Encrypt once
    cipher.encrypt(encrypted, data, PACKET_SIZE);

    // Send on BOTH bands
    lr1121_2400.transmit(encrypted);  // 2.4GHz
    lr1121_900.transmit(encrypted);   // 900MHz
}
```

---

## Upstream ExpressLRS Code to Port

### Key Files to Review

**From [ExpressLRS/ExpressLRS](https://github.com/ExpressLRS/ExpressLRS):**

1. **`src/python/build_flags.py`** - Regulatory domain validation fix
2. **`src/python/UnifiedConfiguration.py`** - Dual-band product detection
3. **`src/lib/LR1121Driver/`** - Complete LR1121 driver ([PR #2540](https://github.com/ExpressLRS/ExpressLRS/pull/2540))
4. **Target definitions** - For DBR4, Nomad, XR4 dual-band devices

**Commit:** 3c04b8d - "Allow choosing the SubGHz domain for LR1121 modules"

---

## Hardware Support

### Compatible Dual-Band Devices

**Receivers:**
- [RadioMaster DBR4](https://radiomasterrc.com/products/dbr4-dual-band-xross-gemini-expresslrs-receiver) - Dual-band, dual-channel ($30)
- [RadioMaster XR4](https://radiomasterrc.com/products/xr4-gemini-xrossband-dual-band-expresslrs-receiver) - Gemini Xrossband
- [GEPRC Gemini Xrossband RX](https://geprc.com/product/geprc-elrs-915m-2-4g-gemini-xrossband-receiver/)

**Transmitters:**
- [RadioMaster Nomad](https://radiomasterrc.com/products/nomad-dual-1-watt-gemini-xrossband-expresslrs-module) - Dual 1W module

**All use 2x LR1121 transceivers for simultaneous dual-band operation.**

---

## Recommendation

### ✅ APPROVE Dual-Band Support for PrivacyLRS

**Reasoning:**

**1. Privacy Benefits:**
- Interference resistance improves reliability
- Dual-band transmission reduces detection/tracking
- Better obstacle penetration in urban environments
- Redundancy reduces retransmission patterns

**2. Performance Viable:**
- Encryption overhead: 0.11% CPU at X150Hz (negligible!)
- Well-tested in upstream ExpressLRS (merged Feb 2024)
- Hardware readily available (~$30)

**3. User Demand:**
- Issue #13 shows real user need
- DBR4/Nomad hardware already in use
- Configurator issue #703 shows ongoing requests

**4. Competitive Feature:**
- ExpressLRS has it (since Feb 2024)
- Privacy + dual-band = **unique selling point**
- Aligns with PrivacyLRS privacy mission

---

## Implementation Plan

### Phase 1: Build System Fix (2-4 hours)

**Tasks:**
1. Update `build_flags.py` - Remove LR1121 from 2.4GHz block
2. Update `UnifiedConfiguration.py` - Add dual-band detection
3. Test build with dual regulatory domains
4. **Deliverable:** Can build DBR4 firmware without errors

### Phase 2: LR1121 Driver Port (8-12 hours)

**Tasks:**
1. Port LR1121 driver from ExpressLRS PR #2540
2. Integrate with PrivacyLRS encryption
3. Add Gemini mode support (X150Hz, X100Hz Full)
4. Test on hardware (requires DBR4 or Nomad)
5. **Deliverable:** Working dual-band transmission

### Phase 3: Testing & Documentation (4-6 hours)

**Tasks:**
1. Range testing (2.4GHz vs 900MHz vs dual)
2. Interference testing (WiFi/Bluetooth environments)
3. Encryption verification on both bands
4. User documentation
5. **Deliverable:** Production-ready dual-band support

**Total Estimated Effort:** 14-22 hours

---

## Risks & Mitigations

### Risk 1: Hardware Availability
**Risk:** Need DBR4/Nomad for testing
**Mitigation:** Devices are $30, readily available from multiple vendors
**Priority:** Low - inexpensive and accessible

### Risk 2: Regulatory Complexity
**Risk:** Dual regulatory domains harder to configure
**Mitigation:** Copy ExpressLRS configurator UI approach
**Priority:** Medium - manageable with good UX

### Risk 3: Encryption Sync
**Risk:** Both bands must stay synchronized with counter
**Mitigation:** Use shared encryption state, extensive testing
**Priority:** High - critical for security

### Risk 4: Maintenance Burden
**Risk:** More code to maintain vs upstream
**Mitigation:** Port cleanly, document well, follow upstream updates
**Priority:** Medium - standard for any feature addition

---

## Alternative: Don't Implement

### If We Skip Dual-Band

**Consequences:**
- Users with DBR4/Nomad hardware **cannot use PrivacyLRS**
- Privacy advantage (interference resistance) lost
- Competitive disadvantage vs ExpressLRS
- Issue #13 remains unsolved

**When This Makes Sense:**
- If team capacity is very limited
- If no users request it beyond Issue #13
- If hardware is too expensive (it's not - $30)

**My Opinion:** The privacy and reliability benefits outweigh the implementation cost.

---

## Next Steps

**If approved:**

1. **Manager:** Prioritize in project roadmap
2. **Developer (me):** Begin Phase 1 (build system fix)
3. **Security Analyst:** Review encryption implications for dual-band
4. **Team:** Acquire DBR4 hardware for testing ($30)

**Timeline:** Could have Phase 1 (build fix) done this week if prioritized.

---

## Sources

- [Issue #13 - PrivacyLRS](https://github.com/sensei-hacker/PrivacyLRS/issues/13)
- [ExpressLRS PR #2540 - Gemini Xrossband](https://github.com/ExpressLRS/ExpressLRS/pull/2540)
- [Configurator Issue #703](https://github.com/ExpressLRS/ExpressLRS-Configurator/issues/703)
- [RadioMaster DBR4 Product Page](https://radiomasterrc.com/products/dbr4-dual-band-xross-gemini-expresslrs-receiver)
- [RadioMaster Nomad Product Page](https://radiomasterrc.com/products/nomad-dual-1-watt-gemini-xrossband-expresslrs-module)
- [Oscar Liang Review](https://oscarliang.com/radiomaster-nomad-dbr4/)

---

## Bottom Line

**Status:** ✅ Research complete
**Recommendation:** APPROVE dual-band support implementation
**Privacy Benefit:** High (interference resistance, anti-detection)
**Performance Impact:** Negligible (0.11% CPU)
**Implementation Effort:** 14-22 hours across 3 phases
**Hardware Cost:** ~$30 for testing
**User Value:** High (Issue #13 + broader dual-band user base)

**Dual-band support aligns perfectly with PrivacyLRS's privacy mission while being technically and economically feasible.**

---

**Developer**
2025-12-05 17:10
