# Claude Workspace

This directory contains organizational structures, communication channels, and documentation for Claude Code when working on the INAV codebase.

## Your Role

**Which role are you taking on?**

### 🎯 Development Manager

**You coordinate, track, and assign work.**

📖 **Read your guide:** [`claude/manager/README.md`](manager/README.md)

**Quick actions:**
- Check inbox: `ls claude/manager/inbox/`
- View active projects: `cat claude/projects/INDEX.md`
- Assign tasks: Create in `manager/sent/`, copy to `developer/inbox/`

---

### 💻 Developer

**You implement code based on manager assignments.**

📖 **Read your guide:** [`claude/developer/README.md`](developer/README.md)

**Quick actions:**
- Check inbox: `ls claude/developer/inbox/`
- Build firmware: `cd inav && ./build.sh TARGETNAME`
- Build configurator: `cd inav-configurator && npm start`
- Report completion: Create in `developer/sent/`, copy to `manager/inbox/`

---

### 📦 Release Manager

**You handle tagging, building, and publishing releases.**

📖 **Read your guide:** [`claude/release-manager/README.md`](release-manager/README.md)

**Quick actions:**
- Check latest tags: `git tag --sort=-v:refname | head -5`
- List PRs since tag: `gh pr list --state merged --limit 50`
- Create draft release: `gh release create X.Y.Z --draft`
- Build firmware: `cd inav && mkdir build && cd build && cmake .. && make`
- Build configurator: `cd inav-configurator && npm run dist`

---

## Directory Structure

```
claude/
├── manager/              - Development manager files
│   ├── README.md        - Manager role guide ⭐ START HERE if you're the manager
│   ├── sent/            - Tasks sent to developer
│   ├── inbox/           - Reports from developer
│   └── inbox-archive/   - Archived reports
│
├── developer/            - Developer files
│   ├── README.md        - Developer role guide ⭐ START HERE if you're the developer
│   ├── inbox/           - Tasks from manager
│   ├── sent/            - Reports to manager
│   └── inbox-archive/   - Archived assignments
│
├── release-manager/      - Release manager files
│   ├── README.md        - Release manager guide ⭐ START HERE if you're releasing
│   ├── releases/        - Release notes and changelogs
│   ├── inbox/           - Incoming messages
│   └── sent/            - Outgoing messages
│
├── projects/             - Active projects
│   ├── INDEX.md         - Master project tracking
│   └── <project-name>/  - Individual project directories
│       ├── summary.md
│       └── todo.md
│
├── archived_projects/    - Completed/cancelled projects
│
└── README.md            - This file
```

## Communication Flow

```
Manager creates task
    ↓
manager/sent/ → copy → developer/inbox/
                            ↓
                    Developer reads & implements
                            ↓
developer/sent/ → copy → manager/inbox/
    ↓
Manager reviews & archives
```

## Project Tracking

All projects are tracked in **`claude/projects/INDEX.md`**

- View active projects: `grep "^### 🚧" claude/projects/INDEX.md`
- View completed: `grep "^### ✅" claude/projects/INDEX.md`
- View backburner: `grep "^### ⏸️" claude/projects/INDEX.md`

## Key Principles

### Role Separation

**Manager:**
- ✅ Creates projects and tracks progress
- ✅ Assigns tasks via email
- ✅ Updates INDEX.md
- ✅ Archives completed work
- ❌ Never edits source code

**Developer:**
- ✅ Implements assigned tasks
- ✅ Writes and tests code
- ✅ Reports completion
- ✅ Asks questions when unclear
- ❌ Never directly updates INDEX.md or project tracking

**Release Manager:**
- ✅ Creates version tags in both repos
- ✅ Generates changelogs from merged PRs
- ✅ Builds firmware and configurator
- ✅ Creates and publishes GitHub releases
- ❌ Never modifies source code (only builds it)

### Communication Protocol

1. **Assignments flow:** manager → developer
2. **Reports flow:** developer → manager
3. **All communication** uses the email system (sent/inbox folders)
4. **Archive processed messages** to keep inboxes clean

### Project Lifecycle

```
TODO → IN PROGRESS → COMPLETED → Archived
             ↓
          BACKBURNER (paused)
             ↓
        CANCELLED (abandoned)
```

## Quick Reference

### Manager Commands

```bash
# Check for completion reports
ls -lt claude/manager/inbox/

# View active projects
grep "Status: IN PROGRESS" claude/projects/*/summary.md

# Archive completed project
mv claude/projects/<name> claude/archived_projects/

# Archive completion report
mv claude/manager/inbox/<report>.md claude/manager/inbox-archive/
```

### Developer Commands

```bash
# Check for new assignments
ls -lt claude/developer/inbox/

# Send completion report
cp claude/developer/sent/<report>.md claude/manager/inbox/

# Archive processed assignment
mv claude/developer/inbox/<task>.md claude/developer/inbox-archive/

# Build & test
cd inav && ./build.sh TARGETNAME
cd inav-configurator && npm test
```

## Getting Started

1. **Determine your role** (Manager, Developer, or Release Manager)
2. **Read your role-specific README:**
   - Manager: [`claude/manager/README.md`](manager/README.md)
   - Developer: [`claude/developer/README.md`](developer/README.md)
   - Release Manager: [`claude/release-manager/README.md`](release-manager/README.md)
3. Tell your human which role you have detected and ask them if you should read your inbox now
4. **Start working** according to your role

---

## Need Help?

- **Manager guide:** `claude/manager/README.md` - Project management, task assignment, tracking
- **Developer guide:** `claude/developer/README.md` - Building, testing, coding standards, architecture
- **Release Manager guide:** `claude/release-manager/README.md` - Tagging, building, publishing releases
- **Project index:** `claude/projects/INDEX.md` - All project status and tracking

**Remember:** Read your role-specific README for detailed instructions!
