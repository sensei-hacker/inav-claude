# Task Assignment: Debug ESP32 ChaCha Benchmark Crash

**Date:** 2025-12-05 12:45
**Project:** privacylrs-fix-finding5-chacha-benchmark
**Priority:** HIGH
**Estimated Effort:** 2-4 hours
**Branch:** From `secure_01` (PrivacyLRS repo)

---

## Task

Debug the ESP32 crash that occurs when running the ChaCha20 benchmark. Use incremental testing approach to isolate the root cause.

---

## Background

The Security Analyst discovered a critical issue while testing Finding #5 (ChaCha20 upgrade):

**Crash Details:**
- Hardware: ESP32 TX module
- Error: `Guru Meditation Error: Core 1 panic'ed (LoadProhibited)`
- PC: 0x400d4314
- EXCVADDR: 0x00000000 (null pointer dereference)
- Behavior: Boot loop (continuous crash/reboot)
- Occurs in both setup() and loop() (after 5-second delay)

**Critical Question:** Is ChaCha encryption working in production on ESP32?

---

## What to Do

### Phase 1: Minimal Serial Test (30 min)

Create a very simple test file for ESP32 to verify basic functionality:

1. Create minimal test firmware with ONLY:
   - Basic ESP32 initialization
   - Serial communication over USB
   - Simple "hello world" message every second

2. Build and flash to ESP32 TX module

3. Verify:
   - ✅ No crashes
   - ✅ Serial communication works
   - ✅ System runs stable for 1+ minutes

**Deliverable:** Confirm ESP32 basic functionality works

---

### Phase 2: Add Components Incrementally (1-2 hours)

Once basic serial works, add ONE component at a time:

**Step 2a: Add ChaCha library include**
```cpp
#include "ChaCha.h"
// Don't use it yet, just include it
```
- Build, flash, test
- Does it still boot?

**Step 2b: Create single ChaCha object**
```cpp
ChaCha cipher(12);  // ChaCha12 (current production)
```
- Build, flash, test
- Does it crash on object creation?

**Step 2c: Initialize ChaCha with key/nonce**
```cpp
uint8_t key[32] = {0};
uint8_t nonce[12] = {0};
cipher.setKey(key, 32);
cipher.setIV(nonce, 12);
```
- Build, flash, test
- Does initialization cause crash?

**Step 2d: Perform single encrypt operation**
```cpp
uint8_t data[8] = {0};
cipher.encrypt(data, 8);
```
- Build, flash, test
- Does encryption operation crash?

**Step 2e: Test ChaCha20 (if ChaCha12 works)**
```cpp
ChaCha cipher(20);  // ChaCha20
// Repeat steps 2c-2d
```
- Build, flash, test
- Does ChaCha20 specifically crash?

**Step 2f: Add benchmark loop**
```cpp
// Minimal benchmark - just encrypt 1000 times
for (int i = 0; i < 1000; i++) {
    cipher.encrypt(data, 8);
}
```
- Build, flash, test
- Does repeated operations cause issues?

**At each step:**
- Print debug messages to serial
- Note EXACT point where crash occurs
- Capture any stack traces or error messages

---

### Phase 3: Production Verification (30 min)

**CRITICAL:** Test if production encryption is affected

1. Flash **normal production firmware** (no benchmark code) to ESP32 TX
2. Pair with RX and test normal operation
3. Verify encryption works in production:
   - Does TX boot successfully?
   - Does encryption handshake work?
   - Can it maintain link with encrypted packets?

**Deliverable:** Confirm production ChaCha12 is safe or identify critical bug

---

## Success Criteria

- [ ] Basic ESP32 serial communication verified working
- [ ] Identified EXACT step where crash occurs
- [ ] Root cause hypothesis documented
- [ ] Production encryption safety verified (working or broken)
- [ ] Clear recommendation: Fix found, or needs deeper investigation

---

## Files to Check

**PrivacyLRS repository:**
- `PrivacyLRS/src/rx_main.cpp` (line 63: ChaCha initialization)
- `PrivacyLRS/src/tx_main.cpp` (line 36: ChaCha initialization)
- `PrivacyLRS/lib/ChaCha/` (ChaCha library implementation)

**Benchmark code (if accessible):**
- Previous benchmark attempt that crashed

---

## Expected Output

### Completion Report Format

```markdown
## Phase 1 Results
- ✅/❌ Basic serial: [result]

## Phase 2 Results
- Step 2a (include): [result]
- Step 2b (create object): [result]
- Step 2c (initialize): [result]
- Step 2d (encrypt): [result]
- Step 2e (ChaCha20): [result]
- Step 2f (benchmark loop): [result]

**Crash occurs at:** [exact step]

## Phase 3 Results
- Production encryption: ✅ Working / ❌ Broken

## Root Cause
[Your analysis]

## Recommendation
[Fix needed / Investigation approach]
```

---

## Debug Tools

**ESP32 Stack Trace Decoder:**
```bash
# If you get a stack trace, decode it:
xtensa-esp32-elf-addr2line -e firmware.elf 0x400d4314
```

**Memory Analysis:**
- Check heap fragmentation
- Check stack size
- Look for buffer overflows

**Alignment Issues:**
- ESP32 requires 4-byte alignment for some operations
- Check if ChaCha uses unaligned memory access

---

## Notes

- **Incremental approach is critical** - don't skip steps
- **Document everything** - even "it worked" is valuable data
- **Safety first** - if production encryption is broken, this becomes CRITICAL priority
- **Take your time** - systematic debugging is faster than guessing

This is a high-priority investigation for security code, so thoroughness is more important than speed.

---

## Context

This task is blocking:
- Finding #5 (ChaCha20 upgrade) - currently BLOCKED
- privacylrs-implement-chacha20-upgrade project - cannot proceed until crash resolved

The Security Analyst is waiting for your findings to determine next steps.

---

**Manager**
2025-12-05 12:45
