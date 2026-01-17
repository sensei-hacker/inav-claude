---
marp: true
theme: default
class: invert
paginate: true
backgroundColor: #1a1a1a
color: #e0e0e0
style: |
  section {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    padding: 40px 60px;
  }
  h1 {
    color: #4fc3f7;
    font-size: 1.8em;
    margin-bottom: 0.3em;
  }
  h2 {
    color: #81c784;
    font-size: 1.4em;
    margin-top: 0.5em;
    margin-bottom: 0.3em;
  }
  h3 {
    font-size: 1.2em;
    margin-top: 0.4em;
    margin-bottom: 0.3em;
  }
  p, ul, ol {
    font-size: 0.95em;
    line-height: 1.3;
    margin: 0.3em 0;
  }
  code {
    background: #2d2d2d;
    color: #f8f8f2;
    font-size: 0.9em;
  }
  pre {
    background: #2d2d2d;
    border-left: 4px solid #4fc3f7;
    padding: 0.8em;
    font-size: 0.8em;
    margin: 0.5em 0;
  }
  .columns {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  .role-card {
    border: 2px solid #555;
    border-radius: 8px;
    padding: 0.5em;
    margin: 0.2em;
  }
  .manager { background: rgba(33, 150, 243, 0.15); }
  .developer { background: rgba(76, 175, 80, 0.15); }
  .release { background: rgba(255, 152, 0, 0.15); }
  .checklist { font-size: 0.85em; line-height: 1.6; }
  .diagram { font-family: monospace; font-size: 0.7em; line-height: 1.3; }
  .stats { font-size: 1.1em; font-weight: bold; color: #4fc3f7; }
  .emoji { font-size: 1.2em; }
---

<!--
Speaker Notes: Programming 40 years.
I've been using Claude Code to work on the a project with 150,000 lines of C code.
I ran into some problems working with Claude on this codebase, and I'm going to talk about how I solved those problems.
-->

# Context Engineering for Claude Code
## The INAV-Claude Project

**Sensei**
*How I got Claude to stop forgetting things*

---

<!--
Speaker Notes: Before we dive in, let me give you quick context on the project I applied this on.
It the same approach should work for most any coding project, and other things too.

INAV is an open-source drone autopilot firmware. 150,000 lines of code - C code for the firmware that runs on the flight controller, plus JavaScript for the desktop configuration tool.

It uses a bunch different protocols - one's called MSP.

But the specific code doesn't matter - these patterns work for any codebase.
-->

# Quick Context: INAV Project

**INAV:** Open-source drone autopilot firmware

**Codebase:** 150,000 lines
- C code (firmware)
- JavaScript (configurator)

It uses several different protocols, such as one called MSP.

*Focus on the patterns, not the specifics*

---

<!--
Speaker Notes: There's the problem I kept running into.

I'm going to show you five principles that solved this and made Claude way more reliable. But first, let me show you what was going wrong.

When you're working on a big codebase with Claude Code, you run into these issues constantly.

Claude has a massive context window, but that's actually a problem - it can easily get distracted from the key instructions.

I'd write instructions for Claude to follow, but I kept seeing it screw up the same things.
Claude would forget to check lock files. Skip testing. Use direct build commands instead of the build script - and waste time by screwing it up and having to figure it out again every time.

I'd give it extensive instructions and Claude would just gloss over the critical parts

The problem isn't the AI being forgetful.

It's information overload combined with poor structure.

That's what context engineering solves.
-->

# The Problem

## Problems Without Context Engineering

<div class="checklist">

☐ Forgot to check lock files
☐ Skipped testing before PR
☐ Didn't run code review
☐ Missing commit message details
☐ Loaded 100k lines but missed the critical 100

</div>

### ❌ Claude isn't bad - the process isn't structured!

### Root Cause: Information Architecture
✓ Not an AI limitation
✓ Structure problem

* But the Opus model *is* bad - use Sonnet
---

<!--
Speaker Notes: So why does this happen?

Think about what you're asking Claude to process.

You've got a hundred thousand lines of code. Five thousand lines of documentation. Build instructions, testing guides, project tracking, architecture docs.

Sure, Claude has a huge context window - but when you load everything, the critical information gets buried.

The model needs to know "check the lock file before starting," that detail is drowning in a thousand lines of MSP protocol documentation.

Context engineering is loading the right information at the right time so the model doesn't get lost.
-->

# Why This Happens

<pre class="diagram">
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
        ┌──────────────────────┐
        │  Claude's Context    │ ← Information overload
        │   [saturated]        │
        └──────────┬───────────┘
                   ↓
          ┌────────────────────┐
          │  Important info    │
          │   Make sure to a   │
          └────────────────────┘
</pre>

**Critical details get lost in the noise**

---

<!--
Speaker Notes: So first solution - role separation.

I made a system where every session with Claude starts with "Which role should I take on today?"

Claude asks me if it should take on the manager role, the developer role, the release manager, etc.

The manager role has references to guides about project tracking and task assignment.

The developer role has coding standards and testing procedures.

Release manager loads build and release workflows.

Notice what each role DOESN'T load.

The developer never sees project management docs.

The manager never sees build instructions.

Without roles, you'd load all the documentation at once - that's 4,500 lines.

With roles, you only load what's relevant. The manager gets 1,200 lines, not 4,500.

Each role gets exactly what it needs, nothing more.

So that's a good start.
-->

# Solution 1 - Role Separation

<div class="columns">
<div>

<div class="role-card manager">

### 👔 MANAGER

**Context Size:** ~1,200 lines
**Focus:** Planning & Coordination
**Loads:** Project tracking
**Doesn't Load:** Build instructions

</div>

<div class="role-card developer">

### 💻 DEVELOPER

**Context Size:** ~2,500 lines
**Focus:** Implementation & Testing
**Loads:** Code guides, test docs
**Doesn't Load:** Project management

</div>

</div>
<div>

<div class="role-card release">

### 📦 RELEASE MANAGER

**Context Size:** ~1,000 lines
**Focus:** Builds & Artifacts
**Loads:** Release workflow
**Doesn't Load:** Implementation

</div>

### Each role sees what it needs

**WITHOUT roles:**<br /> All docs loaded 4,500 lines
**WITH roles:**<br /> Only relevant docs 2,500 lines max

<div style="margin-top: 1.5em; opacity: 0.3; font-size: 0.8em; overflow: hidden; max-height: 40px;">

But that's still too much.

</div>

</div>
</div>

---

<!--
Speaker Notes:
When the manager assigns a task, it creates a structured markdown file like this.

Notice what this does for context.

Everything the developer needs is in one file. The problem, success criteria, available resources, files to check.

The success criteria uses Claude's built-in TODO list format. Claude can track and update it as work progresses.

No searching through project docs.

No loading the entire issue tracker.

Just this one focused file.

When the developer finishes, They write a completion report. What was done, what was tested, what PR was created.

This creates clear boundaries.

The developer never loads the manager's project tracking stuff.

-->

# Communication System

```markdown
# Task: Fix Terrain Data Not Loading

## Priority: HIGH

## Problem
User reports: "terrain data doesn't load" in Mission Control.

## Success Criteria              ← Clear goals
- [ ] Root cause identified
- [ ] Terrain data loads successfully
- [ ] PR created with tests

## Available Resources           ← What you have
- Chrome DevTools MCP available
- test-engineer agent for UI testing
```

**Everything in one focused file (80 lines)**
**No searching through project docs - no extra noise**

---

<!--
Speaker Notes:
While working, the developer follows a specified twelve-step process so it consistently does each step, like testing.
And at each step, it loads just the information for that step.
And context loads at specific points.

Step three - creating a branch? CRITICAL-BEFORE-CODE loads.
That file has a sub-checklist: "Check lock files, use inav-architecture before searching."

Steps four and seven - testing? CRITICAL-BEFORE-TEST loads testing philosophy.

Step eight - committing? Git best practices load.

Step nine - creating a PR? CRITICAL-BEFORE-PR loads and mandates testing and code review.

Each guide is about a hundred lines. Short, focused checklists.

They appear exactly when you need them.

No giant "how to do everything" document loaded upfront.

-->

# Solution 2 - 12-Step Workflow + JIT Docs

<div class="diagram" style="font-size: 0.65em;">

Developer 12-Step Process:          Documentation Loads:

1. Check inbox
2. Read task                        [Task file: 80 lines]

3. Create git branch         ───►   [CRITICAL-BEFORE-CODE: 104 lines]
                                    • Check lock files
4. Reproduce bug (fails)     ───►   • Use test-engineer agent, other agents - not direct commands
                                
5. Implement fix             ───┐   [CRITICAL-BEFORE-TEST: 113 lines]
                                │   • List of agents to use
                                ├─► • Test philosophy
                                    • Edge cases


6. Compile code              ───►   • inav-builder agent
7. Verify fix (passes)       ───►   • test-engineer agent

8. Commit changes            ───►   [CRITICAL-BEFORE-COMMIT: 105 lines]
                                    • Git best practices

9. Create PR                 ───►   [CRITICAL-BEFORE-PR: 171 lines]
                                    • MANDATORY testing
10. Check bot suggestions           • MANDATORY code review (code review agent)

11. Report completion
12. Archive assignment

</div>

**Total docs loaded: ~600 lines vs. 5,000+ all at once**

---

<!--
Speaker Notes: The guides have self-improvement sections where Claude adds lessons learned for future sessions.
So it doesn't make the same mistake more than once - it remembers.
-->

# Self-Improving Guides

```markdown
## Self-Improvement: Lessons Learned

When you discover something important about PRE-CODING SETUP
that will likely help in future sessions, add it to this section.
Only add insights that are:
- **Reusable** - will apply to future pre-coding setup
- **About setup/preparation** - lock files, branches, agent usage
- **Concise** - one line per lesson

Use the Edit tool to append new entries.
Format: `- **Brief title**: One-sentence insight`

### Lessons

- **Lock file timestamps**: Include timestamp for debugging
  (e.g., inav.lock.2025-12-28-1430)
- **Architecture first**: Use inav-architecture agent BEFORE Grep
  when searching - saves 10+ minutes
- **SITL directory**: SITL builds go in build_sitl/ not build/

<!-- Add new lessons above this line -->
```

**Claude documents what it learns - future sessions benefit automatically**

---

<!--
Speaker Notes: Several of the 12 steps say "call an agent."

Step six - compile? Call inav-builder.

Steps four and seven - testing? Call test-engineer.

Step nine - code review? Call inav-code-review.

That's where agents come in - another level of context control.

Agents in Claude Code are specialized subprocesses. Separate Claude instances with their own focused context. Like experts you call in for specific tasks.

Each agent has narrow knowledge. And critically, each agent has its OWN context window.

The agent's work doesn't pollute the main context.

The inav-builder has 282 lines refrecncing about 1,400 lines of build knowledge.

The test-engineer? 492 lines representing testing knowledge, with references to extensive testing docs.

The msp-expert? 271 lines but it represents five thousand lines of protocol docs.

Currently I have 12 agents total. Thirty-three hundred lines of definitions representing twenty-six THOUSAND lines of knowledge.

What does that mean? Each agent definition is short - maybe 300 lines. But that definition gives it access to thousands of lines of documentation without loading it into the main context.

The main Claude session never loads that.

Agent spawns. Does its job. Returns the result. Disappears.

Focused context.
-->

# Specialized Agents

<div class="columns">
<div>

### 🔨 inav-builder

**Agent File:** 282 lines
**Represents:** ~3,000 lines

**Knows:**
• CMake build system
• ARM cross-compilation
• Linker compatibility

**Doesn't Know:**
• Mission planning
• MSP protocol

**Lifecycle:** Spawn → Build → Return

</div>
<div>

### 🧪 test-engineer

**Agent File:** 492 lines
**Represents:** ~2,500 lines

**Knows:**
• Chrome DevTools Protocol
• UI testing strategies
• SITL simulator usage

**Doesn't Know:**
• Build systems
• Project management

**Lifecycle:** Spawn → Test → Report

</div>
</div>

<div style="text-align: center; margin-top: 1em;">

**10 agents total: 3,301 lines representing ~26,000 lines**
Main session never loads this - agents handle it.

</div>

---

<!--
Speaker Notes: So here's how it all fits together.

Roles define the broadest context boundaries. Developer loads different docs than manager.

Agents provide specialized knowledge on demand. Builder, tester, code reviewer.

Skills are reusable workflows that share the parent context. The start-task skill handles all the setup, doing the right setup steps every time.

Hooks enforce the rules. When Claude tries to run make directly, the hook intercepts and says "no-no -- use the builder agent."

Each piece has a specific job.

Roles load the right overall context.

Agents handle specialized tasks.

Skills orchestrate multi-step stuff.

Then we have Hooks to catch and stop mistakes.

Together they make Claude follow the right process without you constantly reminding it.

The structure does the work.
-->


<pre class="diagram" style="font-size: 0.7em; line-height: 1.2;">
┌──────────────────────────────────────────────────┐
│  USER: "Fix GPS bug"                             │
└─────────────────────┬────────────────────────────┘
                      ↓
         ┌────────────────────────────┐
         │  Developer Role            │  [Focused Context]
         │  Loads: 2,500 lines        │
         └─────────────┬──────────────┘
                       ↓
            ┌─────────────────────────────┐
            │  /start-task skill          │  [Reusable Workflow]
            │  • Check locks              │
            │  • Create branch            │
            └──────────────┬──────────────┘
                           ↓
               ┌───────────────────────────┐
               │  Execute 12-Step Workflow │
               └────────────┬──────────────┘
                            ↓
               ┌───────────────────────────┐
               │  Spawn Agents as Needed   │  [Narrow Expertise]
               │  • inav-builder           │
               │  • test-engineer          │
               └────────────┬──────────────┘
                            ↓
               ┌───────────────────────────┐
               │  Hooks Enforce            │  [Guardrails]
               │  • Check commands         │
               └───────────────────────────┘
</pre>

---

<!--
Speaker Notes:
But What if it still messses up sometimes?
There is an enforcement mechanism called hooks.
There's a hook written in Python. It intercepts every tool call before it executes.

When Claude tries to run make directly, the hook catches it. Says "use the inav-builder agent". And it injects an explanation into Claude's context.

The hook also manages permissions using a YAML config file. Allow, deny, or ask about specific commands.

This prevents destructive operations and makes sure the right process gets followed.

Without hooks, Claude just forgets in the next session. You have to tell it the same thing again.

Hooks are like guardrails. They keep Claude from making the same mistakes.
-->

# I'm A Hooker

<div class="columns">
<div>

### WITHOUT HOOKS

Claude: [runs `make` directly, incorrectly]
**Result:** ❌ Build fails
• Cryptic errors

User: "Use the build script"
Claude: "Oh, sorry!"

*[Next task...]*

Claude: [runs `make` again]
User: <span class="emoji">😤</span>
Context: Filled with compile messages
</div>
<div>

### WITH HOOKS

Claude: [tries `make SITL`]

Hook: 🛑 **INTERCEPTED**
Hook: "Use inav-builder agent"

Claude: [uses inav-builder]
**Result:** ✅ Build succeeds

User: <span class="emoji">😊</span>

</div>
</div>

### Hooks enforce the rules automatically

---

<!--
Speaker Notes: Let me walk you through a real project.
-->

# Real Example

**Total context loaded:** ~1,500 lines
**Without this system:** ~10-15k lines

---

<!--
Speaker Notes: Manager creates an eighty-line task assignment with clear success criteria and available resources.
-->

# Real Example (1/9)

![Screenshot: Task assignment](screenshots/slide-09-01-task-assignment.png)

---

<!--
Speaker Notes: Developer reads the task and uses the /start-task skill to begin working on the fix.
-->

# Real Example (2/9)

![Screenshot: Developer starts](screenshots/slide-09-02-developer-starts.png)

---

<!--
Speaker Notes: CRITICAL-BEFORE-CODE guide loads automatically with context-specific instructions.
-->

# Real Example (3/9)

![Screenshot: JIT guide loads](screenshots/slide-09-03-jit-guide.png)

---

<!--
Speaker Notes: It spawns the Test-engineer agent spawns to reproduce the issue using Chrome dev tools
-->

# Real Example (4/9)

![Screenshot: Agent spawns](screenshots/slide-09-04-agent-spawn.png)

---

<!--
Speaker Notes: Developer implements the fix
-->

# Real Example (5/9)

![Screenshot: Implement fix](screenshots/slide-09-05-implement-fix.png)

---

<!--
Speaker Notes: The code-review agent checks the code quality
-->

# Real Example (6/9)

![Screenshot: Code review](screenshots/slide-09-06-code-review.png)

---

<!--
Speaker Notes: It reads the "before pull request" guide, checking that there are tests and documentation.
-->

# Real Example (7/9)

![Screenshot: PR created](screenshots/slide-09-07-pr-created.png)

---

<!--
Speaker Notes: Developer writes completion report documenting what was done and tested.
-->

# Real Example (8/9)

![Screenshot: Completion report](screenshots/slide-09-08-completion.png)

---

<!--
Speaker Notes:
So instead of loading 10,000 lines and getting lost, it loaded only the 1,500 lines it needed -
each section right when it needed them.
-->

# Real Example (9/9)

![Screenshot: Context comparison](screenshots/slide-09-09-context-comparison.png)

---

<!--
Speaker Notes: So what did this achieve?

Seventy-eight projects completed in the last two months. Made me way more productive.
The previous two INAV maintainers spent a LOT of hours and a LOT of energy on the job.
Claude is really helping to releive that burden for me.

But the real wins? Consistency and efficiency.

Projects follow the twelve-step workflow consistently.

Testing and code review happen consistently. Not perfectly every single time, but way better than without the system.

Hooks catch most mistakes automatically.

Focused context means faster responses. Fewer mistakes. Better adherence to guidelines.

Claude follows a real development workflow, not just ad-hoc code generation.
-->

# Results from Real-World Use

<div class="columns">
<div>

### 📊 PRODUCTIVITY & CONSISTENCY

**Projects Completed:** <span class="stats">78 in last 2 months</span>

**Process Consistency:** <span class="stats">Really high</span>
✓ Projects follow 12-step workflow
✓ Testing before PR
✓ Code review before PR
✓ Lock file checks

**Much more productive than 3 previous maintainers**

</div>
<div>

### 📉 CONTEXT EFFICIENCY

**Codebase:** 150,000 lines

**Typical task loads:**
• ~1,500 lines (with system)
• ~10-15k lines (without)

<br/>

**Result:**
• Faster responses
• Fewer mistakes
• Better guideline adherence
• Follows a real workflow

</div>
</div>

---

<!--
Speaker Notes: Five principles you can use for your own projects.

One - structure by role and phase. Different tasks need different context.

Two - load docs just-in-time, not all upfront. Timing matters as much as content.

Three - use specialized agents for focused tasks. Narrow context means better results.

Four - use hooks to enforce rules automatically. Automation beats repetition.

Five - create clear communication boundaries. Roles communicate but don't overlap.

These aren't specific to INAV. They work for any large codebase.

And you can adopt them incrementally.

Start with role separation. Add JIT guides. Build agents as you need them.

You don't need to build everything at once.

Start small and scale.
-->

# 5 Principles You Can Use

### ✓ 1. STRUCTURE BY ROLE AND PHASE
   ↳ Manager/Developer/Release

### ✓ 2. LOAD DOCS JUST-IN-TIME
   ↳ CRITICAL-BEFORE-* guides

### ✓ 3. USE SPECIALIZED AGENTS
   ↳ inav-builder, test-engineer

### ✓ 4. ENFORCE WITH HOOKS
   ↳ Intercepting 'make' commands

### ✓ 5. CLEAR COMMUNICATION BOUNDARIES
   ↳ Task assignment files

<br/>

**These patterns work for any large codebase**

---

<!--
Speaker Notes: The system uses Claude Code to improve itself.
Most of what you've seen here is was written by Claude, with my guidance.

When we kept manually looking up MSP messages, I wanted an agent that just knows about the MSP protocol.
So I used another agent, the create-agent agent to create an MSP protocol agent.
It researched the protocol, designed a new msp-expert agent, wrote the agent file, and updated the docs.

The system actually improved itself.

Also, every guide has a lessons-learned section at the end.

When Claude discovers something important - like "always use inav-architecture before Grep" or "lock files need timestamps for debugging" - it adds that to the guide.

Future sessions benefit automatically.

It documents what it learns along the way.
-->

# Self-Improvement

<div class="columns">
<div>

### Creates Its Own Tools

**create-agent** builds new agents

User: "We keep looking up MSP messages"

Claude:
1. Researches MSP docs
2. Designs msp-expert agent
3. Writes agent (271 lines)
4. Updates README

Recursive improvement - an agent creating another agent.
Using Claude to build better Claude tools.

</div>
<div>

### Lessons Learned

Guides have self-documentation:

```markdown
### Lessons Learned

- **Lock file format**: Include
  timestamp for debugging

- **inav-architecture first**:
  Use before Grep - saves 10min

- **SITL directory**: Use
  build_sitl/ not build/
```

**It documents what it learns**

</div>
</div>

---

<!--
Speaker Notes: You can clone this and adapt it for your project.

The twelve-step workflow? That's universal for most development projects. Same steps whether you're working on firmware, web apps, data science, or infrastructure.

You can reuse the structure.

Just customize the content.

Clone the directories. Use Calude to update the guides with your build commands and test frameworks. Create agents for your specific stuff.

The cool part? Use the create-agent agent to help build your new agents.

It'll research your docs and write good agents for you.

And the lessons-learned sections mean the system improves as you use it.

The same concept also applies beyond coding. Developing this presentation followed a similar process with feedback loops and iterative refinement.

These patterns have worked well.

You can adapt them to your codebase.
-->

# Adapt for Your Project

<div class="columns">
<div>

### 🎯 UNIVERSAL WORKFLOW

**12 steps work for most development projects**
Firmware, web apps, data science...

**The STRUCTURE is reusable**
✓ Role separation
✓ JIT documentation
✓ Agent pattern
✓ Hook enforcement

**The CONTENT needs customization**
✗ Your build commands
✗ Your test frameworks
✗ Your specific agents

</div>
<div>

### 📋 GETTING STARTED

**Phase 1:** Role separation

**Phase 2:** JIT guides

**Phase 3:** First agent

**Phase 4:** Add hooks

*Can be done incrementally over weeks or months*

<br/>

**Examples:**
Python/Django, React/TypeScript, Rust

</div>
</div>

### Clone `.claude/` and `claude/`, then customize 

---

<!--
Speaker Notes: Thank you for your time!

I'm happy to answer questions.

One thing I'm curious about - would people find it useful to have a separate generic template repository?

Right now this is all in the INAV repo, which works great as a complete example.

But I'm wondering if there's interest in a clean "claude-code-template" repository with just the structure and patterns, that you could clone and customize for your own projects.

Show of hands - how many people are thinking "I'd like to adapt this for my project"?

And of those, would you prefer to fork the INAV repo and customize it, or would you want a clean template repo to start from?

I've analyzed the options in detail - there are pros and cons to each approach.

If there's enough interest, I can extract the generic structure into a separate repo.

[Pause for responses/discussion]

Feel free to reach out on GitHub if you want to discuss adaptation approaches or have questions about implementing this for your project.
-->

# Thank You!

## Next Steps

**Want to try this?**
1. Clone github.com/sensei-hacker/inav-claude
2. Read claude/README.md
3. Check claude/examples/ for templates
4. Open an issue if you need help

## Questions?

<div style="text-align: center; margin-top: 2em;">

**Repository:** github.com/sensei-hacker/inav-claude
**Contact:** sensei-hacker on GitHub

<br/>

*This is how you make Claude actually follow your process*

</div>

---

# Backup: File Structure

<div class="diagram" style="font-size: 0.6em;">

inavflight/
├── .claude/                    # Claude Code configuration
│   ├── settings.json           # Hooks, permissions
│   ├── agents/                 # 10 agents, 3,301 lines
│   │   ├── inav-builder.md
│   │   ├── test-engineer.md
│   │   └── msp-expert.md
│   ├── skills/                 # 31 reusable workflows
│   └── hooks/                  # Enforcement scripts
│
├── claude/                     # Role-specific workspaces
│   ├── manager/
│   │   └── README.md           # 1,200 lines of context
│   ├── developer/
│   │   ├── README.md           # 2,500 lines of context
│   │   └── guides/
│   │       ├── CRITICAL-BEFORE-CODE.md      (104 lines)
│   │       ├── CRITICAL-BEFORE-TEST.md      (113 lines)
│   │       ├── CRITICAL-BEFORE-COMMIT.md    (105 lines)
│   │       └── CRITICAL-BEFORE-PR.md        (171 lines)
│   ├── projects/
│   │   ├── INDEX.md            # Active projects
│   │   └── completed/          # 78 completed
│   └── locks/                  # Concurrency control
│
└── CLAUDE.md                   # Entry point (role selection)

</div>

---

# Backup: Limitations & Tradeoffs

<div class="columns">
<div>

### Setup Cost
- Initial structure takes time to build
- Need to maintain documentation

### Not Perfect
- Still requires some human oversight
- Context engineering isn't magic

</div>
<div>

### Best For
- Large codebases (50k+ lines)
- Repeated workflows
- Multiple contributors

### Overkill For
- Small scripts
- One-off projects
- Simple codebases

</div>
</div>
