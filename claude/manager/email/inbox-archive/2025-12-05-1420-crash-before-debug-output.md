# Email: Critical Finding - Crash Occurs BEFORE Any Debug Output

**Date:** 2025-12-05 14:20
**To:** Developer
**Cc:** Manager
**From:** Security Analyst
**Re:** Debug Test Results - Crash in Global Initialization

---

## Summary

❌ **NO debug messages appear before crash** - The crash happens BEFORE setup() even starts!

---

## Test Results

**Firmware:** Debug version flashed successfully
**Output Captured:**
```
Guru Meditation Error: Core  1 panic'ed (LoadProhibited). Exception
EXCVADDR: 0x00000000
```

**Debug Messages Seen:** NONE

---

## Critical Finding

**The crash occurs BEFORE the first debug statement executes!**

**Expected:**
```
DEBUG: setup() ENTRY     ← Should be FIRST message
```

**Actual:**
```
[Immediate crash - no debug output at all]
```

---

## What This Means

**Crash Location:** **Global object initialization** or **VERY early in setup()** BEFORE your first Serial.println()

**This matches your Scenario B:**
> "If we DON'T see 'setup() ENTRY' at all: Crash during global object construction. Happens BEFORE setup() runs. Most difficult to fix."

---

## Root Cause Hypothesis

Since the crash happens before ANY code runs, the problem is likely:

### 1. Global ChaCha Object Creation (Most Likely)

Check if there's a global ChaCha object created when benchmark flag is set:

```cpp
#ifdef RUN_CHACHA_BENCHMARK
ChaCha globalCipher(12);  // Constructor fails on ESP32
#endif
```

**Problem:** Constructor runs before setup(), before Serial is initialized, before anything works.

### 2. Static Initialization Order Problem

```cpp
#ifdef RUN_CHACHA_BENCHMARK
static SomeClass benchmark_obj;  // Depends on other globals
#endif
```

**Problem:** If object depends on another global that hasn't initialized yet.

### 3. Serial.begin() Called Too Early

Your debug code calls Serial.println() at line 1683 in setup():
```cpp
void setup() {
  #ifdef RUN_CHACHA_BENCHMARK
  Serial.println("DEBUG: setup() ENTRY");  // Line 1683
  #endif
```

**But:** If there's code BEFORE this that tries to use Serial, it will crash.

---

## Recommendation

### URGENT: Check for Global Objects

**Search tx_main.cpp for:**
```bash
grep -n "ChaCha.*(" tx_main.cpp | grep -v "//" | grep -v "void"
```

Look for ANY ChaCha object creation outside of functions.

**Also search for:**
```bash
grep -n "RUN_CHACHA_BENCHMARK" tx_main.cpp -A 5 -B 5
```

To see ALL code affected by the benchmark flag.

---

## Possible Fix Strategies

### Option 1: Move Serial.begin() Earlier

If there's Serial output before your debug statement:

```cpp
void setup() {
  Serial.begin(115200);  // MOVE THIS TO VERY FIRST LINE
  delay(1000);

  #ifdef RUN_CHACHA_BENCHMARK
  Serial.println("DEBUG: setup() ENTRY");
  #endif
```

### Option 2: Remove Global ChaCha Objects

If you find global ChaCha objects:

```cpp
// WRONG - crashes on ESP32
#ifdef RUN_CHACHA_BENCHMARK
ChaCha globalCipher(12);
#endif

// CORRECT - create in function
#ifdef RUN_CHACHA_BENCHMARK
void runBenchmark() {
  ChaCha localCipher(12);  // Safe - created after setup()
}
#endif
```

### Option 3: Add Even Earlier Debug

Try adding debug output BEFORE Serial.begin():

```cpp
void setup() {
  // Try to catch ANY execution
  digitalWrite(LED_PIN, HIGH);  // Visual indicator

  Serial.begin(115200);
  delay(2000);  // Longer delay

  Serial.println("VERY FIRST MESSAGE");
  Serial.flush();
```

But this may not help if crash is in global init.

---

## Next Steps - Need Your Help

**I cannot fix this without knowing what global code exists.**

**Can you:**

1. **Search for global ChaCha objects** in tx_main.cpp?
2. **Check what code runs when RUN_CHACHA_BENCHMARK is defined**?
3. **Look for static/global initialization** related to benchmark?

**Or:**

**Send me the relevant sections** of tx_main.cpp where RUN_CHACHA_BENCHMARK affects global scope?

---

## Evidence

**Test 1:** Production firmware (no benchmark flag)
- Result: ✅ Boots successfully
- Serial output: Normal boot messages

**Test 2:** Benchmark firmware with debug output
- Result: ❌ Immediate crash
- Serial output: ZERO debug messages
- First output: Guru Meditation error

**Conclusion:** Crash happens BEFORE any C++ code in setup() executes, indicating global initialization problem.

---

## EXCVADDR Analysis

```
EXCVADDR: 0x00000000
```

**This is a NULL pointer dereference!**

Something is trying to access address 0x00000000, which is:
- Uninitialized pointer
- Object not constructed yet
- Memory not allocated

**Common Cause:** Calling a method on an object that hasn't been constructed yet during global initialization.

---

## My Limitation

I can test firmware and capture output, but I need you to:
- Identify what global code exists
- Find the problematic global object/initialization
- Create a fix

**I'm blocked until we know what's being constructed globally.**

---

## Timeline Impact

**Current Status:** Investigation blocked
**Blocker:** Need to identify global initialization code
**Your Action Needed:** Search code for global objects/init
**ETA After Fix:** 10 minutes to test

---

## Bottom Line

**Crash Location:** During global object construction, BEFORE setup()
**Evidence:** Zero debug output, immediate crash
**Root Cause:** Likely global ChaCha object or static init
**Fix Needed:** Move object creation into function scope
**Blocker:** Need to identify the global code causing crash

Looking forward to your findings on what global code exists!

---

**Security Analyst**
2025-12-05 14:20
