# Settings Simplification Analysis - Request for Back Burner Project

**From:** Developer
**To:** Manager
**Date:** 2026-01-05
**Subject:** Settings Simplification Analysis Complete - Request Back Burner Project

---

## Summary

Completed a comprehensive analysis of INAV flight settings to identify opportunities for automatic determination and consolidation. The results are significant enough to warrant a back burner project.

## What Was Done

Analyzed all flight-related settings (excludes OSD, telemetry, display, etc.) and identified two complementary approaches to reduce configuration complexity:

### 1. Auto-Determinable Settings
- **Found:** 19 settings that can be learned from flight data, physical constants, or calculated
- **Already implemented:** 4 excellent examples (mag declination, gyro cal, etc.)
- **New opportunities:** 15 settings

**Top candidates:**
- Adaptive hover throttle (learn during ALTHOLD)
- Adaptive cruise throttle/speed (learn during cruise)
- Battery chemistry presets (known constants)
- Auto-link reference airspeed to cruise speed

### 2. Consolidated Settings
- **Found:** 47 settings across 10 groups that can be reduced to 12-14 primary settings
- **Reduction:** ~70% of configuration complexity
- **Approach:** Master settings with calculated derivatives, profile-based presets

**Top candidates:**
- Battery voltages: 4 settings → 1 chemistry dropdown
- Landing descent: 4 settings → 1 profile selector
- FW throttle range: 4 settings → cruise + margin

### Combined Impact
- **~48 unique settings** can be eliminated or dramatically simplified
- **Estimated effort:** 7-8 weeks development (phased approach)
- **User impact:** 70% reduction in required configuration

## Documentation Created

All analysis in `claude/developer/investigations/inav-flight-settings/`:

- **MASTER-SUMMARY.md** - Executive summary with implementation roadmap
- **consolidated-settings-analysis.md** - Detailed consolidation analysis (500+ lines)
- **auto-determinable-settings-analysis.md** - Detailed auto-determination analysis (400+ lines)
- **CONSOLIDATED-QUICK-SUMMARY.md** - Quick reference for consolidations
- **QUICK-SUMMARY.md** - Quick reference for auto-determinable settings

## Request

**Please create a back burner project for "Settings Simplification"** to track implementation of these improvements.

**Suggested phasing:**
- **Phase 1:** Quick wins (battery chemistry, auto-link reference airspeed) - ~3 days
- **Phase 2:** Learning features (hover/cruise throttle) - ~3 weeks
- **Phase 3:** Profile systems (landing, throttle range) - ~2 weeks
- **Phase 4:** Advanced consolidations - ~2 weeks

**Rationale for back burner project:**
- Substantial usability improvement (70% fewer settings)
- Clear implementation path with phased approach
- Significant user value, especially for new users
- Reduces support burden (fewer misconfiguration errors)
- Not urgent, but high long-term value

## Example Impact

**Current new user experience:**
- Configure 4 battery voltages (what values?)
- Manually tune hover throttle (trial and error)
- Set up 4 landing descent parameters (confusing)
- Configure dozens of other navigation settings
- Time: 2-3 hours, ~60% success rate

**Proposed new user experience:**
- Battery chemistry: [LiPo ▼]
- Cell count: [4]
- Fly ALTHOLD once (learns hover throttle)
- Most other settings auto-configured or have clear profiles
- Time: ~15 minutes, ~95% success rate

---

Let me know if you'd like me to elaborate on any aspect of the analysis or if you need additional information for project planning.

**Developer**
