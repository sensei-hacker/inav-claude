# Todo List: Fix Finding 4 - Secure Cryptographic Key Logging

## Phase 1: Audit - Find All Sensitive Logging

### Search for Key Logging
- [ ] Search for "session key" in all source files
- [ ] Search for "master key" in all source files
- [ ] Search for "encrypted" in all source files
- [ ] Search for "decrypted" in all source files
- [ ] Search for "nonce" in logging statements
- [ ] Search for "counter" in logging statements
- [ ] Review all DBGLN statements manually

### Document Findings
- [ ] List all files containing key logging
- [ ] List all line numbers
- [ ] Categorize by sensitivity:
  - [ ] Session keys (HIGH - must protect)
  - [ ] Master keys (HIGH - must protect)
  - [ ] Nonces (MEDIUM - consider protecting)
  - [ ] Counters (LOW - may be okay to log)
- [ ] Note any other sensitive data being logged

### Known Locations (from finding)
- [ ] Review `rx_main.cpp:516-517`
- [ ] Review `rx_main.cpp:537`
- [ ] Check for similar patterns in tx_main.cpp
- [ ] Check for similar patterns in common.cpp

## Phase 2: Design Secure Logging

### Design Build Flag
- [ ] Choose flag name: `ALLOW_KEY_LOGGING`
- [ ] Determine where to define (build system)
- [ ] Plan default value (OFF)
- [ ] Plan how to enable for debugging

### Design Logging Macro
- [ ] Choose macro name: `DBGLN_KEY`
- [ ] Design implementation using `#ifdef`
- [ ] Add compile-time warning when enabled
- [ ] Ensure macro works with existing DBGLN syntax
- [ ] Consider additional macros:
  - [ ] `DBGLN_NONCE` (for nonces)
  - [ ] `DBGLN_COUNTER` (for counters)
  - Or use single `DBGLN_KEY` for all sensitive data

### Plan Implementation
- [ ] Identify header file for macro definition
- [ ] Identify build system files to modify
- [ ] Plan testing approach
- [ ] Document usage guidelines for developers

## Phase 3: Implementation

### Create Macro Definition
- [ ] Create or update common header file
- [ ] Add macro definition:
  ```cpp
  #ifdef ALLOW_KEY_LOGGING
    #define DBGLN_KEY(...) DBGLN(__VA_ARGS__)
    #warning "KEY LOGGING ENABLED - DO NOT USE IN PRODUCTION"
  #else
    #define DBGLN_KEY(...) ((void)0)
  #endif
  ```
- [ ] Add documentation comment explaining usage
- [ ] Add build date/time stamp when flag enabled (optional)

### Update Build System
- [ ] Locate build configuration files
  - PlatformIO: `platformio.ini`
  - CMake: `CMakeLists.txt`
  - Other: identify relevant files
- [ ] Add build flag definition
- [ ] Ensure flag defaults to OFF (not defined)
- [ ] Document how to enable flag for debugging
- [ ] Test build system changes

### Replace Key Logging Statements
- [ ] Replace session key logging at `rx_main.cpp:516-517`
  - Change `DBGLN("encrypted session key...")` to `DBGLN_KEY(...)`
- [ ] Replace session key logging at `rx_main.cpp:537`
  - Change `DBGLN("Decrypted session key...")` to `DBGLN_KEY(...)`
- [ ] Replace all other key logging found in audit
- [ ] Review each replacement for correctness
- [ ] Ensure syntax is correct

### Add Runtime Warning (Optional Enhancement)
- [ ] Add startup warning when flag enabled:
  ```cpp
  #ifdef ALLOW_KEY_LOGGING
    DBGLN("WARNING: Key logging is ENABLED - production use NOT recommended");
  #endif
  ```
- [ ] Place warning in initialization code

## Phase 4: Testing

### Test Production Build (Flag OFF - Default)
- [ ] Clean build with flag disabled (default)
- [ ] Run firmware
- [ ] Capture all debug output
- [ ] Verify NO session keys in output
- [ ] Verify NO master keys in output
- [ ] Verify encryption/decryption still works
- [ ] Check for any build warnings/errors

### Test Debug Build (Flag ON)
- [ ] Enable ALLOW_KEY_LOGGING in build system
- [ ] Clean build with flag enabled
- [ ] Verify compile-time warning appears
- [ ] Run firmware
- [ ] Capture all debug output
- [ ] Verify session keys ARE logged as expected
- [ ] Verify runtime warning appears (if implemented)
- [ ] Verify encryption/decryption still works

### Test Build System
- [ ] Test default build (flag should be OFF)
- [ ] Test enabling flag via build command
- [ ] Test enabling flag via build config file
- [ ] Verify flag works on all target platforms
- [ ] Test clean vs incremental builds

### Regression Testing
- [ ] Test all normal firmware functionality
- [ ] Verify no impact on performance
- [ ] Verify no new bugs introduced
- [ ] Check for any unintended side effects

## Phase 5: Code Review and Documentation

### Code Review
- [ ] Review all macro definitions
- [ ] Review all replacements
- [ ] Verify no keys logged in production mode
- [ ] Verify keys logged in debug mode
- [ ] Check for any missed logging locations
- [ ] Ensure coding standards compliance

### Security Review
- [ ] Verify all key logging is protected
- [ ] Check for any bypass possibilities
- [ ] Verify flag defaults to secure state (OFF)
- [ ] Confirm fix addresses original vulnerability
- [ ] Check for any new issues introduced

### Documentation
- [ ] Document the build flag
- [ ] Document the logging macro
- [ ] Add usage examples
- [ ] Document how to enable for debugging
- [ ] Add inline code comments
- [ ] Update developer guidelines
- [ ] Create troubleshooting notes

### Update Build Instructions
- [ ] Document default build behavior
- [ ] Document how to enable key logging for debugging
- [ ] Add security warnings
- [ ] Update README or build documentation

## Phase 6: Completion

### Final Validation
- [ ] Run complete test suite
- [ ] Verify all success criteria met
- [ ] Confirm zero keys in production builds
- [ ] Confirm keys visible in debug builds
- [ ] Review all documentation

### Reporting
- [ ] Create completion report
- [ ] Include test results (production and debug builds)
- [ ] Document any issues found and resolved
- [ ] Include before/after examples
- [ ] Send report to Manager

### Cleanup
- [ ] Archive task assignment from inbox
- [ ] Clean up test artifacts
- [ ] Commit code changes (if applicable to role)
- [ ] Update project status to COMPLETED

## Notes

**Critical Success Factors:**
- All key logging identified and protected
- Production builds completely secure (no key leakage)
- Debug capability preserved when needed
- Build flag works reliably

**Watch Out For:**
- Missing some key logging locations
- Macro syntax errors
- Build system flag not working as expected
- Other sensitive data that should also be protected

**Questions to Resolve:**
- Should nonces and counters also use DBGLN_KEY?
- Should we have separate macros for different sensitivity levels?
- What header file should contain the macro definition?
- What's the exact build system being used?

**Additional Considerations:**
- Consider protecting other sensitive data (nonces, counters)
- Consider adding log sanitization for crash dumps
- Consider security audit of all logging
- Document policy for future logging of sensitive data

**Usage Guidelines for Developers:**
```cpp
// GOOD - Using secure logging for keys
DBGLN_KEY("session key = %d, %d, %d", ...);

// BAD - Direct logging of keys
DBGLN("session key = %d, %d, %d", ...);  // Don't do this!

// GOOD - General debug info
DBGLN("Encryption initialized");

// GOOD - Non-sensitive operational info
DBGLN("Packet received, size = %d", size);
```
