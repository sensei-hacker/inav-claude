# Project: Configurator Web/PWA Migration - CORS Research

**Status:** TODO
**Priority:** MEDIUM
**Type:** Research / Investigation
**Created:** 2025-12-01
**Assigned:** Developer

## Objective

Research the CORS policy issue affecting firmware hex file downloads in the web/PWA migration of INAV Configurator.

## Background

INAV Configurator is being migrated from Electron app to Progressive Web App (PWA). There are two relevant branches:
1. `copilot/convert-electron-app-to-web` - Electron to web conversion work
2. `Scavanger/PWA` - PWA port of Configurator

**CORS Issue:** The CORS (Cross-Origin Resource Sharing) policy is causing problems with the firmware flasher, specifically when downloading hex files (firmware assets) from the INAV repository.

## Tasks

### Phase 1: Review Migration Documentation (2-3h)

1. Checkout branch `copilot/convert-electron-app-to-web`
2. Read `./WEB_MIGRATION.md`
3. Copy `WEB_MIGRATION.md` to this project directory
4. Document key findings about web migration approach

### Phase 2: Review PWA Implementation (2-3h)

1. Checkout branch `Scavanger/PWA`
2. Examine PWA implementation
3. Identify how firmware flashing is handled
4. Document architectural differences from Electron version

### Phase 3: CORS Investigation (3-4h)

**Primary Question:** "The CORS policy is causing problems with the firmware flasher"

**Context:** The issue specifically relates to downloading hex files (firmware assets) from the INAV repository.

**Investigation Areas:**
1. How does the firmware flasher download hex files?
2. What is the origin of the requests? (configurator domain vs github.com)
3. What CORS headers are returned by the INAV repository?
4. Where exactly does the CORS error occur in the code?
5. What are the viable solutions?

**Expected Deliverables:**
- Root cause analysis of CORS issue
- Code locations where downloads occur
- CORS headers analysis
- Proposed solutions with pros/cons
- Recommendation

## Success Criteria

- [x] `WEB_MIGRATION.md` copied to project directory
- [x] Understanding of web migration approach documented
- [x] PWA implementation reviewed
- [x] CORS issue root cause identified
- [x] Solutions proposed with clear recommendation
- [x] Report submitted to manager

## Estimated Time

7-10 hours total

## Notes

**Potential Solutions to Research:**
1. CORS proxy server
2. GitHub API with proper CORS headers
3. Backend service to proxy downloads
4. GitHub Pages or CDN with CORS enabled
5. Browser extension permissions
6. Service Worker caching strategies

**Key Questions:**
- Does Electron app use different mechanism than web app?
- Can GitHub repository serve assets with CORS headers?
- Is there a GitHub API endpoint with CORS support?
- What do other web-based firmware flashers do?

## Reference Documents

- Migration docs: `./WEB_MIGRATION.md` (to be copied here)
- Branches: `copilot/convert-electron-app-to-web`, `Scavanger/PWA`
- Related: Firmware release artifacts in INAV repository

## Location

`claude/projects/configurator-web-cors-research/`
