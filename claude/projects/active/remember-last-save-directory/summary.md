# Project: Remember Last Save Directory

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** UX Enhancement
**Created:** 2025-12-29
**Estimated Effort:** 2-4 hours

## Overview

Implement persistent "last used directory" for all file save dialogs in inav-configurator. Save dialogs should default to the last directory the user used.

## Problem

**Current behavior frustrates users:**
- Save dialogs always default to system directory (Documents, Downloads)
- Users must navigate to their preferred location every time
- Very tedious when saving multiple files (blackbox logs, diffs, etc.)

**Common scenarios:**
- Saving multiple blackbox logs from same flight session
- Saving CLI diffs for troubleshooting
- Exporting configuration files

Users have to repeatedly navigate to the same directory.

## Solution

**Remember the last save directory** across all save operations:
- Store in application settings/localStorage
- Persist across app restarts
- Update automatically after each save

## Objectives

1. Find all file save dialog locations in configurator
2. Store last save directory in persistent storage
3. Use stored directory as default for save dialogs
4. Handle edge cases (deleted directory, first use)
5. Test on all platforms

## Scope

**In Scope:**
- All save dialogs in configurator
- Blackbox log saves
- CLI diff/dump saves
- Configuration exports
- Any other file save operations
- Persistent storage across restarts
- Cross-platform compatibility

**Out of Scope:**
- Per-file-type directories (future enhancement)
- Reset/clear option (can add later)
- Open file dialogs (separate feature)

## Implementation Approach

**Simple global approach:**
1. Single `lastSaveDirectory` setting for all saves
2. Use Electron's `defaultPath` option
3. Store in existing settings mechanism
4. Validate directory exists before using
5. Fall back to system default if needed

**Technology:**
- Electron `dialog.showSaveDialog()` API
- Node.js `path` module for cross-platform paths
- Existing ConfigStorage or similar mechanism

## Success Criteria

- [ ] All save dialog locations identified
- [ ] Last directory stored persistently
- [ ] Save dialogs use last directory as default
- [ ] Handles non-existent directory gracefully
- [ ] Works on first use (no saved directory)
- [ ] Persists across app restarts
- [ ] Tested on Windows, macOS, Linux
- [ ] No errors or crashes

## Files to Investigate

**Find save dialogs:**
- Blackbox tab (blackbox log saving)
- CLI tab (diff/dump saving)
- Configuration backup/export
- Any other save operations

**Storage mechanism:**
- Check existing persistent settings code
- Use same pattern for consistency

## Expected Deliverables

1. Code changes to all save dialogs
2. Helper functions for get/set last directory
3. Testing on all platforms
4. PR with implementation

## Priority Justification

MEDIUM priority because:
- Improves user experience significantly
- Addresses common frustration
- Quick win (2-4 hours)
- Low risk, high value
- However: Not critical, not blocking

## Notes

**Keep it simple:**
- Start with single global directory
- Can enhance to per-type later if users want it
- Don't over-engineer first version

**Cross-platform:**
- Must work on Windows, macOS, Linux
- Use `path` module for compatibility
- Test on all platforms

**Backwards compatible:**
- No saved directory on first use → system default
- Existing users won't notice until first save
- No migration needed

## Related

- Electron dialog API
- User experience improvements
- Configurator settings system
