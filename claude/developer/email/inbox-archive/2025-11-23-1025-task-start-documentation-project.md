# Task: Begin Transpiler Documentation Fix Project

**Priority:** High
**Estimated Complexity:** Moderate
**Assigned Date:** 2025-11-23

## Context

Excellent work on the transpiler audit! Your comprehensive report revealed critical issues that need to be addressed. Based on your findings, I've created **two separate projects** to tackle these issues systematically:

1. **fix-transpiler-documentation/** - Documentation updates (THIS PROJECT - START NOW)
2. **fix-transpiler-api-mismatches/** - Critical API bug fixes (LATER)

## Project Separation Rationale

I've separated these concerns because:
- Documentation fixes are low-risk, code-free changes
- API fixes are critical but require careful investigation and testing
- Working on them separately prevents confusion and keeps PRs focused
- Documentation can be completed quickly while we plan the API fixes carefully

## Your Task: Start Documentation Project Now

Please begin work on the **fix-transpiler-documentation** project immediately.

**Project Location:** `claude/projects/fix-transpiler-documentation/`

**Files Available:**
- `summary.md` - Complete project overview and approach
- `todo.md` - Detailed checklist of all tasks

## What to Do

1. **Read the project files**
   - Review `claude/projects/fix-transpiler-documentation/summary.md`
   - Review `claude/projects/fix-transpiler-documentation/todo.md`
   - Understand the scope and approach

2. **Begin implementation**
   - Follow the TODO checklist
   - Check off items as you complete them
   - Focus on Phase 1: Update Markdown Documentation first

3. **Key Focus Areas:**
   - Fix path references: `tabs/transpiler/` → `js/transpiler/`
   - Update file structure diagrams (remove time.js, add actual files)
   - Document the 4 undocumented API files: events.js, gvar.js, helpers.js, pid.js
   - Verify all existing documentation is accurate

4. **Important Notes:**
   - **DO NOT** touch any code files - this is documentation-only
   - **DO NOT** try to fix the API operand bugs - that's the other project
   - Focus on making docs match reality, not changing reality to match docs
   - Also please identity anything in the documentation which covers only the process of how something was done, anything that isn't relevant to future users and developers

## API Mismatch Project - Do Later

The **fix-transpiler-api-mismatches** project contains the critical bug fixes you identified. We will tackle this separately after the documentation is updated.

**Why later:**
- Requires careful investigation and testing
- Critical bug needs thorough planning
- May need coordination with firmware team
- Higher risk, needs more preparation

I'll send you a separate task for that project when it's time to begin.

## Progress Updates

Please update me on progress by:
- Sending status reports to `claude/manager/inbox/` at meaningful milestones
- Updating the TODO checklist in the project directory
- Asking questions if you encounter any blockers

## Success Criteria

You'll know this project is complete when:
- All documentation files accurately reflect the actual code structure
- All file paths reference correct locations
- No documentation references non-existent files
- TODO checklist is fully checked off

## Resources

**Project Files:**
- `claude/projects/fix-transpiler-documentation/summary.md`
- `claude/projects/fix-transpiler-documentation/todo.md`

**Reference Materials:**
- Your audit report: `claude/manager/inbox/2025-11-23-transpiler-documentation-review-report.md`
- Code location: `bak_inav-configurator/js/transpiler/`
- Docs location: `bak_inav-configurator/js/transpiler/docs/`

**Original Task:**
- `claude/developer/inbox/2025-11-23-1006-task-review-transpiler-documentation.md`

## Questions?

If you have any questions or need clarification:
- Send a question message to `claude/manager/inbox/`
- Reference this task
- I'll respond with guidance

## Next Steps

1. Read the project summary and TODO
2. Begin Phase 1: Update Markdown Documentation
3. Work through the checklist systematically
4. Send status update when Phase 1 is complete

Good luck! Looking forward to seeing clean, accurate documentation.

---

**Manager Note:** The critical API bug fix will be addressed in a separate, focused effort. For now, let's get the documentation in good shape so future work is easier.
