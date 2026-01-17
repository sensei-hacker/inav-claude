# Context Engineering for Claude Code: The INAV-Claude Project

**Presentation by Sensei**
**Duration:** ~12 minutes (11 slides, ~100 words per slide)
**Tone:** Informal, technical
**Audience:** Developers interested in LLM workflows

---

## Slide 1: The Problem - Context is Hard

**Visual:** Checklist of common problems (Option B)

```
Common Problems Without Context Engineering:

☐ Forgot to check lock files
☐ Used `make` instead of inav-builder agent
☐ Skipped testing before PR
☐ Didn't run code review
☐ Pushed to master instead of feature branch
☐ Loaded 100k lines but missed the critical 100

❌ Claude isn't bad - the process isn't structured!
```

**Speaker Notes (~100 words):**

So here's the problem - when you're working on a complex codebase with Claude Code, you run into these issues constantly. Claude has this massive context window, but that doesn't help if you're loading the wrong stuff. I kept seeing the same patterns: Claude would forget to check lock files, would skip testing, would use direct build commands instead of the proper agents. Or worse - I'd paste in the entire coding standards document, and Claude would just gloss over the critical parts. The problem isn't the AI being forgetful. The problem is information overload combined with poor structure. That's what context engineering fixes.

---

## Slide 2: Why This Happens - The Context Problem

**Visual:** System diagram showing information flow (Option A from old Slide 2)

```
┌──────────────────────────────────────────────┐
│  100k Lines of Code                          │
│  + 5k Lines of Documentation                 │
│  + Build Instructions                        │
│  + Testing Guides                            │
│  + Project Tracking                          │
│  + Architecture Docs                         │
│  = 110k+ Lines Total                         │
└──────────────────┬───────────────────────────┘
                   ↓
         ┌─────────────────────┐
         │   Claude's Context  │ ← Information overload
         │   [saturated]       │
         └──────────┬──────────┘
                    ↓
           ┌────────────────┐
           │ Important info │
           │ gets buried!   │
           └────────────────┘

Critical details (lock files, test requirements, agent usage)
are lost in the noise of irrelevant information.
```

**Speaker Notes (~100 words):**

Why does this happen? Think about what you're asking Claude to process. You've got a hundred thousand lines of code, five thousand lines of documentation, build instructions, testing guides, project tracking, architecture docs. It's like trying to find a specific sentence in a library by reading every book. Sure, Claude has a huge context window - but loading everything means the critical information gets buried. When you need to know "check the lock file before starting," that detail is drowning in ten thousand lines of MSP protocol documentation you don't need right now. Context engineering is about loading the right information at the right time.

---

## Slide 3: Solution Part 1 - Role Separation

**Visual:** Role cards with colored backgrounds (Option B)

```
┌─────────────────────────────────────┐
│  👔 MANAGER                         │  [Light Blue Background]
│                                     │
│  Context Size: ~1,200 lines         │
│  Focus: Planning & Coordination     │
│  Loads: Project tracking, INDEX.md  │
│  Doesn't Load: Build instructions   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  💻 DEVELOPER                       │  [Light Green Background]
│                                     │
│  Context Size: ~2,500 lines         │
│  Focus: Implementation & Testing    │
│  Loads: Code guides, test docs      │
│  Doesn't Load: Project management   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  📦 RELEASE MANAGER                 │  [Light Orange Background]
│                                     │
│  Context Size: ~1,000 lines         │
│  Focus: Builds & Artifacts          │
│  Loads: Release workflow, changelogs│
│  Doesn't Load: Implementation       │
└─────────────────────────────────────┘

Each role sees ONLY what it needs - no overlap!
```

**Speaker Notes (~100 words):**

First solution: role separation. Every conversation with Claude starts with "Which role should I take on today?" This isn't just organizational - it's fundamental to context management. The manager role loads guides about project tracking and task assignment - maybe twelve hundred lines total. The developer role loads coding standards and testing procedures - about twenty-five hundred lines. Release manager loads build and release workflows - about a thousand lines. Notice what each role DOESN'T load. The developer never sees project management documentation. The manager never sees build instructions. So far, roles alone reduce context from forty-five hundred lines down to twenty-five hundred. Each role gets exactly the context it needs, nothing more. But that's just the beginning.

---

## Slide 4: Solution Part 2 - Communication System

**Visual:** Message format example (Option C from old Slide 8)

```markdown
# Task: Fix Terrain Data Not Loading

## Priority
HIGH - User-visible feature broken

## Problem
User reports: "terrain data doesn't load" in Mission Control tab.
This prevents users from seeing terrain elevation data on the map,
important for planning fixed-wing missions and terrain clearance.

## Success Criteria              ← Clear, measurable goals
- [ ] Root cause identified and documented
- [ ] Terrain data loads successfully in UI
- [ ] No console errors related to terrain
- [ ] Visual verification: elevation chart displays
- [ ] PR created with fix and tests

## Available Resources           ← What you have to work with
- Configurator currently running and accessible
- Chrome DevTools MCP available for debugging
- test-engineer agent for UI interaction
- Flight controller attached for testing

## Files to Check                ← Narrow the search
- inav-configurator/src/js/tabs/mission_control.js
- Console logs in DevTools

## Related
- Assignment: manager/email/sent/2026-01-12-0955-task.md
```

**Speaker Notes (~100 words):**

When the manager assigns a task, it creates a structured markdown file like this. Notice what this does for context management. Everything the developer needs is in one file - the problem, success criteria, available resources, files to check. No searching through project docs. No loading the entire issue tracker. Just this one focused document. And when the developer finishes? They write a completion report - what was done, what was tested, what PR was created. This creates clear boundaries. The developer never loads the manager's project tracking documentation. Clean information flow that's part of the twelve-step process.

---

## Slide 5: Solution Part 3 - The 12-Step Workflow with Just-In-Time Documentation

**Visual:** Vertical timeline with guide loading (Option A + C highlighting)

```
Developer 12-Step Process:          Documentation Loads:

1. Check inbox for tasks
   Read assignment                  [Task file highlighted]
                                    80 lines: problem, criteria, resources
2. Read task assignment

3. Create git branch         ───►   [CRITICAL-BEFORE-CODE highlighted]
                                    105 lines:
4. Reproduce bug (fails)     ───┐   • Check lock files
                                │   • Use inav-architecture before search
5. Implement the fix            │   • Use agents, not direct commands
                                │
6. Compile the code             │   [CRITICAL-BEFORE-TEST highlighted]
                                ├─► 113 lines:
7. Verify fix (passes)       ───┘   • Test philosophy: reproduce first
                                    • Verify fix works
8. Commit changes            ───►   • Test edge cases

                                    [CRITICAL-BEFORE-COMMIT highlighted]
9. Create pull request       ───┐   105 lines:
                                │   • Git best practices
10. Check bot suggestions       │   • Commit message format
                                │
11. Report completion           │   [CRITICAL-BEFORE-PR highlighted]
                                ├─► 171 lines:
12. Archive assignment       ───┘   • MANDATORY testing
                                    • MANDATORY code review
                                    • Check CI status

Each step loads ONLY the guide needed for that step!
Total documentation loaded: ~600 lines vs. 5,000+ all at once
```

**Speaker Notes (~100 words):**

The developer follows these twelve steps, and context loads at specific points. Step three creating a branch? CRITICAL-BEFORE-CODE loads: "check lock files, use inav-architecture before searching." Steps four and seven testing? CRITICAL-BEFORE-TEST loads testing philosophy. Step eight committing? Git best practices load. Step nine creating PR? CRITICAL-BEFORE-PR loads and mandates testing and code review. Each guide is about a hundred lines - short, focused checklists. They appear exactly when needed. No giant "how to do everything" document loaded upfront. The guides even have self-improvement sections where Claude adds lessons learned for future sessions.

---

## Slide 6: Solution Part 4 - Specialized Agents with Narrow Context

**Visual:** Agent cards with stats (Option A)

```
┌──────────────────────────────────────┐
│  🔨 inav-builder                     │
│                                      │
│  Agent File: 282 lines               │
│  Knowledge Represented: ~3,000 lines │
│                                      │
│  Knows:                              │
│  • CMake build system                │
│  • ARM cross-compilation toolchains  │
│  • Linker compatibility issues       │
│  • Build script locations            │
│                                      │
│  Doesn't Know:                       │
│  • Mission planning                  │
│  • UI implementation                 │
│  • MSP protocol                      │
│                                      │
│  Lifecycle: Spawn → Build → Return   │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  🧪 test-engineer                    │
│                                      │
│  Agent File: 492 lines               │
│  Knowledge Represented: ~2,500 lines │
│                                      │
│  Knows:                              │
│  • Chrome DevTools Protocol          │
│  • UI testing strategies             │
│  • SITL simulator usage              │
│  • Bug reproduction techniques       │
│                                      │
│  Doesn't Know:                       │
│  • Build systems                     │
│  • Project management                │
│  • Release procedures                │
│                                      │
│  Lifecycle: Spawn → Test → Report    │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  📡 msp-expert                       │
│                                      │
│  Agent File: 271 lines               │
│  Knowledge Represented: ~5,000 lines │
│                                      │
│  Knows:                              │
│  • MSP protocol (100+ messages)      │
│  • Packet format specifications      │
│  • mspapi2 library usage             │
│  • Protocol debugging                │
│                                      │
│  Doesn't Know:                       │
│  • Build procedures                  │
│  • UI implementation                 │
│  • Testing workflows                 │
│                                      │
│  Lifecycle: Spawn → Lookup → Return  │
└──────────────────────────────────────┘

Total: 10 agents, 3,301 lines
Knowledge represented: ~26,000 lines (if all loaded at once)
Main session never loads this - agents handle it!
```

**Speaker Notes (~100 words):**

Looking back at the twelve steps, notice that several of them just say "call an agent." Step six compile? Call inav-builder. Step four and seven testing? Call test-engineer. Step nine code review? Call inav-code-review. That's where agents shine. Each agent is a subprocess with narrow knowledge. The inav-builder - 282 lines representing about three thousand lines of build knowledge. The test-engineer? 492 lines representing testing knowledge. The msp-expert? 271 lines but five thousand lines of protocol documentation. Ten agents total, thirty-three hundred lines of definitions representing twenty-six thousand lines of knowledge. Main Claude session never loads that. Agent spawns, does its job, returns result, disappears. Clean, focused context.

---

## Slide 7: Solution Part 5 - Skills, Agents, and Roles Together

**Visual:** Architecture diagram showing relationships

```
┌─────────────────────────────────────────────────────────────┐
│  USER: "Fix GPS bug"                                        │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
      ┌───────────────────────┐
      │  Developer Role       │  [Role = Focused Context]
      │  Loads: README,       │
      │  guides (2,500 lines) │
      └──────────┬────────────┘
                 ↓
         ┌────────────────────────┐
         │  /start-task skill     │  [Skill = Reusable Workflow]
         │  • Check locks         │
         │  • Create branch       │
         │  • Setup project dir   │
         │  • Send assignment     │
         └────────┬───────────────┘
                  ↓
    ┌────────────────────────────┐
    │  Execute 12-Step Workflow  │
    │  JIT guides load at steps  │
    └─────────┬──────────────────┘
              ↓
    ┌──────────────────────────┐
    │  Spawn Agents as Needed  │  [Agents = Narrow Expertise]
    │  • inav-architecture     │
    │  • test-engineer         │
    │  • inav-builder          │
    │  • inav-code-review      │
    └─────────┬────────────────┘
              ↓
    ┌────────────────────┐
    │  Hooks Enforce     │  [Hooks = Guardrails]
    │  • Check commands  │
    │  • Inject context  │
    │  • Prevent errors  │
    └──────────┬─────────┘
               ↓
    ┌──────────────────┐
    │  /finish-task    │  [Skill = Cleanup]
    │  • Create PR     │
    │  • Report back   │
    │  • Release lock  │
    └──────────────────┘

Skills = Multi-step workflows
Roles = Context boundaries
Agents = Specialized knowledge
Hooks = Enforcement & safety
```

**Speaker Notes (~100 words):**

Here's how it all fits together. Skills are reusable workflows - the start-task skill handles all the setup automatically. Roles define context boundaries - developer loads different docs than manager. Agents provide specialized knowledge on demand - builder, tester, code reviewer. Hooks enforce rules and inject context - when Claude tries to run make directly, the hook intercepts and says "use the builder agent." Each piece has a specific job. Skills orchestrate multi-step procedures. Roles load the right context. Agents handle specialized tasks. Hooks prevent mistakes. Together they create a system where Claude consistently follows best practices without needing constant reminders. The structure does the work.

---

## Slide 8: Hooks - Enforcement and Context Injection

**Visual:** Before/After comparison (Option B from old Slide 7)

```
╔═══════════════════════════════════════════════════════════╗
║  WITHOUT HOOKS                                            ║
╚═══════════════════════════════════════════════════════════╝

Claude: [runs make SITL]
Result: ❌ Build fails
  • Wrong directory (build/ vs build_sitl/)
  • Missing linker flags (--no-warn-rwx-segments)
  • Incomplete configuration

User: "Use the build_sitl.sh script instead"
Claude: "Oh, sorry! Let me try that."

[Next task, 2 hours later...]

Claude: [runs make SITL again]
Result: ❌ Same error

User: 😤 "I already told you to use the script!"

─────────────────────────────────────────────────────────────

╔═══════════════════════════════════════════════════════════╗
║  WITH HOOKS                                               ║
╚═══════════════════════════════════════════════════════════╝

Claude: [tries to run make SITL]

Hook: 🛑 INTERCEPTED
Hook: "Use inav-builder agent for all builds"
Hook: [Injects context about why direct make fails]

Claude: "I'll use the inav-builder agent instead"
[Spawns inav-builder agent]
[Agent uses correct script and flags]
Result: ✅ Build succeeds

[Next task, immediately...]

Claude: [starts to type "make"]
Hook: 🛑 INTERCEPTED (again)
Claude: "I'll use inav-builder"
Result: ✅ Build succeeds

User: 😊 "Claude just does the right thing!"

═══════════════════════════════════════════════════════════
Hooks enforce best practices automatically - no repetition!
```

**Speaker Notes (~100 words):**

Hooks are the enforcement mechanism. There's a PreToolUse hook written in Python that intercepts every tool call before it executes. When Claude tries to run make SITL directly, the hook catches it and says "use the inav-builder agent" - and it injects an explanation into Claude's context about why. The hook also manages permissions using a YAML config file - allow, deny, or ask about specific commands. This prevents destructive operations and ensures best practices. Without hooks, you tell Claude once, it forgets next session. With hooks, Claude learns the pattern. The SessionStart hook verifies role selection happened. Hooks are like guardrails that keep Claude on the right path automatically.

---

## Slide 9: Real Example - Fix Terrain Data Loading (Screenshots)

**Visual:** Screenshot sequence (10 seconds each)

```
Screenshot 1: The Problem (0:00-0:10)
─────────────────────────────────────
[INAV Configurator Mission Control tab]
← Arrow pointing to empty area where chart should be
Caption: "User reports: terrain elevation chart not displaying"

Screenshot 2: Task Assignment (0:10-0:20)
─────────────────────────────────────
[Terminal showing cat of task file]
Highlighted sections:
• Problem: terrain data doesn't load
• Success Criteria: chart displays
• Resources: DevTools MCP, test-engineer
Caption: "Manager creates structured 80-line assignment"

Screenshot 3: Developer Starts (0:20-0:30)
─────────────────────────────────────
[Terminal showing developer/email/inbox/ with task]
[Side panel: CRITICAL-BEFORE-CODE guide excerpt]
Highlight: "Use test-engineer agent for testing"
Caption: "Developer reads task, JIT guide loads"

Screenshot 4: test-engineer Agent (0:30-0:40)
─────────────────────────────────────
[Chrome DevTools Console panel]
Showing JavaScript errors or lack of chart initialization
Caption: "test-engineer uses DevTools, investigates UI"

Screenshot 5: Root Cause Found (0:40-0:50)
─────────────────────────────────────
[Code editor showing commented-out plotElevation() function]
Highlight the comment: "// Disabled during ESM migration"
Caption: "Found: function commented out in December 2024"

Screenshot 6: Fix Implemented (0:50-1:00)
─────────────────────────────────────
[Code editor showing Chart.js v4 integration]
Highlight: plotElevation() function uncommented and refactored
Caption: "Fix: Integrate Chart.js v4 with ESM support"

Screenshot 7: Code Review (1:00-1:10)
─────────────────────────────────────
[Terminal showing inav-code-review agent output]
Showing: ✓ No critical issues, ✓ Pattern compliance
Caption: "inav-code-review agent checks quality before PR"

Screenshot 8: Success (1:10-1:20)
─────────────────────────────────────
[INAV Configurator Mission Control with terrain chart visible]
← Arrow pointing to elevation profile chart
Caption: "Fix verified: terrain elevation displays correctly"

Screenshot 9: PR Created (1:20-1:30)
─────────────────────────────────────
[GitHub PR #2518 page]
Showing PR description with tests, changes, verification
Caption: "PR created: github.com/iNavFlight/inav-configurator/pull/2518"

Screenshot 10: Context Comparison (1:30-1:40)
─────────────────────────────────────
Split screen:
Left: "Context Loaded: ~1,500 lines"
  • Developer README (237)
  • Task (80)
  • JIT guides (~300)
  • test-engineer agent (492)
  • Relevant code (~400)

Right: "Without System: ~150,000 lines"
  • Entire codebase
  • All documentation
  • All guides
  • All agents docs

Caption: "99% reduction in unnecessary context"
```

**Speaker Notes (~100 words):**

Let me walk you through a real project. User reports terrain data doesn't load. Manager creates an eighty-line task assignment with clear criteria. Developer reads it, CRITICAL-BEFORE-CODE guide loads and says "use test-engineer for testing." Developer spawns the test-engineer agent which uses Chrome DevTools to investigate. Agent finds the issue - a function was commented out during an ESM migration in December. Developer implements fix using Chart.js v4. Runs inav-code-review agent to check quality. Creates PR. Same-day completion. Total context loaded across the entire workflow? About fifteen hundred lines. Without this system, Claude would search around, load documentation, pull in related files - probably ten to fifteen thousand lines of mostly irrelevant context. Focused workflow wins.

**Auto-advance timing: 10 seconds per screenshot**

---

## Slide 10: Results - What This Achieved

**Visual:** Stats panel with metrics

```
┌──────────────────────────────────────────────────────────┐
│  RESULTS FROM REAL-WORLD USE                             │
└──────────────────────────────────────────────────────────┘

📊 PRODUCTIVITY
   ────────────────────────────────────────────────
   Projects Completed: 78

   Same-Day Completions: 15+ projects
   - fix-terrain-data-not-loading: 4 hours
   - fix-blackbox-zero-motors: 1-word fix
   - fix-climb-rate-deadband: 1 operator change

   Average Project Duration: 1-3 days (complex projects)

🎯 PROCESS CONSISTENCY: VERY HIGH
   ────────────────────────────────────────────────
   Testing before PR:       Consistently enforced
   Code review before PR:   Consistently enforced
   Lock file checks:        Consistently enforced
   Used correct agents:     Usually automatic
   Forgotten steps:         Rare (hooks catch them)

   Manual reminders needed: Minimal
   Hook interventions: Automatic

📉 CONTEXT EFFICIENCY: 99% WASTE REDUCTION
   ────────────────────────────────────────────────
   Codebase size:          150,000 lines

   Typical context loaded per task:
   • Role README:              237 lines
   • Task assignment:           80 lines
   • JIT guides:              ~400 lines
   • Agents (spawned):        ~500 lines
   • Relevant code:           ~300 lines
   ─────────────────────────────────────────
   Total loaded:           ~1,500 lines

   Context NOT loaded:   148,500 lines
   Efficiency gain:           99%

⚡ SPEED & RELIABILITY
   ────────────────────────────────────────────────
   Claude response time: Faster
   (Less to process = faster responses)

   Error rate: Lower
   (Focused context = fewer mistakes)

   User intervention: Minimal
   (Hooks enforce automatically)

───────────────────────────────────────────────────────────
Context engineering transforms Claude from smart assistant
to reliable team member with consistent process adherence.
```

**Speaker Notes (~100 words):**

So what did this achieve? Seventy-eight projects completed. But the real wins are in consistency and efficiency. The vast majority of projects followed the twelve-step workflow correctly. Testing and code review happen consistently - not perfectly every single time, but way better than without the system. Hooks catch most mistakes automatically. When Claude does forget something, the hooks or guides usually catch it. Context efficiency - typical task loads about fifteen hundred lines versus ten to fifteen thousand of scattered documentation without the system. Massive improvement. And that matters - focused context means faster responses, fewer mistakes, better adherence to guidelines. Claude follows a professional software development process, not just ad-hoc code generation.

---

## Slide 11: Key Takeaways - Five Principles You Can Use

**Visual:** Takeaways checklist with explanations

```
╔══════════════════════════════════════════════════════════╗
║  FIVE CONTEXT ENGINEERING PRINCIPLES                     ║
╚══════════════════════════════════════════════════════════╝

✓ 1. STRUCTURE INFORMATION BY ROLE AND PHASE
   ─────────────────────────────────────────────────────
   Different tasks need different context.

   Don't load everything upfront - partition by role:
   • Manager sees project tracking (not build docs)
   • Developer sees code guides (not PM docs)
   • Release manager sees release workflow (not implementation)

   Result: Each role loads 1-3k lines instead of 10k+


✓ 2. LOAD DOCUMENTATION JUST-IN-TIME, NOT ALL UPFRONT
   ─────────────────────────────────────────────────────
   Timing matters as much as content.

   Instead of one giant guide, create phase-specific guides:
   • CRITICAL-BEFORE-CODE (locks, agents, search strategy)
   • CRITICAL-BEFORE-TEST (testing philosophy, edge cases)
   • CRITICAL-BEFORE-COMMIT (git best practices)
   • CRITICAL-BEFORE-PR (mandatory review, CI checks)

   Result: ~100 line guides load exactly when needed


✓ 3. USE SPECIALIZED SUB-AGENTS FOR FOCUSED TASKS
   ─────────────────────────────────────────────────────
   Narrow context = better results.

   Create agents for specialized knowledge domains:
   • Build systems (CMake, toolchains)
   • Testing (DevTools, SITL, reproduction)
   • Protocol knowledge (MSP, settings)
   • Architecture (codebase navigation)

   Agents spawn, execute, return result, disappear.
   Main session never loads their specialized knowledge.

   Result: 26k lines of knowledge, <500 loaded at once


✓ 4. USE HOOKS TO ENFORCE RULES AUTOMATICALLY
   ─────────────────────────────────────────────────────
   Automation beats repetition.

   PreToolUse hooks intercept commands:
   • Deny: Destructive operations (force push, rm -rf)
   • Allow: Safe operations (git status, ls, cat)
   • Ask: Potentially dangerous (git push, delete)
   • Redirect: Wrong patterns (make → use agent)

   Hooks inject context: "Why this is wrong, what to do"

   Result: Zero forgotten rules, automatic enforcement


✓ 5. CREATE CLEAR COMMUNICATION BOUNDARIES
   ─────────────────────────────────────────────────────
   Roles communicate but don't overlap.

   Email-style system:
   • Manager assigns tasks via structured markdown
   • Developer reports completion with full details
   • Clear handoffs, complete information

   Prevents context pollution:
   • Developer doesn't load project tracking docs
   • Manager doesn't load implementation guides

   Result: Clean information flow, focused context

───────────────────────────────────────────────────────────

🎯 BOTTOM LINE:

   These principles work for ANY large codebase.
   You can adopt them incrementally:

   Week 1: Add role separation (CLAUDE.md → role READMEs)
   Week 2: Create CRITICAL-BEFORE-* guides
   Week 3: Build first specialized agent
   Week 4: Add hooks for common mistakes

   Start small. The patterns scale.

───────────────────────────────────────────────────────────

📚 LEARN MORE:

   • GitHub: github.com/iNavFlight/inav (firmware)
   • Configurator: github.com/iNavFlight/inav-configurator
   • Structure: ~/inavflight/.claude/ and ~/inavflight/claude/
   • Contact: sensei-hacker on GitHub

Context engineering turns Claude from a smart assistant
into a reliable, professional development team member.
```

**Speaker Notes (~100 words):**

Five principles you can apply to your own projects. One: structure by role and phase - different tasks need different context. Two: load docs just-in-time, not all upfront - timing matters as much as content. Three: use specialized agents for focused tasks - narrow context means better results. Four: use hooks to enforce rules automatically - automation beats repetition. Five: create clear communication boundaries - roles communicate but don't overlap. These aren't specific to INAV - they work for any large codebase. And you can adopt them incrementally. Start with role separation, add JIT guides, build agents as needed. The beauty is you don't need to build everything at once. Start small and scale.

---

## Slide 12: Self-Improvement and Adaptability

**Visual:** Split screen - Create-Agent and Lessons Learned

```
LEFT SIDE: Claude Creates Its Own Tools
─────────────────────────────────────────────

The create-agent Agent:

Claude can build new specialized agents as needs arise!

User: "We keep looking up MSP messages manually"

Claude: [Uses create-agent agent]
        1. Researches MSP documentation
        2. Designs msp-expert agent
        3. Writes agent file (271 lines)
        4. Updates developer README

Result: New msp-expert agent created
        Future MSP tasks → automatic agent use

─────────────────────────────────────────────
Claude is improving its own working environment!


RIGHT SIDE: Lessons Learned - Self-Documenting
─────────────────────────────────────────────

Each guide has a "Lessons" section at the end:

┌─────────────────────────────────────────┐
│ CRITICAL-BEFORE-CODE.md                 │
├─────────────────────────────────────────┤
│ ...                                     │
│                                         │
│ ### Lessons Learned                     │
│                                         │
│ Add insights here that will help in    │
│ future sessions.                        │
│                                         │
│ - **Lock file format**: Must include   │
│   timestamp and task name, not just     │
│   "locked". Makes debugging conflicts   │
│   much easier.                          │
│                                         │
│ - **inav-architecture first**: Always   │
│   use inav-architecture agent BEFORE    │
│   Grep when searching firmware. Grep    │
│   on wrong directory wastes 10+ minutes.│
│                                         │
│ - **SITL build directory**: Use        │
│   build_sitl/ not build/ to avoid       │
│   conflicts with hardware target builds.│
│                                         │
│ <!-- Add new lessons above this line -->│
└─────────────────────────────────────────┘

Claude discovers patterns → adds to guides →
future sessions benefit automatically!
```

**Speaker Notes (~100 words):**

Two cool features: self-improvement and agent creation. First, Claude has a create-agent agent that builds new specialized agents as needs emerge. When we kept manually looking up MSP messages, Claude used create-agent to research the protocol, design a new msp-expert agent, write the agent file, and update documentation. Claude literally improved its own working environment. Second, every guide has a lessons-learned section at the end. When Claude discovers something important - like "always use inav-architecture before Grep" or "lock files need timestamps for debugging" - it adds that insight to the guide. Future sessions benefit automatically. The system documents itself as it learns. Pretty meta, right?

---

## Slide 13: Adapting This for Your Project

**Visual:** Adaptation checklist

```
╔═══════════════════════════════════════════════════════════╗
║  CLONE AND ADAPT FOR YOUR OWN PROJECT                     ║
╚═══════════════════════════════════════════════════════════╝

🎯 THE 12-STEP WORKFLOW IS UNIVERSAL

For software projects, these steps are nearly identical:

✓ 1-2.  Check inbox, read task         → Same
✓ 3.    Create git branch              → Same
✓ 4.    Reproduce bug (write test)     → Same
✓ 5.    Implement fix                  → Same (different language/framework)
✓ 6.    Compile/build                  → Same concept (npm/make/cargo/etc)
✓ 7.    Verify fix (test passes)       → Same
✓ 8.    Commit changes                 → Same
✓ 9.    Create PR                      → Same
✓ 10.   Check CI/bot feedback          → Same
✓ 11.   Report completion              → Same
✓ 12.   Archive task                   → Same

The STRUCTURE is reusable. The CONTENT needs customization.

─────────────────────────────────────────────────────────────

📋 ADAPTATION GUIDE (1-2 hours setup)

Week 1: Role Separation
├─ Clone ~/inavflight/.claude/ and ~/inavflight/claude/
├─ Update CLAUDE.md for your project name
├─ Customize role READMEs for your workflow
├─ Update .claude/settings.json paths
└─ Remove INAV-specific agents (or keep as examples)

Week 2: Just-In-Time Guides
├─ Keep the 12-step workflow (it works!)
├─ Update CRITICAL-BEFORE-CODE:
│  ├─ Your lock file location
│  ├─ Your build commands → agents
│  └─ Your codebase structure
├─ Update CRITICAL-BEFORE-TEST:
│  ├─ Your test framework (pytest/jest/etc)
│  └─ Your testing philosophy
├─ Update CRITICAL-BEFORE-COMMIT:
│  └─ Your commit message format
└─ Update CRITICAL-BEFORE-PR:
   └─ Your CI requirements

Week 3: Build Your First Agent
├─ Identify: What knowledge do you look up repeatedly?
│  Examples:
│  • API documentation (Django/FastAPI/Express)
│  • Database schema (PostgreSQL/MongoDB)
│  • Build system (Cargo/npm/Maven)
│  • Deployment (Docker/K8s)
├─ Use create-agent agent to build it!
├─ Test with real tasks
└─ Update developer README

Week 4: Add Hooks (Optional but Recommended)
├─ Copy .claude/hooks/ directory
├─ Update tool_permissions.yaml for your commands
├─ Test PreToolUse hook interception
└─ Add project-specific rules

─────────────────────────────────────────────────────────────

⚙️ WHAT TO CUSTOMIZE

Keep As-Is:
✓ Directory structure (.claude/, claude/)
✓ Role separation pattern
✓ 12-step workflow
✓ JIT guide concept (guides load at steps)
✓ Agent pattern (specialized subprocesses)
✓ Hook pattern (enforcement)
✓ Email-style communication
✓ Lessons learned sections

Customize for Your Project:
✗ Guide content (your build commands, test frameworks)
✗ Agent knowledge domains (your APIs, systems, tools)
✗ Hook rules (your safe/unsafe commands)
✗ Project structure (your repos, deployment, etc)
✗ Role responsibilities (if needed)

─────────────────────────────────────────────────────────────

🚀 EXAMPLE ADAPTATIONS

Python/Django Project:
├─ Agent: django-model-expert (ORM, migrations)
├─ Agent: api-docs-lookup (DRF, endpoints)
├─ Agent: pytest-runner (test execution, fixtures)
├─ Guide updates: pytest instead of test-engineer
└─ Hook: Block runserver in production

React/TypeScript Project:
├─ Agent: component-builder (React patterns, hooks)
├─ Agent: npm-package-manager (dependencies, scripts)
├─ Agent: storybook-handler (component docs)
├─ Guide updates: npm/vite instead of cmake/make
└─ Hook: Enforce lint before commit

Rust Project:
├─ Agent: cargo-expert (build, features, workspaces)
├─ Agent: unsafe-code-reviewer (safety checks)
├─ Agent: crates-io-lookup (dependency research)
├─ Guide updates: cargo instead of cmake
└─ Hook: Block cargo publish without approval

─────────────────────────────────────────────────────────────

💡 TIPS FOR SUCCESS

1. Start with Role Separation
   Even without agents, role-based context helps

2. The 12-Step Workflow Works
   Don't reinvent the wheel - adapt the steps

3. Build Agents Incrementally
   Start with 1-2 agents for your biggest pain points

4. Use create-agent to Help
   Let Claude build agents using the template

5. Lessons Learned Are Gold
   The self-documentation really helps

6. Hooks Prevent Mistakes
   Worth the setup time - catches errors automatically

─────────────────────────────────────────────────────────────

📦 GETTING THE FILES

Option 1: Clone INAV Repository
```bash
git clone https://github.com/iNavFlight/inav.git
cd inav
# Copy .claude/ and claude/ directories
```

Option 2: Template Repository (Coming Soon?)
Stripped-down version with just the structure

Option 3: Build From Scratch
Use this presentation as your guide!

─────────────────────────────────────────────────────────────

The structure is proven. The patterns scale.
Adapt it for YOUR codebase and watch Claude become
a reliable, consistent development team member.
```

**Speaker Notes (~100 words):**

You can totally clone this and adapt it for your project. The twelve-step workflow? That's universal for software projects - same steps whether you're doing Python, Rust, JavaScript, whatever. The structure is reusable. Just customize the content. Clone the directories, update the guides with your build commands and test frameworks, create agents for your specific knowledge domains. The cool part? Use the create-agent agent to help build your new agents! It'll research your documentation and write agents following best practices. And the lessons-learned sections mean the system improves as you use it. The patterns are proven. Adapt them to your codebase and get the same benefits we've seen.

---

## Questions?

**Repository:** github.com/iNavFlight/inav
**Contact:** sensei-hacker (GitHub)

**Thank you!**

---

## Appendix: Quick Reference

### File Structure
```
inavflight/
├── .claude/                    # Claude Code configuration
│   ├── settings.json           # Hooks, permissions, sandbox
│   ├── agents/                 # 10 agents, 3,301 lines
│   ├── skills/                 # 31 reusable workflows
│   └── hooks/                  # Enforcement scripts
│
├── claude/                     # Role-specific workspaces
│   ├── manager/                # Planning & coordination
│   ├── developer/              # Implementation & testing
│   │   ├── README.md           # 237 lines
│   │   └── guides/             # JIT documentation
│   │       ├── CRITICAL-BEFORE-CODE.md      (104 lines)
│   │       ├── CRITICAL-BEFORE-TEST.md      (113 lines)
│   │       ├── CRITICAL-BEFORE-COMMIT.md    (105 lines)
│   │       └── CRITICAL-BEFORE-PR.md        (171 lines)
│   ├── projects/               # Project tracking
│   │   ├── INDEX.md            # Active projects
│   │   └── completed/          # 78 completed
│   └── locks/                  # Concurrency control
│
└── CLAUDE.md                   # Entry point (role selection)
```

### Context Loaded by Phase
```
Role Selection:           237 lines (Developer README)
Task Assignment:           80 lines (structured task file)
Pre-coding:              104 lines (CRITICAL-BEFORE-CODE)
Testing:                 113 lines (CRITICAL-BEFORE-TEST)
Committing:              105 lines (CRITICAL-BEFORE-COMMIT)
PR Creation:             171 lines (CRITICAL-BEFORE-PR)

Agent spawns (as needed):
- inav-builder:          282 lines
- test-engineer:         492 lines
- inav-code-review:      401 lines

Total across full workflow: ~2,000 lines
vs. loading everything:    150,000+ lines
```
