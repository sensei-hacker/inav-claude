# Task Assignment: Investigate PR #11025 Telemetry Corruption

**Date:** 2025-12-16 19:00
**Project:** investigate-pr11025-telemetry-corruption
**Priority:** HIGH
**Estimated Effort:** 4-6 hours
**Branch:** Investigation only (no code changes)

## Task

Investigate why PR #11025 (adding airspeed, RPM, and temperature telemetry) caused existing telemetry to stop working, leading to its immediate revert via PR #11139.

## Background

You previously analyzed PR #11025 and #11100 for CRSF telemetry enhancements and created comprehensive test infrastructure. Now we need to understand why PR #11025 failed in production.

**Timeline:**
- **November 28, 2025:** PR #11025 merged (added airspeed, RPM, temperature frames)
- **Same day:** Users reported losing "all esc telemetry sensors as well as alt and vspeed"
- **Same day:** PR #11139 reverted all changes

**Key Clue:**
- Code reviewer warned about "invalid frame emission when no payload data existed"
- This suggests empty or malformed frames corrupted the telemetry stream
- Other telemetry (altitude, vspeed, ESC sensors) stopped working

## What to Do

### 1. Review the PRs

**PR #11025 (original implementation):**
- https://github.com/iNavFlight/inav/pull/11025
- Focus on `src/main/telemetry/crsf.c` and `src/main/rx/crsf.h` changes
- What frame generation functions were added?
- How were frames scheduled in the telemetry cycle?

**PR #11139 (revert):**
- https://github.com/iNavFlight/inav/pull/11139
- Read comments for technical details
- Look for user bug reports

### 2. Analyze the Code (Root Cause Investigation)

**Compare with working telemetry frames:**
- How do GPS, Battery, and Attitude frames check sensor availability?
- What happens when sensors are missing in working code?
- Look for patterns like:
  ```c
  if (!sensors(SENSOR_GPS)) {
      return;  // Don't send frame if sensor unavailable
  }
  ```

**Examine PR #11025 frame implementations:**
- **Airspeed (0x0A):** Does it check `pitotIsHealthy()` before sending?
- **RPM (0x0C):** Does it check ESC telemetry availability?
- **Temperature (0x0D):** Does it check temperature sensor availability?
- **Critical question:** What happens if sensors are NOT available?
  - Does it send empty frames?
  - Does it send frames with garbage data?
  - Does it skip the frame entirely?

**Check frame scheduling:**
- How are frames added to the telemetry schedule?
- Are new frames scheduled unconditionally?
- Should scheduling be conditional on sensor availability?

### 3. Identify the Specific Bug

**Possible failure modes:**
1. **Missing sensor check:** Frames sent even when sensors unavailable
2. **Empty frame emission:** Zero-length or malformed frames sent
3. **Incorrect frame length:** Length field doesn't match payload
4. **Bad CRC calculation:** Invalid CRC for empty/missing data
5. **Scheduling bug:** Frames scheduled incorrectly, breaking timing

**Understand corruption mechanism:**
- How do invalid frames corrupt the CRSF protocol stream?
- Why would receiver lose sync?
- Why would OTHER telemetry (alt, vspeed) stop working?

### 4. Compare with PR #11100

**Why didn't PR #11100 get reverted?**
- Check if it properly validates sensor availability
- Look for patterns to follow in a fix
- Does it use conditional scheduling?

Example from your test plan: PR #11100 adds frame 0x09 (baro/vario)
- Does it check `sensors(SENSOR_BARO)` before sending?
- How does it handle missing barometer?

### 5. Use Your Test Tools

**You have extensive CRSF infrastructure:**
- `claude/test_tools/inav/crsf/test_crsf_frames.py`
- `claude/test_tools/inav/crsf/crsf_rc_sender.py`
- Frame validation and parsing tools

**Consider:**
- Can you reproduce the issue by building PR #11025 branch?
- Can you test with sensors disabled to see frame behavior?
- Can you capture the corrupted telemetry stream?

### 6. Document Your Findings

**Create investigation report:**
- Root cause (specific code location and issue)
- Why it corrupted the telemetry stream
- Why other telemetry stopped working
- Recommended fix strategy
- Code pattern to follow for correct implementation

## Success Criteria

- [ ] Root cause identified and documented
- [ ] Specific code issue pinpointed (file, line, function)
- [ ] Failure mechanism explained (how invalid frames corrupt stream)
- [ ] Fix strategy recommended with code examples
- [ ] Report sent to manager

## Files to Check

**INAV Firmware:**
- `src/main/telemetry/crsf.c` - Telemetry implementation
- `src/main/rx/crsf.h` - Frame type definitions
- Compare with:
  - GPS frame implementation (working reference)
  - Battery frame implementation (working reference)
  - Attitude frame implementation (working reference)

**Your Documentation:**
- `claude/developer/crsf-telemetry-test-plan.md` - Your comprehensive test plan
- `claude/developer/crsf-telemetry-msp-config-guide.md` - MSP configuration
- `claude/developer/crsf-telemetry-bidirectional-complete.md` - Testing tools

**Your Test Tools:**
- `claude/test_tools/inav/crsf/test_crsf_frames.py`
- `claude/test_tools/inav/crsf/crsf_rc_sender.py`
- `claude/test_tools/inav/crsf/crsf_stream_parser.py`

## Notes

**You are well-positioned for this task:**
- You created comprehensive CRSF telemetry test infrastructure
- You identified the airspeed duplication issue between PRs
- You have working test tools and documentation
- You understand CRSF protocol structure

**Focus areas:**
1. **Sensor availability checks** - This is likely the root cause
2. **Frame scheduling** - When/how frames are added to telemetry cycle
3. **Empty frame handling** - What happens with no sensor data
4. **Protocol corruption** - How invalid frames break the stream

**Investigation approach:**
- Start by comparing working frames (GPS, Battery) with PR #11025 frames
- Look for missing validation that working frames have
- Test your hypothesis if possible using your CRSF test tools
- Document findings clearly for future re-implementation

**Output:**
- Create report in `claude/developer/outbox/pr11025-root-cause-analysis.md`
- Include code snippets showing the bug
- Provide recommended fix with code examples
- Explain why the fix will work

---
**Manager**
