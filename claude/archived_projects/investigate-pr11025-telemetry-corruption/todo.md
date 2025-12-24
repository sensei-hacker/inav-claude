# Todo List: Investigate PR #11025 Telemetry Corruption

## Phase 1: Understand the PR Changes

- [ ] Review PR #11025 code changes
  - [ ] Read the PR diff on GitHub
  - [ ] Examine `src/main/telemetry/crsf.c` changes
  - [ ] Examine `src/main/rx/crsf.h` changes
  - [ ] Note what frame generation functions were added
- [ ] Review PR #11139 (revert)
  - [ ] Read comments explaining why it was reverted
  - [ ] Note any technical details about the failure
  - [ ] Check for user bug reports

## Phase 2: Analyze the Code

- [ ] Compare new frames with working frames
  - [ ] How do GPS/Battery/Attitude check sensor availability?
  - [ ] What happens when sensors are missing in working code?
  - [ ] Look for `sensors()` or similar availability checks
- [ ] Examine PR #11025 frame implementations
  - [ ] Airspeed (0x0A): Does it check `pitotIsHealthy()`?
  - [ ] RPM (0x0C): Does it check ESC telemetry availability?
  - [ ] Temperature (0x0D): Does it check temperature sensor availability?
  - [ ] What happens if sensors are not available?
- [ ] Check frame scheduling logic
  - [ ] How are frames added to the telemetry schedule?
  - [ ] Are frames scheduled unconditionally?
  - [ ] Should scheduling be conditional on sensor availability?

## Phase 3: Identify the Bug Pattern

- [ ] Determine the specific failure mode
  - [ ] Are frames sent with no payload (empty)?
  - [ ] Are frame length calculations incorrect?
  - [ ] Are CRC calculations wrong for empty frames?
  - [ ] Is frame scheduling incorrect?
- [ ] Understand corruption mechanism
  - [ ] How do invalid frames corrupt the CRSF stream?
  - [ ] Why would other telemetry stop working?
  - [ ] Does receiver lose sync with corrupted frames?

## Phase 4: Compare with Working Implementation

- [ ] Check if PR #11100 has similar issues
  - [ ] Does it check baro sensor availability?
  - [ ] How does it handle missing sensors?
  - [ ] Why didn't PR #11100 get reverted?
- [ ] Review CRSF protocol requirements
  - [ ] What does TBS CRSF spec say about empty frames?
  - [ ] Are zero-length payloads valid?
  - [ ] How should receivers handle malformed frames?

## Phase 5: Document Findings

- [ ] Write root cause analysis
  - [ ] Specific code location of bug
  - [ ] What check was missing
  - [ ] Why it caused corruption
  - [ ] Why other telemetry stopped working
- [ ] Recommend fix strategy
  - [ ] Add sensor availability checks
  - [ ] Conditional frame scheduling
  - [ ] Example code pattern to follow
  - [ ] Testing approach for validation
- [ ] Create investigation report
  - [ ] Summary of findings
  - [ ] Code snippets showing the issue
  - [ ] Recommended fix approach
  - [ ] Next steps for re-implementation

## Completion

- [ ] Root cause documented
- [ ] Fix strategy clear
- [ ] Send report to manager
