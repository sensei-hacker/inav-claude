# Project: Implement Configurator Test Suite

**Status:** ✉️ ASSIGNED
**Priority:** Medium
**Type:** Infrastructure / Testing
**Created:** 2025-11-25
**Assignee:** Developer

## Overview

Research, design, and implement an automated test suite for the INAV Configurator (Electron application). Establish testing methodology, select appropriate tools, and create proof-of-concept tests to validate the approach.

## Problem

The INAV Configurator currently lacks automated testing:
- No unit tests for JavaScript modules
- No integration tests for tab functionality
- No end-to-end tests for user workflows
- Manual testing only
- Risk of regressions when making changes
- Slow feedback loop for developers

**Impact:**
- Changes may introduce bugs that aren't caught until user reports
- Difficult to refactor code with confidence
- No automated validation of functionality
- Time-consuming manual testing required

## Objectives

1. **Research Testing Options:** Evaluate testing frameworks suitable for Electron apps
2. **Design Test Strategy:** Define what to test and how (unit, integration, E2E)
3. **Select Tools:** Choose appropriate testing frameworks and tools
4. **Implement Proof-of-Concept:** Create sample tests demonstrating the approach
5. **Document Approach:** Provide guidelines for writing tests going forward

## Scope

### In Scope

**Research Phase:**
- Electron testing frameworks (Spectron, Playwright, Puppeteer, WebdriverIO)
- Unit testing frameworks (Jest, Mocha, Vitest)
- Chrome DevTools Protocol (CDP) usage for automation
- CI/CD integration considerations
- Mock strategies for hardware (FC serial communication)

**Implementation Phase:**
- Setup testing infrastructure
- Create proof-of-concept tests (at least 3 types):
  - Unit tests for utility functions
  - Integration tests for a tab (e.g., Setup tab)
  - End-to-end test for a user workflow
- Document testing approach and guidelines

**Deliverables:**
- Testing framework installed and configured
- Sample test suite demonstrating approach
- Documentation for writing new tests
- CI/CD integration plan (optional)

### Out of Scope

- Comprehensive test coverage of entire configurator (initial implementation only)
- Performance testing
- Load testing
- Security testing (separate concern)

## Testing Considerations for Electron Apps

### Architecture Context

INAV Configurator is an **Electron application**:
- **Main Process:** Node.js backend (serial communication, file system)
- **Renderer Process:** Chromium frontend (HTML/CSS/JavaScript UI)
- **IPC:** Communication between main and renderer processes

### Testing Layers

**1. Unit Tests**
- Test individual functions/modules in isolation
- Mock dependencies (MSP, serial, FC)
- Fast execution
- Framework: Jest, Mocha, or Vitest

**2. Integration Tests**
- Test tab functionality with real DOM
- Mock MSP/serial communication
- Test component interactions
- Framework: Jest + jsdom or Electron test environment

**3. End-to-End Tests**
- Test complete user workflows
- Automate full Electron app
- May need FC simulator or mocks
- Framework: Playwright, Spectron (deprecated), or Puppeteer

## Testing Framework Options

### For Unit/Integration Tests

**Jest** (Recommended for unit tests)
- Industry standard for JavaScript testing
- Built-in mocking, assertions, coverage
- Good ES module support
- Fast parallel execution
- Excellent documentation

**Mocha + Chai**
- Flexible, modular
- Popular in Node.js ecosystem
- Requires more setup
- Good for complex test scenarios

**Vitest**
- Modern, fast (Vite-based)
- Jest-compatible API
- Native ES module support
- Good for newer projects

### For E2E Testing Electron Apps

**Playwright** (Recommended)
- Modern, actively maintained
- **Built-in Electron support** (as of v1.9)
- Chrome DevTools Protocol (CDP) based
- Cross-browser (though Electron uses Chromium)
- Excellent documentation and tooling
- Fast, reliable
- Auto-waiting for elements

**Spectron** (Deprecated - DO NOT USE)
- Official Electron testing framework
- **Deprecated in 2021** - no longer maintained
- Based on WebdriverIO
- Many projects migrating away

**Puppeteer**
- Chrome DevTools Protocol based
- Good for Chromium automation
- Requires additional setup for Electron
- Strong community support
- More manual than Playwright

**WebdriverIO**
- Traditional Selenium-based approach
- Can work with Electron
- More complex setup
- Good for cross-platform testing

### Recommendation: Playwright + Jest

**Unit/Integration Tests:** Jest
- Fast, proven, excellent tooling
- Mock MSP/serial communication
- Test individual modules and tabs

**E2E Tests:** Playwright
- Native Electron support
- Modern, actively maintained
- Reliable automation
- Test complete workflows

## Testing Strategy

### Phase 1: Unit Tests (Foundation)

**Target:** Utility functions, helpers, data processing

**Examples:**
- Transpiler functions (already has tests via Mocha)
- MSP message parsing/building
- Data validation functions
- Settings cache operations
- String formatting utilities

**Approach:**
```javascript
// Example: jest.config.js
module.exports = {
  testEnvironment: 'node',
  coverageDirectory: 'coverage',
  testMatch: ['**/__tests__/**/*.test.js']
};

// Example test: tests/msp-helper.test.js
import { buildMSPMessage } from '../js/msp/MSPHelper.js';

describe('MSPHelper', () => {
  test('buildMSPMessage creates valid message', () => {
    const message = buildMSPMessage(MSP_codes.MSP_STATUS);
    expect(message).toBeDefined();
    expect(message.code).toBe(MSP_codes.MSP_STATUS);
  });
});
```

### Phase 2: Integration Tests (Tab Testing)

**Target:** Tab functionality with DOM interaction

**Examples:**
- Setup tab loads and displays FC info
- Ports tab updates serial port configuration
- Modes tab adds/removes mode ranges
- Configuration tab saves settings

**Approach:**
```javascript
// Example: tests/tabs/setup.integration.test.js
import { TABS } from '../tabs/setup.js';

describe('Setup Tab', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="content"></div>';
    // Mock MSP responses
    mockMSP.setResponse(MSP_codes.MSP_IDENT, { ... });
  });

  test('displays firmware version', async () => {
    await TABS.setup.initialize();
    const versionElement = document.querySelector('.firmware-version');
    expect(versionElement.textContent).toBe('INAV 7.1.2');
  });
});
```

### Phase 3: End-to-End Tests (User Workflows)

**Target:** Complete user scenarios

**Examples:**
- Connect to FC → Navigate to Setup → View info
- Change PID values → Save to FC → Verify saved
- Import/export settings backup

**Approach:**
```javascript
// Example: e2e/connect-to-fc.spec.js
const { _electron: electron } = require('playwright');

test('connect to flight controller', async () => {
  const app = await electron.launch({ args: ['.'] });
  const window = await app.firstWindow();

  // Mock serial port
  await window.evaluate(() => {
    // Setup mock serial backend
  });

  // Click connect button
  await window.click('#connectbutton');

  // Verify connected state
  await expect(window.locator('.connect_state')).toHaveText('Connected');

  await app.close();
});
```

## Mocking Strategy

### MSP Communication

**Challenge:** Tests shouldn't require real FC hardware

**Solution:** Mock MSP layer
```javascript
// tests/mocks/msp-mock.js
class MockMSP {
  constructor() {
    this.responses = new Map();
  }

  setResponse(code, data) {
    this.responses.set(code, data);
  }

  send_message(code, data, callback) {
    const response = this.responses.get(code);
    callback(response);
  }
}
```

### Serial Communication

**Challenge:** Tests shouldn't access real serial ports

**Solution:** Mock serial backend
```javascript
// tests/mocks/serial-mock.js
class MockSerial {
  constructor() {
    this.connected = false;
  }

  connect(path, options, callback) {
    this.connected = true;
    callback({ connected: true });
  }

  send(data, callback) {
    // Simulate response
    callback(mockData);
  }
}
```

## Implementation Plan

### Step 1: Setup Jest for Unit Tests

```bash
npm install --save-dev jest @types/jest
```

**Configure Jest:**
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.js'],
  collectCoverageFrom: [
    'js/**/*.js',
    '!js/libraries/**',
    '!node_modules/**'
  ],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/js/$1'
  }
};
```

**Add test script to package.json:**
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

### Step 2: Create Sample Unit Tests

**Create test directory structure:**
```
tests/
  unit/
    msp-helper.test.js
    settings-cache.test.js
    utils.test.js
  integration/
    tabs/
      setup.test.js
  e2e/
    connect-workflow.spec.js
  mocks/
    msp-mock.js
    serial-mock.js
```

**Write 3-5 sample unit tests** for existing utilities.

### Step 3: Setup Playwright for E2E Tests

```bash
npm install --save-dev @playwright/test playwright
```

**Configure Playwright:**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  use: {
    headless: false, // Show Electron window during tests
  },
});
```

### Step 4: Create Sample E2E Test

**Write 1-2 E2E tests** demonstrating:
- Launching Electron app
- Interacting with UI
- Verifying results

### Step 5: Documentation

**Create TESTING.md:**
- How to run tests
- How to write new tests
- Mocking strategies
- Best practices
- CI/CD integration

## Success Criteria

- [ ] Testing framework installed and configured (Jest + Playwright)
- [ ] At least 5 unit tests created and passing
- [ ] At least 1 integration test created and passing
- [ ] At least 1 E2E test created and passing
- [ ] Mock strategy implemented for MSP/serial
- [ ] Documentation created (TESTING.md)
- [ ] Tests run via npm scripts (`npm test`)
- [ ] Coverage reporting configured
- [ ] CI/CD integration plan documented (optional)

## Estimated Time

- **Research:** 2-3 hours
- **Jest setup + unit tests:** 3-4 hours
- **Playwright setup + E2E tests:** 3-4 hours
- **Integration tests:** 2-3 hours
- **Mocking infrastructure:** 2-3 hours
- **Documentation:** 1-2 hours

**Total:** 13-19 hours

## Testing Best Practices

**1. Test Pyramid:**
- Many unit tests (fast, cheap)
- Some integration tests (medium speed/cost)
- Few E2E tests (slow, expensive)

**2. Isolation:**
- Tests shouldn't depend on each other
- Each test should setup and teardown cleanly
- Use mocks to avoid external dependencies

**3. Clarity:**
- Test names describe what they test
- Use AAA pattern: Arrange, Act, Assert
- One assertion per test (generally)

**4. Maintainability:**
- Keep tests simple
- Don't test implementation details
- Update tests when requirements change

## Chrome DevTools Protocol (CDP)

**Note:** Both Playwright and Puppeteer use CDP under the hood for Chromium automation.

**Direct CDP Usage (Advanced):**
```javascript
const { chromium } = require('playwright');

const browser = await chromium.connectOverCDP('http://localhost:9222');
const context = browser.contexts()[0];
const page = context.pages()[0];

// Access CDP directly
const client = await context.newCDPSession(page);
await client.send('Network.enable');
```

**When to use:**
- Advanced debugging
- Network interception
- Performance profiling
- Custom automation needs

**For most testing, Playwright's high-level API is sufficient.**

## CI/CD Integration

**GitHub Actions Example:**
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm test
      - run: npm run test:e2e
        env:
          DISPLAY: ':99.0'
```

**Benefits:**
- Automated test runs on every commit
- Pull request validation
- Prevent regressions
- Build confidence

## Deliverables

1. **Testing Infrastructure:**
   - Jest configured for unit/integration tests
   - Playwright configured for E2E tests
   - Test directory structure created
   - npm scripts for running tests

2. **Sample Tests:**
   - 5+ unit tests (utilities, MSP helpers)
   - 1+ integration test (tab functionality)
   - 1+ E2E test (user workflow)
   - Mock implementations (MSP, serial)

3. **Documentation:**
   - TESTING.md guide
   - How to write tests
   - How to run tests
   - Mocking strategies
   - CI/CD integration plan

4. **Completion Report:**
   - Tools selected and rationale
   - Test coverage achieved
   - Challenges encountered
   - Recommendations for expanding test suite

## Priority Justification

**Medium Priority:**
- Important for code quality and confidence
- Not urgent (no blocking issues)
- Foundational work for future development
- Will pay dividends over time
- Should be done before major refactoring

## Notes

- Transpiler already has Mocha-based tests - can serve as example
- Focus on establishing patterns, not comprehensive coverage
- Proof-of-concept to validate approach
- Can expand test suite incrementally
- Consider developer experience (fast tests, clear output)

## Related Work

- **Backburner:** investigate-automated-testing-mcp (MCP-specific research)
- This project is more general and actionable - establishing core testing infrastructure

## Resources

**Documentation:**
- Playwright Electron: https://playwright.dev/docs/api/class-electron
- Jest: https://jestjs.io/
- Chrome DevTools Protocol: https://chromedevtools.github.io/devtools-protocol/

**Examples:**
- Transpiler tests: `js/transpiler/transpiler/tests/` (Mocha-based)
