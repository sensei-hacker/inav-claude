# Presentation Review: Context Engineering for Claude Code

This document identifies areas for improvement in the presentation slides and speaker notes.

---

## 1. Opening Transition (Slides 2-3)

**Issue:** Abrupt jump from title slide to "The Problem"

**Current:** Title → "Common Problems Without Context Engineering"

**Recommendation:** Add a brief "What This Talk Is About" slide or soften the transition in speaker notes.

**Suggested addition to speaker notes (Slide 2):**
"Today I'm going to show you five principles that solved these problems and made Claude dramatically more effective. But first, let me show you what was going wrong."

---

## 2. Slide 3: Problem Statement Clarity

**Issue:** The checklist items are symptoms, but the root cause isn't immediately clear.

**Current speaker note:** "The problem isn't the AI being forgetful. The problem is information overload combined with poor structure."

**Recommendation:** Make this explicit on the slide itself, not just in speaker notes.

**Suggested slide addition:**
```
### Root Cause: Information Architecture
✓ Not an AI limitation
✓ Structure problem
```

---

## 3. Slide 4: "Why This Happens" - Diagram Truncation

ASCII diagram shows truncated text: "Make sure to a"
This is intentional and should not be "fixed". Lost content is the point of the slide.

---

## 4. Slide 5-6 Transition: Context Reduction Math

**Issue:** Numbers don't connect clearly between slides.

**Slide 5 says:** "4,500 lines → 2,500 lines (so far)"
**Slide 5 note mentions:** "forty-five hundred lines down to twenty-five hundred"

**Problem:** Where does 4,500 come from? Earlier you said:
- Manager: 1,200 lines
- Developer: 2,500 lines
- Release: 1,000 lines

**Recommendation:** Make the "before" number explicit.

**Suggested addition to Slide 5:**
```
**WITHOUT roles:** All docs loaded = 4,500 lines
**WITH roles:** Only relevant docs = 2,500 lines max
```

---

## 5. Slide 7: Missing Connection

**Issue:** Slide 5 ends with faded text "⚠️ Important Info Still Missing" but Slide 7 jumps to Communication System without addressing what was missing.

**Current flow:**
- Role Separation (saves 2k lines)
- [implied gap]
- Communication System

**Recommendation:** Add transition acknowledging the gap.

**Suggested speaker note addition (Slide 7 opening):**
"Roles alone aren't enough. Even with 2,500 lines, the developer still loads everything upfront. That's where the communication system comes in..."

---


## 7. Slide 9: Agent Definition Missing

**Issue:** First mention of "agents" without defining what they are in Claude Code context.

**Current:** "That's where agents shine."

**Problem:** Audience may confuse with AI agents, autonomous agents, or other meanings.

**Recommendation:** Add one-line definition before diving into details.

**Suggested addition to speaker notes:**
"Agents in Claude Code are specialized subprocesses - separate Claude instances with their own focused context. Think of them as expert consultants that get called in for specific tasks."

---

## 8. Slide 10: Agent Math Unclear

**Issue:** "33 hundred lines representing 26 thousand lines" - what's the relationship?

**Current:** "Ten agents total, thirty-three hundred lines of definitions representing twenty-six thousand lines of knowledge."

**Recommendation:** Explain the compression ratio concept.

**Suggested clarification:**
"Each agent definition is short - maybe 300 lines. But that 300-line definition *represents* knowledge from thousands of lines of documentation that the agent can reference without loading it into the main context."

---

## 9. Slide 11: System Diagram Missing Labels

**Issue:** Diagram flow isn't labeled with "WHY" each step matters.

**Current:** Just shows flow from user → role → skill → workflow → agents → hooks

**Recommendation:** Add benefit annotations to the right side.

**Suggested addition:**
```
[Focused Context]     ← Only 2.5k lines loaded
[Reusable Workflow]   ← Don't repeat process
[Narrow Expertise]    ← Separate context windows
[Guardrails]          ← Prevent mistakes
```

*(Actually, I see these ARE there - but could be more prominent)*

---

## 10. Slide 12: Hook Example - Missing Setup Context

**Issue:** Example shows "runs make SITL" but audience doesn't know why that's wrong.

**Current:** "Wrong directory / Missing flags" but that's not explained earlier.

**Recommendation:** Use a better example of building incorrectly, or say "runs make SITL directly, with improper flags"

---

## 11. Slide 13: Real Example Timeline Unclear

**Issue:** "Screenshots advancing every 10 seconds (1:40 total)" but there are no actual screenshots.

**Current:** Lists 10-second increments as text descriptions.

SCREENSHOTS WILL BE ADDED

**Alternative format to add in case the screenshots don't work well:**
```markdown
### Real Example: Fix Terrain Data Not Loading

**Problem:** User reports chart not displaying

**Process:**
1. Manager creates 80-line task assignment
2. Developer reads task, CRITICAL-BEFORE-CODE loads
3. Spawns test-engineer agent with Chrome DevTools
4. Agent finds root cause: plotElevation() commented out
5. Developer implements Chart.js v4 fix
6. Runs inav-code-review agent
7. Creates PR #2518

**Timeline:** Same-day completion
**Context:** ~1,500 lines vs. 10-15k without system
```

---

## 13. Slide 15: Principles Are Abstract

**Issue:** Five principles listed but connection to previous content isn't explicit.

**Current:** Just lists the principles.

**Recommendation:** Connect each principle back to a slide/example shown earlier.

**Suggested format:**
```markdown
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
```

---

## 14. Slide 16: Self-Improvement - Create-Agent Meta-Confusion

**Issue:** "I used the create-agent agent" might confuse audience.

**Current:** "When we kept manually looking up MSP messages, I used the create-agent agent to research..."

**Recommendation:** Clarify the meta-layer.

**Suggested speaker note addition:**
"Yes, that sounds recursive - I'm using an agent to create another agent. But that's the power of the system: create-agent is itself a specialist that knows how to research documentation, design agent interfaces, and follow best practices. It's using Claude to build better Claude tools."

---

## 15. Slide 17: Adaptation Timeline Too Prescriptive

**Issue:** "Week 1... Week 2... Week 3..." suggests rigid timeline.

**Current:** Implies 4-week adoption schedule.

**Recommendation:** Make it more flexible or explain it's an example.

**Suggested change:**
```markdown
### 📋 GETTING STARTED

**Phase 1:** Role separation
**Phase 2:** JIT guides
**Phase 3:** First agent
**Phase 4:** Add hooks

*Can be done incrementally over weeks or months*
```

---


**Suggested addition after Slide 1:**
```markdown
# Quick Context: INAV Project

**INAV:** Open-source drone autopilot firmware
**Codebase:** 150k lines of C99 (firmware) + JavaScript (configurator)
**SITL:** Software-In-The-Loop simulator for testing without hardware
**MSP:** MultiWii Serial Protocol - communication with flight controller

*Don't worry about the specifics - focus on the patterns*
```

---

## 18. Missing: What Doesn't Work Well

**Issue:** Presentation is entirely positive - no limitations or challenges discussed.

**Recommendation:** Add brief acknowledgment of limitations for credibility.

**Suggested addition (perhaps as backup slide):**
```markdown
# Limitations & Tradeoffs

### Setup Cost
- Initial structure takes time to build
- Need to maintain documentation

### Not Perfect
- Still requires some human oversight
- Context engineering isn't magic

### Best For
- Large codebases (50k+ lines)
- Repeated workflows

### Overkill For
- Small scripts
- One-off projects
```

---

## 20. Call to Action Unclear

**Issue:** Slide 18 ends with "Questions?" but doesn't guide next steps clearly.

**Current:** Provides GitHub link but unclear what to do with it.

**Recommendation:** Add explicit next steps.

**Suggested addition to Slide 18:**
```markdown
## Next Steps

**Want to try this?**
1. Clone github.com/sensei-hacker/inav-claude
2. Read claude/README.md
3. Check claude/examples/ for templates
4. Open an issue if you need help

**Questions?** Ask now or reach out on GitHub!
```

---

## 21. Speaker Notes Timing Calibration

**Issue:** No indication of how long each section should take.

**Recommendation:** Add timing guidance to help speaker pace.

**Example additions:**
- Slide 1: [1 minute]
- Slides 2-4: [2 minutes - problem setup]
- Slides 5-8: [3 minutes - solutions part 1]
- Slides 9-12: [3 minutes - solutions part 2]
- Slide 13: [2 minutes - example]
- Slides 14-17: [3 minutes - results and principles]
- Slide 18: [2 minutes - Q&A]

**Total: ~14 minutes + Q&A**

---

## Summary: Priority Improvements

### High Priority (Fix Before Presenting)
1. **Slide 3:** Move root cause to slide, not just notes
3. **Slide 13:** Restructure "Real Example" - current format is confusing
4. **Add:** Technical terms primer after Slide 1

### Medium Priority (Improves Clarity)
5. **Slides 5-6:** Clarify context reduction math
6. **Slide 9:** Define "agents" before using term
7. **Slide 15:** Connect principles back to examples
8. **Slide 18:** Add explicit next steps / call to action

### Low Priority (Polish)
9. **Slide 7:** Add transition about what roles don't solve
11. **Slide 17:** Make timeline more flexible
12. **Add backup slide:** Limitations & Tradeoffs

### Optional
14. **All slides:** Add timing guidance for pacing

---

## Overall Assessment

**Strengths:**
- Clear narrative arc (problem → solution → results → principles)
- Good use of concrete examples
- Speaker notes are detailed and helpful
- Visual variety keeps it interesting

**Main Weaknesses:**
- Some transitions feel abrupt
- Technical jargon not always introduced
- Entirely positive (no limitations discussed)
- Real example section needs restructuring

**Recommendation:** This is a strong presentation with solid content. The improvements above would increase clarity and professionalism, but even without them it would work reasonably well. Prioritize the High/Medium items for maximum impact.
