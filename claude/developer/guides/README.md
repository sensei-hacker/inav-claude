# Developer Guides - Context-Sensitive Checklists

These critical checklists provide **just-in-time information** - read them right before the operation they describe.

## When to Read Each Guide

| Operation | Read This File | Purpose |
|-----------|----------------|---------|
| **At the start of any task** | `WORKFLOW.md` | The 17-step sequence (single source) — copy into your task list |
| **Before modifying code** | `CRITICAL-BEFORE-CODE.md` | Lock files, branch creation, agent usage |
| **Before `git commit`** | `CRITICAL-BEFORE-COMMIT.md` | Git best practices, commit message rules |
| **Before creating PR** | `CRITICAL-BEFORE-PR.md` | Testing requirements, PR checklist, bot checks |
| **Before/during testing** | `CRITICAL-BEFORE-TEST.md` | Test-first approach, testing requirements |
| **Before resolving merge conflicts** | `CRITICAL-BEFORE-MERGE.md` | Apply diffs not files, verify no dropped features |
| **When debugging/fixing bugs** | `root-cause-analysis.md` | Four-level framework: symptom → cause → systemic cause → scope |
| **Finding tools and techniques** | `debugging-guide.md` | Serial printf, GDB, Chrome DevTools, when to use each |

## Integration Points

These guides should be read by:

- **Developer (you)** - Read `CRITICAL-BEFORE-CODE.md` when starting a task
- **`/start-task` skill** - Reads and enforces `CRITICAL-BEFORE-CODE.md`
- **`/git-workflow` skill** - Reads and enforces `CRITICAL-BEFORE-COMMIT.md`
- **`/create-pr` skill** - Reads and enforces `CRITICAL-BEFORE-PR.md`
- **`test-engineer` agent** - Has `CRITICAL-BEFORE-TEST.md` in its instructions

## Memory Policy

**Lessons-in-docs is the harness's memory system.** There is no semantic/vector memory
store — the ChromaDB pipeline (per-prompt injection, session ingestion, forget tooling)
was retired 2026-07-10 (see `claude/projects/active/retire-chromadb-memory-stack/`,
or `completed/` once the manager archives it): it ran on every prompt, its disable
switches were uncommitted, and it structurally couldn't share memory across sessions,
roles, and the human the way a doc committed to git does.

**Placement rules** — when you learn something worth keeping, put it where the next
reader who needs it will already be looking:

| Kind of lesson | Where it goes |
|-----------------|----------------|
| Workflow lesson (how to do a step correctly) | The owning `CRITICAL-*.md` guide above |
| Domain/reference fact (protocol quirk, target detail, library behavior) | The owning agent's instructions or its `docs/` reference |
| SITL behavior/quirk | `test-engineer` agent references |

If none of those own the topic, use judgment on the nearest fitting guide rather than
creating a new catch-all file. The Claude Code auto-memory feature (`MEMORY.md` under
`~/.claude/projects/.../memory/`) is intentionally stubbed out — see its own note — in
favor of this policy.

## Capture Rubric

At task completion (17-step workflow steps 13-14, and `/finish-task`), **decide —
don't default to writing.** The gate is "did you consider it," never "did you
produce something."

**Lesson worth recording?** Yes if it's non-obvious and would generalize: a hidden
constraint, a workaround for a specific broken tool/environment, a mapping or trap
that will recur on similar future work (e.g. "DMA option N maps to stream X, shared
with peripheral Y"), a wrong assumption that cost real time to unwind. No if it's
routine, already documented, or specific to this exact task with no generalization.

If yes, first check whether the lesson has a clear, specific triggering tool or
command (e.g. "whenever `X` is run, remember Y") — if so, prefer adding a short
(1-3 line) rule to `.claude/hooks/tool_context_injections.yaml` instead of, or in
addition to, the guide entry. It reaches the model deterministically at the moment
of action rather than depending on the guide being read; see that file's header for
the schema and the "keep it short, point at docs for detail" convention. Otherwise
— or for anything broader than a single command trigger — add one line to the
topic's existing "Self-Improvement" section, or update the guide as appropriate
(see Placement rules above). If no, do nothing further.

**Tooling worth keeping?** Yes if a plausible *future* task — not just this one —
would reuse the script/test harness/checklist as-is or with minor changes. No if
it's task-specific glue that only works for this exact bug/target, or duplicates an
existing agent/skill/script. If yes, move it out of the gitignored `workspace/` to
its existing destination: shared scripts to `claude/developer/scripts/<category>/`,
agent-specific tools to `claude/agents/<agent-name>/scripts/` (see this README's
"Continuous Improvement" section) — with a one-line note on what it's for. If no,
do nothing further.

## Design Philosophy

**Problem:** 840-line README is overwhelming; critical rules get forgotten.

**Solution:** Context-sensitive checklists (< 50 lines each) read exactly when needed.

**Benefits:**
- Critical info delivered at the right moment
- No cognitive overload from reading everything upfront
- Each checklist is short, focused, and memorable
- Enforced by skills/agents that read them automatically

## File Sizes

Each checklist should be readable in under 2 minutes (~120 lines max). If one grows beyond
that, split or streamline it — growth is usually the "Self-Improvement" lesson block at the
bottom, which should stay concise and actionable, not narrative.
