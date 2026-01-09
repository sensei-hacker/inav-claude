# Todo List: Reorganize Developer Directory

## Phase 1: Discovery (45 minutes)

### Survey Current Directory Structure

- [ ] List all directories in developer/
  - [ ] Run: `tree -L 3 claude/developer/`
  - [ ] Run: `find claude/developer -type d -maxdepth 3 | sort`
  - [ ] Document current directory tree

- [ ] Count files by type
  - [ ] Count total files: `find claude/developer -type f | wc -l`
  - [ ] Count Python scripts: `find claude/developer -name "*.py" | wc -l`
  - [ ] Count markdown docs: `find claude/developer -name "*.md" | wc -l`
  - [ ] Count shell scripts: `find claude/developer -name "*.sh" | wc -l`

- [ ] Identify file locations
  - [ ] List Python scripts: `find claude/developer -name "*.py"`
  - [ ] List markdown docs: `find claude/developer -name "*.md"`
  - [ ] List shell scripts: `find claude/developer -name "*.sh"`
  - [ ] Note which directories are most/least used

- [ ] Identify issues
  - [ ] Files in wrong places?
  - [ ] Directories with unclear purpose?
  - [ ] Clutter or orphaned files?
  - [ ] Redundant or duplicate files?

### Review Skill Documentation

- [ ] Find skill references to developer/
  - [ ] Run: `grep -r "claude/developer" ~/.claude/skills/*/SKILL.md`
  - [ ] Run: `grep -r "scripts" ~/.claude/skills/*/SKILL.md`
  - [ ] Run: `grep -r "docs" ~/.claude/skills/*/SKILL.md`

- [ ] Document skill expectations
  - [ ] What directories do skills expect?
  - [ ] What files do skills create?
  - [ ] Where do skills store output?
  - [ ] Any conflicts with current structure?

### Review Current Documentation

- [ ] Read developer/CLAUDE.md
  - [ ] What structure is documented?
  - [ ] Does it match reality?
  - [ ] What's confusing or unclear?

- [ ] Read developer/INDEX.md
  - [ ] What's documented here?
  - [ ] How useful is it?
  - [ ] What's missing or outdated?

- [ ] Check for README files
  - [ ] Run: `find claude/developer -name "README.md"`
  - [ ] Read any found READMEs
  - [ ] Are they helpful or outdated?

### Analyze Current State

- [ ] Document findings
  - [ ] What's working well?
  - [ ] What's confusing or messy?
  - [ ] What needs to change?
  - [ ] What should be preserved?

## Phase 2: Planning (45 minutes)

### Design New Structure

- [ ] Consider organization principles
  - [ ] Reusable vs. task-specific separation?
  - [ ] Active vs. archived separation?
  - [ ] By content type or by usage pattern?
  - [ ] What makes most sense for actual workflow?

- [ ] Sketch directory structures
  - [ ] Draw out 2-3 alternative structures
  - [ ] Consider pros/cons of each
  - [ ] Test against common use cases
  - [ ] Choose best option

- [ ] Define directory purposes
  - [ ] Write clear purpose for each directory
  - [ ] Define what belongs in each
  - [ ] Define what doesn't belong
  - [ ] Provide examples

### Plan File Moves

- [ ] Create move plan
  - [ ] List all files to move (from → to)
  - [ ] Group related moves together
  - [ ] Identify files to delete
  - [ ] Identify files to consolidate

- [ ] Check for references
  - [ ] Run: `grep -r "claude/developer" claude/`
  - [ ] Note hardcoded paths that need updating
  - [ ] Check skill scripts for path references
  - [ ] Document all references to update

### Plan Documentation Updates

- [ ] List docs to update
  - [ ] developer/CLAUDE.md
  - [ ] developer/INDEX.md
  - [ ] Skill SKILL.md files
  - [ ] Other internal docs with path references

- [ ] Plan documentation content
  - [ ] Directory tree diagram
  - [ ] Purpose of each directory
  - [ ] Examples of what goes where
  - [ ] Guidelines for organization

## Phase 3: Implementation (60 minutes)

### Create New Directories

- [ ] Create new directory structure
  - [ ] Run mkdir commands for new directories
  - [ ] Verify directories created
  - [ ] Set appropriate permissions if needed

### Move Files

- [ ] Move files to new locations
  - [ ] Start with one category at a time
  - [ ] Use `git mv` for tracked files
  - [ ] Use `mv` for gitignored files
  - [ ] Check `git status` frequently

- [ ] Verify moves
  - [ ] Check files arrived in correct location
  - [ ] Check files removed from old location
  - [ ] No broken symlinks
  - [ ] No duplicates created

### Update File References

- [ ] Update skill references
  - [ ] Edit skill SKILL.md files
  - [ ] Edit skill scripts if they write files
  - [ ] Test skills still work

- [ ] Update documentation references
  - [ ] Edit developer/CLAUDE.md
  - [ ] Edit developer/INDEX.md
  - [ ] Edit other docs with path references

- [ ] Update script references
  - [ ] Search for hardcoded paths in scripts
  - [ ] Update to new paths
  - [ ] Test scripts still work

### Clean Up

- [ ] Remove empty directories
  - [ ] Find: `find claude/developer -type d -empty`
  - [ ] Remove if no longer needed
  - [ ] Keep if part of new structure

- [ ] Delete redundant files
  - [ ] Identify duplicates
  - [ ] Remove obsolete files
  - [ ] Clean up temporary files

- [ ] Consolidate duplicates
  - [ ] Find files with same content
  - [ ] Keep best version
  - [ ] Remove others

## Phase 4: Documentation (45 minutes)

### Update developer/CLAUDE.md

- [ ] Replace directory structure section
  - [ ] Add accurate directory tree
  - [ ] Use clear formatting
  - [ ] Show depth appropriate for overview

- [ ] Add directory purposes
  - [ ] Document each directory
  - [ ] Explain what belongs where
  - [ ] Provide examples
  - [ ] Note what doesn't belong

- [ ] Add organization guidelines
  - [ ] When to create new files
  - [ ] Where different types of files go
  - [ ] When to archive
  - [ ] How to keep organized

### Update developer/INDEX.md

- [ ] Update directory listing
  - [ ] Match new structure
  - [ ] Add descriptions
  - [ ] Provide navigation guide

- [ ] Add organization principles
  - [ ] Explain structure rationale
  - [ ] Show examples
  - [ ] Provide guidelines

- [ ] Add helpful references
  - [ ] Common file locations
  - [ ] Where to find things
  - [ ] Directory quick reference

### Update Skill Documentation

- [ ] Update skill SKILL.md files
  - [ ] Fix path references
  - [ ] Update examples
  - [ ] Verify accuracy

- [ ] Test skills
  - [ ] Run skills that interact with files
  - [ ] Verify they work correctly
  - [ ] Check file paths are right

### Update Other Documentation

- [ ] Find other references
  - [ ] Run: `grep -r "developer/" claude/`
  - [ ] Check project files
  - [ ] Check manager/release-manager docs

- [ ] Update found references
  - [ ] Fix old paths
  - [ ] Update examples
  - [ ] Verify links work

### Create README Files (Optional)

- [ ] Consider README locations
  - [ ] Key directories that need explanation?
  - [ ] Directories that are confusing?
  - [ ] Directories with special rules?

- [ ] Write READMEs if helpful
  - [ ] Explain directory purpose
  - [ ] Show examples
  - [ ] Provide guidelines

## Phase 5: Testing (15 minutes)

### Verify File Locations

- [ ] Check all files are in right places
  - [ ] Run file counts by directory
  - [ ] Spot check file locations
  - [ ] No files in wrong places
  - [ ] No orphaned files

### Test Workflows

- [ ] Try common tasks
  - [ ] Find a testing script - easy?
  - [ ] Find debugging documentation - easy?
  - [ ] Start a new investigation - clear where files go?
  - [ ] Find an old report - can locate it?

- [ ] Evaluate usability
  - [ ] Is structure intuitive?
  - [ ] Can find things without docs?
  - [ ] Improvements over old structure?

### Test Skills

- [ ] Run relevant skills
  - [ ] Any skills that read/write files in developer/
  - [ ] Verify they work correctly
  - [ ] Check output goes to right place
  - [ ] No errors or broken paths

### Review Documentation

- [ ] Read updated CLAUDE.md
  - [ ] Clear and accurate?
  - [ ] Easy to understand?
  - [ ] Helpful examples?

- [ ] Read updated INDEX.md
  - [ ] Comprehensive?
  - [ ] Good navigation?
  - [ ] Useful reference?

- [ ] Check for clarity
  - [ ] Can someone new navigate structure?
  - [ ] Are guidelines clear?
  - [ ] Any confusing parts?

## Completion

### Create Migration Documentation

- [ ] Document what changed
  - [ ] Old path → new path mappings
  - [ ] List of moved files
  - [ ] List of deleted files
  - [ ] Rationale for changes

### Create Completion Report

- [ ] Summary of changes
  - [ ] Before/after comparison
  - [ ] Benefits of new structure
  - [ ] Any issues encountered
  - [ ] Lessons learned

- [ ] Report to manager
  - [ ] Email with summary
  - [ ] Link to updated documentation
  - [ ] Note any follow-up needed

### Final Verification

- [ ] All todos complete
- [ ] All files in correct locations
- [ ] All documentation updated
- [ ] Skills tested and working
- [ ] Structure is improved
- [ ] No broken references
- [ ] Clean and organized

## Notes

**Be methodical:**
- Don't rush moves
- Check each step
- Document as you go
- Test frequently

**Keep it practical:**
- Design for actual usage
- Don't over-engineer
- Simple is better
- Easy to maintain

**Document rationale:**
- Why this structure?
- What problem does it solve?
- How to use effectively?
