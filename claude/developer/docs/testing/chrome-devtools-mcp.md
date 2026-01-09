# Using Chrome DevTools MCP Server for Testing INAV Configurator

This document explains how to use the Chrome DevTools MCP server to test the INAV Configurator UI.

**See also:** `.claude/skills/test-configurator/SKILL.md` for the test-configurator skill.

## Connecting to Flight Controller

**CRITICAL: The connect button requires JavaScript execution, NOT the MCP click tool.**

### ❌ WRONG - Using the MCP click tool

```javascript
// This does NOT work reliably:
mcp__chrome-devtools__click({ uid: "SOME_UID" })
```

The MCP click tool frequently fails with the connect button because the button's behavior is entirely JavaScript-driven.

### ✅ CORRECT - Using evaluate_script

```javascript
mcp__chrome-devtools__evaluate_script({
  function: `() => {
    const connectLink = document.querySelector('a.connect');
    if (connectLink) {
      connectLink.click();
      return { clicked: true };
    }
    return { clicked: false };
  }`
})
```

**Then wait for connection:**

```javascript
mcp__chrome-devtools__wait_for({
  text: "Disconnect",
  timeout: 8000
})
```

## Complete Workflow Example

```javascript
// 1. Reload page (optional)
mcp__chrome-devtools__navigate_page({
  type: "reload",
  ignoreCache: true
})

// 2. Connect to FC using evaluate_script (NOT click tool)
mcp__chrome-devtools__evaluate_script({
  function: `() => {
    const connectLink = document.querySelector('a.connect');
    if (connectLink) {
      connectLink.click();
      return { clicked: true };
    }
    return { clicked: false };
  }`
})

// 3. Wait for connection to complete
mcp__chrome-devtools__wait_for({
  text: "Disconnect",
  timeout: 8000
})

// 4. Take snapshot to get fresh UIDs
mcp__chrome-devtools__take_snapshot()

// 5. Navigate to tab (using UID from fresh snapshot)
mcp__chrome-devtools__click({
  uid: "TAB_UID_FROM_SNAPSHOT"
})

// 6. Take screenshot to verify
mcp__chrome-devtools__take_screenshot()
```

## Key Points

1. **Always use `evaluate_script`** with `document.querySelector('a.connect').click()` to connect
2. **Never use the MCP click tool** for the connect button - it doesn't work reliably
3. **Always wait** for "Disconnect" text to appear before proceeding
4. **Always take fresh snapshot** after any page state change to get valid UIDs
5. **UIDs become stale** after page changes - always get fresh snapshot before clicking

## Why This Matters

The connect button in INAV Configurator is implemented as a JavaScript event handler attached to an `<a>` element with class `connect`. The MCP click tool simulates a browser click event, but the configurator's JavaScript doesn't always respond to simulated clicks. Using `evaluate_script` to call `.click()` directly on the DOM element bypasses this issue and works reliably every time.

## Checking i18n Text Display

To verify internationalized text is displaying:

```javascript
mcp__chrome-devtools__evaluate_script({
  function: `() => {
    const introParagraphs = document.querySelectorAll('.note p[i18n], .note p[data-i18n]');
    return {
      count: introParagraphs.length,
      paragraphs: Array.from(introParagraphs).map(p => ({
        i18nKey: p.getAttribute('i18n') || p.getAttribute('data-i18n'),
        textContent: p.textContent,
        hasText: p.textContent.length > 0
      }))
    };
  }`
})
```

This returns information about all elements with i18n keys and whether they have text content.
