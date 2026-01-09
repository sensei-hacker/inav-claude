# Project: Blackbox Viewer Axis Labels and Time Ticks

**Status:** 📋 TODO
**Priority:** Medium
**Type:** UI Enhancement
**Created:** 2026-01-07
**Repository:** inav-blackbox-log-viewer

## Overview

Enhance axis labeling in the INAV blackbox log viewer to make time scale and data magnitude more intuitive.

## Problem

The current blackbox viewer lacks clear axis labeling:
- **X-axis:** Grid lines exist at fixed 100ms intervals but have no labels, and don't scale with zoom
- **Y-axis:** Minimal labeling - multiple overlapping traces with different scales make interpretation difficult

## Objectives

### X-Axis: Enhance Existing Grid
The existing `drawGrid()` function draws vertical lines at hardcoded 100ms intervals. Enhance this to:

1. **Scale the interval based on zoom level** using powers of 10:
   - Very zoomed out: 100s or 10s intervals
   - Normal view: 1s intervals
   - Zoomed in: 100ms intervals
   - Very zoomed in: 10ms intervals

2. **Add time labels to the grid lines** (~6 labeled lines visible)

3. **Labels must update dynamically as user zooms in/out**

### Y-Axis Improvements (More Challenging)
1. Research approaches for multi-trace Y-axis labeling
2. Consider: per-trace scale indicators, color-coded ranges, hover tooltips
3. Balance information density vs. visual clutter

## Current Implementation

**Key file:** `js/grapher.js`

**Existing grid code** (`drawGrid()`, line ~618):
```javascript
// vertical lines - currently hardcoded 100ms
for(var i=(windowStartTime / 100000).toFixed(0) * 100000; i<windowEndTime; i+=100000) {
    var x = timeToCanvasX(i);
    canvasContext.moveTo(x, yScale);
    canvasContext.lineTo(x, -yScale);
}
```

This already:
- Draws vertical lines at regular intervals
- Uses `timeToCanvasX()` for positioning
- Knows about `windowStartTime` and `windowEndTime`

**What's missing:**
- Dynamic interval scaling (currently hardcoded `100000` microseconds = 100ms)
- Labels on the grid lines

## Implementation Approach

### Phase 1: Scale Grid Intervals

Replace hardcoded 100ms with zoom-responsive human-friendly intervals:

**Algorithm:**
1. Compute total visible time (`windowEndTime - windowStartTime`)
2. Divide by 8 to get "ideal" interval
3. Select nearest human-friendly interval from this list:
   - 10ms, 25ms, 100ms, 250ms
   - 1 second, 5 seconds, 10 seconds, 30 seconds
   - 1 minute, 5 minutes, 15 minutes

```javascript
const FRIENDLY_INTERVALS_MICROS = [
    10000,      // 10ms
    25000,      // 25ms
    100000,     // 100ms
    250000,     // 250ms
    1000000,    // 1 second
    5000000,    // 5 seconds
    10000000,   // 10 seconds
    30000000,   // 30 seconds
    60000000,   // 1 minute
    300000000,  // 5 minutes
    900000000,  // 15 minutes
];

function calculateGridInterval(windowWidthMicros) {
    const idealInterval = windowWidthMicros / 8;
    // Find nearest friendly interval
    return FRIENDLY_INTERVALS_MICROS.reduce((prev, curr) =>
        Math.abs(curr - idealInterval) < Math.abs(prev - idealInterval) ? curr : prev
    );
}
```

### Phase 2: Add Labels to Grid Lines

Add time labels at the bottom (or top) of grid lines:
- Format based on interval size: "0.1s", "1.5s", "2:30", etc.
- Only label major grid lines if minor lines are also drawn
- Position labels to avoid overlap

### Phase 3: Y-Axis Scale Indicators

Research and propose approach for multi-trace Y-axis (more complex due to overlapping scales).

## Success Criteria

- [ ] Grid line intervals scale with zoom level (10x steps)
- [ ] Grid lines have time labels (~6 visible)
- [ ] **Labels update correctly when zooming in/out**
- [ ] Time label format adapts to scale (ms vs s vs min:sec)
- [ ] Y-axis has improved scale visibility (approach TBD)
- [ ] No performance regression
- [ ] Visually consistent with existing UI

## Files to Modify

- `js/grapher.js` - `drawGrid()` function primarily

## Notes

Y-axis is inherently more challenging because:
- Multiple traces can have vastly different scales (e.g., gyro ±2000 vs motor 0-100%)
- Traces overlap in same vertical space
- Too much labeling creates clutter
