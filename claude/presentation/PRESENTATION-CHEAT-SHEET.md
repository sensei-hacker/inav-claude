# Presentation Cheat Sheet - Quick Reference

**Print this or keep on second screen during presentation**

---

## Key Statistics (Be Accurate!)

**Agents:**
- Files: 10 agents, 3,301 lines total
- Knowledge: ~26,000 lines represented
- Average: ~330 lines per agent

**Guides (CRITICAL-BEFORE-*):**
- CODE: 104 lines
- TEST: 113 lines
- COMMIT: 105 lines
- PR: 171 lines
- Total: ~600 lines

**Roles:**
- Developer README: 237 lines
- Manager: ~1,200 lines
- Release: ~1,000 lines

**Projects:**
- Completed: 78
- Same-day: 15+
- Duration: 1-3 days average

**Context Efficiency:**
- With system: ~1,500 lines per task
- Without system: ~10-15k scattered lines
- NOT "vs entire 150k codebase" ← avoid this claim

---

## Core Messages (What They Should Remember)

1. Context is hard even with big windows
2. Five techniques: Roles, JIT, Agents, Skills, Hooks
3. Workflow universal - 12 steps work for any software
4. Agents are ephemeral - spawn, work, disappear
5. System self-improves - lessons learned, create-agent
6. Structure reusable - clone and adapt

---

## Slide Order & Time Budget

| # | Topic | Time | Key Point |
|---|-------|------|-----------|
| 1 | Problem | 1m | Checklist of failures |
| 2 | Why | 1m | Info overload diagram |
| 3 | Roles | 1.5m | 4,500→2,500 "so far" |
| 4 | Communication | 1m | Structured task IS workflow |
| 5 | 12 Steps | 1.5m | JIT guides at steps |
| 6 | Agents | 1.5m | Steps CALL agents |
| 7 | Together | 1m | start-task AFTER dev role |
| 8 | Hooks | 1m | Before/after comparison |
| 9 | Example | 1.5m | Screenshots auto-advance |
| 10 | Results | 1.5m | Be realistic! "Very high" |
| 11 | Takeaways | 1m | Five principles |
| 12 | Self-Improve | 1m | create-agent + lessons |
| 13 | Adapt | 1m | Universal workflow |
| **Total** | | **15m** | |

---

## Tricky Spots (Don't Mess These Up!)

### Slide 3
✅ SAY: "So far, roles reduce from 4,500 to 2,500"
✅ SAY: "But that's just the beginning"
❌ DON'T SAY: "That's the final improvement"

### Slide 4
✅ SAY: "Communication IS part of the workflow"
❌ DON'T SAY: "Before diving into the workflow"

### Slide 6
✅ SAY: "Looking back at the 12 steps, notice several just say 'call an agent'"
✅ SAY: "Step 6 compile? Call inav-builder"
❌ DON'T just launch into agents without connecting to workflow

### Slide 7
✅ VISUAL: Developer role THEN /start-task skill
❌ WRONG: /start-task before developer role

### Slide 9
✅ SAY: "Without system: 10-15k lines of scattered docs"
❌ DON'T SAY: "vs 150k entire codebase" or "99% reduction"

### Slide 10
✅ SAY: "Very high consistency" or "Consistently enforced"
✅ SAY: "Vast majority of projects followed workflow"
❌ DON'T SAY: "100% perfect" or "Never fails"
❌ DON'T SAY: "Six months" (no specific timeline)

---

## If You Get Lost

**Problem → Why → Solution Parts 1-5 → Example → Results → Takeaways**

The five solution parts:
1. Roles (separate context)
2. Communication (structured info)
3. 12-step workflow (JIT guides)
4. Agents (narrow knowledge)
5. Skills + Hooks (workflows + enforcement)

Then: Real example, results, how to use it yourself

---

## Files to Show (If Live Demo)

```bash
# Entry point
cat CLAUDE.md

# Developer guide
cat claude/developer/README.md | head -50

# Critical guide
cat claude/developer/guides/CRITICAL-BEFORE-CODE.md | head -30

# Agent example
ls .claude/agents/
cat .claude/agents/inav-builder.md | head -80

# Completed project
cat claude/projects/completed/fix-terrain-data-not-loading/summary.md

# Stats
cat claude/projects/completed/INDEX.md | head -20
```

---

## Color Scheme

**Slide 3 backgrounds (subtle!):**
- Manager: Light blue
- Developer: Light green
- Release: Light orange

**General:**
- Blue = Management
- Green = Development
- Orange = Build/compile
- Red = Errors
- Yellow = Warnings

---

## Example Project Details (Slide 9)

**Project:** fix-terrain-data-not-loading
**Created:** 2026-01-12
**Completed:** Same day (~4 hours)
**PR:** #2518
**Problem:** Terrain chart not displaying
**Root Cause:** plotElevation() commented out during ESM migration
**Fix:** Chart.js v4 integration
**Agents Used:** test-engineer, inav-builder, inav-code-review

---

## Lessons Learned Examples (Slide 12)

Real examples to mention:

1. **Lock file format**: Include timestamp and task name for debugging conflicts

2. **inav-architecture first**: Always use agent BEFORE Grep - saves 10+ minutes

3. **SITL build directory**: Use build_sitl/ not build/ to avoid hardware target conflicts

---

## Adaptation Examples (Slide 13)

**Python/Django:**
- django-model-expert, api-docs-lookup, pytest-runner

**React/TypeScript:**
- component-builder, npm-package-manager, storybook-handler

**Rust:**
- cargo-expert, unsafe-code-reviewer, crates-io-lookup

Key: 12 steps stay same, agents change

---

## Common Questions - Quick Answers

**"Overengineered?"**
→ For 150k line safety-critical code, no. Adopt incrementally.

**"Works with other AI?"**
→ Principles universal, implementation uses Claude Code features.

**"12 steps really universal?"**
→ Yes! Python, Rust, JS - same steps, customize content.

**"Setup time?"**
→ Clone: 1hr, Customize: 1-2hrs, First agent: 30min.

**"Claude builds agents?"**
→ Yes! create-agent researches and writes new agents.

---

## The Money Quote

> "Context engineering turns Claude from a smart assistant into a reliable, professional development team member with consistent process adherence."

---

## Closing Call to Action

"The structure is proven. The patterns scale. Clone the directories, adapt for YOUR codebase, and get the same benefits."

**Repo:** github.com/iNavFlight/inav
**Contact:** sensei-hacker on GitHub

---

## If Time Runs Short

**Skip:** Slide 12 (self-improvement)
**Condense:** Slide 13 (adaptation) - just say "clone and adapt, workflow is universal"
**Focus on:** Slides 10-11 (results + takeaways)

---

## If Time Runs Long

**Add:**
- Show actual hook code
- Demo terminal with file cats
- More project examples
- Discuss agent creation in detail

---

## Backup If Tech Fails

1. Have screenshots pre-made
2. Talk through example verbally
3. Use text-only slides
4. Focus on principles over demos

---

## Final Reminders

✓ Be realistic, not overpromising
✓ Say "very high" not "perfect"
✓ Mention "so far" for roles improvement
✓ Connect agents to 12-step workflow
✓ Emphasize: structure reusable, content customizable
✓ Keep energy up - this is cool stuff!
✓ Pause for questions if time permits
✓ Share repo link at end

---

## Presentation Mode

**Option A:** Slides only (safe, professional)
**Option B:** Slides + terminal demo (engaging)
**Option C:** Pure terminal (hacker style)

**Recommended:** Option B (hybrid)

---

## Success = They Want This For Their Project

If people leave wanting to clone it and adapt it → you win!

---

**You got this! 🚀**
