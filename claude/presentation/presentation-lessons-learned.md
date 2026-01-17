# Lessons Learned: Building Technical Presentations

**Context:** Created presentation about INAV-Claude context engineering
**Date:** 2026-01-12
**For:** Future technical presentations on any topic

---

## 1. Be Realistic, Not Overpromising

**What happened:** Initial draft claimed "100% process consistency" and "six months of use"

**Fix:** Changed to "very high consistency" and removed specific timeline

**Why it matters:** Technical audiences are skeptical. One overpromise destroys credibility.

**For next time:**
- Check all numbers against actual data
- Use "consistently," "usually," "most" instead of "always," "never," "all"
- Compare to realistic baseline, not worst case
- Better to understate than overstate

---

## 2. Flow and Ordering Are Critical

**What happened:** Communication was Slide 8 (late), but it happens before the workflow

**Fix:** Moved to Slide 4, right after roles and before workflow

**Why it matters:** Temporal and conceptual order both matter

**For next time:**
- Think about "what happens when" (temporal)
- Think about "what contains what" (hierarchy)
- Get feedback on slide order early
- Moving one slide can drastically improve clarity

---

## 3. Connect Each Slide to Previous

**What happened:** Slide 6 (Agents) jumped straight into "agents are cool"

**Fix:** Started with "Looking back at the 12 steps, notice several just say 'call an agent'..."

**Why it matters:** Each slide should feel like natural continuation, not random topic

**For next time:**
- Start slides with phrases like:
  - "Looking back at..."
  - "Now let's dig into..."
  - "Remember when I mentioned..."
- Avoid jarring topic changes
- Each slide bridges to next

---

## 4. Visual Type Should Match Content

**What happened:** Different slides needed different visual approaches

**What worked:**
- Problems → Checklist (relatable, scannable)
- Causes → Flow diagram (shows how problem emerges)
- Comparisons → Side-by-side cards
- Processes → Vertical timeline
- Architecture → Relationship diagram
- Impact → Before/after comparison

**For next time:**
- Don't use same visual type for every slide
- Match visual to message type
- Use color strategically (subtle backgrounds, not loud)
- Add personality where appropriate (emojis in before/after)

---

## 5. Presenter Notes vs. Slides Serve Different Purposes

**What worked:**
- Presenter notes: ~100 words, full sentences, what you'll say
- Slides: Minimal text, visual representation, one main idea

**For next time:**
- Write speaker notes first (what you'll say)
- Then create visual that supports (not duplicates)
- If slide has >50 words, it's too wordy
- Numbers should be large on slides
- Diagrams > paragraphs, always

---

## 6. Remove Internal Commentary from Speaker Notes

**What happened:** Notes had phrases like "which IS part of the workflow" - that was me explaining to myself based on feedback

**Fix:** Removed meta-commentary that audience doesn't need

**Why it matters:** Speaker notes are what you'll SAY, not what you're THINKING

**For next time:**
- Read speaker notes aloud - if it sounds weird, it is
- Remove reminders to yourself
- Put internal notes in separate cheat sheet
- Speaker notes should sound natural when spoken

---

## 7. "So Far" Signals More Coming

**What happened:** Slide 3 showed roles reduce context from 4,500 to 2,500 lines

**Fix:** Added "So far, roles reduce... But that's just the beginning"

**Why it matters:** Sets expectation that more improvements are coming

**For next time:**
- Use phrases like "so far," "but that's just the beginning"
- Build anticipation for later slides
- Show incremental improvements, not just final result
- Each technique adds to previous

---

## 8. Self-Improvement and Meta Content Can Be Powerful

**What happened:** Added slides about create-agent (Claude building agents) and lessons learned sections

**Why it worked:** Shows system evolves, not just static tool

**For next time:**
- Meta content resonates ("system that improves itself")
- Show examples of system outputs
- Demonstrate growth over time
- "How it was built" can be as interesting as "what it does"

---

## 9. End with Actionable Takeaways

**What happened:** Initially ended with just results

**Fix:** Added Slide 13 about adapting for your project (clone structure, customize content, week-by-week guide)

**Why it matters:** Audience wants "what can I do with this?"

**For next time:**
- Always end with clear call to action
- Show concrete path to adoption
- Provide examples of adaptation (Python/Rust/JS)
- Make it feel achievable, not overwhelming

---

## 10. Context Matters: What's Universal vs. Specific

**What happened:** Realized the 12-step workflow is universal for software, but content needs customization

**Why it matters:** Helps audience see both "I can use this" and "I need to adapt it"

**For next time:**
- Explicitly call out what's reusable (structure, patterns)
- Explicitly call out what needs customization (content, specifics)
- Use examples from different domains (Python, Rust, JS)
- "Clone and adapt" is clearer than "do exactly this"

---

## 11. Multiple Support Documents Beat One Giant File

**What worked:**
- Main outline (slides + notes)
- Demo guide (how to create examples)
- Key facts reference (stats)
- Cheat sheet (quick reference during talk)
- Final summary (overview)

**For next time:**
- Separate concerns into files
- Each doc has single clear purpose
- Main outline stays focused
- Details live in reference docs
- Cheat sheet for presenter during talk

---

## 12. Iteration Based on Feedback is Essential

**What happened:** Multiple rounds of feedback, each improving presentation:
- Visual selections
- Slide reordering
- Wording changes
- Realistic claims
- New slides added

**For next time:**
- First draft won't be final - plan for it
- Don't get attached to first version
- Each critique usually improves result
- Keep versions (v1, v2, etc.)
- Sometimes feedback contradicts earlier work - that's okay

---

## 13. Plan Time Budget Per Slide

**What worked:**
- 13 slides for 12-15 minutes
- Most slides: ~1 minute
- Complex slides (example): 1:40
- Simple transitions: 30-45 seconds

**For next time:**
- Budget time upfront
- Not all slides are equal (some need more time)
- Build in 2-3 min buffer
- Know which slides can be skipped if running long
- Know which topics can be expanded if running short

---

## 14. Backup Plans Reduce Stress

**What worked:**
- If screenshots not ready → mockups or text
- If time short → skip Slide 12, condense 13
- If time long → live terminal demo
- If tech fails → slides only

**For next time:**
- Always have Plan B ready
- Know what can be skipped
- Know what can be expanded
- Have low-tech fallback
- Print cheat sheet (don't rely on digital)

---

## 15. The "So What?" Test

**Key insight:** Every slide should answer "Why does this matter?" and "How does this help me?"

**Good examples:**
- Roles → Reduces context from 4,500 to 2,500 (so what: faster, clearer)
- Agents → Main session never loads 26k lines (so what: focused context)
- Hooks → No manual reminders needed (so what: automatic enforcement)

**For next time:**
- Each slide needs clear benefit/impact
- Don't just describe features - show value
- Include concrete numbers where possible
- Answer "why should I care?" explicitly

---

## Quick Reference: Technical Presentation Pattern

**Structure that works:**

1. **Problem** (10-15%) - Concrete issue audience has felt
2. **Why** (5-10%) - Root cause explanation
3. **Solution** (50-60%) - Broken into 3-5 digestible pieces
4. **Example** (10-15%) - Real-world walkthrough
5. **Results** (10%) - Realistic outcomes
6. **Takeaways** (10-15%) - How to use it yourself

**Total:** 11-13 slides, 12-15 minutes, ~1 min per slide

---

## What Made This Work

Strengths to replicate:
- Relatable problem (context overload)
- Clear structure (five techniques)
- Real numbers (78 projects, 1,500 vs 10k lines)
- Universal applicability (12-step workflow)
- Realistic claims ("very high" not "perfect")
- Concrete example (full project walkthrough)
- Before/after comparisons
- Actionable ending (clone and adapt)

---

## Final Insight

**The presentation isn't done when you finish writing it. It's done when someone else reviews it and catches your blind spots.**

Feedback is the most valuable part of the process.

---

## For Next Presentation: Pre-Flight Checklist

□ Verify all statistics against source
□ Check slide order (temporal and conceptual)
□ Read speaker notes aloud (do they sound natural?)
□ Connect each slide to previous
□ Match visual type to content
□ Be realistic in claims
□ End with actionable takeaways
□ Create support documents (demo guide, cheat sheet)
□ Plan time budget
□ Prepare backup plans
□ Get feedback from someone else
□ Practice with timer
