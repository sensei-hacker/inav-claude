# Todo List: Fix Finding 5 - ChaCha12 vs ChaCha20 Benchmark

## Phase 1: Setup Benchmarking Environment

### Identify Test Platforms
- [ ] List all target hardware platforms
- [ ] Identify primary platform (most common)
- [ ] Note MCU specifications (CPU, clock speed, architecture)
- [ ] Determine if SITL/simulator available
- [ ] Prioritize platforms for testing

### Create Benchmark Infrastructure
- [ ] Set up timing measurement code
  - Use hardware timer or cycle counter
  - Ensure microsecond precision
- [ ] Create benchmark test harness
- [ ] Add ChaCha12 benchmark function
- [ ] Add ChaCha20 benchmark function
- [ ] Implement packet simulation
- [ ] Add result logging

### Verify Baseline Operation
- [ ] Test that timing code works
- [ ] Verify ChaCha12 currently operational
- [ ] Measure timing overhead
- [ ] Test packet encryption/decryption
- [ ] Confirm realistic test data

## Phase 2: ChaCha12 Baseline Benchmarks

### Measure Encryption Performance
- [ ] Benchmark single packet encryption (ChaCha12)
- [ ] Measure latency (microseconds per operation)
- [ ] Measure throughput (packets per second)
- [ ] Test with various packet sizes
- [ ] Run 1000+ iterations for statistical accuracy
- [ ] Calculate mean, min, max, std dev

### Measure Decryption Performance
- [ ] Benchmark single packet decryption (ChaCha12)
- [ ] Measure latency (microseconds per operation)
- [ ] Measure throughput (packets per second)
- [ ] Test with various packet sizes
- [ ] Run 1000+ iterations for statistical accuracy
- [ ] Calculate mean, min, max, std dev

### Measure System Impact
- [ ] Measure CPU usage during encryption
- [ ] Measure CPU usage during decryption
- [ ] Test at typical packet rates (e.g., 500 Hz)
- [ ] Test at maximum packet rates
- [ ] Measure end-to-end latency
- [ ] Measure jitter

### Document Baseline
- [ ] Record all ChaCha12 metrics
- [ ] Create performance report
- [ ] Note any observations
- [ ] Save raw data for comparison

## Phase 3: ChaCha20 Benchmarks

### Implement ChaCha20 Variant
- [ ] Modify code to use ChaCha20 (20 rounds)
  - Location: `rx_main.cpp:506`
  - Location: `tx_main.cpp:36, 305`
- [ ] Change `uint8_t rounds = 12;` to `rounds = 20;`
- [ ] Change `ChaCha cipher(12);` to `ChaCha cipher(20);`
- [ ] Verify code compiles
- [ ] Test basic functionality

### Measure Encryption Performance
- [ ] Benchmark single packet encryption (ChaCha20)
- [ ] Measure latency (microseconds per operation)
- [ ] Measure throughput (packets per second)
- [ ] Test with various packet sizes (same as ChaCha12 tests)
- [ ] Run 1000+ iterations for statistical accuracy
- [ ] Calculate mean, min, max, std dev

### Measure Decryption Performance
- [ ] Benchmark single packet decryption (ChaCha20)
- [ ] Measure latency (microseconds per operation)
- [ ] Measure throughput (packets per second)
- [ ] Test with various packet sizes (same as ChaCha12 tests)
- [ ] Run 1000+ iterations for statistical accuracy
- [ ] Calculate mean, min, max, std dev

### Measure System Impact
- [ ] Measure CPU usage during encryption
- [ ] Measure CPU usage during decryption
- [ ] Test at typical packet rates (e.g., 500 Hz)
- [ ] Test at maximum packet rates
- [ ] Measure end-to-end latency
- [ ] Measure jitter

### Document ChaCha20 Metrics
- [ ] Record all ChaCha20 metrics
- [ ] Create performance report
- [ ] Note any observations
- [ ] Save raw data for comparison

## Phase 4: Analysis and Comparison

### Calculate Performance Differences
- [ ] Compare encryption latency (ChaCha20 vs ChaCha12)
- [ ] Calculate percentage difference
- [ ] Compare decryption latency
- [ ] Calculate percentage difference
- [ ] Compare throughput
- [ ] Compare CPU usage
- [ ] Compare end-to-end latency

### Assess RC Link Impact
- [ ] Determine if latency increase is acceptable
- [ ] Check if maximum packet rate is affected
- [ ] Assess impact on link reliability
- [ ] Consider impact on user experience
- [ ] Evaluate against decision criteria

### Create Comparison Report
- [ ] Build comparison table (ChaCha12 vs ChaCha20)
- [ ] Include all metrics
- [ ] Highlight significant differences
- [ ] Add graphs/visualizations if helpful
- [ ] Note test conditions and platform

## Phase 5: Decision Making

### Apply Decision Criteria
- [ ] Latency increase < 10%?
  - If YES → Recommend ChaCha20
- [ ] Latency increase 10-25%?
  - If YES → Consult stakeholder
- [ ] Latency increase > 25%?
  - If YES → Recommend staying with ChaCha12

### Security Assessment
- [ ] Research ChaCha12 security status
- [ ] Review any known attacks or weaknesses
- [ ] Assess adequacy for RC telemetry threat model
- [ ] Compare security margin ChaCha12 vs ChaCha20
- [ ] Document security considerations

### Make Recommendation
- [ ] Prepare recommendation based on data
- [ ] Include performance analysis
- [ ] Include security analysis
- [ ] Note trade-offs
- [ ] Present to Manager (or stakeholder if needed)

## Phase 6: Implementation

### If Decision: Upgrade to ChaCha20
- [ ] Update all instances to use 20 rounds
- [ ] Test encryption/decryption functionality
- [ ] Run integration tests
- [ ] Verify no regressions
- [ ] Update documentation
- [ ] Update comments in code
- [ ] Remove ChaCha12 references

### If Decision: Stay with ChaCha12
- [ ] Document rationale for staying with ChaCha12
- [ ] Include benchmark data as justification
- [ ] Document security assessment
- [ ] Add code comment explaining choice
- [ ] Update any relevant documentation
- [ ] No code changes needed

### Testing
- [ ] Test chosen configuration thoroughly
- [ ] Run full regression test suite
- [ ] Test on all target platforms
- [ ] Verify performance meets requirements
- [ ] Verify security is adequate

## Phase 7: Documentation

### Document Benchmark Results
- [ ] Create detailed benchmark report
- [ ] Include methodology
- [ ] Include raw data
- [ ] Include analysis
- [ ] Include decision rationale

### Update Code Documentation
- [ ] Add comments explaining round choice
- [ ] Reference benchmark results
- [ ] Note security considerations
- [ ] Update any technical docs

### Create Decision Record
- [ ] Document final decision
- [ ] Include supporting data
- [ ] Note who made decision and when
- [ ] Reference benchmark report
- [ ] Store in project files

## Phase 8: Completion

### Final Validation
- [ ] Verify decision implemented correctly
- [ ] Run complete test suite
- [ ] Verify all success criteria met
- [ ] Review all documentation

### Reporting
- [ ] Create completion report
- [ ] Include benchmark results summary
- [ ] Include decision and rationale
- [ ] Include any recommendations
- [ ] Send report to Manager

### Cleanup
- [ ] Archive task assignment from inbox
- [ ] Clean up benchmark code (or keep for future use)
- [ ] Commit code changes (if applicable to role)
- [ ] Update project status to COMPLETED

## Notes

**Critical Success Factors:**
- Accurate benchmarks on realistic scenarios
- Representative test data
- Statistical rigor (enough iterations)
- Data-driven decision

**Watch Out For:**
- Benchmark overhead affecting results
- Non-representative test scenarios
- Platform-specific performance variations
- Optimization flags affecting results

**Benchmark Best Practices:**
- Run warm-up iterations before measuring
- Use representative packet sizes
- Test under realistic conditions
- Repeat for statistical validity
- Minimize measurement overhead

**Questions to Resolve:**
- What is the typical packet rate for this RC link?
- What is the maximum acceptable latency?
- What MCU/platform is primary target?
- Are there multiple platforms with different performance?

**Decision Criteria Reference:**
- < 10% increase → Upgrade to ChaCha20
- 10-25% increase → Stakeholder decision
- > 25% increase → Stay with ChaCha12

**Security Context:**
- ChaCha20: IETF standard (RFC 8439), extensively analyzed
- ChaCha12: Less analyzed but no known practical attacks
- RC telemetry: May not need full ChaCha20 security margin
- Performance critical: Low latency essential for RC control
