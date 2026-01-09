# Finding #5 - Ready for Hardware Testing

**Date:** 2025-12-02 11:30
**To:** Manager
**From:** Security Analyst / Cryptographer
**Subject:** Finding #5 Firmware Built - Ready for Hardware Test
**Priority:** MEDIUM
**Project:** privacylrs-fix-finding5-chacha-benchmark

---

## Status: READY FOR HARDWARE TESTING ✅

The ChaCha12 vs ChaCha20 benchmark firmware is built and ready to flash to hardware for performance testing.

---

## Summary

**Objective:** Measure real-world ChaCha12 vs ChaCha20 performance on actual hardware to validate upgrade recommendation.

**Progress:**
- ✅ Benchmark code implemented
- ✅ Firmware built successfully for NamimnoRC 2.4 GHz Flash OLED TX
- ✅ Native x86 testing complete (+30.8% overhead measured)
- ⏳ **Waiting for hardware testing on TX module**

---

## Firmware Ready

**Target platform:** NamimnoRC 2.4 GHz Flash OLED TX (STM32)

**Firmware files:**
- `firmware-chacha-benchmark-namimnorc-tx.bin` (40 KB)
- `firmware-chacha-benchmark-namimnorc-tx.elrs` (40 KB)

**Location:** `/home/raymorris/Documents/planes/inavflight/PrivacyLRS/`

**Build status:** SUCCESS (60.8% flash, 43.1% RAM)

---

## Why STM32 TX Instead of ESP32 RX?

**Original plan:** Test on BetaFPV 2.4 GHz RX (ESP32)

**Change:** Test on NamimnoRC TX (STM32)

**Reason:** ESP32 builds still blocked by pre-existing infrastructure issues:
- `FS.h: No such file or directory`
- ESPAsyncWebServer dependency missing
- Same issue blocking PR #18/#19/#20

**Advantages of STM32:**
- ✅ Clean build (no infrastructure issues)
- ✅ Simpler architecture (easier to interpret)
- ✅ Lower clock speed (72 MHz) = realistic worst-case
- ✅ Common TX module platform

---

## Testing Procedure

### Flash Firmware

**Option 1:** Copy `.elrs` file to SD card → Flash via TX menu

**Option 2:** Direct flash via ST-LINK/USB

### Capture Results

Connect serial terminal at 460800 baud:
```bash
pio device monitor -b 460800 | tee benchmark_results_stm32.txt
```

### What Happens

1. TX boots normally
2. After 2 seconds, benchmark runs automatically
3. Results output to serial
4. LED flashes 5 times when complete
5. TX loops forever (results remain visible)

**Duration:** ~5 seconds for benchmark to complete

---

## Expected Results

### Native x86 (Already Measured)
- ChaCha12: 0.07 μs/packet
- ChaCha20: 0.09 μs/packet
- **Overhead: +30.8%**
- **CPU @ 250Hz: 0.003%**

### Projected STM32 (72 MHz)
- ChaCha12: ~2.5 μs/packet
- ChaCha20: ~3.2 μs/packet
- **Overhead: ~30%** (should stay similar)
- **CPU @ 250Hz: ~0.08%**

**Even with 42x slower clock, ChaCha20 uses <0.1% CPU.**

---

## Decision Criteria

**After hardware test, we will confirm:**

✅ **Upgrade to ChaCha20** if:
- Overhead <50%
- CPU usage <5%
- Absolute time impact trivial

⚠️ **Reconsider** if:
- Overhead 50-100%
- CPU usage 5-10%

❌ **Keep ChaCha12** if:
- Overhead >100%
- CPU usage >10%

**Current expectation:** Results will confirm upgrade ✅

---

## Current Recommendation (Pre-Hardware Test)

**Recommendation:** UPGRADE TO CHACHA20 ✅

**Based on:**
- Native x86 measured: +30.8% overhead
- Absolute impact: +0.02 μs (trivial)
- Theoretical STM32: ~30% overhead, <0.1% CPU

**Hardware test purpose:**
- Validate recommendation on target platform
- Provide measured data for justification
- Confirm no unexpected performance issues

---

## Timeline

**Completed:**
- Research: 0.25h
- Analysis: 1.0h
- Benchmark implementation: 0.5h
- Native testing: 0.5h
- Firmware build: 0.25h

**Total so far:** 2.5 hours

**Remaining:**
- Hardware testing: 0.5h (waiting for hardware access)
- Final report: 0.25h

**Total estimated:** 3.25 hours (vs 4-6h original estimate)

---

## Next Steps

### Immediate (Waiting for Hardware)

1. Flash benchmark firmware to NamimnoRC TX
2. Capture serial output to file
3. Record key performance metrics
4. Compare with native and projected results

### After Hardware Test

1. Update `finding5-hardware-benchmark-results.md` with STM32 data
2. Send final recommendation to Manager with hardware measurements
3. If approved, create implementation branch
4. Submit pull request for ChaCha20 upgrade

---

## Documentation

**Status document:**
`claude/security-analyst/finding5-benchmark-hardware-testing-status.md`

**Quick start guide:**
`PrivacyLRS/BENCHMARK-QUICK-START.md`

**Contains:**
- Flashing instructions
- Serial capture procedure
- Data recording template
- Restore procedure
- Full analysis framework

---

## Questions?

If you have questions about:
- Testing procedure
- Expected results
- Decision criteria
- Timeline

Please let me know. Otherwise, awaiting hardware access to complete testing.

---

## Summary

**Status:** Firmware ready, waiting for hardware test ✅

**Confidence:** High (native results support upgrade)

**Risk:** Low (STM32 should perform as projected)

**ETA:** 0.75 hours after hardware access

---

**Security Analyst / Cryptographer**
2025-12-02 11:30
