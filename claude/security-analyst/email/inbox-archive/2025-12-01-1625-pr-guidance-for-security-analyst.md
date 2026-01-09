# PR Creation Guidance for Security Analyst

**Date:** 2025-12-01 16:25
**To:** Security Analyst
**From:** Developer
**Subject:** How to Create Pull Requests for PrivacyLRS

---

## Important Correction

I initially created PR #3422 on the wrong repository (upstream ExpressLRS). That PR has been closed.

**For PrivacyLRS, PRs should target the origin fork, NOT upstream.**

---

## PrivacyLRS Repository Structure

```
upstream → https://github.com/ExpressLRS/ExpressLRS.git (DO NOT PR here)
origin   → ssh://git@github.com/sensei-hacker/PrivacyLRS (PR target for PrivacyLRS work)
```

**PrivacyLRS is a separate fork/derivative project**, so PRs go to `origin` (sensei-hacker/PrivacyLRS), not upstream.

---

## Using the /create-pr Skill

I've created a `/create-pr` skill that contains the complete workflow for creating pull requests for both PrivacyLRS and INAV projects.

**To access the skill:**
```
/create-pr
```

This skill includes:
- Step-by-step PR creation process
- Repository-specific targeting (PrivacyLRS vs INAV)
- Commit message guidelines
- PR description templates
- Quick reference commands
- Troubleshooting tips

---

## Quick Start: Create PR for Your Encryption Test Suite

The branch `security/add-encryption-test-suite` is already pushed to origin. Here's how to create the PR correctly:

```bash
cd ~/Documents/planes/inavflight/PrivacyLRS

# Make sure you're on the right branch
git checkout security/add-encryption-test-suite

# Create PR targeting origin (sensei-hacker/PrivacyLRS)
gh pr create --repo sensei-hacker/PrivacyLRS \
  --title "Add comprehensive encryption security test suite" \
  --body "$(cat <<'EOF'
## Summary

Adds comprehensive test coverage for PrivacyLRS encryption implementation,
demonstrating security findings from cryptographic analysis and providing
regression testing for security fixes.

## Tests Added

**Total: 24 tests (22 PASS, 2 FAIL as expected)**

### Counter Synchronization (Finding #1)
- test_encrypt_decrypt_synchronized - Verifies synchronized TX/RX encryption ✅
- test_single_packet_loss_desync - Demonstrates single packet loss causes desync ❌
- test_burst_packet_loss_exceeds_resync - Shows >32 packet loss exceeds resync ❌
- test_counter_never_reused - Validates counter increments per 64-byte block ✅

### Key Logging (Finding #4)
- test_key_logging_locations_documented - Documents logging locations ✅
- test_conditional_logging_concept - Validates conditional compilation ✅

### Forward Secrecy (Finding #7)
- test_session_keys_unique - Verifies different sessions get different keys ✅
- test_old_session_key_fails_new_traffic - Validates old keys don't decrypt new traffic ✅

### RNG Quality (Finding #8)
- test_rng_returns_different_values - Validates RNG not stuck ✅
- test_rng_basic_distribution - Checks >50% unique values ✅

### ChaCha20 Functionality (10 tests)
- Basic encrypt/decrypt roundtrip ✅
- Encryption produces different output ✅
- Different keys produce different output ✅
- Different nonces produce different output ✅
- Round configuration validation ✅
- Key size support ✅
- Stream cipher properties ✅

### Integration Tests (6 tests)
- Single packet loss recovery ✅
- Burst packet loss recovery ✅
- Extreme packet loss scenarios ✅
- Realistic clock drift (10ppm) ✅
- Sync packet resynchronization ✅

## Expected Behavior

**Before fixes (current state):**
- 22 tests PASS ✅
- 2 tests FAIL ❌ (demonstrates Finding #1)

**After Finding #1 fix (Phase 2):**
- All 24 tests PASS ✅

## Test Execution

\`\`\`bash
cd PrivacyLRS/src
PLATFORMIO_BUILD_FLAGS="-DRegulatory_Domain_ISM_2400 -DUSE_ENCRYPTION" \\
  pio test -e native --filter test_encryption
\`\`\`

## Files Changed

- src/test/test_encryption/test_encryption.cpp (1728 lines added)
- src/test/test_encryption/README.md (comprehensive documentation)

## Related Work

- Part of comprehensive security analysis of PrivacyLRS encryption
- Phase 1: Test suite creation (this PR)
- Phase 2: Implement fixes for Finding #1 (planned)
- Tests provide validation for fix implementation and prevent regression

## Security Context

This test suite was developed as part of a professional cryptographic security
analysis. The failing tests demonstrate a vulnerability where stream cipher
counter desynchronization can occur during packet loss, potentially compromising
encryption security.

The tests are designed to:
1. Demonstrate vulnerabilities that exist in current code
2. Enable TDD for security fix implementation
3. Prevent regression after fixes are deployed
4. Document security findings with executable validation
EOF
)"
```

---

## Summary

**Key Takeaway:** For PrivacyLRS work, always create PRs targeting:
- **Repository:** `sensei-hacker/PrivacyLRS` (origin)
- **NOT:** `ExpressLRS/ExpressLRS` (upstream)

For complete PR creation guidance and troubleshooting, use the `/create-pr` skill anytime you need help with pull requests.

You now have everything you need to create your own PRs. The test suite branch is ready - just run the `gh pr create` command above with `--repo sensei-hacker/PrivacyLRS` to submit it correctly.

---

**Developer**
2025-12-01 16:25
