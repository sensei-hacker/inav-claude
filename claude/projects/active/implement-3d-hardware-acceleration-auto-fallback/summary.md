# Project: Implement 3D Hardware Acceleration Auto-Fallback

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Feature Enhancement / Error Handling
**Created:** 2025-12-26
**Estimated Effort:** 4-6 hours

## Overview

Implement automatic fallback when 3D hardware acceleration fails, instead of crashing or showing errors. Detect WebGL support at runtime and gracefully degrade to 2D alternatives.

## Problem

inav-configurator has a setting to disable 3D hardware acceleration, but users without GPU support (VMs, remote desktop, older systems) may encounter crashes or errors when the app tries to use WebGL without checking if it's available.

**Current Issues:**
- App probably attempts to create WebGL contexts without checking for support
- Likely crashes or shows cryptic errors when 3D fails
- Users must manually find and enable the "disable 3D" setting

## Solution

Auto-detect 3D capability and fall back gracefully when not available.

## Scope

**In Scope:**
- Investigate existing "disable 3D hardware acceleration" setting
- Add WebGL capability detection
- Implement automatic fallback when 3D unavailable
- Provide 2D alternatives where possible
- User-friendly messages explaining fallback

**Out of Scope:**
- Adding new 3D features
- Improving 3D performance on capable systems

## Implementation Steps

### Phase 1: Investigation
- Find existing "disable 3D hardware acceleration" setting
- Identify all code locations using WebGL/3D rendering
- Document what features are affected
- Common locations: magnetometer calibration 3D view, model viewers

### Phase 2: Capability Detection
- Add inline tests for WebGL context creation
- Detect both full failure and partial/degraded support
- Test before attempting to use 3D features

### Phase 3: Automatic Fallback
- Provide 2D alternatives where possible
- Show user-friendly message explaining fallback
- No crashes or cryptic errors
- Log details for debugging

### Phase 4: Testing
- Test on systems without GPU support
- Test in VMs
- Test with remote desktop
- Verify graceful degradation

## Success Criteria

- [ ] Existing 3D setting located and documented
- [ ] All 3D/WebGL usage points identified
- [ ] Capability detection implemented
- [ ] Automatic fallback working
- [ ] No crashes on systems without 3D support
- [ ] User-friendly messages displayed
- [ ] Testing completed

## Value

**Benefits:**
- Improved UX for users without GPU support
- No crashes or cryptic errors
- No manual setting changes required
- Graceful degradation
- Works in VMs and remote desktop scenarios

**Audience:**
- Users running in VMs
- Users with remote desktop
- Users with older systems without GPU support

## Priority Justification

MEDIUM priority because:
- Improves user experience for affected users
- Prevents crashes
- Non-blocking for most users
- Reasonable effort (4-6 hours)

## Related

- inav-configurator 3D settings
- WebGL support detection
- Magnetometer calibration view
- Model viewers
