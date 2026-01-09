# Todo List: Investigate Boolean Struct Bitfields

## Phase 1: Struct Discovery

- [ ] Use ctags to list all struct definitions in firmware
- [ ] Identify structs with members that appear to be boolean-only
- [ ] Create list of candidate structs for investigation
- [ ] Prioritize config structs that are stored in EEPROM

## Phase 2: Field Size Analysis

- [ ] For each candidate struct:
  - [ ] Check if fields use `:1` bit field syntax
  - [ ] Check if fields use uint8_t, int, or other larger types
  - [ ] Document current field sizes and types
- [ ] Calculate current struct sizes

## Phase 3: EEPROM Storage Investigation

- [ ] Locate EEPROM storage/serialization code
- [ ] Identify how structs are written to EEPROM:
  - [ ] Direct memcpy of struct?
  - [ ] Field-by-field serialization?
  - [ ] Custom encoding?
- [ ] Find where structs are read from EEPROM
- [ ] Document the serialization method for each struct

## Phase 4: Compatibility Analysis

- [ ] For each struct, determine:
  - [ ] Would changing to `:1` change struct size?
  - [ ] Would it change field byte offsets?
  - [ ] Would it break EEPROM compatibility?
- [ ] Document current binary format (layout in memory/EEPROM)
- [ ] Document proposed binary format (if changed to `:1`)
- [ ] Identify any version migration code that exists

## Phase 5: Documentation & Recommendations

- [ ] Create comprehensive findings document
- [ ] List all boolean-only structs found
- [ ] Document current vs proposed formats
- [ ] Assess compatibility impact for each struct
- [ ] Provide clear recommendation:
  - [ ] Safe to change (no EEPROM impact)
  - [ ] Unsafe to change (breaks compatibility)
  - [ ] Requires migration code
- [ ] Send completion report to manager

## Completion

- [ ] All findings documented
- [ ] No code changes made
- [ ] No branches created
- [ ] Send completion report to manager
