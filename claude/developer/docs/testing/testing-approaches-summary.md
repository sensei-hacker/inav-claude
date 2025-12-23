# INAV Configurator - Automated Testing Approaches

## Overview

Three main approaches for automated testing of the INAV Configurator (Electron app):

1. **Playwright Electron API** (Recommended)
2. **Chrome DevTools Protocol (CDP) via MCP**
3. **Manual CDP with Remote Debugging**

---

## Approach 1: Playwright Electron API ⭐ RECOMMENDED

### Status
✅ Playwright 1.57.0 already installed
✅ Chromium browsers available
✅ Documentation created

### Advantages
- **Native Electron support** - Designed specifically for Electron apps
- **Full test framework** - Includes assertions, screenshots, video recording
- **Active development** - Playwright is actively maintained by Microsoft
- **CI/CD ready** - Easy GitHub Actions integration
- **Helper libraries** - `electron-playwright-helpers` for menu clicks, IPC, etc.

### How It Works
```javascript
const { _electron: electron } = require('playwright');

const electronApp = await electron.launch({
  args: ['.vite/build/main.js']
});

const window = await electronApp.firstWindow();
await window.click('#tab-configuration');
await window.screenshot({ path: 'test.png' });
await electronApp.close();
```

### Use Cases
- ✅ Full end-to-end testing
- ✅ UI regression testing
- ✅ Automated PR validation
- ✅ CI/CD integration

### Setup Steps
1. Install: `npm install --save-dev @playwright/test`
2. Build app: `npm run package`
3. Write tests in `tests/` directory
4. Run: `npx playwright test`

### Limitations
- Requires build step (`npm run package`) before tests
- Experimental Electron support
- Can't run multiple instances in parallel safely

**Files Created:**
- `claude/developer/docs/configurator-automated-testing.md` (comprehensive guide)
- `claude/developer/helpers/test-configurator-startup.js` (proof-of-concept)

---

## Approach 2: Chrome DevTools Protocol (CDP) via MCP ⭐ VERIFIED WORKING

### Status
✅ chrome-devtools-mcp installed and verified (2025-12-18)
✅ Works with `npm start` (remote debugging auto-enabled in dev mode)

### Advantages
- **Real-time interaction** - Connect to running app
- **No build required** - Works with `npm start` (dev mode)
- **Full CDP access** - All Chrome DevTools features
- **Claude integration** - Direct MCP tool access
- **Debugging friendly** - Same protocol as Chrome DevTools
- **Efficient** - Snapshots provide clear HTML structure without visual rendering

### How It Works
1. Launch configurator in dev mode (remote debugging auto-enabled):
   ```bash
   cd inav-configurator
   npm start  # Port 9222 automatically enabled
   ```

2. Claude can connect via MCP to:
   - Capture accessibility tree snapshots (PREFERRED - clear HTML with IDs)
   - Execute JavaScript in browser context
   - Query and interact with DOM elements
   - Monitor console and network
   - Capture visual screenshots (only for CSS/layout validation)
   - Debug issues in real-time

**IMPORTANT:** Prefer `take_snapshot` over `take_screenshot`. The Configurator's HTML is well-structured:
```html
<div id="port-picker">
    <div class="connect_controls" id="connectbutton">
        <a class="connect" href="#"></a>
    </div>
```
Clear element IDs make screenshots unnecessary for 90% of testing.

### Use Cases
- ✅ Interactive testing during development
- ✅ Real-time debugging
- ✅ Quick validation without builds
- ✅ DOM inspection and manipulation
- ❌ Not ideal for CI/CD (requires manual start)

### Setup Steps
1. ✅ MCP already installed: `claude mcp add chrome-devtools npx chrome-devtools-mcp@latest`
2. Start configurator: `cd inav-configurator && npm start` (debugging auto-enabled)
3. Use MCP tools to interact (prefer `take_snapshot` over `take_screenshot`)

### Limitations
- Not fully automated (requires Claude to drive tests interactively)
- Less suitable for CI/CD pipelines (better for interactive development testing)

---

## Approach 3: Manual CDP with Remote Debugging

### Status
🔄 Available but not tested yet
⚠️ Electron Forge doesn't support `--remote-debugging-port` flag directly

### Advantages
- **No dependencies** - Uses built-in Electron features
- **Browser DevTools UI** - Can open chrome://inspect
- **Network monitoring** - See all requests/responses

### How It Works
Start Electron with debugging port:
```bash
# May need to bypass electron-forge
electron .vite/build/main.js --remote-debugging-port=9222
```

Then connect:
- Chrome DevTools: `chrome://inspect`
- Playwright CDP: `playwright.chromium.connectOverCDP('http://localhost:9222')`
- curl: `curl http://localhost:9222/json/version`

### Use Cases
- ✅ Manual debugging
- ✅ One-off investigations
- ❌ Not for automated testing

### Limitations
- Electron Forge doesn't pass flags cleanly
- Manual process
- Not automated

---

## Comparison Matrix

| Feature | Playwright | CDP via MCP | Manual CDP |
|---------|-----------|-------------|------------|
| **Automation** | ✅ Full | ⚠️ Semi | ❌ Manual |
| **CI/CD Ready** | ✅ Yes | ❌ No | ❌ No |
| **Build Required** | ✅ Yes | ❌ No | ⚠️ Varies |
| **Real-time Debug** | ⚠️ Limited | ✅ Yes | ✅ Yes |
| **Test Framework** | ✅ Included | ❌ N/A | ❌ N/A |
| **Screenshots** | ✅ Easy | ✅ Possible | ✅ Possible |
| **DOM Interaction** | ✅ Full | ✅ Full | ✅ Full |
| **IPC Testing** | ✅ Via helpers | ⚠️ Complex | ⚠️ Complex |
| **Setup Complexity** | ⭐⭐ Medium | ⭐ Easy | ⭐⭐⭐ Hard |

---

## Recommended Workflow

### For Development (Interactive Testing)
**Use CDP via MCP:**
1. Start configurator: `npm start`
2. Connect via MCP (if port can be exposed)
3. Test changes interactively
4. Quick validation without rebuilds

### For PR Creation (Automated Testing)
**Use Playwright:**
1. Write test: `tests/my-feature.spec.js`
2. Build: `npm run package`
3. Test: `npx playwright test`
4. Review screenshots/videos
5. Create PR with confidence

### For CI/CD (Regression Testing)
**Use Playwright:**
```yaml
# .github/workflows/configurator-tests.yml
- run: npm run package
- run: npx playwright test
- uses: actions/upload-artifact@v3
  with:
    name: test-results
```

---

## Practical Examples for Current Tasks

### I2C Speed Warning Bug (MEDIUM Priority)

**Playwright Test:**
```javascript
test('I2C speed warning at max value', async () => {
  const app = await electron.launch({ args: ['.vite/build/main.js'] });
  const win = await app.firstWindow();

  await win.click('#tab-configuration');
  await win.fill('input[name="i2cspeed"]', '800');

  const warning = await win.locator('.i2c-speed-warning').isVisible();
  expect(warning).toBe(false); // Should NOT show warning at max

  await app.close();
});
```

**CDP via MCP (✅ VERIFIED WORKING):**
```
1. Start configurator: npm start
2. Ask Claude: "Take a snapshot and check if I2C speed warning appears when set to 800"
3. Claude uses MCP to:
   - Take snapshot of current page (shows clear HTML with IDs)
   - Navigate to Configuration tab if needed
   - Set I2C speed to 800 (via fill or evaluate_script)
   - Take another snapshot to check for warning element
   - Report results (no screenshot needed - HTML is clear)
```

### Battery Current Limiter UI (Recently Completed)

**Playwright Test:**
```javascript
test('battery current limiter field exists', async () => {
  const app = await electron.launch({ args: ['.vite/build/main.js'] });
  const win = await app.firstWindow();

  await win.click('#tab-configuration');
  const field = await win.locator('input[name="max_battery_current"]');

  expect(await field.isVisible()).toBe(true);
  await field.fill('150');
  expect(await field.inputValue()).toBe('150');

  await app.close();
});
```

---

## Next Steps

### Short Term (1-2 hours)
1. ✅ Documentation created
2. ✅ Test CDP via MCP - Verified working (2025-12-18)
3. ⬜ Run proof-of-concept Playwright test
4. ✅ Verify snapshot capture works (preferred over screenshots)

### Medium Term (2-4 hours)
1. ⬜ Create `playwright.config.js`
2. ⬜ Write tests for I2C speed warning bug
3. ⬜ Write tests for battery current limiter
4. ⬜ Add test script to package.json

### Long Term (8+ hours)
1. ⬜ Full test suite for all tabs
2. ⬜ CI/CD GitHub Actions integration
3. ⬜ Visual regression testing
4. ⬜ Settings import/export tests

---

## Resources

**Playwright Electron:**
- [Playwright Electron API](https://playwright.dev/docs/api/class-electron)
- [Electron Testing Guide](https://www.electronjs.org/docs/latest/tutorial/automated-testing)
- [electron-playwright-helpers](https://www.npmjs.com/package/electron-playwright-helpers)
- [Multi-window Example](https://github.com/spaceagetv/electron-playwright-example)

**Chrome DevTools Protocol:**
- [CDP Documentation](https://chromedevtools.github.io/devtools-protocol/)
- [Electron Debugging](https://www.electronjs.org/docs/latest/tutorial/debugging-main-process)

**Real-World Examples:**
- [Actual Budget PR #4674](https://github.com/actualbudget/actual/pull/4674) - Playwright implementation
- [Testing Electron Apps with Playwright](https://dev.to/kubeshop/testing-electron-apps-with-playwright-3f89)

---

**Created:** 2025-12-18
**Status:** Documentation and proof-of-concept complete
**Priority:** High value for developer workflow and PR quality
