# Task Assignment: Blackbox Viewer Axis Labels and Time Ticks

**Date:** 2026-01-07 01:50
**Project:** blackbox-viewer-axis-labels
**Priority:** Medium
**Repository:** inav-blackbox-log-viewer

## Task

Enhance the blackbox log viewer's axis labeling to make time scale more visible and intuitive.

## What to Do

### Part 1: Enhance X-Axis Grid with Scaled Intervals and Labels

The existing `drawGrid()` function in `js/grapher.js` (line ~618) already draws vertical grid lines, but they're hardcoded at 100ms intervals with no labels:

```javascript
// Current code - hardcoded 100000 microseconds (100ms)
for(var i=(windowStartTime / 100000).toFixed(0) * 100000; i<windowEndTime; i+=100000) {
    var x = timeToCanvasX(i);
    canvasContext.moveTo(x, yScale);
    canvasContext.lineTo(x, -yScale);
}
```

**Enhance this to:**

1. **Scale the interval based on zoom level** using human-friendly intervals:

   **Algorithm:**
   - Compute total visible time (`windowEndTime - windowStartTime`)
   - Divide by 8 to get "ideal" interval
   - Select nearest human-friendly interval from this list:
     - 10ms, 25ms, 100ms, 250ms
     - 1 second, 5 seconds, 10 seconds, 30 seconds
     - 1 minute, 5 minutes, 15 minutes

   This results in ~8 grid lines at intuitive time intervals.

2. **Add time labels to grid lines** (~6 labeled)
   - Position at bottom or top of grid lines
   - Format appropriately: "0.1s", "1.5s", "2:30" based on interval
   - **Labels must update when user zooms in/out**

3. **Optional: Minor grid lines**
   - Could add fainter lines between major labeled lines
   - Major lines get labels, minor lines don't

### Part 2: Y-Axis Scale Visibility (Research + Propose)

The Y-axis is more challenging because multiple traces with different scales can overlap. Research approaches and propose a solution:

**Possible approaches:**
- Per-trace scale indicators in legend
- Scale labels on left edge of each graph section
- Hover tooltips showing exact values
- Color-coded reference lines

Document your recommendation before implementing.

## Key Requirements

- **Labels must update dynamically as user zooms in/out** - The render function is called on zoom/pan, so calculate intervals fresh each time
- Use "nice number" intervals (1, 2, 5 × power of 10)
- Match existing font styling (`drawingParams.fontSizeAxisLabel`, `DEFAULT_FONT_FACE`)
- No performance regression during zoom/pan

## Files to Study

- `js/grapher.js` - Main file, especially:
  - `drawGrid()` (~line 618) - Existing grid drawing
  - `drawAxisLabel()` (~line 657) - Existing label helper
  - `timeToCanvasX()` (~line 708) - Time to X coordinate conversion
  - `windowStartTime`, `windowEndTime`, `windowWidthMicros` - Current visible range
  - `drawingParams` - Font sizes and styling

## Algorithm Hint

Human-friendly interval selection:
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

## Success Criteria

- [ ] Grid line intervals scale with zoom level (approximately 10x steps)
- [ ] Grid lines have time labels (~6 visible at any zoom)
- [ ] Labels update correctly when zooming in/out
- [ ] Time format adapts to scale (ms, s, min:sec as appropriate)
- [ ] Y-axis improvement proposed (implementation approach documented)
- [ ] Visually consistent with existing UI
- [ ] No performance issues

## Notes

- This is the INAV fork: `inav-blackbox-log-viewer` (not Betaflight's)
- Look at Betaflight's blackbox explorer for UI reference if helpful
- Project summary: `claude/projects/blackbox-viewer-axis-labels/summary.md`

---
**Manager**
