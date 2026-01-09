# Todo List: Fix Finding 7 - Implement Forward Secrecy with Curve25519

## Phase 1: Protocol Design and Research

### Research Current Session Establishment
- [ ] Read current session establishment code
  - Location: `tx_main.cpp:301-357`
- [ ] Map session initialization sequence
- [ ] Identify nonce exchange mechanism
- [ ] Document current packet format
- [ ] Identify where master key is used
- [ ] Document session lifecycle

### Research Curve25519 Libraries
- [ ] Survey available Curve25519 libraries
  - [ ] TweetNaCl (compact, portable)
  - [ ] libsodium (full-featured)
  - [ ] micro-ecc (lightweight)
  - [ ] Platform-specific (hardware crypto?)
- [ ] Check library compatibility with platform
- [ ] Evaluate code size impact
- [ ] Evaluate performance (if benchmarks available)
- [ ] Choose library for implementation

### Design Key Exchange Protocol
- [ ] Design handshake sequence
  - [ ] TX generates ephemeral key pair
  - [ ] RX generates ephemeral key pair
  - [ ] TX sends ephemeral public key
  - [ ] RX sends ephemeral public key
  - [ ] Both compute shared secret
- [ ] Design packet format for key exchange
- [ ] Determine when key exchange occurs
  - [ ] At binding?
  - [ ] At session start?
  - [ ] Periodically?
- [ ] Design session key lifetime
- [ ] Plan for key rotation (if applicable)

### Design Key Derivation
- [ ] Choose KDF (HKDF, custom, etc.)
- [ ] Design KDF inputs:
  - ECDH shared secret
  - Master key (for authentication)
  - Context info (protocol version, nonce, etc.)
- [ ] Design session key output format
- [ ] Determine if multiple keys needed (separate TX/RX?)
- [ ] Document KDF specification

### Design Security Properties
- [ ] Ensure forward secrecy
- [ ] Prevent man-in-the-middle (using master key)
- [ ] Prevent replay attacks
- [ ] Design failure modes
- [ ] Plan for backward compatibility (if needed)
- [ ] Document security properties

### Create Protocol Specification
- [ ] Write detailed protocol document
- [ ] Include message formats
- [ ] Include state machine
- [ ] Include security analysis
- [ ] Include error handling
- [ ] Review and refine

## Phase 2: Library Integration

### Integrate Curve25519 Library
- [ ] Add library to source tree or dependencies
- [ ] Update build system (CMake, PlatformIO, etc.)
- [ ] Create wrapper/interface for library
- [ ] Verify library compiles
- [ ] Check code size impact
- [ ] Verify no build warnings

### Implement KDF
- [ ] Implement or integrate HKDF
  - Or use library's KDF if available
- [ ] Add KDF to build
- [ ] Test KDF independently
- [ ] Verify deterministic output

### Test Cryptographic Primitives
- [ ] Test Curve25519 key generation
- [ ] Test ECDH shared secret computation
- [ ] Verify TX and RX compute same shared secret
- [ ] Test KDF with known test vectors (if available)
- [ ] Verify no memory leaks
- [ ] Benchmark performance

## Phase 3: Implementation - TX Side

### Implement Ephemeral Key Generation (TX)
- [ ] Add ephemeral key pair generation
- [ ] Store private key securely (RAM only, clear after use)
- [ ] Prepare public key for transmission

### Implement Key Exchange Handshake (TX)
- [ ] Send TX ephemeral public key to RX
  - Design packet format
  - Implement transmission
- [ ] Receive RX ephemeral public key
  - Implement reception
  - Validate received key
- [ ] Add timeout and retry logic
- [ ] Add error handling

### Implement Shared Secret Derivation (TX)
- [ ] Compute ECDH shared secret
  - Use TX private key + RX public key
- [ ] Derive session key using KDF
  - Inputs: shared secret, master key, context
- [ ] Store session key
- [ ] Securely erase ephemeral private key
- [ ] Securely erase shared secret

### Update Encryption (TX)
- [ ] Use session key instead of master key
- [ ] Update ChaCha20 initialization
- [ ] Verify encryption works
- [ ] Add logging (secure logging per Finding 4)

## Phase 4: Implementation - RX Side

### Implement Ephemeral Key Generation (RX)
- [ ] Add ephemeral key pair generation
- [ ] Store private key securely (RAM only, clear after use)
- [ ] Prepare public key for transmission

### Implement Key Exchange Handshake (RX)
- [ ] Receive TX ephemeral public key
  - Implement reception
  - Validate received key
- [ ] Send RX ephemeral public key to TX
  - Design packet format
  - Implement transmission
- [ ] Add timeout and error handling

### Implement Shared Secret Derivation (RX)
- [ ] Compute ECDH shared secret
  - Use RX private key + TX public key
- [ ] Derive session key using KDF
  - Inputs: shared secret, master key, context (same as TX)
- [ ] Store session key
- [ ] Securely erase ephemeral private key
- [ ] Securely erase shared secret

### Update Decryption (RX)
- [ ] Use session key instead of master key
- [ ] Update ChaCha20 initialization
- [ ] Verify decryption works
- [ ] Add logging (secure logging per Finding 4)

## Phase 5: Key Rotation (Optional)

### Design Key Rotation
- [ ] Determine rotation trigger
  - Time-based (every N minutes)?
  - Packet-based (every N packets)?
  - Event-based (on demand)?
- [ ] Design rotation protocol
- [ ] Ensure smooth transition (no packet loss)
- [ ] Handle rotation failures

### Implement Key Rotation (if applicable)
- [ ] Implement rotation trigger
- [ ] Repeat key exchange for new session
- [ ] Transition to new session key
- [ ] Securely erase old session key
- [ ] Test rotation under load

## Phase 6: Testing

### Unit Testing - Cryptographic Operations
- [ ] Test key generation (generates valid keys)
- [ ] Test ECDH (produces same shared secret on both sides)
- [ ] Test KDF (produces expected session key)
- [ ] Test with known test vectors
- [ ] Test edge cases (zero keys, etc.)

### Integration Testing - Key Exchange
- [ ] Test full TX → RX key exchange
- [ ] Verify TX and RX derive same session key
- [ ] Test with multiple sessions (different keys each time)
- [ ] Test handshake timeout handling
- [ ] Test with corrupted key exchange packets
- [ ] Test rapid session restarts

### Functional Testing - Encryption/Decryption
- [ ] Test encryption with session keys
- [ ] Test decryption with session keys
- [ ] Verify successful TX → RX communication
- [ ] Test with varying packet rates
- [ ] Test with packet loss (ensure recovery)
- [ ] Test extended operation (no key leaks)

### Security Testing - Forward Secrecy
- [ ] Perform key exchange, derive session key A
- [ ] Encrypt and decrypt test data
- [ ] Simulate master key compromise
- [ ] Verify session key A cannot be recovered
- [ ] Perform new key exchange, derive session key B
- [ ] Verify session key B ≠ session key A
- [ ] Verify old traffic cannot be decrypted with new keys
- [ ] **Confirmed:** Forward secrecy working

### Performance Testing
- [ ] Measure key exchange latency
- [ ] Measure impact on session establishment time
- [ ] Verify acceptable for RC link
- [ ] Measure memory usage
- [ ] Check for memory leaks during rotation

## Phase 7: Error Handling and Edge Cases

### Error Handling
- [ ] Handle key exchange timeout
- [ ] Handle corrupted public keys
- [ ] Handle invalid ECDH results
- [ ] Handle session establishment failures
- [ ] Implement fallback or retry logic
- [ ] Add error logging

### Edge Cases
- [ ] Test rapid session restarts
- [ ] Test simultaneous key exchanges
- [ ] Test with weak/invalid keys (should reject)
- [ ] Test memory exhaustion scenarios
- [ ] Test maximum session count

## Phase 8: Security Review

### Code Review
- [ ] Review all cryptographic operations
- [ ] Verify no key material leaked
- [ ] Verify ephemeral keys properly erased
- [ ] Check for timing side channels (if critical)
- [ ] Verify proper random number usage
- [ ] Ensure constant-time operations (if needed)

### Protocol Review
- [ ] Verify forward secrecy achieved
- [ ] Verify MITM protection (via master key)
- [ ] Check for replay attack vulnerabilities
- [ ] Verify session key uniqueness
- [ ] Review failure modes
- [ ] Confirm security properties

### Cryptographic Validation
- [ ] Verify correct use of Curve25519
- [ ] Verify correct use of KDF
- [ ] Check for nonce reuse issues
- [ ] Verify random number quality for ephemeral keys
- [ ] Compare against ECDH best practices

## Phase 9: Documentation

### Code Documentation
- [ ] Add inline comments explaining protocol
- [ ] Document key exchange sequence
- [ ] Document session key derivation
- [ ] Add security notes
- [ ] Document limitations

### Protocol Documentation
- [ ] Create protocol specification document
- [ ] Include message formats
- [ ] Include state diagrams
- [ ] Document security properties
- [ ] Add troubleshooting guide

### User Documentation
- [ ] Document what forward secrecy means
- [ ] Explain security benefits
- [ ] Note any user-visible changes
- [ ] Update any relevant guides

## Phase 10: Completion

### Final Validation
- [ ] Run complete test suite
- [ ] Verify all success criteria met
- [ ] Verify forward secrecy working
- [ ] Performance acceptable
- [ ] Review all documentation

### Reporting
- [ ] Create completion report
- [ ] Include protocol specification
- [ ] Include test results
- [ ] Include security analysis
- [ ] Include performance measurements
- [ ] Send report to Manager

### Cleanup
- [ ] Archive task assignment from inbox
- [ ] Clean up test code
- [ ] Commit code changes (if applicable to role)
- [ ] Update project status to COMPLETED

## Notes

**Critical Success Factors:**
- Forward secrecy verified (old keys unrecoverable)
- TX and RX derive same session key
- No master key exposure in session keys
- Performance acceptable for RC link
- Protocol secure against MITM

**Watch Out For:**
- Key exchange adds latency (optimize handshake)
- Memory leaks in key generation
- Ephemeral keys not properly erased
- Timing issues in handshake
- Backward compatibility breaking changes

**Security Best Practices:**
- Use cryptographically secure random numbers for ephemeral keys
- Erase ephemeral private keys immediately after use
- Use constant-time operations if timing attacks are a concern
- Combine ECDH with master key for authentication
- Validate received public keys (reject weak/invalid keys)

**Questions to Resolve:**
- When exactly does key exchange occur (binding, session start, periodic)?
- How is session lifetime determined?
- Is key rotation needed, or one-time per session?
- What Curve25519 library is best for target platform?
- Is backward compatibility with non-ECDH devices needed?

**Performance Expectations:**
- Curve25519: ~few milliseconds per key exchange
- KDF: <1 millisecond
- Total handshake: <100ms expected
- No per-packet overhead (only at session establishment)

**Library Choice Considerations:**
- **TweetNaCl:** Small code size, portable, easy to integrate
- **libsodium:** Full-featured, well-tested, larger footprint
- **micro-ecc:** Embedded-optimized, multiple curves
- Consider RAM usage, code size, and performance for target MCU
