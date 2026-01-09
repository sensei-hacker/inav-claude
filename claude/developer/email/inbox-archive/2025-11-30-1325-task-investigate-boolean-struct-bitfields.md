# Task Assignment: Investigate Boolean Struct Bitfields

**Date:** 2025-11-30 13:25
**Project:** investigate-boolean-struct-bitfields
**Priority:** Medium
**Estimated Effort:** 3-5 hours
**Branch:** None (research only - do NOT create branches)

## Task

Investigate structs in the INAV firmware that contain members used only as boolean (true/false) conditions. Determine whether these fields currently use bit fields (`:1`) or larger data types, and analyze whether converting them to single-bit fields would change the EEPROM binary storage format.

**IMPORTANT:** This is a research-only task. Do NOT modify any code or create any branches until the information is fully documented.

## Background

Structs with boolean-only members may be wasting memory if they're not using bit fields. However, we need to understand the EEPROM storage implications before making any changes, as altering the binary format would break compatibility with existing saved settings.

## What to Do

### 1. Find Boolean-Only Structs

- Use ctags to search for struct definitions in the firmware
- Identify structs where all members appear to be used only as true/false conditions
- Focus on config structs that are stored in EEPROM
- Create a list of candidate structs

**Tip:** The ctags index at `/home/raymorris/Documents/planes/inavflight/inav/tags` can help you quickly find struct definitions.

### 2. Analyze Current Field Definitions

For each candidate struct, examine the field declarations:
- Are fields defined with `:1` bit field syntax? (e.g., `uint8_t enabled:1;`)
- Are fields using full types? (e.g., `uint8_t enabled;` or `bool enabled;`)
- Document the current field sizes

### 3. Investigate EEPROM Storage

Find out how these structs are stored in EEPROM:
- Look at `src/main/config/config_streamer.c` and related files
- Determine the serialization method:
  - Direct memcpy of the struct?
  - Field-by-field serialization?
  - Custom encoding via settings.yaml?
- Understand how the data is read back from EEPROM

### 4. Assess Binary Format Impact

For each struct, determine:
- Would changing fields to `:1` change the struct size?
- Would it change field byte offsets within the struct?
- Would it change the binary format written to EEPROM?
- Would existing saved settings become incompatible?

### 5. Document Everything

Create a comprehensive findings document that includes:
- List of all boolean-only structs found
- Current field definitions (with `:1` or without)
- Current struct sizes
- EEPROM storage mechanism for each struct
- Binary format compatibility analysis
- Clear recommendation on whether changes are safe

## Success Criteria

- [ ] All structs with boolean-only members identified
- [ ] Current field sizes documented (`:1` vs full types)
- [ ] EEPROM storage mechanism understood and documented
- [ ] Binary format compatibility impact clearly explained
- [ ] Recommendation provided (safe/unsafe/requires migration)
- [ ] **NO code changes made**
- [ ] **NO branches created**

## Files to Check

Start with these areas:
- `src/main/navigation/` - Navigation config structs
- `src/main/fc/` - Flight controller config structs
- `src/main/config/config_streamer.c` - EEPROM serialization
- `src/main/fc/settings.yaml` - Settings definitions
- Use grep to find structs with multiple boolean-looking fields

## Examples to Look For

Structs like this (hypothetical example):
```c
typedef struct {
    uint8_t enableFeature1;  // Used as: if (config.enableFeature1) ...
    uint8_t enableFeature2;  // Used as: if (config.enableFeature2) ...
    uint8_t isActive;        // Used as: if (config.isActive) ...
} exampleConfig_t;
```

Could potentially be:
```c
typedef struct {
    uint8_t enableFeature1:1;
    uint8_t enableFeature2:1;
    uint8_t isActive:1;
} exampleConfig_t;
```

But only if it doesn't break EEPROM compatibility!

## Notes

- **DO NOT CHANGE CODE:** This is research only
- **DO NOT CREATE BRANCHES:** No implementation yet
- Focus on config structs that persist to EEPROM
- Consider padding and alignment issues with bit fields
- Document thoroughly - this will inform whether we proceed

## Output

Send a completion report to manager/inbox/ when done with:
1. List of candidate structs
2. Analysis of current vs proposed formats
3. EEPROM compatibility assessment
4. Recommendation on next steps

---
**Manager**
