# Projects Directory

This directory contains subdirectories for each feature or fix being worked on in the INAV codebase. Each project typically corresponds to a pull request.

## Quick Links

📊 **[View Project Index](INDEX.md)** - See status of all projects at a glance

## Directory Structure

```
projects/
├── INDEX.md           - Project status tracking
├── feature-name-1/
│   ├── summary.md
│   ├── todo.md
│   └── notes.md (optional)
├── fix-bug-name/
│   ├── summary.md
│   ├── todo.md
│   └── notes.md (optional)
└── README.md (this file)
```

## Naming Conventions

Project directories should be named using kebab-case and follow these patterns:

- **Features:** `feature-<brief-description>`
  - Example: `feature-improved-wind-estimation`
  - Example: `feature-mag-calibration-ui`

- **Bug Fixes:** `fix-<brief-description>`
  - Example: `fix-rtl-altitude-bug`
  - Example: `fix-serial-overflow`

- **Refactoring:** `refactor-<brief-description>`
  - Example: `refactor-navigation-estimator`

- **Performance:** `perf-<brief-description>`
  - Example: `perf-reduce-pid-latency`

## Required Files

### summary.md

Contains an overview of the project, its purpose, and implementation approach.

**Template:**
```markdown
# Project: <Name>

**Type:** Feature | Bug Fix | Refactor | Performance
**Status:** Planning | In Progress | Testing | Ready for Review | Completed
**Target Version:** INAV X.Y.Z
**Pull Request:** #XXXX (when created)

## Overview
<Brief description of what this project accomplishes>

## Motivation
<Why this change is needed>

## Technical Approach
<High-level description of how this will be implemented>

## Files to Modify
- `path/to/file1.c` - Description of changes
- `path/to/file2.h` - Description of changes
- ...

## Testing Strategy
<How this will be tested>
- SITL testing
- Hardware testing (which boards?)
- Unit tests (if applicable)

## Risks & Considerations
<Potential issues, backwards compatibility concerns, etc.>

## Related Issues/PRs
- Issue #XXX
- Related PR #XXX
- ...
```

### todo.md

Contains actionable tasks with checkboxes for tracking progress.

**Template:**
```markdown
# TODO: <Project Name>

## Planning
- [ ] Review existing code
- [ ] Design implementation approach
- [ ] Identify all files to modify
- [ ] Review similar features in codebase

## Implementation
- [ ] Task 1: Brief description
  - [ ] Subtask 1.1
  - [ ] Subtask 1.2
- [ ] Task 2: Brief description
- [ ] Task 3: Brief description

## Testing
- [ ] Write/update unit tests
- [ ] Test in SITL
- [ ] Test on target hardware (specify board)
- [ ] Verify no regressions in other features

## Documentation
- [ ] Update inline code comments
- [ ] Update relevant .md files in docs/
- [ ] Update settings.yaml if config changes
- [ ] Add changelog entry

## Code Review Prep
- [ ] Self-review all changes
- [ ] Check code style consistency
- [ ] Remove debug code
- [ ] Verify all TODOs addressed

## Pull Request
- [ ] Create PR with detailed description
- [ ] Link related issues
- [ ] Address review comments
- [ ] Merge when approved
```

### notes.md (Optional)

Freeform notes, design decisions, code snippets, research, etc.

## Workflow

### Starting a New Project

1. Create a new directory with an appropriate name:
   ```bash
   mkdir -p claude/projects/feature-my-new-feature
   ```

2. Copy templates and fill them in:
   ```bash
   cd claude/projects/feature-my-new-feature
   # Create summary.md and todo.md using templates above
   ```

3. Update status in `summary.md` to "Planning" or "In Progress"

### Working on a Project

1. Check `todo.md` for next tasks
2. Update checkboxes as you complete tasks
3. Add notes to `notes.md` as needed
4. Update `summary.md` if approach changes

### Completing a Project

1. Ensure all tasks in `todo.md` are checked off
2. Update `summary.md` status to "Completed"
3. Add PR number to `summary.md`
4. Optionally move to `archive/` subdirectory

## Examples

### Example Project Structure

```
projects/
├── feature-improved-wind-estimation/
│   ├── summary.md          # Overview, motivation, approach
│   ├── todo.md             # Detailed task list
│   └── notes.md            # Research notes, code snippets
├── fix-rtl-altitude-bug/
│   ├── summary.md
│   └── todo.md
└── archive/                # Completed projects
    └── feature-xyz/
        ├── summary.md
        └── todo.md
```

## Tips

- Keep `todo.md` granular - tasks should be completable in one session
- Update status regularly so you can pick up where you left off
- Use `notes.md` for anything that doesn't fit in summary or todos
- Reference specific file paths and line numbers in tasks
- Mark dependent tasks clearly
