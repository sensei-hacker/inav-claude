# Presentation Demo Guide

This document provides guidance for creating the demo/example for Slide 9 of the presentation.

---

## Recommended Example: fix-terrain-data-not-loading

**Why this project is perfect for the demo:**

1. **Complete** - Finished same day (2026-01-12), has PR #2518
2. **Clear problem** - "Terrain data doesn't load" is easy to understand
3. **Used multiple agents** - test-engineer, inav-builder, inav-code-review
4. **Real debugging** - Found commented-out function, fixed it
5. **Visible outcome** - Chart appears in UI (great for screenshots)
6. **Not too complex** - Can explain in 100 words

**Project files:**
- Summary: `claude/projects/completed/fix-terrain-data-not-loading/summary.md`
- Assignment: `claude/manager/email/sent/2026-01-12-0955-task-fix-terrain-data-not-loading.md`
- Completion: `claude/developer/email/sent/2026-01-12-1210-completed-terrain-data-loading-fix.md`
- PR: https://github.com/iNavFlight/inav-configurator/pull/2518

---

## Option A: Re-create with Screenshots (Recommended)

If you want authentic, live screenshots:

### Setup
1. Revert the fix temporarily:
   ```bash
   cd inav-configurator
   git checkout <commit-before-fix>
   npm start
   ```

2. Take "before" screenshots showing:
   - Mission Control tab with no terrain elevation chart
   - Console errors (if any)

### Walkthrough Steps

**Screenshot 1: Initial Problem**
- Show Mission Control tab in configurator
- Highlight missing terrain elevation chart area
- Caption: "User reports: terrain data doesn't load"

**Screenshot 2: Task Assignment**
- Show `claude/manager/email/sent/2026-01-12-0955-task-fix-terrain-data-not-loading.md`
- Highlight key parts: problem description, success criteria
- Caption: "Manager creates structured task assignment"

**Screenshot 3: Developer Inbox**
- Show `ls claude/developer/email/inbox/` output with the task file
- Caption: "Developer checks inbox, sees new assignment"

**Screenshot 4: CRITICAL-BEFORE-CODE Guide**
- Show excerpt from `guides/CRITICAL-BEFORE-CODE.md`
- Highlight: "Use test-engineer agent for testing"
- Caption: "Just-in-time guide loads, directs to use test-engineer"

**Screenshot 5: Test Engineer in Action**
- Show Claude using test-engineer agent
- Show Chrome DevTools console output
- Caption: "test-engineer agent navigates UI, checks console, finds issue"

**Screenshot 6: Root Cause Found**
- Show the commented-out `plotElevation()` function in code
- Highlight the comment explaining why it was disabled
- Caption: "Found: function disabled during ESM migration"

**Screenshot 7: Code Review Agent**
- Show inav-code-review agent output
- Show it checking the fix for issues
- Caption: "Before creating PR, inav-code-review agent checks quality"

**Screenshot 8: After Fix**
- Show Mission Control with terrain elevation chart working
- Highlight the visible elevation profile
- Caption: "Fix complete: terrain elevation displays correctly"

**Screenshot 9: PR Created**
- Show the actual PR #2518 on GitHub
- Caption: "PR created with full context and testing documentation"

**Screenshot 10: Completion Report**
- Show `claude/developer/email/sent/2026-01-12-1210-completed-terrain-data-loading-fix.md`
- Highlight: PR link, testing performed, files modified
- Caption: "Developer reports back to manager with full details"

### After Demo
```bash
cd inav-configurator
git checkout master  # Return to current state
```

---

## Option B: Simulate with Mockups (Faster)

If you don't want to revert code, create mockup screenshots:

1. **Use existing screenshots** from the configurator
2. **Add annotations** with a tool like:
   - Excalidraw (for overlays)
   - GIMP (for professional editing)
   - Simple screenshot + arrows in Google Slides

3. **Show file contents** as terminal screenshots:
   ```bash
   cat claude/projects/completed/fix-terrain-data-not-loading/summary.md | head -30
   ```

4. **Show agent invocations** as text snippets:
   ```
   > Task tool invocation:
   subagent_type: "test-engineer"
   prompt: "Navigate to Mission Control, check terrain display"
   ```

---

## Key Talking Points for Slide 9

When presenting this example, emphasize:

1. **Structured Start**: Manager creates detailed task, not just "fix this"
2. **Guided Process**: CRITICAL-BEFORE-CODE directs to right agent
3. **Specialized Agents**: test-engineer has DevTools knowledge, developer doesn't need it all
4. **Focused Context**: Each agent sees only what it needs
5. **Quality Gates**: Code review agent checks before PR
6. **Complete Trail**: Assignment → Implementation → Testing → Review → PR → Report

**Context Efficiency:**
- Without system: Load entire codebase (100k+ lines), all build docs, all testing guides
- With system: Load ~5k lines total across all steps (role guide + task + guides + agent-specific)

---

## Alternative Examples (if needed)

### fix-climb-rate-deadband
- **PR:** #11230
- **Simple:** One-word fix (AND → OR)
- **Good for:** Showing how small fixes still follow full process

### fix-crsf-msp-overflow
- **PR:** #11218
- **Technical:** Buffer overflow fix
- **Good for:** Showing safety-critical code review

### implement-pitot-sensor-validation
- **Status:** Currently in-progress
- **Good for:** Showing active project tracking
- **Note:** Not complete, so can't show full cycle

---

## Screenshot Logistics

**Tools:**
- **Linux:** `gnome-screenshot`, `flameshot` (best for annotations)
- **Windows:** Snipping Tool, ShareX
- **Mac:** Cmd+Shift+4

**Format:**
- PNG format for quality
- 1920x1080 or 1280x720 for projector compatibility
- Annotate with arrows/boxes to highlight key areas
- Keep file size reasonable (<1MB each)

**Organization:**
```
presentation/
├── slides/
│   ├── slide-09-01-before.png
│   ├── slide-09-02-assignment.png
│   ├── slide-09-03-inbox.png
│   └── ...
└── script/
    └── timing-notes.txt
```

---

## Timing Notes for Slide 9

**Total time:** ~60 seconds

**Breakdown:**
- Problem statement (10s): "User reports terrain data doesn't load"
- Process overview (20s): Walk through the workflow steps
- Key insight (20s): "Context loaded? Maybe 5k lines vs 100k"
- Result (10s): "Same-day completion, PR #2518"

**Don't:**
- Get bogged down in technical details
- Show every single step
- Explain the entire codebase structure

**Do:**
- Keep it high-level
- Focus on the context engineering aspects
- Show how roles/agents/guides work together
- Emphasize the efficiency gain

---

## Backup Plan

If live demo fails or screenshots aren't ready:

**Talk through it verbally** with simple text slides:
```
Problem: "Terrain data doesn't load"
    ↓
Manager: Creates task → developer/inbox
    ↓
Developer: Reads CRITICAL-BEFORE-CODE guide
    ↓
Spawns: test-engineer agent (DevTools + UI testing)
    ↓
Finds: plotElevation() commented out
    ↓
Fixes: Integrates Chart.js v4
    ↓
Review: inav-code-review agent checks code
    ↓
Result: PR #2518, merged same day
```

The workflow story is more important than perfect visuals.
