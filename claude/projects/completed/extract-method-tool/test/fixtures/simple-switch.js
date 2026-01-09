/**
 * simple-switch.js - Test Fixture
 *
 * Tests extraction of code from within a switch case.
 * Common real-world scenario for refactoring.
 *
 * TARGET: Lines 14-16 (case 'save' body statements)
 * EXPECTED: Feasible, tests break statement handling
 */

function handleAction(action) {
  switch(action) {
    case 'save':
      console.log('Saving...');
      const result = performSave();
      console.log('Done!');
      break;
    case 'load':
      console.log('Loading...');
      break;
  }
}
