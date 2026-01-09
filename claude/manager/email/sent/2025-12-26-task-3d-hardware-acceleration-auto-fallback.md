# Task Assignment: 3D Hardware Acceleration Auto-Fallback

**Date:** 2025-12-26
**Project:** inav-configurator (JavaScript/Electron)
**Priority:** Medium
**Estimated Effort:** 4-6 hours

## Task

Implement automatic fallback for 3D hardware acceleration failures in inav-configurator. Currently there's a setting to disable 3D hardware acceleration, but the app should detect when 3D support fails and automatically fall back gracefully.

## Objectives

### 1. Identify What Uses 3D Hardware Acceleration

Find all code locations that depend on 3D hardware acceleration:
- Search for WebGL/3D canvas creation
- Look for the existing "disable 3D hardware acceleration" setting
- Identify what features are affected when this setting is disabled
- Document where 3D rendering is used (e.g., 3D model viewer, magnetometer calibration?)

### 2. Implement Inline Support Tests

Add runtime capability detection:
- Test if WebGL context can be created successfully
- Test if required 3D features are available
- Detect failures early before attempting to use 3D features
- Handle both full failure (no 3D support) and partial failure (degraded support)

### 3. Implement Automatic Fallback

When 3D hardware acceleration fails:
- Automatically fall back to 2D rendering or alternative UI
- Show user-friendly message explaining the fallback
- Don't crash or show cryptic errors
- Gracefully degrade functionality where possible
- Log the issue for debugging

## Example Approach

**Typical 3D canvas creation:**
```javascript
// Before (no error handling)
const canvas = document.getElementById('3d-view');
const gl = canvas.getContext('webgl');
// Assumes gl is valid, crashes if null
```

**After (with auto-fallback):**
```javascript
function init3DView() {
  const canvas = document.getElementById('3d-view');
  let gl = null;

  try {
    gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  } catch (e) {
    console.error('WebGL initialization failed:', e);
  }

  if (!gl) {
    // Automatic fallback
    console.warn('3D hardware acceleration not available, using 2D fallback');
    return init2DFallback(canvas);
  }

  // Continue with 3D rendering
  return init3DRenderer(gl);
}

function init2DFallback(canvas) {
  // Provide alternative 2D representation
  // Or hide the feature with a message
  canvas.parentElement.innerHTML =
    '<div class="fallback-message">3D view requires hardware acceleration. ' +
    'Using simplified 2D view.</div>';
  // Return a compatible API that works with 2D
}
```

## Investigation Steps

### Step 1: Find the Setting

1. Search for "3D" or "hardware acceleration" in settings code
2. Locate the setting definition and where it's used
3. Trace what happens when the setting is enabled vs disabled

**Likely locations:**
- Settings/options configuration files
- Electron main process configuration
- Chromium flags/switches

### Step 2: Find 3D Usage

Search the codebase for:
- `getContext('webgl')`
- `getContext('experimental-webgl')`
- `THREE.js` or other 3D libraries
- Model viewer components
- 3D visualization code

### Step 3: Test Failure Scenarios

Verify behavior when:
1. 3D hardware acceleration is disabled via setting
2. Running on system without GPU support
3. Running in VM or remote desktop
4. WebGL blacklisted by browser

## Implementation Requirements

### Must Have:
- Detect WebGL support before attempting to use it
- Graceful fallback when 3D not available
- User-friendly messaging
- No crashes or cryptic errors

### Should Have:
- Log detailed information for debugging
- Provide alternative 2D visualization where appropriate
- Show helpful message suggesting solutions (enable setting, update drivers)

### Nice to Have:
- Detect partial 3D support (e.g., limited features)
- Progressive enhancement based on capabilities
- Performance fallback for slow 3D rendering

## Expected Deliverables

1. **Investigation Report:**
   - Where 3D hardware acceleration is used
   - What the current setting affects
   - Current behavior when 3D fails
   - List of features that need fallback

2. **Code Changes:**
   - Capability detection functions
   - Automatic fallback implementation
   - Error handling for 3D initialization failures
   - User-friendly messaging

3. **Testing:**
   - Test with 3D acceleration disabled
   - Test on system without GPU
   - Verify graceful fallback
   - Ensure no crashes or errors

4. **Documentation:**
   - Update code comments
   - Document the fallback behavior
   - Note any limitations of 2D fallback

## Success Criteria

- [ ] Identified all locations using 3D hardware acceleration
- [ ] Implemented capability detection for WebGL/3D support
- [ ] Added automatic fallback when 3D fails
- [ ] No crashes when 3D hardware acceleration unavailable
- [ ] User-friendly messages explaining fallback
- [ ] Tested with 3D disabled and on non-GPU system
- [ ] Code handles both full and partial 3D failures

## Testing Approach

**Disable 3D in different ways:**
1. Via configurator setting (if exists)
2. Chrome flag: `--disable-webgl`
3. Electron app flag: `--disable-gpu`
4. Browser blacklist override

**Test these scenarios:**
- Startup with 3D disabled
- Navigate to features using 3D
- Verify fallback UI appears
- Check for console errors
- Ensure app remains functional

## Resources

**Search Commands:**
```bash
# Find WebGL usage
grep -r "getContext.*webgl" inav-configurator/

# Find 3D libraries
grep -r "THREE\|WebGL\|gl-matrix" inav-configurator/

# Find hardware acceleration settings
grep -ri "hardware.*accel\|disable.*3d" inav-configurator/
```

**Related Files (Likely):**
- Settings/configuration files
- Magnetometer calibration (often uses 3D view)
- Model viewer (if exists)
- Electron main process initialization

## Notes

- This improves user experience for users without GPU support
- Prevents confusing crashes and errors
- Makes the app more robust and accessible
- Current setting requires manual intervention - auto-detection is better UX
- Some virtualized environments don't support WebGL well

## Why This Matters

**User Impact:**
- Users on VMs, remote desktop, or older systems often lack 3D support
- Current behavior probably crashes or shows errors
- Users may not understand the "disable 3D" setting
- Auto-fallback provides seamless experience

**Code Quality:**
- Proper error handling and capability detection
- Defensive programming practices
- Better user experience
- Easier to debug 3D issues

---
**Manager**
