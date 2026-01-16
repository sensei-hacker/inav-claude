# Cross-Role Communication Matrix

This document defines how roles communicate with each other in the INAV project.

## Roles

| Role | Directory | Primary Responsibility |
|------|-----------|----------------------|
| **Manager** | `claude/manager/` | Project planning, task assignment, progress tracking |
| **Developer** | `claude/developer/` | Code implementation, bug fixes, testing |
| **Release Manager** | `claude/release-manager/` | Builds, releases, tagging |
| **Tester** | `claude/tester/` | Test execution, bug reporting (future) |

## Communication Channels

### Manager ↔ Developer

| Direction | Message Types | Examples |
|-----------|--------------|----------|
| Manager → Developer | Task assignments, guidance, questions | "Implement feature X", "Fix bug Y" |
| Developer → Manager | Completion reports, status updates, blockers, questions | "Task complete", "Blocked by Z" |

### Manager ↔ Release Manager

| Direction | Message Types | Examples |
|-----------|--------------|----------|
| Manager → Release Manager | Release requests, timing coordination | "Ready to release 8.0.1" |
| Release Manager → Manager | Release status, blockers, completion | "Release published", "Build failing" |

### Developer ↔ Release Manager

| Direction | Message Types | Examples |
|-----------|--------------|----------|
| Developer → Release Manager | Hotfix notifications, build issues | "Critical fix merged, needs release" |
| Release Manager → Developer | Build failures, missing dependencies | "Target X fails to build" |

### Future: Tester Communications

| Direction | Message Types | Examples |
|-----------|--------------|----------|
| Manager → Tester | Test requests | "Test release candidate" |
| Tester → Manager | Test results, bug reports | "Found issue in feature X" |
| Tester → Developer | Bug details, reproduction steps | "Steps to reproduce bug" |
| Developer → Tester | Fix verification requests | "Please verify fix" |

## Email System

### Folder Structure (per role)

```
claude/{role}/email/
├── inbox/           # Incoming messages
├── inbox-archive/   # Processed messages
├── sent/            # Copies of sent messages
└── outbox/          # Drafts awaiting delivery
```

### Sending a Message

1. Create message file in `{your-role}/email/sent/` (or `outbox/` for drafts)
2. Copy file to `{recipient-role}/email/inbox/`
3. Recipient processes and archives to `email/inbox-archive/`

### File Naming Convention

```
YYYY-MM-DD-HHMM-{type}-{brief-description}.md

Types:
- task      - Task assignment
- completed - Completion report
- status    - Status update
- question  - Question needing answer
- response  - Response to question
- reminder  - Future action reminder
- guidance  - Direction or decision
```

### Message Template

```markdown
# {Type}: {Title}

**Date:** YYYY-MM-DD HH:MM
**From:** {Role}
**To:** {Role}
**Re:** {Related task/project if applicable}

## Content

{Message body}

---
**{Your Role}**
```

## Workflow Examples

### Task Assignment Flow

```
1. Manager creates task in manager/email/sent/
2. Manager copies to developer/email/inbox/
3. Developer reads and implements
4. Developer creates report in developer/email/sent/
5. Developer copies to manager/email/inbox/
6. Manager reviews and archives
```

### Release Coordination Flow

```
1. Manager notifies release-manager of readiness
2. Release Manager builds and tests
3. Release Manager reports status to Manager
4. If issues: Release Manager notifies Developer
5. Developer fixes, notifies Release Manager
6. Release Manager publishes, notifies Manager
```

### Blocker Escalation Flow

```
1. Developer hits blocker
2. Developer creates message in developer/email/outbox/ (draft)
3. Developer refines message
4. Developer moves to developer/email/sent/, copies to manager/email/inbox/
5. Manager reviews and responds
```

## Best Practices

1. **Be specific** - Include file paths, commit hashes, PR numbers
2. **One topic per message** - Easier to track and archive
3. **Include context** - Reference related projects/tasks
4. **Use templates** - Consistent formatting helps parsing
5. **Archive promptly** - Keep inboxes clean
6. **Check outbox** - Don't forget draft messages
