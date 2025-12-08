# Finding #5: ChaCha12 vs ChaCha20 Benchmark Design

**Date:** 2025-12-02 04:15
**Project:** privacylrs-fix-finding5-chacha-benchmark
**Security Analyst:** Cryptographer

---

## Objective

Measure the performance difference between ChaCha12 (12 rounds, current) and ChaCha20 (20 rounds, standard) on target hardware platforms to make a data-driven decision on upgrading to RFC 8439 standard.

---

## Current Status

**Confirmed Implementation:**
- **RX:** `ChaCha cipher(12);` in `src/rx_main.cpp:63`
- **TX:** `ChaCha cipher(12);` in `src/tx_main.cpp:36`
- **Current:** ChaCha12 (12 rounds)
- **Standard:** ChaCha20 (20 rounds) per RFC 8439

---

## Target Hardware Platforms

### Priority 1: Most Common
1. **ESP32** (240MHz dual-core) - Original, widely deployed
2. **ESP8285** (80/160MHz single-core) - Lower-end, performance-constrained
3. **ESP32S3** (240MHz dual-core) - Newer, better performance

### Priority 2: Additional Coverage
4. **ESP32C3** (RISC-V) - Different architecture
5. **STM32** (ARM Cortex-M) - Microcontroller platform

**Benchmark focus:** ESP32, ESP8285 (worst case), ESP32S3 (best case)

---

## Benchmark Metrics

### 1. Throughput
- **Metric:** Packets encrypted/decrypted per second
- **Test:** Encrypt 1000 packets, measure time
- **Packet sizes:** 8 bytes (OTA4), 14 bytes (OTA8)

### 2. Latency
- **Metric:** Time per single encryption operation (microseconds)
- **Test:** Single packet encryption, measure time
- **Important for:** Real-time packet rates (50Hz, 150Hz, 250Hz)

### 3. CPU Usage
- **Metric:** Percentage of CPU time spent in encryption
- **Calculate:** (encryption_time / packet_interval) × 100%
- **Example:** At 250Hz, packet interval = 4ms

### 4. Overhead Percentage
- **Metric:** (ChaCha20_time - ChaCha12_time) / ChaCha12_time × 100%
- **Decision threshold:** If <10%, upgrade to ChaCha20

---

## Benchmark Design

### Test Implementation

**Location:** `src/test/test_encryption/test_chacha_benchmark.cpp`

**Test structure:**
```cpp
void benchmark_chacha12_throughput()
{
  ChaCha cipher(12);
  cipher.setKey(key, 32);
  cipher.setIV(nonce, 8);
  cipher.setCounter(counter, 8);

  uint32_t start = micros();
  for (int i = 0; i < 1000; i++) {
    cipher.encrypt(output, input, 8);  // OTA4 packet size
  }
  uint32_t elapsed = micros() - start;

  // Calculate throughput
  float packets_per_second = 1000.0 / (elapsed / 1000000.0);
  float us_per_packet = elapsed / 1000.0;
}

void benchmark_chacha20_throughput()
{
  ChaCha cipher(20);  // 20 rounds
  // ... same test
}
```

### Test Cases

1. **test_benchmark_chacha12_8byte** - ChaCha12, 8-byte packets
2. **test_benchmark_chacha20_8byte** - ChaCha20, 8-byte packets
3. **test_benchmark_chacha12_14byte** - ChaCha12, 14-byte packets
4. **test_benchmark_chacha20_14byte** - ChaCha20, 14-byte packets
5. **test_benchmark_overhead_calculation** - Calculate percentage overhead

---

## Expected Results

### Hypothesis (from Finding #5)
- **Expected overhead:** <1-2% on ARM Cortex-M and ESP32
- **ChaCha20 performance:** Still very fast even with 67% more rounds (20 vs 12)

### Decision Criteria

| Overhead | Decision |
|----------|----------|
| <5% | **Upgrade to ChaCha20** - negligible performance cost |
| 5-10% | **Consider upgrade** - analyze CPU headroom |
| 10-20% | **Keep ChaCha12** - significant performance impact |
| >20% | **Keep ChaCha12** - unacceptable performance cost |

**Note:** ChaCha is very efficient; 67% more rounds ≠ 67% more time due to:
- Pipeline efficiency
- Cache effects
- Optimized quarter-round operations

---

## Real-World Performance Analysis

### Packet Rate Scenarios

**Packet rates:**
- 50Hz (D250/D500) - 20ms intervals
- 150Hz (D250 Fast) - 6.67ms intervals
- 250Hz (D500 Fast) - 4ms intervals

**Example calculation for 250Hz:**
- Packet interval: 4000μs
- If ChaCha12: 10μs per packet → 0.25% CPU
- If ChaCha20: 12μs per packet → 0.30% CPU
- Overhead: +0.05% CPU (negligible)

### CPU Headroom

If encryption takes <1% of CPU time, even a 50% increase (0.5% → 0.75%) is acceptable.

---

## Implementation Plan

### Phase 1: Benchmark Implementation (1-2h)

**Tasks:**
1. Create `src/test/test_encryption/test_chacha_benchmark.cpp`
2. Implement throughput benchmarks (ChaCha12/20, 8/14 bytes)
3. Implement latency benchmarks (single packet timing)
4. Calculate overhead percentages
5. Add to test suite

### Phase 2: Platform Testing (2-3h)

**Tasks:**
1. **ESP32 testing:**
   - Build for `Unified_ESP32_2400_RX_via_UART`
   - Run benchmarks, collect data
   - Test at 50Hz, 150Hz, 250Hz packet rates

2. **ESP8285 testing:**
   - Build for `Unified_ESP8285_2400_RX_via_UART`
   - Run benchmarks, collect data
   - Focus on worst-case performance

3. **ESP32S3 testing:**
   - Build for `Unified_ESP32S3_2400_RX_via_UART`
   - Run benchmarks, collect data
   - Show best-case performance

### Phase 3: Analysis (1h)

**Tasks:**
1. Compile results table
2. Calculate overhead percentages
3. Analyze CPU headroom
4. Compare against RFC 8439 recommendations
5. Make upgrade recommendation

### Phase 4: Report (1h)

**Tasks:**
1. Create detailed findings report
2. Include performance data
3. Provide upgrade recommendation
4. Document security vs performance trade-off

**Total estimated time: 5-7 hours**

---

## Benchmark Code Structure

### Test File Organization

```
src/test/test_encryption/
├── test_encryption.cpp          # Existing security tests
├── test_chacha_benchmark.cpp    # NEW: Performance benchmarks
└── README.md                     # Update with benchmark info
```

### Benchmark Functions

```cpp
// Throughput tests
void test_chacha12_throughput_8byte();
void test_chacha20_throughput_8byte();
void test_chacha12_throughput_14byte();
void test_chacha20_throughput_14byte();

// Latency tests
void test_chacha12_latency_single_packet();
void test_chacha20_latency_single_packet();

// Overhead calculation
void test_chacha_overhead_percentage();

// Real-world scenario tests
void test_chacha_cpu_usage_50hz();
void test_chacha_cpu_usage_150hz();
void test_chacha_cpu_usage_250hz();
```

---

## Expected Benchmark Output

```
Benchmark: ChaCha12 vs ChaCha20 Performance
===========================================

Platform: ESP32 @ 240MHz
-----------------------
ChaCha12 (8 bytes):  11.2μs per packet  (89,285 packets/sec)
ChaCha20 (8 bytes):  13.1μs per packet  (76,335 packets/sec)
Overhead: +16.9%

ChaCha12 (14 bytes): 11.8μs per packet  (84,745 packets/sec)
ChaCha20 (14 bytes): 13.8μs per packet  (72,463 packets/sec)
Overhead: +16.9%

CPU Usage @ 250Hz (4ms interval):
  ChaCha12: 0.28%
  ChaCha20: 0.33%
  Additional: +0.05%

Platform: ESP8285 @ 160MHz
--------------------------
ChaCha12 (8 bytes):  22.5μs per packet  (44,444 packets/sec)
ChaCha20 (8 bytes):  26.3μs per packet  (38,022 packets/sec)
Overhead: +16.9%

CPU Usage @ 250Hz (4ms interval):
  ChaCha12: 0.56%
  ChaCha20: 0.66%
  Additional: +0.10%

Recommendation: UPGRADE TO CHACHA20
- Overhead: ~17% (acceptable for security gain)
- CPU impact: <0.7% even on slowest platform
- Aligns with RFC 8439 standard
- Improved security margin
```

---

## Security vs Performance Trade-off

### Security Gain
- **ChaCha20:** Standard, extensively analyzed, recommended by IETF
- **ChaCha12:** Experimental, less cryptanalytic scrutiny
- **Margin:** 20 rounds provides stronger security guarantees

### Performance Cost
- **Expected:** ~15-20% slower encryption
- **Absolute:** <1% of total CPU time
- **Impact:** Negligible on 240MHz ESP32 platforms

### Decision Factors
1. **Standards compliance:** ChaCha20 is RFC 8439 standard
2. **Security margin:** 20 rounds > 12 rounds
3. **Performance:** Modern processors handle ChaCha20 easily
4. **Reputation:** Using non-standard crypto reduces confidence

---

## Next Steps

1. ✅ Research complete - ChaCha12 currently used
2. ✅ Finding #5 reviewed - benchmark approach confirmed
3. ✅ Platforms identified - ESP32, ESP8285, ESP32S3
4. ✅ Benchmark design complete
5. ⏸️ Implement benchmark code
6. ⏸️ Run tests on hardware
7. ⏸️ Analyze results
8. ⏸️ Make recommendation

---

**Security Analyst / Cryptographer**
2025-12-02 04:15
