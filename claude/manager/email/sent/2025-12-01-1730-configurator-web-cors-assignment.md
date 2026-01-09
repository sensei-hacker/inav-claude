# Assignment: Configurator Web/PWA Migration - CORS Research

**Date:** 2025-12-01 17:30
**To:** Developer
**From:** Manager
**Subject:** New Assignment - Research CORS Issue in Web/PWA Configurator Migration
**Priority:** MEDIUM
**Project:** configurator-web-cors-research

---

## Assignment Overview

You are assigned to research the CORS (Cross-Origin Resource Sharing) policy issue affecting firmware downloads in the INAV Configurator web/PWA migration.

**Project Location:** `claude/projects/configurator-web-cors-research/`

---

## Background

INAV Configurator is being migrated from an Electron desktop application to a Progressive Web App (PWA). This migration enables the configurator to run in web browsers without requiring installation.

**Key Branches:**
1. `copilot/convert-electron-app-to-web` - Contains web migration documentation
2. `Scavanger/PWA` - PWA port implementation

**The Problem:** The CORS policy is causing problems with the firmware flasher, specifically when downloading hex files (firmware assets) from the INAV repository.

---

## Tasks

### Phase 1: Review Migration Documentation

1. **Checkout branch:** `copilot/convert-electron-app-to-web`
2. **Read:** `./WEB_MIGRATION.md` in the inav-configurator directory
3. **Copy:** `WEB_MIGRATION.md` to `claude/projects/configurator-web-cors-research/`
4. **Document:** Key findings about the web migration approach

### Phase 2: Review PWA Implementation

1. **Checkout branch:** `Scavanger/PWA`
2. **Examine:** PWA implementation, especially firmware flashing code
3. **Identify:** How firmware flashing differs from Electron version
4. **Document:** Architectural changes and approach

### Phase 3: CORS Investigation

**Research Question:** "The CORS policy is causing problems with the firmware flasher"

**Specific Context:** The issue relates to downloading hex files (firmware assets) from the INAV repository.

**Investigate:**
1. How does the firmware flasher download hex files?
2. What is the request origin? (configurator domain vs github.com)
3. What CORS headers does the INAV repository return?
4. Where in the code does the CORS error occur?
5. What are viable solutions?

**Expected Analysis:**
- Root cause of CORS failure
- Code locations involved in downloads
- CORS headers from INAV repository
- Comparison: Electron approach vs web approach
- Why Electron works but web/PWA doesn't

**Proposed Solutions:**
Research and evaluate these approaches:
1. CORS proxy server
2. GitHub API endpoints (may have different CORS policies)
3. Backend service to proxy firmware downloads
4. CDN or GitHub Pages with CORS headers
5. Browser extension with additional permissions
6. Service Worker caching strategies

For each solution, provide:
- How it works
- Pros and cons
- Implementation complexity
- Security implications
- Recommendation (yes/no and why)

---

## Deliverables

**Submit to Manager:**

1. **WEB_MIGRATION.md** - Copied to project directory
2. **Migration Analysis** - Summary of web migration approach
3. **PWA Review** - Findings from Scavanger/PWA branch
4. **CORS Root Cause** - Detailed explanation of why CORS is failing
5. **Code Locations** - Where downloads happen, where errors occur
6. **Solutions Analysis** - Evaluation of each potential solution
7. **Recommendation** - Your recommended approach with justification

**Report Format:** Email to manager with:
- Executive summary (2-3 paragraphs)
- Detailed findings (root cause, code analysis)
- Solutions comparison table
- Final recommendation
- Next steps

---

## Success Criteria

- Understanding of web migration documented
- PWA implementation reviewed
- CORS issue root cause identified with evidence
- Multiple solutions evaluated objectively
- Clear recommendation with justification
- All findings documented in project directory

---

## Estimated Time

**Total:** 7-10 hours

- Phase 1 (migration docs): 2-3h
- Phase 2 (PWA review): 2-3h
- Phase 3 (CORS research): 3-4h

---

## Research Hints

**Key Questions:**
- Does the Electron app use Node.js APIs unavailable in browsers?
- Can GitHub serve repository assets with CORS headers?
- Is there a GitHub API endpoint that supports CORS?
- What do other web-based firmware flashers use (Betaflight Configurator, etc.)?

**Electron vs Web:**
- Electron has no same-origin policy restrictions
- Web browsers enforce CORS for cross-origin requests
- This is likely why it works in Electron but not web

**Potential GitHub Endpoints:**
- Raw content: `https://raw.githubusercontent.com/...`
- Releases API: `https://api.github.com/repos/.../releases`
- Release assets: Different CORS policies than raw content

---

## Notes

**This is a research task, not an implementation task.** Your goal is to understand the problem and propose solutions, not to implement the fix.

**Be thorough.** This CORS issue is likely a blocker for the web/PWA migration, so a comprehensive analysis will help stakeholders make the right decision.

**Document as you go.** Save your findings in the project directory so the analysis is preserved.

---

## Communication

- **Questions/Blockers:** Email manager immediately
- **Progress Update:** Send update after Phase 1 and Phase 2 completion
- **Completion Report:** Full report when research is complete

---

**Good luck with the research!**

---

**Development Manager**
2025-12-01 17:30
