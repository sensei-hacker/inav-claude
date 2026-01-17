# Context Engineering Presentation

**12-15 minute technical presentation** explaining how the INAV-Claude project uses context engineering to make Claude Code consistently follow best practices.

---

## 📊 Main Files

### Presentation
- **[presentation-slides.md](presentation-slides.md)** - Main presentation (Marp format, dark theme, 13 slides)
- **[PRESENTATION-CHEAT-SHEET.md](PRESENTATION-CHEAT-SHEET.md)** - Quick reference for during talk
- **[EXPORT-INSTRUCTIONS.md](EXPORT-INSTRUCTIONS.md)** - How to export to HTML/PDF/PPTX

### Slide 9 Screenshots (Workflow Mockups)
- **[slide-09-01-task-assignment.md](slide-09-01-task-assignment.md)** through **[slide-09-09-context-comparison.md](slide-09-09-context-comparison.md)**
- **[slide-09-screenshots-README.md](slide-09-screenshots-README.md)** - Usage guide

### Supporting Documentation
- **[presentation-outline-v2.md](presentation-outline-v2.md)** - Detailed outline with speaker notes
- **[presentation-lessons-learned.md](presentation-lessons-learned.md)** - Insights for future presentations
- **[presentation-key-files.md](presentation-key-files.md)** - Statistics and references
- **[presentation-demo-guide.md](presentation-demo-guide.md)** - Original screenshot creation guide
- **[presentation-slide-visuals.md](presentation-slide-visuals.md)** - Visual design options

### Planning & Analysis
- **[REPOSITORY-SEPARATION-ANALYSIS.md](REPOSITORY-SEPARATION-ANALYSIS.md)** - Generic vs INAV-specific analysis
- **[STATUS-AND-NEXT-STEPS.md](STATUS-AND-NEXT-STEPS.md)** - Current status and reminders
- **[FINAL-COMPLETION-SUMMARY.md](FINAL-COMPLETION-SUMMARY.md)** - Complete project summary

---

## 🚀 Quick Start

### To Export and Present:

```bash
cd ~/Documents/planes/inavflight/claude/presentation

# Export to PPTX for LibreOffice
marp presentation-slides.md -o presentation.pptx
libreoffice --impress presentation.pptx

# Or export to PDF
marp presentation-slides.md -o presentation.pdf

# Or export to HTML
marp presentation-slides.md -o presentation.html
firefox presentation.html
```

### During Presentation:

1. Have `PRESENTATION-CHEAT-SHEET.md` open on laptop
2. Use Slide 9 mockups (copy into slides or narrate)
3. Target 12-15 minutes
4. Gauge interest in generic template repo (speaker notes on final slide)

---

## 📋 Content Overview

### The Five Techniques

1. **Role Separation** - Manager/Developer/Release contexts
2. **Just-In-Time Documentation** - CRITICAL-BEFORE-* guides
3. **Specialized Agents** - Narrow expertise, separate context windows
4. **Reusable Skills** - /start-task, /create-pr workflows
5. **Enforcement Hooks** - Automatic best practice adherence

### Key Statistics

- **Agents:** 10 total, 3,301 lines, representing ~26,000 lines
- **Guides:** CODE (104), TEST (113), COMMIT (105), PR (171)
- **Projects:** 78 completed in 2 months
- **Context Efficiency:** ~1,500 lines vs ~10-15k without system

### Universal 12-Step Workflow

Adaptable to any software project - same steps, customize content.

---

## 🎯 Important Reminders

### Slide 9 Screenshot Options

The mockups are terminal-style text files. You can:
- Copy into slides as code blocks
- Screenshot actual terminals (cat each file)
- Use as presenter notes and narrate
- Recreate live during presentation

### End Slide - Gauge Interest

Speaker notes on final slide help you:
- Ask if people want to adapt for their projects
- Gauge interest in separate generic template repo
- Get feedback on preferences
- Offer to extract if there's demand

See `REPOSITORY-SEPARATION-ANALYSIS.md` for detailed options.

### Fresh Eyes Review (TODO)

In a separate Claude session (fresh context):
- Read presentation-slides.md without studying repo
- Identify unclear parts
- Note flow issues
- Suggest improvements from outsider perspective

---

## 📁 Repository

**Repository:** https://github.com/sensei-hacker/inav-claude

**Contact:** sensei-hacker on GitHub

---

## 📝 Presentation History

**Created:** 2026-01-12
**Format:** Marp markdown with dark theme
**Duration:** 12-15 minutes
**Slides:** 13 total
**Iterations:** Multiple based on detailed feedback

**Key Improvements:**
- Realistic claims (not overpromising)
- Connected slides with transitions
- Reduced text on wordy slides
- Added speaker notes with newlines
- Intentional visual cutoff on Slide 3
- Repository separation analysis

---

## 🎤 Key Insight

> "Context engineering turns Claude from a smart assistant into a reliable, professional development team member with consistent process adherence."

---

**Ready to present? Export your slides and go! 🚀**
