# Finding #5 - ChaCha20 Benchmark Hardware Testing Status

**Date:** 2025-12-02 11:30
**Security Analyst:** Cryptographer
**Project:** privacylrs-fix-finding5-chacha-benchmark
**Status:** READY FOR HARDWARE TESTING

---

## Summary

Hardware benchmark firmware is built and ready to flash to **NamimnoRC 2.4 GHz Flash OLED TX** module.

**Goal:** Measure real-world ChaCha12 vs ChaCha20 performance on actual hardware to validate upgrade recommendation.

---

## Current Status

### Completed ✅

1. **Benchmark code implemented**
   - Inline benchmark function in `tx_main.cpp`
   - Measures ChaCha12 vs ChaCha20 on 8-byte and 14-byte packets
   - 1000 iterations per test for accuracy
   - Outputs detailed performance metrics via Serial

2. **Firmware built successfully**
   - Target: NamimnoRC 2.4 GHz Flash OLED TX (STM32)
   - Platform: STM32 (more reliable than ESP32 for this test)
   - Build: SUCCESS
   - Size: 40 KB (60.8% flash, 43.1% RAM)

3. **Build infrastructure updated**
   - Pulled latest from `secure_01` branch
   - Contains Finding #4 security logging fixes
   - Build flags configured for benchmark mode

### Pending ⏳

1. **Flash firmware to TX module**
2. **Run hardware benchmark**
3. **Capture serial output**
4. **Analyze results**
5. **Update Finding #5 recommendation with hardware data**

---

## Firmware Files

### Location

**Base directory:** `/home/raymorris/Documents/planes/inavflight/PrivacyLRS/`

**Firmware files:**
```
firmware-chacha-benchmark-namimnorc-tx.bin   (40 KB)  - Binary for ST-LINK
firmware-chacha-benchmark-namimnorc-tx.elrs  (40 KB)  - For WiFi flash
```

**Build directory:**
```
src/.pio/build/NamimnoRC_FLASH_2400_TX_via_STLINK/firmware.*
```

### Git Status

**Branch:** `secure_01`
**Commit:** 9fd4078e (latest, includes Finding #4 secure logging)

**Modified files:**
- `src/src/tx_main.cpp` - Added benchmark code
- `src/src/rx_main.cpp` - Added benchmark code (not used for TX test)

**Note:** These modifications are NOT committed. They contain benchmark code only, not production changes.

---

## Hardware Test Procedure

### Equipment Needed

- NamimnoRC 2.4 GHz Flash OLED TX module
- USB cable or ST-LINK programmer
- Computer with serial terminal (or `pio device monitor`)

### Flashing Instructions

#### Option 1: Via WiFi (Recommended)

1. Copy `firmware-chacha-benchmark-namimnorc-tx.elrs` to SD card
2. Insert SD card into TX module
3. Power on TX module
4. Navigate to menu: "Flash External ELRS"
5. Wait for flash to complete
6. TX will reboot automatically

#### Option 2: Via ST-LINK

```bash
cd /home/raymorris/Documents/planes/inavflight/PrivacyLRS/src

# Flash firmware
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DUSE_ENCRYPTION -DRUN_CHACHA_BENCHMARK -DDEBUG_LOG" \
  pio run -e NamimnoRC_FLASH_2400_TX_via_STLINK --target upload
```

### Capturing Benchmark Results

#### Method 1: PlatformIO Monitor

```bash
cd /home/raymorris/Documents/planes/inavflight/PrivacyLRS/src
pio device monitor -b 460800
```

#### Method 2: Screen

```bash
screen /dev/ttyUSB0 460800
```

#### Method 3: Minicom

```bash
minicom -D /dev/ttyUSB0 -b 460800
```

**Important:**
- Baud rate: **460800** (STM32 default)
- The benchmark runs immediately after boot
- Results display once, then TX loops forever
- LED flashes 5 times when benchmark completes
- Save the output to a file for analysis

#### Saving Output to File

```bash
# Using pio device monitor with tee
pio device monitor -b 460800 | tee benchmark_results_stm32.txt

# Or redirect to file
pio device monitor -b 460800 > benchmark_results_stm32.txt
```

---

## Expected Output Format

```
========================================
ChaCha12 vs ChaCha20 Hardware Benchmark
Finding #5 - Hardware Performance Test
========================================

Testing ChaCha12 (8-byte packets)...
  Time: XXXX us for 1000 iterations
  Average: X.XX us/packet
  Throughput: XXXXX packets/sec

Testing ChaCha20 (8-byte packets)...
  Time: XXXX us for 1000 iterations
  Average: X.XX us/packet
  Throughput: XXXXX packets/sec

Testing ChaCha12 (14-byte packets)...
  Time: XXXX us for 1000 iterations
  Average: X.XX us/packet
  Throughput: XXXXX packets/sec

Testing ChaCha20 (14-byte packets)...
  Time: XXXX us for 1000 iterations
  Average: X.XX us/packet
  Throughput: XXXXX packets/sec

========================================
OVERHEAD ANALYSIS
========================================
8-byte packets:  +XX.X%
14-byte packets: +XX.X%
Average:         +XX.X%

========================================
CPU USAGE @ DIFFERENT PACKET RATES
========================================
50Hz (20.00ms interval):
  ChaCha12: X.XXX%
  ChaCha20: X.XXX%
  Additional: +X.XXX%

150Hz (6.67ms interval):
  ChaCha12: X.XXX%
  ChaCha20: X.XXX%
  Additional: +X.XXX%

250Hz (4.00ms interval):
  ChaCha12: X.XXX%
  ChaCha20: X.XXX%
  Additional: +X.XXX%

========================================
BENCHMARK COMPLETE
========================================
```

---

## Data to Record

After running the benchmark, record these values:

### ChaCha12 Performance
- [ ] 8-byte packets: _____ μs/packet
- [ ] 14-byte packets: _____ μs/packet
- [ ] Throughput (8-byte): _____ packets/sec
- [ ] Throughput (14-byte): _____ packets/sec

### ChaCha20 Performance
- [ ] 8-byte packets: _____ μs/packet
- [ ] 14-byte packets: _____ μs/packet
- [ ] Throughput (8-byte): _____ packets/sec
- [ ] Throughput (14-byte): _____ packets/sec

### Overhead Analysis
- [ ] 8-byte overhead: +_____%
- [ ] 14-byte overhead: +_____%
- [ ] Average overhead: +_____%

### CPU Usage @ 250Hz (Most Important)
- [ ] ChaCha12: _____%
- [ ] ChaCha20: _____%
- [ ] Additional: +_____%

---

## Analysis After Testing

Once we have the hardware results, we need to:

1. **Compare with native x86 results:**
   - Native (x86_64): +30.8% overhead
   - STM32 (actual): ____%

2. **Validate theoretical projections:**
   - We projected STM32 would be slower but still <1% CPU
   - Confirm absolute impact (μs) is still negligible

3. **Update recommendation:**
   - If overhead <50% and CPU <5%: Upgrade to ChaCha20 ✅
   - If overhead 50-100% and CPU <10%: Consider upgrade ⚠️
   - If overhead >100% or CPU >10%: Keep ChaCha12 ❌

4. **Document findings:**
   - Update `finding5-hardware-benchmark-results.md` with STM32 data
   - Update final recommendation email to Manager
   - Create pull request if upgrade approved

---

## Technical Details

### Benchmark Code Location

**File:** `src/src/tx_main.cpp`
**Function:** `runChaCha20Benchmark()` (lines 1597-1805)
**Activation:** Conditional compilation with `-DRUN_CHACHA_BENCHMARK`

**Key features:**
- Uses `micros()` for microsecond timing
- 10-iteration warm-up before each test
- 1000-iteration test runs for accuracy
- Tests both 8-byte (OTA4) and 14-byte (OTA8) packets
- Calculates percentage overhead
- Estimates CPU usage at different packet rates

### Build Configuration

**Environment:** `NamimnoRC_FLASH_2400_TX_via_STLINK`

**Build flags:**
```
-DRegulatory_Domain_ISM_2400   # 2.4 GHz regulatory domain
-DUSE_ENCRYPTION               # Enable encryption code
-DRUN_CHACHA_BENCHMARK         # Enable benchmark at startup
-DDEBUG_LOG                    # Enable serial debug output
```

**Platform:** STM32F103 (ARM Cortex-M3)
- Clock: 72 MHz
- Flash: 64 KB (60.8% used)
- RAM: 20 KB (43.1% used)

### Why STM32 Instead of ESP32?

**ESP32 build issues:**
- `FS.h: No such file or directory` error
- ESPAsyncWebServer dependency missing
- Pre-existing build infrastructure issues
- Blocked same as PR #18/#19/#20

**STM32 advantages:**
- Clean build (no infrastructure issues)
- Simpler architecture (easier to interpret results)
- Lower clock speed (72 MHz vs 240 MHz) = more realistic worst-case
- NamimnoRC TX is common hardware platform

---

## Comparison Data Available

### Native x86_64 Results (Already Measured)

**Platform:** Linux x86_64 @ ~3 GHz

**Results:**
- ChaCha12 (8-byte): 0.07 μs/packet
- ChaCha20 (8-byte): 0.09 μs/packet
- **Overhead: +31.9%** (8-byte), **+29.7%** (14-byte)
- **Average: +30.8%**

**CPU @ 250Hz:**
- ChaCha12: 0.002%
- ChaCha20: 0.003%
- Additional: +0.001%

**Absolute impact:** +0.02 μs per packet (trivial)

### Theoretical STM32 Projection

**Clock scaling:** 3000 MHz → 72 MHz = ~42x slower

**BUT:** STM32 is simpler architecture, so real factor likely 30-50x

**Projected STM32:**
- ChaCha12: 0.07 μs × 35 = **~2.5 μs/packet**
- ChaCha20: 0.09 μs × 35 = **~3.2 μs/packet**
- Overhead: still **~30%**

**CPU @ 250Hz (4ms interval):**
- ChaCha12: 2.5 μs / 4000 μs = **0.063%**
- ChaCha20: 3.2 μs / 4000 μs = **0.080%**
- Additional: **+0.017%**

**Conclusion:** Even if STM32 is 50x slower than x86, ChaCha20 still uses <0.1% CPU.

---

## After Hardware Testing: Next Steps

### Step 1: Capture Results ✅
- Flash firmware to TX module
- Record serial output
- Save output to file: `benchmark_results_stm32.txt`

### Step 2: Analyze Results ✅
- Compare with native x86 results
- Calculate absolute impact (μs)
- Verify CPU usage is acceptable
- Determine if overhead matches projections

### Step 3: Update Documentation ✅
- Update `finding5-hardware-benchmark-results.md`
- Add STM32 platform section
- Include actual measured values
- Compare with theoretical projections

### Step 4: Final Recommendation ✅
- Confirm or revise upgrade recommendation
- Create email to Manager with hardware data
- Justify recommendation with measured performance

### Step 5: Implementation (if approved) ✅
- Create branch: `fix-finding5-upgrade-chacha20`
- Modify `src/src/rx_main.cpp:63`: `ChaCha cipher(12)` → `ChaCha cipher(20)`
- Modify `src/src/tx_main.cpp:36`: `ChaCha cipher(12)` → `ChaCha cipher(20)`
- Add comments with measured overhead
- Create pull request
- Request Developer review and merge

---

## Questions to Answer with Hardware Data

1. **What is the actual overhead on STM32?**
   - Native: +30.8%
   - STM32: ____%

2. **Does STM32 overhead match our projection (+30%)?**
   - Projected: ~30%
   - Actual: ____%
   - Difference: ____%

3. **What is the absolute time impact?**
   - Native: +0.02 μs
   - STM32: +_____ μs

4. **What is the CPU usage at 250Hz?**
   - ChaCha12: ____%
   - ChaCha20: ____%
   - Is this acceptable? YES / NO

5. **Does the data support upgrading to ChaCha20?**
   - Performance: ACCEPTABLE / UNACCEPTABLE
   - Security benefit: SIGNIFICANT
   - Final recommendation: UPGRADE / KEEP CHACHA12

---

## Restoring Normal Firmware

After testing, to restore normal (non-benchmark) firmware:

```bash
cd /home/raymorris/Documents/planes/inavflight/PrivacyLRS/src

# Build normal firmware (without benchmark)
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DUSE_ENCRYPTION" \
  pio run -e NamimnoRC_FLASH_2400_TX_via_STLINK --target upload
```

Or flash a regular release firmware from the web UI.

---

## Files to Update After Testing

1. **`finding5-hardware-benchmark-results.md`**
   - Add STM32 section
   - Include measured values
   - Update recommendation if needed

2. **Email to Manager**
   - Create: `sent/2025-12-02-finding5-stm32-results-final.md`
   - Include hardware test results
   - Confirm or revise recommendation
   - Request approval for implementation

3. **If upgrade approved:**
   - Create implementation branch
   - Modify rx_main.cpp and tx_main.cpp
   - Create pull request

---

## Current Recommendation (Before Hardware Test)

**Based on native x86 data:** **UPGRADE TO CHACHA20** ✅

**Justification:**
- Measured overhead: +30.8% (relative)
- Absolute impact: +0.02 μs (trivial)
- CPU usage: +0.001% @ 250Hz
- Security benefit: RFC 8439 standard
- Risk: None
- Implementation: 2 lines of code

**Hardware test purpose:**
- Validate recommendation on actual target platform
- Measure real-world STM32 performance
- Confirm CPU usage is acceptable
- Provide data-driven justification for Manager approval

---

## Summary

**Ready for testing:** Firmware built and ready to flash ✅

**Waiting for:** Hardware testing on NamimnoRC TX module ⏳

**Expected result:** STM32 overhead ~30%, CPU usage <0.1%

**Expected outcome:** Confirms upgrade to ChaCha20 ✅

**Time estimate:** 15-30 minutes for flashing, testing, and capturing results

---

**Security Analyst / Cryptographer**
2025-12-02 11:30
