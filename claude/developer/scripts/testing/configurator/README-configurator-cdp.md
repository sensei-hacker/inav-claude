# Configurator CDP Testing Scripts

## Overview

Two scripts here cover Chrome DevTools Protocol (CDP) access to INAV Configurator:

- `configurator_cdp_test.py` - Comprehensive test script for verifying the CDP connection to INAV Configurator works.
- `cdp_eval.mjs` - Minimal zero-dependency helper that evaluates a single JS expression in the renderer and prints the JSON result.

## Purpose

Tests that the configurator's CDP debugging interface is working correctly. This is essential for:
- Automated UI testing
- Chrome DevTools integration
- MCP Chrome DevTools server functionality
- Interactive debugging

## Prerequisites

1. **Start INAV Configurator:**
   ```bash
   cd inav-configurator
   npm start
   ```

2. **Verify CDP is enabled:**
   - Automatically enabled in development mode (`npm start`)
   - Port 9222 must be available
   - Check with: `curl http://localhost:9222/json/version`

## Usage

```bash
python3 claude/developer/scripts/testing/configurator_cdp_test.py
```

## What It Tests

The script performs 5 comprehensive tests:

1. **Runtime.evaluate** - JavaScript execution
   - Gets page title
   - Verifies JS code can execute in configurator context

2. **Accessibility.getFullAXTree** - UI element tree
   - Captures all accessible elements
   - Counts nodes (should be 300+)
   - Used by MCP snapshot functionality

3. **Page.captureScreenshot** - Visual capture
   - Takes PNG screenshot
   - Verifies image generation
   - Used for visual regression testing

4. **DOM querying** - Element inspection
   - Finds connect button (`a.connect`)
   - Verifies DOM queries work
   - Used for UI automation

5. **Text extraction** - Content reading
   - Reads button text
   - Verifies text content access
   - Used for i18n testing

## cdp_eval.mjs — One-Shot Expression Evaluator

`cdp_eval.mjs` connects to a single CDP page target and evaluates one JS
expression in the renderer, printing the JSON result. It complements
`configurator_cdp_test.py` (which verifies the CDP *connection* is healthy) by
being the quick way to *drive* arbitrary JS in the running Configurator. It is
zero-dependency (uses Node's built-in `WebSocket`, Node 22+).

### Usage

```bash
node cdp_eval.mjs <webSocketDebuggerUrl> <expression | ->
# Pass `-` as the expression to read it from stdin.
```

Get the target URL first:

```bash
curl -s http://localhost:9222/json/list | jq -r '.[0].webSocketDebuggerUrl'
```

### Examples

```bash
WS_URL=$(curl -s http://localhost:9222/json/list | jq -r '.[0].webSocketDebuggerUrl')

# Inspect renderer state
node cdp_eval.mjs "$WS_URL" "document.title"

# Read a longer expression from stdin
echo "import('/js/msp.js').then(m => m.MSP.promise(1,1))" | node cdp_eval.mjs "$WS_URL" -
```

The expression is evaluated with `awaitPromise: true`, `returnByValue: true`,
and `userGesture: true`, so async results are awaited and resolved to plain
JSON. Exit codes: `0` success, `1` CDP error / renderer exception / 20s
timeout, `2` usage error.

### When to Use

Use `cdp_eval.mjs` when you need a one-shot `Runtime.evaluate` in a live
Configurator — state inspection, poisoning globals, or observing async promise
settlement (e.g. reproducing the `MSP.promise()` hang: poison
`MSP.parseFailures` and watch the promise never settle vs reject after a fix).

For driving the full UI (clicking tabs, screenshots, DOM queries), use
`tab_sweep_cdp.py` or the Chrome DevTools MCP instead.

## Expected Output

```
============================================================
Chrome DevTools Protocol Connection Test
============================================================

✓ Found INAV Configurator (ID: ...)
✓ WebSocket connected

✓ Runtime.evaluate: Page title = 'INAV Configurator'
✓ Accessibility.getFullAXTree: 353 nodes
✓ Page.captureScreenshot: 253536 chars (base64)
✓ DOM query: Connect button exists = True
✓ Get element text: Connect button text = 'Connect'

============================================================
Results: 5/5 tests passed
============================================================

✅ SUCCESS: CDP connection fully functional!
```

## Troubleshooting

### Port 9222 Not Listening

**Problem:** `Connection refused`

**Solution:**
```bash
# Check if configurator is running
ps aux | grep electron

# Restart configurator
cd inav-configurator && npm start
```

### Wrong Page Found

**Problem:** "INAV Configurator page not found"

**Solutions:**
1. Wait 2-3 seconds after launch for page to load
2. Check available pages:
   ```bash
   curl -s http://localhost:9222/json/list | jq '.[] | .title'
   ```
3. Verify configurator loaded (should show landing page)

### WebSocket Connection Failed

**Problem:** WebSocket fails to connect

**Solutions:**
1. Check firewall rules (port 9222 must be open)
2. Verify CDP endpoint responds:
   ```bash
   curl http://localhost:9222/json/version
   ```
3. Restart configurator if needed

### Tests Pass But MCP Tools Don't Work

**Note:** This script tests the underlying CDP connection. If this passes but MCP tools fail, the issue is with MCP configuration, not CDP itself.

**Check:**
1. `.mcp.json` exists in workspace root
2. MCP server configured: `@modelcontextprotocol/server-chrome-devtools`
3. Claude session was started with configurator running
4. Agent vs interactive session (MCP may not load in agents)

## Integration with MCP

This script verifies the same functionality used by MCP Chrome DevTools tools:

| MCP Tool | CDP Method Tested |
|----------|------------------|
| `mcp__chrome-devtools__evaluate_script` | Runtime.evaluate |
| `mcp__chrome-devtools__take_snapshot` | Accessibility.getFullAXTree |
| `mcp__chrome-devtools__take_screenshot` | Page.captureScreenshot |
| `mcp__chrome-devtools__click` | Runtime.evaluate + DOM query |

If this script passes, the CDP layer is working. MCP provides a higher-level abstraction over these same APIs.

## Use Cases

**Before PR:** Verify configurator debugging works
```bash
cd inav-configurator && npm start
# Wait 3 seconds
python3 claude/developer/scripts/testing/configurator_cdp_test.py
```

**After configurator changes:** Ensure CDP still works
```bash
# After modifying main.js or startup code
npm start
python3 claude/developer/scripts/testing/configurator_cdp_test.py
```

**CI/CD validation:** Automated check
```bash
# In GitHub Actions or local automation
npm start &
sleep 5
python3 claude/developer/scripts/testing/configurator_cdp_test.py
```

## Related Documentation

- `claude/developer/docs/testing/chrome-devtools-mcp.md` - MCP usage guide
- `.claude/skills/test-configurator/SKILL.md` - Test configurator skill
- `claude/developer/docs/testing/configurator-debugging-setup.md` - CDP setup details

## Notes

- Test requires `websockets` Python package (`pip install websockets`)
- Configurator must be running in dev mode (`npm start`)
- Production builds have CDP disabled for security
- Script is non-destructive (read-only operations)

---

**Created:** 2026-01-27
**Status:** ✅ Verified working
**CDP Endpoint:** http://localhost:9222
**Configurator:** INAV Configurator 9.0.0
