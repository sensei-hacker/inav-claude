/**
 * return-value.js - Test Fixture
 *
 * Tests detection of code that needs to return a value.
 * Block modifies a variable that is used after the block.
 *
 * TARGET: Lines 15-16
 * EXPECTED: Return value needed (saveResult) - Phase 2
 */

function doWork() {
  const data = getData();

  // Extract this block (lines 15-16)
  let saveResult = null;
  saveResult = saveToDatabase(data);

  if (saveResult.success) {
    console.log('Saved!');
  }
}
