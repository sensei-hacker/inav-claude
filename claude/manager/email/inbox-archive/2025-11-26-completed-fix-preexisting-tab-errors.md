# Task Completed: Fix Pre-existing Tab Errors

## Status: COMPLETED

## Summary

Fixed two JavaScript errors that were present in the INAV Configurator tabs.

## Issue 1: ports.js - `checkMSPPortCount is not defined`

**Root Cause**: The functions `checkMSPPortCount()` and `showMSPWarning()` were lost during merge conflict resolution in commits 8ccf4f83 and 895c526c. The functions were originally added in commit 92ee3431.

**Fix**: Restored both functions to `tabs/ports.js`.

**PR**: https://github.com/iNavFlight/inav-configurator/pull/2436

## Issue 2: magnetometer.js - `modelUrl is not defined` and model not loading

**Root Cause**: Dynamic import at line 740 destructures as `{default: model}` but the code was using an undefined variable `modelUrl`. Additionally, `model.add()` calls at lines 762 and 777 were incorrect because `model` is the URL string, not the THREE.js scene object.

**Fix**:
- Changed `loader.load(modelUrl, ...)` to `loader.load(model, ...)`
- Changed `model.add(gps)` to `modelScene.add(gps)`
- Changed `model.add(fc)` to `modelScene.add(fc)`

**Verification**: User confirmed the 3D model did not load before the fix, and loads correctly after.

**PR**: https://github.com/iNavFlight/inav-configurator/pull/2437

## Files Modified

- `tabs/ports.js` - Restored lost functions
- `tabs/magnetometer.js` - Fixed variable references

## Related

The "Fix preload.mjs forEach Error" task was paused earlier - see separate report. The bugs found in connection classes (addOnReceiveCallback pushing to wrong array) remain unfixed but may not be related to the original reported error.
