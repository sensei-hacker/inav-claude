# Project: Onboard PrivacyLRS Repository

**Status:** 📋 TODO
**Priority:** Medium
**Type:** Infrastructure / Role Setup
**Created:** 2025-11-30
**Estimated Time:** 3-4 hours

## Overview

Onboard the PrivacyLRS repository into the Claude Code workflow system and establish a new Security Analyst / Cryptographer role to work with it.

## Problem

The PrivacyLRS repository is currently not integrated into the Claude Code workflow. We need to:
1. Set up proper role-based access and workflows for security-focused work
2. Create specialized documentation for cryptographic and security analysis tasks
3. Integrate PrivacyLRS alongside inav/, inav-configurator/, and uNAVlib/

## Objectives

1. Create Security Analyst / Cryptographer role with dedicated workspace
2. Document role responsibilities, workflows, and best practices
3. Update main CLAUDE.md to include the new role
4. Establish email communication system for the security analyst
5. Create project tracking infrastructure for security-focused work

## Scope

**In Scope:**
- Create `claude/security-analyst/` directory structure
- Write comprehensive README.md for security analyst role
- Create CLAUDE.md for role-specific instructions
- Set up email folders (inbox/, sent/, inbox-archive/, outbox/)
- Update main CLAUDE.md with role selection instructions
- Update .gitignore if needed to exclude PrivacyLRS contents
- Document PrivacyLRS repository in main README

**Out of Scope:**
- Actual security analysis or cryptographic work (that's for the security analyst)
- Modifying PrivacyLRS code
- Setting up build/test infrastructure for PrivacyLRS
- Creating specific security analysis tasks (handled after role is established)

## Implementation Steps

1. **Create role directory structure**
   - `claude/security-analyst/`
   - `claude/security-analyst/inbox/`
   - `claude/security-analyst/sent/`
   - `claude/security-analyst/inbox-archive/`
   - `claude/security-analyst/outbox/`

2. **Write security analyst documentation**
   - `claude/security-analyst/README.md` - Complete role guide
   - `claude/security-analyst/CLAUDE.md` - Role-specific Claude instructions

3. **Update main CLAUDE.md**
   - Add security analyst to role selection prompt
   - Add quick reference section for security analyst

4. **Update repository documentation**
   - Update main README.md to mention PrivacyLRS
   - Update .gitignore to handle PrivacyLRS/ directory

5. **Update project tracking**
   - Add this project to INDEX.md
   - Set up project tracking workflow for security analyst

## Success Criteria

- [ ] Security analyst role directory exists with complete structure
- [ ] README.md documents all security analyst responsibilities and workflows
- [ ] CLAUDE.md provides clear role instructions
- [ ] Main CLAUDE.md includes security analyst in role selection
- [ ] Email folders created for security analyst communication
- [ ] INDEX.md updated with this project
- [ ] All changes committed to git

## Estimated Time

3-4 hours

## Priority Justification

Medium priority - This enables security-focused work on PrivacyLRS but is not blocking other active development tasks. Should be completed to establish proper workflow infrastructure before assigning security analysis tasks.

## Notes

**Security Analyst Responsibilities:**
- Cryptographic protocol review and analysis
- Security vulnerability assessment
- Code review for security issues
- Threat modeling and risk assessment
- Security best practices documentation
- Secure coding guidance

**PrivacyLRS Context:**
The PrivacyLRS repository appears to be a privacy-focused project related to LRS (Long Range Systems), likely involving wireless communication protocols that require careful security analysis.
