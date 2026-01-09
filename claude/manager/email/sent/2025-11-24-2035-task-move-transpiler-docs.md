# Task Assignment: Move Transpiler Documentation to INAV Repository

**Date:** 2025-11-24 20:35
**Project:** move-transpiler-docs-to-inav-repo
**Priority:** High
**Estimated Effort:** 2-3 hours
**Branches:** programming_transpiler_js (both repos)

## Task

Reorganize transpiler documentation by moving it from inav-configurator to the main INAV repository, and create cross-links with the traditional logic conditions documentation.

## Three Main Actions

### 1. Copy TESTING_GUIDE.md to Tests Directory

**Copy:** `inav-configurator/js/transpiler/docs/TESTING_GUIDE.md`
**To:** `inav-configurator/js/transpiler/transpiler/tests/TESTING_GUIDE.md`

**Purpose:** Keep testing guide accessible in tests directory for developers

### 2. Move Transpiler Documentation to INAV Repo

**Move FROM:** `inav-configurator/js/transpiler/`
- `docs/` directory
- `api/` directory
- `examples/` directory
- `scripts/` directory (if applicable)

**Move TO:** `inav/docs/javascript_programming/`

**Important:** Only move documentation and supporting files. The actual transpiler code (`js/transpiler/transpiler/`) stays in inav-configurator.

### 3. Add Cross-Links Between Documentation

**Update:** `inav/docs/Programming Framework.md`
- Add section introducing JavaScript programming alternative
- Add links to JavaScript programming documentation

**Update:** `inav/docs/javascript_programming/docs/JAVASCRIPT_PROGRAMMING_GUIDE.md`
- Add section explaining relationship to logic conditions
- Add links back to Programming Framework.md

## Why This Matters

- **Centralization:** INAV documentation should be in the INAV repository
- **Discoverability:** Users learning about logic conditions need to know about JavaScript alternative
- **Context:** JavaScript programming users need to understand the underlying logic conditions system
- **Organization:** Documentation belongs with the firmware, not just the configurator

## Directory Structure After Move

```
inav/
└── docs/
    ├── Programming Framework.md (updated with links)
    └── javascript_programming/
        ├── docs/
        │   ├── JAVASCRIPT_PROGRAMMING_GUIDE.md (updated with links)
        │   ├── TESTING_GUIDE.md
        │   ├── JavaScript_Variables.md
        │   └── [other docs]
        ├── api/
        ├── examples/
        └── scripts/

inav-configurator/
└── js/
    └── transpiler/
        ├── transpiler/ (stays here - the actual code)
        │   └── tests/
        │       └── TESTING_GUIDE.md (new copy)
        ├── index.js (stays here)
        └── editor/ (stays here)
```

## Detailed Steps

### Step 1: Copy TESTING_GUIDE.md (5 min)

```bash
cd inav-configurator
cp js/transpiler/docs/TESTING_GUIDE.md \
   js/transpiler/transpiler/tests/TESTING_GUIDE.md
git add js/transpiler/transpiler/tests/TESTING_GUIDE.md
```

### Step 2: Copy Documentation to INAV Repo (30 min)

Since these are separate repositories, use `cp` not `git mv`:

```bash
# Create destination
mkdir -p ../inav/docs/javascript_programming

# Copy directories
cp -r js/transpiler/docs ../inav/docs/javascript_programming/docs
cp -r js/transpiler/api ../inav/docs/javascript_programming/api
cp -r js/transpiler/examples ../inav/docs/javascript_programming/examples
cp -r js/transpiler/scripts ../inav/docs/javascript_programming/scripts  # if needed

# Add to INAV git
cd ../inav
git add docs/javascript_programming/
```

### Step 3: Add Cross-Links in Programming Framework.md (15 min)

Edit `inav/docs/Programming Framework.md`:

**Add near beginning:**
```markdown
## JavaScript-Based Programming (Alternative)

INAV also supports a JavaScript-based programming interface that provides a more
familiar syntax for those comfortable with JavaScript. See the
[JavaScript Programming Guide](javascript_programming/docs/JAVASCRIPT_PROGRAMMING_GUIDE.md)
for details.

The JavaScript code is transpiled into traditional logic conditions, so both methods
ultimately use the same underlying system.
```

**Add in related documentation section:**
```markdown
## Related Documentation

- [JavaScript Programming Guide](javascript_programming/docs/JAVASCRIPT_PROGRAMMING_GUIDE.md) -
  Alternative JavaScript-based syntax for programming logic conditions
- [JavaScript Variables](javascript_programming/docs/JavaScript_Variables.md) -
  Using variables in JavaScript programming
```

### Step 4: Add Cross-Links in JAVASCRIPT_PROGRAMMING_GUIDE.md (15 min)

Edit `inav/docs/javascript_programming/docs/JAVASCRIPT_PROGRAMMING_GUIDE.md`:

**Add near beginning:**
```markdown
## Relationship to Logic Conditions

This JavaScript programming interface is built on top of INAV's traditional
[Logic Conditions](../../Programming%20Framework.md) system. The JavaScript code you
write is transpiled (converted) into logic conditions that run on the flight controller.

If you're familiar with the traditional logic conditions interface, you can think of
JavaScript programming as a more user-friendly syntax that generates the same logic
conditions behind the scenes.

See the [Programming Framework documentation](../../Programming%20Framework.md) for
details about the underlying logic conditions system.
```

### Step 5: Test All Links (15 min)

- Verify relative paths work correctly
- Check that all cross-links function
- Test in markdown viewer

### Step 6: Commit in INAV Repo (10 min)

```bash
cd inav
git add docs/Programming\ Framework.md
git add docs/javascript_programming/

git commit -m "$(cat <<'EOF'
Add JavaScript programming documentation to INAV docs

- Move transpiler documentation from inav-configurator to docs/javascript_programming/
- Includes docs, API definitions, examples, and scripts
- Add cross-links from Programming Framework.md to JavaScript docs
- Add cross-links from JavaScript docs back to Programming Framework.md
- Improves documentation discoverability and centralization

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Step 7: Remove Old Files from inav-configurator (15 min)

```bash
cd inav-configurator
git rm -r js/transpiler/docs
git rm -r js/transpiler/api
git rm -r js/transpiler/examples
git rm -r js/transpiler/scripts  # if copied
```

**Important:** Keep `js/transpiler/transpiler/` - only remove documentation directories

### Step 8: Commit in inav-configurator (10 min)

```bash
git commit -m "$(cat <<'EOF'
Move transpiler documentation to INAV repository

- Documentation moved to inav/docs/javascript_programming/
- Transpiler code remains in js/transpiler/transpiler/
- Copy of TESTING_GUIDE.md added to tests directory
- Centralizes INAV documentation in main repository

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Verification Checklist

- [ ] TESTING_GUIDE.md exists in `inav-configurator/js/transpiler/transpiler/tests/`
- [ ] All docs moved to `inav/docs/javascript_programming/`
- [ ] Programming Framework.md has links to JavaScript docs
- [ ] JAVASCRIPT_PROGRAMMING_GUIDE.md has links to Programming Framework.md
- [ ] All cross-links work correctly
- [ ] Old directories removed from inav-configurator
- [ ] Transpiler code (`js/transpiler/transpiler/`) still exists in inav-configurator
- [ ] Commits made in both repositories

## Success Criteria

- [ ] Documentation successfully moved to INAV repo
- [ ] TESTING_GUIDE.md in two locations (docs and tests)
- [ ] Cross-links functional in both directions
- [ ] Clean commits in both repositories
- [ ] No documentation left orphaned

## Notes

- This affects **two repositories** - coordinate commits
- Work on `programming_transpiler_js` branch
- Test links carefully - different repo structure
- Don't move transpiler code, only documentation
- Both commits should reference each other in messages

## Estimated Time

- Copy TESTING_GUIDE.md: 5 minutes
- Move documentation: 30-45 minutes
- Add cross-links: 30 minutes
- Test links: 15 minutes
- Git operations: 30 minutes

**Total:** ~2-3 hours

## Completion

Send report to `claude/manager/inbox/` with:
- Both commit hashes (inav and inav-configurator)
- Confirmation all links work
- Summary of files moved
- Any issues encountered

---

**Manager**
