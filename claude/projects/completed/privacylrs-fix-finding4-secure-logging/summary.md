# Project: Fix Finding 4 - Secure Cryptographic Key Logging

**Status:** 📋 TODO
**Priority:** HIGH
**Severity:** HIGH
**Type:** Security Fix
**Created:** 2025-11-30
**Assigned:** Security Analyst (or Developer)
**Estimated Time:** 3-4 hours

## Overview

Implement secure logging mechanism that prevents cryptographic keys from being logged in production builds while maintaining debugging capability when explicitly enabled.

## Problem

**Security Finding 4 (HIGH):** Cryptographic Key Logging in Production Code

**Location:**
- `PrivacyLRS/src/src/rx_main.cpp:516-517, 537`

**Current Code:**
```cpp
DBGLN("encrypted session key = %d, %d, %d, %d", ...);
DBGLN("Decrypted session key: %s", sessionKey);
```

**Issue:**
- Session keys logged in debug output
- May be included in production builds
- Keys could be exposed through:
  - Serial console output
  - Log files
  - Crash dumps
  - Debug interfaces

**Impact:**
- Potential key exposure in production environments
- Compromises cryptographic security
- Violates security best practices
- Keys should never be logged in production

## Approved Solution

**Decision:** Secure logging with explicit build flag

Implement logging that only outputs keys when explicitly enabled via build flag (e.g., `ALLOW_KEY_LOGGING=1`).

**Rationale:**
- Maintains debugging capability when needed
- Prevents accidental key exposure in production
- Requires explicit opt-in for sensitive logging
- Industry standard approach
- Simple to implement and verify

## Objectives

1. Identify all key logging locations in codebase
2. Design secure logging macro/mechanism
3. Implement build flag-controlled logging
4. Replace all key logging with secure logging
5. Test that keys are NOT logged in production builds
6. Test that keys ARE logged when flag is enabled
7. Document secure logging usage

## Implementation Steps

### Phase 1: Audit (1 hour)
1. Find all instances of key logging
2. Search for session key logging
3. Search for master key logging (if any)
4. Search for nonce logging (if any)
5. Search for counter logging (if any)
6. Document all sensitive data logging locations
7. Categorize by sensitivity level

### Phase 2: Design (30 minutes)
1. Design build flag name (e.g., `ALLOW_KEY_LOGGING`)
2. Design secure logging macro
3. Choose implementation approach:
   - Option A: Conditional compilation (`#ifdef`)
   - Option B: Runtime check with compile-time flag
4. Plan integration with existing logging
5. Document usage guidelines

### Phase 3: Implementation (1-2 hours)
1. Create secure logging macro
2. Add build flag to build system
3. Replace all key logging with secure logging
4. Update other sensitive data logging
5. Add warnings when flag is enabled
6. Test compilation with and without flag

### Phase 4: Testing and Validation (1 hour)
1. Build with flag DISABLED (production mode)
2. Build with flag ENABLED (debug mode)
3. Verify keys not logged in production build
4. Verify keys ARE logged in debug build
5. Test runtime behavior
6. Review all changes

## Scope

**In Scope:**
- All cryptographic key logging
- Session key logging
- Master key logging (if any)
- Build flag implementation
- Secure logging macro

**Out of Scope:**
- Non-cryptographic logging
- General debug logging improvements
- Other security findings
- Logging infrastructure changes

## Success Criteria

- [ ] All key logging identified
- [ ] Secure logging macro implemented
- [ ] Build flag added to build system
- [ ] All key logging uses secure macro
- [ ] Production build (flag OFF): NO keys logged
- [ ] Debug build (flag ON): Keys logged as expected
- [ ] Warning displayed when flag enabled
- [ ] Code reviewed and tested
- [ ] Documentation updated

## Testing Requirements

**Test Scenarios:**
1. Production build (default, flag OFF)
   - Verify no keys in output
   - Verify no keys in logs
   - Test encryption/decryption still works

2. Debug build (flag ON)
   - Verify keys appear in output
   - Verify keys are readable
   - Verify warning is displayed
   - Test encryption/decryption still works

3. Build system
   - Verify flag defaults to OFF
   - Verify flag can be set to ON
   - Verify clean compilation both ways

**Success Metrics:**
- 100% of key logging protected
- Zero keys logged in production mode
- All keys logged in debug mode when flag enabled

## Dependencies

**Technical:**
- Understanding of build system (PlatformIO/CMake)
- Knowledge of preprocessor macros
- Access to build environment

**Related Findings:**
- Independent of other findings
- May be used in Finding 2 implementation (counter logging)
- May be used in Finding 1 implementation (debug logging)

## Risk Assessment

**Technical Risks:**
- May miss some key logging locations (mitigation: thorough code search)
- Build flag may not work on all platforms (mitigation: test on target platforms)
- Low risk overall

**Project Risks:**
- HIGH priority but straightforward fix
- Low risk of breaking existing functionality
- Easy to test and verify

## Priority Justification

**HIGH** - Logging cryptographic keys in production builds is a serious security vulnerability that could lead to key compromise. While not causing system crashes, this represents a clear and easily exploitable security weakness.

## Notes

**Reference Documents:**
- Security findings report: `claude/manager/inbox-archive/2025-11-30-1500-findings-privacylrs-comprehensive-analysis.md`
- Decisions document: `claude/projects/security-analysis-privacylrs-initial/findings-decisions.md`

**Stakeholder Decision:**
"Option 2" (Secure logging with explicit build flag)

**Implementation Example:**
```cpp
// In common header file:
#ifdef ALLOW_KEY_LOGGING
  #define DBGLN_KEY(...) DBGLN(__VA_ARGS__)
  #warning "KEY LOGGING ENABLED - DO NOT USE IN PRODUCTION"
#else
  #define DBGLN_KEY(...) ((void)0)
#endif

// In code:
DBGLN_KEY("session key = %d, %d, %d", ...);  // Only logs if flag enabled
```

**Search Terms for Audit:**
- "session key"
- "master key"
- "nonce"
- "counter"
- "encrypted"
- "decrypted"
- Review all DBGLN statements for sensitive data
