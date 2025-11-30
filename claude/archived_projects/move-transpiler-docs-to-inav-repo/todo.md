# TODO: Move Transpiler Documentation to INAV Repo

**Created:** 2025-11-24
**Status:** Not yet assigned

---

## Phase 1: Copy TESTING_GUIDE.md to Tests Directory

- [ ] Verify source file exists: `inav-configurator/js/transpiler/docs/TESTING_GUIDE.md`
- [ ] Verify destination directory exists: `inav-configurator/js/transpiler/transpiler/tests/`
- [ ] Copy TESTING_GUIDE.md to tests directory:
  ```bash
  cp inav-configurator/js/transpiler/docs/TESTING_GUIDE.md \
     inav-configurator/js/transpiler/transpiler/tests/TESTING_GUIDE.md
  ```
- [ ] Verify copy is successful
- [ ] Stage file in git (do not commit yet)

**Deliverable:** TESTING_GUIDE.md in tests directory

---

## Phase 2: Prepare INAV Repo for New Documentation

- [ ] Navigate to inav repository
- [ ] Create destination directory:
  ```bash
  mkdir -p inav/docs/javascript_programming
  ```
- [ ] Verify directory created successfully

**Deliverable:** Empty javascript_programming directory in inav/docs/

---

## Phase 3: Copy Documentation to INAV Repo

Since these are separate git repositories, we need to copy (not git mv):

- [ ] Copy docs directory:
  ```bash
  cp -r inav-configurator/js/transpiler/docs \
        inav/docs/javascript_programming/docs
  ```

- [ ] Copy api directory:
  ```bash
  cp -r inav-configurator/js/transpiler/api \
        inav/docs/javascript_programming/api
  ```

- [ ] Copy examples directory:
  ```bash
  cp -r inav-configurator/js/transpiler/examples \
        inav/docs/javascript_programming/examples
  ```

- [ ] Copy scripts directory (if needed):
  ```bash
  cp -r inav-configurator/js/transpiler/scripts \
        inav/docs/javascript_programming/scripts
  ```

- [ ] Verify all files copied correctly

**Deliverable:** Documentation copied to inav repo

---

## Phase 4: Add Files to INAV Git

- [ ] Navigate to inav repository
- [ ] Add new files:
  ```bash
  git add docs/javascript_programming/
  ```
- [ ] Verify files staged:
  ```bash
  git status
  ```

**Deliverable:** Files staged in inav repo (do not commit yet)

---

## Phase 5: Add Cross-Links in Programming Framework.md

- [ ] Open `inav/docs/Programming Framework.md`
- [ ] Find appropriate location near beginning (after introduction)
- [ ] Add JavaScript programming section:
  ```markdown
  ## JavaScript-Based Programming (Alternative)

  INAV also supports a JavaScript-based programming interface that provides a more
  familiar syntax for those comfortable with JavaScript. See the
  [JavaScript Programming Guide](javascript_programming/docs/JAVASCRIPT_PROGRAMMING_GUIDE.md)
  for details.

  The JavaScript code is transpiled into traditional logic conditions, so both methods
  ultimately use the same underlying system.
  ```

- [ ] Find "Related Documentation" or similar section (or create one)
- [ ] Add links to JavaScript docs:
  ```markdown
  ## Related Documentation

  - [JavaScript Programming Guide](javascript_programming/docs/JAVASCRIPT_PROGRAMMING_GUIDE.md) -
    Alternative JavaScript-based syntax for programming logic conditions
  - [JavaScript Variables](javascript_programming/docs/JavaScript_Variables.md) -
    Using variables in JavaScript programming
  ```

- [ ] Save file
- [ ] Stage changes:
  ```bash
  git add "docs/Programming Framework.md"
  ```

**Deliverable:** Updated Programming Framework.md with cross-links

---

## Phase 6: Add Cross-Links in JAVASCRIPT_PROGRAMMING_GUIDE.md

- [ ] Open `inav/docs/javascript_programming/docs/JAVASCRIPT_PROGRAMMING_GUIDE.md`
- [ ] Find appropriate location near beginning
- [ ] Add logic conditions relationship section:
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

- [ ] Save file
- [ ] Stage changes:
  ```bash
  git add docs/javascript_programming/docs/JAVASCRIPT_PROGRAMMING_GUIDE.md
  ```

**Deliverable:** Updated JAVASCRIPT_PROGRAMMING_GUIDE.md with cross-links

---

## Phase 7: Test All Links in INAV Repo

- [ ] Test link from Programming Framework.md to JAVASCRIPT_PROGRAMMING_GUIDE.md
- [ ] Test link from Programming Framework.md to JavaScript_Variables.md
- [ ] Test link from JAVASCRIPT_PROGRAMMING_GUIDE.md to Programming Framework.md
- [ ] Verify all relative paths are correct
- [ ] Check that files render correctly in markdown viewer

**Deliverable:** All links verified working

---

## Phase 8: Commit Changes in INAV Repo

- [ ] Review all staged files:
  ```bash
  git status
  ```
- [ ] Create commit:
  ```bash
  git commit -m "$(cat <<'EOF'
  Add JavaScript programming documentation to INAV docs

  - Move transpiler documentation from inav-configurator to inav/docs/javascript_programming/
  - Includes docs, API definitions, examples, and scripts
  - Add cross-links from Programming Framework.md to JavaScript programming docs
  - Add cross-links from JavaScript docs back to Programming Framework.md
  - Improves documentation discoverability and centralization

  Related: programming_transpiler_js branch

  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude <noreply@anthropic.com>
  EOF
  )"
  ```
- [ ] Verify commit successful:
  ```bash
  git log -1
  ```

**Deliverable:** Committed changes in inav repo

---

## Phase 9: Remove Moved Files from inav-configurator Repo

- [ ] Navigate to inav-configurator repository
- [ ] Remove docs directory (content now in inav repo):
  ```bash
  git rm -r js/transpiler/docs
  ```
- [ ] Remove api directory:
  ```bash
  git rm -r js/transpiler/api
  ```
- [ ] Remove examples directory:
  ```bash
  git rm -r js/transpiler/examples
  ```
- [ ] Remove scripts directory (if copied):
  ```bash
  git rm -r js/transpiler/scripts
  ```
- [ ] Verify removals:
  ```bash
  git status
  ```

**Note:** Keep the transpiler code itself (js/transpiler/transpiler/) - only remove documentation

**Deliverable:** Documentation files removed from inav-configurator

---

## Phase 10: Commit Changes in inav-configurator Repo

- [ ] Review changes:
  ```bash
  git status
  ```
- [ ] Create commit for moved docs:
  ```bash
  git commit -m "$(cat <<'EOF'
  Move transpiler documentation to INAV repository

  - Documentation moved to inav/docs/javascript_programming/
  - Transpiler code remains in inav-configurator (js/transpiler/transpiler/)
  - Copy of TESTING_GUIDE.md added to tests directory for convenience
  - Centralizes INAV documentation in main repository

  Related: programming_transpiler_js branch

  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude <noreply@anthropic.com>
  EOF
  )"
  ```
- [ ] Verify commit successful:
  ```bash
  git log -1
  ```

**Deliverable:** Committed changes in inav-configurator repo

---

## Phase 11: Final Verification

- [ ] Verify TESTING_GUIDE.md exists in both locations:
  - [ ] `inav/docs/javascript_programming/docs/TESTING_GUIDE.md`
  - [ ] `inav-configurator/js/transpiler/transpiler/tests/TESTING_GUIDE.md`

- [ ] Verify documentation structure in inav repo:
  ```bash
  tree inav/docs/javascript_programming/
  ```

- [ ] Verify files removed from inav-configurator:
  ```bash
  ls inav-configurator/js/transpiler/
  # Should NOT show docs/, api/, examples/ directories
  # Should show transpiler/ and editor/ directories
  ```

- [ ] Test cross-links again in both repos

**Deliverable:** Complete verification

---

## Phase 12: Completion

- [ ] Document changes made
- [ ] Create summary:
  - Files moved
  - Links added
  - Commits in both repos
- [ ] Send completion report to manager inbox
- [ ] Include both commit hashes

**Deliverable:** Completion report

---

## Reference: File Locations

**Source (inav-configurator):**
- `js/transpiler/docs/TESTING_GUIDE.md`
- `js/transpiler/docs/JAVASCRIPT_PROGRAMMING_GUIDE.md`
- `js/transpiler/docs/*.md`
- `js/transpiler/api/`
- `js/transpiler/examples/`
- `js/transpiler/scripts/`

**Destinations:**
- TESTING_GUIDE.md → Two locations:
  1. `inav/docs/javascript_programming/docs/TESTING_GUIDE.md`
  2. `inav-configurator/js/transpiler/transpiler/tests/TESTING_GUIDE.md`
- All other docs → `inav/docs/javascript_programming/`

**Files to Update:**
- `inav/docs/Programming Framework.md`
- `inav/docs/javascript_programming/docs/JAVASCRIPT_PROGRAMMING_GUIDE.md`

---

## Important Notes

- Work on programming_transpiler_js branch
- This involves TWO repositories - inav and inav-configurator
- Must commit to both repositories
- Keep transpiler code in inav-configurator
- Move only documentation to inav repository
- Test all links before committing
- Coordinate commits in both repos
