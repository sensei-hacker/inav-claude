# Project: Identify Transpiler Generic Handler Opportunities

**Status:** TODO
**Priority:** Medium
**Type:** Code Analysis / Refactoring Research
**Created:** 2025-12-12
**Estimated Time:** 3-5 hours
**Depends On:** document-transpiler-ast-types

## Overview

Analyze the transpiler code to identify cases where specific handling for each subtype could be simplified by handling the supertype generically.

## Objective

Find opportunities where:
- Code has separate handling for each subclass/subtype
- A single generic handler for the supertype would be **simpler** or **more powerful**
- The change would reduce code complexity, not just combine functions

## What We're Looking For

### Good Candidates (DO report)
- Separate handlers for ">", "<", "===" that duplicate logic → combine into generic comparison handler
- Switch statements with many similar cases that could use a lookup table
- Repeated patterns across subtypes that could be abstracted
- Cases where adding a new subtype requires touching multiple places

### Not Candidates (DON'T report)
- Several short, clear functions that happen to handle related types
- Cases where subtypes genuinely need different logic
- Combining would just make one long function instead of several short ones
- Abstractions that would obscure rather than clarify

## Key Question

For each case found, ask: "Would a generic handler make this **simpler to understand and maintain**, or just **different**?"

## Deliverable

Report (`transpiler-generic-handler-opportunities.md`) containing:
- List of identified opportunities
- For each:
  - Current code location (file:line)
  - What subtypes are handled separately
  - Proposed generic approach
  - Why it would be simpler/better
  - Effort estimate

## Success Criteria

- [ ] Transpiler code reviewed with type hierarchy in mind
- [ ] Only genuine simplification opportunities identified
- [ ] Clear rationale for each recommendation
- [ ] No "combine for combining's sake" suggestions

## Input

- `transpiler-ast-types.md` (from previous task)
- `inav-configurator/js/transpiler/` source code

## Note

This task should be done AFTER document-transpiler-ast-types is complete, as that document provides the type hierarchy needed for this analysis.
