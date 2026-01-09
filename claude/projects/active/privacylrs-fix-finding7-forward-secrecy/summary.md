# Project: Fix Finding 7 - Implement Forward Secrecy with Curve25519

**Status:** 📋 TODO
**Priority:** MEDIUM
**Severity:** MEDIUM
**Type:** Security Enhancement / Cryptographic Protocol
**Created:** 2025-11-30
**Assigned:** Security Analyst (or Developer)
**Estimated Time:** 12-16 hours

## Overview

Implement ephemeral Diffie-Hellman key exchange using Curve25519 to provide forward secrecy, preventing compromise of master key from exposing past communications.

## Problem

**Security Finding 7 (MEDIUM):** No Forward Secrecy

**Location:** `PrivacyLRS/src/src/tx_main.cpp:301-357`

**Current Design:**
- Uses long-term shared master key for all sessions
- Master key compromise exposes all past communications
- Master key compromise exposes all future communications
- No session key rotation
- No ephemeral key exchange

**Issue:**
- If master key is compromised (lost device, extracted from flash, etc.)
- Attacker can decrypt all captured past traffic
- Attacker can decrypt all future traffic
- No cryptographic protection for historical data

**Impact:**
- Loss of forward secrecy
- Compromised master key has permanent consequences
- Captured traffic can be decrypted retroactively
- Standard security best practice violated

## Approved Solution

**Decision:** Implement Diffie-Hellman with Curve25519

Implement ephemeral Diffie-Hellman key exchange using Curve25519 for forward secrecy.

**Rationale:**
- Curve25519 is modern, fast, and secure
- Provides perfect forward secrecy
- Well-suited for embedded systems
- Industry standard for ECDH
- Smaller keys and faster than traditional DH

**Stakeholder Specification:**
"Diffie-Hellman"

## Objectives

1. Design ECDH key exchange protocol integration
2. Implement Curve25519 key generation
3. Implement key exchange handshake
4. Derive session keys from ECDH shared secret
5. Implement session key rotation
6. Test key exchange and forward secrecy
7. Ensure backward compatibility path (if needed)
8. Document protocol

## Implementation Steps

### Phase 1: Protocol Design (3-4 hours)
1. Review current session establishment
2. Design ECDH integration into protocol
3. Design handshake sequence
4. Design session key derivation (from ECDH + master key)
5. Plan session key lifetime and rotation
6. Design backward compatibility (if needed)
7. Document protocol specification

### Phase 2: Curve25519 Integration (3-4 hours)
1. Select Curve25519 library for platform
2. Integrate library into build system
3. Implement key pair generation
4. Implement ECDH computation
5. Implement KDF (Key Derivation Function)
6. Test cryptographic operations

### Phase 3: Protocol Implementation (4-5 hours)
1. Implement TX-side key exchange
2. Implement RX-side key exchange
3. Implement session key derivation
4. Update encryption to use session keys
5. Implement key rotation (if applicable)
6. Add error handling and validation

### Phase 4: Testing (2-3 hours)
1. Test key generation
2. Test key exchange handshake
3. Verify shared secret matches on TX and RX
4. Test session key derivation
5. Test encryption/decryption with session keys
6. Test forward secrecy (key rotation)
7. Test error handling

## Scope

**In Scope:**
- ECDH key exchange protocol design
- Curve25519 implementation
- Session key derivation
- Testing forward secrecy
- Protocol documentation

**Out of Scope:**
- Authentication (master key still used for that)
- Other cipher changes
- Other security findings
- Full protocol redesign

## Success Criteria

- [ ] ECDH protocol designed and documented
- [ ] Curve25519 library integrated
- [ ] Key exchange implemented on TX and RX
- [ ] Session keys derived correctly
- [ ] TX and RX derive same session key
- [ ] Encryption uses session keys (not master key)
- [ ] Forward secrecy verified (old session keys unrecoverable)
- [ ] Tests pass
- [ ] Performance acceptable
- [ ] Documentation complete

## Protocol Design Considerations

### Key Exchange Phases

**1. Ephemeral Key Generation:**
- TX generates ephemeral Curve25519 key pair
- RX generates ephemeral Curve25519 key pair

**2. Public Key Exchange:**
- TX sends its ephemeral public key to RX
- RX sends its ephemeral public key to TX

**3. Shared Secret Derivation:**
- Both compute ECDH shared secret
- Both derive session key from shared secret + master key

**4. Session Encryption:**
- Use derived session key for ChaCha20
- Discard ephemeral private keys after session

### Key Derivation

Use HKDF or similar KDF:
```
session_key = KDF(ecdh_shared_secret, master_key, context_info)
```

This combines:
- **ECDH shared secret:** Provides forward secrecy
- **Master key:** Provides authentication (prevents MITM)
- **Context info:** Prevents cross-protocol attacks

### Session Lifetime

Options:
- **Per-binding:** New session key per TX-RX binding
- **Time-based:** Rotate keys every N minutes
- **Event-based:** Rotate after N packets

## Dependencies

**Technical:**
- Curve25519 library for target platform(s)
  - Options: TweetNaCl, libsodium, micro-ecc, custom
- KDF implementation (HKDF or similar)
- Understanding of current session establishment
- Additional protocol overhead for key exchange

**Related Findings:**
- Independent of other findings
- Works alongside Finding 2 (counter init) and Finding 1 (sync)

## Risk Assessment

**Technical Risks:**
- Key exchange adds latency (mitigation: optimize handshake)
- Curve25519 may be slow on some MCUs (mitigation: benchmark)
- Protocol complexity increases (mitigation: thorough testing)
- Backward compatibility challenges (mitigation: version negotiation)

**Project Risks:**
- MEDIUM priority - important but not critical
- Complex implementation (12-16 hours estimated)
- Requires protocol changes
- Requires cryptographic expertise

## Priority Justification

**MEDIUM** - Forward secrecy is a security enhancement that protects historical data from future compromises. While important for long-term security, it's not as critical as fixing the stream cipher desync (Finding 1) which causes immediate crashes.

## Notes

**Reference Documents:**
- Security findings report: `claude/manager/inbox-archive/2025-11-30-1500-findings-privacylrs-comprehensive-analysis.md`
- Decisions document: `claude/projects/security-analysis-privacylrs-initial/findings-decisions.md`

**Stakeholder Decision:**
"Diffie-Hellman"

**Curve25519 Advantages:**
- Fast: ~250K cycles for key exchange on ARM Cortex-M
- Small: 32-byte keys
- Secure: ~128-bit security level
- Simple: No parameter choices, hard to misuse
- Standard: RFC 7748, widely deployed

**Curve25519 Libraries for Embedded:**
- **TweetNaCl:** Compact, simple, portable
- **libsodium:** Full-featured, well-tested
- **micro-ecc:** Lightweight, embedded-focused
- **Custom:** Optimize for specific platform

**Forward Secrecy Benefits:**
- Master key compromise doesn't expose past traffic
- Each session has unique cryptographic keys
- Attacker cannot retroactively decrypt captured traffic
- Industry standard for secure communications

**Protocol Considerations:**
- Must prevent man-in-the-middle attacks
- Master key authenticates the key exchange
- Consider replay protection for key exchange messages
- Consider version negotiation for backward compatibility

**Performance Impact:**
- Key exchange: ~few milliseconds per session
- Only on session establishment, not per-packet
- Minimal impact on link latency once established
