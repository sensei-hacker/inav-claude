# Task Assignment: Implement Configurator Test Suite

**Date:** 2025-11-25 20:30
**Project:** implement-configurator-test-suite
**Priority:** Medium
**Estimated Effort:** 13-19 hours
**Branch:** Create from master

## Task

Research, design, and implement an automated test suite for the INAV Configurator. Establish testing infrastructure using appropriate tools for Electron applications and create proof-of-concept tests.

## Problem

The configurator currently has no automated testing:
- No unit tests for JavaScript modules
- No integration tests for tabs
- No end-to-end tests for workflows
- Manual testing only
- High risk of regressions
- Difficult to refactor with confidence

## Objectives

1. **Research & Select Tools:** Evaluate testing frameworks for Electron/Node.js apps
2. **Setup Infrastructure:** Install and configure testing tools
3. **Implement Mocks:** Create mock layer for MSP/serial communication
4. **Write Sample Tests:** Create proof-of-concept tests at 3 levels
5. **Document Approach:** Provide testing guide for future development

## Recommended Approach

### Testing Layers

**Unit Tests (Foundation)**
- Test individual functions in isolation
- Fast, cheap, many tests
- Framework: **Jest** (recommended)

**Integration Tests (Middle)**
- Test tab functionality with DOM
- Mock MSP responses
- Medium speed/cost
- Framework: **Jest + jsdom**

**E2E Tests (Top)**
- Test complete workflows
- Automate full Electron app
- Slow, expensive, few tests
- Framework: **Playwright** (recommended - native Electron support)

### Tool Recommendations

**Jest for Unit/Integration Testing:**
- Industry standard JavaScript testing
- Built-in mocking, assertions, coverage
- Good ES module support
- Fast execution
- Excellent documentation

**Playwright for E2E Testing:**
- Native Electron support (as of v1.9)
- Modern, actively maintained
- Chrome DevTools Protocol based
- Reliable automation
- Auto-waiting for elements

**Do NOT use:**
- **Spectron** - Deprecated in 2021, no longer maintained

**Alternatives to consider:**
- Puppeteer (CDP-based, requires extra Electron setup)
- WebdriverIO (more complex)
- Vitest (modern Jest alternative)
- Mocha + Chai (existing transpiler tests use this)

## Implementation Plan

### Phase 1: Research (2-3 hours)

Research and document:
- Jest vs. Mocha vs. Vitest for unit tests
- Playwright vs. Puppeteer for E2E
- Chrome DevTools Protocol capabilities
- Mocking strategies for hardware (FC serial)
- CI/CD integration approaches

**Deliverable:** Tool selection rationale document

### Phase 2: Setup Jest (3-4 hours)

```bash
npm install --save-dev jest @types/jest
```

**Configure:**
- Create `jest.config.js`
- Setup test directory structure: `tests/unit/`, `tests/integration/`, `tests/mocks/`
- Add npm scripts: `test`, `test:watch`, `test:coverage`
- Configure ES module support
- Setup coverage reporting

**Deliverable:** Jest running with smoke test

### Phase 3: Create Mocks (2-3 hours)

**Mock MSP Communication:**
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

**Mock Serial Communication:**
```javascript
// tests/mocks/serial-mock.js
class MockSerial {
  connect(path, options, callback) {
    this.connected = true;
    callback({ connected: true });
  }
}
```

**Create Test Fixtures:**
- Sample MSP responses (IDENT, STATUS, etc.)
- Common FC configuration data

**Deliverable:** Reusable mock infrastructure

### Phase 4: Write Unit Tests (3-4 hours)

Create 5+ unit tests for:
- MSP helper functions (message building/parsing)
- Settings cache operations (get/set/clear)
- Utility functions (formatting, validation)
- Data processing functions

**Example:**
```javascript
// tests/unit/msp-helper.test.js
import { buildMSPMessage } from '../../js/msp/MSPHelper.js';

describe('MSPHelper', () => {
  test('buildMSPMessage creates valid message', () => {
    const message = buildMSPMessage(MSP_codes.MSP_STATUS);
    expect(message).toBeDefined();
    expect(message.code).toBe(MSP_codes.MSP_STATUS);
  });
});
```

**Deliverable:** 5+ passing unit tests

### Phase 5: Write Integration Test (2-3 hours)

Create 1+ integration test for tab functionality:

**Example - Setup Tab:**
```javascript
// tests/integration/tabs/setup.test.js
describe('Setup Tab', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="content"></div>';
    mockMSP.setResponse(MSP_codes.MSP_IDENT, {
      version: '7.1.2',
      multiType: 3
    });
  });

  test('displays firmware version', async () => {
    await TABS.setup.initialize();
    const version = document.querySelector('.firmware-version');
    expect(version.textContent).toBe('INAV 7.1.2');
  });
});
```

**Deliverable:** 1+ passing integration test

### Phase 6: Setup Playwright (3-4 hours)

```bash
npm install --save-dev @playwright/test playwright
```

**Configure:**
```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  use: {
    headless: false, // Show window during dev
  },
});
```

**Add npm scripts:**
- `test:e2e` - Run E2E tests
- `test:e2e:headed` - Run with visible window

**Deliverable:** Playwright configured for Electron

### Phase 7: Write E2E Test (3-4 hours)

Create 1+ E2E test for user workflow:

**Example - App Launch:**
```javascript
// tests/e2e/app-launch.spec.js
const { _electron: electron } = require('playwright');
const { test, expect } = require('@playwright/test');

test('launches configurator', async () => {
  const app = await electron.launch({ args: ['.'] });
  const window = await app.firstWindow();

  await expect(window).toHaveTitle('INAV Configurator');

  await app.close();
});
```

**Example - Tab Navigation:**
```javascript
// tests/e2e/navigation.spec.js
test('navigates between tabs', async () => {
  const app = await electron.launch({ args: ['.'] });
  const window = await app.firstWindow();

  // Click Setup tab
  await window.click('a[href="#tab-setup"]');
  await expect(window.locator('#tab-setup')).toBeVisible();

  // Click Configuration tab
  await window.click('a[href="#tab-configuration"]');
  await expect(window.locator('#tab-configuration')).toBeVisible();

  await app.close();
});
```

**Deliverable:** 1+ passing E2E test

### Phase 8: Documentation (1-2 hours)

Create `TESTING.md` with:
- Overview of test strategy (test pyramid)
- How to run tests (`npm test`, etc.)
- How to write unit tests
- How to write integration tests
- How to write E2E tests
- Mocking strategies
- Best practices
- CI/CD integration plan (GitHub Actions example)

**Deliverable:** Comprehensive testing guide

## Testing Best Practices

**Test Pyramid:**
- Many fast unit tests (70%)
- Some integration tests (20%)
- Few slow E2E tests (10%)

**Isolation:**
- Tests don't depend on each other
- Each test sets up and tears down cleanly
- Use mocks to avoid external dependencies

**Clarity:**
- Test names describe what they verify
- Use AAA pattern: Arrange, Act, Assert
- Keep tests simple and focused

**Maintainability:**
- Don't test implementation details
- Update tests when requirements change
- Keep tests DRY (Don't Repeat Yourself)

## Chrome DevTools Protocol (CDP)

**Note:** Playwright and Puppeteer both use CDP under the hood. You don't need to use CDP directly unless you need advanced features.

**CDP provides:**
- Network interception
- Performance profiling
- Custom automation
- Low-level browser control

**For most testing, Playwright's high-level API is sufficient.**

## Success Criteria

- [ ] Jest installed and configured
- [ ] Playwright installed and configured
- [ ] Mock infrastructure for MSP/serial
- [ ] 5+ unit tests passing
- [ ] 1+ integration test passing
- [ ] 1+ E2E test passing
- [ ] TESTING.md documentation created
- [ ] npm test scripts working
- [ ] Coverage reporting configured
- [ ] All tests green ✅

## Deliverables

1. **Testing Infrastructure:**
   - Jest configured for unit/integration tests
   - Playwright configured for E2E tests
   - Test directory structure
   - npm scripts

2. **Mock Layer:**
   - MSP mock implementation
   - Serial mock implementation
   - Test fixtures

3. **Sample Tests:**
   - 5+ unit tests
   - 1+ integration test
   - 1+ E2E test

4. **Documentation:**
   - TESTING.md guide
   - How to run tests
   - How to write tests
   - Mocking strategies

5. **Completion Report:**
   - Tools selected and rationale
   - Test coverage achieved
   - Challenges encountered
   - Recommendations for expanding test suite

## Estimated Time

- Research: 2-3 hours
- Jest setup + unit tests: 3-4 hours
- Playwright setup + E2E tests: 3-4 hours
- Integration tests: 2-3 hours
- Mocking infrastructure: 2-3 hours
- Documentation: 1-2 hours

**Total: 13-19 hours**

## Priority Justification

**Medium Priority:**
- Important for code quality and confidence
- Not urgent (no blocking issues)
- Foundational work for future development
- Will pay dividends over time
- Should be established before major refactoring

## Notes

- Transpiler already has Mocha-based tests in `js/transpiler/transpiler/tests/` - good reference
- Focus on establishing patterns, not comprehensive coverage
- Proof-of-concept to validate approach
- Can expand test suite incrementally after foundation is laid
- Consider developer experience (fast tests, clear output)

## Questions?

- Need guidance on tool selection? Research and document tradeoffs
- Unsure how to mock something? Document the challenge and propose approach
- Hit issues with Electron testing? Check Playwright Electron docs

## Resources

**Documentation:**
- Jest: https://jestjs.io/
- Playwright: https://playwright.dev/
- Playwright Electron: https://playwright.dev/docs/api/class-electron
- Chrome DevTools Protocol: https://chromedevtools.github.io/devtools-protocol/

**Examples:**
- Existing transpiler tests: `js/transpiler/transpiler/tests/`

---

**Manager**
