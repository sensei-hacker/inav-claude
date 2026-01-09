# Project: Analyze Transpiler Code Structure

**Status:** TODO
**Priority:** Low
**Type:** Research / Code Organization
**Created:** 2025-12-12
**Estimated Time:** 3-5 hours

## Overview

Analyze the largest transpiler files for:
1. Files that should be split into multiple modules
2. Overly long functions that should be divided up

## Files to Analyze (by size)

| Lines | File |
|-------|------|
| 1,083 | decompiler.js |
| 954 | codegen.js |
| 664 | analyzer.js |
| 664 | parser.js |
| 623 | optimizer.js |
| 580 | condition_generator.js |
| 561 | index.js |
| 520 | action_decompiler.js |

## What to Analyze

### File-Level
1. Can any file be logically split into separate modules?
2. Are there distinct responsibilities that should be separated?
3. What are the internal dependencies?

### Function-Level
1. Identify functions over ~50-80 lines
2. Can long functions be broken into smaller, named helpers?
3. Are there repeated patterns that could be extracted?

## Deliverable

Brief report with:
- List of recommended file splits (if any)
- List of functions recommended for splitting
- Rationale for each recommendation
- Effort estimate
- Priority order for changes

## Success Criteria

- [ ] All 8 files reviewed
- [ ] Long functions identified
- [ ] Clear recommendations with rationale
- [ ] Actionable next steps

## Directory

`inav-configurator/js/transpiler/transpiler/`
