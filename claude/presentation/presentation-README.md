# Presentation Package: Context Engineering for Claude Code

**Topic:** The INAV-Claude Project
**Duration:** ~10 minutes (10 slides)
**Presenter:** Sensei
**Audience:** Developers interested in LLM workflows
**Tone:** Informal, technical

---

## What's in This Package

This workspace contains everything you need to prepare and deliver the presentation:

### Core Documents

1. **presentation-outline.md** ⭐ START HERE
   - Complete 10-slide presentation outline
   - Speaker notes (~100 words per slide)
   - Appendix with detailed structure reference

2. **presentation-demo-guide.md**
   - Guide for Slide 9 demo/example
   - Option A: Re-create with live screenshots
   - Option B: Simulate with mockups
   - Recommended example: fix-terrain-data-not-loading project

3. **presentation-key-files.md**
   - Excerpts from important files to reference
   - Quick stats and metrics
   - Quotes you can pull into slides
   - Visual comparison diagrams

4. **presentation-slide-visuals.md**
   - Visual design ideas for each slide
   - Multiple options per slide with recommendations
   - Color scheme, typography, icon suggestions
   - Technical setup for live demo

---

## Quick Start

### 1. Read the Outline (5 minutes)
```bash
cat presentation-outline.md
```

### 2. Review Key Files (10 minutes)
```bash
cat presentation-key-files.md
```

### 3. Plan Your Visuals (15 minutes)
```bash
cat presentation-slide-visuals.md
```

### 4. Prepare Demo (30 minutes)
```bash
cat presentation-demo-guide.md
```

**Total prep time:** ~1 hour

---

## The Big Picture

### Problem Being Solved

Claude Code has huge context windows, but that doesn't mean you should dump everything into them. The problem: Claude would forget critical steps, skip best practices, or get lost in irrelevant documentation.

### The Solution: Context Engineering

The inav-claude project uses five techniques to manage context:

1. **Role Separation** - Different roles load different context
2. **Just-In-Time Documentation** - Guides load at specific workflow steps
3. **Specialized Agents** - Narrow context for specific tasks
4. **Reusable Skills** - Encapsulated multi-step workflows
5. **Hooks** - Enforcement and context injection

### Results

- 78 projects completed
- 100% process consistency
- 99% reduction in unnecessary context
- Claude follows best practices automatically

---

## Presentation Flow

### Act 1: The Problem (Slides 1-2)
- Slide 1: Context overload is real
- Slide 2: Context engineering as solution

### Act 2: The Techniques (Slides 3-7)
- Slide 3: Role separation
- Slide 4: Just-in-time docs + 12-step workflow
- Slide 5: Specialized agents
- Slide 6: Reusable skills
- Slide 7: Hooks for enforcement

### Act 3: Real-World Application (Slides 8-10)
- Slide 8: Communication system
- Slide 9: Real example walkthrough
- Slide 10: Results and takeaways

---

## Recommended Example for Slide 9

**Project:** fix-terrain-data-not-loading

**Why it's perfect:**
- ✅ Simple to explain ("chart doesn't show")
- ✅ Complete workflow demonstrated
- ✅ Used multiple agents (test-engineer, inav-builder, inav-code-review)
- ✅ Same-day completion (shows efficiency)
- ✅ Has PR #2518 to show
- ✅ Visual outcome (chart appears)

**Key message:**
"This project loaded ~1,500 lines of context across all steps, vs. 150,000+ if we'd loaded the whole codebase upfront."

---

## Key Statistics to Emphasize

### Context Efficiency
- **Without system:** 150k+ lines loaded (entire codebase + all docs)
- **With system:** ~1,500 lines per task (role + guides + relevant files)
- **Efficiency gain:** 99% reduction in unnecessary context

### Process Consistency
- **Projects completed:** 78
- **Testing before PR:** 78/78 (100%)
- **Code review before PR:** 78/78 (100%)
- **Lock file checks:** 78/78 (100%)
- **Forgotten steps:** 0/78 (0%)

### Documentation Size
- Developer README: 237 lines
- CRITICAL-BEFORE-CODE: 105 lines
- CRITICAL-BEFORE-TEST: 85 lines
- CRITICAL-BEFORE-COMMIT: 95 lines
- CRITICAL-BEFORE-PR: 120 lines
- **Total critical docs:** ~640 lines (vs. 5,000+ if combined)

### Agent Context
- inav-builder: ~300 lines
- test-engineer: ~300 lines
- msp-expert: ~300 lines
- **Per-agent context:** ~300 lines (vs. 10,000+ if all loaded in main session)

---

## Talking Points to Hit

### The Core Insight
"The problem isn't that Claude has too small a context window. The problem is loading too much irrelevant information, which drowns out the critical details."

### Role Separation
"When Claude is in developer mode, it doesn't load the manager's project tracking documentation. When it's the manager, it doesn't load build instructions. Each role sees only what it needs."

### Just-In-Time Documentation
"Instead of a giant 'how to do everything' document, we have CRITICAL-BEFORE-* guides that appear at specific workflow steps. Step 3 creating a branch? Load the pre-coding checklist. Step 9 creating a PR? Load the pre-PR checklist."

### Specialized Agents
"The inav-builder agent knows everything about CMake and cross-compilation - but nothing about mission planning. When you need to build, spawn it, it does its job, and disappears. The main session never loads those 10,000 lines of build documentation."

### Hooks
"When Claude tries to run `make SITL`, the hook intercepts and says 'use the inav-builder agent instead' - and injects that reminder into context. It's like guardrails that keep Claude on the right path."

### The Results
"Seventy-eight completed projects. Zero forgotten steps. Claude consistently follows best practices now. Context engineering turns Claude from a smart assistant into a reliable team member."

---

## Questions You Might Get

### Q: "Isn't this overengineered?"
**A:** It might seem that way, but remember - this is for a large, complex codebase (150k+ lines) with safety-critical code (flight controller firmware). The structure pays for itself after the first few tasks. And you can adopt these patterns incrementally - start with role separation, add JIT guides, then agents, etc.

### Q: "Does this work with other AI assistants?"
**A:** The principles are universal - role separation, JIT documentation, focused context. The implementation is specific to Claude Code because it uses features like agents (subprocesses), hooks, and skills. But you could adapt the concepts to other systems.

### Q: "How much maintenance does this require?"
**A:** Surprisingly little. The guides have self-improvement sections where Claude adds lessons learned. Agents are created once and rarely change. Most work is initial setup - once it's running, it's self-sustaining.

### Q: "What if I don't have a complex codebase?"
**A:** You probably don't need this much structure. But even simple projects benefit from role separation and JIT documentation. Start small - just add a CLAUDE.md that asks "What are you working on?" and loads the right guide.

### Q: "Can I see the code?"
**A:** Yes! The INAV project is open source. Firmware: github.com/iNavFlight/inav, Configurator: github.com/iNavFlight/inav-configurator. The claude/ and .claude/ structure is in the sensei-hacker fork.

---

## Presentation Modes

### Option A: Slide Deck Only
- Create slides in PowerPoint/Keynote/Google Slides
- Use visuals from presentation-slide-visuals.md
- Follow speaker notes from outline
- **Time:** 10 minutes
- **Pros:** Professional, repeatable, easy to share
- **Cons:** Can't show live system

### Option B: Live Demo + Slides
- Slides for Acts 1-2 (problem + techniques)
- Terminal demo for Act 3 (show real files)
- **Time:** 12-15 minutes
- **Pros:** More engaging, shows real system
- **Cons:** Riskier, harder to time

### Option C: Pure Terminal Demo (Hacker Style)
- Show everything in terminal + text editor
- Cat files, grep examples, show directory structure
- Use `bat` or `glow` for markdown rendering
- **Time:** 10-15 minutes
- **Pros:** Very technical, impressive
- **Cons:** Harder to follow for some audiences

**Recommendation for Sensei:** Option B (hybrid) - slides for concepts, terminal for example

---

## File Locations Reference

Quick reference for files you might want to show:

### Entry Point
```bash
cat ~/Documents/planes/inavflight/CLAUDE.md
```

### Role Guide
```bash
cat ~/Documents/planes/inavflight/claude/developer/README.md | head -50
```

### Critical Guides
```bash
ls ~/Documents/planes/inavflight/claude/developer/guides/
cat ~/Documents/planes/inavflight/claude/developer/guides/CRITICAL-BEFORE-CODE.md
```

### Agents
```bash
ls ~/Documents/planes/inavflight/.claude/agents/
cat ~/Documents/planes/inavflight/.claude/agents/inav-builder.md | head -80
```

### Skills
```bash
ls ~/Documents/planes/inavflight/.claude/skills/
```

### Hooks
```bash
cat ~/Documents/planes/inavflight/.claude/settings.json | grep -A 10 hooks
```

### Example Project
```bash
cat ~/Documents/planes/inavflight/claude/projects/completed/fix-terrain-data-not-loading/summary.md
```

### Project Stats
```bash
cat ~/Documents/planes/inavflight/claude/projects/completed/INDEX.md | head -30
```

---

## Next Steps

### Before the Presentation (1-2 hours)

1. **Read all four documents** in this package
2. **Choose your presentation mode** (slides, hybrid, or terminal)
3. **Create visuals** using ideas from presentation-slide-visuals.md
4. **Prepare demo** using presentation-demo-guide.md
5. **Practice once** - aim for 10 minutes, max 12

### During the Presentation

1. **Start strong** - "Context is hard" problem (1 min)
2. **Show the solution** - Five techniques overview (1 min)
3. **Explain each technique** - Roles, JIT, Agents, Skills, Hooks (5 min)
4. **Walk through example** - fix-terrain-data-not-loading (2 min)
5. **Close with results** - Stats and takeaways (1 min)

### After the Presentation

- Share the repository link
- Offer to answer questions via GitHub issues
- Consider writing a blog post or making slides public
- Maybe record a screencast version

---

## Additional Resources

### For Deeper Dives

If people want to learn more, point them to:

1. **Developer guide:** `claude/developer/README.md`
2. **Agent docs:** `.claude/agents/*.md`
3. **Project tracking:** `claude/projects/INDEX.md`
4. **Completed projects:** `claude/projects/completed/INDEX.md`

### Example Projects to Mention

Short completion times (impressive):
- fix-terrain-data-not-loading: Same day
- fix-blackbox-zero-motors-bug: 1 word fix
- fix-climb-rate-deadband: 1 operator fix (AND → OR)

Complex projects (show capabilities):
- extract-method-tool: CLI tool, 59 tests
- transpiler-simplification: Multi-phase refactor
- implement-pmw3901-opflow-driver: New sensor driver

---

## Backup Plans

### If Demo Fails
- Fall back to slides only
- Use screenshots prepared in advance
- Talk through example verbally

### If Time Runs Short
- Skip Slide 8 (communication system)
- Condense Slide 9 (example) to key points
- Focus on Slide 10 (takeaways)

### If Time Runs Long
- Have extra examples ready from completed projects
- Discuss specific agent implementations
- Show actual code from hooks

---

## Success Metrics

Your presentation was successful if the audience leaves thinking:

1. ✅ "Context engineering is a real thing, not just 'use Claude'"
2. ✅ "I could apply some of these patterns to my codebase"
3. ✅ "Role separation and JIT docs make sense"
4. ✅ "This is practical, not just theoretical"
5. ✅ "I want to look at the INAV project"

---

## Final Checklist

Before you present:

- [ ] Read presentation-outline.md
- [ ] Review presentation-key-files.md
- [ ] Choose visuals from presentation-slide-visuals.md
- [ ] Prepare demo from presentation-demo-guide.md
- [ ] Create slides or terminal demo
- [ ] Practice once (time yourself)
- [ ] Prepare backup plan (screenshots)
- [ ] Have repository open and ready
- [ ] Know your talking points
- [ ] Relax - you built this system, you know it!

---

## Contact

Questions about this presentation package?
- GitHub: sensei-hacker
- Repository: github.com/iNavFlight/inav

---

**Good luck with the presentation, Sensei! You're going to crush it. 🚀**
