# TODO: Improve Transpiler Error Reporting

## Phase 1: Audit Current State

### Find All Error Cases
- [ ] Search codebase for `console.warn`
- [ ] Search codebase for `console.error`
- [ ] Search for `throw new Error`
- [ ] Search for silent failures (returns null/undefined)
- [ ] Document each error case found

### Test Current Behavior
- [ ] Try various invalid code inputs
- [ ] Document what errors show in console
- [ ] Document what errors show in UI (if any)
- [ ] Test with DevTools closed (user perspective)
- [ ] Identify which errors are silent

### Analyze Error Paths
- [ ] Review `parser.js` error handling
- [ ] Review `analyzer.js` error handling
- [ ] Review `codegen.js` error handling
- [ ] Review `decompiler.js` error handling
- [ ] Map error flow from detection to user

## Phase 2: Design Error System

### Define Error Structure
- [ ] Design error object schema
- [ ] Define severity levels (error/warning/info)
- [ ] Define error codes/categories
- [ ] Design suggestion system
- [ ] Document error data structure

### Design UI Components
- [ ] Sketch error display mockups
- [ ] Choose error display approach (modal/panel/inline)
- [ ] Design save button state management
- [ ] Design error highlighting approach
- [ ] Plan error clearing behavior

### Create Error Utilities
- [ ] Design fuzzy matching for suggestions
- [ ] Design error formatting functions
- [ ] Design error aggregation logic
- [ ] Plan error priority/sorting

## Phase 3: Implement Error Collection

### Modify Parser
- [ ] Add errors array to parser state
- [ ] Replace console.warn with error collection
- [ ] Add line/column information to errors
- [ ] Add suggestions for common mistakes
- [ ] Return errors with parse result

### Modify Analyzer
- [ ] Add errors array to analyzer state
- [ ] Collect undefined variable errors
- [ ] Collect type mismatch errors
- [ ] Collect constraint violation errors
- [ ] Return errors with analysis result

### Modify CodeGen
- [ ] Add errors array to codegen state
- [ ] Collect unknown operand errors
- [ ] Collect invalid condition errors
- [ ] Collect size/limit exceeded errors
- [ ] Return errors with generated code

### Update Main Transpiler
- [ ] Aggregate errors from all phases
- [ ] Return structured result object
- [ ] Include both conditions and errors
- [ ] Preserve error order/priority
- [ ] Add debug mode flag

## Phase 4: Implement UI Display

### Create Error Display Component
- [ ] Design error message formatting
- [ ] Create error list component
- [ ] Add error severity icons/colors
- [ ] Add clickable line numbers
- [ ] Add expand/collapse for details

### Integrate with Programming Tab
- [ ] Hook transpile function to check for errors
- [ ] Display errors when transpilation fails
- [ ] Clear errors on successful transpile
- [ ] Update UI state based on errors
- [ ] Add error count indicator

### Manage Save Button State
- [ ] Disable save when errors exist
- [ ] Add tooltip explaining why disabled
- [ ] Enable save when no errors
- [ ] Show error count on button
- [ ] Add visual indicator (red border, etc.)

### Add Code Highlighting
- [ ] Highlight error lines in editor
- [ ] Add error markers/gutters
- [ ] Show error on hover
- [ ] Clear highlights when fixed
- [ ] Handle multiple errors on same line

## Phase 5: Create Good Error Messages

### Write Error Messages
- [ ] Undefined variable: "Variable 'X' is not defined. Available: gvar[0-7], flight.*, rc.*"
- [ ] Unknown operand: "Unknown property 'X' on 'flight'. Did you mean 'Y'?"
- [ ] Syntax error: "Unexpected token 'X' on line Y"
- [ ] Type error: "Cannot assign string to numeric property"
- [ ] Unsupported feature: "Feature 'X' is not supported. Use Y instead"
- [ ] Too complex: "Code is too complex. Maximum N conditions allowed"

### Add Suggestions
- [ ] Implement fuzzy string matching
- [ ] Suggest similar variable names
- [ ] Suggest similar property names
- [ ] Suggest alternative approaches
- [ ] Link to documentation where appropriate

### Internationalization (Optional)
- [ ] Make error messages translatable
- [ ] Use i18n system if available
- [ ] Keep error codes in English

## Phase 6: Testing

### Unit Tests
- [ ] Test error collection in parser
- [ ] Test error collection in analyzer
- [ ] Test error collection in codegen
- [ ] Test error aggregation
- [ ] Test suggestion generation

### Integration Tests
- [ ] Test undefined variable detection
- [ ] Test unknown operand detection
- [ ] Test syntax error detection
- [ ] Test type error detection
- [ ] Test complex code limits

### UI Tests
- [ ] Test error display appears
- [ ] Test save button disables
- [ ] Test error highlighting works
- [ ] Test error clearing works
- [ ] Test multiple errors display

### Manual Testing
- [ ] Test with DevTools closed (real user view)
- [ ] Test each error type
- [ ] Test error messages are clear
- [ ] Test suggestions are helpful
- [ ] Test UX flow is smooth

## Phase 7: Documentation

### User Documentation
- [ ] Document common errors
- [ ] Document how to fix them
- [ ] Add troubleshooting section
- [ ] Document supported features
- [ ] Add examples of valid code

### Developer Documentation
- [ ] Document error system architecture
- [ ] Document how to add new error types
- [ ] Document error codes
- [ ] Document testing approach
- [ ] Add comments to code

## Phase 8: Release

### Prepare PR
- [ ] Clean up debug logging
- [ ] Remove commented code
- [ ] Update changelog
- [ ] Create PR description
- [ ] Add screenshots of error UI

### Testing Before Merge
- [ ] Test with real flight controller
- [ ] Test with SITL
- [ ] Test all example code
- [ ] Verify no regressions
- [ ] Test backwards compatibility

### Post-Merge
- [ ] Monitor for user feedback
- [ ] Track common errors (telemetry?)
- [ ] Improve suggestions based on usage
- [ ] Update documentation as needed

## Future Enhancements

### Advanced Features
- [ ] Real-time error checking (as you type)
- [ ] Auto-fix suggestions
- [ ] Code completion based on available operands
- [ ] Linting rules
- [ ] Performance profiling/warnings

### Analytics
- [ ] Track most common errors
- [ ] Identify documentation gaps
- [ ] Improve suggestions over time
- [ ] A/B test error messages

## Notes

- Start with parser errors - easiest to implement
- Focus on clear, actionable messages
- Test from user perspective (DevTools closed)
- Don't overwhelm with too many errors at once
- Progressive disclosure: show 5, "and 10 more..."
