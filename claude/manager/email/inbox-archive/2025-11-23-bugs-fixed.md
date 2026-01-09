# Critical Transpiler Bugs Fixed

**Date:** 2025-11-23  
**Status:** ✅ Complete

## Bugs Fixed

### 1. Flight API Operand Mismatches
- **Files:** `flight.js`
- **Problem:** Hardcoded operand values drifted from firmware
- **Examples:** yaw=17→40, isArmed=18→17, isFailsafe=20→24
- **Fix:** Import from auto-generated `inav_constants.js`
- **Result:** 9 bugs fixed, 25+ missing parameters added

### 2. GET_LC_VALUE Bug
- **Files:** `codegen.js`, `decompiler.js`, `api_definitions_summary.md`
- **Problem:** Used `OPERAND_TYPE.GET_LC_VALUE` (doesn't exist)
- **Fix:** Changed to `OPERAND_TYPE.LC`
- **Result:** Edge/sticky/delay/timer all work correctly

### 3. Math.abs() Not Supported
- **Files:** `parser.js`, `codegen.js`
- **Problem:** Parser converted `Math.abs(expr)` to empty string
- **Fix:** Added expression handling in parser + Math.abs() implementation in codegen
- **Result:** `Math.abs()` now transpiles to `max(x, 0-x)` logic conditions

## Files Modified
- `js/transpiler/api/definitions/flight.js`
- `js/transpiler/transpiler/codegen.js`
- `js/transpiler/transpiler/decompiler.js`
- `js/transpiler/transpiler/parser.js`
- `js/transpiler/docs/api_definitions_summary.md`

## Testing
✅ All modules load  
✅ Operand values correct  
✅ Math.abs() transpiles correctly
