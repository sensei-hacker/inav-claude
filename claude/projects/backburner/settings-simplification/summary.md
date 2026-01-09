# Project: Settings Simplification

**Status:** ⏸️ BACKBURNER
**Priority:** MEDIUM
**Type:** Feature / UX Improvement
**Created:** 2026-01-07
**Estimated Effort:** 7-8 weeks (phased)

## Overview

Reduce INAV configuration complexity by ~70% through automatic determination and consolidation of flight settings. Analysis identified 48 settings that can be eliminated or dramatically simplified.

## Problem

New users face overwhelming configuration complexity:
- Configure 4 battery voltages (what values?)
- Manually tune hover throttle (trial and error)
- Set up 4 landing descent parameters (confusing)
- Configure dozens of navigation settings
- **Current experience:** 2-3 hours, ~60% success rate

## Solution

Two complementary approaches:

### 1. Auto-Determinable Settings (19 identified)
Settings that can be learned from flight data, physical constants, or calculated:
- **Already implemented:** 4 examples (mag declination, gyro cal, etc.)
- **New opportunities:** 15 settings

**Top candidates:**
- Adaptive hover throttle (learn during ALTHOLD)
- Adaptive cruise throttle/speed (learn during cruise)
- Battery chemistry presets (known constants)
- Auto-link reference airspeed to cruise speed

### 2. Consolidated Settings (47 → 12-14 primary)
Master settings with calculated derivatives:
- Battery voltages: 4 settings → 1 chemistry dropdown
- Landing descent: 4 settings → 1 profile selector
- FW throttle range: 4 settings → cruise + margin

## Expected Impact

**After implementation:**
- Battery chemistry: [LiPo ▼]
- Cell count: [4]
- Fly ALTHOLD once (learns hover throttle)
- Most other settings auto-configured
- **New experience:** ~15 minutes, ~95% success rate

## Implementation Phases

### Phase 1: Quick Wins (~3 days)
- Battery chemistry presets
- Auto-link reference airspeed to cruise speed

### Phase 2: Learning Features (~3 weeks)
- Adaptive hover throttle
- Adaptive cruise throttle/speed

### Phase 3: Profile Systems (~2 weeks)
- Landing descent profiles
- Throttle range consolidation

### Phase 4: Advanced Consolidations (~2 weeks)
- Remaining consolidation opportunities

## Analysis Documentation

All analysis stored in `claude/developer/investigations/inav-flight-settings/`:
- **MASTER-SUMMARY.md** - Executive summary with roadmap
- **consolidated-settings-analysis.md** - Detailed consolidation analysis
- **auto-determinable-settings-analysis.md** - Auto-determination analysis
- **CONSOLIDATED-QUICK-SUMMARY.md** - Quick reference
- **QUICK-SUMMARY.md** - Quick reference for auto settings

## Value

- **70% reduction** in required configuration
- **Fewer support issues** from misconfiguration
- **Better new user experience**
- **Reduced barrier to entry**

## Why Backburner

- Not urgent (existing system works)
- Significant development effort (7-8 weeks)
- High long-term value but lower immediate priority
- Other safety-critical work takes precedence

## Notes

- Analysis complete and thorough
- Ready to activate when bandwidth allows
- Consider Phase 1 quick wins for earlier release
