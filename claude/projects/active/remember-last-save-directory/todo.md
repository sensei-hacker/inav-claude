# Todo List: Remember Last Save Directory

## Phase 1: Investigation

- [ ] Find all save dialog locations
  - [ ] Search for `showSaveDialog` calls
  - [ ] Search for `dialog.showSaveDialog` calls
  - [ ] Search for file save operations
  - [ ] Document all locations found

- [ ] Identify file types being saved
  - [ ] Blackbox logs
  - [ ] CLI diffs/dumps
  - [ ] Configuration exports
  - [ ] Other file saves

- [ ] Understand existing storage mechanism
  - [ ] Find ConfigStorage or similar
  - [ ] Review how other settings are stored
  - [ ] Check persistence patterns

## Phase 2: Design

- [ ] Design storage approach
  - [ ] Choose global vs per-type directory
  - [ ] Decide on setting key name
  - [ ] Plan fallback behavior

- [ ] Plan helper functions
  - [ ] getSavedDirectory()
  - [ ] saveLastDirectory()
  - [ ] getValidSavedDirectory() (with existence check)

## Phase 3: Implementation

- [ ] Create helper functions
  - [ ] Implement getSavedDirectory()
  - [ ] Implement saveLastDirectory()
  - [ ] Implement directory existence check
  - [ ] Add proper error handling

- [ ] Update all save dialogs
  - [ ] Blackbox log save dialog
  - [ ] CLI diff save dialog
  - [ ] Configuration export dialog
  - [ ] Any other save dialogs
  - [ ] Add defaultPath to each
  - [ ] Update directory after save

## Phase 4: Edge Cases

- [ ] Handle first use
  - [ ] No saved directory exists
  - [ ] Fall back to system default
  - [ ] Test behavior

- [ ] Handle deleted directory
  - [ ] Check directory exists before using
  - [ ] Fall back to system default
  - [ ] No error messages
  - [ ] Test behavior

- [ ] Handle cross-platform paths
  - [ ] Use path.dirname()
  - [ ] Use path.join()
  - [ ] Test on all platforms

## Phase 5: Testing

- [ ] Test on Windows
  - [ ] First save
  - [ ] Second save (same session)
  - [ ] Restart and save
  - [ ] Deleted directory scenario
  - [ ] Different file types

- [ ] Test on macOS
  - [ ] First save
  - [ ] Second save (same session)
  - [ ] Restart and save
  - [ ] Deleted directory scenario
  - [ ] Different file types

- [ ] Test on Linux
  - [ ] First save
  - [ ] Second save (same session)
  - [ ] Restart and save
  - [ ] Deleted directory scenario
  - [ ] Different file types

## Phase 6: PR Creation

- [ ] Create feature branch
- [ ] Commit changes
- [ ] Write clear commit message
- [ ] Create PR with description
- [ ] Test PR builds
- [ ] Address review feedback

## Completion

- [ ] All save dialogs updated
- [ ] All platforms tested
- [ ] PR created and merged
- [ ] Send completion report to manager
