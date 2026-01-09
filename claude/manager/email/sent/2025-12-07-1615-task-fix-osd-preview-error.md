# Task Assignment: Fix OSD Tab Preview Error

**Date:** 2025-12-07 16:15
**Priority:** HIGH
**Estimated Effort:** 1-2 hours
**Type:** Bug Fix
**Branch:** From `maintenance-9.x`

## Task

Fix the JavaScript error occurring in the OSD tab:

```
osd.js:3207 Uncaught (in promise) TypeError: Cannot set properties of undefined (setting 'preview')
    at OSD.GUI.updatePreviews (osd.js:3207:22)
    at updatePilotAndCraftNames (osd.js:4240:13)
    at osd.js:3747:13
```

## Error Analysis

**Error Type:** `TypeError: Cannot set properties of undefined`

**Root Cause (likely):** Code is trying to set `.preview` on an object that doesn't exist. The object being accessed is `undefined`.

**Call Stack:**
1. `osd.js:3747` - Some initialization or callback
2. `updatePilotAndCraftNames()` at line 4240 - Updates pilot/craft name previews
3. `OSD.GUI.updatePreviews()` at line 3207 - Tries to set `.preview` on undefined object

## What to Do

### 1. Examine the Error Location

```bash
cd inav-configurator

# Look at line 3207 and surrounding context
sed -n '3200,3215p' tabs/osd.js

# Look at updatePilotAndCraftNames function
sed -n '4230,4250p' tabs/osd.js

# Look at the caller at line 3747
sed -n '3740,3755p' tabs/osd.js
```

### 2. Identify the Undefined Object

At line 3207, something like this is happening:
```javascript
someObject.preview = value;  // someObject is undefined
```

**Determine:**
- What object is expected to exist?
- Why is it undefined? (not initialized? wrong index? race condition?)
- Under what conditions does this error occur?

### 3. Common Causes

**Possible issues:**

**A. Array index out of bounds:**
```javascript
// If OSD.data.preview_items[index] doesn't exist
OSD.data.preview_items[index].preview = value;
```

**B. Object not initialized:**
```javascript
// If OSD.GUI.previews wasn't created yet
OSD.GUI.previews[key].preview = value;
```

**C. Race condition:**
```javascript
// If updatePreviews called before data loaded
// Object exists later but not at call time
```

**D. Missing null check:**
```javascript
// Need defensive check
if (item) {
    item.preview = value;
}
```

### 4. Reproduce the Error

1. Run Configurator: `npm start`
2. Connect to SITL or FC
3. Navigate to OSD tab
4. Note when error occurs:
   - On initial load?
   - After changing settings?
   - After specific action?

### 5. Implement Fix

**Typical fix patterns:**

**Pattern A: Add null/undefined check**
```javascript
// Before (crashes):
item.preview = value;

// After (safe):
if (item) {
    item.preview = value;
}
```

**Pattern B: Ensure initialization**
```javascript
// Ensure object exists before use
if (!OSD.data.preview_items[index]) {
    OSD.data.preview_items[index] = { preview: null };
}
OSD.data.preview_items[index].preview = value;
```

**Pattern C: Guard the function call**
```javascript
// In updatePilotAndCraftNames:
if (OSD.GUI.isInitialized) {
    OSD.GUI.updatePreviews();
}
```

### 6. Test the Fix

1. Verify error no longer occurs on OSD tab load
2. Verify OSD preview functionality still works
3. Test edge cases:
   - Fresh connection
   - Reconnection after disconnect
   - Different OSD configurations
   - Empty pilot/craft names

### 7. Check for Similar Issues

Search for similar patterns that might have the same bug:
```bash
grep -n "\.preview\s*=" tabs/osd.js | head -20
grep -n "updatePreviews" tabs/osd.js
```

## Success Criteria

- [ ] Error no longer occurs when loading OSD tab
- [ ] OSD preview functionality works correctly
- [ ] Fix handles edge cases (null/undefined data)
- [ ] No regressions introduced
- [ ] Code follows existing patterns in the file
- [ ] Completion report sent to Manager

## Deliverables

**If fix is straightforward:**
- Implement fix
- Test locally
- Report what was wrong and how you fixed it

**If fix requires PR:**
- Create branch from `maintenance-9.x`
- Implement and test fix
- Create PR to upstream
- Report PR number

## Notes

### Line Numbers May Shift

The line numbers in the error (3207, 4240, 3747) are from a specific build. If you're working on latest code, lines may have shifted. Use the function names to find the right locations.

### Check Recent Changes

This might be a regression. Check recent commits to osd.js:
```bash
git log --oneline -20 -- tabs/osd.js
```

### Consider Async Timing

The error is "Uncaught (in promise)" which suggests this happens in async code. The object might be undefined due to a timing issue where the preview update runs before data is fully loaded.

---
**Manager**
