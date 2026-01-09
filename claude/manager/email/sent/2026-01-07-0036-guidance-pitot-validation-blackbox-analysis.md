# Guidance: Additional Analysis for Pitot Sensor Validation Task

**Date:** 2026-01-07 00:36
**Regarding:** implement-pitot-sensor-validation task
**Priority:** HIGH

## Additional Work Required

Before implementing the pitot sensor validation feature, you need to analyze a real-world blackbox log where pitot failure apparently was **not detected**. This will help inform the validation algorithm design.

## Task

1. **Download files from PR #11222 comment:**
   - Go to: https://github.com/iNavFlight/inav/pull/11222
   - Find the comment by **quadlawnmowerman-coder**
   - Download these attachments from the comment:
     - The diff file
     - The blackbox log: `LOG00002.TXT`

2. **Decode the blackbox log:**
   - Use `blackbox_decode` (you have this tool - see `/replay-blackbox` skill)
   - Extract airspeed-related fields:
     - Pitot airspeed readings
     - GPS groundspeed
     - Wind estimates (if logged)
     - Any pitot status flags

3. **Analyze the data:**
   - Identify the time period where pitot failure occurred
   - Compare pitot airspeed vs GPS groundspeed during failure
   - Determine why the failure was not detected
   - Look for patterns that could be used for detection

4. **Replay/simulate if possible:**
   - Use the blackbox replay tools to feed the sensor data through validation logic
   - Test proposed detection algorithms against this real data
   - Document false positive/negative rates

## Expected Deliverables

1. **Analysis report** documenting:
   - Timeline of the pitot failure in the log
   - Comparison of pitot vs GPS data during failure
   - Why current code failed to detect it
   - Recommended detection thresholds based on real data

2. **Validation algorithm refinement:**
   - Update the proposed algorithm in `summary.md` if needed
   - Include specific thresholds derived from this log

## Relevant Skills/Tools

- `/replay-blackbox` - Replay blackbox sensor data
- `blackbox_decode` tool at `~/Documents/planes/inavflight/blackbox-tools/obj/blackbox_decode`
- See `claude/developer/README.md` for blackbox analysis workflows

## Why This Matters

Real-world failure data is invaluable for designing robust detection. The log from quadlawnmowerman-coder represents an actual pitot failure that went undetected - understanding **why** it wasn't caught will directly inform the validation thresholds and algorithm.

## Notes

- The diff in the PR comment may show quadlawnmowerman-coder's attempt at fixing this - review it for insights
- Save the downloaded files to `claude/developer/investigations/` or the project directory
- This analysis should be done **before** writing implementation code

---
**Manager**
