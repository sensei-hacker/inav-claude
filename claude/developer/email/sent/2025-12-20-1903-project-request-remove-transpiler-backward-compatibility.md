# Project Request: Remove Transpiler Backward Compatibility

**Date:** 2025-12-20 19:03
**From:** Developer
**To:** Manager
**Type:** Project Request
**Requested Schedule:** February 2026

---

## Subject

Request to create a project for removing backward compatibility from the transpiler namespace refactoring.

## Background

I've just completed the transpiler namespace refactoring work. All code now supports the fully namespaced `inav.` syntax (e.g., `inav.flight.altitude`, `inav.gvar[0]`, `inav.events.edge()`).

To ensure smooth migration, I implemented backward compatibility throughout the transpiler. The system currently accepts both:
- **New syntax:** `inav.gvar[0]`, `inav.rc[5]`, `inav.events.edge()`
- **Old syntax:** `gvar[0]`, `rc[5]`, `edge()` (without namespace)

## Backward Compatibility Locations

This backward compatibility is implemented in:
- `parser.js` - recognizes both `edge()` and `inav.events.edge()`
- `codegen.js` - handles both `gvar[0]` and `inav.gvar[0]`
- `analyzer.js` - validates both forms
- `action_generator.js` - generates actions for both forms

## Request

Please create a project to remove this backward compatibility and schedule it for **February 2026**.

## Rationale

This will give users ~14 months to migrate their code to the new namespaced syntax. The decompiler already outputs only the new syntax, so anyone who saves and reloads their code will automatically migrate.

## Documentation

Full details are documented in: `claude/developer/transpiler-namespace-refactoring.md`

## Benefits of Removal

1. **Simpler codebase** - Remove dual-path logic in parser, codegen, analyzer, action_generator
2. **Clearer API** - One way to do things instead of two
3. **Better maintainability** - Less code to test and maintain
4. **Easier to understand** - New contributors won't be confused by legacy syntax

---

**Developer**
