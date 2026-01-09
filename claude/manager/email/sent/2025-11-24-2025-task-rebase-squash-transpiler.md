# Task Assignment: Rebase and Squash Transpiler Branch Commits

**Date:** 2025-11-24 20:25
**Project:** rebase-squash-transpiler-branch
**Priority:** Medium
**Estimated Effort:** 2-3 hours
**Branch:** programming_transpiler_js

## Task

Analyze the 37 commits in `programming_transpiler_js` branch and create a git rebase script that squashes them into 3-6 focused, logical commits.

## Background

The `programming_transpiler_js` branch has accumulated 37 commits during development. Before merging to master, these should be squashed into a clean, logical commit history.

**Current:** 37 commits
**Target:** 3-6 commits

## Objective

Create a file `claude/projects/rebase-squash-transpiler-branch/rebase-script.txt` containing a git rebase interactive script in this format:

```
pick b976af64 Cleanup old references that should have been `control_profile`
squash 7600c043 plc javascript transpiler initital commit
squash 906fb00b transpiler: add to navigation
...
```

## Preliminary Analysis

**Current commits** (run this to see them):
```bash
git log --oneline master..programming_transpiler_js --reverse
```

**Suggested groupings (5-6 commits):**

1. **Initial transpiler implementation** (~8 commits)
   - b976af64 through c481da8e
   - Cleanup, initial commit, navigation, Monaco, Acorn parser
   - **pick** first, **squash** rest

2. **Core transpiler features** (~15 commits)
   - 44bab914 through 2f25fd18
   - API definitions, control flow (when→if), operators, error handling
   - **pick** first, **squash** rest

3. **ESM conversion** (~7 commits)
   - 8776626c through 31ecca47
   - Convert all CommonJS to ESM modules
   - **pick** first, **squash** rest

4. **JavaScript variables support** (~4 commits)
   - a9d7cb73 through a4b92ee6
   - VariableHandler, let/var implementation, fixes, documentation
   - **pick** first, **squash** rest

5. **Auto-insert INAV import** (1 commit)
   - e2b16280
   - **pick** (already single commit)

6. **Duplicate column fix** (1 commit)
   - c8d1e78b - **drop** (belongs on master, not this branch)

## Important Notes

### Commit to Drop

**c8d1e78b** "programming.html: activator column shown twice"
- This is the duplicate column bug fix
- It's a separate project assigned to be fixed on **master** branch
- It should NOT be on programming_transpiler_js
- Mark as `drop` in rebase script

### Rebase Commands

- `pick` - Keep commit as-is
- `squash` - Combine with previous commit, preserve message
- `fixup` - Combine with previous commit, discard message
- `drop` - Remove commit entirely

Use `squash` when commit messages provide useful context.
Use `fixup` for trivial commits like "fix typo" or "remove comments".

## Steps

1. **Review commits:**
   ```bash
   git log master..programming_transpiler_js --oneline --reverse
   ```

2. **Analyze and group:**
   - Group commits by logical feature/phase
   - Identify first commit in each group (will be `pick`)
   - Identify subsequent commits in group (will be `squash` or `fixup`)

3. **Create rebase script:**
   - File: `claude/projects/rebase-squash-transpiler-branch/rebase-script.txt`
   - Format exactly like git rebase interactive:
   ```
   pick <hash> <message>
   squash <hash> <message>
   squash <hash> <message>
   pick <hash> <message>
   squash <hash> <message>
   ...
   drop c8d1e78b programming.html: activator column shown twice
   ```

4. **Document rationale:**
   - Update project summary with grouping decisions
   - Explain why commits were combined
   - Note any alternative approaches

5. **Validate:**
   - Ensure all 37 commits accounted for
   - Verify final count: 3-6 commits
   - Confirm c8d1e78b is marked `drop`

## Output Format Example

```
# Rebase script for programming_transpiler_js
# Target: 5 focused commits from 37 original commits

# Group 1: Initial transpiler implementation
pick b976af64 Cleanup old references that should have been `control_profile`
squash 7600c043 plc javascript transpiler initital commit
squash 906fb00b transpiler: add to navigation
squash 5c204179 transpiler: move directory, commonjs module
squash 2cfe68f7 transpiler: local Monaco editor
squash d982ecef javascript programming, Acorn parser
squash d4568061 javascript programming, fix loading LCs
fixup c481da8e javascript programming: Remove some comments

# Group 2: Core transpiler features
pick 44bab914 javascript programming: update api definitions
squash 87dcb004 javascript programming: add several files
...

# Group 3: ESM conversion
pick 8776626c transpiler: convert exports from CommonJS to ESM
squash 821316e9 transpiler: convert imports from CommonJS to ESM
...

# etc.
```

## Success Criteria

- [ ] Rebase script created in proper git format
- [ ] All 37 commits accounted for
- [ ] Final commit count: 3-6 commits
- [ ] Each group has logical cohesion
- [ ] c8d1e78b marked as `drop`
- [ ] Rationale documented

## Completion

Send report to `claude/manager/inbox/` with:
- Rebase script file path
- Summary of grouping decisions
- Final commit count
- Any concerns or alternatives

---

**Manager**
