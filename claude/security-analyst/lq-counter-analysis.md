# LQ Counter Analysis for Crypto Synchronization

**Date:** 2025-12-01
**Analyst:** Security Analyst / Cryptographer
**Purpose:** Phase 2 Step 1 - Analyze LQ/packet counter for crypto integration

---

## Executive Summary

**OtaNonce** is the packet sequence counter that can be used for crypto synchronization.

**Key Findings:**
- ✅ OtaNonce increments on every timer tick (every packet slot)
- ✅ OtaNonce is transmitted in SYNC packets
- ⚠️ OtaNonce is **NOT** in every packet type (only SYNC packets)
- ⚠️ OtaNonce (uint8_t, 0-255) and crypto counter (8 bytes, 64-bit) increment at different rates
- ⚠️ Mapping strategy needed to handle 8-bit to 64-bit conversion

**Recommendation:** Add OtaNonce to ALL packet types (1-byte overhead) or derive crypto counter directly from OtaNonce

---

## OtaNonce Definition

**Declaration:** `lib/OTA/OTA.h:162`
```c
extern volatile uint8_t OtaNonce;
```

**Properties:**
- Type: `uint8_t` (8-bit unsigned integer)
- Range: 0-255 (wraps around after 255)
- Volatile: Changes frequently
- Increments: Every timer tick (every packet timing slot)

---

## OtaNonce Increment Behavior

**TX Side - Increment Location:** `tx_main.cpp:823, 864`

```c
void ICACHE_RAM_ATTR nonceAdvance()
{
  OtaNonce++;  // Line 823
  if ((OtaNonce + 1) % ExpressLRS_currAirRate_Modparams->FHSShopInterval == 0)
  {
    ++FHSSptr;  // Advance frequency hopping
  }
}

void ICACHE_RAM_ATTR timerCallback()
{
  /* If writing to EEPROM, just advance nonces, no SPI traffic */
  if (commitInProgress)
  {
    nonceAdvance();
    return;
  }

  // ... other code ...

  // Nonce advances on every timer tick
  if (!InBindingMode)
    OtaNonce++;  // Line 864
}
```

**RX Side - Synchronization:** `rx_main.cpp:1194`
```c
OtaNonce = otaSync->nonce;  // Sync from received SYNC packet
```

**Increment Frequency:**
- Every timer tick (typically ~500Hz for 500Hz packet rate)
- Independent of actual packet transmission
- Increments even if packet is not sent (e.g., during EEPROM writes)

---

## OtaNonce Transmission

**OTA_Sync_s Structure:** `lib/OTA/OTA.h:26-35`
```c
typedef struct {
    uint8_t fhssIndex;
    uint8_t nonce;       // <-- OtaNonce transmitted here
    uint8_t switchEncMode:1,
            newTlmRatio:3,
            rateIndex:4;
    uint8_t UID3;
    uint8_t UID4;
    uint8_t UID5;
} PACKED OTA_Sync_s;
```

**Transmitted in:** PACKET_TYPE_SYNC only

**SYNC Packet Frequency:** `tx_main.cpp:704, 720`
```c
uint32_t SyncInterval = (connectionState == connected && !isTlmDisarmed)
    ? ExpressLRS_currAirRate_RFperfParams->SyncPktIntervalConnected
    : ExpressLRS_currAirRate_RFperfParams->SyncPktIntervalDisconnected;

// Regular sync rotates through 4x slots, twice on each slot
// Only on sync FHSS channel with timed delay
if ((!skipSync) && ((syncSlot / 2) <= NonceFHSSresult)
    && (now - SyncPacketLastSent > SyncInterval) && FHSSonSyncChannel())
{
    otaPkt.std.type = PACKET_TYPE_SYNC;
    GenerateSyncPacketData(...);
}
```

**SYNC Packet Frequency:** Periodic, NOT every packet
- Connected: `SyncPktIntervalConnected` (varies by rate)
- Disconnected: `SyncPktIntervalDisconnected`
- Only on sync FHSS channel
- Time-delayed between SYNC packets

**Problem:** If SYNC packets are lost, OtaNonce synchronization is lost

---

## Current Packet Structures

### OTA_Packet4_s (8 bytes total)

**Header (1 byte):**
```c
uint8_t type: 2,        // Packet type (2 bits)
        crcHigh: 6;     // CRC high bits (6 bits)
```

**Payload (6 bytes):** Union of:
- RC data (channels)
- MSP data
- SYNC data (includes nonce)
- TLM data

**Footer (1 byte):**
```c
uint8_t crcLow;         // CRC low byte
```

### OTA_Packet8_s (13 bytes total)

**Payload (11 bytes):** Union of:
- RC data (more channels)
- MSP data
- SYNC data (includes nonce)
- TLM data
- Airport data

**Footer (2 bytes):**
```c
uint16_t crc;           // CRC16
```

**Observation:** No dedicated sequence number field in RC/MSP/TLM packets

---

## Crypto Counter vs OtaNonce

### Current Crypto Counter Behavior

**From previous ChaCha analysis:**
- Crypto counter: 8 bytes (64-bit)
- Increments: Per 64-byte ChaCha keystream block
- Packet size: 8-13 bytes
- **Multiple packets use same crypto counter** (same 64-byte block)

**Example:**
- Packet 1 (8 bytes): Uses crypto counter block, counter doesn't increment
- Packet 2 (8 bytes): Uses same block, bytes 8-15, counter doesn't increment
- ...
- After 64 bytes: Counter increments

### OtaNonce Behavior

- OtaNonce: 1 byte (8-bit)
- Increments: Every timer tick (every packet slot)
- Range: 0-255, wraps around

### Mapping Challenge

**Problem:** Different increment rates
- OtaNonce: +1 per packet
- Crypto counter: +1 per 64 bytes (~5-8 packets depending on packet size)

**Option 1: Direct Mapping**
- Set crypto counter = OtaNonce (pad to 8 bytes)
- Forces one keystream block per packet
- Changes ChaCha usage pattern (less efficient)
- **Pros:** Simple, explicit synchronization
- **Cons:** Higher cryptographic overhead, uses more keystream

**Option 2: Derived Mapping**
- Crypto counter = OtaNonce * packets_per_block
- Calculate expected counter based on OtaNonce
- **Pros:** Preserves block efficiency
- **Cons:** More complex, requires accurate packet size knowledge

**Option 3: OtaNonce for Resync Only**
- Use OtaNonce to calculate approximate position
- Fine-tune with limited lookahead (±4 positions)
- **Pros:** Efficient, handles packet size variations
- **Cons:** Still has small resync window

---

## Integration Points

### TX Side

**Where to modify:**

1. **Counter Initialization:** `tx_main.cpp:309` (CryptoSetKeys function)
   - Set initial crypto counter based on OtaNonce

2. **Before Encryption:** Before `EncryptMsg()` call
   - Calculate crypto counter from current OtaNonce
   - Set counter: `cipher.setCounter(counter, 8)`

3. **Packet Transmission:** Add OtaNonce to packet header
   - **Challenge:** Packet structures are space-constrained
   - **Option A:** Modify packet structure to include nonce field
   - **Option B:** Use existing SYNC mechanism more frequently
   - **Option C:** Embed in encrypted data (requires decryption first)

### RX Side

**Where to modify:**

1. **Counter Initialization:** `rx_main.cpp:510` (CryptoSetKeys function)
   - Set initial crypto counter based on received OtaNonce

2. **DecryptMsg():** `common.cpp:242`
   - **Current:** 32-position blind lookahead
   - **New:** Extract OtaNonce from packet, calculate expected counter
   - **Set counter before decryption attempt**
   - **Eliminate or reduce lookahead** (maybe ±2 for rounding errors)

3. **Sync Handling:** `rx_main.cpp:1194`
   - Already syncs OtaNonce from SYNC packets
   - May need to trigger crypto counter resync

---

## Proposed Approaches

### Approach A: Add OtaNonce to ALL Packets (Unencrypted)

**Implementation:**
1. Modify packet structures to include 1-byte nonce field
2. Place nonce in packet header (before encryption)
3. RX extracts nonce, calculates crypto counter, decrypts

**Pros:**
- Simple and explicit
- Works with any packet loss pattern
- No blind lookahead needed

**Cons:**
- Requires packet structure changes (1-byte overhead)
- Backwards compatibility issues
- May not fit in 8-byte packet (OTA4)

**Packet Size Impact:**
- OTA4: 8 bytes → 9 bytes (12.5% overhead)
- OTA8: 13 bytes → 14 bytes (7.7% overhead)

### Approach B: Derive Counter from OtaNonce (Use SYNC Packets)

**Implementation:**
1. Keep SYNC packet nonce transmission as-is
2. On RX, track OtaNonce locally (increment per received packet)
3. Periodically resync from SYNC packets
4. Derive crypto counter from OtaNonce

**Pros:**
- No packet structure changes
- Uses existing SYNC mechanism
- Backwards compatible

**Cons:**
- Relies on regular SYNC packet reception
- If SYNC packets lost, gradual drift possible
- Complex counter derivation logic

### Approach C: Embed OtaNonce in Encrypted Payload

**Implementation:**
1. First byte of encrypted payload = OtaNonce
2. Try decryption, check if first byte matches expected OtaNonce ±N
3. Adjust counter and retry if mismatch

**Pros:**
- No packet structure changes
- OtaNonce authenticated by encryption
- Works with any packet type

**Cons:**
- 1-byte payload overhead (encrypted)
- Chicken-and-egg: need correct counter to decrypt to get nonce
- Requires modified lookahead strategy

---

## Crypto Counter Derivation Formula

**Assuming Approach A or B**, need to map OtaNonce → Crypto Counter:

**Variables:**
- OtaNonce: 8-bit (0-255)
- Crypto Counter: 64-bit
- Packet Size: 8 or 13 bytes
- ChaCha Block Size: 64 bytes

**Formula Options:**

**Option 1: Direct Mapping (1:1)**
```c
crypto_counter[0] = OtaNonce;
crypto_counter[1-7] = 0;
```
- Simple, explicit
- One ChaCha block per packet
- Higher overhead

**Option 2: Scaled Mapping**
```c
packets_per_block = 64 / packet_size;  // ~5-8 packets
crypto_counter_64bit = OtaNonce / packets_per_block;
```
- Preserves ChaCha block efficiency
- Complex rounding with varying packet sizes

**Option 3: Hybrid**
```c
// Use OtaNonce to get close, fine-tune with small lookahead
approximate_counter = OtaNonce / packets_per_block;
cipher.setCounter(approximate_counter);
// Try decrypt, if fail, try ±2 positions
```
- Balance efficiency and robustness
- Handles packet size variations

---

## Recommended Approach

**Recommendation: Approach B (Derive from OtaNonce) + Approach C (Embed for validation)**

**Hybrid Strategy:**
1. **Use existing SYNC packets** to synchronize OtaNonce periodically
2. **Derive crypto counter** from OtaNonce (scaled mapping)
3. **Embed OtaNonce in first encrypted byte** for validation
4. **Small lookahead** (±2) for edge cases

**Implementation Steps:**
1. **TX Side:**
   - Before EncryptMsg(): `payload[0] = OtaNonce` (first byte)
   - Calculate `crypto_counter = f(OtaNonce, packet_size)`
   - Set counter: `cipher.setCounter(crypto_counter, 8)`
   - Encrypt packet (OtaNonce now encrypted)

2. **RX Side:**
   - Receive packet
   - Calculate expected `crypto_counter = f(local_OtaNonce, packet_size)`
   - Set counter: `cipher.setCounter(crypto_counter, 8)`
   - Decrypt packet
   - Check `decrypted[0] == local_OtaNonce ± tolerance`
   - If mismatch, try ±2 counter positions
   - If success, update local_OtaNonce from decrypted[0]
   - If SYNC packet, hard-sync OtaNonce

**Advantages:**
- No packet structure changes ✅
- Backwards compatible ✅
- Self-validating (OtaNonce in payload) ✅
- Handles wraparound (OtaNonce 255→0) ✅
- Robust to SYNC packet loss ✅
- Minimal lookahead (±2 vs ±32) ✅

---

## Potential Issues and Solutions

### Issue 1: OtaNonce Wraparound (255→0)

**Problem:** Crypto counter derivation breaks at wraparound

**Solution:**
- Track wraparound count: `crypto_counter = (wraparound_count << 8) | OtaNonce`
- Or: Use modulo arithmetic, accept periodic resync

### Issue 2: Packet Size Variation (OTA4 vs OTA8)

**Problem:** Different packet sizes affect packets-per-block calculation

**Solution:**
- Include packet size in counter calculation
- Or: Use direct mapping (1:1) to avoid complexity

### Issue 3: Skipped Packets (Timer Ticks Without Transmission)

**Problem:** OtaNonce increments even when packet not transmitted

**Solution:**
- RX tracks OtaNonce locally, expects gaps
- SYNC packets provide ground truth
- Embedded OtaNonce validates correct position

### Issue 4: Initial Synchronization

**Problem:** RX doesn't know initial OtaNonce value

**Solution:**
- Wait for SYNC packet to get initial OtaNonce
- Or: Try all 256 possible OtaNonce values (expensive)
- Current implementation already waits for SYNC

---

## Next Steps

**Phase 2 Step 2: Design Integration**
1. Choose final approach (recommend Hybrid)
2. Define exact counter derivation formula
3. Design TX-side modifications
4. Design RX-side modifications
5. Handle edge cases (wraparound, initialization, packet loss)
6. Document integration points

**Estimated time:** 2-3 hours

---

**Security Analyst / Cryptographer**
2025-12-01
