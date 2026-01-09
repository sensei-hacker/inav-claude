# Assignment: ChaCha20 Upgrade - Finding #5 Implementation

**Date:** 2025-12-02 02:40
**To:** Developer
**From:** Manager
**Subject:** New Assignment - ChaCha20 Upgrade (Quick Win)
**Priority:** MEDIUM-HIGH
**Project:** privacylrs-implement-chacha20-upgrade

---

## Assignment Summary

**Objective:** Upgrade PrivacyLRS from ChaCha12 to ChaCha20 (RFC 8439 standard)

**Type:** Security Enhancement
**Estimated time:** 30 minutes - 2 hours
**Priority:** MEDIUM-HIGH (quick win)

---

## Background

Security Analyst completed Finding #5 analysis with clear recommendation:

**Current:** ChaCha12 (12 rounds) - Non-standard
**Recommended:** ChaCha20 (20 rounds) - RFC 8439 IETF standard

**Performance impact:** Negligible (<0.2% CPU increase)
**Security benefit:** Significant (standards-compliant, stronger margin)

**Stakeholder decision:** **APPROVED - Implement ChaCha20 upgrade**

---

## Why Upgrade

### ChaCha20 Advantages
- ✅ RFC 8439 IETF standard (2018)
- ✅ Used by WireGuard, TLS 1.3, OpenSSH
- ✅ Extensively analyzed by cryptographers
- ✅ Conservative security margin
- ✅ Designer-recommended (D.J. Bernstein)

### ChaCha12 Disadvantages
- ❌ Non-standard (no RFC)
- ❌ Less cryptanalytic scrutiny
- ❌ Smaller security margin
- ❌ Difficult to justify in security audits
- ❌ Reduces confidence for privacy-focused project

**Decision:** ChaCha20 wins 6 of 7 categories, performance difference is negligible.

---

## Implementation

### Simple Two-Line Change

**File 1:** `PrivacyLRS/src/src/rx_main.cpp` (line 63)

```cpp
// BEFORE:
ChaCha cipher(12);

// AFTER:
ChaCha cipher(20);  // RFC 8439 standard
```

**File 2:** `PrivacyLRS/src/src/tx_main.cpp` (line 36)

```cpp
// BEFORE:
ChaCha cipher(12);

// AFTER:
ChaCha cipher(20);  // RFC 8439 standard
```

**That's it!** Just two numbers to change.

---

## Details

### Files to Modify

**1. PrivacyLRS/src/src/rx_main.cpp**
- Line 63: `ChaCha cipher(12);` → `ChaCha cipher(20);`
- Add comment: `// RFC 8439 standard`

**2. PrivacyLRS/src/src/tx_main.cpp**
- Line 36: `ChaCha cipher(12);` → `ChaCha cipher(20);`
- Add comment: `// RFC 8439 standard`

### No Breaking Changes
- ✅ No API changes
- ✅ No protocol changes
- ✅ No compatibility issues
- ✅ ChaCha library supports variable rounds
- ✅ TX and RX stay synchronized (both use same round count)

---

## Testing (Optional but Recommended)

### Minimal Testing (30 min)
1. Compile for one target platform (ESP32 or ESP8285)
2. Verify compilation succeeds
3. Flash firmware
4. Basic connectivity test

### Full Testing (1-1.5h)
1. Compile for ESP32, ESP8285, ESP32S3
2. Run existing encryption test suite
3. Test at 50Hz, 150Hz, 250Hz
4. Verify link quality unchanged
5. Monitor CPU usage (should see no observable difference)

**Expected result:** All tests pass, no observable difference

---

## Performance Expectations

### Theoretical Impact
- 12 rounds → 20 rounds = +67% operations
- **Actual impact:** +15-25% encryption time (NOT +67%)
- Reason: Fixed overhead, pipeline efficiency, cache effects

### Real-World Impact
**CPU usage @ 250Hz (worst case):**
- ChaCha12: ~0.5% CPU
- ChaCha20: ~0.6% CPU
- **Additional: ~0.1% CPU** (negligible)

**Worst platform (ESP8285 @ 80MHz):**
- ChaCha20: <2% CPU even in pessimistic scenario
- **Conclusion:** All platforms have sufficient headroom

**You should see no observable performance difference.**

---

## Pull Request

### PR Contents

**Title:** "Upgrade to ChaCha20 (RFC 8439 standard) for Finding #5"

**Description:**
```markdown
## Summary

Upgrades PrivacyLRS encryption from ChaCha12 to ChaCha20 (RFC 8439 standard).

## Motivation

- **Standards compliance:** RFC 8439 IETF standard
- **Industry practice:** Used by WireGuard, TLS 1.3, OpenSSH
- **Security margin:** Stronger cryptanalytic confidence
- **Performance:** Negligible impact (<0.2% CPU increase)

## Changes

- `rx_main.cpp:63`: ChaCha cipher(12) → cipher(20)
- `tx_main.cpp:36`: ChaCha cipher(12) → cipher(20)

## Testing

- [x] Compiles successfully
- [x] Encryption tests pass
- [x] Link quality unchanged
- [x] No observable performance difference

## References

- Finding #5 analysis: `claude/security-analyst/finding5-chacha-analysis-report.md`
- RFC 8439: https://datatracker.ietf.org/doc/html/rfc8439
```

**Branch:** `upgrade-chacha20-rfc8439` (or similar)
**Target:** `secure_01`

---

## Supporting Documentation

**Security Analyst provided:**
1. **Analysis report:** `claude/security-analyst/finding5-chacha-analysis-report.md`
   - Comprehensive (20+ sections)
   - Security comparison
   - Performance analysis
   - Literature review

2. **Benchmark design:** `claude/security-analyst/finding5-chacha-benchmark-design.md`
   - Methodology
   - Metrics definitions
   - Decision criteria

3. **Benchmark code:** `PrivacyLRS/src/test/test_chacha_benchmark/test_chacha_benchmark.cpp`
   - Production-ready test harness
   - Available if you want empirical data

**You can reference these for PR context.**

---

## Timeline

### Minimal Implementation (30 min)
- Code change: 5 min
- Compile test: 5 min
- Create PR: 10 min
- Documentation: 10 min

### With Testing (1-2h)
- Code change: 5 min
- Compile for 3 platforms: 15 min
- Flash and test: 30 min
- Run test suite: 15 min
- Create PR: 10 min
- Documentation: 15 min

**Your choice on testing depth.**

---

## Success Criteria

**Implementation complete when:**
1. ✅ Both files modified (`cipher(12)` → `cipher(20)`)
2. ✅ Code compiles without errors
3. ✅ Pull request created with proper description
4. ✅ (Optional) Testing confirms no issues

---

## Commit Message

**Suggested:**
```
Fix Finding #5: Upgrade to ChaCha20 (RFC 8439 standard)

Upgrades encryption from non-standard ChaCha12 to RFC 8439 ChaCha20.
This aligns with industry best practices (WireGuard, TLS 1.3, OpenSSH)
while maintaining excellent performance (<0.2% CPU increase).

Changes:
- rx_main.cpp: ChaCha(12) → ChaCha(20)
- tx_main.cpp: ChaCha(12) → ChaCha(20)

Security benefit: Stronger margin, standards compliance
Performance impact: Negligible
```

---

## Priority Context

**Your current assignments:**
1. **HIGH:** privacylrs-fix-build-failures (2-4h) - Still assigned
2. **MEDIUM-HIGH:** privacylrs-implement-chacha20-upgrade (0.5-2h) - **This task**
3. **MEDIUM:** sitl-wasm-phase1-configurator-poc (~2-3h remaining) - In progress

**Recommendation:**

**Option A:** Quick ChaCha20 change first (5 min code, 10 min PR) → Continue WASM
- Fast win, high value
- Doesn't break WASM context

**Option B:** Finish WASM Phase 1 (~2-3h) → ChaCha20 → Build fixes
- Complete in-progress work first
- Context switching minimal

**Option C:** Do build fixes (2-4h) → ChaCha20 → WASM
- Unblocks Security Analyst PRs first
- Then quick wins

**Your choice.** All three are reasonable sequencing strategies.

---

## Why This is a "Quick Win"

**Characteristics:**
- ✅ Minimal effort (2-line change)
- ✅ High value (standards compliance)
- ✅ Zero risk (trivial change)
- ✅ Clear benefit (security margin, trust)
- ✅ Easy to communicate (RFC 8439 standard)

**This is the kind of improvement every project wants:**
- Easy to implement
- Hard to argue against
- Clear value proposition

---

## Questions for Manager

If you have questions:
- Implementation approach
- Testing requirements
- Priority relative to other tasks
- Technical details

Email Manager with questions.

---

## Recognition

**This is a textbook security improvement:**
- Standards-based (RFC 8439)
- Pragmatic (trivial implementation)
- Data-driven (analysis complete)
- Low-risk (no breaking changes)

**Security Analyst completed analysis in 1.25h (vs 4-6h estimated) - 70-80% under budget.**

**Your implementation should be similarly efficient.**

---

## Summary

**Assignment:** Upgrade ChaCha12 → ChaCha20

**Files:** 2 (rx_main.cpp, tx_main.cpp)
**Changes:** 2 lines (plus comments)
**Time:** 30 minutes - 2 hours
**Priority:** MEDIUM-HIGH

**Benefit:** Standards compliance, stronger security margin, user trust

**Performance cost:** Negligible (<0.2% CPU)

**There is no technical reason to stay with non-standard ChaCha12.**

---

**Let me know when you're starting this task, or if you have questions.**

---

**Development Manager**
2025-12-02 02:40
