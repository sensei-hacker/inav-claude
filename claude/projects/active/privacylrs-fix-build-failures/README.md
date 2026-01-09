# Project: Fix PrivacyLRS Build Failures

**Created:** 2025-12-02
**Status:** PROPOSED
**Priority:** MEDIUM
**Repository:** PrivacyLRS
**Assigned to:** TBD (Recommended: Developer)

---

## Objective

Resolve pre-existing build failures in PrivacyLRS CI/CD pipeline that are blocking proper validation of security fixes.

---

## Background

PR #18 (Finding #1 fix) shows build failures that are **pre-existing** and unrelated to the security implementation:
- Same failures exist in merged PR #16 (test suite)
- Failures exist before any counter increment changes
- Affect all PRs to secure_01 branch

---

## Scope

### 1. Fix Test Suite Compilation (Native Platform)

**Error:**
```
test/test_encryption/test_encryption.cpp:1535:5: error: 'printf' was not declared in this scope
```

**Fix required:**
- Add `#include <stdio.h>` to test_encryption.cpp
- Verify native test builds pass
- May need other standard library includes

**Estimated effort:** 15-30 minutes

---

### 2. Fix NimBLE Library Conflicts (ESP32/ESP32S3 TX via UART)

**Errors:**
```
multiple definition of `NimBLEClient::serviceDiscoveredCB(...)`
multiple definition of `NimBLERemoteCharacteristic::descriptorDiscCB(...)`
multiple definition of `NimBLERemoteService::characteristicDiscCB(...)`
```

**Root cause:** NimBLE-Arduino library version conflict (duplicate symbols)

**Affected platforms:**
- Unified_ESP32_2400_TX_via_UART
- Unified_ESP32_900_TX_via_UART
- Unified_ESP32_LR1121_TX_via_UART
- Unified_ESP32S3_2400_TX_via_UART
- Unified_ESP32S3_900_TX_via_UART
- Unified_ESP32S3_LR1121_TX_via_UART

**Investigation needed:**
- Which NimBLE-Arduino versions are being pulled?
- Why are multiple versions present?
- Which version should be used?

**Possible fixes:**
1. Pin NimBLE-Arduino to specific version in platformio.ini
2. Remove duplicate dependency declarations
3. Update to newer NimBLE version that fixes conflicts
4. Add library conflict resolution configuration

**Estimated effort:** 1-3 hours

---

## Deliverables

1. ✅ Test suite compiles on native platform
2. ✅ ESP32/ESP32S3 TX builds pass
3. ✅ All CI checks green on test PR
4. ✅ Documentation of fixes applied

---

## Success Criteria

- [ ] Native test build succeeds
- [ ] All 6 ESP32/ESP32S3 TX via UART builds pass
- [ ] No new build failures introduced
- [ ] PR #18 can be properly validated

---

## Dependencies

**Blocks:**
- PR #18 validation (Finding #1 fix)
- Future PRs to secure_01 branch

**Blocked by:**
- Manager approval

---

## Timeline Estimate

- Investigation: 30 minutes
- Test suite fix: 15 minutes
- NimBLE fix: 1-2 hours
- Testing/validation: 1 hour
- **Total: 2-4 hours**

---

## Resources

**Build logs:**
- PR #18: https://github.com/sensei-hacker/PrivacyLRS/pull/18
- PR #16: https://github.com/sensei-hacker/PrivacyLRS/pull/16

**GitHub Actions:**
- Failed test run: https://github.com/sensei-hacker/PrivacyLRS/actions/runs/19843243622/job/56855849764
- Failed ESP32 build: https://github.com/sensei-hacker/PrivacyLRS/actions/runs/19843243622/job/56855880480

---

## Notes

- These are infrastructure issues, not security issues
- Recommend assigning to Developer (build system expertise)
- Security Analyst available for consultation
- After completion, Security Analyst will verify PR #18 passes all checks

---

## Related Projects

- privacylrs-complete-tests-and-fix-finding1 (parent project)
- Depends on completion before Finding #1 can be merged

---

**Status:** Awaiting manager approval
