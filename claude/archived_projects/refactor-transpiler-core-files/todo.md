# TODO: Refactor Transpiler Core Files

**Created:** 2025-11-24
**Status:** Not yet assigned

---

## Phase 1: Analyze codegen.js (1,261 lines)

- [ ] Read entire file to understand structure
- [ ] Identify all methods in INAVCodeGenerator class
- [ ] List methods longer than 12 lines
- [ ] Find repeated code patterns:
  - [ ] Similar switch/case structures
  - [ ] Repeated AST node handling
  - [ ] Repeated operand lookups
  - [ ] Repeated command generation
  - [ ] Repeated error handling
- [ ] Calculate duplication percentage
- [ ] Estimate size reduction from function extraction
- [ ] Identify potential module boundaries
- [ ] Document findings

**Deliverable:** codegen.js analysis section

---

## Phase 2: Analyze analyzer.js (822 lines)

- [ ] Read entire file to understand structure
- [ ] Identify all methods/functions
- [ ] List functions longer than 12 lines
- [ ] Find repeated code patterns:
  - [ ] Similar AST traversal patterns
  - [ ] Repeated validation logic
  - [ ] Repeated error checks
  - [ ] Similar analysis for different node types
- [ ] Calculate duplication percentage
- [ ] Estimate size reduction from function extraction
- [ ] Identify potential module boundaries
- [ ] Document findings

**Deliverable:** analyzer.js analysis section

---

## Phase 3: Analyze decompiler.js (792 lines)

- [ ] Read entire file to understand structure
- [ ] Identify all methods/functions
- [ ] List functions longer than 12 lines
- [ ] Find repeated code patterns:
  - [ ] Repeated CLI parsing
  - [ ] Repeated AST construction
  - [ ] Similar logic for different commands
- [ ] Calculate duplication percentage
- [ ] Estimate size reduction from function extraction
- [ ] Identify potential module boundaries
- [ ] Document findings

**Deliverable:** decompiler.js analysis section

---

## Phase 4: Analyze parser.js (622 lines)

- [ ] Read entire file to understand structure
- [ ] Identify all methods/functions
- [ ] List functions longer than 12 lines
- [ ] Find repeated code patterns:
  - [ ] Repeated parsing patterns
  - [ ] Similar validation logic
- [ ] Calculate duplication percentage
- [ ] Estimate size reduction from function extraction
- [ ] Identify potential module boundaries
- [ ] Document findings

**Deliverable:** parser.js analysis section

---

## Phase 5: Create Analysis Report

- [ ] Compile all findings into `analysis-report.md`
- [ ] For each file, document:
  - [ ] Current size and structure
  - [ ] Repeated patterns found
  - [ ] Duplication percentage
  - [ ] Potential size reduction
  - [ ] Recommended approach (extract functions / split modules / both)
- [ ] Prioritize refactoring efforts
- [ ] Create summary table

**Deliverable:** `analysis-report.md`

---

## Phase 6: Create Refactoring Plan

- [ ] For each file requiring refactoring:
  - [ ] List functions to extract
  - [ ] Define helper modules to create (if applicable)
  - [ ] Specify module boundaries
  - [ ] Document expected size reduction
- [ ] Define implementation order
- [ ] Identify shared utilities across files
- [ ] Plan testing strategy

**Deliverable:** `refactoring-plan.md`

---

## Phase 7: Implement codegen.js Refactoring

- [ ] Create helper functions for repeated patterns
- [ ] Extract long methods into smaller functions
- [ ] Create helper modules if needed
- [ ] Update imports/exports
- [ ] Verify file size reduction
- [ ] Run transpiler tests
- [ ] Fix any issues
- [ ] Commit changes

**Deliverable:** Refactored codegen.js

---

## Phase 8: Implement analyzer.js Refactoring

- [ ] Create helper functions for repeated patterns
- [ ] Extract long methods into smaller functions
- [ ] Create helper modules if needed
- [ ] Update imports/exports
- [ ] Verify file size reduction
- [ ] Run transpiler tests
- [ ] Fix any issues
- [ ] Commit changes

**Deliverable:** Refactored analyzer.js

---

## Phase 9: Implement decompiler.js Refactoring

- [ ] Create helper functions for repeated patterns
- [ ] Extract long methods into smaller functions
- [ ] Create helper modules if needed
- [ ] Update imports/exports
- [ ] Verify file size reduction
- [ ] Run transpiler tests
- [ ] Fix any issues
- [ ] Commit changes

**Deliverable:** Refactored decompiler.js

---

## Phase 10: Implement parser.js Refactoring

- [ ] Create helper functions for repeated patterns
- [ ] Extract long methods into smaller functions
- [ ] Create helper modules if needed (if necessary)
- [ ] Update imports/exports
- [ ] Verify file size reduction
- [ ] Run transpiler tests
- [ ] Fix any issues
- [ ] Commit changes

**Deliverable:** Refactored parser.js

---

## Phase 11: Final Testing

- [ ] Run complete transpiler test suite
- [ ] Verify all tests pass (100%)
- [ ] Test with real-world examples
- [ ] Test edge cases
- [ ] Verify no performance regressions
- [ ] Test error handling
- [ ] Document any issues found and resolved

**Deliverable:** Testing report

---

## Phase 12: Documentation and Completion

- [ ] Update code comments if needed
- [ ] Document architectural changes
- [ ] Create summary of changes:
  - [ ] Before/after line counts
  - [ ] Functions extracted
  - [ ] Modules created
  - [ ] Size reduction achieved
- [ ] Send completion report to manager inbox
- [ ] Include lessons learned

**Deliverable:** Completion report

---

## Reference: Current File Sizes

```
1,261 lines - codegen.js (PRIORITY HIGH)
  822 lines - analyzer.js (PRIORITY HIGH)
  792 lines - decompiler.js (PRIORITY MEDIUM)
  622 lines - parser.js (PRIORITY MEDIUM)
------
3,497 lines - Total
```

**Target reduction:** ≥20% per file where applicable

---

## Implementation Guidelines

### When Analyzing

- Look for code blocks that appear 3+ times
- Identify functions longer than 12 lines
- Note logical groupings that could be modules
- Calculate duplication percentage

### When Extracting Functions

- Name functions descriptively
- Keep functions focused (single responsibility)
- Target <12 lines per function
- Extract to helper modules if used across files

### When Creating Modules

- Ensure module has cohesive purpose
- Follow existing module patterns
- Update imports/exports properly
- Test thoroughly after creation

### When Testing

- Run full test suite after each file
- Test edge cases
- Verify no functional changes
- Check for performance impact

---

## Notes

- Work on one file at a time
- Test and commit after each file
- If file is already well-structured, document why and skip refactoring
- Don't over-engineer - focus on real problems
- Preserve all existing functionality
