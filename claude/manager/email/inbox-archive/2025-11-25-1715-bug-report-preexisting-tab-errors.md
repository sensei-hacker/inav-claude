# Bug Report: Pre-existing Tab Errors

**Date:** 2025-11-25 17:15
**Reporter:** Developer (during MSP optimization work)
**Priority:** Low (pre-existing, not blocking current work)
**Context:** Found while testing MSP profiler on optimize-tab-msp-communication branch

---

## Summary

While testing the configurator with the new MSP profiler, discovered two pre-existing JavaScript errors in tab initialization code. These are **not** related to the current MSP optimization work - they existed before any changes were made.

---

## Bugs Found

### 1. Ports Tab - Missing Function

**Location:** `tabs/ports.js:206:33`

**Error:**
```
Uncaught (in promise) ReferenceError: checkMSPPortCount is not defined
    at on_tab_loaded_handler (ports.js:206:33)
    at GUI_control.load (gui.js:284:9)
```

**Impact:**
- Ports tab loads but throws error in console
- May affect functionality in `on_tab_loaded_handler`

**Cause:** Function `checkMSPPortCount` is called but never defined

---

### 2. Magnetometer/Alignment Tab - Undefined Variable

**Location:** `tabs/magnetometer.js:742:17`

**Error:**
```
Uncaught (in promise) ReferenceError: modelUrl is not defined
    at magnetometer.js:742:17
```

**Impact:**
- Magnetometer tab loads but throws error in console
- Likely affects 3D model loading or visualization

**Cause:** Variable `modelUrl` used but never declared/assigned

---

## Recommendation

These bugs should be tracked and fixed in a separate task. They don't appear to break critical functionality but should be cleaned up for code quality.

**Suggested Priority:** Low (technical debt)
**Estimated Fix Time:** 15-30 minutes total

---

## Notes

- Both tabs still load and appear functional despite errors
- Errors were present before MSP optimization work began
- Found during Phase 1 (profiling/measurement) of MSP optimization project
- No user reports filed on these specific errors (may have been present for some time)

---

**Developer**
