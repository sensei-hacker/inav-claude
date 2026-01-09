# Task Assignment: Update MSP Library Documentation to mspapi2

**Date:** 2025-12-18 01:15
**Project:** update-msp-library-documentation
**Priority:** MEDIUM
**Estimated Effort:** 2-3 hours
**Branch:** Documentation update (no code branch needed)

## Task

Update internal documentation and skills to reference **mspapi2** instead of **uNAVlib** for MSP communication. The author of uNAVlib recommends using their newer library, mspapi2, which is better.

## Background

Our internal documentation currently references uNAVlib for MSP communication with INAV. The library author has created a newer, better library called **mspapi2** and recommends using it instead.

**Current references to uNAVlib:**
- 2 CLAUDE.md files (developer and manager)
- 3 skills (msp-protocol, sitl-arm, test-crsf-sitl)
- Developer documentation (CRSF telemetry MSP config guide)
- Various test scripts and examples

## What to Do

### 1. Research mspapi2

**Find the library:**
- GitHub repository URL
- Installation instructions (`pip install mspapi2` or similar)
- Basic API documentation
- Usage examples

**Compare with uNAVlib:**
- Are the APIs similar?
- Any significant differences in usage?
- Are there breaking changes?
- Can we provide migration guidance?

### 2. Update CLAUDE.md Files

**File: `claude/developer/CLAUDE.md` (line 44)**
```markdown
Current: - **uNAVlib/** - Python MSP library - You edit this

Update to:
- **mspapi2** - Python MSP library (recommended)
- **uNAVlib** - Older MSP library (still available as alternative)
```

**File: `claude/manager/CLAUDE.md` (line 42)**
```markdown
Current: - **uNAVlib/** - Python MSP library

Update to:
- **mspapi2** - Python MSP library (recommended)
- **uNAVlib** - Older alternative MSP library
```

### 3. Update Skills (3 files)

**File: `.claude/skills/msp-protocol/SKILL.md`**
- Change primary recommendation to mspapi2
- Update installation instructions
- Update code examples with mspapi2 imports
- Add note: "If you find issues or need improvements in mspapi2, you can submit PRs to the library"
- Keep uNAVlib mention as "older alternative for backward compatibility"

**File: `.claude/skills/sitl-arm/SKILL.md`**
- Update MSP library references
- Update any import statements in examples
- Update installation section
- Preserve uNAVlib as fallback option

**File: `.claude/skills/test-crsf-sitl/SKILL.md`**
- Update MSP configuration examples
- Update library imports
- Update installation instructions

### 4. Update Developer Documentation

**File: `claude/developer/crsf-telemetry-msp-config-guide.md`**
- Update imports (likely `from unavlib.main import MSPy` → mspapi2 equivalent)
- Update code examples
- Update installation instructions at top of file
- Add note about uNAVlib compatibility if people have old code

**Search for other references:**
```bash
grep -r "unavlib\|uNAVlib\|MSPy" claude/developer/ --include="*.md"
```

Update any test scripts, examples, or patterns that reference the old library.

### 5. Add Important Note

**In all updated files, add:**
- Note that mspapi2 is open to PRs for improvements/additions
- If you encounter issues or see things that should be added, you can contribute
- Include link to mspapi2 GitHub repository

### 6. Preserve Backward Compatibility

**Important:**
- Don't delete all uNAVlib references
- Keep mentions as "older alternative"
- Some existing projects may still use uNAVlib
- Provide migration guidance if APIs differ significantly

## Success Criteria

- [ ] mspapi2 repository found and documented
- [ ] Installation instructions verified
- [ ] Both CLAUDE.md files updated
- [ ] All 3 skills updated with mspapi2 as primary recommendation
- [ ] Developer documentation updated
- [ ] Note added about submitting PRs to mspapi2
- [ ] uNAVlib preserved as "older alternative" where appropriate
- [ ] No broken references or missing information

## Files to Update

**CLAUDE.md files (2):**
- `claude/developer/CLAUDE.md`
- `claude/manager/CLAUDE.md`

**Skills (3):**
- `.claude/skills/msp-protocol/SKILL.md`
- `.claude/skills/sitl-arm/SKILL.md`
- `.claude/skills/test-crsf-sitl/SKILL.md`

**Developer docs:**
- `claude/developer/crsf-telemetry-msp-config-guide.md`
- Any other files found with uNAVlib references

## Notes

**Key points:**
- mspapi2 is the new recommended library (per author recommendation)
- uNAVlib still works but is older
- Keep backward compatibility mentions
- mspapi2 accepts PRs for improvements

**Research checklist:**
- Find mspapi2 GitHub URL
- Get `pip install` command
- Review API (is it similar to uNAVlib?)
- Check for usage examples
- Note any major differences

**Update pattern:**
```markdown
# Old
**Library:** uNAVlib

# New
**Recommended Library:** mspapi2
- Installation: `pip install mspapi2`
- GitHub: [link]
- PRs welcome for improvements!

**Older Alternative:** uNAVlib (still functional, use for backward compatibility)
```

**Don't forget:**
- Update import statements in code examples
- Update installation commands
- Add PR contribution note
- Preserve uNAVlib as alternative

---
**Manager**
