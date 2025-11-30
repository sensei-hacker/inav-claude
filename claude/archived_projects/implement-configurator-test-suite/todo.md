# Todo List: Implement Configurator Test Suite

## Phase 1: Research & Planning

- [ ] Research Electron testing frameworks
  - [ ] Playwright for Electron (recommended)
  - [ ] Puppeteer alternatives
  - [ ] WebdriverIO evaluation
  - [ ] Note: Skip Spectron (deprecated)

- [ ] Research unit testing frameworks
  - [ ] Jest (recommended)
  - [ ] Mocha + Chai
  - [ ] Vitest
  - [ ] Compare pros/cons

- [ ] Research Chrome DevTools Protocol (CDP)
  - [ ] Understand CDP capabilities
  - [ ] How Playwright/Puppeteer use CDP
  - [ ] When to use CDP directly

- [ ] Review existing tests
  - [ ] Examine transpiler tests (Mocha-based)
  - [ ] Identify patterns to reuse
  - [ ] Note what works well

- [ ] Define testing strategy
  - [ ] Test pyramid: Unit → Integration → E2E
  - [ ] What to test at each layer
  - [ ] Mocking approach for MSP/serial
  - [ ] Coverage goals

- [ ] Document tool selections
  - [ ] Chosen frameworks and rationale
  - [ ] Tradeoffs considered
  - [ ] Integration plan

## Phase 2: Setup Jest for Unit Testing

- [ ] Install Jest
  - [ ] `npm install --save-dev jest @types/jest`
  - [ ] Install additional helpers if needed

- [ ] Configure Jest
  - [ ] Create `jest.config.js`
  - [ ] Set test environment (node)
  - [ ] Configure test paths
  - [ ] Setup coverage reporting
  - [ ] Configure ES module support

- [ ] Add npm scripts
  - [ ] `npm test` - Run all tests
  - [ ] `npm test:watch` - Watch mode
  - [ ] `npm test:coverage` - Coverage report
  - [ ] `npm test:unit` - Unit tests only

- [ ] Create test directory structure
  - [ ] `tests/unit/`
  - [ ] `tests/integration/`
  - [ ] `tests/e2e/`
  - [ ] `tests/mocks/`
  - [ ] `tests/fixtures/`

- [ ] Test Jest setup
  - [ ] Create simple smoke test
  - [ ] Verify Jest runs correctly
  - [ ] Verify coverage works

## Phase 3: Create Mock Infrastructure

- [ ] Mock MSP layer
  - [ ] Create `tests/mocks/msp-mock.js`
  - [ ] Implement MockMSP class
  - [ ] Support setResponse() for test data
  - [ ] Mock send_message() function
  - [ ] Support common MSP commands

- [ ] Mock serial communication
  - [ ] Create `tests/mocks/serial-mock.js`
  - [ ] Implement MockSerial class
  - [ ] Mock connect/disconnect
  - [ ] Mock send/receive
  - [ ] Simulate connection states

- [ ] Create test fixtures
  - [ ] Sample FC responses (MSP_IDENT, MSP_STATUS, etc.)
  - [ ] Sample configuration data
  - [ ] Common test data patterns

- [ ] Document mocking approach
  - [ ] How to use mocks in tests
  - [ ] How to add new mock responses
  - [ ] Best practices

## Phase 4: Write Unit Tests

- [ ] Identify testable units
  - [ ] Utility functions
  - [ ] MSP message parsing/building
  - [ ] Data validation
  - [ ] String formatting
  - [ ] Settings cache operations

- [ ] Write MSP helper tests
  - [ ] Test message building
  - [ ] Test message parsing
  - [ ] Test error handling
  - [ ] `tests/unit/msp-helper.test.js`

- [ ] Write settings cache tests
  - [ ] Test get/set operations
  - [ ] Test scoping (per FC)
  - [ ] Test clear operations
  - [ ] `tests/unit/settings-cache.test.js`

- [ ] Write utility tests
  - [ ] String utilities
  - [ ] Number formatting
  - [ ] Data conversion
  - [ ] `tests/unit/utils.test.js`

- [ ] Write validation tests
  - [ ] Input validation functions
  - [ ] Range checks
  - [ ] Type checks
  - [ ] `tests/unit/validation.test.js`

- [ ] Aim for 5+ passing unit tests

## Phase 5: Write Integration Tests

- [ ] Setup integration test environment
  - [ ] Configure jsdom or similar for DOM
  - [ ] Setup tab testing infrastructure
  - [ ] Create tab test helpers

- [ ] Write Setup tab integration test
  - [ ] Mock MSP responses (IDENT, STATUS, etc.)
  - [ ] Test tab initialization
  - [ ] Test FC info display
  - [ ] Verify DOM updates
  - [ ] `tests/integration/tabs/setup.test.js`

- [ ] Write additional integration test (optional)
  - [ ] Ports tab or Modes tab
  - [ ] Test tab-specific functionality
  - [ ] Verify user interactions

- [ ] Aim for 1+ passing integration test

## Phase 6: Setup Playwright for E2E Testing

- [ ] Install Playwright
  - [ ] `npm install --save-dev @playwright/test playwright`
  - [ ] Install browsers if needed

- [ ] Configure Playwright
  - [ ] Create `playwright.config.js`
  - [ ] Set test directory (`tests/e2e/`)
  - [ ] Configure Electron launch
  - [ ] Set timeouts appropriately
  - [ ] Configure headless/headed mode

- [ ] Add npm scripts
  - [ ] `npm test:e2e` - Run E2E tests
  - [ ] `npm test:e2e:headed` - Run with visible window

- [ ] Create E2E test helpers
  - [ ] Electron app launcher
  - [ ] Common UI interactions
  - [ ] Wait utilities

## Phase 7: Write E2E Tests

- [ ] Write app launch test
  - [ ] Test Electron app starts
  - [ ] Verify main window appears
  - [ ] Basic UI elements present
  - [ ] `tests/e2e/app-launch.spec.js`

- [ ] Write navigation test
  - [ ] Click through tabs
  - [ ] Verify tab switching works
  - [ ] Check tab content loads
  - [ ] `tests/e2e/navigation.spec.js`

- [ ] Write connect workflow test (optional)
  - [ ] Mock serial port
  - [ ] Click connect button
  - [ ] Verify connection state
  - [ ] Navigate to Setup tab
  - [ ] Verify FC info displayed
  - [ ] `tests/e2e/connect-workflow.spec.js`

- [ ] Aim for 1+ passing E2E test

## Phase 8: Documentation

- [ ] Create TESTING.md
  - [ ] Overview of test strategy
  - [ ] How to run tests
  - [ ] How to write new tests
  - [ ] Mocking strategies
  - [ ] Directory structure
  - [ ] Best practices

- [ ] Document unit testing
  - [ ] How to write unit tests
  - [ ] How to use mocks
  - [ ] Examples

- [ ] Document integration testing
  - [ ] How to test tabs
  - [ ] How to mock MSP responses
  - [ ] Examples

- [ ] Document E2E testing
  - [ ] How to write E2E tests
  - [ ] How to launch Electron app
  - [ ] How to interact with UI
  - [ ] Examples

- [ ] Document CI/CD integration
  - [ ] GitHub Actions example
  - [ ] Running tests in CI
  - [ ] Coverage reporting

## Phase 9: Testing & Validation

- [ ] Run all tests
  - [ ] All unit tests pass
  - [ ] All integration tests pass
  - [ ] All E2E tests pass
  - [ ] No flaky tests

- [ ] Check coverage
  - [ ] Generate coverage report
  - [ ] Review coverage percentages
  - [ ] Identify gaps (for future work)

- [ ] Verify npm scripts
  - [ ] `npm test` works
  - [ ] `npm test:unit` works
  - [ ] `npm test:e2e` works
  - [ ] `npm test:coverage` works

- [ ] Test on clean install
  - [ ] Clone repo fresh
  - [ ] `npm install`
  - [ ] `npm test`
  - [ ] Verify all works

## Phase 10: Completion & Reporting

- [ ] Create completion report
  - [ ] Tools selected and why
  - [ ] Test infrastructure implemented
  - [ ] Sample tests created
  - [ ] Coverage achieved
  - [ ] Challenges encountered
  - [ ] Recommendations for expanding tests

- [ ] Update project documentation
  - [ ] Add testing section to README (if applicable)
  - [ ] Link to TESTING.md
  - [ ] Note test requirements for contributors

- [ ] Send completion report to manager
  - [ ] Summarize work done
  - [ ] Show sample test output
  - [ ] Provide next steps recommendations

## Success Checklist

- [ ] Jest installed and configured
- [ ] Playwright installed and configured
- [ ] Test directory structure created
- [ ] Mock infrastructure implemented
- [ ] 5+ unit tests passing
- [ ] 1+ integration test passing
- [ ] 1+ E2E test passing
- [ ] TESTING.md documentation created
- [ ] npm test scripts working
- [ ] Coverage reporting configured
- [ ] All tests green ✅

## Optional Enhancements

- [ ] CI/CD integration (GitHub Actions)
- [ ] Visual regression testing
- [ ] Test result reporting
- [ ] Code coverage badges
- [ ] Pre-commit hooks for tests
- [ ] Watch mode for development
