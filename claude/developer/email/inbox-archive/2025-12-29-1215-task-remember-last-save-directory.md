# Task Assignment: Remember Last Save Directory

**Date:** 2025-12-29 12:15
**Project:** remember-last-save-directory
**Priority:** MEDIUM
**Estimated Effort:** 2-4 hours
**Type:** UX Enhancement

## Task

Implement persistent "last used directory" for all file save dialogs in inav-configurator. When users save blackbox logs, diffs, or any other files, the save dialog should default to the last directory they used.

## Problem

**Current behavior:**
- Save dialogs always default to some system directory (Documents, Downloads, etc.)
- Users must navigate to their preferred location every single time
- This is tedious when saving multiple files in a session

**User frustration:**
- Saving multiple blackbox logs requires repeated navigation
- Saving diffs requires re-navigating each time
- No memory of user's preferred location

## Solution

**Remember the last save directory** and use it as the default for future save operations.

**Persistence:**
- Store last save directory in application settings/localStorage
- Persist across app restarts
- Update whenever user successfully saves a file

## What to Do

### 1. Investigation Phase

**Find all save dialog locations:**

Search for file save operations in the codebase:
```bash
cd inav-configurator

# Find save dialog usage
grep -r "showSaveDialog" js/
grep -r "dialog.showSaveDialog" js/
grep -r "save.*file" js/
grep -r "saveAs" js/
```

**Common locations to check:**
- Blackbox log saving (likely in blackbox tab)
- Diff/dump saving (CLI tab or similar)
- Configuration export
- Any other file export features

**Technology used:**
- Electron's `dialog.showSaveDialog()` API
- Check if there's already a dialog wrapper/helper

### 2. Design the Solution

**Decide on storage mechanism:**

**Option A: Single global "last save directory"**
- Store one directory for all save operations
- Simplest approach
- Example: `settings.lastSaveDirectory`

**Option B: Per-feature save directories**
- Store different directories for different file types
- Example: `settings.lastBlackboxDirectory`, `settings.lastDiffDirectory`
- More complex but more flexible

**Recommendation:** Start with Option A (global), can enhance to Option B later if needed.

**Storage location:**
- Use existing settings/localStorage mechanism
- Check how other persistent settings are stored
- Follow existing patterns in configurator

### 3. Implementation

**Core implementation pattern:**

```javascript
// When showing save dialog
const defaultPath = getSavedDirectory() || getSystemDefaultDirectory();
const result = await dialog.showSaveDialog({
    defaultPath: defaultPath,
    // ... other options
});

if (result.filePath) {
    // Save the file as normal
    await saveFile(result.filePath, data);

    // Remember the directory for next time
    const directory = path.dirname(result.filePath);
    saveLastDirectory(directory);
}
```

**Helper functions needed:**

```javascript
// Get the last saved directory from settings
function getSavedDirectory() {
    return ConfigStorage.get('lastSaveDirectory');
}

// Save the directory to settings
function saveLastDirectory(directory) {
    ConfigStorage.set('lastSaveDirectory', directory);
}

// Verify directory still exists (handle moved/deleted folders)
function getValidSavedDirectory() {
    const saved = getSavedDirectory();
    if (saved && fs.existsSync(saved)) {
        return saved;
    }
    return null; // Fall back to system default
}
```

**Apply to all save dialogs:**
- Find every `showSaveDialog()` call
- Add `defaultPath` parameter using saved directory
- Update saved directory after successful save
- Verify directory exists before using it

### 4. Handle Edge Cases

**Directory no longer exists:**
- User might delete or rename the directory
- Check if directory exists before using it
- Fall back to system default if not

**First time use:**
- No saved directory yet
- Use system default (Documents, Downloads, etc.)
- Save directory after first successful save

**Multiple concurrent saves:**
- User might have multiple save dialogs open
- Ensure last save wins (standard behavior)

**Cross-platform:**
- Test on Windows, macOS, Linux
- Ensure path handling works on all platforms
- Use `path.join()` for cross-platform compatibility

### 5. Testing

**Manual testing checklist:**

1. **First save:**
   - Open configurator
   - Save a blackbox log
   - Choose a specific directory
   - Verify file saves correctly

2. **Second save (same session):**
   - Save another file (same or different type)
   - Verify dialog opens to the directory used in step 1
   - Save successfully

3. **After restart:**
   - Close and reopen configurator
   - Save a file
   - Verify dialog opens to last used directory
   - Persistence works across sessions

4. **Directory deleted:**
   - Delete the last used directory
   - Open save dialog
   - Verify falls back to system default gracefully (no errors)

5. **Different file types:**
   - Test blackbox log saves
   - Test diff/dump saves
   - Test any other save operations
   - Verify all use the same last directory

**Test on all platforms:**
- Windows
- macOS
- Linux

### 6. Configuration (Optional)

**Consider adding a reset option:**
- Allow users to clear the saved directory
- Useful if they want to reset to defaults
- Could be in settings or a hidden feature

**Not required for first implementation** - can add later if users request it.

### 7. Documentation

**User-facing documentation:**
- Probably doesn't need explicit documentation
- This is expected behavior (most apps work this way)
- Users will notice it "just works"

**Code comments:**
- Comment the helper functions
- Explain the persistence mechanism
- Note edge case handling

## Success Criteria

- [ ] All save dialog locations identified
- [ ] Last save directory stored in settings/localStorage
- [ ] Save dialogs use last directory as default path
- [ ] Directory updated after each successful save
- [ ] Handles non-existent directory gracefully
- [ ] Works on first use (no saved directory yet)
- [ ] Persists across app restarts
- [ ] Tested on Windows, macOS, Linux
- [ ] All save operations use the feature (blackbox, diff, etc.)
- [ ] No errors or crashes
- [ ] Code follows existing configurator patterns

## Important Notes

**Follow existing patterns:**
- Check how other persistent settings are stored
- Use existing `ConfigStorage` or similar mechanism
- Match code style of surrounding code

**Electron dialog API:**
- Reference: https://www.electronjs.org/docs/latest/api/dialog#dialogshowsavedialogbrowserwindow-options
- The `defaultPath` option sets the initial directory
- Returns object with `filePath` property

**Path handling:**
- Use Node.js `path` module for cross-platform compatibility
- `path.dirname(filePath)` to get directory from full path
- `path.join()` to construct paths

**Storage keys:**
- Use a clear key name like `lastSaveDirectory`
- Check existing key naming conventions
- Ensure it's in the right scope (global settings)

**Keep it simple:**
- Start with single global directory for all saves
- Can enhance later if users want per-feature directories
- Don't over-engineer the first version

**Backwards compatible:**
- If no saved directory exists yet, fall back to system default
- Existing users won't notice anything different at first
- After first save, feature kicks in

---
**Manager**
