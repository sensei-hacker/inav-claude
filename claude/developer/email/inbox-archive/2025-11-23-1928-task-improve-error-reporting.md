# Task: Improve Transpiler Error Reporting

**Priority:** Medium
**Estimated Complexity:** Moderate
**Assigned Date:** 2025-11-23

## Context

We have a **user safety issue** with the transpiler: when it encounters code it doesn't know how to handle, it may silently skip the code or only log warnings to the console that users never see.

**Current bad behavior:**
- User writes code with undefined variable
- Transpiler logs "Unknown operand" to console
- User doesn't have DevTools open, doesn't see warning
- Save appears successful
- Only partial/incorrect logic saved to flight controller
- Aircraft behaves unexpectedly - **SAFETY HAZARD**

## The Problem

Users think their code is working when it's not. The transpiler is failing silently from the user's perspective.

### Example Scenario

```javascript
// User writes this:
if (flight.yaw > 1800 && customVariable > 5) {
  override.vtx.power = 4;
}

// Console shows: "Unknown operand: customVariable"
// User sees: Nothing (DevTools closed)
// Result: Incomplete logic saved, user confused
```

## Your Task

Make the transpiler warn users clearly when their code can't be transpiled, instead of silently doing the wrong thing.

**Project Location:** `claude/projects/improve-transpiler-error-reporting/`

**Files Available:**
- `summary.md` - Complete project overview and technical approach
- `todo.md` - Detailed implementation checklist

## What Success Looks Like

### Current (Bad)
1. User writes code with error
2. Save appears to work
3. Logic doesn't work as expected
4. User has no idea why

### After Your Fix (Good)
1. User writes code with error
2. UI shows: **"Error on line 1: 'customVariable' is not defined. Did you mean 'gvar[0]'?"**
3. Save button disabled with clear message
4. User fixes error
5. Error clears, save enabled
6. Everything works correctly

## Key Requirements

### Must Have

1. **Collect all errors** - Don't just log to console
   - Parser errors
   - Analyzer errors (undefined variables)
   - CodeGen errors (unknown operands)

2. **Display errors in UI** - User must see them
   - Error list or modal dialog
   - Show line numbers
   - Clear, actionable messages

3. **Prevent bad saves** - Block save when errors exist
   - Disable save button
   - Show tooltip explaining why
   - Only enable when errors cleared

4. **Helpful messages** - Not just "error"
   - "Variable 'foo' is not defined. Available: gvar[0-7], flight.*, rc.*"
   - "Unknown property 'yw' on flight. Did you mean 'yaw'?"
   - Include suggestions when possible

### Nice to Have

- Highlight error lines in code editor
- Fuzzy matching for suggestions ("flght" → "did you mean 'flight'?")
- Error severity levels (error vs warning)
- Real-time error checking (as you type)

## Phased Approach

**Phase 1: Audit (Start Here)**
- Find all console.warn/console.error in transpiler
- Test various invalid inputs
- Document what errors are currently silent
- Read through summary.md for full context

**Phase 2: Design**
- Design error object structure
- Design UI for displaying errors
- Plan how to integrate with existing code

**Phase 3: Implement**
- Modify parser/analyzer/codegen to collect errors
- Create error display UI
- Integrate with save button
- Write good error messages

**Phase 4: Test**
- Test each error type shows correctly
- Test with DevTools closed (user view)
- Verify save blocking works
- Check suggestions are helpful

## Important Notes

### This Affects Safety

Users rely on the transpiler to generate correct logic for their aircraft. Silent failures are dangerous. Take this seriously.

### Start with Phase 1

Don't jump to coding. First understand:
- Where are all the error cases?
- Which are handled, which aren't?
- What does the user currently see?

Document your findings before designing a solution.

### Focus on User Perspective

**Test with DevTools CLOSED** - that's how users experience it. If they don't see the error, it might as well not exist.

### Error Messages Matter

Bad: "Error in transpiler"
Good: "Variable 'altitude' is not defined. Did you mean 'flight.altitude'?"

Take time to write helpful, actionable messages.

## Communication

Send status report after Phase 1 with:
- All error cases found
- Current behavior for each
- Recommendation for UI approach

Ask questions if:
- Unclear what errors should block save
- Need UX/design guidance
- Find unexpected complexity

## Resources

**Project Files:**
- `claude/projects/improve-transpiler-error-reporting/summary.md`
- `claude/projects/improve-transpiler-error-reporting/todo.md`

**Code Location:**
- `bak_inav-configurator/js/transpiler/`
- `bak_inav-configurator/tabs/javascript_programming.js`

**Related:**
- This complements the API mismatch fix (prevents wrong operand values)
- This complements the save lockup fix (prevents bad saves)

## Success Criteria

You'll know this is complete when:
- [ ] No silent failures in transpiler
- [ ] All errors displayed to user in UI
- [ ] Save button blocks on errors
- [ ] Error messages are clear and helpful
- [ ] Tested with DevTools closed
- [ ] User can't accidentally save broken code

## Next Steps

1. Read the project summary.md thoroughly
2. Begin Phase 1: Audit current error handling
3. Test transpiler with various invalid inputs
4. Document findings
5. Send status report

This is important work that directly impacts user safety. Looking forward to seeing a robust error reporting system!

---

**Manager Note:** This is lower priority than the API mismatch bug (currently in progress), but it's still important. Start with the audit phase so we understand the full scope.
