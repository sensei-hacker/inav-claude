# Task Assignment: Move JavaScript Programming Docs to New Branch

**Date:** 2025-11-28 19:20
**Project:** JavaScript Programming Documentation
**Priority:** Medium
**Estimated Effort:** < 30 minutes

## Task

Create a new branch `docs_javascript_programming` off master in the inav repository and copy the JavaScript programming documentation from the `nexus_xr` branch to it.

## Background

The JavaScript programming documentation currently exists only on the `nexus_xr` branch. We need it on a dedicated documentation branch for cleaner PR submission.

## What to Do

1. In `inav/`, create a new branch `docs_javascript_programming` off master
2. Copy the documentation directory from `nexus_xr` branch
3. Commit the changes
4. Report back

## Files to Copy

From `nexus_xr` branch, copy the entire directory:

```
docs/javascript_programming/
├── docs/
│   ├── GENERATE_CONSTANTS_README.md
│   ├── JAVASCRIPT_PROGRAMMING_GUIDE.md
│   ├── OPERATIONS_REFERENCE.md
│   ├── TESTING_GUIDE.md
│   ├── TIMER_WHENCHANGED_EXAMPLES.md
│   ├── TIMER_WHENCHANGED_IMPLEMENTATION.md
│   ├── api_definitions_summary.md
│   ├── api_maintenance_guide.md
│   ├── example_override_rc.png
│   ├── example_vtx_power.png
│   ├── implementation_summary.md
│   ├── index.md
│   ├── intellisense.png
│   └── warnings.png
```

Also check if `docs/Programming Framework.md` was updated with cross-links on `nexus_xr` - if so, copy that update as well.

## Method

```bash
cd inav
git checkout master
git checkout -b docs_javascript_programming
git checkout nexus_xr -- docs/javascript_programming/
# Check if Programming Framework.md has cross-links on nexus_xr
git diff master nexus_xr -- "docs/Programming Framework.md"
# If it has changes, copy it too:
# git checkout nexus_xr -- "docs/Programming Framework.md"
git commit -m "Add JavaScript programming documentation"
```

## Success Criteria

- [ ] New branch `docs_javascript_programming` created off master
- [ ] `docs/javascript_programming/` directory copied from nexus_xr
- [ ] Cross-links in Programming Framework.md included (if present on nexus_xr)
- [ ] Changes committed
- [ ] Report sent to manager

---
**Manager**
