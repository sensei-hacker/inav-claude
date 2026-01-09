# Todo List: Create PrivacyLRS Test Runner Skill

## Phase 1: Discover Testing Infrastructure

- [ ] Explore `PrivacyLRS/src/test/` directory structure
- [ ] Find all test files in codebase
  - [ ] Search for `*test*.py` files
  - [ ] Search for `test_*.py` files
  - [ ] Search for `*_test.py` files
- [ ] Identify test framework(s) being used
  - [ ] Check for pytest
  - [ ] Check for unittest
  - [ ] Check for other frameworks
- [ ] Locate test configuration files
  - [ ] Look for `pytest.ini`
  - [ ] Look for `tox.ini`
  - [ ] Look for `.coveragerc`
  - [ ] Look for `setup.cfg` test config
- [ ] Find test documentation
  - [ ] Check for README in test directories
  - [ ] Look for test docs in `docs/`
  - [ ] Check CI/CD configs (.github/workflows/, .gitlab-ci.yml)
- [ ] Document findings in working notes

## Phase 2: Learn Test Execution

- [ ] Identify test commands
  - [ ] Check Makefile for test targets
  - [ ] Look for test scripts (run_tests.sh, test.sh)
  - [ ] Check package.json if Node.js project
  - [ ] Review CI/CD for test commands
- [ ] Try running tests
  - [ ] Run all tests
  - [ ] Run specific test directory
  - [ ] Run specific test file
  - [ ] Run with verbose output
  - [ ] Run with coverage reporting
- [ ] Document prerequisites
  - [ ] List required dependencies
  - [ ] Note environment variables needed
  - [ ] Document setup steps
- [ ] Note test results
  - [ ] Do all tests pass?
  - [ ] Any failing tests?
  - [ ] How long does suite take?
  - [ ] What's the test coverage?
- [ ] Document in working notes

## Phase 3: Create Working Notes

- [ ] Document test infrastructure overview
  - [ ] Test framework(s) used
  - [ ] Number of test files
  - [ ] Number of tests
  - [ ] Test organization/structure
- [ ] Write step-by-step execution guide
  - [ ] Prerequisites and setup
  - [ ] Commands to run all tests
  - [ ] Commands for specific tests
  - [ ] Options and flags
  - [ ] Expected output
- [ ] Document common commands
  - [ ] Quick smoke tests
  - [ ] Full test suite
  - [ ] Coverage reporting
  - [ ] Verbose output
  - [ ] Specific test selection
- [ ] Add troubleshooting section
  - [ ] Common errors
  - [ ] Solutions
  - [ ] Dependencies issues

## Phase 4: Create Test Runner Skill

- [ ] Design skill functionality
  - [ ] Determine common use cases
  - [ ] Plan skill structure
  - [ ] Identify commands to include
- [ ] Write skill file
  - [ ] Create `.claude/skills/privacylrs-test-runner.md`
  - [ ] Write clear description
  - [ ] Add step-by-step instructions
  - [ ] Include command examples
  - [ ] Add common options
  - [ ] Include troubleshooting tips
- [ ] Test the skill
  - [ ] Try using skill to run all tests
  - [ ] Try using skill for specific tests
  - [ ] Verify instructions work
  - [ ] Fix any issues
- [ ] Refine skill based on testing

## Phase 5: Completion

- [ ] Review all deliverables
  - [ ] Working notes complete
  - [ ] Skill file complete and tested
  - [ ] All success criteria met
- [ ] Create completion report
  - [ ] Summary of test infrastructure
  - [ ] How to run tests (brief)
  - [ ] Location of skill file
  - [ ] Any issues discovered
- [ ] Send report to manager
  - [ ] Save to `security-analyst/sent/`
  - [ ] Copy to `manager/inbox/`
- [ ] Archive task assignment
  - [ ] Move from `security-analyst/inbox/`
  - [ ] To `security-analyst/inbox-archive/`
