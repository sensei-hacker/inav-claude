# Repository Locks

This directory contains lock files to prevent multiple developers from working in the same repository simultaneously.

## Lock Files

- `inav.lock` - Locks the firmware repository (`inav/`)
- `inav-configurator.lock` - Locks the configurator repository (`inav-configurator/`)

## Rules

1. **One developer per repo** - Only one developer can hold a lock on a repository at a time
2. **Parallel work allowed** - One developer can work in `inav/` while another works in `inav-configurator/`
3. **Check before starting** - Always check for existing locks before beginning work
4. **Release when done** - Remove your lock file when task is complete

## Lock File Format

```
LOCKED_BY: Developer
TASK: <project-name or task description>
LOCKED_AT: YYYY-MM-DD HH:MM
BRANCH: <branch-name>
```

## How to Use

### Acquiring a Lock (Developer)

Before starting work that modifies a repository:

1. Check if lock exists: `cat claude/locks/inav.lock` or `cat claude/locks/inav-configurator.lock`
2. If no lock, create one with your details
3. If locked by someone else, wait or ask manager

### Releasing a Lock (Developer)

When task is complete:

1. Remove the lock file: `rm claude/locks/inav.lock`
2. Include in completion report: "Released inav.lock"

### Manager Responsibilities

- Include lock acquisition in task assignments
- Verify locks are released in completion reports
- Resolve conflicts if two tasks need same repo
