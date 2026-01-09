# Project: Fix Finding 5 - ChaCha12 vs ChaCha20 Benchmark

**Status:** 📋 TODO
**Priority:** MEDIUM
**Severity:** MEDIUM
**Type:** Security Enhancement / Performance Analysis
**Created:** 2025-11-30
**Assigned:** Security Analyst (or Developer)
**Estimated Time:** 4-6 hours

## Overview

Benchmark ChaCha20 (20 rounds) performance on target hardware and decide whether to upgrade from ChaCha12 (12 rounds) based on actual performance measurements.

## Problem

**Security Finding 5 (MEDIUM):** ChaCha12 vs ChaCha20

**Location:**
- `PrivacyLRS/src/src/rx_main.cpp:506`
- `PrivacyLRS/src/src/tx_main.cpp:36, 305`

**Current Code:**
```cpp
uint8_t rounds = 12;
ChaCha cipher(12);
```

**Issue:**
- Uses ChaCha12 (12 rounds) instead of standard ChaCha20 (20 rounds)
- ChaCha20 is the widely-analyzed standard
- Reduced rounds may have security implications
- Unknown if performance difference is significant

**Security Considerations:**
- ChaCha20 has extensive cryptanalysis
- ChaCha12 has less security margin
- Performance critical for RC link (low latency required)
- Need to balance security vs performance

## Approved Solution

**Decision:** Benchmark first, then decide

Benchmark ChaCha20 performance on target hardware before making decision:
- If performance impact is negligible → upgrade to ChaCha20
- If performance impact is significant → document decision to stay with ChaCha12

**Rationale:**
- Data-driven decision making
- Performance is critical for RC link
- Need actual measurements on target hardware
- ChaCha12 may be adequate for threat model
- Avoid premature optimization or premature security choices

## Objectives

1. Set up benchmarking infrastructure
2. Benchmark ChaCha12 performance (baseline)
3. Benchmark ChaCha20 performance
4. Measure performance impact on actual RC operations
5. Analyze latency, throughput, and CPU usage
6. Make informed decision based on data
7. Implement decision (upgrade to ChaCha20 or document rationale for ChaCha12)

## Implementation Steps

### Phase 1: Setup (1-2 hours)
1. Identify target hardware platforms
2. Set up benchmarking environment
3. Create benchmark test harness
4. Implement timing measurements
5. Verify baseline operation

### Phase 2: ChaCha12 Baseline (1 hour)
1. Benchmark ChaCha12 encryption
2. Benchmark ChaCha12 decryption
3. Measure latency (single operation)
4. Measure throughput (ops/second)
5. Measure CPU usage
6. Test under realistic packet rates
7. Document baseline metrics

### Phase 3: ChaCha20 Testing (1 hour)
1. Modify code to use ChaCha20 (20 rounds)
2. Benchmark ChaCha20 encryption
3. Benchmark ChaCha20 decryption
4. Measure latency (single operation)
5. Measure throughput (ops/second)
6. Measure CPU usage
7. Test under realistic packet rates
8. Document ChaCha20 metrics

### Phase 4: Analysis (1 hour)
1. Compare ChaCha12 vs ChaCha20 performance
2. Calculate percentage difference
3. Assess impact on RC link latency
4. Assess impact on maximum packet rate
5. Determine if difference is acceptable
6. Make recommendation

### Phase 5: Decision and Implementation (1-2 hours)
1. Review benchmark results with stakeholder (if needed)
2. Make final decision
3. If upgrading to ChaCha20: implement permanently
4. If staying with ChaCha12: document security rationale
5. Update code and documentation

## Scope

**In Scope:**
- ChaCha12 and ChaCha20 benchmarking
- Performance analysis on target hardware
- Decision documentation
- Code update if upgrading to ChaCha20

**Out of Scope:**
- Other cipher algorithms
- Other security findings
- Protocol changes
- Backwards compatibility (if ChaCha20 chosen)

## Success Criteria

- [ ] Benchmarking infrastructure created
- [ ] ChaCha12 baseline metrics collected
- [ ] ChaCha20 metrics collected
- [ ] Performance comparison documented
- [ ] Decision made based on data
- [ ] If upgrading: ChaCha20 implemented and tested
- [ ] If staying: Security rationale documented
- [ ] Results and decision documented

## Testing Requirements

**Benchmark Metrics:**
1. **Latency (microseconds per operation):**
   - Single packet encryption
   - Single packet decryption

2. **Throughput (operations per second):**
   - Continuous encryption
   - Continuous decryption

3. **CPU Usage (percentage):**
   - Idle vs active
   - Peak usage

4. **RC Link Impact:**
   - Maximum packet rate achievable
   - End-to-end latency
   - Jitter

**Test Platforms:**
- Primary target hardware (specify MCU)
- Secondary targets (if multiple platforms supported)

**Success Metrics:**
- Benchmarks completed on all target platforms
- Performance difference quantified
- Decision justified by data

## Decision Criteria

**Acceptable Performance Impact:**
- Latency increase < 10% → Upgrade to ChaCha20
- Latency increase < 25% → Consider upgrade (stakeholder decision)
- Latency increase > 25% → Stay with ChaCha12, document rationale

**Security Consideration:**
- ChaCha12 is still considered secure for most applications
- No known practical attacks on ChaCha12
- RC telemetry threat model may not require ChaCha20 security margin

## Dependencies

**Technical:**
- Access to target hardware or accurate simulator
- Timing/profiling tools
- Understanding of ChaCha implementation
- Realistic test scenarios

**Related Findings:**
- Independent of other findings
- Results may inform overall security posture

## Risk Assessment

**Technical Risks:**
- Benchmark may not reflect real-world usage (mitigation: use realistic scenarios)
- Performance may vary across platforms (mitigation: test on all platforms)
- ChaCha20 may be too slow (mitigation: document and stay with ChaCha12)

**Project Risks:**
- MEDIUM priority - not urgent but important
- Low risk - primarily analysis work
- Decision may be to keep ChaCha12 (acceptable outcome)

## Priority Justification

**MEDIUM** - This is a security enhancement rather than a critical vulnerability fix. ChaCha12 is still considered secure, but ChaCha20 would be better if performance allows. Data-driven decision is appropriate.

## Notes

**Reference Documents:**
- Security findings report: `claude/manager/inbox-archive/2025-11-30-1500-findings-privacylrs-comprehensive-analysis.md`
- Decisions document: `claude/projects/security-analysis-privacylrs-initial/findings-decisions.md`

**Stakeholder Decision:**
"Option 2" (Benchmark first, then decide)

**ChaCha Round Comparison:**
- **ChaCha20:** 20 rounds, widely analyzed, IETF standard (RFC 8439)
- **ChaCha12:** 12 rounds, 40% fewer rounds, faster but less security margin
- **ChaCha8:** 8 rounds, even faster, significantly less analyzed

**Security Research:**
- ChaCha20: No known practical attacks
- ChaCha12: No known practical attacks for most use cases
- ChaCha8: Some theoretical concerns

**Typical Performance:**
- ChaCha20: ~3-5 cycles per byte on modern CPUs
- ChaCha12: ~60% of ChaCha20 time (rough estimate)
- Actual measurements needed on embedded hardware

**Decision Documentation Required:**
- If staying with ChaCha12: Document why performance requires it
- Include benchmark data
- Include security assessment that ChaCha12 is adequate for threat model
