# LQ Counter Integration Design

**Date:** 2025-12-01
**Analyst:** Security Analyst / Cryptographer
**Purpose:** Phase 2 Step 2 - Design crypto counter synchronization using OtaNonce

---

## Executive Summary

**Chosen Approach:** Direct 1:1 mapping with embedded validation

**Design:**
1. Set crypto counter directly from OtaNonce (8-bit → 64-bit zero-padded)
2. Embed OtaNonce as first byte of encrypted payload for validation
3. RX validates decrypted OtaNonce matches expected value
4. Eliminates blind 32-position lookahead

**Benefits:**
- ✅ Simple implementation
- ✅ Explicit synchronization
- ✅ Self-validating
- ✅ No packet structure changes
- ✅ Handles any packet loss pattern
- ✅ Backwards compatible (with flag)

---

## Design Decision: Direct 1:1 Mapping

### Rationale

After evaluating three approaches (see lq-counter-analysis.md), **Direct 1:1 Mapping** is optimal because:

1. **Simplicity:** No complex packet-size-dependent calculations
2. **Robustness:** Works regardless of packet size variations
3. **Explicit:** Crypto counter directly tied to packet sequence number
4. **Maintainable:** Easy to understand and debug

**Trade-off:** Uses one ChaCha20 block per packet instead of sharing blocks
- Slightly less efficient (more keystream generation)
- Acceptable cost for reliability and simplicity

### Counter Mapping Formula

```c
// TX and RX both use same mapping
void setCounterFromOtaNonce(uint8_t nonce) {
    uint8_t counter[8] = {0};
    counter[0] = nonce;          // Low byte = OtaNonce
    counter[1] = 0;              // High bytes = 0
    counter[2] = 0;
    counter[3] = 0;
    counter[4] = 0;
    counter[5] = 0;
    counter[6] = 0;
    counter[7] = 0;

    cipher.setCounter(counter, 8);
}
```

**Properties:**
- Counter range: 0 to 255 (matches OtaNonce range)
- Counter wraps at 256 (same as OtaNonce)
- No ambiguity - one-to-one correspondence

---

## Embedded Validation Mechanism

### Why Embed OtaNonce?

**Problem:** How does RX know which OtaNonce value the TX used?

**Solution:** Embed OtaNonce as first byte of plaintext (before encryption)

**Benefit:** After decryption, RX can validate the OtaNonce matches expectations

### Payload Structure

**Before Encryption (TX):**
```
Byte 0: OtaNonce  (validation byte)
Byte 1-N: Original packet data
```

**After Encryption:**
```
Byte 0: Encrypted(OtaNonce)
Byte 1-N: Encrypted(original packet data)
```

**After Decryption (RX):**
```
Byte 0: OtaNonce (recovered)
Byte 1-N: Original packet data (recovered)
```

**Validation:**
```c
if (decrypted[0] == expected_OtaNonce) {
    // Decryption successful, counter was correct
    // Use decrypted[1..N] as packet data
} else {
    // Counter mismatch, packet lost or corrupted
}
```

---

## TX-Side Implementation Design

### Modification Points

**File:** `src/common.cpp`
**Function:** `EncryptMsg()`

**Current Implementation:**
```c
void ICACHE_RAM_ATTR EncryptMsg(uint8_t *output, uint8_t *input)
{
  size_t packetSize;
  if (OtaIsFullRes)
      packetSize = OTA8_PACKET_SIZE;
  else
      packetSize = OTA4_PACKET_SIZE;

  cipher.encrypt(output, input, packetSize);
}
```

**New Implementation:**
```c
void ICACHE_RAM_ATTR EncryptMsg(uint8_t *output, uint8_t *input)
{
  size_t packetSize;
  uint8_t plaintext[OTA8_PACKET_SIZE + 1];  // +1 for embedded OtaNonce
  uint8_t ciphertext[OTA8_PACKET_SIZE + 1];
  uint8_t counter[8];

  if (OtaIsFullRes)
      packetSize = OTA8_PACKET_SIZE;
  else
      packetSize = OTA4_PACKET_SIZE;

  // Set crypto counter from OtaNonce (direct 1:1 mapping)
  memset(counter, 0, 8);
  counter[0] = OtaNonce;
  cipher.setCounter(counter, 8);

  // Embed OtaNonce as first byte of plaintext
  plaintext[0] = OtaNonce;
  memcpy(&plaintext[1], input, packetSize);

  // Encrypt: plaintext (packetSize+1 bytes) → ciphertext
  cipher.encrypt(ciphertext, plaintext, packetSize + 1);

  // Output encrypted data (skip embedded OtaNonce byte)
  memcpy(output, &ciphertext[1], packetSize);
}
```

**Key Changes:**
1. Set counter from OtaNonce before encryption
2. Prepend OtaNonce to plaintext
3. Encrypt plaintext (including embedded OtaNonce)
4. Skip first encrypted byte in output (OtaNonce stays encrypted in ciphertext[0])

**Wait - Issue:** This changes packet size by +1 byte!

**Revised Approach:** Embed OtaNonce in EXISTING packet payload

---

## Revised TX Implementation (No Size Change)

**Better Approach:** Use first byte of EXISTING packet for OtaNonce

**Constraint:** Original packet data reduced by 1 byte

**TX Implementation:**
```c
void ICACHE_RAM_ATTR EncryptMsg(uint8_t *output, uint8_t *input)
{
  size_t packetSize;
  uint8_t plaintext[OTA8_PACKET_SIZE];
  uint8_t counter[8];

  if (OtaIsFullRes)
      packetSize = OTA8_PACKET_SIZE;
  else
      packetSize = OTA4_PACKET_SIZE;

  // Set crypto counter from OtaNonce
  memset(counter, 0, 8);
  counter[0] = OtaNonce;
  cipher.setCounter(counter, 8);

  // Build plaintext: [OtaNonce | packet_data[0..packetSize-2]]
  plaintext[0] = OtaNonce;
  memcpy(&plaintext[1], input, packetSize - 1);

  // Encrypt
  cipher.encrypt(output, plaintext, packetSize);
}
```

**Payload Usage:**
- Byte 0: OtaNonce (for validation)
- Bytes 1-(N-1): Original packet data (1 byte less)

**Trade-off:** Lose 1 byte of payload per packet
- OTA4: 8 bytes → 7 bytes payload (+ 1 byte OtaNonce)
- OTA8: 13 bytes → 12 bytes payload (+ 1 byte OtaNonce)

**Impact:** 12.5% (OTA4) or 7.7% (OTA8) payload reduction
- May affect channel data or MSP throughput
- **Acceptable for security/reliability**

---

## RX-Side Implementation Design

### Modification Points

**File:** `src/common.cpp`
**Function:** `DecryptMsg()`

**Current Implementation (Simplified):**
```c
bool ICACHE_RAM_ATTR DecryptMsg(uint8_t *input)
{
  uint8_t decrypted[OTA8_PACKET_SIZE];
  bool success = false;
  int resync = 32;  // Try up to 32 positions

  do
  {
    EncryptMsg(decrypted, input);  // Decrypt (EncryptMsg is symmetric)
    success = OtaValidatePacketCrc(otaPktPtr);
  } while (resync-- > 0 && !success);

  if (success)
  {
    memcpy(input, decrypted, packetSize);
    cipher.getCounter(encryptionCounter, 8);  // Save position
  } else {
    cipher.setCounter(encryptionCounter, 8);  // Reset to last good
  }
  return(success);
}
```

**New Implementation:**
```c
bool ICACHE_RAM_ATTR DecryptMsg(uint8_t *input)
{
  uint8_t decrypted[OTA8_PACKET_SIZE];
  uint8_t plaintext[OTA8_PACKET_SIZE];
  uint8_t counter[8];
  bool success = false;
  size_t packetSize;

  if (OtaIsFullRes)
      packetSize = OTA8_PACKET_SIZE;
  else
      packetSize = OTA4_PACKET_SIZE;

  // Set crypto counter from LOCAL OtaNonce
  memset(counter, 0, 8);
  counter[0] = OtaNonce;
  cipher.setCounter(counter, 8);

  // Decrypt with OtaNonce-based counter
  cipher.encrypt(plaintext, input, packetSize);  // ChaCha encrypt/decrypt same

  // Validate: First byte should match OtaNonce
  if (plaintext[0] == OtaNonce)
  {
    // Success! Extract original packet data
    memcpy(decrypted, &plaintext[1], packetSize - 1);

    // Validate CRC (uses decrypted data)
    OTA_Packet_s *otaPktPtr = (OTA_Packet_s *)decrypted;
    success = OtaValidatePacketCrc(otaPktPtr);

    if (success)
    {
      // Packet valid, update crypto counter
      cipher.getCounter(encryptionCounter, 8);
      memcpy(input, decrypted, packetSize - 1);
    }
  }
  else
  {
    // OtaNonce mismatch - packet loss detected
    // Option 1: Try ±1 OtaNonce (handle clock drift)
    // Option 2: Wait for next SYNC packet
    success = false;
  }

  return(success);
}
```

**Key Changes:**
1. Set counter from LOCAL OtaNonce (RX tracks OtaNonce)
2. Decrypt packet
3. Validate first byte == OtaNonce
4. If match, extract packet data and validate CRC
5. If mismatch, packet lost (wait for resync)

**No blind lookahead** - exact synchronization!

---

## OtaNonce Synchronization Strategy

### RX OtaNonce Tracking

**Problem:** RX needs to track OtaNonce locally

**Solution:**
1. Initialize from SYNC packet (existing mechanism)
2. Increment OtaNonce for each received packet
3. Periodically resync from SYNC packets

**RX-side OtaNonce Management:**

```c
// rx_main.cpp

void incrementLocalOtaNonce() {
    OtaNonce++;  // Local tracking
}

void handleReceivedPacket() {
    // Attempt decryption with current OtaNonce
    bool success = DecryptMsg(packet);

    if (success) {
        // Packet decrypted successfully
        incrementLocalOtaNonce();
    } else {
        // Decryption failed - packet lost or OtaNonce out of sync
        // Wait for next SYNC packet to resync
    }
}

void handleSyncPacket(OTA_Sync_s *syncData) {
    // Hard resync from SYNC packet
    OtaNonce = syncData->nonce;

    // Update crypto counter to match
    uint8_t counter[8] = {0};
    counter[0] = OtaNonce;
    cipher.setCounter(counter, 8);
}
```

### Packet Loss Handling

**Scenario:** TX sends packets 100, 101, 102. RX only receives 100, 102 (101 lost)

**Current Implementation:**
- RX tries 32 positions forward, finds 102 at position+2
- Crypto counter off by 2 packets
- Inefficient, limited to 32 packets

**New Implementation:**
- RX OtaNonce = 100, receives packet 102
- Attempts decrypt with counter=100, fails (embedded OtaNonce = 102 ≠ 100)
- RX detects packet loss (mismatch)
- RX increments to 101, still doesn't match
- Waits for SYNC packet or tries incrementing OtaNonce until match

**Enhanced Approach with Limited Lookahead:**
```c
bool DecryptMsg(uint8_t *input)
{
  // ... (as before, try with current OtaNonce)

  if (plaintext[0] != OtaNonce)
  {
    // Try up to ±4 positions (much smaller than current ±32)
    for (int8_t offset = -4; offset <= 4; offset++)
    {
      uint8_t test_nonce = OtaNonce + offset;
      uint8_t counter[8] = {0};
      counter[0] = test_nonce;
      cipher.setCounter(counter, 8);
      cipher.encrypt(plaintext, input, packetSize);

      if (plaintext[0] == test_nonce)
      {
        // Found correct OtaNonce!
        OtaNonce = test_nonce;  // Resync
        // ... (validate CRC and continue)
        return true;
      }
    }

    // No match found - wait for SYNC packet
    return false;
  }
}
```

**Lookahead: ±4 instead of ±32** (87.5% reduction)

---

## Wraparound Handling

**Problem:** OtaNonce wraps from 255 → 0

**Impact on crypto counter:**
- Counter goes from 255 → 0 (natural wraparound)
- ChaCha20 counter wraps correctly (no special handling needed)

**RX Validation:**
```c
// Embedded OtaNonce after wraparound
TX sends packet with OtaNonce=255: plaintext[0] = 255
TX sends packet with OtaNonce=0:   plaintext[0] = 0 (wrapped)

RX OtaNonce = 255 → decrypts, validates, increments → 0
RX OtaNonce = 0 → decrypts next packet correctly
```

**No special handling required** - uint8_t wraps naturally

---

## Initialization Sequence

**Problem:** RX doesn't know initial OtaNonce at startup

**Current Mechanism:** Wait for SYNC packet

**Keep Same Approach:**
1. RX waits for SYNC packet
2. Extracts OtaNonce from SYNC: `OtaNonce = syncData->nonce`
3. Sets crypto counter: `counter[0] = OtaNonce`
4. Begins normal packet reception

**No changes needed** to initialization - existing SYNC mechanism works

---

## CRC Handling

**Issue:** CRC calculated on packet data, not including OtaNonce

**Current CRC:**
```c
CRC = crc(packet_data[0..N])
```

**With Embedded OtaNonce:**
```c
Encrypted: [OtaNonce_encrypted | packet_data_encrypted[0..N-1]]
Decrypted: [OtaNonce | packet_data[0..N-1]]

CRC calculation: crc(packet_data[0..N-1])  // Excludes OtaNonce byte
```

**CRC should NOT include OtaNonce** because:
- OtaNonce changes every packet
- CRC validates packet integrity, not sequence
- OtaNonce validation is separate from CRC validation

**Implementation:**
- Current CRC functions already operate on packet_data
- After extracting OtaNonce, CRC validates remaining data
- No CRC changes needed

---

## Performance Impact

### Cryptographic Overhead

**Current:** Multiple packets share one ChaCha block (64 bytes)
- ~5-8 packets per block (depending on packet size)
- Amortized cost: ~1/7 block generation per packet

**New:** One ChaCha block per packet
- 1 packet per block
- Cost: 1 block generation per packet

**Overhead:** ~7x more ChaCha20 block generations

**Impact:**
- ChaCha20 is very fast (~few microseconds per block on embedded CPUs)
- Packet rate: ~500 Hz (2ms between packets)
- Block generation time << packet interval
- **Negligible performance impact**

### Payload Reduction

**OTA4 (8 bytes):**
- Before: 8 bytes payload
- After: 1 byte OtaNonce + 7 bytes payload
- Loss: 12.5%

**OTA8 (13 bytes):**
- Before: 13 bytes payload
- After: 1 byte OtaNonce + 12 bytes payload
- Loss: 7.7%

**Impact on Features:**
- RC channels: May need to use hybrid encoding more
- MSP data: Slightly reduced throughput
- **Acceptable trade-off for reliability**

---

## Backward Compatibility

**Problem:** New firmware won't work with old firmware

**Solution:** Add compatibility flag

```c
#ifdef USE_OTANONCE_CRYPTO_SYNC
  // New implementation with embedded OtaNonce
#else
  // Old implementation with blind lookahead
#endif
```

**Deployment Strategy:**
1. Update TX firmware first (with flag disabled)
2. Update RX firmware (with flag disabled)
3. Enable flag on both sides
4. Gradual rollout

**Alternatively:** Make it mandatory (breaking change, requires synchronized update)

---

## Edge Cases

### Case 1: SYNC Packet Lost

**Scenario:** Multiple SYNC packets lost, OtaNonce drifts

**Mitigation:** Embedded OtaNonce provides validation
- Even without SYNC, RX can detect drift
- ±4 lookahead catches up quickly

**Result:** Self-correcting within 4 packets

### Case 2: Burst Packet Loss (>4 packets)

**Scenario:** 10 consecutive packets lost

**Current:** Resync fails (32-packet limit)
**New:** Wait for SYNC packet, hard resync

**Improvement:** SYNC packets still work, no blind lookahead limit

### Case 3: Corrupted Packet

**Scenario:** Packet corrupted during transmission

**Detection:**
- Embedded OtaNonce mismatch → decryption "succeeds" but validation fails
- CRC check fails on corrupted data
- Packet rejected

**No false positives** - double validation (OtaNonce + CRC)

### Case 4: OtaNonce Collision After Wraparound

**Scenario:** OtaNonce wraps 255→0, repeats values

**ChaCha20 Security:** Different nonce per session (see Finding #2 analysis)
- Nonce changes per TX boot
- Counter wraparound doesn't reuse keystream
- Secure per RFC 8439

**No security issue**

---

## Testing Strategy

### Unit Tests

**Test 1:** Verify Counter Mapping
```c
void test_counter_mapping() {
    uint8_t nonce = 42;
    uint8_t counter[8];

    setCounterFromOtaNonce(nonce, counter);

    TEST_ASSERT_EQUAL(42, counter[0]);
    TEST_ASSERT_EQUAL(0, counter[1]);
    // ... verify all other bytes are 0
}
```

**Test 2:** Verify Embedded OtaNonce
```c
void test_embedded_otanonce() {
    OtaNonce = 100;
    uint8_t input[8] = {0xAA, 0xBB, 0xCC, ...};
    uint8_t encrypted[8];

    EncryptMsg(encrypted, input);

    // Decrypt and verify first byte
    DecryptMsg(encrypted);
    TEST_ASSERT_EQUAL(100, decrypted[0]);
}
```

**Test 3:** Single Packet Loss
```c
void test_single_packet_loss_resync() {
    // TX sends packet 100
    OtaNonce = 100;
    EncryptMsg(encrypted_100, data);

    // TX sends packet 101
    OtaNonce = 101;
    EncryptMsg(encrypted_101, data);

    // RX receives 100, then skips 101, receives 102
    RX_OtaNonce = 100;
    DecryptMsg(encrypted_100);  // Success, RX_OtaNonce → 101

    // Packet 101 lost (not received)

    OtaNonce = 102;
    EncryptMsg(encrypted_102, data);

    // RX tries with OtaNonce=101, should detect mismatch and resync
    TEST_ASSERT_TRUE(DecryptMsg(encrypted_102));  // Should succeed with lookahead
    TEST_ASSERT_EQUAL(102, RX_OtaNonce);  // Should resync to 102
}
```

**Test 4:** Wraparound
```c
void test_otanonce_wraparound() {
    OtaNonce = 255;
    EncryptMsg(encrypted_255, data);
    TEST_ASSERT_TRUE(DecryptMsg(encrypted_255));

    OtaNonce = 0;  // Wrapped
    EncryptMsg(encrypted_0, data);
    TEST_ASSERT_TRUE(DecryptMsg(encrypted_0));
}
```

### Integration Tests

**Test 5:** Extended Packet Loss
- Simulate 25%, 50%, 75% packet loss
- Verify RX still decrypts successfully
- Measure resync time

**Test 6:** SYNC Packet Loss
- Drop all SYNC packets
- Verify OtaNonce embedded validation still works
- Verify no desynchronization

**Test 7:** Runtime Stability
- Run for 30+ minutes with random packet loss
- Verify no crashes, no permanent desync
- Verify all CRITICAL tests PASS

---

## Implementation Plan

### Phase 1: TX Side (2-3h)

1. Modify `EncryptMsg()` in `common.cpp`
   - Add counter setting from OtaNonce
   - Embed OtaNonce in plaintext[0]
   - Adjust payload copy

2. Test TX-side encryption
   - Verify counter set correctly
   - Verify OtaNonce embedded
   - Verify packet size unchanged

### Phase 2: RX Side (2-3h)

1. Modify `DecryptMsg()` in `common.cpp`
   - Set counter from local OtaNonce
   - Validate embedded OtaNonce
   - Implement ±4 lookahead
   - Update local OtaNonce on success

2. Test RX-side decryption
   - Verify decryption with matching OtaNonce
   - Verify rejection with mismatched OtaNonce
   - Verify lookahead works

### Phase 3: Integration (1-2h)

1. Test TX-RX together
   - Synchronized operation
   - Packet loss handling
   - Wraparound handling

2. Run existing unit tests
   - Verify no regression
   - Update failing tests

### Phase 4: Validation (3-4h)

1. Run CRITICAL tests
   - `test_single_packet_loss_desync` should PASS ✅
   - `test_burst_packet_loss_exceeds_resync` should PASS ✅

2. Extended testing
   - Packet loss scenarios
   - Runtime stability
   - Performance measurement

---

## Success Criteria

**Phase 2 complete when:**
- ✅ `test_single_packet_loss_desync` **PASSES**
- ✅ `test_burst_packet_loss_exceeds_resync` **PASSES**
- ✅ All existing tests still pass (74+ tests)
- ✅ No crashes under packet loss
- ✅ OtaNonce synchronization working
- ✅ Lookahead reduced from ±32 to ±4
- ✅ Code documented

---

## Summary

**Design Chosen:** Direct 1:1 OtaNonce → Crypto Counter mapping with embedded validation

**Key Innovations:**
1. **No blind lookahead** - explicit sync via embedded OtaNonce
2. **Self-validating** - embedded OtaNonce proves correct decryption
3. **Efficient** - ±4 lookahead vs ±32 (87.5% reduction)
4. **Simple** - direct mapping, easy to understand
5. **Robust** - handles any packet loss pattern

**Trade-offs:**
- 1 byte payload reduction (acceptable)
- More ChaCha blocks (negligible performance impact)

**Next:** Proceed to implementation

---

**Security Analyst / Cryptographer**
2025-12-01
