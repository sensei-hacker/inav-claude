# Task Assignment: Fix gpsNumSat → gpsSats in Examples

**Date:** 2025-12-02 22:05
**To:** Developer
**From:** Manager
**Project:** New (standalone bug fix)
**Priority:** HIGH
**Estimated Effort:** 15-30 minutes
**Branch:** From master or maintenance branch (wherever transpiler code lives)

---

## Task

Fix transpilation error caused by outdated property name in JavaScript Programming examples. The examples use `flight.gpsNumSat` but the API was renamed to `flight.gpsSats`.

---

## Problem

**User report:**
```
Transpilation Error:
Semantic errors:
- Unknown property 'gpsNumSat' in 'flight.gpsNumSat'.
  Available: ... gpsSats, gpsValid, ...
```

**Error location:**
```javascript
if (flight.gpsNumSat < 6) {  // Line 4 in user's code (from example)
  gvar[0] = 0;
}

if (flight.gpsNumSat < 6) {  // Line 8
  // ...
}
```

**Root cause:** Example code uses old property name `gpsNumSat`, but API definition has `gpsSats`.

---

## Investigation Findings (Manager)

**Files with inconsistency:**

**CORRECT (API definition):**
- `js/transpiler/api/definitions/flight.js:120` → `gpsSats:` ✅
- `js/transpiler/transpiler/inav_constants.js:289` → `'gpsSats'` ✅
- `js/transpiler/transpiler/tests/test_flight.js:37,82` → `gpsSats` ✅
- `js/transpiler/transpiler/tests/comparison_operators.test.cjs:114,123` → `gpsSats` ✅

**INCORRECT (examples):**
- `js/transpiler/examples/index.js:120` → `gpsNumSat` ❌
- `js/transpiler/examples/index.js:124` → `gpsNumSat` ❌

---

## Solution

**Simple find-replace in examples file:**

**File:** `js/transpiler/examples/index.js`

Replace all instances of `gpsNumSat` with `gpsSats`.

**Expected changes (2 lines):**

Line 120:
```javascript
// BEFORE:
if (flight.gpsNumSat < 6) {

// AFTER:
if (flight.gpsSats < 6) {
```

Line 124:
```javascript
// BEFORE:
if (flight.gpsNumSat >= 6) {

// AFTER:
if (flight.gpsSats >= 6) {
```

---

## Implementation

### Step 1: Verify Current State

```bash
cd js/transpiler
grep -n "gpsNumSat" examples/index.js
```

Should show lines 120 and 124.

### Step 2: Fix Examples

**Option A - Manual edit:**
- Open `js/transpiler/examples/index.js`
- Line 120: Change `gpsNumSat` → `gpsSats`
- Line 124: Change `gpsNumSat` → `gpsSats`

**Option B - Automated:**
```bash
sed -i 's/gpsNumSat/gpsSats/g' js/transpiler/examples/index.js
```

### Step 3: Verify Fix

```bash
# Should return no results
grep -n "gpsNumSat" js/transpiler/examples/index.js

# Should show the fixed lines
grep -n "gpsSats" js/transpiler/examples/index.js
```

### Step 4: Test

1. Build configurator: `npm run make` (or dev build)
2. Launch configurator
3. Go to JavaScript Programming tab
4. Load the example that uses GPS satellites
5. Click "Transpile"
6. **Verify:** No "Unknown property 'gpsNumSat'" error
7. **Verify:** Transpilation succeeds

---

## Testing

### Minimal Test:

**Test code** (paste in JavaScript Programming tab):
```javascript
const { flight, gvar } = inav;

if (flight.gpsSats < 6) {
  gvar[0] = 0;
}

if (flight.gpsSats >= 6) {
  gvar[0] = 1;
}
```

**Expected result:** Transpiles successfully, no errors.

### Full Example Test:

1. Load GPS-related example from dropdown
2. Transpile
3. Verify success

---

## Root Cause Analysis

**Why did this happen?**

Likely scenario:
1. Property was originally named `gpsNumSat` in API
2. Recent commit renamed it to `gpsSats` (more concise, consistent naming)
3. API definition and tests were updated
4. Examples file was **missed** in the renaming

**How to prevent:**
- Automated tests that transpile all examples
- Pre-commit hook that validates examples
- Search for all references when renaming API properties

---

## Files Modified

**Single file:**
- `js/transpiler/examples/index.js` (2 line changes)

---

## Success Criteria

- [ ] No instances of `gpsNumSat` remain in examples/index.js
- [ ] All instances changed to `gpsSats`
- [ ] Example code transpiles without errors
- [ ] No regression in other examples
- [ ] Build succeeds

---

## Priority Justification

**HIGH priority because:**
- **User-facing bug:** Prevents users from using examples
- **Learning impact:** Examples are first thing new users try
- **Quick fix:** 2 line change, 15-30 minutes
- **Immediate value:** Unblocks users right away

---

## Additional Checks

**While fixing this, also verify:**

1. **Are there other renamed properties in examples?**
   ```bash
   # Check if examples match current API
   grep -r "flight\." js/transpiler/examples/
   ```

2. **Are all examples valid?**
   - Consider adding automated validation
   - Transpile all examples as part of test suite

---

## Commit Message Template

```
Fix outdated gpsNumSat property in JS examples

The API property was renamed from 'gpsNumSat' to 'gpsSats' but the
examples file was not updated, causing transpilation errors.

Changes:
- js/transpiler/examples/index.js: gpsNumSat → gpsSats (2 instances)

Fixes transpilation error: "Unknown property 'gpsNumSat'"

Users can now successfully use GPS satellite examples.
```

---

## PR Information

**This fix should go in:**
- Same PR as other transpiler fixes (if open)
- Or standalone bugfix PR
- Should be merged quickly (user-blocking)

**Related PRs:**
- PR #2439 (transpiler feature)
- PR #2451 (cleanup)
- May be good to include in one of these

---

## Notes

- This is a **documentation bug**, not a code logic bug
- The API itself is correct (`gpsSats`)
- Only the examples were wrong
- Very low risk fix (examples only)

---

**Manager**
2025-12-02 22:05
