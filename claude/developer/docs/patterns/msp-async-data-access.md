# Pattern: MSP Async Data Access

## The Problem

Race conditions occur when code accesses MSP-loaded data before the response has been received and processed.

## Key Principle

- **DO** send MSP requests early (improves perceived performance)
- **DON'T** access the returned values until the response callback fires

## Bad Pattern

```javascript
// Tab initialization
mspHelper.loadSomeData();  // Fires async request

// Later in same sync execution...
doSomethingWith(FC.SOME_DATA);  // BUG: Data not loaded yet!
```

## Good Pattern

```javascript
// Tab initialization - fire request early
mspHelper.loadSomeData(function() {
    // Only access data inside the callback
    doSomethingWith(FC.SOME_DATA);
});
```

## Alternative: Centralized Update Function

If multiple pieces of data need to be loaded before UI updates:

```javascript
// Fire requests early, update UI in coordinated callback chain
OSD.reload(function() {
    // OSD.reload handles all MSP loading internally
    // Only called after ALL data is ready
    OSD.GUI.updateAll();  // Safe to access all OSD data here
});
```

## Examples Fixed (PR #2467 / osd.js)

### 1. updatePilotAndCraftNames()

**Problem:** Called at end of tab init, before `OSD.data` was initialized by async font loading chain.

**Fix:** Removed premature call, added to `OSD.GUI.updateAll()` which runs after `OSD.reload()` completes.

### 2. createCustomElements() / fillCustomElementsValues()

**Problem:** `loadOsdCustomElements(createCustomElements)` was called during tab init, racing with `OSD.reload()` which also loads custom elements.

**Fix:** Removed premature call. Let `OSD.reload()` handle it in its properly-sequenced callback chain.

### 3. loadLogicConditions() in OSD tab

**Problem:** Called fire-and-forget, then `getLCoptions()` accessed conditions before loaded.

**Fix:** Added callback to refresh dropdowns after loading completes.

## How to Identify Similar Issues

1. **Error signature:** `Cannot read properties of undefined (reading 'xxx')`
2. **Location:** Usually in a function that accesses `FC.*` data structures
3. **Timing:** Occurs on tab load, especially with legacy/slower firmware
4. **Pattern:** Look for `mspHelper.load*()` calls without callbacks that are followed by code accessing that data

## Audit Checklist for Other Tabs

Search for this pattern in each tab file:

```bash
# Find fire-and-forget MSP loads (no callback)
grep -n "mspHelper\.load.*();" tabs/*.js

# Find data access that might race
grep -n "FC\.\w\+\." tabs/*.js | head -50
```

Questions to ask:
1. Is this MSP data accessed before its load callback fires?
2. Is there a race between multiple async chains accessing the same data?
3. Should this function be moved into a callback chain?

## Related

- MSP responses are async - callback fires when response arrives
- JavaScript is single-threaded but async operations interleave
- Legacy firmware may respond slower, making races more likely to manifest
