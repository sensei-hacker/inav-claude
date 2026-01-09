/**
 * parameters-needed.js - Test Fixture
 *
 * Tests detection of code that requires parameters.
 * Block uses variables defined outside the extraction range.
 *
 * TARGET: Lines 16-18
 * EXPECTED: 2 parameters needed (userData, config) - Phase 2
 */

function processUser() {
  const userData = getUserData();
  const config = getConfig();

  // Extract this block (lines 16-18)
  const validated = validateData(userData);
  const processed = processData(userData, config);
  saveToDatabase(processed);
}
