# Task Assignment: Handle setTimeout in Transpiler

**Date:** 2025-12-10
**To:** Developer
**From:** Manager
**Priority:** LOW
**Project:** transpiler-enhancements

## Objective

Improve user experience when they try to use `setTimeout()` in JavaScript programming.

## Background

Users familiar with JavaScript may try to use `setTimeout()` which doesn't exist in the INAV logic condition environment. We should either help them or actually support it.

## Options

### Option A: Helpful Error Message (Simpler)

If user writes `setTimeout(...)`, show a helpful error suggesting alternatives:

```
Error: setTimeout() is not available. Consider using:
  - delay(condition, ms) - Returns true after condition has been true for ms milliseconds
  - timer(onMs, offMs) - Alternates between true (for onMs) and false (for offMs)
  - edge(condition, ms) - Returns true momentarily when condition becomes true, stays true for ms
```

### Option B: Actually Implement setTimeout (More Complex)

If it's feasible, implement `setTimeout()` that transpiles to appropriate logic conditions.

**Considerations:**
- Would need to map to `delay()` or `timer()` operations
- Callback execution model doesn't map cleanly to logic conditions
- May require significant complexity for limited benefit

## Task

1. Evaluate both options
2. Implement Option A at minimum (helpful error)
3. If Option B seems reasonable after analysis, propose an implementation approach

## Notes

- Option A is the safe/easy choice
- Option B would be nice-to-have if it doesn't add too much complexity
- The transpiler already has `delay()`, `timer()`, and `edge()` which cover most timing use cases

## Deliverable

- At minimum: Helpful error message when `setTimeout` is used
- Optionally: Working `setTimeout` implementation if feasible
