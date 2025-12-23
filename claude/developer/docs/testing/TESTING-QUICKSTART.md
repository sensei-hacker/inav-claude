# INAV Configurator Testing - Quick Start Guide

## TL;DR - Three Ways to Test

### 🚀 Option 1: Interactive Testing (No Build Required)

**Best for:** Testing changes during development

```bash
cd inav-configurator
./start-with-debugging.sh

# Then in another terminal:
curl http://localhost:9222/json/version  # Verify connection

# Or open Chrome:
# chrome://inspect → Click "inspect" on INAV Configurator
```

**What you get:**
- Real-time DOM inspection
- JavaScript console
- Network monitoring
- No rebuild needed!

---

### 🤖 Option 2: Automated Testing with Playwright

**Best for:** PR validation, regression testing, CI/CD

```bash
cd inav-configurator

# First time setup:
npm install --save-dev @playwright/test

# Every test run:
npm run package  # Build the app
node ../claude/developer/helpers/test-configurator-startup.js

# Or run full test suite:
npx playwright test
```

**What you get:**
- Automated test execution
- Screenshots on failure
- Video recording
- CI/CD integration

---

### 🎨 Option 3: Claude MCP Integration

**Best for:** Asking Claude to test things for you

**Status:** ✅ Verified working (tested 2025-12-18)

```bash
cd inav-configurator
npm start  # Remote debugging auto-enabled in dev mode

# Then ask Claude:
# "Take a snapshot of the configurator"
# "Take a screenshot of the configurator"
# "What tabs are visible?"
# "Check if the I2C speed warning is visible"
# "Click the Configuration tab and tell me what you see"
# "Fill the baud rate selector with 57600"
```

**What you get:**
- Claude can interact with the UI directly via Chrome DevTools Protocol
- Access to 20+ MCP tools (click, fill, navigate, snapshot, evaluate JS)
- No coding required
- Great for exploratory testing and interactive debugging
- Full accessibility tree inspection
- Real-time UI state validation

**Verified Capabilities:**
- List pages and elements
- Capture accessibility tree snapshots (PREFERRED - use this instead of screenshots)
- Click buttons and links
- Fill form inputs
- Execute JavaScript
- Navigate pages
- Monitor console and network
- Take visual screenshots (only for CSS/layout validation)

**IMPORTANT: Prefer Snapshots over Screenshots**

The Configurator has well-structured HTML with clear IDs and semantic markup. For example:
```html
<div id="port-picker">
    <div class="connect_controls" id="connectbutton">
        <a class="connect" href="#"></a>
        <a class="connect_state" data-i18n="connect"></a>
    </div>
```
This is clearly the connect button - a snapshot provides all needed info without visual rendering overhead.

**When to use each:**
- **Snapshot (90%)**: Element existence, UI state, form values, navigation
- **Screenshot (10%)**: Visual bugs, CSS issues, layout problems

---

## Files and Documentation

### 📁 Quick Access

```
claude/developer/
├── docs/
│   ├── configurator-automated-testing.md      # Full Playwright guide
│   ├── configurator-debugging-setup.md        # Chrome DevTools setup
│   └── testing-approaches-summary.md          # Comparison of methods
├── helpers/
│   ├── test-configurator-startup.js           # Playwright test
│   ├── add-remote-debugging.patch             # Optional code patch
│   └── README-testing-tools.md                # Helper tools guide
└── TESTING-QUICKSTART.md                       # This file

inav-configurator/
└── start-with-debugging.sh                     # Launch with debugging
```

### 📚 Which Doc Should I Read?

- **"How do I test this change?"** → This file (you're here!)
- **"How do I write Playwright tests?"** → `configurator-automated-testing.md`
- **"How do I enable remote debugging?"** → `configurator-debugging-setup.md`
- **"Which testing approach should I use?"** → `testing-approaches-summary.md`

---

## Practical Examples for Current Tasks

### I2C Speed Warning Bug

**Interactive approach:**
```bash
./start-with-debugging.sh
# Open chrome://inspect
# Navigate to Configuration tab
# Set I2C speed to 800 (maximum)
# Verify warning does NOT appear
```

**Playwright approach:**
```javascript
test('I2C speed warning at max value', async () => {
  const app = await electron.launch({ args: ['.vite/build/main.js'] });
  const win = await app.firstWindow();
  await win.click('#tab-configuration');
  await win.fill('input[name="i2cspeed"]', '800');

  const warning = await win.locator('.i2c-speed-warning').isVisible();
  expect(warning).toBe(false);

  await app.close();
});
```

**Claude MCP approach:**
```bash
npm start
# Then: "Claude, take a snapshot and check if I2C speed warning appears when set to 800"
# No screenshot needed - the HTML structure is clear
```

### Battery Current Limiter UI

**Verify the field exists:**
```bash
./start-with-debugging.sh
# Open chrome://inspect
# Navigate to Configuration tab
# Find input[name="max_battery_current"]
# Test values 0-200A
```

---

## Before Creating a PR

### Checklist

1. **Make your changes** in configurator code
2. **Test interactively** with `./start-with-debugging.sh`
3. **Verify with Playwright** (optional but recommended):
   ```bash
   npm run package
   npx playwright test  # Or specific test
   ```
4. **Review screenshots** in `screenshots/` directory
5. **Create PR** with confidence!

### Why This Matters

- Catches bugs before PR review
- Provides proof the feature works (screenshots)
- Prevents "it works on my machine" issues
- Makes reviewers happy 😊

---

## Installation (One-Time Setup)

### Playwright (for automated testing)

```bash
cd inav-configurator
npm install --save-dev @playwright/test
npm install --save-dev electron-playwright-helpers  # Optional
```

### Chrome DevTools MCP (for Claude integration)

Already installed! Just start configurator with debugging enabled.

### Remote Debugging Patch (optional)

Makes debugging permanently available via environment variable:

```bash
cd inav-configurator
patch -p1 < ../claude/developer/helpers/add-remote-debugging.patch

# Then use:
ENABLE_REMOTE_DEBUGGING=1 npm start
```

---

## Troubleshooting

### "Port 9222 already in use"

```bash
pkill -f remote-debugging-port
# Or:
lsof -i :9222  # Find the process
kill <PID>
```

### "No remote target in chrome://inspect"

1. Wait 2-3 seconds after launching
2. Click "Configure" in chrome://inspect
3. Add `localhost:9222` manually

### "npm run package fails"

Check that all dependencies are installed:
```bash
npm install
```

### "Playwright can't find electron"

Make sure you built the app first:
```bash
npm run package
ls -la .vite/build/main.js  # Should exist
```

---

## System Status

✅ **Playwright 1.57.0** - Installed
✅ **chrome-devtools-mcp** - Configured and verified working (2025-12-18)
✅ **Chromium browsers** - Available
✅ **Documentation** - Complete
✅ **Test scripts** - Ready
✅ **Startup script** - Created
✅ **MCP Integration** - 20+ tools verified operational

---

## Next Steps

### Immediate (Try it now!)

```bash
cd inav-configurator
./start-with-debugging.sh
```

Then open `chrome://inspect` and explore!

### Short Term (1-2 hours)

1. Write a test for the I2C speed warning bug
2. Test the battery current limiter UI
3. Take screenshots for documentation

### Long Term (4-8 hours)

1. Create test suite for all tabs
2. Add GitHub Actions CI integration
3. Document testing patterns for future contributors

---

## Benefits

**For You:**
- Catch bugs before review
- Faster development cycle
- More confidence in changes

**For the Project:**
- Fewer bugs reach production
- Better code quality
- Easier for new contributors

**For PRs:**
- Faster review process
- Visual proof of functionality
- Reduced back-and-forth

---

**Questions?** See the full documentation in `claude/developer/docs/`

**Ready to test?** Run `./start-with-debugging.sh` and explore!
