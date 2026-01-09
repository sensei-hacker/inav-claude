# Project: Fix Finding 8 - Multi-Source Entropy with Dynamic Detection

**Status:** 📋 TODO
**Priority:** MEDIUM
**Severity:** MEDIUM (upgraded from LOW due to multiple sources requirement)
**Type:** Security Enhancement
**Created:** 2025-11-30
**Assigned:** Security Analyst (or Developer)
**Estimated Time:** 6-8 hours

## Overview

Implement robust entropy gathering that XORs multiple entropy sources (hardware RNG, timer jitter, ADC noise, RSSI) with dynamic detection and graceful fallback for platform compatibility.

## Problem

**Security Finding 8 (LOW → MEDIUM):** RNG Quality - RSSI Sampling Alone Insufficient

**Location:** `PrivacyLRS/src/src/tx_main.cpp:214-251` (function `RandRSSI()`)

**Current Implementation:**
- Relies solely on RSSI (Received Signal Strength Indicator) sampling for entropy
- `RandRSSI()` samples RSSI values as source of randomness
- RSSI can be predictable in static environments
- Single source of entropy is risky

**Issue:**
- RSSI may be constant in static/indoor environments
- Attacker could predict RSSI patterns
- No fallback if RSSI unavailable
- Single point of failure for cryptographic randomness
- Used for ephemeral key generation (Finding 7) and nonces

**Impact:**
- Weak random number generation
- Predictable cryptographic keys
- Reduced security of entire encryption system
- Especially critical for Finding 7 (ECDH ephemeral keys)

## Approved Solution

**Decision:** XOR all available sources with dynamic detection

Implement entropy gathering that:
- XORs multiple entropy sources:
  - Hardware RNG (if available)
  - Timer jitter
  - ADC noise (if available)
  - RSSI sampling (existing)
- Dynamically detects available hardware sources at runtime
- Gracefully falls back if hardware unavailable
- Never crashes due to missing entropy hardware
- Uses what is available on each platform

**Rationale:**
- Defense in depth for entropy generation
- Robust across different hardware platforms
- Graceful degradation improves reliability
- Multiple entropy sources increase unpredictability
- Platform-agnostic approach

**Stakeholder Specification:**
"Option 1 and 3. xor all available sources. But it is important that it not crash if the hardware isn't available. use what is available, dynamically"

## Objectives

1. Audit current entropy usage in codebase
2. Design multi-source entropy gathering architecture
3. Implement hardware capability detection
4. Implement entropy source wrappers
5. Implement entropy mixing (XOR)
6. Test on multiple platforms
7. Verify robust fallback behavior
8. Ensure no crashes on any platform

## Implementation Steps

### Phase 1: Analysis (1-2 hours)
1. Audit current random number usage
2. Identify all calls to `RandRSSI()`
3. Identify platforms and their capabilities
4. Research available entropy sources per platform
5. Design entropy source abstraction
6. Plan dynamic detection mechanism

### Phase 2: Entropy Source Implementation (2-3 hours)
1. Implement hardware RNG wrapper
2. Implement timer jitter collector
3. Implement ADC noise sampler
4. Implement RSSI sampler (refactor existing)
5. Add dynamic capability detection
6. Test each source independently

### Phase 3: Entropy Mixing (1-2 hours)
1. Implement entropy pool / mixing function
2. XOR outputs from all available sources
3. Add entropy quality tracking (optional)
4. Implement unified RNG interface
5. Replace `RandRSSI()` calls

### Phase 4: Testing (2-3 hours)
1. Test on platform with all entropy sources
2. Test on platform with subset of sources
3. Test with hardware RNG disabled
4. Verify graceful fallback
5. Test randomness quality
6. Verify no crashes

## Scope

**In Scope:**
- Multiple entropy source integration
- Dynamic hardware detection
- Graceful fallback
- Testing on multiple platforms
- Replacing `RandRSSI()` usage

**Out of Scope:**
- Full CSPRNG (Cryptographically Secure PRNG) implementation
- Formal randomness testing (NIST test suite)
- Other security findings
- Changing cryptographic primitives

## Success Criteria

- [ ] Hardware RNG wrapper implemented
- [ ] Timer jitter collector implemented
- [ ] ADC noise sampler implemented
- [ ] RSSI sampler refactored
- [ ] Dynamic detection working
- [ ] Entropy sources XORed together
- [ ] Graceful fallback verified
- [ ] No crashes on any platform
- [ ] `RandRSSI()` calls replaced
- [ ] Tests pass on multiple platforms
- [ ] Documentation complete

## Entropy Sources

### 1. Hardware RNG
- **Availability:** Platform-dependent
- **Quality:** High (if hardware is good)
- **Detection:** Check for RNG peripheral at runtime
- **Fallback:** Continue without if unavailable

### 2. Timer Jitter
- **Availability:** Universal (all platforms have timers)
- **Quality:** Medium (depends on interrupt timing)
- **Detection:** Always available
- **Implementation:** Sample high-resolution timer

### 3. ADC Noise
- **Availability:** Platform-dependent
- **Quality:** Medium (floating ADC input)
- **Detection:** Check for ADC peripheral at runtime
- **Fallback:** Continue without if unavailable

### 4. RSSI Sampling
- **Availability:** High (RC receivers have RSSI)
- **Quality:** Low to Medium (varies with environment)
- **Detection:** Existing mechanism
- **Implementation:** Keep existing `RandRSSI()` logic

## Dynamic Detection Design

```cpp
struct EntropyConfig {
    bool has_hw_rng;
    bool has_adc;
    bool has_rssi;
    bool has_timer;  // Always true
};

EntropyConfig detectEntropyCapabilities() {
    // Runtime detection of available entropy sources
}

uint32_t getRandomBytes(uint8_t* buffer, size_t len) {
    // Collect from all available sources and XOR
}
```

## Dependencies

**Technical:**
- Understanding of platform hardware capabilities
- Access to multiple test platforms
- Knowledge of HAL (Hardware Abstraction Layer) APIs

**Related Findings:**
- **Finding 7:** ECDH ephemeral keys need strong RNG
- **Finding 2:** Nonce generation may use RNG
- Independent of other findings

## Risk Assessment

**Technical Risks:**
- Hardware RNG may not be available (mitigation: fallback to timer + ADC + RSSI)
- ADC may not be available (mitigation: fallback to timer + RSSI)
- Timer jitter may be weak (mitigation: combine with other sources)
- Low risk overall (defense in depth approach)

**Project Risks:**
- MEDIUM priority - important for Finding 7
- Moderate complexity
- Platform-specific testing required
- Risk of platform-specific bugs

## Priority Justification

**MEDIUM** - While originally rated LOW, the stakeholder's decision to use multiple sources elevates this to MEDIUM. Strong entropy is critical for Finding 7 (ECDH ephemeral keys) and Finding 2 (counter initialization). Weak entropy undermines cryptographic security.

## Notes

**Reference Documents:**
- Security findings report: `claude/manager/inbox-archive/2025-11-30-1500-findings-privacylrs-comprehensive-analysis.md`
- Decisions document: `claude/projects/security-analysis-privacylrs-initial/findings-decisions.md`

**Stakeholder Decision:**
"Option 1 and 3. xor all available sources. But it is important that it not crash if the hardware isn't available. use what is available, dynamically"

**Entropy Mixing:**
XOR is appropriate for combining entropy sources:
- If any source has entropy, the output has entropy
- Simple and fast
- No state to manage
- Industry standard for entropy mixing

**Hardware RNG Considerations:**
- Some hardware RNGs can be weak or biased
- XOR with other sources provides defense
- Check platform documentation for RNG quality
- Consider post-processing if RNG is weak

**Timer Jitter Collection:**
```cpp
uint32_t collectTimerJitter() {
    uint32_t entropy = 0;
    for (int i = 0; i < 32; i++) {
        uint32_t t1 = micros();
        // Small work to cause jitter
        entropy ^= (t1 & 1) << i;
    }
    return entropy;
}
```

**ADC Noise Sampling:**
```cpp
uint32_t collectADCNoise() {
    uint32_t entropy = 0;
    for (int i = 0; i < 32; i++) {
        uint16_t adc_val = readADC(floating_pin);
        entropy ^= (adc_val & 1) << i;
    }
    return entropy;
}
```

**RSSI Sampling:**
- Keep existing logic from `RandRSSI()`
- Incorporate as one of multiple sources

**Testing Randomness:**
- Visual inspection (shouldn't see patterns)
- Basic statistical tests (chi-square)
- Not full NIST suite (out of scope)
- Ensure different across runs

**Platform Testing:**
- Test on primary platform (all sources available)
- Test on minimal platform (timer + RSSI only)
- Verify no crashes when sources unavailable
- Document which sources available per platform
