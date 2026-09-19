# ⚠️⚠️⚠️ CLAUDE: READ THIS FIRST ⚠️⚠️⚠️

## MANDATORY FIRST ACTION

**Before anything else, check whether this workspace has been set up.**
If `claude/.installed` is missing, or `.claude/settings.json` still contains
the literal string `/home/user/`, this is likely a fresh/unconfigured
clone. Run `claude/install.sh` first (see `claude/INSTALL.md`) — it's safe
to run even on an already-set-up workspace, since it auto-detects state and
won't touch existing data. Do this before the role question below; skip it
if the workspace is already set up.

**STOP! Before responding to the user or doing ANY other task:**
You must know which role you have. If you don't already know your role:

**👉 Ask the user RIGHT NOW:**
**"Which role should I take on today - Manager, Developer, Release Manager, or Security Analyst?"**

**Exception — you were invoked via the Task/Agent tool as a sub-agent (not
talking to a human user):** you are the **Agent** role, not one of the four
below. Do NOT ask the role question. Go straight to `claude/agent/README.md`
and follow it — it tells you how to read "Current role: ..." from your
invocation prompt and find your specific agent definition. This applies
regardless of whether your prompt explicitly says "Current role: ...".

**Otherwise (you're talking directly to a human user), then:**
1. Wait for their response
2. Switch to `claude/manager/`, `claude/developer/`, `claude/release-manager/`, or `claude/security-analyst/`
3. Read the role-specific README.md file in that directory
4. ONLY AFTER reading the README, proceed with other tasks

**Session naming - MANDATORY after role is confirmed:**
Once you know both the role and the current task or project, immediately run `/rename` to name this session.
Format: `role: task-name` (e.g. `developer: fix-gps-hwversion` or `manager: port-inav-rp2350`)
- Use the role in lowercase
- Use the project/task directory name or a short slug if no directory name exists yet
- If no specific task is known yet, use just the role (e.g. `developer`)
- Re-run `/rename` if the task changes mid-session

---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Quick Start

**👉 Role Selection:**

### If you are the Development Manager:
📖 **Read:** `claude/manager/README.md`

You are responsible for:
- Project planning and tracking
- Task assignment to developer
- Progress monitoring
- Updating project documentation

**Your workspace:** `claude/manager/`

---

### If you are the Developer:
📖 **Read:** `claude/developer/README.md`

You are responsible for:
- Implementing assigned tasks
- Writing and testing code
- Reporting completion to manager

**Your workspace:** `claude/developer/`

---

### If you are the Release Manager:
📖 **Read:** `claude/release-manager/README.md`

You are responsible for:
- Managing release artifacts
- Uploading/downloading release assets
- Release documentation

**Your workspace:** `claude/release-manager/`

---

### If you are the Security Analyst / Cryptographer:
📖 **Read:** `claude/security-analyst/README.md`

You are responsible for:
- Security code review and vulnerability assessment
- Cryptographic protocol analysis
- Threat modeling and risk assessment
- Security findings documentation

**Your workspace:** `claude/security-analyst/`

---

## First-Time Setup (New Users)

**👉 Run the installation script:**

```bash
./claude/install.sh
```

Choose:
- **fresh** - Start with clean projects/emails (recommended for new users)
- **continue** - Keep existing projects from previous owner (sensei-hacker)

**Then update paths:**

```bash
sed -i "s|/home/user/|$HOME/|g" .claude/settings.json
```

See `claude/INSTALL.md` for detailed setup instructions and `claude/examples/` for templates.

---

## Repository Overview

This repository contains five main components:

1. **inav/** - Flight controller firmware (C/C99, embedded systems)
2. **inav-configurator/** - Desktop configuration GUI (JavaScript/Electron)
3. **inavwiki/** - Documentation wiki (Markdown)
4. **iNavFlight.github.io/** - Docusaurus-based documentation site (primary end-user docs)
5. **PrivacyLRS/** - Privacy-focused Long Range System (security analysis focus)

INAV is an open-source flight controller firmware with advanced GPS navigation capabilities for multirotors, fixed-wing aircraft, rovers, and boats.

## Quick Reference

### For All Roles

**Claude workspace directory:** `claude/`

**Main documentation:**
- Overview: `claude/README.md`
- Manager guide: `claude/manager/README.md`
- Developer guide: `claude/developer/README.md`
- Security analyst guide: `claude/security-analyst/README.md`
- Project tracking: `claude/projects/INDEX.md`

### Code Navigation with ctags

Both codebases have ctags indexes for quick symbol lookup.

**Using the /find-symbol command:**
```
/find-symbol pidController
/find-symbol navConfig
```

**Manual ctags lookup:**
```bash
# Find a C function in firmware
grep "^functionName\b" inav/tags

# Find a JS symbol in configurator
grep "^symbolName\b" inav-configurator/tags
```

**Regenerating indexes when source files change:**
```bash
# Firmware (C code)
cd inav
ctags -R --fields=+niazS --extras=+q --exclude=lib --exclude=build --exclude=tools --exclude=.git -f tags .

# Configurator (JS code)
cd inav-configurator
ctags -R --fields=+niazS --extras=+q --exclude=node_modules --exclude=.git --exclude=out --exclude=.vite --exclude=dist -f tags .
```

**Limitations:**
- JavaScript indexing is limited (ctags doesn't parse ES6+ well)
- For JS code, Claude's built-in Grep tool often works better
- C firmware indexing works well for functions, structs, and variables

### Use scripts and other local tools
- Use local tools such as rg (ripgrep) as needed
- If a local tool isn't installed, you can ask for it to be installed
- Consider writing a short Python script or shell script to help you do tasks involving a large number of items, or involving large files

---

## Environment Facts

- **`/tmp` is NOT shared with subagents.**  Use $TMPDIR (./tmp aka ~/inavflight/tmp/) for shared info



## Important: Read Your Role-Specific Guide

This file provides only a brief overview. For detailed instructions, workflows, and best practices:

- **Manager:** Read `claude/manager/README.md`
- **Developer:** Read `claude/developer/README.md`
- **Security Analyst:** Read `claude/security-analyst/README.md`

All technical details, build instructions, architecture information, coding standards, security analysis procedures, and role-specific workflows are documented in those guides.
