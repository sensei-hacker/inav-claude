# Project: Reorganize Developer Directory Structure

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Infrastructure / Organization
**Created:** 2025-12-31
**Estimated Effort:** 3-4 hours

## Overview

Analyze, plan, and implement a better organization structure for `claude/developer/` directory, then update all documentation to reflect the new structure.

## Problem

The current `claude/developer/` directory structure has evolved organically and needs improvement:
- Structure documented in `developer/CLAUDE.md` is "not great"
- Documentation may not match actual directory layout
- Files may be scattered or poorly organized
- Skills may have expectations about file locations that aren't met
- No clear guidelines for where different types of files should go

## Objectives

1. **Audit Current State**
   - Survey actual files and directories
   - Review skill documentation about file organization
   - Review current documentation
   - Identify what's working and what's not

2. **Plan Better Structure**
   - Design realistic, useful organization
   - Match how work is actually done
   - Keep things neat, tidy, and easy to find
   - Consider reusable vs. task-specific files
   - Consider active vs. archived work

3. **Implement Organization**
   - Move files to new locations
   - Create necessary directories
   - Clean up clutter
   - Ensure everything has a clear home

4. **Update Documentation**
   - Update `developer/CLAUDE.md`
   - Update `developer/INDEX.md`
   - Update skill documentation if needed
   - Update other internal docs

## Scope

**In Scope:**
- Analyzing current directory structure
- Planning better organization
- Moving files to new locations
- Creating new directories as needed
- Updating all documentation
- Ensuring skills still work
- Cleaning up clutter

**Out of Scope:**
- Changing content of files (just moving them)
- Reorganizing other `claude/` subdirectories
- Major rewrites of documentation (just update paths/structure)
- Creating new tools or scripts (focus on organization)

## Key Design Principles

A good structure should:
- **Be intuitive** - Easy to find things without reading docs
- **Match actual usage** - Reflect how work is actually done
- **Support workflows** - Make common tasks easier
- **Scale well** - Handle growth without becoming messy
- **Be self-documenting** - Directory names explain purpose

## Organization Questions to Answer

1. **Reusable vs. Task-Specific**
   - Where do reusable Python scripts go?
   - Where do task-specific investigation scripts go?

2. **Active vs. Archived**
   - How to handle completed work?
   - When to archive?

3. **Script Categories**
   - Testing scripts
   - Build scripts
   - Analysis scripts
   - Investigation scripts
   - Tool scripts

4. **Documentation Categories**
   - How-to guides
   - Reference docs
   - Investigation reports
   - Project documentation

5. **Working Files**
   - Where do task working files go?
   - How to keep them separate from reusable content?

## Implementation Approach

### Phase 1: Discovery (45 min)
1. Survey current directory structure
2. Review skill documentation
3. Review current docs
4. Identify issues and opportunities

### Phase 2: Planning (45 min)
1. Design new structure
2. Document rationale
3. Plan file moves
4. Identify documentation updates needed

### Phase 3: Implementation (60 min)
1. Create new directories
2. Move files to new locations
3. Update file references
4. Clean up old directories

### Phase 4: Documentation (45 min)
1. Update `developer/CLAUDE.md`
2. Update `developer/INDEX.md`
3. Update skill documentation
4. Update other internal docs
5. Create README files if helpful

### Phase 5: Testing (15 min)
1. Verify file locations
2. Test workflows
3. Test skills
4. Review documentation

## Expected Deliverables

1. **Reorganized Directory Structure**
   - All files in logical locations
   - Clean, intuitive organization
   - No clutter or orphaned files

2. **Updated Documentation**
   - `developer/CLAUDE.md` accurately describes structure
   - `developer/INDEX.md` provides comprehensive guide
   - Skill documentation updated if needed
   - Other internal docs updated

3. **Migration Documentation**
   - Document what changed (old → new paths)
   - Explain rationale for structure
   - Provide guidelines for future organization

4. **Completion Report**
   - Summary of changes
   - Before/after comparison
   - Benefits of new structure

## Success Criteria

- [ ] All files in logical, appropriate locations
- [ ] Documentation accurately reflects structure
- [ ] Skills still work correctly
- [ ] Structure is intuitive and easy to navigate
- [ ] No files in wrong places or orphaned
- [ ] Clear guidelines for future organization
- [ ] Improved from previous state

## Value

**Benefits:**
- Easier to find files and documentation
- Clear guidelines for where things go
- Better organization supports productivity
- Easier for new developers (or AI instances) to navigate
- Reduces clutter and confusion
- Makes maintenance easier

**Audience:**
- Developer role (primary user of directory)
- Manager role (may reference reports/docs)
- Future developers or AI instances

## Priority Justification

MEDIUM priority because:
- Improves workflow and productivity
- Not urgent (current state is functional, just messy)
- Reasonable effort (3-4 hours)
- Infrastructure improvement with long-term benefits
- Makes future work easier

## Notes

**Keep It Realistic:**
Don't design a perfect theoretical structure - design one that matches actual usage and is easy to maintain.

**Don't Break Things:**
Skills may depend on certain paths. Test changes before finalizing.

**Document Rationale:**
Explain why each organizational decision was made.

**From manager's note in CLAUDE.md:**
> "When working on a task, keep the files you create neatly organized. Testing scripts should go in scripts_testing if they are reuseable. Other things should go in the appropriate task working directory. When creating Python scripts that you may need to re-use later, save them to an appropriately named file, with documentation at the top. Don't leave files littering random directories."

The new structure should make this guidance easier to follow.

## Related

- Current documentation: `claude/developer/CLAUDE.md`
- Current index: `claude/developer/INDEX.md`
- Skill documentation: `~/.claude/skills/*/SKILL.md`
