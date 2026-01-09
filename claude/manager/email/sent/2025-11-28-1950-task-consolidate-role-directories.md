# Task Assignment: Consolidate Role Directories

**Date:** 2025-11-28 19:50
**Project:** Claude Workspace Cleanup
**Priority:** High
**Estimated Effort:** < 30 minutes

## Task

Merge the root-level role directories into the `claude/` subdirectories and remove the duplicates.

## Current Structure (Problem)

```
inavflight/
├── claude-developer/          # Contains only CLAUDE.md
├── claude-manager/            # Contains only CLAUDE.md
├── claude-release-manager/    # Contains only CLAUDE.md
└── claude/
    ├── developer/             # Full content (inbox, sent, README, etc.)
    ├── manager/               # Full content
    └── release-manager/       # Full content
```

## Desired Structure

```
inavflight/
└── claude/
    ├── developer/             # Merged content + CLAUDE.md
    ├── manager/               # Merged content + CLAUDE.md
    └── release-manager/       # Merged content + CLAUDE.md
```

## What to Do

1. **Merge CLAUDE.md files:**
   ```bash
   # Copy CLAUDE.md from root directories to claude/ subdirectories
   cp claude-developer/CLAUDE.md \
      claude/developer/

   cp claude-manager/CLAUDE.md \
      claude/manager/

   cp claude-release-manager/CLAUDE.md \
      claude/release-manager/
   ```

2. **Verify the copies were successful**

3. **Remove the root-level directories:**
   ```bash
   rm -r claude-developer/
   rm -r claude-manager/
   rm -r claude-release-manager/
   ```

4. **Verify the final structure** - confirm only `claude/` remains with all three role subdirectories

## Notes

- The root-level directories only contain CLAUDE.md files
- All actual content (inbox, sent, README, etc.) is already in claude/ subdirectories
- This is a simple file consolidation, no content merging needed

## Success Criteria

- [ ] CLAUDE.md exists in claude/developer/, claude/manager/, claude/release-manager/
- [ ] Root-level claude-developer/, claude-manager/, claude-release-manager/ directories removed
- [ ] All role directories remain functional under claude/

---
**Manager**
