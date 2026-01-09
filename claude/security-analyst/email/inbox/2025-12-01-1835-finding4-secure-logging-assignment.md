# Assignment: Fix Finding #4 - Secure Cryptographic Key Logging

**Date:** 2025-12-01 18:35
**To:** Security Analyst / Cryptographer
**From:** Manager
**Subject:** New Assignment - Implement Secure Logging for Finding #4
**Priority:** HIGH
**Project:** privacylrs-fix-finding4-secure-logging

---

## Assignment Overview

You are assigned to implement the fix for **Finding #4 (HIGH): Cryptographic Key Logging in Production Code**.

**Project Location:** `claude/projects/privacylrs-fix-finding4-secure-logging/`

---

## Background

During your comprehensive security analysis of PrivacyLRS, you identified that cryptographic keys (session keys, master keys) are being logged via `DBGLN()` statements. This poses a security risk if these logs appear in production builds.

**Your Finding (Finding #4):**
- **Severity:** HIGH
- **Location:** `PrivacyLRS/src/src/rx_main.cpp:516-517, 537`
- **Issue:** Session keys logged in debug output
- **Impact:** Potential key exposure through serial console, log files, crash dumps

**Stakeholder Decision:** "Option 2" - Implement secure logging with explicit build flag

---

## Problem Statement

**Current Code:**
```cpp
DBGLN("encrypted session key = %d, %d, %d, %d", ...);
DBGLN("Decrypted session key: %s", sessionKey);
```

**Why This Is A Problem:**
- Keys may be logged in production builds
- Keys could leak through:
  - Serial console output
  - Log files
  - Crash dumps
  - Debug interfaces
- Violates security best practices
- Compromises the entire encryption system

**Critical Requirement:** Keys should NEVER be logged in production builds.

---

## Approved Solution

**Implement secure logging with build flag:**

1. Create `DBGLN_KEY()` macro that only logs when `ALLOW_KEY_LOGGING=1` build flag is set
2. Replace all key logging with this secure macro
3. Add compile-time warning when flag is enabled
4. Default: Flag OFF (production safe)

**Example Implementation:**
```cpp
// In common header (e.g., encryption.h or common.h)
#ifdef ALLOW_KEY_LOGGING
  #define DBGLN_KEY(...) DBGLN(__VA_ARGS__)
  #warning "KEY LOGGING ENABLED - DO NOT USE IN PRODUCTION"
#else
  #define DBGLN_KEY(...) ((void)0)  // No-op in production
#endif

// Usage in code:
DBGLN_KEY("Decrypted session key: %s", sessionKey);  // Safe - only logs if flag enabled
```

---

## Tasks

### Phase 1: Audit All Key Logging (1h)

**Find all locations where cryptographic keys are logged:**

1. **Search for session key logging:**
   ```bash
   grep -rn "session key" PrivacyLRS/src/
   grep -rn "sessionKey" PrivacyLRS/src/
   ```

2. **Search for master key logging:**
   ```bash
   grep -rn "master key" PrivacyLRS/src/
   grep -rn "masterKey" PrivacyLRS/src/
   ```

3. **Search for other sensitive crypto material:**
   ```bash
   grep -rn "DBGLN.*key" PrivacyLRS/src/
   grep -rn "DBGLN.*nonce" PrivacyLRS/src/
   grep -rn "DBGLN.*counter" PrivacyLRS/src/
   ```

4. **Document findings:**
   - List all locations
   - Categorize by sensitivity (critical, moderate, low)
   - Note which need secure logging

**Deliverable:** List of all key logging locations

### Phase 2: Design Secure Logging Macro (30m)

**Design decisions:**

1. **Macro name:** `DBGLN_KEY()` (clear, consistent with existing `DBGLN()`)

2. **Build flag name:** `ALLOW_KEY_LOGGING` (explicit, hard to enable accidentally)

3. **Implementation approach:**
   - Use `#ifdef` for compile-time elimination (zero runtime cost)
   - Add `#warning` to alert developers when enabled
   - Keep interface identical to `DBGLN()`

4. **Header location:**
   - Add to existing header (e.g., `encryption.h` or `common.h`)
   - Or create new `secure_logging.h`

**Deliverable:** Design document with macro definition

### Phase 3: Implementation (1-2h)

**Implementation steps:**

1. **Create secure logging macro:**
   - Add to appropriate header file
   - Include compile-time warning
   - Test compilation with and without flag

2. **Add build flag to build system:**
   - Locate build configuration (PlatformIO or CMake)
   - Document how to enable flag (e.g., `build_flags = -DALLOW_KEY_LOGGING`)
   - Ensure default is OFF

3. **Replace all key logging:**
   - Change `DBGLN("...key...")` to `DBGLN_KEY("...key...")`
   - Keep non-sensitive `DBGLN()` unchanged
   - Update all identified locations from Phase 1

4. **Add usage documentation:**
   - Document in README or code comments
   - Explain when to use `DBGLN_KEY()` vs `DBGLN()`
   - Warn against production use

**Deliverable:** Code changes implementing secure logging

### Phase 4: Testing and Validation (1h)

**Test scenarios:**

1. **Production build (flag OFF - default):**
   ```bash
   # Build without flag
   pio run -e <target>

   # Expected:
   # - No compile warnings
   # - No keys in output
   # - Encryption still works
   ```

2. **Debug build (flag ON):**
   ```bash
   # Build with flag enabled
   pio run -e <target> -DALLOW_KEY_LOGGING

   # Expected:
   # - Compile warning: "KEY LOGGING ENABLED - DO NOT USE IN PRODUCTION"
   # - Keys appear in output
   # - Encryption still works
   ```

3. **Verify logging behavior:**
   - Run with production build → NO keys visible
   - Run with debug build → Keys visible
   - Test on actual hardware or SITL

**Deliverable:** Test results confirming proper behavior

---

## Success Criteria

- [x] All key logging locations identified
- [x] Secure logging macro (`DBGLN_KEY`) implemented
- [x] Build flag (`ALLOW_KEY_LOGGING`) added
- [x] All key logging replaced with secure macro
- [x] Production build: NO keys logged ✅
- [x] Debug build (flag ON): Keys logged ✅
- [x] Compile warning when flag enabled ✅
- [x] Documentation updated
- [x] Tests pass (existing encryption tests)

---

## Estimated Time

**Total:** 3-4 hours

- Phase 1 (Audit): 1h
- Phase 2 (Design): 30m
- Phase 3 (Implementation): 1-2h
- Phase 4 (Testing): 1h

---

## Important Notes

### Security Considerations

**This is a HIGH priority security fix:**
- Keys should NEVER leak in production
- Even debug builds should warn loudly
- Flag must default to OFF
- Implementation must be foolproof

### Testing Requirements

**You MUST test both modes:**
1. Production mode (flag OFF) - verify NO keys logged
2. Debug mode (flag ON) - verify keys ARE logged

**Don't skip the testing phase** - this is critical for validating the fix works correctly.

### Code Review

**Before submitting:**
- Search entire codebase for any missed key logging
- Verify all `DBGLN()` statements with sensitive data are converted
- Double-check build flag defaults to OFF
- Test on actual hardware if possible

---

## Related Findings

**This fix may benefit:**
- Finding #1: Counter sync debugging (use `DBGLN_KEY` for counter values)
- Finding #2: Counter init debugging (use `DBGLN_KEY` for nonce/counter)
- Any future cryptographic debugging

**Consider creating a general pattern for sensitive data logging.**

---

## Reference Documents

**Security Analysis:**
- Original finding: `claude/manager/inbox-archive/2025-11-30-1500-findings-privacylrs-comprehensive-analysis.md`
- Decisions: `claude/projects/security-analysis-privacylrs-initial/findings-decisions.md`

**Code Locations:**
- Main issue: `PrivacyLRS/src/src/rx_main.cpp:516-517, 537`
- TX side: `PrivacyLRS/src/src/tx_main.cpp` (check for similar logging)
- Common: `PrivacyLRS/src/src/common.cpp` (check encryption functions)

---

## Deliverables

**Submit to Manager:**

1. **Audit Report:**
   - List of all key logging locations
   - Severity assessment for each

2. **Implementation:**
   - Secure logging macro code
   - Build flag configuration
   - All code changes

3. **Test Results:**
   - Production build output (NO keys)
   - Debug build output (keys visible)
   - Compilation warnings

4. **Documentation:**
   - Usage guidelines
   - Build flag instructions
   - Developer notes

5. **Completion Report:**
   - Summary of changes
   - Test validation
   - Recommendations

---

## Example Search Results

**Known locations from your original finding:**

```
PrivacyLRS/src/src/rx_main.cpp:516
    DBGLN("encrypted session key = %d, %d, %d, %d", ...);

PrivacyLRS/src/src/rx_main.cpp:537
    DBGLN("Decrypted session key: %s", sessionKey);
```

**You may find additional locations during Phase 1 audit.**

---

## Git Workflow

**Branches:**
- Base branch: `secure_01`
- Feature branch: `fix-finding4-secure-logging`

**Process:**
1. Checkout `secure_01`
2. Create feature branch: `git checkout -b fix-finding4-secure-logging`
3. Implement changes
4. Test thoroughly
5. Commit with clear message
6. Push to origin
7. Create PR: `fix-finding4-secure-logging` → `secure_01`

---

## Questions?

If you encounter any issues or have questions:
- Email manager immediately
- Document any blockers
- Propose alternatives if needed

---

**This is a straightforward fix with high security impact. Your cryptographic expertise makes you the ideal person for this task.**

**Good luck!**

---

**Development Manager**
2025-12-01 18:35
