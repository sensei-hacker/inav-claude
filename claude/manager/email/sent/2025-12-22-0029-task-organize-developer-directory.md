# Task Assignment: Organize claude/developer/ Directory Structure

**Date:** 2025-12-22 00:29
**Project:** inav (internal organization)
**Priority:** Medium
**Estimated Effort:** 2-3 hours

## Task

Organize the `claude/developer/` directory into a clean, logical directory tree structure, then document the organization in CLAUDE.md and create/update an index.md file.

## Current Situation

The `claude/developer/` directory has grown organically and now contains:
- 50+ loose markdown files at the root level (status reports, investigations, analysis)
- Multiple subdirectories with varying purposes
- Mixed content types (docs, scripts, reports, test results, investigations)

**Current subdirectories:**
- `docs/` - Testing documentation and guides
- `reports/` - Analysis reports
- `helpers/` - Scripts and tools
- `blueberry-pid-performance-investigation/` - Specific investigation
- `builds/`, `cleanup/`, `completed/`, `legacy-test-scripts/`, `patterns/`, `temp-files/`, `test_tools/`, `work-in-progress/`

**Email directories (DO NOT MOVE):**
- `inbox/`, `inbox-archive/`, `sent/`, `outbox/`

## What to Do

### Step 1: Analyze Current Content

1. Review all files and subdirectories in `claude/developer/`
2. Categorize content by type and purpose:
   - Active investigations vs completed work
   - Testing documentation vs analysis reports
   - Scripts/tools vs status updates
   - Project-specific vs general content

### Step 2: Design Directory Structure

Create a logical organization. Suggested structure (adjust as needed):

```
claude/developer/
├── CLAUDE.md                  # Developer guide (update with new structure)
├── README.md                  # Existing developer README
├── INDEX.md                   # New/updated: Directory organization guide
│
├── inbox/                     # DO NOT MOVE - Email inbox
├── inbox-archive/             # DO NOT MOVE - Email archive
├── sent/                      # DO NOT MOVE - Sent emails
├── outbox/                    # DO NOT MOVE - Pending emails
│
├── docs/                      # Documentation and guides
│   ├── testing/               # Testing guides
│   ├── debugging/             # Debugging guides
│   ├── transpiler/            # Transpiler documentation
│   └── reference/             # Reference materials
│
├── investigations/            # Active and completed investigations
│   ├── h743-msc/              # H743 USB MSC investigation
│   ├── crsf-telemetry/        # CRSF telemetry testing
│   ├── blueberry-pid/         # PID performance investigation
│   └── ...
│
├── reports/                   # Analysis reports
│   └── ...
│
├── scripts/                   # Scripts and automation tools
│   ├── testing/               # Test scripts
│   ├── build/                 # Build helpers
│   └── analysis/              # Analysis scripts
│
├── projects/                  # Project-specific work
│   └── ...
│
└── archive/                   # Completed/old work
    ├── completed/             # Completed investigations
    ├── temp-files/            # Temporary files
    └── legacy/                # Legacy scripts/files
```

### Step 3: Execute Organization

1. **Create new directory structure**
2. **Move files to appropriate locations:**
   - Group related files together
   - Separate active work from archived content
   - Organize by purpose/category
3. **Update any scripts** that reference moved files
4. **Test that nothing breaks** (check script paths, references)

### Step 4: Document Organization

1. **Update `claude/developer/CLAUDE.md`:**
   - Add a concise "Directory Structure" section
   - Document purpose of each major directory
   - Keep it brief (2-3 paragraphs max)

2. **Create/Update `claude/developer/INDEX.md`:**
   - Detailed directory tree visualization
   - Purpose/description of each directory
   - Quick reference for finding specific content
   - Instructions for where to put new content

## Important Constraints

### DO NOT MOVE:
- `inbox/`
- `inbox-archive/`
- `sent/`
- `outbox/`

These are email directories and must stay at the top level.

### Be Careful With:
- Any scripts that reference file paths
- Any tools that depend on specific locations
- Any symlinks or references from other directories

## Success Criteria

- [ ] Directory structure is logical and easy to navigate
- [ ] Related content is grouped together
- [ ] Active work separated from archived content
- [ ] Email directories remain at top level (not moved)
- [ ] `CLAUDE.md` updated with concise structure summary
- [ ] `INDEX.md` created/updated with detailed organization
- [ ] No broken scripts or references
- [ ] Sent completion report

## Deliverables

1. **Organized directory structure** in `claude/developer/`
2. **Updated CLAUDE.md** with "Directory Structure" section
3. **INDEX.md** file documenting the organization
4. **Brief completion report** listing:
   - New directory structure
   - What was moved where
   - Any scripts updated
   - How to find specific content

## Notes

- **Use your judgment** on the exact structure - suggested structure is just a starting point
- **Group logically** - the goal is easy navigation, not perfect categorization
- **Keep it simple** - don't over-engineer the organization
- **Document well** - future developers should understand the structure easily

## Why This Matters

The developer directory has grown to 50+ files and needs organization for:
- Easy navigation and content discovery
- Clear separation of active vs archived work
- Better maintainability
- Easier onboarding for new developers
- Professional appearance

---
**Manager**
