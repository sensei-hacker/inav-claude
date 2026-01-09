/**
 * simple-block.js - Test Fixture
 *
 * Tests extraction of a simple self-contained code block
 * with no external dependencies.
 *
 * TARGET: Lines 14-16 (const x, const y, console.log)
 * EXPECTED: Feasible, 0 parameters, no return value
 */

function example() {
  console.log('Before');
  // Extract this (lines 14-16)
  const x = 1;
  const y = 2;
  console.log(x + y);

  console.log('After');
}
