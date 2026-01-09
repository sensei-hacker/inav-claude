# Claude Workspace Installation

Welcome! This guide will help you set up the Claude workspace for INAV development.

## First-Time Setup

### Option 1: Fresh Start (Recommended for New Users)

Start with clean project and email directories, keeping only the examples as reference.

```bash
./claude/install.sh fresh
```

This will:
- Clear `projects/active/`, `projects/backburner/`
- Clear all email directories (`inbox/`, `sent/`, etc.)
- Keep `projects/completed/` (historical reference)
- Keep `examples/` (templates and references)
- Create necessary directory structure

### Option 2: Continue with Existing Data

Keep all existing projects and emails from the previous owner (sensei-hacker).

```bash
./claude/install.sh continue
```

This will:
- Keep all existing projects and their history
- Keep all existing emails
- Just verify directory structure exists

### Option 3: Manual Setup

If you prefer to set up manually:

1. **Review existing content:**
   ```bash
   ls claude/projects/active/
   ls claude/projects/completed/
   ls claude/manager/email/inbox/
   ```

2. **Clear what you don't need:**
   ```bash
   # Clear active projects (keep completed for reference)
   rm -rf claude/projects/active/*
   rm -rf claude/projects/backburner/*

   # Clear emails
   rm -rf claude/*/email/inbox/*
   rm -rf claude/*/email/sent/*
   ```

3. **Create directory structure:**
   ```bash
   mkdir -p claude/projects/{active,backburner,completed}
   mkdir -p claude/{manager,developer,release-manager,security-analyst}/email/{inbox,sent,outbox,inbox-archive}
   mkdir -p claude/developer/workspace
   mkdir -p claude/locks
   ```

## Directory Structure

After installation, you'll have:

```
claude/
├── INSTALL.md              # This file
├── examples/               # High-quality templates (always kept)
│   ├── projects/
│   └── emails/
├── projects/
│   ├── active/             # Current work
│   ├── backburner/         # Paused projects
│   └── completed/          # Historical reference
├── manager/
│   └── email/
├── developer/
│   ├── email/
│   └── workspace/          # Temporary working files
├── release-manager/
│   └── email/
├── security-analyst/
│   └── email/
└── locks/                  # Repo lock files
```

## Next Steps

1. **Choose your role:**
   - Manager: Read `claude/manager/README.md`
   - Developer: Read `claude/developer/README.md`
   - Release Manager: Read `claude/release-manager/README.md`
   - Security Analyst: Read `claude/security-analyst/README.md`

2. **Review examples:**
   - Project templates: `claude/examples/projects/`
   - Email templates: `claude/examples/emails/`

3. **Start working:**
   - Use `/start-task` skill to begin new tasks
   - Use `/finish-task` skill to complete tasks
   - Use `/email` skill to communicate between roles

## Troubleshooting

### "Directory already exists" errors

The install script is safe to run multiple times. It won't delete existing content unless you explicitly choose "fresh" mode.

### Missing directories

Run the install script with any option to create missing directories:
```bash
./claude/install.sh continue
```

### Permission issues

Make the script executable:
```bash
chmod +x claude/install.sh
```

## About This Repository

This workspace supports multi-role INAV development:
- **Manager** - Project planning and task assignment
- **Developer** - Code implementation
- **Release Manager** - Release coordination
- **Security Analyst** - Security review (PrivacyLRS)

The email system enables asynchronous communication between roles across Claude sessions.
