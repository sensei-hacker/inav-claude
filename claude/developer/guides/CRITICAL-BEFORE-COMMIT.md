# ⚠️ CRITICAL CHECKLIST - Read Before Git Commit

**Complete this checklist before running `git commit`:**

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

### 8. Branches

**NEVER** merge another branch to master except by pulling from remote repo.

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

<!-- Add new lessons above this line -->
