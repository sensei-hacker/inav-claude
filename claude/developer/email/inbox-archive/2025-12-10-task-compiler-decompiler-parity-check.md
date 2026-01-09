# Task Assignment: Compiler vs Decompiler Parity Check

**Date:** 2025-12-10
**To:** Developer
**From:** Manager
**Priority:** MEDIUM
**Project:** transpiler-maintenance

## Objective

Compare the transpiler's compiler and decompiler to identify any feature mismatches - features supported by one but not the other.

## Background

During a decompilation test, we discovered that:
- The **decompiler** generates `flight.mode.poshold` for flight mode checks
- The **compiler** doesn't recognize `flight.mode.*` (missing from API definitions)

This suggests there may be other such mismatches.

## Task

1. **Review the decompiler** (`js/transpiler/transpiler/decompiler.js`):
   - What operand types does it handle?
   - What syntax does it generate for each?

2. **Review the compiler** (`js/transpiler/transpiler/codegen.js`, `condition_generator.js`, etc.):
   - What syntax does it accept?
   - What operand types can it generate?

3. **Check API definitions** (`js/transpiler/api/definitions/`):
   - Are all INAV operand types represented?
   - Do the property paths match what decompiler generates?

4. **Document mismatches** - Create a list of:
   - Features decompiler outputs that compiler doesn't accept
   - Features compiler accepts that decompiler doesn't generate
   - Missing API definitions

## Known Issues to Verify

- `flight.mode.*` - Decompiler generates, compiler rejects
- `rc[N].high/mid/low` - Should work in both, verify it does

## Deliverable

A report listing:
1. All mismatches found
2. Recommended fixes for each
3. Priority ranking (which cause real problems vs cosmetic)

Save report to: `claude/developer/transpiler-parity-report.md`
