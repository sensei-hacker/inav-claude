# PrivacyLRS Test Infrastructure - Working Notes

**Created:** 2025-11-30
**Author:** Security Analyst / Cryptographer
**Purpose:** Understanding test infrastructure for validating security fixes

---

## Overview

PrivacyLRS uses **PlatformIO's Unit Testing** framework for testing. Tests are written in C++ using the **Unity** testing framework.

### Key Facts
- **Test Framework:** PlatformIO Unit Testing + Unity (C/C++ unit test framework)
- **Build System:** PlatformIO
- **Test Location:** `PrivacyLRS/src/test/`
- **Total Test Directories:** 13
- **Total Test Files:** ~10 C++ test files
- **CI/CD:** GitHub Actions (.github/workflows/build.yml)

---

## Test Directory Structure

```
PrivacyLRS/src/test/
├── README                  # PlatformIO unit testing info
├── test_crc/              # CRC implementation tests
├── test_crsf/             # CRSF protocol tests
├── test_embedded/         # Embedded hardware tests (SKIPPED on native)
├── test_fhss/             # Frequency Hopping Spread Spectrum tests
├── test_fifo/             # FIFO buffer tests
├── test_fmap/             # Frequency map tests
├── test_msp/              # MSP protocol tests
├── test_msp2crsf2msp/     # MSP<->CRSF conversion tests
├── test_msp_vtx/          # MSP VTX tests
├── test_ota/              # Over-the-air packet tests
├── test_stubborn/         # Stubborn sender/receiver tests
└── test_telemetry/        # Telemetry tests
```

### Test File Naming
- Main test files: `test_<component>.cpp`
- Helper files: Various `.h`, `.cpp` files
- Test utilities: Mock objects, system mocks

---

## Test Environments

### Native Environment (`[env:native]`)
- **Platform:** native (runs on host computer, not embedded hardware)
- **Purpose:** Unit testing without requiring physical hardware
- **Configuration:** `PrivacyLRS/src/platformio.ini`
- **Ignored Tests:** `test_embedded` (requires actual hardware)
- **Build Flags:**
  - `-D UNIT_TEST=1`
  - `-D TARGET_NATIVE`
  - `-D CRSF_RX_MODULE`
  - `-D CRSF_TX_MODULE`

### Hardware Environments
- All other environments (ESP32, ESP8285, STM32, etc.) are for embedded targets
- Tests exist for these but require physical hardware
- In CI/CD, only `native` environment is tested

---

## Running Tests

### Prerequisites

1. **PlatformIO installed:**
```bash
python3 -m pip install platformio
```

2. **Navigate to source directory:**
```bash
cd PrivacyLRS/src
```

### Basic Commands

**Run all tests (native environment):**
```bash
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400" pio test -e native
```

**List available tests:**
```bash
pio test -e native --list-tests
```

**Run specific test:**
```bash
pio test -e native --filter test_crc
```

**Verbose output:**
```bash
pio test -e native -v    # verbose
pio test -e native -vv   # very verbose
pio test -e native -vvv  # maximum verbosity
```

**Run without build (if already built):**
```bash
pio test -e native --without-building
```

**Clean and rebuild:**
```bash
pio test -e native --clean
```

### Command Options

| Option | Description |
|--------|-------------|
| `-e native` | Specify environment (native for host-based tests) |
| `--filter <name>` | Run only tests matching name pattern |
| `--list-tests` | Show available tests without running |
| `-v`, `-vv`, `-vvv` | Increase verbosity level |
| `--without-building` | Skip compilation, run existing binaries |
| `--clean` | Clean build files before testing |
| `--upload-port <port>` | Serial port for embedded tests |
| `--test-port <port>` | Port for test communication |

### CI/CD Command (from GitHub Actions)

The GitHub Actions workflow runs:
```bash
cd src
platformio pkg install --platform native
platformio pkg update
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400" pio test -e native
```

---

## Test Framework (Unity)

### Test Structure Example

```cpp
#include <unity.h>

void test_example_function(void) {
    // Arrange
    int expected = 42;

    // Act
    int actual = my_function();

    // Assert
    TEST_ASSERT_EQUAL(expected, actual);
}

void setUp(void) {
    // runs before each test
}

void tearDown(void) {
    // runs after each test
}

void process(void) {
    UNITY_BEGIN();
    RUN_TEST(test_example_function);
    UNITY_END();
}

int main(int argc, char **argv) {
    process();
    return 0;
}
```

### Common Unity Assertions

```cpp
TEST_ASSERT_EQUAL(expected, actual)
TEST_ASSERT_TRUE(condition)
TEST_ASSERT_FALSE(condition)
TEST_ASSERT_NULL(pointer)
TEST_ASSERT_NOT_NULL(pointer)
TEST_ASSERT_EQUAL_STRING(expected, actual)
TEST_ASSERT_EQUAL_MEMORY(expected, actual, num_bytes)
```

---

## Test Categories

### Protocol Tests
- `test_crsf` - Crossfire protocol handling
- `test_msp` - MultiWii Serial Protocol
- `test_msp2crsf2msp` - Protocol conversion
- `test_msp_vtx` - Video transmitter control

### Data Structure Tests
- `test_fifo` - FIFO buffer implementation
- `test_fmap` - Frequency mapping

### Communication Tests
- `test_fhss` - Frequency hopping
- `test_ota` - Over-the-air packets
- `test_telemetry` - Telemetry data
- `test_stubborn` - Reliable transmission

### Algorithm Tests
- `test_crc` - CRC calculation algorithms

### Hardware Tests
- `test_embedded` - **SKIPPED on native** (requires hardware)
  - TX/RX tests for SX1280 radios
  - EEPROM tests
  - Hardware-specific functionality

---

## Important Notes for Security Testing

### What Tests Currently Cover

Based on test directory names:
- ✅ CRC implementations
- ✅ Protocol parsing/encoding (CRSF, MSP)
- ✅ FIFO buffers
- ✅ OTA packet structure
- ✅ Telemetry encoding
- ✅ FHSS frequency selection

### What Tests DON'T Cover (Security Gaps)

**⚠️ NO ENCRYPTION TESTS FOUND**
- No `test_encryption/` directory
- No `test_crypto/` directory
- No `test_chacha/` or `test_cipher/` tests
- No tests for `DecryptMsg()` or `EncryptMsg()`
- No tests for key establishment (`CryptoSetKeys()`, `InitCrypto()`)
- No tests for random number generation (`RandRSSI()`)
- No tests for counter synchronization
- No tests for replay protection

**This is a CRITICAL GAP:**
- Cannot verify security fixes work correctly
- Cannot regression test cryptographic implementations
- Cannot validate counter synchronization fixes
- Cannot test keystream resynchronization mechanisms

### Recommended New Tests Needed

To test security fixes from my findings report, we need:

1. **test_encryption/** directory with:
   - `test_chacha20.cpp` - ChaCha20 cipher basic functionality
   - `test_key_derivation.cpp` - Master key and session key derivation
   - `test_counter_sync.cpp` - **CRITICAL** - Counter synchronization under packet loss
   - `test_encrypt_decrypt.cpp` - Full encryption/decryption cycle
   - `test_resync.cpp` - Resynchronization mechanism
   - `test_replay_protection.cpp` - Replay attack prevention
   - `test_rng.cpp` - Random number generation quality
   - `test_key_rotation.cpp` - Session key rotation (if implemented)

2. **test_security/** directory with:
   - `test_packet_counter.cpp` - Explicit packet counter (when implemented)
   - `test_aead.cpp` - ChaCha20-Poly1305 AEAD (if upgraded)
   - `test_nonce_uniqueness.cpp` - Nonce/IV uniqueness
   - `test_key_management.cpp` - Key lifecycle management

---

## Test Execution Status

**Test Run Date:** 2025-11-30
**Environment:** native
**Status:** Running...

### Expected Results

Based on CI/CD configuration, all tests in `native` environment should:
- Build successfully
- Execute without errors
- Report PASSED status

### Actual Results

**To be updated after test completion**

---

## Test Durations (To Be Measured)

- **Full test suite:** TBD
- **Individual tests:** TBD
- **Build time:** TBD

---

## Dependencies

### Required Packages
- PlatformIO Core
- Platform: native
- Framework: Unity (automatically managed by PlatformIO)

### Auto-installed Libraries
PlatformIO manages dependencies via `platformio.ini`:
- Unity testing framework
- Various ELRS/PrivacyLRS libraries

---

## Troubleshooting

### Common Issues

**Issue:** "platformio: command not found"
**Solution:** Install PlatformIO: `python3 -m pip install platformio`
**Alternative:** Add `~/.local/bin` to PATH

**Issue:** "Environment 'native' does not exist"
**Solution:** Ensure you're in `PrivacyLRS/src/` directory with `platformio.ini`

**Issue:** Tests fail with "No such file or directory"
**Solution:** Run from correct directory: `cd PrivacyLRS/src && pio test -e native`

**Issue:** "Platform 'native' is not installed"
**Solution:** `platformio pkg install --platform native`

**Issue:** Build failures
**Solution:** Update packages: `platformio pkg update`

**Issue:** Obsolete PlatformIO version warning
**Solution:** Multiple PIO installations exist, remove old ones (usually safe to ignore)

---

## Testing Workflow for Security Fixes

### Step 1: Create Tests First (TDD Approach)
```bash
# Create test directory
mkdir -p PrivacyLRS/src/test/test_encryption

# Write failing test that demonstrates the vulnerability
# Example: test_counter_sync_packet_loss.cpp
```

### Step 2: Run Tests (Should FAIL)
```bash
cd PrivacyLRS/src
pio test -e native --filter test_encryption
# Expected: FAILED (demonstrates vulnerability exists)
```

### Step 3: Implement Fix
```bash
# Edit PrivacyLRS/src/src/common.cpp
# Apply security fix from findings report
```

### Step 4: Run Tests (Should PASS)
```bash
pio test -e native --filter test_encryption
# Expected: PASSED (fix resolves vulnerability)
```

### Step 5: Regression Testing
```bash
# Run ALL tests to ensure fix doesn't break existing functionality
pio test -e native
# Expected: ALL PASSED
```

### Step 6: Document Results
```bash
# Record test results
# Compare before/after metrics
# Verify no performance degradation
```

---

## Next Steps

1. ✅ Run full test suite to establish baseline
2. ⬜ Create encryption/security test suite
3. ⬜ Write tests for all 8 security findings
4. ⬜ Implement fixes
5. ⬜ Validate with tests
6. ⬜ Performance benchmarking

---

## References

- PlatformIO Unit Testing: https://docs.platformio.org/page/plus/unit-testing.html
- Unity Testing Framework: http://www.throwtheswitch.org/unity
- ExpressLRS (upstream): https://www.expresslrs.org/
- PrivacyLRS README: `PrivacyLRS/README.md`
- CI/CD Configuration: `PrivacyLRS/.github/workflows/build.yml`

---

## File Locations Quick Reference

| Item | Path |
|------|------|
| Test directory | `PrivacyLRS/src/test/` |
| PlatformIO config | `PrivacyLRS/src/platformio.ini` |
| Encryption code | `PrivacyLRS/src/src/common.cpp` (DecryptMsg, EncryptMsg) |
| RX crypto | `PrivacyLRS/src/src/rx_main.cpp` (CryptoSetKeys) |
| TX crypto | `PrivacyLRS/src/src/tx_main.cpp` (InitCrypto, RandRSSI) |
| Crypto header | `PrivacyLRS/src/include/encryption.h` |
| Build flags | `PrivacyLRS/src/python/build_flags.py` |
| GitHub CI | `PrivacyLRS/.github/workflows/build.yml` |

---

**END OF NOTES**
