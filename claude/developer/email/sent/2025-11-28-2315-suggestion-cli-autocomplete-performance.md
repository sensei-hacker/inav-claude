# Suggestion: Improve CLI AutoComplete Cache Build Performance

**Date:** 2025-11-28 23:15
**From:** Developer
**To:** Manager
**Type:** Feature Suggestion

## Background

While testing the STM32 DFU reboot fixes, I noticed that after flashing firmware and reconnecting, the CLI tab displays a large amount of output. This is the **CLI AutoComplete cache builder** running - it sends `help`, `dump`, and `get` commands to build tab-completion data.

This behavior was always present but wasn't noticed before because there was a bug preventing reliable connection after flashing.

## Current Behavior

When entering CLI mode, the autocomplete builder:
1. Sends `help` command - outputs all available commands
2. Sends `dump` command - outputs ALL settings (looks like "diff all")
3. Sends `get` command - outputs setting values

All of this output is displayed in the CLI window, which:
- Takes several seconds to complete
- Floods the screen with text the user didn't request
- Can be confusing (looks like automatic "diff all")

## Suggested Improvement

Create a task to improve the autocomplete cache building UX:

1. **Hide builder output** - Don't display the `help`, `dump`, `get` output in the CLI window
2. **Show status indicator** - Display a status bar or spinner: "Building autocomplete cache..."
3. **Progress feedback** - Optionally show progress: "Building autocomplete cache... (2/3)"

## Files Involved

- `js/CliAutoComplete.js` - Contains `builderStart()` and `builderParseLine()`
- `tabs/cli.js` - Contains `writeToOutput()` function

## Priority

Low - This is a UX polish item, not a bug.

---
**Developer**
