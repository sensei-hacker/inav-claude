# Enabling Chrome DevTools Protocol for INAV Configurator

## Quick Start

The INAV Configurator can be launched with Chrome DevTools Protocol (CDP) enabled, allowing:
- Real-time debugging with Chrome DevTools
- Automated testing via Playwright CDP
- Claude MCP chrome-devtools integration
- DOM inspection and JavaScript execution

## Method 1: Simple Startup Script ⭐ EASIEST

Use the provided startup script:

```bash
cd inav-configurator
./start-with-debugging.sh
```

This sets the required environment variables and launches with debugging on port 9222.

## Method 2: Manual Environment Variables

Set environment variables before starting:

```bash
cd inav-configurator
export ELECTRON_ENABLE_LOGGING=1
export ELECTRON_REMOTE_DEBUGGING_PORT=9222
NODE_ENV=development npm start -- --remote-debugging-port=9222
```

## Method 3: Modify main.js (Permanent)

Add remote debugging support directly in `js/main/main.js`:

```javascript
// After the existing app.commandLine.appendSwitch calls (around line 36)

// Enable remote debugging when ENABLE_REMOTE_DEBUGGING is set
if (process.env.ENABLE_REMOTE_DEBUGGING === '1') {
  const port = process.env.REMOTE_DEBUGGING_PORT || '9222';
  app.commandLine.appendSwitch('remote-debugging-port', port);
  console.log(`Remote debugging enabled on port ${port}`);
  console.log(`Chrome DevTools: chrome://inspect`);
  console.log(`CDP Endpoint: http://localhost:${port}`);
}
```

Then start with:
```bash
ENABLE_REMOTE_DEBUGGING=1 npm start
```

## Verifying Connection

Once the configurator is running with debugging enabled:

### Test with curl
```bash
curl http://localhost:9222/json/version
```

Expected output:
```json
{
  "Browser": "Chrome/xxx",
  "Protocol-Version": "1.3",
  "User-Agent": "...",
  "V8-Version": "...",
  "WebKit-Version": "...",
  "webSocketDebuggerUrl": "ws://localhost:9222/devtools/..."
}
```

### Connect with Chrome DevTools
1. Open Chrome browser
2. Navigate to `chrome://inspect`
3. Look for "Remote Target" section
4. Click "inspect" next to the INAV Configurator window

### Use with Playwright CDP
```javascript
const { chromium } = require('playwright');

const browser = await chromium.connectOverCDP('http://localhost:9222');
const contexts = browser.contexts();
const page = contexts[0].pages()[0]; // Get the configurator window

// Now you can interact with it
await page.screenshot({ path: 'configurator.png' });
await page.click('#tab-configuration');
```

## Using with Chrome DevTools MCP

The chrome-devtools-mcp was installed with:
```bash
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

**To use it:**
1. Start configurator with debugging: `./start-with-debugging.sh`
2. The MCP should auto-detect on port 9222
3. Ask Claude to interact with the configurator via MCP

**Example Claude commands:**
- "Take a screenshot of the configurator"
- "Check if the I2C speed warning appears when set to 800"
- "Navigate to the Configuration tab and get the battery current limiter value"
- "Execute JavaScript to read all tab names"

## Troubleshooting

### Port already in use
```bash
# Find process using port 9222
lsof -i :9222

# Kill it if needed
pkill -f remote-debugging-port=9222
```

### Connection refused
- Verify the configurator started successfully
- Check that debugging port is in the command line:
  ```bash
  ps aux | grep electron | grep remote-debugging
  ```

### No remote target in chrome://inspect
- Wait 2-3 seconds after launch
- Click "Configure" in chrome://inspect
- Add `localhost:9222` if not listed

### Electron Forge doesn't pass flags
The `npm start -- --remote-debugging-port=9222` syntax may not work with Electron Forge. In that case:
1. Use Method 3 (modify main.js)
2. Or use environment variable `ELECTRON_REMOTE_DEBUGGING_PORT=9222`

## Current Configuration

**Location:** `inav-configurator/js/main/main.js`

**Existing command line switches:**
```javascript
app.commandLine.appendSwitch('disable-features', 'OutOfBlinkCors');
app.commandLine.appendSwitch("enable-experimental-web-platform-features", true);
app.commandLine.appendSwitch("enable-web-bluetooth", true);
```

**Recommended addition:**
```javascript
// Enable remote debugging for testing/development
if (process.env.ENABLE_REMOTE_DEBUGGING === '1') {
  const port = process.env.REMOTE_DEBUGGING_PORT || '9222';
  app.commandLine.appendSwitch('remote-debugging-port', port);
  if (process.env.NODE_ENV === 'development') {
    console.log(`🔍 Remote debugging enabled on port ${port}`);
    console.log(`   Chrome DevTools: chrome://inspect`);
    console.log(`   CDP Endpoint: http://localhost:${port}`);
  }
}
```

## Use Cases

### Interactive Testing During Development
1. Start with debugging: `./start-with-debugging.sh`
2. Make code changes
3. Use Chrome DevTools to test changes live
4. No rebuild required

### Automated Testing with Playwright
```javascript
const { chromium } = require('playwright');

async function testConfiguratorLive() {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const page = browser.contexts()[0].pages()[0];

  // Test navigation
  await page.click('#tab-configuration');

  // Test I2C speed warning
  await page.fill('input[name="i2cspeed"]', '800');
  const warning = await page.locator('.i2c-speed-warning').isVisible();
  console.log('Warning visible:', warning);

  await browser.close();
}
```

### Claude MCP Integration
With the chrome-devtools MCP installed, Claude can:
- Inspect DOM elements
- Execute JavaScript
- Capture screenshots
- Monitor network traffic
- Test UI interactions

**No build required** - works with `npm start` in development mode!

## Comparison: CDP vs Full Playwright

| Feature | CDP (Live) | Playwright (Built) |
|---------|-----------|-------------------|
| **Build Required** | ❌ No | ✅ Yes |
| **Restart Required** | ⚠️ For code changes | ✅ Clean start |
| **Test Framework** | ❌ Manual | ✅ Included |
| **Real-time Debug** | ✅ Yes | ⚠️ Limited |
| **CI/CD Ready** | ❌ No | ✅ Yes |
| **Use Case** | Development | Testing |

## Files Created

- `inav-configurator/start-with-debugging.sh` - Startup script with debugging enabled
- `claude/developer/docs/configurator-debugging-setup.md` - This documentation

## Next Steps

1. **Try it out:**
   ```bash
   cd inav-configurator
   ./start-with-debugging.sh
   curl http://localhost:9222/json/version
   ```

2. **Test with Chrome DevTools:**
   - Open `chrome://inspect`
   - Click "inspect" on the configurator

3. **Test with Claude MCP:**
   - Ask Claude to interact with the running configurator
   - Try: "Take a screenshot" or "What tabs are visible?"

4. **Optional: Make permanent** by adding the code snippet to `main.js`

---

**Status:** Ready to use
**Priority:** High value for development workflow
**MCP:** chrome-devtools-mcp installed and configured
