# Transpiler Core Files Refactoring Analysis

**Date:** 2025-11-25
**Analyzed Files:** codegen.js (1,283), analyzer.js (855), decompiler.js (792), parser.js (622)
**Total Lines:** 3,552

## Executive Summary

Comprehensive analysis identified **28-39% code reduction potential** (1,000-1,400 lines) through:
- Extracting 45+ repeated patterns
- Splitting 12 massive methods (>100 lines each)
- Creating shared utility modules
- Implementing helper functions

## Per-File Analysis

### codegen.js (1,283 lines) - HIGH PRIORITY

**Reduction Potential:** 35-45% (450-600 lines)
**Complexity:** HIGH

**Key Issues:**
1. **Massive methods:**
   - `generateCondition` (213 lines) - handles all condition types
   - `generateExpression` (251 lines) - handles all expression types
   - `generateAction` (171 lines) - handles all action types

2. **Repeated patterns (15+):**
   - Argument validation (11+ occurrences) - ~150 lines extractable
   - Math method processing (6 identical blocks) - ~200 lines extractable
   - Logic condition generation (40+ occurrences) - ~100 lines extractable
   - GVAR assignment optimization (3 occurrences)
   - Arrow helper extraction pattern

**Specific Examples:**
- Lines 269-276, 313-320, 360-367, 407-414, 461-468: Identical argument validation
- Lines 1019-1132: Nearly identical Math.min/max/sin/cos/tan handlers
- Lines 183-186, 209-211, 241-244: Repeated command generation

**Recommendations:**
1. Extract `validateArguments(fnName, args, expectedCount, stmt)` → saves ~150 lines
2. Extract Math method handler with operation map → saves ~200 lines
3. Extract `pushLogicCommand(operation, operandA, operandB, activatorId)` → saves ~100 lines
4. Split `generateCondition` into 4-5 methods by condition type
5. Split `generateAction` into 4-5 methods by action type
6. Split `generateExpression` into 6-7 methods by expression type

---

### analyzer.js (855 lines) - HIGH PRIORITY

**Reduction Potential:** 30-40% (250-350 lines)
**Complexity:** MEDIUM

**Key Issues:**
1. **Massive methods:**
   - `checkPropertyAccess` (119 lines) - validates all property access
   - `isAlwaysFalse` (41 lines) + `isAlwaysTrue` (41 lines) - duplicated logic

2. **Repeated patterns (12+):**
   - Error pushing (20+ occurrences) - ~50 lines extractable
   - Property definition lookup (repeated pattern)
   - Condition type checking (4 similar switch statements)
   - GVAR index extraction and validation (4 occurrences) - ~40 lines
   - Range check warnings (3 occurrences) - ~30 lines

**Specific Examples:**
- Lines 188-192, 193-197, 379-383: Identical error pushing
- Lines 186-197, 376-390: Identical GVAR validation
- Lines 594-634, 639-679: Duplicated isAlwaysTrue/False logic

**Recommendations:**
1. Extract `addError(message, line)` and `addWarning(type, message, line)` → saves ~50 lines
2. Extract `validateGvarAccess(gvarStr, line)` → saves ~40 lines
3. Combine `isAlwaysTrue`/`isAlwaysFalse` into single method → saves ~35 lines
4. Extract condition traversal base method → saves ~60 lines
5. Split `checkPropertyAccess` into 3-4 methods by namespace
6. Extract `checkRange(value, min, max, propertyName, line)` → saves ~30 lines

---

### decompiler.js (792 lines) - MEDIUM PRIORITY

**Reduction Potential:** 25-35% (200-300 lines)
**Complexity:** MEDIUM

**Key Issues:**
1. **Massive methods:**
   - `decompileCondition` (136 lines) - handles all condition types
   - `decompileAction` (117 lines) - handles all action types

2. **Repeated patterns (10+):**
   - Pattern detection structure (5 occurrences) - ~50 lines
   - Warning push pattern (15+ occurrences) - ~15 lines
   - Operand decompilation calls (repeated pattern)
   - Override operation mapping (15+ similar cases) - ~80 lines
   - Math operation decompilation (similar structure)

**Specific Examples:**
- Lines 200-215, 218-234, 237-251, 254-266, 269-280: Similar pattern detection
- Lines 575-662: Switch cases with repeated structure for overrides
- Lines 508-527: Similar Math.sin/cos/tan handling

**Recommendations:**
1. Extract pattern detection with method map → saves ~50 lines
2. Extract override decompilation using mapping object → saves ~80 lines
3. Extract trig operation handler → saves ~30 lines
4. Split `decompileCondition` by operation category
5. Split `decompileAction` by action category
6. Extract `addWarning(message)` helper → saves ~15 lines

---

### parser.js (622 lines) - LOW-MEDIUM PRIORITY

**Reduction Potential:** 15-25% (100-150 lines)
**Complexity:** LOW-MEDIUM

**Key Issues:**
1. **Functions needing decomposition:**
   - `transformIfStatement` (69 lines)
   - `transformEventHandler` (59 lines)
   - `transformCondition` (57 lines)
   - `transformExpression` (47 lines)

2. **Repeated patterns (8+):**
   - Warning push pattern (4 occurrences) - ~15 lines
   - Expression type checking (repeated if/else chains) - ~30 lines
   - Body transformation (2 similar patterns) - ~20 lines
   - Recursive transform pattern

**Specific Examples:**
- Lines 307-312, 332-336, 360-365, 517-522: Similar warning pushing
- Lines 107-111, 137-141, 371-376: Repeated body transformation

**Recommendations:**
1. Extract `addWarning(message, loc)` → saves ~15 lines
2. Extract type checking helpers (`isLiteral`, `isIdentifier`) → saves ~30 lines
3. Extract `transformBodyBlock(node, transformer)` → saves ~20 lines
4. Consolidate `extractIdentifier` and `extractValue` → saves ~15 lines
5. Create expression type handler map → improves maintainability

---

## Cross-File Patterns

### 1. API Definition Processing (3 files)
- **codegen.js:** lines 39-74 (buildOperandMapping)
- **analyzer.js:** lines 42-88 (buildAPIStructure)
- **decompiler.js:** lines 58-98 (buildOperandMapping)

**Potential:** Extract to shared utility module → saves ~100 lines total

### 2. Condition/Expression Traversal (3 files)
- **codegen.js:** lines 525-737
- **analyzer.js:** lines 330-362, 828-851
- **parser.js:** lines 391-447

**Potential:** Create base visitor class → saves ~80 lines total

### 3. Error/Warning Collection (all files)
All files push errors/warnings with similar structures

**Potential:** Unified error handler interface → saves ~60 lines total

---

## Summary Table

| File | Lines | Patterns | Extractable | Reduction % | Complexity |
|------|-------|----------|-------------|-------------|------------|
| codegen.js | 1,283 | 15+ | 450-600 | 35-45% | HIGH |
| analyzer.js | 855 | 12+ | 250-350 | 30-40% | MEDIUM |
| decompiler.js | 792 | 10+ | 200-300 | 25-35% | MEDIUM |
| parser.js | 622 | 8+ | 100-150 | 15-25% | LOW-MEDIUM |
| **TOTAL** | **3,552** | **45+** | **1,000-1,400** | **28-39%** | **MEDIUM-HIGH** |

---

## Top 10 Refactoring Opportunities (by impact)

1. **Extract Math operation handlers** (codegen.js) → saves ~200 lines
2. **Extract argument validation** (codegen.js) → saves ~150 lines
3. **Split generateCondition** (codegen.js, 213 lines) → improve maintainability
4. **Split generateExpression** (codegen.js, 251 lines) → improve maintainability
5. **Split generateAction** (codegen.js, 171 lines) → improve maintainability
6. **Extract command generation helper** (codegen.js) → saves ~100 lines
7. **Create shared API mapping utility** (3 files) → saves ~100 lines
8. **Split checkPropertyAccess** (analyzer.js, 119 lines) → improve maintainability
9. **Extract override decompilation map** (decompiler.js) → saves ~80 lines
10. **Extract condition traversal helpers** (analyzer.js) → saves ~60 lines

---

## Next Steps

See `refactoring-plan.md` for detailed implementation strategy.
