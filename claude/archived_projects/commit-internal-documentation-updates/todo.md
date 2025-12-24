# Todo List: Commit Internal Documentation Updates

## Phase 1: Review Changes

- [ ] Review modified files
  - [ ] Run `git diff --stat`
  - [ ] Review skill file changes (`.claude/skills/*/SKILL.md`)
  - [ ] Review role documentation changes (`claude/*/README.md`, `CLAUDE.md`)
  - [ ] Review project index changes (`claude/projects/INDEX.md`)
  - [ ] Check for sensitive information (API keys, tokens, passwords)

- [ ] Review untracked files
  - [ ] Run `git status --short | grep "^??"`
  - [ ] Identify new skills directories
  - [ ] Identify research/analysis documents
  - [ ] Identify test tools and scripts
  - [ ] Identify files to exclude (temp files, build artifacts)

- [ ] Create exclusion list
  - [ ] Submodules (PrivacyLRS/, inav/, inav-configurator/, uNAVlib/)
  - [ ] Temporary test files (evaluate test_*.py, test_*.sh at root)
  - [ ] System errors ("c -l|" - appears to be typo/error)
  - [ ] Any files that should be in .gitignore

## Phase 2: Stage Files

### Skills
- [ ] Stage all modified skills
  ```bash
  git add .claude/skills/
  ```

### Role Documentation
- [ ] Stage developer documentation
  ```bash
  git add claude/developer/README.md claude/developer/CLAUDE.md
  ```

- [ ] Stage manager documentation
  ```bash
  git add claude/manager/README.md
  ```

- [ ] Stage release manager documentation
  ```bash
  git add claude/release-manager/README.md
  git add claude/release-manager/download_guide.md
  ```

- [ ] Stage security analyst documentation
  ```bash
  git add claude/security-analyst/README.md
  git add claude/security-analyst/CLAUDE.md
  ```

### Project Tracking
- [ ] Stage INDEX.md updates
  ```bash
  git add claude/projects/INDEX.md
  ```

- [ ] Stage new project directory
  ```bash
  git add claude/projects/coordinate-crsf-telemetry-pr-merge/
  ```

### Research & Analysis Documents
- [ ] Stage developer research documents
  ```bash
  git add claude/developer/2025-12-07-crsf-telemetry-testing-status.md
  git add claude/developer/crsf-*.md
  git add claude/developer/github-pages-implementation-plan.md
  git add claude/developer/pwa-tcp-websocket-analysis.md
  git add claude/developer/sitl-websocket-feasibility.md
  git add claude/developer/websocket-implementation-complete.md
  ```

- [ ] Stage release manager documents
  ```bash
  git add claude/release-manager/9.0.0-*.md
  git add claude/release-manager/CHANGELOG-2025-12-06.md
  git add claude/release-manager/INCOMPATIBLE-SETTINGS-WORKFLOW.md
  git add claude/release-manager/dmg-verification-implementation.md
  git add claude/release-manager/macos-build-analysis.md
  ```

- [ ] Stage security analyst documents
  ```bash
  git add claude/security-analyst/finding5-*.md
  git add claude/security-analyst/lq-counter-*.md
  git add claude/security-analyst/privacylrs-test-infrastructure-notes.md
  git add claude/security-analyst/test_counter_never_reused_investigation.md
  ```

### Test Tools & Scripts
- [ ] Stage INAV test tools
  ```bash
  git add claude/test_tools/inav/test_crsf_telemetry.sh
  git add claude/test_tools/inav/quick_test_crsf.sh
  git add claude/test_tools/inav/2025-11-25-test-instructions.md
  ```

- [ ] Stage developer test tools
  ```bash
  git add claude/developer/test_tools/
  ```

- [ ] Stage release manager scripts
  ```bash
  git add claude/release-manager/find-incompatible-settings.sh
  git add claude/release-manager/verify-dmg-contents.sh
  git add claude/release-manager/rename-firmware-for-release.sh
  ```

### Verification
- [ ] Review all staged files
  ```bash
  git status
  git diff --cached --stat
  git diff --cached --name-only
  ```

- [ ] Verify no sensitive information staged
  ```bash
  git diff --cached | grep -i "password\|token\|api_key\|secret"
  ```

- [ ] Verify submodules not staged
  ```bash
  git diff --cached --name-only | grep -E "^(PrivacyLRS|inav|inav-configurator|uNAVlib)/"
  ```

## Phase 3: Create Commit

- [ ] Draft commit message
  - [ ] Title: "Docs: Update internal documentation and tooling"
  - [ ] Summary of skills updates
  - [ ] Summary of role documentation updates
  - [ ] Summary of project tracking updates
  - [ ] Summary of research documents
  - [ ] Summary of test tools
  - [ ] Note: Internal documentation only, no source code

- [ ] Save commit message to file
  ```bash
  cat > /tmp/commit_msg.txt <<'EOF'
  [commit message content]
  EOF
  ```

- [ ] Create commit
  ```bash
  git commit -F /tmp/commit_msg.txt
  ```

- [ ] Review commit
  ```bash
  git show --stat
  git log --oneline -1
  ```

## Phase 4: Push to Repository

- [ ] Verify current branch
  ```bash
  git branch --show-current
  ```

- [ ] Push to origin
  ```bash
  git push origin master
  ```

- [ ] Verify push succeeded
  ```bash
  git log --oneline -1
  git status
  ```

## Phase 5: Verification & Cleanup

- [ ] Check working directory status
  ```bash
  git status
  ```

- [ ] Verify expected files remain uncommitted
  - [ ] Submodules (normal - separate repos)
  - [ ] Temporary test files (if excluded intentionally)

- [ ] Create list of intentionally excluded files
  - [ ] Document why each was excluded
  - [ ] Verify none should have been committed

- [ ] Clean up temporary files
  ```bash
  rm /tmp/commit_msg.txt
  ```

## Completion Report

- [ ] Draft completion report for Manager
  - [ ] Number of files committed
  - [ ] Categories of changes
  - [ ] Commit hash
  - [ ] Any excluded files and why
  - [ ] Verification results

- [ ] Send report to Manager
  ```bash
  # Save as: claude/developer/sent/2025-12-07-HHMM-documentation-commit-complete.md
  # Copy to: claude/manager/inbox/
  ```

## Final Checklist

- [ ] All relevant documentation committed
- [ ] All test tools committed
- [ ] Meaningful commit message created
- [ ] No sensitive information committed
- [ ] No submodules committed
- [ ] Changes pushed successfully
- [ ] Completion report sent
- [ ] Project can be archived

---

## Notes

**Files to Evaluate (at root level):**
- `serial_printf_debugging.md` - Check if this is valuable or temporary
- `test_align_mag.py` - Related to align_mag CLI investigation?
- `test_cli_mag.sh` - Related to align_mag CLI investigation?
- `"c -l|"` - Appears to be file system error, should delete

**If in doubt:**
- Commit valuable documentation and tools
- Exclude temporary test files unless they're reusable
- Can always commit more files later
- Better to commit too much than lose valuable work

**Alternative: Multiple Commits**
Could split into themed commits:
1. Skills updates
2. Role documentation
3. Research documents
4. Test tools

Single comprehensive commit is acceptable and faster for internal docs.
