# INAV Test Tools

Tools for testing INAV firmware optimizations.

## Tools

### msp_benchmark.py
Python script for benchmarking MSP request/response performance.

**Usage:**
```bash
# Start SITL first
cd inav
./inav_SITL

# Run benchmark
python3 msp_benchmark.py [host] [port]
# Defaults: localhost 5761
```

### run_comparison_test.sh
Automated comparison script for testing baseline vs optimized builds.

**Usage:**
```bash
./run_comparison_test.sh
# Follow prompts to switch between baseline and optimized SITL
```

### 2025-11-25-test-instructions.md
Step-by-step instructions for manual SITL testing with Configurator.

### BUILDING_SITL.md
Reference documentation for building INAV SITL binaries from source.

## Requirements

- Python 3
- INAV SITL binaries (baseline and optimized)
- bash, bc (for comparison script)

## Benchmark Test Results (2025-11-25)

### Test Setup
- **Baseline**: master branch (unmodified)
- **Optimized**: faster_msp_when_disarmed branch (2 commands per cycle when disarmed)
- **Forced**: maxCommandsPerCycle hardcoded to 2 (always)
- **Methodology**: Send 250 MSP requests as fast as possible, measure firmware processing rate

### Results Summary

| Version | Throughput | Responses Received | Notes |
|---------|------------|-------------------|-------|
| Baseline | 123.3 req/sec | 200/250 (80%) | Master branch |
| Optimized (with ARMING_FLAG check) | 121.0 req/sec | 200/250 (80%) | No improvement |
| Forced (always 2 commands) | 121.1 req/sec | 200/250 (80%) | No improvement |

**All three versions show identical performance (~97-99 responses/sec).**

### Key Findings

1. **No observable improvement**: The optimization to process 2 commands per cycle shows no measurable performance gain in SITL testing.

2. **20% packet loss**: All versions drop 50 out of 250 requests (20%), suggesting the firmware cannot keep up with the request flood rate.

3. **Bottleneck is elsewhere**: Even when forcing the firmware to always attempt processing 2 commands per cycle, performance remains identical. This indicates:
   - The serial receive buffer may not have multiple commands ready when the task runs
   - TCP/serial data delivery rate may be the limiting factor
   - Another bottleneck exists before the command processing loop

4. **Throughput matches cycle rate**: ~97 responses/sec ≈ 100 Hz serial task rate, indicating exactly 1 command processed per cycle regardless of the code change.

### Next Steps

Further investigation needed to identify the actual bottleneck:
- Profile the serial TCP receive path
- Check if `serialRxBytesWaiting()` ever reports multiple bytes available
- Investigate TCP socket buffering and delivery timing
- Test with real hardware (USB CDC) instead of SITL

---

## Related Skills

- **build-sitl** - Build SITL firmware for testing
- **sitl-arm** - Arm SITL for automated testing
- **msp-protocol** - MSP protocol reference and command definitions
- **run-configurator** - Run configurator for manual SITL testing
