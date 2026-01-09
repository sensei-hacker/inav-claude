# Examples Directory

This directory contains curated high-quality examples from real INAV project work. Use these as templates and references when creating new projects or communications.

## Directory Structure

```
examples/
├── README.md                    # This file
├── projects/
│   ├── completed/               # Examples of completed projects
│   │   ├── fix-gps-recovery-issue-11049/
│   │   │   ├── summary.md       # Bug fix with GitHub issue
│   │   │   └── todo.md          # Task tracking for bug fix
│   │   └── implement-pmw3901-opflow-driver/
│   │       └── summary.md       # Feature implementation
│   └── active/
│       └── enable-galileo-optimize-gps-rate/
│           ├── summary.md       # Feature with research phases
│           └── todo.md          # Detailed phased task list
└── emails/
    ├── manager/
    │   ├── task-assignment-example.md       # How to assign tasks
    │   └── completion-acknowledgment-example.md  # How to acknowledge work
    └── developer/
        ├── completion-report-example.md     # How to report completion
        └── status-report-example.md         # How to report progress
```

## What These Examples Demonstrate

### Projects

**fix-gps-recovery-issue-11049** (Bug Fix)
- Clear problem statement linked to GitHub issue
- Scoped objectives and implementation steps
- Safety considerations noted
- Success criteria as checklist

**implement-pmw3901-opflow-driver** (Feature)
- Technical implementation details
- File locations and code patterns
- Clear scope boundaries

**enable-galileo-optimize-gps-rate** (Feature with Research)
- Phased approach (research → implement → test)
- Decision points documented
- Background and rationale included
- Detailed todo breakdown

### Emails

**Task Assignment** (Manager → Developer)
- Clear task description
- Background context
- Step-by-step instructions
- Success criteria
- Files to check
- Expected deliverables

**Completion Acknowledgment** (Manager → Developer)
- Summary of accomplishments
- Recognition of quality work
- PR links and status
- Next steps

**Completion Report** (Developer → Manager)
- Concise summary
- PR link prominently displayed
- Technical solution explained
- Testing results
- Checklist status

**Status Report** (Developer → Manager)
- Executive summary at top
- Detailed findings
- Recommendations with rationale
- Questions for manager
- Clear next steps

## Using These Examples

### Creating a New Project

1. Copy the appropriate example's structure
2. Replace placeholder content with your specifics
3. Adjust sections as needed for your project type

### Writing Emails

1. Follow the format of the relevant example
2. Include all standard sections
3. Be concise but complete
4. Always include actionable items or clear status

## Key Patterns

### Project Summaries Should Have

- Status, Priority, Type, Dates
- Clear Overview (2-3 sentences)
- Problem statement
- Objectives (numbered)
- Scope (In/Out)
- Implementation steps
- Success criteria (checkboxes)
- Related links (Issues, PRs)

### Todo Lists Should Have

- Phases with clear names
- Checkboxes for all items
- Completion section
- Logical ordering

### Emails Should Have

- Date and reference info
- Clear subject/purpose
- Background/context
- Actionable items
- Status checklist (for reports)
