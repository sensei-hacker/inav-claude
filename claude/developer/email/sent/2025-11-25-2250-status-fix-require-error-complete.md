# Status Report: Fix require() Error - COMPLETE

**Task Reference:** `developer/inbox/2025-11-25-1700-task-fix-require-error-onboard-logging.md`
**Status:** Completed
**Date:** 2025-11-25 22:50

## Summary

Fixed ESM conversion regressions in search and logging tabs. PR submitted.

## PR

https://github.com/iNavFlight/inav-configurator/pull/2434

## Changes

- `tabs/search.js`: Convert `require()` to ESM imports, replace `path.join(__dirname, ...)` with dynamic import
- `js/configurator_main.js`: Change search tab loading from `require()` to `import().then()`
- `tabs/logging.js`: Add missing `store` import, use `window.electronAPI.appendFile()`
- `js/main/main.js`: Add `appendFile` IPC handler
- `js/main/preload.js`: Expose `appendFile` in electronAPI

## Notes

The error was in `tabs/search.js`, not `onboard_logging.js` as the stack trace suggested. The search tab was never converted from CommonJS to ESM.

---

**Developer**
