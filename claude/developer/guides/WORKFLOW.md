# Developer Workflow (17 steps)

Single source for the developer's task sequence. At the start of every task, copy the
numbered list below into your task-list tool and check steps off as you complete them.
Each step names the agent/skill to use and the guide to read first.

## Key principles (override everything else)

1. **Test-first.** Before fixing a bug, have the `test-engineer` agent write a test that
   reproduces it (step 5). You can't verify a fix you can't reproduce.
2. **The inbox is the queue, not the project tracker.** Step 1 tells you what's pending.
   `claude/projects/active/...` status fields are the manager's bookkeeping and can lag
   behind what you've actually done. If an inbox item looks already finished, check
   `claude/developer/email/sent/` for a prior completion/status mail before assuming it's
   still open.

## The 17 steps

1. **Check inbox for assignments** — `email-manager` agent ("Read my inbox. Current role: developer").
2. **Read the task assignment** — the task file in the inbox.
3. **Create a git branch** — `git-workflow` skill / `scripts/git/new-branch.sh`. Read `CRITICAL-BEFORE-CODE.md`, `git-workflow.md`.
4. **Draft user documentation (if needed)** — only for new features / behavior changes. Read `CRITICAL-BEFORE-CODE.md` step 3.
5. **Reproduce the issue (test should fail)** — `test-engineer` agent. Read `CRITICAL-BEFORE-TEST.md`.
6. **Implement the fix** — check specialized agents first, then code. Read `CRITICAL-BEFORE-CODE.md`, `coding-standards.md`.
7. **Compile** — `inav-builder` agent (never `cmake`/`make`/`npm build` directly).
8. **Verify the fix (test should pass)** — `test-engineer` agent. Read `CRITICAL-BEFORE-TEST.md`.
9. **Finalize user documentation (if drafted)** — update the draft, add to `inav/docs/` or `inavwiki/`. Read `CRITICAL-BEFORE-PR.md`.
10. **Commit** — follow git best practices. Read `CRITICAL-BEFORE-COMMIT.md`.
11. **Create a pull request** — `create-pr` skill / `/create-pr`. Read `CRITICAL-BEFORE-PR.md`.
12. **Check PR status and bot suggestions** — `check-pr-bots` agent or `check-builds` skill.
13. **Decide: lesson worth recording?** — against the Capture Rubric; if yes add one line to the relevant guide. Read `guides/README.md`.
14. **Decide: reusable tooling worth keeping?** — against the Capture Rubric; if yes move it out of `workspace/` to its destination convention. Read `guides/README.md`.
15. **Create completion report** — `email-manager` agent.
16. **Notify manager** — `email-manager` agent.
17. **Archive assignment** — `email-manager` agent + `/finish-task` skill.

## Phase → guide map

| When | Read | Workflow step(s) |
|------|------|------------------|
| Starting a task (lock, branch, implement) | `CRITICAL-BEFORE-CODE.md` | 3, 4, 6 |
| Testing / reproducing | `CRITICAL-BEFORE-TEST.md` | 5, 8 |
| Committing | `CRITICAL-BEFORE-COMMIT.md` | 10 |
| PR creation and follow-up | `CRITICAL-BEFORE-PR.md` | 9, 11, 12 |
| Merge conflicts (ad hoc, not a numbered step) | `CRITICAL-BEFORE-MERGE.md` | — |
