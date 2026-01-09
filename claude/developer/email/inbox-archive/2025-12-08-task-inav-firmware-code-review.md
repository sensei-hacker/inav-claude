# Task Assignment: INAV Firmware Code Review

**Date:** 2025-12-08
**To:** Developer
**From:** Manager
**Priority:** MEDIUM
**Project:** inav-firmware-code-review

## Objective

Systematic code review of `inav/src/main/` to find bugs, logic errors, and potential failure modes.

**Focus ON:**
- Runtime errors, null pointer issues
- Logic bugs and edge cases
- Resource leaks, uninitialized variables
- Integer overflow/underflow
- Buffer issues

**Do NOT focus on:**
- Security vulnerabilities (separate project)
- Coding style issues
- Audit logging
- Documentation

## Approach

### Phase 1: Run cppcheck (FREE static analyzer)

1. Install if needed:
```bash
sudo apt install cppcheck
```

2. Run analysis:
```bash
cd /home/raymorris/Documents/planes/inavflight/inav
cppcheck --enable=warning,performance,portability \
         --suppress=unusedFunction \
         --inconclusive \
         --force \
         --std=c99 \
         -I src/main \
         src/main/ 2>&1 | tee cppcheck-results.txt
```

3. Create summary of findings categorized by:
   - Severity (error, warning, portability, performance)
   - Directory (navigation, flight, fc, sensors, rx, etc.)

### Phase 2: Claude Manual Review

Review directories in priority order based on safety-criticality:

| Priority | Directory | Lines | Why |
|----------|-----------|-------|-----|
| 1 | navigation/ | 12,050 | Safety-critical GPS/autopilot |
| 2 | flight/ | 7,052 | PID, failsafes, motor control |
| 3 | fc/ | 16,200 | Core logic, arming, modes |
| 4 | sensors/ | 5,292 | IMU fusion, calibration |
| 5 | rx/ | 5,201 | Radio protocols, failsafes |

For each directory:
1. Review cppcheck findings
2. Manually inspect complex logic
3. Document any bugs found

## Codebase Stats

- Total files: 1,366 C/H files
- Total lines: ~171,000
- Largest: io/ (28k), drivers/ (24k), fc/ (16k)
- Highest risk: navigation/, flight/, fc/

## Deliverables

1. **cppcheck-results.txt** - Raw output from static analyzer
2. **Summary report** - Findings categorized by severity/directory
3. **Manual review notes** - For each priority directory reviewed
4. **GitHub issues** - For confirmed bugs

## Notes

- Start with Phase 1 (cppcheck) to get quick wins
- Report back after cppcheck analysis before deep-diving into manual review
- This is a large project - OK to do in multiple sessions
- clang-tidy is also available if you want a second opinion

## Reference

See project docs:
- `claude/projects/inav-firmware-code-review/summary.md`
- `claude/projects/inav-firmware-code-review/todo.md`
