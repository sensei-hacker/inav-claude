# Presentation Visual Design Ideas

This document provides ideas for how to visually represent each slide effectively.

---

## Slide 1: The Problem - Context is Hard

**Visual Options:**

### Option A: Split screen comparison
```
┌──────────────────────┐  ┌──────────────────────┐
│  Claude's Context    │  │  What Claude Needs   │
│                      │  │                      │
│  ████████████████    │  │  ██ (2%)             │
│  ████████████████    │  │                      │
│  ████████████████    │  │  "Just the lock      │
│  ████████████████    │  │   file check!"       │
│  ████████████████    │  │                      │
│  "Everything!"       │  │                      │
└──────────────────────┘  └──────────────────────┘
     100k lines                  200 lines
```

### Option B: Missed steps checklist
```
Common Problems Without Context Engineering:

☐ Forgot to check lock files
☐ Used `make` instead of inav-builder agent
☐ Skipped testing before PR
☐ Didn't run code review
☐ Pushed to master instead of feature branch

❌ Claude isn't bad - the process isn't structured!
```

### Option C: Screenshot
- Actual screenshot of Claude Code with a huge CLAUDE.md file loaded
- Highlight how much scrolling is needed
- Annotate: "Too much info = key details missed"

**Recommendation:** Use Option B (checklist) - most relatable and clear

---

## Slide 2: The Solution - Context Engineering

**Visual Options:**

### Option A: System diagram
```
┌─────────────────────────────────────────────────┐
│  USER: "Fix GPS bug"                            │
└────────────────┬────────────────────────────────┘
                 ↓
         ┌───────────────┐
         │ Role Selection│
         │  (Developer)  │
         └───────┬───────┘
                 ↓
    ┌────────────────────────┐
    │ Load Developer README  │
    │      (237 lines)       │
    └────────┬───────────────┘
             ↓
   ┌──────────────────┐
   │ Execute Workflow │
   │ with JIT Guides  │
   └─────────┬────────┘
             ↓
   ┌─────────────────────┐
   │ Spawn Agents        │
   │ (focused context)   │
   └──────────┬──────────┘
              ↓
   ┌──────────────────┐
   │ Hooks Check      │
   │ (prevent errors) │
   └──────┬───────────┘
          ↓
   ┌─────────────┐
   │   Success!  │
   └─────────────┘
```

### Option B: Five pillars
```
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│  Roles  │ │   JIT   │ │ Agents  │ │ Skills  │ │  Hooks  │
│         │ │  Docs   │ │         │ │         │ │         │
│ Separate│ │ Right   │ │ Narrow  │ │Reusable │ │ Enforce │
│ Context │ │  Time   │ │ Context │ │Workflow │ │  Rules  │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
    ↓           ↓           ↓           ↓           ↓
       Context Engineering Architecture
```

**Recommendation:** Use Option B (five pillars) - clean and memorable

---

## Slide 3: Roles - Separation of Concerns

**Visual Options:**

### Option A: Directory tree (already in outline)
Good, but consider color-coding:
- Manager = Blue
- Developer = Green
- Release Manager = Orange
- Security Analyst = Red

### Option B: Role cards with stats
```
┌────────────────────────┐
│  👔 MANAGER            │
│  Workspace: 1,200 lines│
│  Focus: Planning       │
│  Loads: Project docs   │
│  Doesn't Load: Build   │
└────────────────────────┘

┌────────────────────────┐
│  💻 DEVELOPER          │
│  Workspace: 2,500 lines│
│  Focus: Implementation │
│  Loads: Code guides    │
│  Doesn't Load: PM docs │
└────────────────────────┘
```

### Option C: Context overlap diagram
```
Without Roles:          With Roles:
┌─────────────┐        ┌────┐  ┌────┐  ┌────┐
│             │        │ M  │  │ D  │  │ R  │
│   ALL THE   │        │    │  │    │  │    │
│   THINGS    │        │    │  │    │  │    │
│             │        └────┘  └────┘  └────┘
│   Manager   │         No context overlap!
│   Developer │         Each sees only their
│   Release   │         role's information
│   Security  │
└─────────────┘
```

**Recommendation:** Use Option C (overlap diagram) - shows the efficiency gain

---

## Slide 4: Just-In-Time Documentation - The 12-Step Workflow

**Visual Options:**

### Option A: Vertical timeline (best for this)
```
Developer 12-Step Process:          Documentation Loads:

1. Check inbox
2. Read task assignment
                                    ┌────────────────────────┐
3. Create git branch        ────────┤ CRITICAL-BEFORE-CODE   │
                                    │ • Check locks          │
4. Reproduce bug (fails)    ────┐   │ • Use agents           │
                                │   └────────────────────────┘
5. Implement fix                │
                                │   ┌────────────────────────┐
6. Compile code                 ├───┤ CRITICAL-BEFORE-TEST   │
                                │   │ • Test philosophy      │
7. Verify fix (passes)      ────┘   │ • Edge cases           │
                                    └────────────────────────┘
8. Commit changes           ────────┬─ CRITICAL-BEFORE-COMMIT
                                    │  • Git best practices
9. Create PR                ────────┼─ CRITICAL-BEFORE-PR
                                    │  • Mandatory review
10. Check bot suggestions           └─ • Mandatory testing
11. Report completion
12. Archive assignment

Each guide = ~100 lines, loads only when needed!
```

### Option B: Table format
```
| Step | Action          | Guide Loaded              | Lines |
|------|-----------------|---------------------------|-------|
| 3    | Create branch   | CRITICAL-BEFORE-CODE      | 105   |
| 4,7  | Testing         | CRITICAL-BEFORE-TEST      | 85    |
| 5    | Implementation  | coding-standards.md       | 200   |
| 8    | Commit          | CRITICAL-BEFORE-COMMIT    | 95    |
| 9    | Create PR       | CRITICAL-BEFORE-PR        | 120   |
|      |                 | **Total loaded: ~600**    |       |

vs. loading all documentation upfront: 5,000+ lines
```

### Option C: Animated progression (for digital presentation)
Show each step appearing one by one with the corresponding guide popping in

**Recommendation:** Use Option A (vertical timeline) for static, Option C if presentation is digital

---

## Slide 5: Specialized Agents - Narrow Context

**Visual Options:**

### Option A: Agent cards in a grid (already in outline)
Good! Consider adding stats to each card:
```
┌─────────────────────────────┐
│  🔨 inav-builder            │
│                             │
│  Context: 300 lines         │
│  Knows: CMake, ARM GCC      │
│  Doesn't know: Mission plan │
│                             │
│  Spawns → Builds → Returns  │
└─────────────────────────────┘
```

### Option B: Context size comparison
```
Without Agents:
Claude's main session needs to know:
• Build systems (CMake, Make)              3,000 lines
• Cross-compilation toolchains             2,000 lines
• MSP protocol (100+ messages)             5,000 lines
• Settings system (4,500 parameters)       8,000 lines
• Testing frameworks                       2,000 lines
• Architecture (subsystem locations)       3,000 lines
                                    Total: 23,000 lines!

With Agents:
Main session: 500 lines
Each agent: 300 lines (loaded only when spawned)
```

### Option C: Agent lifecycle diagram
```
Main Claude Session (1,000 lines context)
        ↓
    "Need to build SITL"
        ↓
    ┌─────────────────────┐
    │ Spawn inav-builder  │ ← Loads 300 lines
    │ agent               │   (build knowledge)
    └─────────┬───────────┘
              ↓
    Agent builds firmware
              ↓
    Returns: "SITL.elf built successfully"
              ↓
    Agent terminates ← Build knowledge unloaded
        ↓
Main session continues (1,000 lines)
```

**Recommendation:** Use Option C (lifecycle) - shows the ephemeral nature

---

## Slide 6: Skills - Reusable Workflows

**Visual Options:**

### Option A: Code snippet (already in outline)
Good! Consider adding a side-by-side comparison:

```
Without /start-task skill:        With /start-task skill:

User: "Start fixing GPS bug"     User: "/start-task GPS bug"
Claude: "Okay"
[User waits]                      Claude:
                                  ✓ Checked lock files
Claude: "What should I do first?" ✓ Acquired lock
User: "Check locks"               ✓ Created branch fix/gps-bug
Claude: "Lock file doesn't exist" ✓ Created project dir
User: "Create one"                ✓ Sent assignment email
Claude: "What should I write?"    ✓ Ready to start!
User: [explains lock format]
Claude: "Should I create branch?" Time: 5 seconds
User: "Yes"                       Steps: 0 (automatic)

Time: 5 minutes
Steps: 8 back-and-forth
```

### Option B: Skills catalog
```
Available Skills:

/start-task     Setup: locks, branch, project dir
/create-pr      PR: review, draft, bot check
/finish-task    Cleanup: report, archive, release locks
/git-workflow   Git: branch, merge, rebase
/check-builds   CI: build status, logs
/flash-firmware Flash: DFU mode, verify

Each skill = encapsulated workflow = no forgotten steps
```

**Recommendation:** Use Option A (comparison) - shows the efficiency

---

## Slide 7: Hooks - Context Injection & Guardrails

**Visual Options:**

### Option A: Interception flow (already in outline)
Good! Add some color:
- Red: Denied command
- Yellow: Hook intercepts
- Green: Corrected action

### Option B: Before/After comparison
```
Before Hooks:                    After Hooks:

Claude: [runs make SITL]         Claude: [tries to run make SITL]
Result: ❌ Build fails            Hook: 🛑 DENIED
(wrong directory, missing flags)  Hook: 💡 "Use inav-builder agent"
                                 Claude: [uses inav-builder agent]
User: "Use the build script"     Result: ✅ Build succeeds
Claude: "Oh, sorry!"
                                 No user intervention needed!
[Repeat next task...]
[Claude tries make again...]     Hook learns, Claude follows rules
User: 😤                          User: 😊
```

### Option C: Hook types table
```
Hook Type        When It Runs       Purpose
────────────────────────────────────────────────
SessionStart     Session begins     Verify role selected
PreToolUse       Before tool calls  Enforce rules, inject context
PermissionReq    User approval      Manage permissions

Example Rules:
✅ Allow: git log, git status, git diff
❓ Ask: git push, git commit --amend
❌ Deny: git push --force, rm -rf
```

**Recommendation:** Use Option B (Before/After) - most impactful

---

## Slide 8: Communication System - Clear Information Flow

**Visual Options:**

### Option A: Email flow diagram (already in outline)
Good! Consider adding example filenames:

```
Manager                         Developer
   │                               │
   │ Creates task assignment       │
   │ manager/email/sent/           │
   │ 2026-01-12-0955-task.md       │
   │                               │
   ├──────── copy ─────────────────>│
   │                               │
   │                            Reads task
   │                            Implements
   │                            Tests
   │                               │
   │                         Creates report
   │                         developer/email/sent/
   │                         2026-01-12-1210-completed.md
   │                               │
   │<──────── copy ────────────────┤
   │                               │
Reviews result                     │
Updates projects/INDEX.md          │
Archives report                    │
```

### Option B: Folder structure
```
claude/
├── manager/email/
│   ├── inbox/         ← Receives: completion reports
│   ├── sent/          ← Sends: task assignments
│   └── inbox-archive/ ← Processed messages
│
└── developer/email/
    ├── inbox/         ← Receives: task assignments
    ├── sent/          ← Sends: completion reports
    └── inbox-archive/ ← Processed tasks

Clear boundaries = no context pollution!
```

### Option C: Message format example
Show an actual email message with annotations:
```markdown
# Task: Fix Terrain Data Not Loading

## Priority: HIGH

## Problem
User reports: "terrain data doesn't load"

## Success Criteria              ← Clear goals
- [ ] Root cause identified
- [ ] Feature works
- [ ] PR created

## Available Resources           ← What you have
- Chrome DevTools MCP
- test-engineer agent
```

**Recommendation:** Use Option B (folder structure) + Option C (example)

---

## Slide 9: Real Example - Fix Terrain Data Loading

**Visual Options:**

### Option A: Timeline with screenshots
```
0:00  Problem reported      [Screenshot: missing chart]
0:05  Task assigned         [Screenshot: email file]
0:10  Developer starts      [Screenshot: CRITICAL-BEFORE-CODE]
0:15  test-engineer spawns  [Screenshot: DevTools console]
0:30  Root cause found      [Screenshot: commented code]
1:00  Fix implemented       [Screenshot: Chart.js integration]
2:00  Code review passes    [Screenshot: inav-code-review output]
3:00  PR created            [Screenshot: GitHub PR]
4:00  Completed             [Screenshot: working chart]
```

### Option B: Split screen walkthrough
```
┌──────────────────────┐  ┌──────────────────────┐
│  Context Loaded      │  │  Actions Taken       │
├──────────────────────┤  ├──────────────────────┤
│                      │  │ 1. Read task         │
│ Developer README     │  │    (80 lines)        │
│ Task assignment      │  │                      │
│ (237 + 80 lines)     │  │ 2. Load guide        │
│                      │  │    (105 lines)       │
├──────────────────────┤  │                      │
│ CRITICAL-BEFORE-CODE │  │ 3. Spawn agent       │
│ (105 lines)          │  │    test-engineer     │
│                      │  │    (300 lines)       │
├──────────────────────┤  │                      │
│ test-engineer agent  │  │ 4. Find issue        │
│ (300 lines)          │  │    Function disabled │
│                      │  │                      │
├──────────────────────┤  │ 5. Implement fix     │
│ Relevant code files  │  │    Chart.js v4       │
│ (~500 lines)         │  │                      │
├──────────────────────┤  │ 6. Code review       │
│ inav-code-review     │  │    (300 lines)       │
│ (300 lines)          │  │                      │
└──────────────────────┘  │ 7. Create PR #2518   │
                          │                      │
Total: ~1,500 lines       │ Time: 4 hours        │
vs. 150k line codebase    └──────────────────────┘
```

**Recommendation:** Use Option B (split screen) - shows context efficiency

---

## Slide 10: Results & Takeaways

**Visual Options:**

### Option A: Stats panel (already in outline)
Good! Add more visual elements:
```
┌─────────────────────────────────────────┐
│  Results After 6 Months                 │
├─────────────────────────────────────────┤
│  📊 Projects Completed: 78              │
│                                         │
│  🎯 Process Consistency: 100%           │
│     • Testing before PR: 78/78 ✓        │
│     • Code review: 78/78 ✓              │
│     • Lock file checks: 78/78 ✓         │
│                                         │
│  📉 Context Efficiency: 99%             │
│     • Average loaded: 1,500 lines       │
│     • Codebase size: 150,000 lines      │
│     • Waste reduction: 148,500 lines    │
│                                         │
│  ⚡ Speed: Fast                          │
│     • Same-day completions: 15+         │
│     • Clear process = fast execution    │
└─────────────────────────────────────────┘
```

### Option B: Key takeaways checklist
```
Five Context Engineering Principles:

✓ 1. Structure by Role and Phase
     Different tasks need different context

✓ 2. Load Documentation Just-In-Time
     Not everything upfront

✓ 3. Use Specialized Sub-Agents
     Narrow focus = better results

✓ 4. Enforce with Hooks
     Automate best practices

✓ 5. Create Clear Boundaries
     Roles communicate, don't overlap

Apply these to ANY large codebase!
```

### Option C: Before/After comparison
```
Before Context Engineering    After Context Engineering
────────────────────────────────────────────────────
Inconsistent process          Consistent 12-step workflow
Forgot testing sometimes      Mandatory testing (100%)
Skipped code review          Automatic code review (100%)
Used wrong commands          Hooks prevent mistakes
Lost in documentation        JIT guides at right time
Context overload             Focused context per task

Result: Claude as reliable team member, not just assistant
```

**Recommendation:** Combine all three - stats, takeaways, comparison

---

## General Design Tips

### Color Scheme
- **Blue:** Management/planning activities
- **Green:** Development/implementation
- **Orange:** Build/compile operations
- **Red:** Errors/denials/problems
- **Yellow:** Warnings/asks/attention

### Typography
- **Bold:** Key concepts (Role, Agent, Hook, Skill)
- **Monospace:** File paths, commands, code
- **Sans-serif:** Body text
- **Large:** Numbers/stats for impact

### Icons
- 👔 Manager
- 💻 Developer
- 📦 Release Manager
- 🔒 Security Analyst
- 🔨 Builder
- 🧪 Tester
- 📝 Documentation
- ✅ Success
- ❌ Failure
- ⚠️ Warning

### Animations (if digital presentation)
- Slide 2: Five pillars appear one by one
- Slide 4: Workflow steps progress with guides popping in
- Slide 7: Hook interception flow animates
- Slide 9: Timeline progresses

### Keep It Simple
- Max 50 words on screen per slide
- One main visual per slide
- Speaker says the details (in notes)
- Slides are visual aids, not full content

---

## Technical Presentation Setup

If giving this as a live demo:

**Have Ready:**
- This repository open in terminal
- Example files ready to cat/show:
  - `CLAUDE.md`
  - `claude/developer/README.md`
  - `claude/developer/guides/CRITICAL-BEFORE-CODE.md`
  - `claude/projects/completed/fix-terrain-data-not-loading/summary.md`
- Maybe have `inav-configurator` running to show the terrain chart working

**Demo flow:**
1. Show CLAUDE.md entry point (role selection)
2. Show developer README structure
3. Cat a CRITICAL-BEFORE-* guide
4. Show .claude/agents/ directory (ls)
5. Show completed project example
6. Show the actual PR #2518 on GitHub

**Backup plan:**
If live demo breaks, you have the screenshots prepared!
