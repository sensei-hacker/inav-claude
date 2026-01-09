# Task Assignment: Fix Transpiler Tests - Jest Dependency

**Date:** 2025-12-10
**To:** Developer
**From:** Manager
**Priority:** MEDIUM
**Project:** transpiler-maintenance

## Objective

Some tests in `js/transpiler/transpiler/tests/` may require Jest or another external test framework that isn't installed. Fix these so they can run.

## Task

1. Check `inav-configurator/js/transpiler/transpiler/tests/` for tests that require Jest or other external dependencies

2. For each test file that requires Jest:
   - **Option A (Preferred):** Adjust the test to run without Jest using Node.js built-in `assert` or simple console-based testing
   - **Option B:** If Jest is truly needed, install it via yarn:
     ```bash
     cd inav-configurator
     yarn add --dev jest
     ```

3. Verify all tests can run successfully

## Notes

- The project uses yarn, not npm
- Prefer lightweight solutions that don't add heavy dependencies
- If converting from Jest, simple patterns like this work:
  ```javascript
  // Instead of: expect(result).toBe(expected)
  // Use: assert.strictEqual(result, expected)

  // Instead of: expect(result).toEqual(expected)
  // Use: assert.deepStrictEqual(result, expected)
  ```

## Deliverable

- All tests in `js/transpiler/transpiler/tests/` runnable
- Document how to run the tests (e.g., `node test_foo.js` or `yarn test`)
