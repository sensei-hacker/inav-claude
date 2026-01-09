# Project: Document u-blox GPS Configuration

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Documentation / Analysis
**Created:** 2025-12-31
**Estimated Effort:** 4-6 hours

## Overview

Analyze and document INAV's u-blox GPS receiver configuration choices, compare with ArduPilot, and provide recommendations for improvements.

## Problem

INAV configures u-blox GPS receivers with specific settings for:
- GNSS constellations (GPS, GLONASS, Galileo, BeiDou)
- Navigation models (airborne, pedestrian, etc.)
- Update rates
- Protocol configuration
- Special features

**Questions:**
- Why were these specific choices made?
- How do they compare to ArduPilot's choices?
- Are there better alternatives?
- What trade-offs exist?

## Objectives

1. **Document INAV's configuration** with rationale from code and datasheets
2. **Analyze ArduPilot's approach** to see alternative choices
3. **Provide recommendations** based on analysis and trade-offs
4. **Create reference documentation** for future GPS work

## Scope

**In Scope:**
- INAV u-blox configuration code analysis
- u-blox datasheet references
- ArduPilot u-blox configuration analysis
- Side-by-side comparison
- Trade-off analysis
- Recommendations with rationale

**Out of Scope:**
- Implementing changes (documentation only)
- Other GPS manufacturers (Quectel, MediaTek, etc.)
- GPS hardware design
- Antenna selection

## Key Configuration Areas

1. **GNSS Constellations**
   - Which systems? GPS, GLONASS, Galileo, BeiDou
   - Channel allocation
   - Satellite tracking capacity

2. **Navigation Model**
   - Portable, Stationary, Pedestrian, Automotive, Sea, Airborne (<1g, <2g, <4g)
   - Appropriate for flight controller use?

3. **Update Rates**
   - Position update frequency
   - Measurement rates
   - Dynamic adjustments

4. **Protocol Settings**
   - NMEA vs UBX
   - Message selection
   - Output rates

5. **Special Features**
   - SBAS (WAAS/EGNOS)
   - Jamming detection
   - Power modes

## Expected Findings

**Likely differences with ArduPilot:**
- Different constellation priorities
- Different navigation models
- Different update rate strategies
- Different message configurations

**Potential recommendations:**
- Add Galileo support (if not present)
- Make navigation model configurable
- Adjust update rates for specific use cases
- Enable additional u-blox features

## Implementation Approach

1. **Code Analysis**
   - Read INAV u-blox driver code
   - Extract all configuration commands
   - Understand initialization sequence

2. **Datasheet Research**
   - Find u-blox M8/M9/M10 documentation
   - Understand each configuration option
   - Note trade-offs and alternatives

3. **ArduPilot Comparison**
   - Read ArduPilot GPS driver
   - Document their choices
   - Identify key differences

4. **Recommendations**
   - Analyze trade-offs
   - Consider INAV's use cases
   - Provide specific, actionable recommendations

## Expected Deliverables

1. **INAV Configuration Analysis**
   - `claude/developer/reports/ublox-gps-configuration-analysis.md`
   - Complete documentation of INAV's settings
   - u-blox datasheet references

2. **Comparison Document**
   - `claude/developer/reports/ublox-gps-inav-vs-ardupilot.md`
   - Side-by-side comparison
   - Trade-off analysis
   - Recommendations

3. **Completion Report**
   - Summary to manager
   - Key findings
   - Top recommendations

## Success Criteria

- [ ] All INAV u-blox settings documented
- [ ] u-blox datasheets referenced
- [ ] ArduPilot settings documented
- [ ] Key differences identified
- [ ] Trade-offs analyzed
- [ ] Recommendations provided with rationale
- [ ] Documents created in reports/
- [ ] Report sent to manager

## Value

**Benefits:**
- Better understanding of GPS configuration
- Informed decisions about future GPS improvements
- Reference for troubleshooting GPS issues
- Knowledge sharing with community

**Audience:**
- INAV developers working on GPS
- Users wanting to understand GPS settings
- Anyone comparing INAV with ArduPilot

## Priority Justification

MEDIUM priority because:
- Valuable documentation/research
- Not urgent (no active bug/issue)
- Could inform future improvements
- Moderate time investment (4-6 hours)
- Local documentation (no PR needed)

## Notes

**This is analysis/documentation work** - no code changes, no PR. Results stay in local `claude/developer/reports/` directory.

**ArduPilot as reference:**
- ArduPilot has mature GPS implementation
- Well-tested across many platforms
- Good source for comparison
- But INAV may have different requirements

**u-blox documentation is authoritative:**
- Don't guess what settings do
- Reference official datasheets
- Understand manufacturer recommendations

## Related

- GPS configuration in INAV
- u-blox M8/M9/M10 receivers
- ArduPilot GPS drivers
- GNSS technology
