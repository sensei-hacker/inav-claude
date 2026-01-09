# Task Paused: Fix preload.mjs forEach Error

## Status: PAUSED - Cannot Reproduce

## Summary

Investigated the reported error:
```
preload.mjs:25 Uncaught Error: Cannot read properties of undefined (reading 'forEach')
```

## Findings

1. **Error location misleading**: Line 25 of built `preload.mjs` is `onSerialData` which registers an IPC callback. The actual forEach calls are in the callback handlers in connection classes.

2. **Found real bugs** in `addOnReceiveCallback` method across three files:
   - `js/connection/connectionSerial.js:109`
   - `js/connection/connectionTcp.js:106`
   - `js/connection/connectionUdp.js:105`

   All three have the same typo - they push to `_onReceiveErrorListeners` instead of `_onReceiveListeners`. This would cause data receive callbacks to never fire, but may not be the cause of the reported error.

3. **`_onReceiveErrorListeners` is declared in base class** (`connection.js:24`), so it shouldn't be undefined after `super()` completes.

4. **Cannot reproduce**: After reverting to original code, the error no longer appears in console.

## Recommendation

- Error may be intermittent or environment-specific
- The `addOnReceiveCallback` typo bugs are real and should be fixed separately
- Suggest closing this task unless error reappears
- If it does reappear, need exact reproduction steps

## Files Examined

- `js/main/preload.js` (source)
- `.vite/build/preload.mjs` (built)
- `js/connection/connectionSerial.js`
- `js/connection/connectionTcp.js`
- `js/connection/connectionUdp.js`
- `js/connection/connection.js` (base class)
