# Developer Testing Tools

Helper scripts and patches for testing the INAV Configurator.

## Quick Reference

### 1. Start Configurator with Remote Debugging

```bash
cd inav-configurator
./start-with-debugging.sh
```

Enables Chrome DevTools Protocol on port 9222 for:
- Chrome DevTools UI (`chrome://inspect`)
- Playwright CDP connections
- Claude MCP chrome-devtools integration

### 2. Run Playwright Startup Test

```bash
cd inav-configurator
npm run package  # Build first
node ../claude/developer/scripts/testing/test-configurator-startup.js
```

Launches configurator, validates title, takes screenshot.

### 3. Apply Remote Debugging Patch (Optional)

Makes remote debugging permanent in the code:

```bash
cd inav-configurator
patch -p1 < ../claude/developer/docs/debugging/add-remote-debugging.patch
```

Then use:
```bash
ENABLE_REMOTE_DEBUGGING=1 npm start
```

## Related Files

**Testing scripts:** `../scripts/testing/`
- **test-configurator-startup.js** - Playwright proof-of-concept test

**Debugging tools:** `../debugging/`
- **add-remote-debugging.patch** - Adds remote debugging to main.js

**Build scripts:** `../scripts/build/`
- **build-and-flash.sh** - Build and flash firmware to flight controller

## Documentation

- **configurator-automated-testing.md** - Full Playwright guide
- **configurator-debugging-setup.md** - Chrome DevTools Protocol setup
- **testing-approaches-summary.md** - Comparison of testing methods

## Environment Variables

**For Remote Debugging:**
- `ENABLE_REMOTE_DEBUGGING=1` - Enable debugging (if patch applied)
- `REMOTE_DEBUGGING_PORT=9222` - Custom port (default: 9222)
- `NODE_ENV=development` - Show debug output

**For Playwright:**
- `NODE_ENV=test` - Test mode (optional)
- `CI=1` - CI environment flag

## Common Workflows

### Test a UI Change

1. Make changes in `tabs/*.html` or `tabs/*.js`
2. Start with debugging: `./start-with-debugging.sh`
3. Test interactively with Chrome DevTools
4. OR: Build and run Playwright test

### Before Creating PR

1. Build: `npm run package`
2. Test: Run relevant Playwright tests
3. Review screenshots in `screenshots/`
4. Create PR with confidence

### Debug a Bug Report

1. Start with debugging: `./start-with-debugging.sh`
2. Open Chrome DevTools: `chrome://inspect`
3. Reproduce the bug
4. Inspect DOM, console, network
5. Fix and test

## Tips

- **No rebuild needed** for Chrome DevTools approach - works with `npm start`
- **Rebuild required** for Playwright tests - needs `npm run package`
- **Screenshots useful** for bug reports and PR documentation
- **MCP integration** allows Claude to test changes interactively

## See Also

- Main developer guide: `claude/developer/README.md`
- Skills: `.claude/skills/*/SKILL.md`
- Project tracking: `claude/projects/INDEX.md`
