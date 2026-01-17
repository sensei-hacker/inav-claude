```markdown
# Task Completed: Fix Terrain Data Not Loading

**Status:** COMPLETED
**Branch:** fix/terrain-elevation-chart-esm

## Root Cause
plotElevation() commented out due to ESM compatibility

## Changes
1. Added Chart.js v4.4.1 with ESM support
2. Imported as ES module
3. Uncommented plotElevation()

## PR
#2518 - github.com/iNavFlight/inav-configurator/pull/2518
```
