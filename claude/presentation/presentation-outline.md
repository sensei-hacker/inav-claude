# Context Engineering for Claude Code: The INAV-Claude Project

**Presentation by Sensei**
**Duration:** ~10 minutes (10 slides, ~100 words per slide)
**Tone:** Informal, technical
**Audience:** Developers interested in LLM workflows

---

## Slide 1: The Problem - Context is Hard

**Visual:** Screenshot of Claude with a massive wall of text in context

**Speaker Notes (~100 words):**

So here's the problem - when you're working on a complex codebase with Claude Code, you run into this fundamental tension. Claude has a huge context window, right? But that doesn't mean you should dump everything into it. I kept running into the same issues: Claude would forget to check lock files, would skip testing, would use `make` directly instead of the proper build scripts. Or worse - I'd paste in the entire 5000-line coding standards document, and Claude would just gloss over the critical parts. The problem isn't the AI - it's about getting the RIGHT information at the RIGHT time. That's what context engineering is all about.

---

## Slide 2: The Solution - Context Engineering

**Visual:** Diagram showing the flow:
```
User Request → Role Selection → Load Role-Specific Guides →
Execute with Specialized Agents → Check with Hooks → Success
```

**Speaker Notes (~100 words):**

The solution is what I call "context engineering" - deliberately structuring information so Claude sees exactly what it needs, when it needs it. The key insight is that different tasks need different context. When you're about to compile code, you need build instructions. When you're creating a PR, you need testing checklists. When you're searching firmware code, you need architecture guidance. So I built a system with five key pieces: role separation, just-in-time documentation, specialized agents that encapsulate knowledge, reusable skills, and hooks that inject context or enforce rules. Let me show you how each piece works.

---

## Slide 3: Roles - Separation of Concerns

**Visual:** Directory tree showing:
```
claude/
├── manager/     (Planning, tracking, assignments)
├── developer/   (Implementation, testing, coding)
├── release-manager/ (Builds, releases, artifacts)
└── security-analyst/ (Security review, crypto analysis)
```

**Speaker Notes (~100 words):**

First, role separation. Every conversation with Claude starts with: "Which role should I take on today?" This isn't just organizational theater - it's fundamental to context management. The manager role loads guides about project tracking and task assignment. The developer role loads coding standards, build instructions, and testing procedures. Each role has its own inbox/outbox email system for communication. This means when Claude is in developer mode, it doesn't have the manager's project tracking documentation cluttering its context. And the manager never sees low-level build instructions. Each role gets exactly the context it needs, nothing more.

---

## Slide 4: Just-In-Time Documentation - The 12-Step Workflow

**Visual:** The 12-step developer workflow with guide loading points highlighted:
```
Developer 12-Step Process:
1. Check inbox
2. Read task
3. Create git branch           ← CRITICAL-BEFORE-CODE loads here
4. Reproduce bug (test fails)  ← CRITICAL-BEFORE-TEST
5. Implement fix               ← guides/coding-standards.md
6. Compile
7. Verify fix (test passes)    ← CRITICAL-BEFORE-TEST
8. Commit changes              ← CRITICAL-BEFORE-COMMIT
9. Create PR                   ← CRITICAL-BEFORE-PR
10. Check bot suggestions
11. Report completion
12. Archive assignment

Each step loads ONLY the guidance needed for that step!
```

**Speaker Notes (~100 words):**

Now the really clever bit - just-in-time documentation tied to workflow phases. The developer follows a 12-step process, and context loads at specific steps. Step 3 creating a branch? CRITICAL-BEFORE-CODE loads: "check lock files, use inav-architecture agent before searching." Step 4 and 7 testing? CRITICAL-BEFORE-TEST loads with testing philosophy. Step 8 committing? CRITICAL-BEFORE-COMMIT loads with git best practices. Step 9 creating PR? CRITICAL-BEFORE-PR mandates code review. Each guide is maybe 100 lines - short, focused checklists that appear exactly when needed. No giant "how to do everything" document. The guides even have self-improvement sections where Claude adds lessons learned.

---

## Slide 5: Specialized Agents - Narrow Context

**Visual:** Grid of agent cards:
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ inav-builder    │  │ test-engineer   │  │ msp-expert      │
│ Builds firmware │  │ Runs tests      │  │ MSP protocol    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ inav-architecture│  │ settings-lookup │  │ sitl-operator   │
│ Find code paths │  │ CLI parameters  │  │ SITL lifecycle  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Speaker Notes (~100 words):**

Specialized agents are where context engineering really shines. Each agent is a sub-process with narrow, specific knowledge. The inav-builder agent knows everything about CMake, cross-compilation, and linker flags - but nothing about mission planning. The msp-expert agent knows the MSP protocol inside and out - but doesn't load the entire firmware codebase. When you need to build SITL, you spawn the builder agent, it does its job with focused context, returns the result, and disappears. This means the main Claude session doesn't have 10,000 lines of build system documentation. The agents are proactive - they're automatically invoked when their expertise is needed.

---

## Slide 6: Skills - Reusable Workflows

**Visual:** Code snippet showing skill invocation:
```
User: "/start-task fix GPS bug"

Claude internally:
1. Check/acquire lock files
2. Create git branch: fix/gps-bug
3. Create project directory
4. Send assignment email
5. Load developer guides
```

**Speaker Notes (~100 words):**

Skills are like macros for complex workflows. They encapsulate multi-step procedures that happen frequently. The `/start-task` skill handles all the setup: checking for conflicts with other work, acquiring lock files, creating a git branch, setting up project directories, and sending the assignment email to kick off the developer role. The `/create-pr` skill handles the PR workflow: reviewing changes, drafting the PR description based on commit history, running code review, and creating the actual PR. Each skill has its own markdown document with detailed instructions. When you invoke a skill, Claude loads just that skill's documentation, executes it, and moves on. Clean, focused context.

---

## Slide 7: Hooks - Context Injection & Guardrails

**Visual:** Hook execution flow:
```
Claude wants to run: cmake .. && make SITL
                          ↓
            PreToolUse Hook intercepts
                          ↓
        "Use inav-builder agent instead!"
                          ↓
         Additional context injected:
         "Never use cmake/make directly"
```

**Speaker Notes (~100 words):**

Hooks are the enforcement mechanism. There's a PreToolUse hook written in Python that intercepts every tool call before execution. When Claude tries to run a direct build command like `make SITL`, the hook catches it and says "use the inav-builder agent instead" - and it injects that reminder into Claude's context. The hook also manages permissions - checking tool_permissions.yaml to allow, deny, or ask about commands. This prevents Claude from accidentally running destructive operations or skipping important steps. There's also a SessionStart hook that verifies the role-selection happened. Hooks are like guardrails that keep Claude on the right path.

---

## Slide 8: Communication System - Clear Information Flow

**Visual:** Email flow diagram:
```
Manager creates task
    ↓
manager/email/sent/ → copy → developer/email/inbox/
                            ↓
                    Developer implements
                            ↓
developer/email/sent/ → copy → manager/email/inbox/
    ↓
Manager updates project tracking
```

**Speaker Notes (~100 words):**

The communication system might seem quaint - "email folders"? Really? But it's brilliant for context management. When the manager assigns a task, it creates a structured markdown file in developer/email/inbox. That file has everything the developer needs: problem description, success criteria, related files. When the developer finishes, they write a completion report. This creates a paper trail that's both human-readable and machine-parseable. More importantly, it enforces role boundaries. The developer can't directly edit the project tracking index - they have to report back. This prevents context pollution where the developer loads all the project management documentation unnecessarily.

---

## Slide 9: Real Example - Fix Terrain Data Loading

**Visual:** Split screen showing:
- Left: Project summary.md
- Right: Key steps taken

**Speaker Notes (~100 words):**

Let me show you a real project. User reports: "terrain data doesn't load in the configurator." The manager creates a task, puts it in developer inbox. Developer role starts, reads CRITICAL-BEFORE-CODE which says use the test-engineer agent. The test-engineer agent (using Chrome DevTools MCP) navigates the UI, checks console errors, finds the issue: a function is commented out. Developer investigates, finds it was disabled during an ESM migration. Implements the fix using Chart.js v4, runs the inav-code-review agent to check for issues, creates PR. Total context loaded? Maybe 5000 lines across the whole workflow. Compare that to loading the entire 100k-line codebase upfront.

**Timeline:** Created and completed same day (2026-01-12)
**PR:** #2518
**Key agents used:** test-engineer, inav-builder, inav-code-review

---

## Slide 10: Results & Takeaways

**Visual:** Stats panel:
```
📊 Projects Completed: 78
🎯 Success Rate: High
📉 Context Waste: Minimized
🔄 Process Consistency: Enforced
```

**Speaker Notes (~100 words):**

So what did this get us? Seventy-eight completed projects tracked so far. But more importantly - Claude consistently follows best practices now. It doesn't forget to test. It doesn't skip code review. It uses the right agents automatically. The key takeaways: One, structure your information by role and phase. Two, load documentation just-in-time, not all upfront. Three, use specialized sub-agents for focused tasks. Four, use hooks to enforce critical rules. Five, create clear communication boundaries between roles. This isn't specific to INAV - you can apply these patterns to any large codebase. Context engineering turns Claude from a smart assistant into a reliable team member.

**Links:**
- GitHub: github.com/iNavFlight/inav (firmware)
- Project: ~/inavflight/.claude/ and ~/inavflight/claude/ (structure)

---

## Appendix: File Structure Overview

For reference, here's the key directory structure:

```
inavflight/
├── .claude/                    # Claude Code configuration
│   ├── settings.json           # Hooks, permissions, sandbox
│   ├── agents/                 # Specialized agent definitions
│   │   ├── inav-builder.md
│   │   ├── test-engineer.md
│   │   ├── msp-expert.md
│   │   └── ...
│   ├── skills/                 # Reusable workflow skills
│   │   ├── start-task/
│   │   ├── create-pr/
│   │   └── ...
│   └── hooks/                  # Hook scripts
│       ├── pre_tool_use_hook.py
│       └── tool_permissions.yaml
│
├── claude/                     # Role-specific workspaces
│   ├── manager/
│   │   ├── README.md           # Manager role guide
│   │   └── email/              # Inbox/outbox/sent
│   ├── developer/
│   │   ├── README.md           # Developer role guide
│   │   ├── guides/             # Just-in-time guides
│   │   │   ├── CRITICAL-BEFORE-CODE.md
│   │   │   ├── CRITICAL-BEFORE-COMMIT.md
│   │   │   ├── CRITICAL-BEFORE-PR.md
│   │   │   └── CRITICAL-BEFORE-TEST.md
│   │   ├── workspace/          # Active task directories
│   │   └── email/              # Inbox/outbox/sent
│   ├── projects/               # Project tracking
│   │   ├── INDEX.md            # Active projects
│   │   ├── active/             # In-progress projects
│   │   └── completed/          # Finished projects
│   ├── locks/                  # Concurrency control
│   └── ...
│
├── CLAUDE.md                   # Entry point - role selection
├── inav/                       # Firmware codebase
└── inav-configurator/          # GUI codebase
```

---

## Questions?

**Contact:** sensei-hacker (GitHub)
**Repository:** github.com/iNavFlight/inav

---

## Bonus: Implementation Tips

If you want to implement this in your own project:

1. **Start Small:** Begin with role separation (CLAUDE.md → role README.md)
2. **Add Just-in-Time Guides:** Create CRITICAL-BEFORE-* guides for key workflow points
3. **Identify Bottlenecks:** Where does Claude repeatedly need the same specialized knowledge? → Create an agent
4. **Workflow Patterns:** What multi-step procedures happen frequently? → Create a skill
5. **Enforcement:** What rules does Claude forget? → Add hooks
6. **Iterate:** Add lessons learned sections to guides, improve based on real usage

The beauty is you can adopt these patterns incrementally - you don't need to build the whole system at once.
