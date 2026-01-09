# ⚠️⚠️⚠️ CLAUDE: READ THIS FIRST ⚠️⚠️⚠️

## MANDATORY FIRST ACTION - NO EXCEPTIONS

**STOP! Before responding to the user or doing ANY other task:**

**👉 Ask the user RIGHT NOW:**
**"Which role should I take on today - Manager, Developer, Release Manager, or Security Analyst?"**

**Then:**
1. Wait for their response
2. Switch to `claude/manager/`, `claude/developer/`, `claude/release-manager/`, or `claude/security-analyst/`
3. Read the role-specific README.md file in that directory
4. ONLY AFTER reading the README, proceed with other tasks

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

This repository contains four main components:

1. **inav/** - Flight controller firmware (C/C99, embedded systems)
2. **inav-configurator/** - Desktop configuration GUI (JavaScript/Electron)
3. **inavwiki/** - Documentation wiki (Markdown)
4. **PrivacyLRS/** - Privacy-focused Long Range System (security analysis focus)

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

## Important: Read Your Role-Specific Guide

This file provides only a brief overview. For detailed instructions, workflows, and best practices:

- **Manager:** Read `claude/manager/README.md`
- **Developer:** Read `claude/developer/README.md`
- **Security Analyst:** Read `claude/security-analyst/README.md`

All technical details, build instructions, architecture information, coding standards, security analysis procedures, and role-specific workflows are documented in those guides.
