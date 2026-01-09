# Task Update: Collaborate with Security Analyst on ESP32 Crash Investigation

**Date:** 2025-12-05 13:05
**To:** Developer
**From:** Manager
**Re:** ESP32 ChaCha crash investigation - collaboration approach
**Priority:** HIGH

---

## Task Update: Collaborative Investigation

This is an update to your assigned task: **debug-esp32-chacha-crash**

You'll be **working together with the Security Analyst** on this investigation since they have the hardware and benchmark code.

---

## Division of Responsibilities

### Security Analyst Has:
- ESP32 TX hardware
- Benchmark code that crashes
- Familiarity with crypto implementation
- Already attempted tests

### You Will Provide:
- Systematic debugging methodology
- Incremental testing approach
- Code analysis expertise
- Root cause investigation

### Work Together On:
- Bisect method to isolate crash
- Root cause analysis
- Fix implementation
- Verification testing

---

## Your Role: Guide the Investigation

You should **collaborate with the Security Analyst** using these approaches:

### Approach 1: Incremental Testing (from your original assignment)

Guide them through systematic testing:
1. Basic ESP32 functionality test
2. Add components one at a time
3. Identify exact crash point
4. Verify production encryption safety

### Approach 2: Bisect Method (NEW)

**If production works but benchmark crashes**, use binary search to isolate:

**Bisect Process:**
1. Comment out half the benchmark code
2. Test: does it crash?
3. If YES → problem is in remaining half
4. If NO → problem is in commented half
5. Repeat on problematic half until minimal crashing code found

**Why bisect works:**
- Fast convergence: ~7 iterations for 100 lines (log₂(100))
- Each iteration: 5 minutes (comment, build, flash, test)
- **Total: 30-45 minutes to isolate root cause**

---

## Investigation Steps

### Phase 1: Production Safety Verification (CRITICAL)

**Security Analyst tests:**
1. Flash normal production firmware to ESP32 TX
2. Test encryption handshake with RX
3. Verify encrypted link works

**You analyze:**
- If production crashes → CRITICAL bug, emergency fix needed
- If production works → benchmark-specific issue, proceed to Phase 2

---

### Phase 2: Incremental Testing

**Security Analyst runs tests, you guide the process:**

Starting from minimal test, add one component at a time:
- Basic serial communication
- Include ChaCha library
- Create ChaCha object
- Initialize with key/nonce
- Perform single encrypt
- Test ChaCha20 vs ChaCha12
- Add benchmark loop

**Document at each step:**
- Does it crash? If yes, you've found the breaking change
- Capture error messages, stack traces, behavior

---

### Phase 3: Bisect Method (if needed)

**If crash is in benchmark code, you guide the bisect:**

**Example bisect on hypothetical benchmark:**
```cpp
// Section 1: Setup
ChaCha cipher(20);
cipher.setKey(key, 32);
cipher.setIV(nonce, 12);

// Section 2: Data prep
uint8_t testData[1024];
memset(testData, 0, 1024);

// Section 3: Timing
unsigned long start = micros();

// Section 4: Loop
for (int i = 0; i < 10000; i++) {
    cipher.encrypt(testData, 1024);
}

// Section 5: Results
unsigned long end = micros();
float throughput = calculate(...);

// Section 6: Output
Serial.println(throughput);
```

**Iteration 1:** Comment sections 4-6
- Crash? → Problem in sections 1-3
- No crash? → Problem in sections 4-6

**Iteration 2:** Continue on problematic half

**Result:** Minimal crashing code identified

---

## Common Root Causes to Look For

Work with Security Analyst to check:

1. **Stack Overflow**
   - Large buffers (1KB+) on stack
   - Deep call chains
   - Look for: Large local arrays, recursive calls

2. **Heap Issues**
   - Multiple ChaCha object creation
   - Memory leaks in loop
   - Look for: `new` without `delete`, fragmentation

3. **Watchdog Timer**
   - Tight loop without delays
   - Starves system tasks
   - Look for: Long loops without `yield()` or `delay()`

4. **Serial Buffer Overflow**
   - Heavy serial printing in tight loop
   - Buffer can't keep up
   - Look for: `Serial.print()` in hot path

5. **Memory Alignment**
   - ESP32 requires 4-byte alignment
   - ChaCha operations on misaligned data
   - Look for: Unaligned pointers, packed structs

6. **Interrupt Conflicts**
   - Benchmark disables interrupts too long
   - Conflicts with WiFi/BLE
   - Look for: Critical sections, interrupt disabling

---

## Collaboration Protocol

### Communication Flow

**Security Analyst → You:**
- Test results at each step
- Error messages and stack traces
- Hardware observations

**You → Security Analyst:**
- Next test to run
- Code modifications to try
- Analysis and hypotheses

**Both → Manager:**
- Progress updates
- Root cause identification
- Fix recommendations

### Example Collaboration

**Security Analyst:** "Production firmware works fine, encryption tested OK. Benchmark crashes immediately on boot."

**You:** "Good, production is safe. Let's bisect the benchmark. Comment out everything after cipher initialization. Does it still crash?"

**Security Analyst:** "No crash with just initialization."

**You:** "OK, uncomment half of what you commented. Try adding just the data preparation section."

**Security Analyst:** "Crashes when I add the 1KB testData array."

**You:** "Found it! Stack overflow from large buffer. Try reducing to 64 bytes or move to heap with malloc."

---

## Deliverables

### Joint Investigation Report

You and Security Analyst should produce:

1. **Phase 1 Results:** Production safety status
2. **Phase 2 Results:** Incremental test results (if needed)
3. **Phase 3 Results:** Bisect findings (if needed)
4. **Root Cause:** Technical analysis
5. **Fix Recommendation:** How to resolve

### Report Format

```markdown
## Investigation Summary

**Production Status:** ✅ Working / ❌ Broken
**Crash Isolated To:** [specific code/component]
**Root Cause:** [technical explanation]
**Fix Recommendation:** [solution]

## Test Results

[Detailed results from each phase]

## Technical Analysis

[Your analysis of why it crashes]

## Proposed Fix

[Code changes or approach]
```

---

## Timeline

**Phase 1:** 30 minutes (production testing)
**Phase 2:** 1-2 hours (if needed - incremental testing)
**Phase 3:** 30-45 minutes (if needed - bisect)

**Total:** 2-4 hours estimated

---

## Priority

**HIGH** - This blocks:
- Finding #5 (ChaCha20 upgrade analysis)
- privacylrs-implement-chacha20-upgrade project

**CRITICAL if production is broken** - would require immediate emergency fix

---

## Your Task Summary

1. ✅ Review Security Analyst's crash report (already in your awareness)
2. 📋 Coordinate with Security Analyst on investigation approach
3. 📋 Guide them through systematic testing (incremental or bisect)
4. 📋 Analyze results and identify root cause
5. 📋 Propose fix or deeper investigation path
6. 📋 Send joint completion report to Manager

---

## Questions?

If you need:
- Access to PrivacyLRS code
- Clarification on crypto implementation
- Hardware details
- Anything else

Contact Security Analyst or let me know.

---

**Manager**
2025-12-05 13:05

**Related Emails:**
- Your original assignment: `2025-12-05-1245-task-debug-esp32-chacha-crash.md`
- Security Analyst update: `2025-12-05-1300-finding5-bisect-investigation.md`
