# Presentation Export Instructions

**Source File:** `presentation-slides.md`
**Format:** Marp markdown with dark theme
**Marp Version:** v4.2.3

---

## Export Options

### 1. HTML (Web Presentation)

```bash
cd /home/raymorris/Documents/planes/inavflight/claude/presentation
marp presentation-slides.md -o presentation.html
```

**Features:**
- Interactive navigation
- Works in any browser
- Speaker notes in console (F12)
- Can host online

**To present:** Open `presentation.html` in browser, press F for fullscreen

---

### 2. PDF (Universal Format)

```bash
marp presentation-slides.md -o presentation.pdf
```

**Features:**
- Universal compatibility
- Can print
- Easy to share
- Static format (no animations)

**Note:** Requires Chrome/Chromium for PDF generation

---

### 3. PPTX (PowerPoint/LibreOffice)

```bash
marp presentation-slides.md -o presentation.pptx
```

**Features:**
- Edit in LibreOffice Impress or PowerPoint
- Add animations/transitions manually
- Customize per-slide
- Native presentation format

**To open in LibreOffice:**
```bash
libreoffice --impress presentation.pptx
```

---

### 4. Live Preview

```bash
marp presentation-slides.md --preview
```

**Features:**
- Real-time preview in browser
- Auto-refresh on file changes
- Great for testing
- Press 'p' for presenter mode

---

## Recommended Workflow

### For Final Presentation

**Option A: Direct Marp HTML** (Best)
1. Export to HTML: `marp presentation-slides.md -o presentation.html`
2. Open in browser: `firefox presentation.html` or `chromium presentation.html`
3. Press F for fullscreen, arrow keys to navigate
4. Speaker notes visible in browser console (F12)

**Option B: LibreOffice Editable**
1. Export to PPTX: `marp presentation-slides.md -o presentation.pptx`
2. Open in LibreOffice: `libreoffice --impress presentation.pptx`
3. Add custom animations if desired
4. Present with LibreOffice Impress

**Option C: PDF for Sharing**
1. Export to PDF: `marp presentation-slides.md -o presentation.pdf`
2. View: `evince presentation.pdf` or any PDF viewer
3. Good for sending to others, not ideal for presenting

---

## Troubleshooting

### "Command hangs during export"

Try with explicit output path:
```bash
marp ./presentation-slides.md --output ./output-presentation.html
```

### "Chrome/Chromium not found" (for PDF)

Install Chromium:
```bash
sudo apt install chromium-browser  # Ubuntu/Debian
```

Or set Chrome path:
```bash
export CHROME_PATH=/usr/bin/chromium-browser
marp presentation-slides.md -o presentation.pdf
```

### "Speaker notes not showing"

In HTML format:
1. Open presentation in browser
2. Press F12 to open developer console
3. Speaker notes appear in HTML comments
4. Or use Marp presenter mode (press 'p')

---

## Current Status

**Marp CLI:** ✅ Installed (v4.2.3)
**Source File:** ✅ Ready (`presentation-slides.md`)
**Corrections Applied:** ✅ All user feedback incorporated
**Styling:** ✅ Dark theme, adjusted spacing

**Ready to export when you choose a format!**

---

## File Locations

- **Source:** `claude/presentation/presentation-slides.md`
- **Exports will be in:** `claude/presentation/`
- **Screenshots:** `slide-09-01-*.md` through `slide-09-09-*.md`
- **Cheat Sheet:** `PRESENTATION-CHEAT-SHEET.md`

---

## Quick Commands Reference

```bash
# Navigate to workspace
cd ~/Documents/planes/inavflight/claude/developer/workspace

# Preview live
marp presentation-slides.md --preview

# Export HTML
marp presentation-slides.md -o presentation.html

# Export PDF
marp presentation-slides.md -o presentation.pdf

# Export PPTX for LibreOffice
marp presentation-slides.md -o presentation.pptx

# Open in LibreOffice
libreoffice --impress presentation.pptx
```

---

## Presentation Day Checklist

- [ ] Export to chosen format
- [ ] Test on presentation computer/projector
- [ ] Have `PRESENTATION-CHEAT-SHEET.md` open on laptop
- [ ] Decide on Slide 9 approach (text mockups vs live demo)
- [ ] Backup plan if tech fails
- [ ] Practice timing (target 12-15 minutes)
- [ ] Have repo link ready: github.com/sensei-hacker/inav-claude

**You're ready to go! 🚀**
