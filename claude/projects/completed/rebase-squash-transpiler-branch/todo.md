# TODO: Rebase and Squash Transpiler Branch

**Created:** 2025-11-24
**Status:** Not yet assigned

---

## Phase 1: Analyze Commit History

- [ ] Run `git log --oneline master..programming_transpiler_js`
- [ ] Review all 37 commits in chronological order
- [ ] Identify logical groupings by feature/phase
- [ ] Note which commits are fixes vs features
- [ ] Document preliminary groupings

**Deliverable:** List of commit groups with rationale

---

## Phase 2: Create Logical Groups

- [ ] **Group 1: Initial implementation**
  - Identify first set of commits that establish transpiler
  - Should include: initial commit, navigation, Monaco setup, parser

- [ ] **Group 2: Core features**
  - Identify commits that add transpiler features
  - Should include: API definitions, control flow, operators, error handling

- [ ] **Group 3: ESM conversion**
  - Identify all CommonJS → ESM conversion commits
  - Should be atomic: all ESM changes in one commit

- [ ] **Group 4: Variables support**
  - Identify VariableHandler and let/var commits
  - Should be cohesive: complete feature in one commit

- [ ] **Group 5: Auto-import**
  - Single commit already

- [ ] **Note commits to drop**
  - c8d1e78b (duplicate column) - belongs on master

**Deliverable:** Finalized commit groups (3-6 groups)

---

## Phase 3: Create Rebase Script

- [ ] Create `rebase-script.txt` file
- [ ] Format in git rebase interactive style:
  ```
  pick <hash> <message>
  squash <hash> <message>
  ...
  ```
- [ ] First commit in each group: `pick`
- [ ] Subsequent commits in group: `squash` or `fixup`
- [ ] Use `squash` to preserve commit messages
- [ ] Use `fixup` to discard commit message
- [ ] Mark c8d1e78b as `drop`

**Deliverable:** `rebase-script.txt`

---

## Phase 4: Document Decisions

- [ ] Write rationale for each group
- [ ] Explain why commits were combined
- [ ] Note what each final commit will contain
- [ ] Suggest improved commit messages (if needed)
- [ ] Document any concerns or alternatives

**Deliverable:** Documentation in project summary

---

## Phase 5: Review and Validate

- [ ] Verify all 37 commits are accounted for
- [ ] Ensure final count is 3-6 commits
- [ ] Check that each group has logical cohesion
- [ ] Confirm duplicate column commit is dropped
- [ ] Review with manager if uncertain

**Deliverable:** Validated rebase script

---

## Phase 6: Completion

- [ ] Send completion report to manager inbox
- [ ] Include final rebase script
- [ ] Explain grouping decisions
- [ ] Note any alternative approaches considered

**Deliverable:** Completion report

---

## Reference: Current Commits (37 total)

```
b976af64 Cleanup old references that should have been `control_profile`
7600c043 plc javascript transpiler initital commit
906fb00b transpiler: add to navigation
5c204179 transpiler: move directory, commonjs module
2cfe68f7 transpiler: local Monaco editor
d982ecef javascript programming, Acorn parser
d4568061 javascript programming, fix loading LCs
c481da8e javascript programming: Remove some comments
44bab914 javascript programming: update api definitions
87dcb004 javascript programming: add several files
d498c1f8 javascript programming: chnage when() to if()
67c18ae5 javascript programming: more when() to if()
72608fdd javascript programming: several changes
d02ed074 JavaScript programming: Temporarily disable gbar optimization
90a9b4f3 javascript programming: timer, delay
252343c5 javascript programming: improve recursive booleans
8df1a85a javascriupt programming: several updates
1c67a6b1 javascript programming: on.arm
0459e780 javascript programming: update docs
53a6d486 javascript programming: added API parser script and new docs
fdad8b16 javascript programming: handle nested expressions better / Math.abs
8d4241c9 javascript programming: better reporting of errors and warnings
2f25fd18 javascript programming: add error handler module
7eeb93a2 programming UI change 01
8776626c transpiler: convert exports from CommonJS to ESM
821316e9 transpiler: convert imports from CommonJS to ESM
4a61d44f tabs: convert require() to ESM imports
7afb4783 transpiler: correct import paths in javascript_programming.js
cca2b19d transpiler: fix acorn import to use namespace import
775dc0a5 transpiler: remove module.exports from javascript_programming.js
31ecca47 transpiler: convert monaco_loader.js to ESM and fix Vite compatibility
a9d7cb73 transpiler: add VariableHandler foundation for let/var support
30d7a3e7 transpiler: implement let/var variable support (Phase 2)
a7eab9ef transpiler: fix VariableHandler state reuse across multiple transpile calls
a4b92ee6 transpiler: add polish features and documentation for variables
e2b16280 transpiler: AUtmatically add import inav if it's missing
c8d1e78b programming.html: activator column shown twice [DROP - wrong branch]
```

## Notes

- Use `git log --format="%h %s" master..programming_transpiler_js` to get commit list
- Use `git show <hash>` to review individual commits if needed
- Rebase script will be used with: `git rebase -i master`
- Manager will review before executing rebase
