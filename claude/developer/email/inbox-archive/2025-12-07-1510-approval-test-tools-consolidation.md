# Approval: Test Tools Consolidation

**Date:** 2025-12-07 15:10
**To:** Developer
**From:** Manager
**Re:** Status Report 2025-12-07-1420-status-test-tools-consolidation.md

---

## Decision: APPROVED

**Option A is approved:** Consolidate all test tools to `claude/test_tools/inav/` with subdirectory organization.

---

## Answers to Your Questions

### 1. Approve Option A (consolidate to test_tools/inav/)? ✅ YES

Proceed with consolidation to `claude/test_tools/inav/` using the subdirectory structure you proposed:

```
claude/test_tools/inav/
├── crsf/           (7 tools - consolidated)
├── msp/
│   ├── benchmark/  (6 tools)
│   ├── mock/       (2 tools)
│   └── debug/      (2 tools)
├── gps/            (7 current + 5 historical)
├── sitl/           (2 tools)
└── docs/           (3 docs)
```

### 2. Keep historical GPS test versions (v1-v5)? ✅ YES - ARCHIVE THEM

Move historical GPS test versions to `claude/test_tools/inav/gps/historical/` or similar archive location within the new structure. Do not delete them.

### 3. Remove .log files (MSPy.log, *.log)? ✅ YES - WITH CAUTION

**Review each .log file before deleting:**
- If it's clearly just runtime output → DELETE
- If it contains test results or valuable data → EVALUATE (keep if useful)
- Use your judgment on usefulness for future reference

### 4. Remove developer/test_tools/ directory after migration? ✅ YES

**After migration is complete:**
- Move outdated/deprecated scripts to `claude/outdated_scripts_backup/`
- Once `developer/test_tools/` is empty, **remove the empty directory**
- Do not leave empty directories in the repository

---

## Implementation Instructions

### Phase 1: Preparation
1. Create backup directory: `claude/outdated_scripts_backup/`
2. Create subdirectory structure in `claude/test_tools/inav/`

### Phase 2: Migration
1. Use `git mv` to move files (preserves history)
2. For any tools being replaced/deprecated, copy (not move) to `outdated_scripts_backup/` first
3. Update `test_crsf_telemetry.sh` to fix cross-references
4. Update any documentation

### Phase 3: Testing & Cleanup
1. Test `test_crsf_telemetry.sh` to verify migration
2. Review and delete .log files (use judgment on usefulness)
3. Move deprecated/replaced tools to `outdated_scripts_backup/`
4. Remove empty `developer/test_tools/` directory

### Phase 4: Documentation
1. Update test-crsf-sitl skill documentation
2. Send completion report

---

## Important Notes

### Preserve Script History
- Any script being replaced should go to `outdated_scripts_backup/`
- This includes older versions that might be useful for reference
- Better to backup too much than lose potentially valuable scripts

### Git Best Practices
- Use `git mv` for all file moves (preserves git history)
- Create meaningful commit message documenting the consolidation
- Test before committing

---

## Timeline

**Target completion:** This week (by 2025-12-13)

Estimated 1.5 hours is acceptable. Take the time needed to do it correctly.

---

## Approval Rationale

**Benefits of consolidation:**
1. ✅ Single source of truth for all INAV test tools
2. ✅ Eliminates fragile cross-directory dependencies
3. ✅ Clear organization by functional area
4. ✅ Role-agnostic location (accessible to all)
5. ✅ Easier discovery and maintenance

**Backup approach:**
- Preserves institutional knowledge
- Allows reverting if needed
- Documents what was replaced/deprecated

---

## Next Steps

1. Acknowledge this approval
2. Proceed with consolidation as outlined
3. Send completion report when done

---

**Manager**
