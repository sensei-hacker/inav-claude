# INAV Configurator Automated Testing with Playwright

## Overview

The INAV Configurator is an Electron application, which means it can be automated using Playwright's experimental Electron support. Playwright launches the app, interacts with the UI, and validates behavior - perfect for testing configurator changes before creating PRs.

## Current Status

**Testing Infrastructure:** None currently exists
**Playwright Version:** 1.57.0 (already installed)
**Framework:** Electron Forge + Vite

## Setup Requirements

### 1. Install Playwright Test Runner

```bash
cd inav-configurator
npm install --save-dev @playwright/test
```

### 2. Optional: Install Electron Helpers

```bash
npm install --save-dev electron-playwright-helpers
```

Provides utilities for:
- Clicking Electron menu items
- Sending IPC messages
- Stubbing dialogs
- Getting menu structures

## Basic Test Example

### Launch the Configurator

```javascript
// tests/basic.spec.js
const { _electron: electron } = require('playwright');
const { test, expect } = require('@playwright/test');

test('configurator launches successfully', async () => {
  // Launch the Electron app
  const electronApp = await electron.launch({
    args: ['.vite/build/main.js'],
    cwd: process.cwd(),
    timeout: 30000
  });

  // Wait for the first window
  const window = await electronApp.firstWindow();

  // Verify the window loaded
  const title = await window.title();
  expect(title).toContain('INAV');

  // Take a screenshot
  await window.screenshot({ path: 'screenshots/startup.png' });

  // Close the app
  await electronApp.close();
});
```

### Test Tab Navigation

```javascript
test('can navigate to Configuration tab', async () => {
  const electronApp = await electron.launch({
    args: ['.vite/build/main.js']
  });

  const window = await electronApp.firstWindow();

  // Wait for UI to load
  await window.waitForSelector('#tab-configuration');

  // Click the Configuration tab
  await window.click('#tab-configuration');

  // Verify tab content loaded
  const tabContent = await window.locator('.tab-configuration').isVisible();
  expect(tabContent).toBe(true);

  await electronApp.close();
});
```

### Test I2C Speed Warning Bug (MEDIUM Priority Task)

This is directly applicable to the I2C Speed Warning bug in the developer inbox:

```javascript
test('I2C speed warning validation', async () => {
  const electronApp = await electron.launch({
    args: ['.vite/build/main.js']
  });

  const window = await electronApp.firstWindow();

  // Navigate to Configuration tab
  await window.click('#tab-configuration');

  // Find the I2C speed input
  const i2cSpeedInput = await window.locator('input[name="i2cspeed"]');

  // Set to maximum value
  await i2cSpeedInput.fill('800');

  // Verify warning does NOT appear for valid max value
  const warning = await window.locator('.i2c-speed-warning');
  const isVisible = await warning.isVisible().catch(() => false);

  expect(isVisible).toBe(false);

  // Take screenshot of the configuration
  await window.screenshot({ path: 'screenshots/i2c-config.png' });

  await electronApp.close();
});
```

### Test Battery Current Limiter UI (Recently Completed)

```javascript
test('battery current limiter field validation', async () => {
  const electronApp = await electron.launch({
    args: ['.vite/build/main.js']
  });

  const window = await electronApp.firstWindow();

  // Navigate to Configuration/Battery tab
  await window.click('#tab-configuration');

  // Find the max battery current input
  const batteryCurrentInput = await window.locator('input[name="max_battery_current"]');

  // Verify field exists
  expect(await batteryCurrentInput.isVisible()).toBe(true);

  // Test range validation (0-200A)
  await batteryCurrentInput.fill('150');
  const value = await batteryCurrentInput.inputValue();
  expect(parseInt(value)).toBe(150);

  // Test invalid value
  await batteryCurrentInput.fill('250');
  // Should show validation error or clamp to max

  await electronApp.close();
});
```

## Running Tests

### Package the App First

Electron Forge requires building before testing:

```bash
cd inav-configurator
npm run package
```

### Run Playwright Tests

```bash
npx playwright test
```

### Run with UI Mode (Interactive)

```bash
npx playwright test --ui
```

### Run Specific Test

```bash
npx playwright test tests/battery.spec.js
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Configurator Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run package
      - run: npx playwright test
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-screenshots
          path: screenshots/
```

## Test Structure Recommendations

```
inav-configurator/
├── tests/
│   ├── setup/
│   │   └── electron-setup.js    # Common test setup
│   ├── tabs/
│   │   ├── configuration.spec.js
│   │   ├── battery.spec.js
│   │   ├── receiver.spec.js
│   │   └── motors.spec.js
│   ├── settings/
│   │   ├── cli-validation.spec.js
│   │   └── settings-import.spec.js
│   └── screenshots/             # Test screenshots
├── playwright.config.js          # Playwright configuration
└── package.json                  # Add test scripts
```

## Configuration File

```javascript
// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 60000,
  use: {
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'electron',
      testMatch: '**/*.spec.js',
    },
  ],
});
```

## Benefits for INAV Development

1. **Catch UI bugs before PR creation**
   - I2C speed warning validation
   - Battery limiter range checks
   - Tab navigation issues

2. **Regression testing**
   - Verify old bugs don't reappear
   - Test multiple configurator versions

3. **Screenshot comparison**
   - Visual regression testing
   - UI layout validation

4. **Automated smoke testing**
   - App launches successfully
   - All tabs load
   - Settings save/load correctly

## Practical Use Cases for Current Tasks

### I2C Speed Warning Bug
```javascript
// Verify the bug is fixed:
// 1. Launch configurator
// 2. Navigate to Configuration
// 3. Set I2C speed to 800 (maximum)
// 4. Assert warning does NOT show
// 5. Take screenshot as proof
```

### Future PR Testing
Before creating a PR:
```bash
npm run package
npx playwright test tests/my-feature.spec.js
```

## Limitations

1. **Requires build step** - Must run `npm run package` before tests
2. **Experimental** - Playwright Electron support is experimental
3. **Serial testing** - Can't safely run multiple Electron instances in parallel
4. **No mock flight controller** - Can't test actual FC communication (yet)

## Next Steps

1. Create `playwright.config.js`
2. Write basic smoke test (app launches)
3. Add tests for pending tasks:
   - I2C speed warning validation
   - Battery current limiter UI
4. Document test patterns in developer guide
5. Consider CI/CD integration

## References

- [Playwright Electron API](https://playwright.dev/docs/api/class-electron)
- [Electron Testing Guide](https://www.electronjs.org/docs/latest/tutorial/automated-testing)
- [electron-playwright-helpers](https://www.npmjs.com/package/electron-playwright-helpers)
- [Example: Multi-window Testing](https://github.com/spaceagetv/electron-playwright-example)
- [Actual Budget PR #4674](https://github.com/actualbudget/actual/pull/4674) - Real-world implementation

---

**Status:** Documentation only - no tests implemented yet
**Priority:** Useful for testing configurator changes (I2C bug, battery limiter, etc.)
**Effort:** ~2-4 hours to set up basic test infrastructure
