# Proposal: Blackbox.c Refactoring Project

**From:** Developer
**To:** Manager
**Date:** 2025-12-31
**Subject:** Backburner Project Proposal - Refactor blackbox.c for Maintainability
**Priority:** Low (Backburner)

---

## Context

While updating the blackbox CLAUDE.md documentation with current line numbers, I identified opportunities to improve the maintainability of `inav/src/main/blackbox/blackbox.c`.

---

## Current State

**File Size:** 2,344 lines (well above the 500-line guideline)

**Large Data Blocks (267 lines, 11% of file):**
- `blackboxMainFields[]` (lines 205-398): 194 lines - Main flight data field definitions
- `blackboxGpsGFields[]` (lines 402-417): 16 lines - GPS position/velocity fields
- `blackboxGpsHFields[]` (lines 420-423): 4 lines - GPS home fields
- `blackboxSlowFields[]` (lines 427-471): 45 lines - Slow data fields

---

## Immediate Quick Win: Extract Field Definitions to Header

### What
Move the four field definition arrays from blackbox.c to `blackbox_fielddefs.h`

### Why
1. **Separation of concerns**: Field definitions are data declarations, not implementation logic
2. **Precedent exists**: `blackbox_fielddefs.h` already exists for field-related types/enums
3. **Immediate benefit**: Reduces blackbox.c by 267 lines (~11%)
4. **Zero runtime impact**: These are `const` arrays

### Changes Required
**blackbox_fielddefs.h** - Add extern declarations:
```c
extern const blackboxDeltaFieldDefinition_t blackboxMainFields[];
extern const blackboxConditionalFieldDefinition_t blackboxGpsGFields[];
extern const blackboxSimpleFieldDefinition_t blackboxGpsHFields[];
extern const blackboxSimpleFieldDefinition_t blackboxSlowFields[];
```

**blackbox.c** - Remove `static` keyword from arrays (4 one-word changes)

**Verification needed:**
- Ensure no other .c files reference these arrays (grep confirms only blackbox.c uses them)
- Build test to confirm no linker issues

---

## Larger Backburner Project: Split blackbox.c into Logical Files

### Goal
Split the 2,344-line blackbox.c into files ≤500 lines each, following single-responsibility principle.

### Proposed File Structure

**blackbox_encoding.c** (~400 lines)
- `writeIntraframe()` (852-1055)
- `writeInterframe()` (1085-1311)
- `blackboxWriteArrayUsingAveragePredictor16/32()` (1057-1083)
- Frame encoding logic

**blackbox_gps.c** (~100 lines)
- `writeGPSFrame()` (1594-1628)
- `writeGPSHomeFrame()` (1582-1592)
- GPS-specific logging

**blackbox_slow.c** (~150 lines)
- `writeSlowFrame()` (1313-1441)
- `writeSlowFrameIfNeeded()`
- Slow data logging

**blackbox_state.c** (~150 lines)
- `loadMainState()` (1630-1769)
- State population logic

**blackbox_header.c** (~200 lines)
- `sendFieldDefinition()` (1770-1867)
- Header generation state machine
- Header-related functions

**blackbox.c** (~500 lines)
- Core blackbox state management
- Device I/O coordination
- Public API functions
- Include coordination logic

**blackbox_fielddefs.c** (~270 lines)
- Field definition arrays (moved from blackbox.c)
- Field metadata

### Benefits
1. **Easier navigation**: Find specific functionality quickly
2. **Reduced cognitive load**: Each file has one clear purpose
3. **Better testability**: Smaller units easier to unit test
4. **Parallel development**: Multiple developers can work on different aspects
5. **Follows project guidelines**: 500-line file size recommendation

### Risks
1. **Build system changes**: May need CMakeLists.txt updates
2. **Header dependencies**: Need careful management of includes
3. **Testing burden**: Must verify no functional changes
4. **Time investment**: 2-4 hours estimated for careful refactoring

---

## Recommendation

**Phase 1 (Quick Win):** Extract field arrays to header - Low risk, immediate benefit
**Phase 2 (Backburner):** Full file split - Schedule when time permits, not urgent

Both changes maintain identical functionality while improving code organization and maintainability.

---

## Request

Please create a backburner project for this refactoring work. I can tackle Phase 1 quickly if approved, and Phase 2 when higher-priority work allows.

Would you like me to proceed with Phase 1 (field array extraction), or should both phases wait for formal project planning?

---

**Developer**
