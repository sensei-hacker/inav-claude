# ⚠️ CRITICAL CHECKLIST - Read Before Git Commit

**Complete this checklist before running `git commit`:**

**Use a task list tool to track each step as you complete it.**

## Git Best Practices

### 1. NEVER Use `git add -A`

Review each file individually:
```bash
git status
git diff path/to/file.c
git add path/to/file.c path/to/file.h
```

### 2. Human Review of Commit Message

**ALWAYS** use editor for commit review:
```bash
GIT_EDITOR="gedit" git commit --edit -m "Your commit message"
```

### 3. Commit Message Rules

**❌ NEVER:**
- End with "Generated with https://claude.com/claude-code"
- Mention Claude or AI assistance in commit messages
- Use generic messages like "fix bug" or "update code"
- Do NOT mention Claude in commit messages. - Do NOT put "Co-Authored-By: Claude Sonnet 4.6" or similar in a commit message

**✅ ALWAYS:**
- Focus on WHY, not just WHAT
- Be specific: "Fix blackbox corruption when no motors defined in mixer"
- Keep it concise (1-2 sentences)
- Follow repository's existing commit style (check `git log`)

### 4. Use HEREDOC for Multi-line Messages

```bash
git commit -m "$(cat <<'EOF'
Fix blackbox corruption when no motors defined in mixer

The blackbox logger assumed at least one motor exists.
EOF
)"
```

### 5. NEVER Amend Unless ALL Conditions Met

**Only use `git commit --amend` when:**
1. HEAD commit was created by you in this conversation, AND
2. Commit has NOT been pushed to remote, AND
3. (User explicitly requested amend OR pre-commit hook auto-modified files)

**If commit FAILED or was REJECTED:** NEVER amend - fix issue and create NEW commit

### 6. NEVER Use --no-verify

Let pre-commit hooks run. They catch important issues.

### 7. Run Linter (if applicable)

Before committing, run the appropriate linter for your changes:

**C code:**
```bash
clang-tidy src/file.c -- -I. -Iinav/src/main
```

**JavaScript:**
```bash
cd inav-configurator
eslint src/file.js
# Auto-fix minor issues:
eslint --fix src/file.js
```

**Shell scripts:**
```bash
shellcheck script.sh
```

Fix any issues before committing.

### 8. Branches and Merges

**NEVER** merge another branch to master except by pulling from remote repo.

#### ⛔ ABSOLUTE PROHIBITION: Never merge a higher version into a lower one

This has caused serious damage twice. Version branches represent specific release points in time:
- `release/9.x` = the 9.x release (older)
- `maintenance-10.x` = the December release (newer)

**NEVER pull a higher version into a lower one:**

- ❌ `git merge maintenance-10.x` while on `release/9.x` — drags future features into old release

**The direction that IS legitimate (lower → higher):**
- ✅ Backporting: cherry-picking or merging a 9.x fix INTO 10.x or master is fine
- ✅ Merging a PR author's feature/fix branch into its intended base branch
- ✅ Merging the base branch INTO a PR branch to resolve conflicts (see CRITICAL-BEFORE-MERGE.md)

If a CI failure looks like it could be fixed by merging another version branch in, **STOP**. That is always the wrong diagnosis. The real fix is surgical — find the specific conflicting lines and fix them with the Edit tool, exactly as you would fix any other compile error.

When a legitimate upward merge IS needed (carrying 9.x changes into 10.x), use the procedure in `guides/merge-release-into-next-version.md`.

### 9. Pushing

**NEVER push to `upstream` directly.** Always push to `origin` (your fork) and open a PR.

Pushing directly to `upstream` bypasses code review and branch protection. The only exception is if the user types an explicit instruction like "push this to upstream" — even then, confirm exactly which branch and why before executing.

---

**Ready to commit? Review the checklist above, then proceed.**

---

## Self-Improvement: Lessons Learned

When you discover something important about GIT COMMIT PRACTICES that will likely help in future sessions, add it to this section. Only add insights that are:
- **Reusable** - will apply to future commit operations, not one-off situations
- **About git/commits** - commit messages, staging, hooks, amending, linting
- **Concise** - one line per lesson

Use the Edit tool to append new entries. Format: `- **Brief title**: One-sentence insight`

### Lessons

- **Don't route around permission/auth restrictions on your own initiative**: Narrow GitHub token scopes, force-push blocks, etc. are deliberate guardrails, not bugs — agents have previously force-pushed to public branches after amending commits, destroying other people's work. If an operation fails due to a permission restriction, report the failure; only switch to a broader-scoped credential or bypass it if the user explicitly authorizes that specific case.

<!-- Add new lessons above this line -->
