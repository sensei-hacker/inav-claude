# Project: Remove Transpiler Backward Compatibility

**Status:** ⏸️ BACKBURNER
**Priority:** LOW
**Type:** Refactoring
**Created:** 2025-12-28
**Scheduled For:** February 2026
**Estimated Effort:** 4-6 hours

## Overview

Remove backward compatibility support from the transpiler namespace refactoring, requiring users to use the fully namespaced `inav.` syntax.

## Problem

The transpiler currently supports dual syntax to maintain backward compatibility:
- **New syntax:** `inav.gvar[0]`, `inav.rc[5]`, `inav.events.edge()`
- **Old syntax:** `gvar[0]`, `rc[5]`, `edge()` (without namespace)

This dual-path logic adds complexity across multiple transpiler components and should be removed after users have had sufficient time to migrate.

## Objectives

1. Remove backward compatibility support for old (non-namespaced) syntax
2. Simplify transpiler codebase by removing dual-path logic
3. Update any remaining examples or documentation to use new syntax only
4. Ensure migration path is well-documented

## Scope

**In Scope:**
- Remove backward compatibility from `parser.js`
- Remove backward compatibility from `codegen.js`
- Remove backward compatibility from `analyzer.js`
- Remove backward compatibility from `action_generator.js`
- Update any examples using old syntax
- Update documentation to reflect new-syntax-only requirement

**Out of Scope:**
- Changes to the decompiler (already outputs new syntax only)
- New transpiler features
- Changes to the runtime (firmware side)

## Implementation Steps

1. Review current backward compatibility implementation in all four files
2. Create branch from maintenance-9.x (or appropriate base at time of implementation)
3. Remove old syntax support from `parser.js`
4. Remove old syntax support from `codegen.js`
5. Remove old syntax support from `analyzer.js`
6. Remove old syntax support from `action_generator.js`
7. Run all transpiler tests to ensure nothing breaks
8. Update any examples still using old syntax
9. Update documentation
10. Create PR

## Success Criteria

- [ ] All backward compatibility code removed from parser.js
- [ ] All backward compatibility code removed from codegen.js
- [ ] All backward compatibility code removed from analyzer.js
- [ ] All backward compatibility code removed from action_generator.js
- [ ] All transpiler tests still passing
- [ ] No examples use old syntax
- [ ] Documentation updated to show new syntax only
- [ ] PR created and reviewed
- [ ] Changes merged

## Timeline

**Migration Period:** December 2024 - February 2026 (~14 months)
**Scheduled Implementation:** February 2026

## Rationale

**14-month migration period justification:**
- Gives users substantial time to update their JavaScript Programming code
- Decompiler already outputs new syntax, so saving/reloading auto-migrates
- Users who never save their code have >1 year to notice and update
- Long enough to be safe, short enough to not accumulate excessive technical debt

## Benefits of Removal

1. **Simpler codebase** - Remove dual-path logic in multiple files
2. **Clearer API** - One way to do things instead of two
3. **Better maintainability** - Less code to test and maintain
4. **Easier for new contributors** - Won't be confused by legacy syntax support
5. **Reduced cognitive load** - No need to remember/support two syntax variants

## Files to Modify

**Primary:**
- `inav-configurator/js/transpiler/transpiler/parser.js`
- `inav-configurator/js/transpiler/transpiler/codegen.js`
- `inav-configurator/js/transpiler/transpiler/analyzer.js`
- `inav-configurator/js/transpiler/transpiler/action_generator.js`

**Documentation:**
- Any files referencing backward compatibility
- Examples showing old syntax

**Reference:**
- `claude/developer/transpiler-namespace-refactoring.md` - Original implementation details

## Notes

**Branch:** Use `maintenance-9.x` or `maintenance-10.x` depending on what's current in Feb 2026

**Testing:** All existing transpiler tests should continue passing. The removal should not require new tests, just verify existing ones pass with backward compatibility removed.

**User Communication:** Consider announcing the upcoming removal in advance (e.g., January 2026) to give users final notice.

**Breaking Change:** This IS a breaking change for users still using old syntax. However:
- 14-month migration period is substantial
- Decompiler provides automatic migration path
- Change simplifies codebase long-term

## Related Work

- Original namespace refactoring: Completed December 2024
- Developer documentation: `claude/developer/transpiler-namespace-refactoring.md`
