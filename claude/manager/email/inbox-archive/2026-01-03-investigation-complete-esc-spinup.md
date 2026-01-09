# Investigation Complete: ESC Motor Spinup After Disarm

**Date:** 2026-01-03
**Developer:** Developer
**Task:** investigate-esc-spinup-after-disarm
**Priority:** HIGH (Safety Critical - User Injury Confirmed)
**Status:** ✅ INVESTIGATION COMPLETE - Root Cause Identified, Solution Proposed

---

## Executive Summary

**ROOT CAUSE CONFIRMED:** INAV's EEPROM save uses blocking STM32 HAL flash functions that stop the main loop for 70-650ms. During this time, DShot packet generation stops completely (DMA is one-shot, not circular), causing ESCs to detect signal loss, reboot, and potentially spin motors during reboot.

**CRITICAL DISCOVERY:** STM32 HAL provides interrupt-based flash functions (`HAL_FLASH_Program_IT()` and `HAL_FLASHEx_Erase_IT()`) that allow truly non-blocking EEPROM writes. This enables a proper architectural solution.

**RECOMMENDED FIX:** Implement non-blocking EEPROM save using HAL interrupt-based flash functions. This fixes the root cause permanently and benefits all motor protocols.

Possibly outdated. See real-world-implementations-research.md

---

## Root Cause Analysis - Detailed Call Chain

### Exact Blocking Call Chain:

```
Main Loop (scheduler running tasks)
│
└─→ processDelayedSave() - called 0.5s after disarm (fc_core.c:918-925)
    │
    └─→ processSaveConfigAndNotify() (config.c:360-369)
        │
        ├─→ suspendRxSignal()
        │
        ├─→ writeEEPROM() (config.c:371-373)
        │   │
        │   └─→ writeConfigToEEPROM() (config_eeprom.c:322-342)
        │       │
        │       └─→ for (attempt = 0; attempt < 3; attempt++) {
        │           │
        │           └─→ writeSettingsToEEPROM() (config_eeprom.c:245-320)
        │               │
        │               ├─→ config_streamer_write(&header, 1 byte)
        │               │
        │               └─→ PG_FOREACH(reg) {  ⚠️ TIGHT LOOP - NO YIELD
        │                   │
        │                   ├─→ config_streamer_write(&record, 6 bytes)
        │                   │   │
        │                   │   └─→ for (byte loop) {
        │                   │       └─→ Every 4 bytes:
        │                   │           └─→ config_streamer_impl_write_word()
        │                   │               │
        │                   │               └─→ config_streamer_stm32f7.c:111-139
        │                   │                   │
        │                   │                   ├─→ If at sector boundary:
        │                   │                   │   HAL_FLASHEx_Erase()
        │                   │                   │   ⚠️ BLOCKS 20-200ms PER SECTOR
        │                   │                   │
        │                   │                   └─→ HAL_FLASH_Program()
        │                   │                       ⚠️ BLOCKS ~100-500μs PER CALL
        │                   │
        │                   └─→ config_streamer_write(reg->address, variable size)
        │                       └─→ (repeats blocking calls)
        │
        │               } ⚠️ END LOOP - NO SCHEDULER CALLS MADE
        │
        ├─→ readEEPROM() (also blocking but reads are fast)
        │
        └─→ resumeRxSignal()
```

### Blocking Call Frequency:

**Buffer Sizes:**
- F4/F7: 4 bytes per call
- H7: 16-32 bytes per call

**For typical 2KB config on F7:**
- `HAL_FLASH_Program()`: **~512 blocking calls**
- `HAL_FLASHEx_Erase()`: **1-2 blocking calls**

**Blocking Duration:**
- Each `HAL_FLASH_Program()`: 100-500μs
- Each `HAL_FLASHEx_Erase()`: 20-200ms
- **Total blocking: 70-650ms continuous**

**ESC Timeout Thresholds:**
- BLHeli_32 32.10 (first 5s): **30ms** ❌ EXCEEDED
- BLHeli_32 32.9: **320ms** ⚠️ LIKELY EXCEEDED

---

## DMA Configuration Analysis

### Critical Finding: DMA is ONE-SHOT, Not Continuous

**DMA Mode Configuration:**
```c
// From timer_impl_stdperiph.c:325
DMA_InitStructure.DMA_Mode = DMA_Mode_Normal;  // ONE-SHOT!

// From timer_impl_hal.c:391
init.Mode = LL_DMA_MODE_NORMAL;  // ONE-SHOT!
```

**What `DMA_MODE_NORMAL` means:**
- DMA sends buffer **once**
- DMA stops and waits
- **Must be restarted by software** for next packet
- NOT `DMA_MODE_CIRCULAR` (which would auto-repeat)

### DShot Packet Sending Process:

**Normal Operation (main loop running):**
```
Loop iteration 1:
  pwmCompleteMotorUpdate() called
    → prepareDshotPacket() - creates packet in RAM buffer
    → loadDmaBufferDshot() - fills DMA buffer (18 bytes)
    → timerPWMStartDMA() - starts DMA transfer
    → DMA sends 18 bytes to timer CCR register
    → DMA completes and STOPS

[~2-8ms later depending on DShot rate]

Loop iteration 2:
  pwmCompleteMotorUpdate() called AGAIN
    → New packet prepared
    → DMA restarted
    → Cycle repeats
```

**During EEPROM Blocking (70-650ms):**
```
Last packet before blocking:
  pwmCompleteMotorUpdate() sends final packet
    → DMA completes and STOPS

[EEPROM write blocks - main loop FROZEN]

  ⚠️ pwmCompleteMotorUpdate() NOT CALLED
  ⚠️ No new packet prepared
  ⚠️ DMA NOT restarted
  ⚠️ ESC signal pin SILENT for 70-650ms

[30-320ms later]
  ESC timeout exceeded
  ESC reboots
  Motor may spin during reboot

[EEPROM write completes - main loop resumes]

Next iteration:
  pwmCompleteMotorUpdate() called
    → New packet sent
    → But ESC already rebooting!
```

---

## Why PWM/OneShot Don't Have This Problem

**PWM/OneShot/MultiShot are hardware-based:**
- Use timer compare registers (CCR)
- Timer hardware generates PWM signal automatically
- Pin toggles based on timer counter value
- **No CPU intervention needed after initial setup**
- Signal continues even when CPU blocked

**DShot is software-based:**
- Requires DMA buffer loaded with new packet data
- `pwmCompleteMotorUpdate()` must run every 2-8ms
- If software doesn't run → no packets → silence
- **ESC interprets silence as signal loss**

**Therefore: Fix ONLY needed for DShot protocol**

---

## Critical Discovery: Non-Blocking Flash Functions Exist!

### STM32 HAL Provides Interrupt-Based Flash Operations

**Available Functions (F4, F7, H7):**
```c
// Non-blocking flash erase
HAL_StatusTypeDef HAL_FLASHEx_Erase_IT(FLASH_EraseInitTypeDef *pEraseInit);

// Non-blocking flash program
HAL_StatusTypeDef HAL_FLASH_Program_IT(uint32_t TypeProgram, uint32_t Address, uint64_t Data);

// Interrupt handler (called automatically)
void HAL_FLASH_IRQHandler(void);

// Completion callback (weak function - user implements)
void HAL_FLASH_EndOfOperationCallback(uint32_t address);
```

**How They Work:**
1. Call `HAL_FLASH_Program_IT()` → Returns **immediately**
2. Flash hardware performs operation in background
3. **Main loop continues running** (DShot packets keep sending!)
4. When complete, hardware triggers interrupt
5. Callback indicates completion, can write next chunk

**This changes everything!**

---

## Proposed Solutions

### OPTION A: Non-Blocking EEPROM Save (RECOMMENDED) ⭐ POSSIBLY OUTDATED - NON-FUNCTIONAL, MAYBE

**Use STM32 HAL interrupt-based flash functions to make EEPROM save truly non-blocking.**

**Implementation:**
```c
// State machine for async EEPROM save
typedef enum {
    EEPROM_SAVE_IDLE,
    EEPROM_SAVE_ERASE_IN_PROGRESS,
    EEPROM_SAVE_WRITE_IN_PROGRESS,
    EEPROM_SAVE_COMPLETE
} eepromSaveState_e;

// Start async write
int config_streamer_impl_write_word_nonblocking(...) {
    if (erase_needed) {
        HAL_FLASHEx_Erase_IT(&EraseInitStruct);  // Returns immediately
        state = EEPROM_SAVE_ERASE_IN_PROGRESS;
    } else {
        HAL_FLASH_Program_IT(...);  // Returns immediately
        state = EEPROM_SAVE_WRITE_IN_PROGRESS;
    }
    return IN_PROGRESS;
}

// Callback when flash operation completes
void HAL_FLASH_EndOfOperationCallback(uint32_t address) {
    // Operation complete - can write next chunk
    state = EEPROM_SAVE_IDLE;
}

// Called from main loop
void processEEPROMSaveNonBlocking(void) {
    if (state == IN_PROGRESS) {
        // Flash operation ongoing - main loop continues!
        // pwmCompleteMotorUpdate() keeps running!
        // DShot packets keep sending!
        return;
    }

    if (bytesRemaining > 0) {
        writeNextChunk();  // Starts next async operation
    }
}
```

**Advantages:**
- ✅ **Fixes root cause permanently**
- ✅ **Works for ALL protocols** (PWM/OneShot/DShot)
- ✅ **Main loop never blocks**
- ✅ **Proper architectural solution**
- ✅ **Uses standard HAL features**
- ✅ **Future-proof**

**Disadvantages:**
- ⚠️ State machine adds complexity
- ⚠️ Async error handling needed
- ⚠️ More testing required

**Files to Modify:**
- `src/main/config/config_streamer*.c` - Use _IT functions
- `src/main/config/config_eeprom.c` - State machine
- `src/main/fc/fc_core.c` - Call state machine periodically

**Estimated Effort:** 8-12 hours implementation + testing

---

### OPTION B: Timer-Based DShot Keepalive (Workaround)

**Use timer interrupt to send DShot 0 packets during blocking operations.**

**Implementation:**
- Configure timer interrupt at DShot update rate
- When disarmed + DShot protocol: enable interrupt
- Interrupt sends DShot 0 packets
- EEPROM can block safely

**Advantages:**
- ✅ Simpler than Option A
- ✅ Minimal changes to EEPROM code
- ✅ Proven approach (Betaflight similar)

**Disadvantages:**
- ❌ Doesn't fix root cause
- ❌ DShot-specific (doesn't improve PWM/OneShot)
- ❌ Additional timer interrupt overhead
- ❌ Still have blocking in system

---

### OPTION C: Defer EEPROM Save (Quick Fix)

**Increase delay from 0.5s to 10s before saving.**

**Advantages:**
- ✅ Trivial to implement
- ✅ Low risk

**Disadvantages:**
- ❌ Doesn't fix root cause
- ❌ Risk of stats loss if battery disconnected
- ❌ Poor user experience

---

## Recommendation

**STRONGLY RECOMMEND: Option A (Non-Blocking EEPROM Save)**

**Rationale:**
1. **Fixes root cause** - No more blocking operations
2. **Benefits everyone** - All protocols, not just DShot
3. **Better architecture** - Proper async design
4. **HAL-provided** - Standard, tested functions
5. **Long-term value** - Future improvements easier

While more complex to implement, this is the **correct engineering solution** that will benefit INAV long-term.

---

## Testing Plan

### Functional Testing:
- [ ] EEPROM integrity - verify no corruption
- [ ] Power loss during save - safe handling
- [ ] Multiple rapid saves - state machine validation
- [ ] Flash error injection - error handling
- [ ] All platforms - F4, F7, H7 targets

### DShot Testing:
- [ ] No motor spinup after disarm with stats enabled
- [ ] Continuous DShot signal - verify no gaps
- [ ] Different ESC firmware - BLHeli_32 32.9, 32.10, BlueJay, AM32
- [ ] Different DShot rates - 150/300/600
- [ ] Rapid arm/disarm cycles

### Performance Testing:
- [ ] CPU load - should be same or lower
- [ ] Interrupt latency - ensure acceptable
- [ ] Task scheduling - verify no disruption

---

## Related Issues Analyzed

- **#10913** - Primary issue (user injury confirmed, DShot specific)
- **#9441** - ESC reboot due to EEPROM (explains mechanism)
- **#10003** - Motors wouldn't stop after crash
- **#10009** - Failed to turn off motors on disarm
- **#9968** - Motor keeps spinning after disarm
- **#10606** - Referenced as related

**Betaflight References:**
- **PR #12544** - DShot 0 packet continuity (different approach)
- **PR #12560** - Beacon control restoration

---

## Investigation Documents

**Complete analysis available in:**
1. `claude/developer/projects/investigate-esc-spinup-after-disarm/investigation-notes.md`
   - Initial issue analysis
   - GitHub issue summaries

2. `claude/developer/projects/investigate-esc-spinup-after-disarm/findings.md`
   - Original detailed analysis
   - Multiple solution options

3. `claude/developer/projects/investigate-esc-spinup-after-disarm/blocking-analysis.md`
   - Exact call chain to blocking functions
   - DMA configuration analysis
   - Why PWM/OneShot don't need fix

4. `claude/developer/projects/investigate-esc-spinup-after-disarm/non-blocking-flash-solution.md`
   - Non-blocking HAL functions discovery
   - Implementation details
   - Comparison to other approaches

---

## Success Criteria Achieved

- ✅ Issue #10913 thoroughly analyzed
- ✅ Issue #9441 context understood
- ✅ EEPROM save code located and analyzed
- ✅ Motor output code during disarm analyzed
- ✅ Exact blocking call chain documented
- ✅ DMA configuration analyzed
- ✅ Root cause confirmed with code evidence
- ✅ Non-blocking HAL functions discovered
- ✅ Fix proposed with implementation plan
- ✅ Safety impact assessed
- ✅ Comprehensive documentation created

---

## Next Steps - Awaiting Manager Decision

**Option 1: Implement Non-Blocking Solution (Recommended)**
- I can proceed with Option A implementation
- Start with F7 platform prototype
- Bench test with props off
- Expand to other platforms

**Option 2: Implement Quick Fix**
- Option B or C for faster deployment
- Schedule Option A for future release

**Option 3: Document as Known Issue**
- Add to release notes
- Recommend workarounds (OneShot, disable stats)
- Community can use OneShot until fixed

Please advise on preferred approach.

---

## Risk Assessment

**User Safety:** ⚠️ HIGH PRIORITY
- User injury confirmed (propeller laceration)
- Random occurrence makes it unpredictable
- Can happen to any user with DShot + stats enabled

**Implementation Risk:** MEDIUM
- Non-blocking solution requires careful implementation
- State machine bugs could corrupt EEPROM
- Extensive testing required

**Mitigation:**
- Props-off testing first
- Multiple platform testing
- Beta release to community
- Fallback to blocking mode on errors

---

**End of Investigation Report**

**Completion Time:** ~6 hours
**Confidence Level:** HIGH - Root cause definitively identified with code evidence
**Solution Viability:** HIGH - HAL provides exact functions needed
