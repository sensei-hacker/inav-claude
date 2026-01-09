# Finding 6 Replay Protection - Detailed Code Path Analysis

**Date:** 2025-11-30 18:45
**From:** Security Analyst / Cryptographer
**To:** Manager
**Re:** Finding 6 Replay Protection - Code Path Verification and Revised Assessment

---

## Executive Summary

**You and the user are CORRECT.** After detailed code path analysis, I confirm that **replay attacks are NOT feasible during normal operation** because the resynchronization mechanism only searches forward, and old packets cannot decrypt at any forward counter position.

**Revised Recommendation:** Downgrade Finding #6 from **MEDIUM** to **LOW/INFORMATIONAL** with clarification that the vulnerability only applies in specific edge cases involving session re-establishment with counter reuse.

---

## 1. Code Path Analysis - Counter Behavior During Resync

### The DecryptMsg() Function (common.cpp:242-294)

```cpp
bool ICACHE_RAM_ATTR DecryptMsg(uint8_t *input)
{
  uint8_t decrypted[OTA8_PACKET_SIZE];
  bool success = false;
  int resync = 32;  // Try up to 32 forward positions
  static bool encryptionStarted = false;

  // RESYNC LOOP - tries counter positions forward only
  do {
    EncryptMsg(decrypted, input);  // Line 265: Increments counter each iteration
    success = OtaValidatePacketCrc(otaPktPtr);
    encryptionStarted = encryptionStarted || success;
  } while ( resync-- > 0 && !success );  // Line 281: Try up to 32 times

  if (success) {
    memcpy(input, decrypted, packetSize);
    cipher.getCounter(encryptionCounter, 8);  // Line 286: SAVE successful position
  } else {
    cipher.setCounter(encryptionCounter, 8);  // Line 291: RESET to last known good
  }
  return(success);
}
```

### Critical Observations

**1. Counter Movement is FORWARD-ONLY:**
- Each call to `EncryptMsg()` (line 265) increments the ChaCha cipher counter
- The loop tries positions: N, N+1, N+2, N+3... up to N+32
- There is **NO mechanism** to move the counter backwards
- On failure, counter is reset to `encryptionCounter` (last known good position)

**2. Old Packet Decryption is IMPOSSIBLE:**

Suppose:
- Current counter position: **N = 1000**
- Old packet encrypted at: **N-10 = 990** (10 packets ago)
- Attacker replays the old packet

What happens:
1. Resync loop tries: 1000, 1001, 1002... 1032
2. Old packet requires counter position **990** to decrypt
3. **990 is NOT in the range [1000, 1032]**
4. Old packet will NOT decrypt at any attempted position
5. CRC validation fails at all 32 positions
6. Packet is rejected

**Conclusion:** Standard replay attacks are **NOT FEASIBLE** during normal operation.

---

## 2. Replay Attack Feasibility Assessment

### ❌ NOT FEASIBLE: Replay During Normal Operation

**Attack scenario:** Attacker captures valid packet and replays it later

**Why it fails:**
- Captured packet was encrypted at counter position N
- By the time attacker replays it, RX counter is at N+k (where k > 0)
- Resync searches N+k, N+k+1, N+k+2... N+k+32
- Original packet at position N cannot decrypt
- CRC validation fails
- Packet rejected

**Verdict:** **Replay attacks are NOT possible during normal operation.**

---

### ⚠️ EDGE CASE: Session Re-establishment with Counter Reuse

There is ONE edge case where replay could be theoretically possible:

**Prerequisites (all must occur):**
1. Session 1 is established with counter initialized to hardcoded value {109, 110, 111, 112, 113, 114, 115, 116}
2. Attacker captures packets from Session 1 (counter positions 109-150)
3. Link is lost and session is re-established
4. Session 2 is initialized with the SAME hardcoded counter {109, 110, 111, 112, 113, 114, 115, 116}
5. Attacker replays captured packets from Session 1

**What happens:**
- Session 2 counter resets to position 109
- Replayed packet from position 115 falls within forward search window [109, 141]
- **Packet could potentially decrypt successfully**

**However, this requires:**
- Same session key (unlikely - keys should be per-session)
- Same nonce value (unlikely - nonce should change)
- Counter reuse (this IS the case due to Finding #2)

**Mitigation:**
This edge case is **already addressed by Finding #2** (Hardcoded Counter Initialization). When Finding #2 is fixed by randomizing the counter initialization, this replay scenario becomes impossible.

---

### Code Evidence: Session Initialization

**When CryptoSetKeys() is called (rx_main.cpp:504-560):**

```cpp
bool CryptoSetKeys(encryption_params_t *params)
{
    uint8_t rounds = 12;
    size_t counterSize = 8;
    size_t keySize = 16;

    // Extract nonce and key from params
    uint8_t nonce[] = {params->nonce[0], params->nonce[1], ...};
    uint8_t counter[] = {109, 110, 111, 112, 113, 114, 115, 116};  // HARDCODED!

    memcpy(encryptionCounter, counter, counterSize);  // Line 541
    cipher.clear();
    cipher.setKey(params->key, keySize);
    cipher.setIV(nonce, 8);
    cipher.setCounter(counter, counterSize);
    cipher.setNumRounds(rounds);
}
```

**When this is called:**
- Initial pairing: MSP command `MSP_ELRS_INIT_ENCRYPT` (rx_main.cpp:1358)
- Session re-establishment after link loss (same MSP command)

**Frequency:** Rare - only during initial setup or after complete link loss requiring re-pairing

---

## 3. Revised Finding Assessment

### Original Finding #6 (MEDIUM Severity)

**Original statement:**
> "No explicit replay protection mechanism exists. The 32-position lookahead window could allow recently-captured packets to be replayed."

**Original severity:** MEDIUM

**Original concern:** Attacker could replay packets within the 32-packet window

---

### Revised Finding #6 (LOW/INFORMATIONAL Severity)

**Revised statement:**
> "Replay attacks are not feasible during normal operation because the resynchronization mechanism only searches forward. However, in the edge case of session re-establishment with the same hardcoded counter initialization (Finding #2), previously captured packets could theoretically be replayed. This vulnerability is fully mitigated by implementing Finding #2 (randomized counter initialization)."

**Revised severity:** **LOW** (or INFORMATIONAL)

**Revised concern:** Replay only possible in rare edge case already covered by Finding #2

---

### Justification for Downgrade

| Factor | Assessment |
|--------|------------|
| **Normal operation replay** | ❌ NOT FEASIBLE - counter moves forward only |
| **Resync window replay** | ❌ NOT FEASIBLE - old packets outside forward range |
| **Session restart replay** | ⚠️ THEORETICALLY POSSIBLE (requires counter reuse) |
| **Practical exploit difficulty** | HIGH - requires session restart with same counter |
| **Mitigation dependency** | Already addressed by Finding #2 fix |
| **Real-world impact** | MINIMAL - edge case only |

**Conclusion:** The original finding overestimated the replay attack surface. The forward-only resync mechanism provides inherent replay protection for normal operation.

---

## 4. Edge Cases and Session Reset Scenarios

### Scenario 1: Normal Packet Loss (Common)

**What happens:**
- RX misses packets 100-105 (counter stays at 100)
- TX sends packet 106
- RX resync searches: 100, 101, 102... finds valid packet at 106
- Counter advances to 107
- Old packets (0-99) cannot decrypt

**Replay feasible?** ❌ NO

---

### Scenario 2: Link Re-establishment (Rare)

**What happens:**
- Session 1: Counter at position 5000
- Complete link loss (TX/RX lose sync entirely)
- `MSP_ELRS_INIT_ENCRYPT` called to re-establish
- Session 2: Counter resets to hardcoded {109, 110, 111, 112, 113, 114, 115, 116}
- Now counter is at lower value than Session 1

**Replay feasible?** ⚠️ THEORETICALLY YES (if session keys/nonces reused)

**BUT:**
- Requires complete session restart
- Should use new session key (implementation unclear from code review)
- Should use new nonce (nonce is passed in params, likely different)
- **Fixed by implementing Finding #2** (randomized counter)

---

### Scenario 3: Power Cycle (Rare)

**What happens:**
- RX/TX power cycled
- Counter resets to initialization value
- Similar to Scenario 2

**Replay feasible?** ⚠️ Same as Scenario 2

---

## 5. Code Path Verification - Detailed Trace

### Question: "Does this only move counter forward?"

```cpp
do {
    EncryptMsg(decrypted, input);  // Does this only move counter forward?
    success = OtaValidatePacketCrc(otaPktPtr);
    encryptionStarted = encryptionStarted || success;
} while ( resync-- > 0 && !success );
```

**Answer:** ✅ **YES - Counter ONLY moves forward**

**Proof from EncryptMsg() (common.cpp:227-240):**

```cpp
void ICACHE_RAM_ATTR EncryptMsg(uint8_t *output, uint8_t *input)
{
  size_t packetSize;

  if (OtaIsFullRes) {
    packetSize = OTA8_PACKET_SIZE;
  } else {
    packetSize = OTA4_PACKET_SIZE;
  }

  cipher.encrypt(output, input, packetSize);  // ChaCha.encrypt() increments counter
}
```

**ChaCha cipher behavior (from Crypto library):**
- Each `cipher.encrypt()` call processes one block
- Counter is incremented after each block
- **Counter cannot move backwards**
- Counter is a monotonically increasing value

**Detailed trace for 3-iteration resync:**

```
Initial state: counter = 1000, encryptionCounter = 1000

Iteration 1:
  - EncryptMsg() called
  - cipher.encrypt() uses counter=1000, then increments to 1001
  - CRC check fails
  - Counter now at 1001

Iteration 2:
  - EncryptMsg() called
  - cipher.encrypt() uses counter=1001, then increments to 1002
  - CRC check fails
  - Counter now at 1002

Iteration 3:
  - EncryptMsg() called
  - cipher.encrypt() uses counter=1002, then increments to 1003
  - CRC check succeeds!
  - Counter saved: encryptionCounter = 1003

If all fail:
  - cipher.setCounter(encryptionCounter, 8)  // Reset to 1000
  - Counter back to original position (does NOT go backwards from original)
```

**Conclusion:** Counter tries positions [N, N+1, N+2... N+32], never backwards.

---

## 6. Comparison: Before and After Analysis

### Before Analysis (Original Finding)

**Assumption:** 32-packet lookahead window enables replay

**Concern:** Recent packets could be replayed within window

**Example:**
- "If RX is at counter 1000, attacker could replay packets from 968-999"

**Flaw in reasoning:** Didn't account for forward-only search

---

### After Analysis (Corrected Understanding)

**Reality:** Lookahead searches FORWARD from current position

**Actual behavior:** RX at counter 1000 searches 1000-1032, not backwards

**Example:**
- RX at counter 1000
- Searches: 1000, 1001, 1002... 1032
- Packet from position 990 is OUTSIDE this range
- Cannot decrypt

**Corrected reasoning:** Forward search inherently prevents replay of old packets

---

## 7. Recommended Actions

### Immediate Actions

**1. Update Finding #6 Documentation ✓**

**Current status:** MEDIUM severity

**Recommended change:**
- **Severity:** MEDIUM → **LOW** (or **INFORMATIONAL**)
- **Title:** "Replay Protection - Edge Case Only (Session Restart)"
- **Description:** Clarify that normal operation has inherent replay protection via forward-only counter search

---

**2. Clarify Relationship with Finding #2 ✓**

Finding #6 is essentially a **subset** of Finding #2:
- Finding #2: Hardcoded counter initialization (HIGH severity)
- Finding #6: Replay during session restart (LOW severity)

**Recommendation:**
- Keep Finding #2 as HIGH priority
- Downgrade Finding #6 to LOW
- Note in Finding #6: "Fully mitigated by implementing Finding #2"

---

**3. No Additional Code Changes Needed ✓**

**Current implementation is sufficient for normal operation.**

The forward-only resync mechanism provides adequate replay protection. No additional replay protection logic is needed beyond fixing Finding #2.

---

### Optional Enhancements (Defense in Depth)

If defense-in-depth is desired, consider:

**1. Explicit Timestamp/Sequence Validation**
- Add packet timestamp to OTA format
- Reject packets older than threshold (e.g., 5 seconds)
- **Impact:** Additional complexity, minimal security benefit

**2. Session Counter Tracking**
- Track highest seen counter per session
- Reject any packet with counter ≤ highest seen
- **Impact:** Marginal benefit, already implicit in current design

**3. Randomized Counter Initialization (Finding #2)**
- **THIS IS THE KEY FIX**
- Prevents session restart replay scenario
- **Recommended:** HIGH priority

---

## 8. Summary and Conclusions

### Key Findings

✅ **Confirmed:** Counter movement is forward-only during resync

✅ **Confirmed:** Standard replay attacks are NOT feasible

✅ **Confirmed:** The 32-packet window searches forward (N to N+32), not backward

⚠️ **Edge Case:** Session restart with counter reuse could enable replay (rare, requires Finding #2 vulnerability)

---

### Revised Threat Assessment

| Threat | Original Assessment | Revised Assessment |
|--------|-------------------|-------------------|
| **Replay during normal operation** | MEDIUM concern | ❌ NOT FEASIBLE |
| **Replay within 32-packet window** | MEDIUM concern | ❌ NOT FEASIBLE |
| **Replay after session restart** | Not considered | ⚠️ LOW concern (edge case) |

---

### Revised Finding #6 Summary

**Severity:** MEDIUM → **LOW/INFORMATIONAL**

**Attack feasibility:**
- Normal operation: ❌ NOT FEASIBLE
- Session restart: ⚠️ THEORETICALLY POSSIBLE (rare edge case)

**Mitigation:**
- Already addressed by Finding #2 (randomized counter initialization)
- No additional code changes needed

**Priority:**
- MEDIUM → **LOW**
- Address as part of Finding #2 implementation
- No standalone fix required

---

### Answer to Manager's Questions

**1. Counter Movement Analysis:**
- ✅ YES - Resync loop only tries keystream positions FORWARD (N, N+1... N+32)
- ✅ NO backwards movement during normal operation
- ⚠️ Counter CAN reset during session re-establishment (rare)

**2. Replay Attack Feasibility:**
- ✅ Confirmed: Replay attacks are NOT possible during normal operation
- ✅ Confirmed: Old packets cannot decrypt in forward-only lookahead window
- ⚠️ Edge case: Session restart with counter reuse (addressed by Finding #2)

**3. Code Path Verification:**
- ✅ Confirmed: Counter can only advance in the resync loop
- ✅ Confirmed: No mechanism for old packets to fall within forward search
- ⚠️ Session restart via `MSP_ELRS_INIT_ENCRYPT` can reset counter

---

## Appendix: Code References

**DecryptMsg() function:**
- File: `PrivacyLRS/src/src/common.cpp`
- Lines: 242-294
- Resync loop: Lines 263-281

**CryptoSetKeys() function:**
- File: `PrivacyLRS/src/src/rx_main.cpp`
- Lines: 504-560
- Counter initialization: Line 541

**Session re-establishment:**
- File: `PrivacyLRS/src/src/rx_main.cpp`
- MSP command handler: Line 1358
- Command: `MSP_ELRS_INIT_ENCRYPT`

---

## Thank You

Thank you for the excellent question and for carefully reviewing the original finding. This deeper analysis has clarified that the forward-only resync mechanism provides stronger inherent replay protection than originally assessed.

**Recommended next step:** Update Finding #6 documentation to reflect the revised LOW/INFORMATIONAL severity and clarify the edge case scenario.

---

**Security Analyst / Cryptographer**
2025-11-30 18:45
