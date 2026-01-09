# Todo List: Fix Finding 2 - Counter Initialization from Nonce

## Phase 1: Analysis

### Locate Nonce Implementation
- [ ] Find nonce generation code (TX side)
- [ ] Find nonce transmission in packet structure
- [ ] Find nonce reception code (RX side)
- [ ] Document nonce size (bytes)
- [ ] Document nonce data type
- [ ] Verify nonce is unique per-session
- [ ] Check if nonce is already used elsewhere

### Analyze Current Counter
- [ ] Review current hardcoded counter code
  - Location: `rx_main.cpp:510`
  - Location: `tx_main.cpp:309`
- [ ] Document counter size (8 bytes confirmed)
- [ ] Document counter data type
- [ ] Identify where counter is used
- [ ] Check for other counter initialization points

### Design Derivation Function
- [ ] Determine if nonce size matches counter size (8 bytes)
- [ ] If match: plan direct copy
- [ ] If mismatch: design derivation function
  - Option: Hash-based (e.g., first 8 bytes of SHA256)
  - Option: Padding or truncation
- [ ] Ensure derivation is deterministic
- [ ] Ensure TX and RX can compute same result
- [ ] Document design decision

## Phase 2: Implementation

### Create Derivation Function
- [ ] Implement function to derive counter from nonce
  ```cpp
  // Pseudocode:
  // void DeriveCounterFromNonce(uint8_t* counter, const uint8_t* nonce, size_t nonce_len)
  ```
- [ ] Handle size differences (if any)
- [ ] Add validation checks
- [ ] Add error handling
- [ ] Test derivation function in isolation

### Update TX Side
- [ ] Locate TX counter initialization
  - Current: `tx_main.cpp:309`
- [ ] Replace hardcoded value with nonce derivation
- [ ] Ensure nonce is available at initialization time
- [ ] Call derivation function
- [ ] Add debug logging (secure logging per Finding 4)
- [ ] Remove old hardcoded value

### Update RX Side
- [ ] Locate RX counter initialization
  - Current: `rx_main.cpp:510`
- [ ] Replace hardcoded value with nonce derivation
- [ ] Ensure nonce is available at initialization time
- [ ] Call derivation function
- [ ] Add debug logging (secure logging per Finding 4)
- [ ] Remove old hardcoded value

### Integration
- [ ] Verify TX and RX use identical derivation
- [ ] Check for any other counter initialization points
- [ ] Ensure compatibility with Finding 1 (LQ sync)
- [ ] Add comments explaining derivation
- [ ] Update any related constants or defines

## Phase 3: Testing

### Initialization Testing
- [ ] Test TX counter initialization from nonce
- [ ] Test RX counter initialization from nonce
- [ ] Verify TX and RX counters match
- [ ] Print/log counters to confirm (secure logging)
- [ ] Test with multiple different nonces

### Uniqueness Testing
- [ ] Generate 10 different nonces
- [ ] Verify 10 different counter values
- [ ] Verify no counter collisions
- [ ] Test edge cases (all-zero nonce, all-FF nonce)
- [ ] Verify deterministic (same nonce → same counter)

### Integration Testing
- [ ] Test encryption with new counter initialization
- [ ] Test decryption with new counter initialization
- [ ] Verify successful encryption/decryption
- [ ] Test full TX→RX communication flow
- [ ] Verify no packet loss due to counter mismatch

### Session Testing
- [ ] Start session 1, verify counter A
- [ ] Start session 2, verify counter B (B ≠ A)
- [ ] Start session 3, verify counter C (C ≠ A, C ≠ B)
- [ ] Verify each session works correctly
- [ ] Test rapid session restarts

### Finding 1 Integration (if implemented)
- [ ] Test counter init + LQ sync together
- [ ] Verify LQ sync continues from nonce-derived counter
- [ ] Test packet loss with new counter init
- [ ] Verify no conflicts between init and sync
- [ ] Verify complete counter solution works

## Phase 4: Code Review and Documentation

### Code Review
- [ ] Review derivation function implementation
- [ ] Verify TX and RX use same logic
- [ ] Check for potential bugs
- [ ] Verify error handling
- [ ] Ensure no hardcoded values remain
- [ ] Check coding standards compliance

### Security Review
- [ ] Verify unique counters per-session
- [ ] Confirm no keystream reuse
- [ ] Check derivation function is cryptographically sound
- [ ] Verify nonce handling is secure
- [ ] Confirm fix addresses original vulnerability

### Documentation
- [ ] Document derivation function logic
- [ ] Add inline code comments
- [ ] Document nonce-to-counter relationship
- [ ] Update technical documentation
- [ ] Document testing results
- [ ] Note any assumptions or limitations

## Phase 5: Completion

### Final Validation
- [ ] Run complete test suite
- [ ] Verify all success criteria met
- [ ] Confirm unique counters across sessions
- [ ] Test integration with Finding 1 (if applicable)
- [ ] Review all documentation

### Reporting
- [ ] Create completion report
- [ ] Include test results
- [ ] Document any issues found and resolved
- [ ] Note integration with Finding 1 status
- [ ] Send report to Manager

### Cleanup
- [ ] Archive task assignment from inbox
- [ ] Clean up test artifacts
- [ ] Commit code changes (if applicable to role)
- [ ] Update project status to COMPLETED

## Notes

**Critical Success Factors:**
- Deterministic derivation (same nonce → same counter)
- TX and RX compute identical counters
- Unique counters for different nonces
- Works with Finding 1 LQ sync

**Watch Out For:**
- Nonce availability timing (ensure available when needed)
- Nonce size mismatch with counter size
- Endianness issues in derivation
- Integration with Finding 1

**Questions to Resolve:**
- What is the exact nonce size?
- When is nonce available on TX and RX?
- Should derivation be direct copy or hash-based?
- Is Finding 1 implemented yet (affects integration testing)?

**Coordination Notes:**
- If Finding 1 is implemented: test integration
- If Finding 1 is not implemented: design for future integration
- Both findings affect counter management
- Finding 2 (init) + Finding 1 (sync) = complete counter solution
