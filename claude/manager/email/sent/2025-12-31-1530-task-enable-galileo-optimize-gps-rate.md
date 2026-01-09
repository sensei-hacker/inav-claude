# Task Assignment: Enable Galileo by Default and Optimize GPS Update Rate

**Date:** 2025-12-31 15:30
**Project:** enable-galileo-optimize-gps-rate
**Priority:** MEDIUM
**Estimated Effort:** 2-3 hours
**Type:** Feature / Optimization

## Task

Implement the top recommendations from the u-blox GPS configuration analysis:

1. **Enable Galileo by default** on M8+ GPS receivers
2. **Optimize GPS update rate** - consider lowering from 10Hz to 8Hz based on Jetrell's testing

## Background

The u-blox GPS configuration analysis (`claude/developer/reports/ublox-gps-inav-vs-ardupilot.md`) identified clear opportunities for improvement. The comparison with ArduPilot and research into GNSS constellations shows:

**Galileo Benefits:**
- Equal or better accuracy than GPS
- No downsides to enabling it
- Modern receivers (M8+) have been Galileo-capable since 2016
- More satellites = better HDOP and faster TTFF
- Research shows clear positioning benefits

**GPS Update Rate:**
- Current INAV default: 10Hz
- ArduPilot uses: 5Hz (noted M9N performance issues above 5Hz)
- **Jetrell's testing suggests 8Hz may be optimal balance**
- Need to investigate the testing results and validate

## Objectives

### 1. Enable Galileo by Default (Clear Win)

**Change:**
```c
// Current default
#define SETTING_GPS_UBLOX_USE_GALILEO_DEFAULT OFF

// New default
#define SETTING_GPS_UBLOX_USE_GALILEO_DEFAULT ON
```

**Location:** `inav/src/main/fc/settings.yaml` around line 1730-1786 (GPS settings)

**Impact:**
- All users with M8+ GPS will automatically get Galileo satellites
- Typically +8 Galileo satellites visible
- Better HDOP (dilution of precision)
- Faster time-to-first-fix
- Improved accuracy, especially in interference/multipath environments

**Backward Compatibility:**
- Users can still disable via CLI: `set gps_ublox_use_galileo = OFF`
- No breaking change, just better default

---

### 2. Investigate and Optimize GPS Update Rate

**Current State:**
- INAV: 10Hz on M7+
- ArduPilot: 5Hz (conservative, documented M9N issues)
- **Jetrell's testing: Suggests 8Hz may be optimal**

**Research Needed:**

1. **Find Jetrell's Testing Results:**
   - Search for Jetrell's posts/comments about GPS update rate
   - Likely in INAV Discord, GitHub issues, or RC Groups
   - Document specific findings (performance metrics, hardware tested)

2. **Understand the Trade-offs:**
   - Why is 8Hz better than 10Hz?
   - Is this specific to certain GPS modules (M8, M9, M10)?
   - What metrics improved? (accuracy, CPU usage, reliability)

3. **Implementation Options:**

   **Option A: Change default to 8Hz for all M7+**
   ```c
   // In gps_ublox.c
   if (gpsState.hwVersion >= UBX_HW_VERSION_UBLOX7) {
       configureRATE(hz2rate(8));  // Was 10Hz, now 8Hz
   }
   ```

   **Option B: Hardware-specific rates**
   ```c
   if (gpsState.hwVersion >= UBX_HW_VERSION_UBLOX10) {
       configureRATE(hz2rate(10));  // M10 can handle 10Hz
   } else if (gpsState.hwVersion >= UBX_HW_VERSION_UBLOX7) {
       configureRATE(hz2rate(8));   // M7/M8/M9 at 8Hz
   } else {
       configureRATE(hz2rate(5));   // M6 at 5Hz
   }
   ```

   **Option C: Keep 10Hz but make it easier to configure**
   - Keep current default
   - Improve documentation about when to use 8Hz
   - Make it a preset in Configurator

**Decision Criteria:**
- Does Jetrell's testing show clear benefit of 8Hz over 10Hz?
- Is the benefit hardware-specific or universal?
- What does the community use?
- Any downsides to reducing from 10Hz?

---

## Implementation Steps

### Phase 1: Research (30 minutes)

1. **Find Jetrell's Testing:**
   - Search INAV GitHub issues for "jetrell gps" or "gps rate" or "8hz"
   - Search Discord history if accessible
   - Check RC Groups INAV thread
   - Document findings in project notes

2. **Review Current Code:**
   - Read `inav/src/main/io/gps_ublox.c` GPS rate configuration
   - Understand how `gps_ublox_nav_hz` setting works
   - Note any existing comments about rate selection

### Phase 2: Enable Galileo (45 minutes)

1. **Modify Default Setting:**
   - Edit `inav/src/main/fc/settings.yaml`
   - Change `gps_ublox_use_galileo` default from OFF to ON
   - Update description if needed to mention it's enabled by default

2. **Test Build:**
   - Build a test target: `./build.sh MATEKF405`
   - Verify it compiles successfully
   - Check generated defaults

3. **Documentation:**
   - Update `docs/Gps.md` or relevant GPS documentation
   - Note that Galileo is now enabled by default on M8+
   - Explain benefits and how to disable if needed

### Phase 3: GPS Update Rate Decision (45-60 minutes)

**Based on research findings, choose one path:**

#### Path A: Change Default to 8Hz
1. Modify `gps_ublox.c` rate configuration
2. Test build
3. Document the change and rationale
4. Note: This is a behavior change users might notice

#### Path B: Keep 10Hz, Document 8Hz Option
1. Keep current code
2. Improve documentation about rate selection
3. Explain when users might want to use 8Hz
4. Add to Configurator presets if applicable

#### Path C: Hardware-Specific Rates
1. Implement conditional logic based on GPS hardware version
2. Test build
3. Document different rates for different hardware
4. More complex but potentially optimal

**Make this decision based on evidence from Jetrell's testing.**

### Phase 4: Testing (30 minutes)

1. **Build Test:**
   - Build at least 2 targets to verify compilation
   - Check that defaults are correctly set

2. **Hardware Test (if available):**
   - Flash to a board with M8+ GPS
   - Verify Galileo is enabled automatically
   - Check satellite count increases
   - Verify GPS rate setting

3. **Documentation Test:**
   - Verify CLI help text is accurate
   - Check that documentation reflects changes

### Phase 5: Create Pull Request

1. **Commit Message:**
   ```
   GPS: Enable Galileo by default on M8+ receivers, optimize update rate

   - Enable Galileo by default for improved accuracy and TTFF
   - [Describe GPS rate change if made]
   - Based on u-blox GPS configuration analysis
   - Users can still disable Galileo via CLI if needed

   Rationale:
   - Galileo provides equal/better accuracy than GPS
   - More satellites improve HDOP and fix reliability
   - Modern GPS receivers (M8+) have supported Galileo since 2016
   - No downsides to enabling by default
   [- GPS rate: Jetrell's testing shows 8Hz optimal for M8/M9]
   ```

2. **PR Description:**
   - Reference the analysis document
   - Cite Jetrell's testing results
   - Explain benefits
   - Note backward compatibility
   - Request testing from users with various GPS hardware

---

## Key Questions to Answer

Before finalizing the GPS rate change:

1. **What exactly did Jetrell test?**
   - Which GPS modules? (M8, M9, M10?)
   - What metrics? (position accuracy, CPU usage, reliability?)
   - What were the results at 5Hz, 8Hz, 10Hz?

2. **Is 8Hz better than 10Hz universally or hardware-specific?**
   - If hardware-specific, implement conditional logic
   - If universal, change default for all

3. **What is the community consensus?**
   - Do experienced users run 8Hz or 10Hz?
   - Any known issues with 10Hz?

4. **What does u-blox documentation say?**
   - Are there official recommendations about update rates?
   - Any warnings about specific rates on specific hardware?

---

## Files to Modify

### Definitely:
- `inav/src/main/fc/settings.yaml` - Change Galileo default to ON
- `docs/Gps.md` (or equivalent) - Document changes

### Potentially:
- `inav/src/main/io/gps_ublox.c` - Update default GPS rate if evidence supports it
- `inav-configurator/` - Update any GPS configuration UI if needed

---

## Testing Requirements

### Minimum Testing:
- ✅ Compiles successfully
- ✅ Defaults are correct (Galileo ON)
- ✅ CLI parameter still works to disable Galileo
- ✅ GPS rate setting is applied correctly

### Ideal Testing:
- Test with real M8+ GPS hardware
- Verify increased satellite count
- Verify GPS performance
- Test on multiple GPS models (M8, M9, M10 if available)
- Verify no regression in fix time or accuracy

---

## Expected Deliverables

1. **Code Changes:**
   - Modified settings.yaml with Galileo enabled by default
   - GPS rate optimization if evidence supports it
   - Documentation updates

2. **Pull Request:**
   - Clear description of changes
   - Rationale based on analysis
   - Reference to Jetrell's testing
   - Request for community testing

3. **Project Documentation:**
   - Update project notes with findings
   - Document Jetrell's testing results
   - Explain decision on GPS rate

4. **Completion Report:**
   - Email to manager with summary
   - Include any decisions made
   - Note any follow-up needed

---

## Success Criteria

- [ ] Galileo enabled by default on M8+ receivers
- [ ] Jetrell's testing findings documented
- [ ] GPS rate decision made with clear rationale
- [ ] Code compiles successfully
- [ ] Documentation updated
- [ ] Pull request created
- [ ] Changes tested (at minimum build test, ideally hardware test)

---

## Notes

### Galileo is a Clear Win
This is well-supported by research and the analysis document. No controversy here.

### GPS Rate Needs Investigation
The 8Hz suggestion from Jetrell needs to be researched. Don't blindly change it - understand WHY 8Hz might be better than 10Hz.

**Possible reasons 8Hz might be better:**
- Lower CPU overhead
- Better GPS module performance (some modules struggle at 10Hz)
- Lower UART bandwidth
- Better timing alignment with flight controller loop

**Possible reasons to keep 10Hz:**
- Lower latency (100ms vs 125ms)
- More data points for navigation
- Works fine on modern hardware

**Find the evidence, then decide.**

### Backward Compatibility
Both changes maintain backward compatibility:
- Galileo can still be disabled via CLI
- GPS rate is still user-configurable

### Community Testing
Request testing from users with different GPS hardware in the PR.

---

## References

- Analysis document: `claude/developer/reports/ublox-gps-inav-vs-ardupilot.md`
- INAV GPS code: `inav/src/main/io/gps_ublox.c`
- GPS settings: `inav/src/main/fc/settings.yaml:1730-1786`
- Jetrell's testing: [To be found and documented]

---

**Manager**
