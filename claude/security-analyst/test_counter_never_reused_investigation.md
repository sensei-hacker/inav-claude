# Investigation: test_counter_never_reused Failure

**Date:** 2025-11-30 20:00
**Analyst:** Security Analyst / Cryptographer
**Issue:** `test_counter_never_reused` test failed unexpectedly

---

## Summary

**Root Cause:** Test design flaw - does not account for ChaCha cipher's block-based counter increment behavior.

**Impact:** Test methodology error, NOT a security vulnerability. ChaCha implementation is correct.

**Fix Required:** Modify test to encrypt enough data to force block boundary crossing.

---

## Investigation Details

### Test Failure

**Error message:**
```
test/test_encryption/test_encryption.cpp:249: test_counter_never_reused:
Expected FALSE Was TRUE [FAILED]
```

**Line 249:**
```cpp
TEST_ASSERT_FALSE(memcmp(counter2, counter3, TEST_COUNTER_SIZE) == 0);
```

This checks that counter2 != counter3. The failure means counter2 == counter3 (counter didn't advance).

---

### ChaCha Counter Increment Behavior

**Code analysis:** `lib/Crypto/src/ChaCha.cpp` lines 174-214

**Counter increments when:**
```cpp
if ( (posn >= 64) || ((uint8_t) len < 64 && (uint8_t) len > (64 - posn)) )  {
    // Generate new keystream block
    hashCore((uint32_t *)stream, (const uint32_t *)block, rounds);
    posn = 0;

    // Increment counter (line 191-192)
    uint32_t *inc = (uint32_t *) &block[48];
    (*inc)++;
}
```

**Conditions for counter increment:**
1. `posn >= 64` - Entire 64-byte keystream block has been used
2. `(len < 64) && (len > (64 - posn))` - Packet would cross block boundary

**Key insight (line 182):**
"Ensure that packets don't cross block boundaries, for easier re-sync"

**This is a CUSTOM MODIFICATION to standard ChaCha!**

Standard ChaCha increments counter per 64-byte block. This modified version ensures packets don't span blocks by forcing a new block if the packet wouldn't fit.

---

### Test Execution Trace

**Test code:**
```cpp
void test_counter_never_reused(void) {
    init_test_encryption();  // Sets posn = 64 via setCounter()

    uint8_t counter1[8], counter2[8], counter3[8];
    uint8_t plaintext[8] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0x11};
    uint8_t encrypted[8];

    // Get initial counter
    test_cipher_tx.getCounter(counter1, 8);

    // Encrypt packet 1 (8 bytes)
    test_cipher_tx.encrypt(encrypted, plaintext, 8);
    test_cipher_tx.getCounter(counter2, 8);

    // Encrypt packet 2 (8 bytes)
    test_cipher_tx.encrypt(encrypted, plaintext, 8);
    test_cipher_tx.getCounter(counter3, 8);

    // Check all counters are different
    TEST_ASSERT_FALSE(memcmp(counter1, counter2, 8) == 0);  // ✅ PASS
    TEST_ASSERT_FALSE(memcmp(counter2, counter3, 8) == 0);  // ❌ FAIL
}
```

**What actually happens:**

**First encrypt(8 bytes):**
- `posn = 64` (from setCounter initialization)
- Condition: `posn >= 64` → **TRUE**
- **Generates new keystream block**
- **Increments counter** (counter1 → counter2)
- Uses bytes 0-7 of new block
- `posn = 8`

**Second encrypt(8 bytes):**
- `posn = 8`
- `len = 8`
- Remaining space: `64 - 8 = 56 bytes`
- Condition 1: `posn >= 64` → FALSE (8 < 64)
- Condition 2: `(8 < 64) && (8 > 56)` → `TRUE && FALSE` → **FALSE**
- **Does NOT generate new block**
- **Counter stays same** (counter2 == counter3)
- Uses bytes 8-15 of SAME block
- `posn = 16`

**Result:** counter2 == counter3 (test fails)

---

## Security Implications

**Is this a vulnerability?** ❌ **NO**

**Reasoning:**
1. ChaCha cipher is working **correctly** per its block-based design
2. The counter increments per 64-byte keystream block, as specified in RFC 8439
3. Multiple packets can (and should) use the same keystream block if they fit
4. As long as the counter + position is unique, there's no keystream reuse

**Security property:**
What matters is that **(counter, position)** tuples are never reused, not that the counter changes after every encrypt() call.

**Counter reuse would only be a problem if:**
- Same counter value
- Same position within block
- Encrypting different plaintext

This doesn't happen because `posn` advances after each encryption.

---

## Test Design Flaw

**Problem:** Test assumes counter increments after each encrypt() call, which is incorrect.

**Correct behavior:** Counter increments per 64-byte block, not per encryption.

**Why the test is wrong:**
- Encrypting two 8-byte packets uses the same keystream block (bytes 0-15)
- This is **expected and correct** behavior
- The test incorrectly flags this as a failure

---

## Fix Options

### Option 1: Encrypt Enough Data to Cross Block Boundary

Encrypt 64+ bytes to force counter increment:

```cpp
void test_counter_never_reused(void) {
    init_test_encryption();

    uint8_t counter1[8], counter2[8], counter3[8];
    uint8_t plaintext[64];  // Full block
    uint8_t encrypted[64];

    memset(plaintext, 0xAA, 64);

    test_cipher_tx.getCounter(counter1, 8);

    // Encrypt 64 bytes (full block)
    test_cipher_tx.encrypt(encrypted, plaintext, 64);
    test_cipher_tx.getCounter(counter2, 8);

    // Encrypt another 64 bytes (another full block)
    test_cipher_tx.encrypt(encrypted, plaintext, 64);
    test_cipher_tx.getCounter(counter3, 8);

    // Now counters should all be different
    TEST_ASSERT_FALSE(memcmp(counter1, counter2, 8) == 0);  // Should PASS
    TEST_ASSERT_FALSE(memcmp(counter2, counter3, 8) == 0);  // Should PASS
}
```

---

### Option 2: Test (Counter, Position) Uniqueness

Test the actual security property - unique (counter, position) tuples:

```cpp
void test_keystream_position_never_reused(void) {
    init_test_encryption();

    struct CounterPos {
        uint8_t counter[8];
        uint8_t position;
    };

    CounterPos state1, state2, state3;
    uint8_t plaintext[8] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0x11};
    uint8_t encrypted[8];

    // Capture state 1
    test_cipher_tx.getCounter(state1.counter, 8);
    state1.position = test_cipher_tx.posn;  // Would need to expose posn

    test_cipher_tx.encrypt(encrypted, plaintext, 8);

    // Capture state 2
    test_cipher_tx.getCounter(state2.counter, 8);
    state2.position = test_cipher_tx.posn;

    test_cipher_tx.encrypt(encrypted, plaintext, 8);

    // Capture state 3
    test_cipher_tx.getCounter(state3.counter, 8);
    state3.position = test_cipher_tx.posn;

    // Check that (counter, position) tuples are unique
    // Either counter differs OR position differs
    bool state1_vs_2_unique = (memcmp(state1.counter, state2.counter, 8) != 0) ||
                               (state1.position != state2.position);
    bool state2_vs_3_unique = (memcmp(state2.counter, state3.counter, 8) != 0) ||
                               (state2.position != state3.position);

    TEST_ASSERT_TRUE(state1_vs_2_unique);
    TEST_ASSERT_TRUE(state2_vs_3_unique);
}
```

**Note:** This requires exposing the `posn` member variable, which is currently private.

---

### Option 3: Remove Test

Since the test doesn't actually test a security property correctly, we could remove it and rely on the other tests.

---

## Recommendation

**Use Option 1:** Modify test to encrypt 64-byte blocks to force counter increment.

**Rationale:**
1. Simple fix - just change packet size
2. Tests the intended behavior (counter increments between encryptions)
3. Doesn't require exposing internal implementation details
4. Maintains test readability

**Updated test:**
```cpp
void test_counter_increments_per_block(void) {
    init_test_encryption();

    uint8_t counter1[TEST_COUNTER_SIZE];
    uint8_t counter2[TEST_COUNTER_SIZE];
    uint8_t counter3[TEST_COUNTER_SIZE];

    uint8_t plaintext[64];   // Full ChaCha block size
    uint8_t encrypted[64];

    memset(plaintext, 0xAA, 64);

    // Get initial counter
    test_cipher_tx.getCounter(counter1, TEST_COUNTER_SIZE);

    // Encrypt block 1 (64 bytes - forces counter increment)
    test_cipher_tx.encrypt(encrypted, plaintext, 64);
    test_cipher_tx.getCounter(counter2, TEST_COUNTER_SIZE);

    // Encrypt block 2 (64 bytes - forces another counter increment)
    test_cipher_tx.encrypt(encrypted, plaintext, 64);
    test_cipher_tx.getCounter(counter3, TEST_COUNTER_SIZE);

    // Counters should all be different
    TEST_ASSERT_FALSE(memcmp(counter1, counter2, TEST_COUNTER_SIZE) == 0);
    TEST_ASSERT_FALSE(memcmp(counter2, counter3, TEST_COUNTER_SIZE) == 0);
    TEST_ASSERT_FALSE(memcmp(counter1, counter3, TEST_COUNTER_SIZE) == 0);
}
```

**Also add documentation comment:**
```cpp
/**
 * TEST: Counter increments per 64-byte block
 *
 * ChaCha counter increments per 64-byte keystream block, not per encryption call.
 * This test verifies counter advances after processing full blocks.
 *
 * Note: The custom modification (line 182 in ChaCha.cpp) ensures packets don't
 * cross block boundaries for easier resynchronization.
 */
```

---

## Conclusion

**Finding:** Test design flaw, NOT a security vulnerability.

**Root cause:** Test didn't account for ChaCha's block-based counter increment.

**Security status:** ✅ ChaCha implementation is correct and secure.

**Fix:** Modify test to encrypt 64-byte blocks to force counter increment.

**Estimated time to fix:** 15 minutes

---

**Security Analyst / Cryptographer**
2025-11-30 20:00
