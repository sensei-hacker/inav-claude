# Task Assignment: Profile OSD Page MSP Loading Performance

**Date:** 2025-12-07 16:10
**Priority:** MEDIUM
**Estimated Effort:** 2-4 hours
**Type:** Performance Analysis / Optimization Research

## Task

Profile which MSP message types consume the most time when loading the OSD tab in INAV Configurator. Identify optimization opportunities, such as retrieving only enabled logic conditions instead of all slots.

## Background

When users open the OSD tab in the Configurator, multiple MSP requests are made to retrieve configuration data from the flight controller. Some of these requests may be inefficient - for example, fetching all 64 logic condition slots when only a few are actually in use.

**Goal:** Identify the slowest MSP operations and propose optimizations to improve OSD page load time.

## What to Do

### 1. Set Up Profiling Environment

**Option A: Browser DevTools**
```bash
# Run configurator in dev mode
cd inav-configurator
npm start
```
- Open Chrome DevTools → Network tab
- Filter by WebSocket or relevant connection type
- Enable timing information

**Option B: Add Instrumentation**
- Add timing logs to MSP request/response handlers
- Log message type, payload size, and round-trip time

**Option C: Use MSP Debug Tools**
```bash
cd claude/test_tools/inav/msp/debug/
# Use existing MSP debug tools to monitor traffic
```

### 2. Profile OSD Tab Loading

**Steps:**
1. Connect Configurator to SITL (or real FC)
2. Start profiling/timing capture
3. Navigate to OSD tab
4. Wait for full load
5. Stop profiling
6. Analyze captured data

**Capture for each MSP message:**
- Message code (e.g., MSP_LOGIC_CONDITIONS)
- Request timestamp
- Response timestamp
- Round-trip time (RTT)
- Payload size (bytes)
- Number of calls

### 3. Identify Slow Operations

**Create a table like:**

| MSP Code | Name | Calls | Avg RTT | Total Time | Payload Size |
|----------|------|-------|---------|------------|--------------|
| 180 | MSP_LOGIC_CONDITIONS | 64 | 5ms | 320ms | 1024 bytes |
| ... | ... | ... | ... | ... | ... |

**Sort by:**
1. Total time (calls × avg RTT)
2. Payload size
3. Number of redundant calls

### 4. Analyze Logic Conditions Specifically

**Current behavior (suspected):**
- Fetches all 64 logic condition slots
- Each slot requires separate MSP request
- Most slots are likely empty/disabled

**Check the code:**
```bash
# Find logic condition loading code
cd inav-configurator
grep -r "LOGIC_CONDITION" js/ tabs/
grep -r "MSP_LOGIC" js/
```

**Questions to answer:**
1. How many MSP calls for logic conditions?
2. Are empty slots being fetched?
3. Is there a way to query "which slots are enabled"?
4. Could we use a bulk fetch instead of individual requests?

### 5. Research Optimization Options

**Option A: Fetch Only Enabled Slots**
- Does firmware support querying which slots are active?
- Could add new MSP command: `MSP_LOGIC_CONDITIONS_ACTIVE_MASK`
- Configurator fetches mask first, then only enabled slots

**Option B: Bulk Fetch**
- Single MSP request returns all logic conditions
- Trade-off: Larger single payload vs many small requests
- May be faster over serial, similar over TCP

**Option C: Lazy Loading**
- Load visible/expanded items first
- Fetch remaining in background
- User sees faster initial load

**Option D: Caching**
- Cache logic conditions after first fetch
- Only re-fetch on explicit refresh
- Risk: Stale data if FC modified externally

### 6. Check Other Slow Operations

Beyond logic conditions, also profile:
- Programming PID data
- Global functions
- OSD element positions
- Font loading
- Any other repeated MSP calls

### 7. Propose Solutions

For each slow operation identified:
1. Describe current behavior
2. Measure current performance
3. Propose optimization
4. Estimate improvement
5. Note implementation complexity (firmware change needed? configurator only?)

## Deliverables

### Performance Report

Send report to Manager with:

**Filename:** `claude/developer/sent/2025-12-07-HHMM-osd-msp-profiling-results.md`

**Include:**
1. **Profiling methodology** - How you measured
2. **Results table** - All MSP messages, sorted by total time
3. **Top 5 slowest operations** - Detailed analysis of each
4. **Logic conditions analysis** - Specific findings
5. **Optimization proposals** - Ranked by impact/effort ratio
6. **Recommendations** - What should we pursue?

## Success Criteria

- [ ] Profiled OSD tab loading with timing data
- [ ] Identified top 5 slowest MSP operations
- [ ] Analyzed logic conditions loading specifically
- [ ] Researched optimization options
- [ ] Proposed at least 2-3 concrete optimizations
- [ ] Estimated performance improvement for each
- [ ] Noted implementation requirements (firmware/configurator)
- [ ] Sent comprehensive report to Manager

## Notes

### Focus Areas

**Primary:** Logic conditions (user specifically mentioned this)
**Secondary:** Any other operations taking >100ms total

### Don't Implement Yet

This is a **research and profiling** task. Don't implement optimizations yet - just identify and propose them. We'll prioritize and assign implementation separately.

### Consider Both Sides

Some optimizations require:
- **Configurator only** - Easier, no firmware changes
- **Firmware + Configurator** - More complex, but potentially bigger gains

Document which category each proposal falls into.

### Existing Work

Check if there are existing issues or discussions about OSD loading performance:
```bash
gh issue list --repo iNavFlight/inav-configurator --search "OSD slow" --limit 10
gh issue list --repo iNavFlight/inav-configurator --search "loading performance" --limit 10
```

---
**Manager**
