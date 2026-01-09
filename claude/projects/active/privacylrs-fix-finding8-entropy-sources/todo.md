# Todo List: Fix Finding 8 - Multi-Source Entropy with Dynamic Detection

## Phase 1: Analysis and Design

### Audit Current RNG Usage
- [ ] Find all calls to `RandRSSI()` in codebase
- [ ] Document what each call is used for
  - Nonce generation?
  - Key generation?
  - Session IDs?
  - Other?
- [ ] Identify how much randomness is needed
- [ ] Note any critical uses (crypto keys, etc.)

### Analyze Existing RSSI Implementation
- [ ] Read `RandRSSI()` function
  - Location: `tx_main.cpp:214-251`
- [ ] Understand current entropy collection
- [ ] Document RSSI sampling approach
- [ ] Identify any issues or limitations
- [ ] Note code to preserve/refactor

### Survey Platform Capabilities
- [ ] List all target platforms (MCUs)
- [ ] For each platform, identify:
  - [ ] Hardware RNG availability
  - [ ] ADC availability
  - [ ] Timer specifications
  - [ ] RSSI availability
- [ ] Create platform capability matrix
- [ ] Document HAL APIs for each source

### Design Entropy Architecture
- [ ] Design entropy source abstraction
- [ ] Design dynamic capability detection
- [ ] Design entropy mixing approach (XOR)
- [ ] Design unified RNG interface
- [ ] Plan fallback strategy
- [ ] Document architecture

## Phase 2: Implement Dynamic Detection

### Create Capability Detection
- [ ] Implement hardware RNG detection
  ```cpp
  bool hasHardwareRNG() {
    // Check if RNG peripheral exists and is accessible
  }
  ```
- [ ] Implement ADC detection
  ```cpp
  bool hasADC() {
    // Check if ADC is available
  }
  ```
- [ ] Implement RSSI detection
  ```cpp
  bool hasRSSI() {
    // Check if RSSI sampling works
  }
  ```
- [ ] Timer is always available (no detection needed)

### Create Entropy Configuration
- [ ] Define entropy configuration structure
  ```cpp
  struct EntropyConfig {
    bool has_hw_rng;
    bool has_adc;
    bool has_rssi;
    bool has_timer;  // Always true
  };
  ```
- [ ] Implement `detectEntropyCapabilities()`
- [ ] Call detection at initialization
- [ ] Store configuration globally
- [ ] Add logging (what sources are available)

## Phase 3: Implement Entropy Sources

### Implement Hardware RNG Wrapper
- [ ] Create hardware RNG wrapper function
  ```cpp
  bool getHardwareRNG(uint32_t* output) {
    // Returns true if successful, false if unavailable
  }
  ```
- [ ] Handle platform-specific RNG APIs
- [ ] Add error handling (RNG failure)
- [ ] Test on platform with hardware RNG
- [ ] Test graceful failure when unavailable

### Implement Timer Jitter Collector
- [ ] Create timer jitter collection function
  ```cpp
  uint32_t collectTimerJitter() {
    // Collect entropy from high-resolution timer jitter
  }
  ```
- [ ] Use high-resolution timer (micros() or cycle counter)
- [ ] Collect multiple samples
- [ ] Extract LSBs (least predictable)
- [ ] Test and verify varies across calls

### Implement ADC Noise Sampler
- [ ] Create ADC noise sampling function
  ```cpp
  bool getADCNoise(uint32_t* output) {
    // Returns true if successful, false if unavailable
  }
  ```
- [ ] Select floating ADC input (if available)
- [ ] Sample ADC multiple times
- [ ] Extract LSBs
- [ ] Handle ADC unavailable case
- [ ] Test on platform with ADC
- [ ] Test graceful failure when unavailable

### Refactor RSSI Sampler
- [ ] Extract RSSI sampling into wrapper function
  ```cpp
  bool getRSSINoise(uint32_t* output) {
    // Use existing RandRSSI() logic
  }
  ```
- [ ] Preserve existing RandRSSI() logic
- [ ] Handle RSSI unavailable case (if possible)
- [ ] Test RSSI sampling still works

## Phase 4: Implement Entropy Mixing

### Create Entropy Mixing Function
- [ ] Implement entropy pool/mixer
  ```cpp
  void getRandomBytes(uint8_t* buffer, size_t len) {
    // XOR all available entropy sources
  }
  ```
- [ ] Collect from hardware RNG (if available)
- [ ] Collect from timer jitter (always)
- [ ] Collect from ADC (if available)
- [ ] Collect from RSSI (if available)
- [ ] XOR all collected entropy
- [ ] Fill output buffer

### Implement Unified RNG Interface
- [ ] Create `getRandomU32()` function
  ```cpp
  uint32_t getRandomU32() {
    uint32_t result;
    getRandomBytes((uint8_t*)&result, sizeof(result));
    return result;
  }
  ```
- [ ] Create `getRandomBytes()` function
- [ ] Support arbitrary length random data
- [ ] Add error handling (if all sources fail)
- [ ] Add logging (secure logging per Finding 4)

### Replace RandRSSI() Calls
- [ ] Find all uses of `RandRSSI()`
- [ ] Replace with new unified RNG
- [ ] Ensure semantics are preserved
- [ ] Update any related code
- [ ] Test each replacement

## Phase 5: Testing - Individual Sources

### Test Hardware RNG
- [ ] Test on platform with hardware RNG
  - Verify RNG is detected
  - Verify RNG returns data
  - Verify data appears random (no obvious patterns)
- [ ] Test on platform without hardware RNG
  - Verify graceful failure (returns false)
  - Verify no crashes

### Test Timer Jitter
- [ ] Test timer jitter collection
- [ ] Verify output varies across calls
- [ ] Check for patterns (shouldn't be obvious)
- [ ] Test on different platforms
- [ ] Verify always works (universal)

### Test ADC Noise
- [ ] Test on platform with ADC
  - Verify ADC is detected
  - Verify ADC returns data
  - Verify data appears noisy
- [ ] Test on platform without ADC
  - Verify graceful failure (returns false)
  - Verify no crashes

### Test RSSI Sampling
- [ ] Test refactored RSSI sampling
- [ ] Verify still works as before
- [ ] Test in different RF environments
- [ ] Verify output varies

## Phase 6: Testing - Integrated System

### Test Entropy Mixing
- [ ] Test with all sources available
  - Verify all sources contribute
  - Verify XOR mixing works
  - Check output for patterns
- [ ] Test with subset of sources
  - Disable hardware RNG: verify works
  - Disable ADC: verify works
  - Only timer + RSSI: verify works
- [ ] Verify no crashes in any configuration

### Test Randomness Quality
- [ ] Generate 1000+ random values
- [ ] Visual inspection (print some values)
- [ ] Basic statistics:
  - Check bit distribution (roughly 50/50 0s and 1s)
  - Chi-square test (basic)
  - Verify no obvious patterns
- [ ] Compare single-source vs multi-source quality

### Test Across Platforms
- [ ] Test on platform A (all sources)
  - Verify all sources detected
  - Verify randomness quality good
- [ ] Test on platform B (subset of sources)
  - Verify correct sources detected
  - Verify randomness quality acceptable
- [ ] Test on minimal platform (timer + RSSI only)
  - Verify graceful fallback
  - Verify still works
  - Verify no crashes

### Integration Testing
- [ ] Test nonce generation (Finding 2)
  - Use new RNG for nonces
  - Verify unique nonces generated
- [ ] Test ephemeral key generation (Finding 7)
  - Use new RNG for Curve25519 keys
  - Verify key quality
- [ ] Test any other crypto operations using RNG
- [ ] Verify no functional regressions

## Phase 7: Error Handling and Edge Cases

### Error Handling
- [ ] Handle case where ALL sources fail
  - Log error
  - Fallback strategy?
  - Fail safely (don't use weak randomness)
- [ ] Handle hardware RNG failure during operation
- [ ] Handle ADC failure during operation
- [ ] Test error paths

### Edge Cases
- [ ] Test rapid successive calls
- [ ] Test concurrent calls (if multi-threaded)
- [ ] Test at system startup (before full init)
- [ ] Test after hardware de-init
- [ ] Test with interrupts disabled (if relevant)

## Phase 8: Code Review and Documentation

### Code Review
- [ ] Review all entropy source implementations
- [ ] Verify no security issues
- [ ] Check for memory leaks
- [ ] Verify no resource leaks (ADC, RNG, etc.)
- [ ] Ensure proper error handling
- [ ] Check coding standards compliance

### Security Review
- [ ] Verify entropy sources are unpredictable
- [ ] Confirm XOR mixing is correct
- [ ] Check for bias in entropy collection
- [ ] Verify cryptographic uses are safe
- [ ] Ensure no entropy leaks via side channels

### Performance Review
- [ ] Measure RNG call latency
- [ ] Verify acceptable for real-time use
- [ ] Check for any performance regressions
- [ ] Optimize if necessary

### Documentation
- [ ] Document entropy source architecture
- [ ] Document which sources available per platform
- [ ] Add inline code comments
- [ ] Document RNG API usage
- [ ] Create troubleshooting guide
- [ ] Document fallback behavior

## Phase 9: Completion

### Final Validation
- [ ] Run complete test suite
- [ ] Verify all success criteria met
- [ ] Test on all target platforms
- [ ] Verify no crashes
- [ ] Review all documentation

### Reporting
- [ ] Create completion report
- [ ] Include platform capability matrix
- [ ] Include randomness quality tests
- [ ] Include test results for all platforms
- [ ] Document any platform-specific issues
- [ ] Send report to Manager

### Cleanup
- [ ] Archive task assignment from inbox
- [ ] Clean up test code
- [ ] Commit code changes (if applicable to role)
- [ ] Update project status to COMPLETED

## Notes

**Critical Success Factors:**
- No crashes on any platform
- Graceful fallback when sources unavailable
- Multiple sources combined via XOR
- Good randomness quality
- All critical crypto uses updated

**Watch Out For:**
- Platform-specific API differences
- Hardware RNG may have bugs (combine with other sources!)
- Timing issues in jitter collection
- ADC may not be truly floating (add external pull-down if needed)
- Don't assume any single source is perfect

**Entropy Source Quality:**
- **Hardware RNG:** High (if hardware is good) - but verify!
- **Timer Jitter:** Medium - varies by platform
- **ADC Noise:** Medium - depends on hardware and environment
- **RSSI:** Low to Medium - varies by RF environment
- **Combined (XOR):** High - defense in depth

**Questions to Resolve:**
- Which platforms are highest priority for testing?
- What's the minimum acceptable randomness quality?
- What should happen if ALL sources fail?
- Are there platform-specific RNG libraries to use?

**Testing Priorities:**
1. Test on primary platform (most important)
2. Test on minimal platform (worst case)
3. Test on representative platforms

**Platform Capability Example:**
```
Platform A (ESP32):
  ✓ Hardware RNG (ESP32 has TRNG)
  ✓ ADC
  ✓ High-res timer
  ✓ RSSI

Platform B (STM32F1):
  ✗ No hardware RNG
  ✓ ADC
  ✓ SysTick timer
  ✓ RSSI

Platform C (ATmega):
  ✗ No hardware RNG
  ✓ ADC
  ✓ Timer
  ✓ RSSI
```

**XOR Mixing Example:**
```cpp
uint32_t getRandomU32() {
    uint32_t entropy = 0;
    uint32_t temp;

    // Always collect timer jitter
    entropy ^= collectTimerJitter();

    // Collect hardware RNG if available
    if (config.has_hw_rng && getHardwareRNG(&temp)) {
        entropy ^= temp;
    }

    // Collect ADC if available
    if (config.has_adc && getADCNoise(&temp)) {
        entropy ^= temp;
    }

    // Collect RSSI if available
    if (config.has_rssi && getRSSINoise(&temp)) {
        entropy ^= temp;
    }

    return entropy;
}
```
