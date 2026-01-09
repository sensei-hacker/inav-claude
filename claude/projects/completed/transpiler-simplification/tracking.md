# Transpiler Simplification - Task Tracking

**Project:** Transpiler Code Simplification
**Created:** 2025-12-10
**Manager:** Manager
**Developer:** Developer

## Overview

This project tracks the 8 simplification opportunities identified in the developer's review of the transpiler codebase (~8400 lines across 14 files).

**Important:** The current code is working well. All changes must use test-driven development to avoid regressions.

---

## Implementation PR

**PR #2472:** [Transpiler: Refactor decompiler to simplify, make more robust](https://github.com/iNavFlight/inav-configurator/pull/2472)

This PR implements items 1-5 and 7 from this tracking document. Key improvements:
- Eliminates "stringify then parse" anti-patterns
- Structural LC chain analysis replaces regex string parsing
- Lookup tables replace switch/case boilerplate
- ~600 lines saved/removed

---

## Task List

### 1. Extract extractValue() Function - IN PR #2472
**Status:** ✅ IN PR #2472
**Priority:** High
**Risk:** Low
**Files:** `parser.js`, `arrow_function_helper.js`
**Lines Saved:** ~80

**Description:** Same function duplicated in two files. Bug fixes must be applied twice.

**Solution:** Extracted to shared `expression_utils.js` module.

**Implementation:** PR #2472 - `extractValue()` and `extractIdentifier()` moved to shared module

---

### 2. Declarative Operand Validation - IN PR #2472
**Status:** ✅ IN PR #2472
**Priority:** Medium
**Risk:** Low
**Files:** `codegen.js`
**Lines Saved:** Part of ~150 (lookup tables)

**Description:** gvar/rc/pid each have ~25 lines of nearly identical validation with different bounds.

**Solution:** `INDEXED_OPERAND_DEFS` lookup table replaces repetitive switch/case.

**Implementation:** PR #2472 - Declarative operand definitions

---

### 3. Switch Statement to Lookup Table - IN PR #2472
**Status:** ✅ IN PR #2472
**Priority:** Medium
**Risk:** Medium
**Files:** `condition_decompiler.js`
**Lines Saved:** Part of ~150 (lookup tables)

**Description:** 30+ case switch with many trivial template string handlers.

**Solution:** `SIMPLE_BINARY_OPS` and `SIMPLE_UNARY_OPS` lookup tables.

**Implementation:** PR #2472 - Replaces ~150 lines of switch/case boilerplate

---

### 4. handleNot() String Manipulation - IN PR #2472
**Status:** ✅ IN PR #2472
**Priority:** Low
**Risk:** High
**Files:** `condition_decompiler.js`
**Lines Saved:** 0 (but much safer)

**Description:** ~50 lines of regex-based string manipulation that's fragile and error-prone.

**Solution:** Structural LC chain analysis replaces regex string parsing.

**Implementation:** PR #2472 - Direct structural analysis on LC chain instead of "stringify then parse"

---

### 5. Centralize Latch Variable Handling - IN PR #2472
**Status:** ✅ IN PR #2472
**Priority:** Medium
**Risk:** Medium
**Files:** Multiple files
**Lines Saved:** ~20

**Description:** Latch variables handled differently in each file. Decompiler uses fragile regex.

**Solution:** Uses `variableMap.latch_variables` for structural tracking.

**Implementation:** PR #2472 - Structural latch detection replaces regex pattern matching

---

### 6. Normalize >= and <= Operators
**Status:** ⏸️ DEFERRED
**Priority:** Medium
**Risk:** Low (constants), High (general)
**Files:** `condition_generator.js`
**Estimated Lines Saved:** ~20

**Description:** `>=` compiled as `NOT(LT)` using 2 LC slots instead of 1. Pre-normalize `x >= 5` to `x > 4` for constants.

**Note:** Only works for constant comparisons, not `x >= y`. Not included in PR #2472 - consider for future optimization.

---

### 7. Dead Code Removal - IN PR #2472
**Status:** ✅ IN PR #2472
**Priority:** Low
**Risk:** Low
**Files:** `decompiler.js`
**Lines Removed:** ~370 lines

**Description:** Tree-based decompiler replaced older group-based approach.

**Removed functions:** `groupConditions()`, `decompileGroup()`, `countNestingDepth()`, `findInnermostFunctionCall()`, `simplifyNestedExpr()`, and other redundant helpers.

**Implementation:** PR #2472 - ~370 lines of dead code removed

---

### 8. Inconsistent Error Handling
**Status:** ⏸️ DEFERRED
**Priority:** Low
**Risk:** Medium
**Files:** Various
**Estimated Lines Saved:** 0 (but cleaner)

**Description:** Some places throw errors, others add to errorHandler. Inconsistent user experience.

**Solution:** Standardize on error collection pattern.

**Note:** Not included in PR #2472 - consider for future cleanup.

---

## Progress Summary

| # | Task | Status | Lines Saved |
|---|------|--------|-------------|
| 1 | Extract extractValue() | ✅ IN PR #2472 | ~80 |
| 2 | Declarative operand validation | ✅ IN PR #2472 | (part of lookup) |
| 3 | Lookup table for operations | ✅ IN PR #2472 | ~150 |
| 4 | handleNot() improvement | ✅ IN PR #2472 | 0 (safer) |
| 5 | Centralize latch handling | ✅ IN PR #2472 | ~20 |
| 6 | Normalize >= and <= | ⏸️ DEFERRED | ~20 est |
| 7 | Dead code removal | ✅ IN PR #2472 | ~370 |
| 8 | Consistent error handling | ⏸️ DEFERRED | 0 (cleaner) |

**Total:** 8 tasks
**In PR #2472:** 6
**Deferred:** 2

**Total Lines Saved in PR #2472:** ~600+ lines

---

## Notes

- **Test-Driven Development Required:** The current code is working well. All changes must have tests written FIRST.
- Work through items one at a time to minimize risk.
- Developer's full analysis: `claude/developer/transpiler-simplification-opportunities.md`

---

## Project Status: ✅ COMPLETE

**Completed:** 2025-12-11
**Implementation:** [PR #2472](https://github.com/iNavFlight/inav-configurator/pull/2472)

6 of 8 simplification items implemented in PR #2472, saving ~600+ lines of code. Remaining 2 items (normalize operators, error handling) deferred as low priority future improvements.
