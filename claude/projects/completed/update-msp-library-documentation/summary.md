# Project: Update MSP Library Documentation to mspapi2

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Documentation Update
**Created:** 2025-12-18
**Estimated Time:** 2-3 hours

## Overview

Update internal documentation and skills to reference **mspapi2** instead of **uNAVlib** for MSP communication. The author of uNAVlib recommends using their newer library, mspapi2, which is better.

## Problem

**Current state:**
- Internal documentation references uNAVlib for MSP communication
- Skills reference uNAVlib
- CLAUDE.md files mention uNAVlib

**What needs to change:**
- Primary recommendation should be mspapi2
- Preserve mention of uNAVlib as older alternative
- Update all skills that reference uNAVlib
- Update developer and manager CLAUDE.md files

## Objectives

1. Update documentation to recommend mspapi2 as the primary MSP library
2. Preserve references to uNAVlib as "older alternative" for backward compatibility
3. Update all skills that mention uNAVlib
4. Update CLAUDE.md files in claude/developer and claude/manager
5. Provide installation instructions for mspapi2
6. Note that PRs can be submitted to mspapi2 if improvements are needed

## Scope

**Files to Update (12 references found):**

**CLAUDE.md files:**
- `claude/developer/CLAUDE.md` - Line 44
- `claude/manager/CLAUDE.md` - Line 42

**Skills (3 skills):**
- `.claude/skills/msp-protocol/SKILL.md`
- `.claude/skills/sitl-arm/SKILL.md`
- `.claude/skills/test-crsf-sitl/SKILL.md`

**Developer Documentation:**
- `claude/developer/crsf-telemetry-msp-config-guide.md`
- Any other MSP-related guides that reference uNAVlib

**Pattern Updates:**
- Ensure MSP async patterns still apply to mspapi2

## Implementation Steps

1. Research mspapi2
   - GitHub repository location
   - Installation instructions
   - API differences from uNAVlib
   - Basic usage examples
2. Update CLAUDE.md files
   - Change primary recommendation to mspapi2
   - Note uNAVlib as older alternative
3. Update skills
   - msp-protocol: Update library recommendation
   - sitl-arm: Update MSP communication examples
   - test-crsf-sitl: Update CRSF telemetry configuration
4. Update developer documentation
   - CRSF telemetry MSP config guide
   - Any test scripts that import uNAVlib
5. Test references
   - Ensure all imports/examples use correct library name
   - Verify installation instructions are accurate

## Success Criteria

- [ ] All CLAUDE.md files reference mspapi2 as primary library
- [ ] All 3 skills updated with mspapi2 references
- [ ] uNAVlib preserved as "older alternative" where appropriate
- [ ] Installation instructions for mspapi2 provided
- [ ] Note added that PRs can be submitted to mspapi2 for improvements
- [ ] Developer documentation updated
- [ ] No broken references to old library

## Estimated Time

2-3 hours:
- Research mspapi2: 30 minutes
- Update CLAUDE.md files: 15 minutes
- Update 3 skills: 45-60 minutes
- Update developer docs: 30-45 minutes
- Review and test: 15-30 minutes

## Priority Justification

MEDIUM priority - Important for keeping documentation current and recommending best tools, but doesn't block active development work.

## Notes

**Important:**
- Preserve backward compatibility references to uNAVlib
- Don't delete uNAVlib mentions entirely - some projects may still use it
- Note that mspapi2 accepts PRs for improvements/additions
- Ensure API differences are documented if significant

**Library Information:**
- **mspapi2** - Newer, recommended MSP library by same author
- **uNAVlib** - Older MSP library, still functional but superseded by mspapi2
