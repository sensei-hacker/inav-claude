# TODO: Fix Transpiler Documentation

## Planning

- [x] Review developer's audit report
- [x] Identify all documentation files to update
- [x] List specific changes needed
- [ ] Determine tools needed for PDF editing
- [ ] Create backup of all documentation files

## Implementation

### Phase 1: Update Markdown Documentation

- [ ] Update `api_definitions_summary.md`
  - [ ] Add section for `events.js` (timer/whenChanged)
  - [ ] Add section for `gvar.js` (global variables)
  - [ ] Add section for `helpers.js` (utility functions)
  - [ ] Add section for `pid.js` (PID controller access)
  - [ ] Update directory structure diagram

- [ ] Update `api_maintenance_guide.md`
  - [ ] Verify all paths are correct (should be `js/transpiler/`)
  - [ ] Update file listing to include all actual files
  - [ ] Add notes about undocumented files if needed

- [ ] Update `implementation_summary.md`
  - [ ] Verify file structure section matches actual code
  - [ ] Add any missing component descriptions
  - [ ] Update architecture diagrams if needed

- [ ] Verify `JAVASCRIPT_PROGRAMMING_GUIDE.md`
  - [ ] Check all code examples reference correct paths
  - [ ] Verify examples still work with current implementation
  - [ ] No changes needed (verify only)

- [ ] Verify `TIMER_WHENCHANGED_IMPLEMENTATION.md`
  - [ ] Confirm implementation description is accurate
  - [ ] Check code references point to actual locations
  - [ ] No changes needed (verify only)

- [ ] Verify `TIMER_WHENCHANGED_EXAMPLES.md`
  - [ ] Test examples against current implementation
  - [ ] Verify code snippets are accurate
  - [ ] No changes needed (verify only)

- [ ] Verify `GENERATE_CONSTANTS_README.md`
  - [ ] Check process description is current
  - [ ] Verify paths and commands
  - [ ] No changes needed (verify only)

### Phase 2: Update PDF Documentation

- [ ] Determine PDF editing approach
  - [ ] Option A: Edit source document and regenerate PDF
  - [ ] Option B: Annotate existing PDF with corrections
  - [ ] Option C: Create new markdown version and deprecate PDF

- [ ] Update `API_MAINTENANCE.md - Single Source of Truth Guide.pdf`
  - [ ] Fix all `tabs/transpiler/` → `js/transpiler/`
  - [ ] Remove `time.js` from directory structure diagrams
  - [ ] Add `events.js`, `gvar.js`, `helpers.js`, `pid.js` to diagrams
  - [ ] Update any outdated file listings
  - [ ] Verify page numbers and references are correct

### Phase 3: Create Missing Documentation

- [ ] Document `events.js`
  - [ ] Describe `timer()` function
  - [ ] Describe `whenChanged()` function
  - [ ] Provide usage examples
  - [ ] Note operand type and values

- [ ] Document `gvar.js`
  - [ ] Describe global variable access
  - [ ] Show syntax and examples
  - [ ] Note any limitations

- [ ] Document `helpers.js`
  - [ ] List available helper functions
  - [ ] Describe purpose of each
  - [ ] Provide usage examples

- [ ] Document `pid.js`
  - [ ] Describe PID controller access
  - [ ] List available properties
  - [ ] Show usage examples

## Testing

- [ ] Path Verification
  - [ ] Extract all file paths from documentation
  - [ ] Verify each path exists in actual codebase
  - [ ] Fix any broken references

- [ ] File Listing Verification
  - [ ] List all files in `js/transpiler/api/definitions/`
  - [ ] Compare with documented file list
  - [ ] Ensure 100% match

- [ ] Cross-Reference Check
  - [ ] Compare documentation with developer's audit report
  - [ ] Verify all identified issues are addressed
  - [ ] Check off each item in audit report

- [ ] Manual Walkthrough
  - [ ] Follow documentation step-by-step
  - [ ] Verify each instruction works
  - [ ] Test code examples
  - [ ] Check all links and references

## Documentation

- [ ] Update changelog/release notes
  - [ ] Document what was fixed
  - [ ] Note any documentation reorganization

- [ ] Create README if needed
  - [ ] Add overview of documentation structure
  - [ ] Guide to which docs to read first

- [ ] Add metadata to docs
  - [ ] Last updated date
  - [ ] Version information
  - [ ] Author/maintainer info

## Code Review Prep

- [ ] Self-review all changes
  - [ ] Read through all modified documentation
  - [ ] Check for typos and grammar
  - [ ] Verify technical accuracy

- [ ] Create diff/summary
  - [ ] List all files changed
  - [ ] Summarize changes for each file
  - [ ] Highlight major improvements

- [ ] Prepare before/after comparison
  - [ ] Screenshot old directory structure diagram
  - [ ] Screenshot new directory structure diagram
  - [ ] Show path correction examples

## Pull Request

- [ ] Create PR with detailed description
  - [ ] Reference audit report
  - [ ] List all fixes applied
  - [ ] Include before/after examples

- [ ] Link related issues
  - [ ] Reference developer's audit report
  - [ ] Link to API fix project (complementary work)

- [ ] Request review from technical writers (if available)
- [ ] Address review comments
- [ ] Merge when approved

## Notes

- Keep this separate from code changes
- Focus only on documentation accuracy
- Do not attempt to fix API bugs in this project
- If you discover new documentation issues, add them to this TODO
