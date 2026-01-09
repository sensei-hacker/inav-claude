# INAV Firmware Code Review Project

## Objective
Systematic code review of `inav/src/main/` to find bugs, logic errors, and potential failure modes. Focus on correctness and reliability, NOT security audits, style, or documentation.

## Scope
- **Target:** 1,366 C files, ~171,000 lines of code
- **Focus:** Runtime errors, logic bugs, edge cases, resource leaks, uninitialized variables
- **Exclude:** Security vulnerabilities, coding style, audit logging, documentation

## Recommended Approach: Two-Phase Strategy

### Phase 1: Automated Static Analysis with cppcheck (FREE)

**Tool:** `cppcheck` - Industry-standard free static analyzer for C/C++

**Installation:**
```bash
sudo apt install cppcheck
```

**Benefits:**
- Fast: Analyzes entire codebase in minutes
- Catches: null pointer dereferences, buffer overflows, uninitialized variables, memory leaks, dead code, logic errors
- Low false-positive rate compared to other tools
- Understands embedded C patterns

**Recommended Command:**
```bash
cd /home/raymorris/Documents/planes/inavflight/inav
cppcheck --enable=warning,performance,portability,style \
         --suppress=style \
         --suppress=unusedFunction \
         --inconclusive \
         --force \
         --std=c99 \
         -I src/main \
         src/main/ 2>&1 | tee cppcheck-results.txt
```

**Expected Output:** List of potential issues with file:line references that Claude can then review.

### Phase 2: Claude Review of High-Value Directories

After cppcheck identifies hotspots, Claude reviews by priority:

| Priority | Directory | Lines | Rationale |
|----------|-----------|-------|-----------|
| 1 | `navigation/` | 12,050 | Complex state machines, GPS math, safety-critical |
| 2 | `flight/` | 7,052 | PID controllers, failsafes, motor mixing |
| 3 | `fc/` | 16,200 | Flight controller core, mode logic, arming |
| 4 | `sensors/` | 5,292 | IMU fusion, calibration, data integrity |
| 5 | `rx/` | 5,201 | Radio protocols, failsafe triggers |
| 6 | `io/` | 28,529 | Large but mostly peripheral I/O (lower risk) |
| 7 | `drivers/` | 24,574 | Hardware abstraction (mostly stable) |

### Why This Order?

1. **Safety-critical code first** - navigation and flight control affect aircraft behavior
2. **State machine complexity** - nav/flight have the most complex logic
3. **User-facing failures** - fc/ handles modes, arming, user commands
4. **Data integrity** - sensors/ affects all downstream calculations
5. **External inputs** - rx/ processes untrusted radio data

## Alternative/Additional Tools (All FREE)

| Tool | Install | Best For |
|------|---------|----------|
| `clang-tidy` | Already installed | Modern C++ checks, some C support |
| `scan-build` | `sudo apt install clang-tools` | Clang static analyzer |
| `splint` | `sudo apt install splint` | Strict C linting (many false positives) |
| `flawfinder` | `sudo apt install flawfinder` | Security-focused (not our goal) |
| `gcc -Wall -Wextra` | Already have | Compiler warnings on build |

## Workflow Recommendation

1. **Developer runs cppcheck** on full codebase (~5-10 min)
2. **Developer filters results** to remove noise (unused functions, style)
3. **Developer creates summary** of findings by directory
4. **Claude reviews** cppcheck output + manual inspection of top 3 priority directories
5. **Issues filed** for confirmed bugs

## Deliverables

- [ ] cppcheck results file with filtered findings
- [ ] Summary of issues by severity and directory
- [ ] Manual review notes for navigation/, flight/, fc/
- [ ] GitHub issues or PR for confirmed bugs

## Estimated Effort

- Phase 1 (cppcheck): 2-3 hours
- Phase 2 (Claude review per directory): 2-4 hours each
- Total for top 5 directories: 15-20 hours

## Status
TODO - Awaiting assignment
