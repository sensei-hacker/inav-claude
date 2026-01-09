# Project: Debug ESP32 ChaCha Crash

**Status:** 📋 TODO
**Priority:** HIGH
**Type:** Bug Investigation / Security
**Created:** 2025-12-05
**Estimated Time:** 2-4 hours

---

## Overview

Debug critical ESP32 crash discovered during ChaCha20 benchmark testing. Crash causes boot loop with null pointer dereference. Must verify production encryption safety and identify root cause.

---

## Problem

Security Analyst discovered crash while testing Finding #5 (ChaCha20 upgrade):
- **Hardware:** ESP32 TX module
- **Error:** Guru Meditation Error (LoadProhibited)
- **Symptoms:** Null pointer dereference, boot loop
- **Frequency:** 100% reproducible (crashed in both setup() and loop())

**Critical Question:** Is production ChaCha12 encryption affected?

---

## Objectives

1. Verify ESP32 basic functionality (serial communication)
2. Incrementally test ChaCha components to isolate crash point
3. Identify root cause (library bug, alignment issue, memory corruption)
4. Verify production encryption safety
5. Provide fix or investigation path

---

## Scope

**In Scope:**
- ESP32 TX module testing
- ChaCha library investigation
- Production encryption verification
- Root cause analysis

**Out of Scope:**
- Other hardware platforms (ESP8285, ESP32S3)
- Full benchmark implementation
- Performance analysis (blocked until crash fixed)

---

## Implementation Steps

### Phase 1: Basic Verification
1. Create minimal ESP32 test (serial only)
2. Verify basic functionality works

### Phase 2: Incremental Testing
1. Add ChaCha library include
2. Create ChaCha object
3. Initialize with key/nonce
4. Perform single encrypt operation
5. Test ChaCha20 specifically
6. Add benchmark loop

### Phase 3: Production Verification
1. Flash production firmware
2. Test normal encryption operation
3. Verify safety or identify critical bug

---

## Success Criteria

- [ ] Basic ESP32 functionality verified
- [ ] Crash point identified (exact step)
- [ ] Root cause hypothesis documented
- [ ] Production encryption safety confirmed
- [ ] Fix implemented or investigation path defined

---

## Priority Justification

**HIGH Priority because:**
- Blocks Finding #5 (ChaCha20 upgrade)
- Production encryption safety unknown
- Could be critical security bug affecting live systems
- Security Analyst blocked until resolution

---

## Dependencies

**Blocks:**
- privacylrs-fix-finding5-chacha-benchmark (Finding #5 analysis)
- privacylrs-implement-chacha20-upgrade (cannot proceed without safety verification)

**Related:**
- privacylrs-complete-tests-and-fix-finding1 (completed, PR #18 merged)
- privacylrs-fix-finding4-secure-logging (completed, PR #19)

---

## Assignee

Developer

---

## Assignment Email

`claude/manager/sent/2025-12-05-1245-task-debug-esp32-chacha-crash.md`
