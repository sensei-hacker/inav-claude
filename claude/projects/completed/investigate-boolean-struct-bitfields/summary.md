# Project: Investigate Boolean Struct Bitfields

**Status:** 📋 TODO
**Priority:** Medium
**Type:** Research / Memory Optimization
**Created:** 2025-11-30
**Estimated Time:** 3-5 hours

## Overview

Investigate structs in the INAV firmware that contain members used only as boolean (true/false) conditions. Determine if these fields are currently using bit fields (`:1`) or larger data types, and analyze the impact of converting them to single-bit fields on EEPROM storage format.

## Problem

Structs with boolean-only members may be wasting memory if they're not using bit fields. However, changing to bit fields could potentially change the binary format in EEPROM, which would break compatibility with existing saved settings.

## Objectives

1. **Identify boolean-only structs:** Find structs where all members are used only as true/false conditions
2. **Analyze current field sizes:** Check if fields use `:1` bit fields or larger types (uint8_t, int, etc.)
3. **Understand EEPROM storage:** Determine how these structs are serialized to EEPROM
4. **Assess compatibility impact:** Document whether changing to `:1` would alter the EEPROM binary format
5. **Document findings:** Create detailed report before making any code changes

## Scope

**In Scope:**
- Search for structs with boolean-only members
- Use ctags to identify struct definitions
- Analyze field declarations (`:1` vs full types)
- Trace EEPROM storage/serialization code
- Document current vs proposed binary formats
- Assess backward compatibility concerns

**Out of Scope:**
- Making code changes (documentation only at this stage)
- Creating branches
- Modifying struct definitions
- Testing EEPROM changes

## Implementation Steps

1. Use ctags to find struct definitions in the firmware
2. Identify structs where all members are used as booleans
3. For each candidate struct:
   - Check if fields use `:1` bit fields or larger types
   - Find where the struct is stored in EEPROM
   - Determine serialization method (direct memcpy vs field-by-field)
4. Analyze EEPROM format compatibility:
   - Would `:1` change the struct size?
   - Would it change field offsets?
   - How would it affect saved settings?
5. Document all findings before proposing changes

## Success Criteria

- [ ] List of structs with boolean-only members identified
- [ ] Current field sizes documented (`:1` vs full types)
- [ ] EEPROM storage mechanism understood
- [ ] Binary format compatibility impact documented
- [ ] Clear recommendation on whether to proceed with changes
- [ ] No code changes or branches created (research only)

## Key Files to Check

- Firmware struct definitions (look for config structs)
- EEPROM storage code: `src/main/config/config_streamer.c`
- Settings definitions: `src/main/fc/settings.yaml`
- Navigation config: `src/main/navigation/`
- Flight controller config: `src/main/fc/`

## Notes

- **IMPORTANT:** This is a research task only - do not modify code or create branches
- Use ctags index for efficient struct lookup
- Focus on config structs that are persisted to EEPROM
- Consider both RAM savings and EEPROM compatibility
- Document everything thoroughly before proposing changes

## Priority Justification

Medium priority:
- Potential memory optimization opportunity
- Research-only task, low risk
- Could lead to RAM savings in resource-constrained firmware
- Important to understand EEPROM compatibility before changes
