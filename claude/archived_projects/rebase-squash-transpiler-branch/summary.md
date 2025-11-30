# Rebase and Squash Transpiler Branch Commits

**Status:** 📝 PLANNED
**Type:** Git Operations / Branch Management
**Priority:** Medium
**Created:** 2025-11-24
**Branch:** programming_transpiler_js

## Problem

The `programming_transpiler_js` branch contains 37 commits from master. Many of these are incremental development commits that should be squashed into focused, logical commits before merging to master.

Current commit count: **37 commits**
Target commit count: **3-6 commits**

## Objective

Analyze the commit history of `master..programming_transpiler_js` and create a rebase plan that squashes commits into 3-6 logical, focused commits.

## Approach

1. Review all 37 commits and group by logical feature/phase
2. Identify which commits should be squashed together
3. Create a rebase script in the format used by `git rebase -i`
4. Output suggested squash plan for review

## Commit Groups (Preliminary Analysis)

Based on `git log master..programming_transpiler_js`:

**Initial Implementation** (8 commits):
- b976af64 Cleanup old references
- 7600c043 plc javascript transpiler initial commit
- 906fb00b transpiler: add to navigation
- 5c204179 transpiler: move directory, commonjs module
- 2cfe68f7 transpiler: local Monaco editor
- d982ecef javascript programming, Acorn parser
- d4568061 javascript programming, fix loading LCs
- c481da8e javascript programming: Remove some comments

**Core Features Development** (15 commits):
- 44bab914 through 2f25fd18
- API definitions, when() to if(), timer/delay, error reporting, etc.

**UI Changes** (1 commit):
- 7eeb93a2 programming UI change 01

**ESM Conversion** (7 commits):
- 8776626c through 31ecca47
- Convert CommonJS to ESM throughout codebase

**Variables Support** (4 commits):
- a9d7cb73 transpiler: add VariableHandler foundation
- 30d7a3e7 transpiler: implement let/var support
- a7eab9ef transpiler: fix VariableHandler state reuse
- a4b92ee6 transpiler: add polish features and documentation

**Auto-Import Feature** (1 commit):
- e2b16280 transpiler: Automatically add import inav if missing

**Bug Fix** (1 commit):
- c8d1e78b programming.html: activator column shown twice
  - **NOTE:** This commit should NOT be on this branch - it's assigned as separate project on master

## Suggested Commit Structure (Target: 5-6 commits)

1. **Initial transpiler implementation** - Squash initial 8 commits
   - First Monaco-based JavaScript transpiler

2. **Core transpiler features** - Squash 15+ feature commits
   - API definitions, control flow, operators, error handling

3. **ESM conversion** - Squash 7 ESM commits
   - Convert entire codebase from CommonJS to ESM

4. **JavaScript variables support** - Squash 4 variable commits
   - Add let/const/var support with VariableHandler

5. **Auto-insert INAV import** - Keep as single commit
   - Automatically add missing import statement

6. **Drop duplicate column fix** - This belongs on master, not this branch

## Deliverable

Create file: `claude/projects/rebase-squash-transpiler-branch/rebase-script.txt`

**Format:** Git rebase interactive format
```
pick <hash> <message>
squash <hash> <message>
squash <hash> <message>
...
```

## Notes

- The `c8d1e78b` commit (duplicate column fix) should be dropped - it's a separate project assigned to master
- Review commit messages to create clear, descriptive final messages
- Ensure each final commit represents a logical, atomic change
- Squashing preserves all changes, just combines commit history

## Success Criteria

- [ ] All 37 commits analyzed
- [ ] Logical groupings identified
- [ ] Rebase script created in git format
- [ ] Final commit count: 3-6 commits
- [ ] Each commit has clear focus/purpose
- [ ] Duplicate column fix marked for dropping

## Estimated Time

~2-3 hours
- Review commits: 1 hour
- Group and analyze: 30 minutes
- Create rebase script: 30 minutes
- Document decisions: 30 minutes
