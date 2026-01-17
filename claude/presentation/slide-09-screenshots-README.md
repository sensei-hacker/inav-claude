# Slide 9 Screenshots - Usage Guide

**Created:** 2026-01-12
**Format:** Text-based mockups showing inav-claude workflow

## Files Created

| File | Timestamp | Content |
|------|-----------|---------|
| slide-09-01-task-assignment.md | 0:00 | Manager creates structured task |
| slide-09-02-developer-starts.md | 0:10 | /start-task skill, JIT guide loads |
| slide-09-03-jit-guide.md | 0:20 | CRITICAL-BEFORE-CODE guide |
| slide-09-04-agent-spawn.md | 0:30 | test-engineer agent investigates |
| slide-09-05-implement-fix.md | 0:40 | Code changes (git diff) |
| slide-09-06-code-review.md | 0:50 | inav-code-review agent |
| slide-09-07-pr-created.md | 1:00 | /create-pr skill, PR #2518 |
| slide-09-08-completion.md | 1:10 | Completion report, project archived |
| slide-09-09-context-comparison.md | 1:20 | With/without system comparison |

**Total presentation time:** 1:20 (80 seconds)

## How to Use in Presentation

### Option A: Embedded in Slides (Recommended)

Copy the content from each markdown file into Slide 9 as sequential sub-slides or advancing content.

**Marp syntax:**
```markdown
---

# Real Example - Fix Terrain Data Loading

[Content from slide-09-01-task-assignment.md]

---

[Content from slide-09-02-developer-starts.md]

---

[...etc...]
```

### Option B: External Images

Convert each markdown file to a terminal screenshot image:

```bash
# Using terminal screenshot tool
for file in slide-09-*.md; do
  cat "$file" | convert -font Courier -pointsize 12 label:@- "${file%.md}.png"
done
```

Then reference in slides:
```markdown
![](slide-09-01-task-assignment.png)
```

### Option C: Presenter Notes Only

Keep the text-based mockups in presenter notes and narrate the workflow verbally.

## Key Points to Emphasize

**Screenshot 1-2:** Structured communication, TODO format
**Screenshot 3:** Just-in-time documentation loading
**Screenshot 4:** Agent with separate context window
**Screenshot 5-6:** Quality gates (testing, code review)
**Screenshot 7-8:** Complete trail of work
**Screenshot 9:** Context efficiency comparison

## Timing

If presenting live, advance screens every ~10 seconds:
- 0:00 → Screenshot 1
- 0:10 → Screenshot 2
- 0:20 → Screenshot 3
- 0:30 → Screenshot 4
- 0:40 → Screenshot 5
- 0:50 → Screenshot 6
- 1:00 → Screenshot 7
- 1:10 → Screenshot 8
- 1:20 → Screenshot 9
- 1:30 → Return to slide

Total: 1:30 for full walkthrough

## Customization

These are **text-based mockups** showing the workflow. You can:

1. **Use as-is** - Copy into slides as code blocks
2. **Screenshot terminals** - Cat each file in terminal and screenshot
3. **Recreate live** - Actually run the commands during presentation
4. **Simplify** - Pick 3-5 key screenshots instead of all 9

## File Locations

All files in: `claude/developer/workspace/`

These files show the **inav-claude context engineering system** in action, not the terrain bug itself.

## Integration with Slide 9

Current Slide 9 in presentation-slides.md has placeholder text. Replace with actual screenshot content or reference these files in presenter notes.
