# Task Assignment: Reorganize Developer Directory Structure

**Date:** 2025-12-31 23:45
**Project:** reorganize-developer-directory
**Priority:** MEDIUM
**Estimated Effort:** 3-4 hours
**Type:** Infrastructure / Organization

## Task

Analyze the current `claude/developer/` directory organization, plan a better structure, implement it, and update all documentation to reflect the new organization.

## Background

The current directory structure in `claude/developer/` has evolved organically and needs improvement. The structure documented in `developer/CLAUDE.md` is "not great" and doesn't accurately reflect how the directory is actually being used.

Additionally, skills may have documentation about where tools and docs should be stored that needs to be aligned with the actual structure.

## Objectives

1. **Audit Current State**
   - Survey actual files and directories in `claude/developer/`
   - Review what skills say about file organization
   - Review current documentation in `developer/CLAUDE.md` and `developer/INDEX.md`
   - Identify what's working and what's not

2. **Plan Better Structure**
   - Design a realistic, useful organization that matches how work is actually done
   - Keep things neat, tidy, and easy to find
   - Consider:
     - Reusable vs. task-specific files
     - Active work vs. completed/archived work
     - Different types of content (scripts, docs, reports, investigations)
     - Skill expectations about file locations

3. **Implement Organization**
   - Move files to new locations
   - Create necessary directories
   - Clean up any clutter or redundant files
   - Ensure everything has a clear home

4. **Update Documentation**
   - Update `developer/CLAUDE.md` with new structure
   - Update `developer/INDEX.md` with new structure
   - Update skill documentation if needed
   - Update any other internal docs that reference file locations
   - Ensure documentation is clear and helpful

## Current Known Issues

From `developer/CLAUDE.md`:
```
claude/developer/
├── docs/                 # Documentation and guides
│   ├── testing/          # Testing guides and results
│   ├── debugging/        # Debugging techniques and tools
│   ├── transpiler/       # Transpiler documentation
│   └── patterns/         # Code patterns and best practices
├── scripts/              # Reusable scripts
│   ├── testing/          # Test scripts
│   ├── build/            # Build helpers
│   └── analysis/         # Code analysis tools
├── investigations/       # Project-specific investigations (gitignored)
├── reports/              # Analysis reports (gitignored)
├── archive/              # Completed/old work (gitignored)
└── inbox/outbox/sent/    # Email directories
```

This structure may not reflect reality or may not be the most useful organization.

## Discovery Phase

### 1. Audit Current Directory Structure

**List actual directory contents:**
```bash
cd ~/Documents/planes/inavflight/claude/developer/
find . -type d -maxdepth 3 | sort
find . -type f -maxdepth 2 | sort
```

**Understand what's there:**
- How many files in each directory?
- What types of files (Python scripts, markdown docs, data files, etc.)?
- Which directories are actively used?
- Which are cluttered or poorly organized?
- Any files in wrong locations?

### 2. Review Skill Documentation

**Check what skills expect:**
```bash
grep -r "claude/developer" ~/.claude/skills/*/SKILL.md
grep -r "scripts" ~/.claude/skills/*/SKILL.md
grep -r "docs" ~/.claude/skills/*/SKILL.md
```

**Key questions:**
- Do skills expect certain directories to exist?
- Do skills store files in specific locations?
- Are there conflicts between skill expectations and actual structure?

### 3. Review Current Documentation

**Read:**
- `claude/developer/CLAUDE.md` - Current structure documentation
- `claude/developer/INDEX.md` - Directory index/guide
- Any README files in subdirectories

**Identify:**
- What's documented but doesn't exist?
- What exists but isn't documented?
- What's confusing or unclear?

## Planning Phase

### 1. Design Principles

A good structure should:
- **Be intuitive** - Easy to find things without reading docs
- **Match actual usage** - Reflect how work is actually done
- **Support workflows** - Make common tasks easier
- **Scale well** - Handle growth without becoming messy
- **Be self-documenting** - Directory names explain purpose

### 2. Key Organization Questions

**Consider:**

1. **Reusable vs. Task-Specific**
   - Where do reusable Python scripts go?
   - Where do task-specific investigation scripts go?
   - How to prevent mixing the two?

2. **Active vs. Archived**
   - How to handle completed work?
   - When to archive?
   - How to find archived work later?

3. **Script Categories**
   - Testing scripts (reusable test harnesses)
   - Build scripts (build helpers, automation)
   - Analysis scripts (one-time analysis tools)
   - Investigation scripts (task-specific exploration)
   - Tool scripts (general utilities)

4. **Documentation Categories**
   - How-to guides (testing, debugging, building)
   - Reference docs (API docs, architecture)
   - Investigation reports (analysis findings)
   - Project documentation (task-specific)

5. **Working Files**
   - Where do task working files go?
   - How to keep them separate from reusable content?
   - When to clean them up?

### 3. Proposed Structure Ideas

**Consider structures like:**

**Option A: By Content Type**
```
developer/
├── scripts/          # All reusable scripts
├── docs/             # All documentation
├── tools/            # Helper utilities
├── working/          # Active task work (gitignored)
└── archive/          # Completed work (gitignored)
```

**Option B: By Usage Pattern**
```
developer/
├── library/          # Reusable code and docs
│   ├── scripts/
│   └── docs/
├── workspace/        # Active task work (gitignored)
│   ├── [task-name]/
│   └── [task-name]/
└── archive/          # Old work (gitignored)
```

**Option C: Hybrid**
```
developer/
├── tools/            # Reusable scripts and utilities
│   ├── testing/
│   ├── build/
│   └── analysis/
├── guides/           # How-to documentation
├── reference/        # Reference documentation
├── projects/         # Active task work (gitignored)
│   └── [task-name]/
├── reports/          # Analysis reports (gitignored)
└── archive/          # Old work (gitignored)
```

**Choose the structure that best matches actual usage patterns.**

## Implementation Phase

### 1. Create New Directory Structure

```bash
cd ~/Documents/planes/inavflight/claude/developer/

# Create new directories as needed
mkdir -p [new-structure]

# Don't delete old directories yet - move files first
```

### 2. Move Files to New Locations

**Plan moves carefully:**
- Create a move plan (from → to mapping)
- Check for references to old paths (grep)
- Move files in logical groups
- Test after major moves

**Be careful with:**
- Git-tracked vs. gitignored files
- Symlinks (if any)
- Files referenced by skills
- Files referenced in documentation

### 3. Update File References

**Search for hardcoded paths:**
```bash
# In skills
grep -r "claude/developer" ~/.claude/skills/

# In documentation
grep -r "claude/developer" ~/Documents/planes/inavflight/claude/

# In scripts
grep -r "claude/developer" ~/Documents/planes/inavflight/claude/developer/
```

**Update references to point to new locations.**

### 4. Clean Up

- Remove empty directories
- Delete redundant files
- Consolidate duplicates
- Archive old work

## Documentation Phase

### 1. Update developer/CLAUDE.md

**Replace current structure with:**
- Clear, accurate directory tree
- Purpose of each directory
- Examples of what goes where
- Guidelines for keeping it organized

**Format:**
```markdown
## Directory Structure

claude/developer/
├── [directory]/      # [Purpose and what goes here]
├── [directory]/      # [Purpose and what goes here]
└── [directory]/      # [Purpose and what goes here]

### Directory Purposes

**[directory-name]/**
- **Purpose:** [What this is for]
- **Contents:** [What belongs here]
- **Examples:** [Specific examples]
- **Don't put here:** [Common mistakes]

...
```

### 2. Update developer/INDEX.md

Update the directory index to match new structure:
- Document all directories
- Explain organization principles
- Provide navigation guide
- Add examples

### 3. Update Skill Documentation

If any skills reference file locations:
- Update SKILL.md files
- Update skill scripts that write files
- Test skills still work

### 4. Update Other Documentation

Search for references:
```bash
grep -r "developer/" ~/Documents/planes/inavflight/claude/
```

Update any documentation that references old paths.

### 5. Create README Files

Consider adding README.md in key directories:
- Explain purpose
- Show examples
- Provide guidelines

## Testing Phase

### 1. Verify File Locations

- All reusable scripts in correct location
- All docs in correct location
- No files in wrong places
- No orphaned files

### 2. Test Workflows

**Try common tasks:**
- Finding a testing script
- Finding debugging documentation
- Starting a new investigation
- Finding an old report

**Should be easy and intuitive.**

### 3. Test Skills

Run skills that interact with developer/ directory:
- Verify they still work
- Check file paths are correct
- No broken references

### 4. Review Documentation

- Read updated CLAUDE.md - is it clear?
- Read updated INDEX.md - is it helpful?
- Can someone new navigate the structure?

## Deliverables

1. **Reorganized Directory Structure**
   - All files in appropriate locations
   - Logical, intuitive organization
   - No clutter or mess

2. **Updated Documentation**
   - `developer/CLAUDE.md` accurately describes structure
   - `developer/INDEX.md` provides comprehensive guide
   - Skill documentation updated if needed
   - Other internal docs updated

3. **Migration Documentation**
   - Document what changed (old path → new path)
   - Note any breaking changes
   - Explain rationale for structure

4. **Completion Report**
   - Summary of changes
   - Before/after comparison
   - Benefits of new structure
   - Any issues encountered

## Success Criteria

- [ ] All files in logical, appropriate locations
- [ ] Documentation accurately reflects structure
- [ ] Skills still work correctly
- [ ] Structure is intuitive and easy to navigate
- [ ] No files in wrong places or orphaned
- [ ] Clear guidelines for future organization
- [ ] Improved from previous state

## Important Notes

### Keep It Realistic

Don't design a perfect theoretical structure - design one that:
- Matches how you actually work
- Is easy to maintain
- Doesn't require constant reorganization
- Makes finding things easier

### Don't Break Things

- Skills may depend on certain paths
- Other documentation may reference paths
- Test changes before finalizing
- Keep track of what you move

### Document Rationale

When making organization decisions, document:
- Why this structure?
- What problem does it solve?
- What are the trade-offs?
- How to use it effectively?

### Version Control

Be careful with Git:
- Some directories are gitignored
- Don't accidentally commit large files
- Use `git mv` for tracked files to preserve history
- Check `git status` frequently

### Note from Manager's CLAUDE.md

The developer CLAUDE.md mentions:
> "When working on a task, keep the files you create neatly organized. Testing scripts should go in scripts_testing if they are reuseable. Other things should go in the appropriate task working directory. When creating Python scripts that you may need to re-use later, save them to an appropriately named file, with documentation at the top. Don't leave files littering random directories."

Your new structure should make this guidance easier to follow.

## Examples to Consider

### Before (Current Mess)
```
developer/
├── test_something.py
├── old_analysis.py
├── random_script.sh
├── notes.txt
├── investigation-x/
│   └── messy_files
└── docs/
    └── lots_of_stuff
```

### After (Clean Structure)
```
developer/
├── tools/
│   └── testing/
│       └── test_something.py       # Reusable test script
├── guides/
│   └── testing/
│       └── how-to-test.md          # Testing documentation
├── projects/
│   └── investigation-x/            # Task-specific work
│       ├── analysis.py
│       ├── notes.md
│       └── results/
└── archive/
    └── 2025-12/
        └── investigation-x/        # Completed work
```

## Helpful Commands

**Survey current state:**
```bash
# Directory tree
tree -L 3 claude/developer/

# File counts
find claude/developer -type f | wc -l
find claude/developer -type d | wc -l

# Recent files
find claude/developer -type f -mtime -7

# Large files
find claude/developer -type f -size +1M
```

**Find references:**
```bash
# Find all references to a path
grep -r "old/path" claude/

# Find Python scripts
find claude/developer -name "*.py"

# Find markdown docs
find claude/developer -name "*.md"
```

**Move files safely:**
```bash
# Git-tracked files (preserve history)
git mv old/path new/path

# Gitignored files (simple move)
mv old/path new/path

# Test a move plan (dry run)
# [Create a script to simulate moves]
```

## Resources

- Current structure: `claude/developer/`
- Current docs: `claude/developer/CLAUDE.md`, `claude/developer/INDEX.md`
- Skills: `~/.claude/skills/`
- Project docs: `claude/projects/`

---

**Manager**
