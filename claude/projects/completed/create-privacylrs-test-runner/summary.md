# Project: Create PrivacyLRS Test Runner Skill

**Status:** 📋 TODO
**Priority:** Medium
**Type:** Testing Infrastructure / Skill Development
**Created:** 2025-11-30
**Assigned:** Security Analyst
**Estimated Time:** 4-6 hours

## Overview

Explore the PrivacyLRS testing infrastructure, learn how to run tests, and create a reusable test runner skill for automated testing workflows.

## Problem

To effectively perform security analysis and verify security fixes, we need to:
- Understand the test infrastructure
- Know how to run tests to verify functionality
- Have an automated way to run tests during security work
- Ensure security patches don't break existing functionality

Currently, we don't have documented procedures for running PrivacyLRS tests or a convenient skill for test execution.

## Objectives

1. Map the PrivacyLRS testing infrastructure
2. Document how to run tests (all tests, specific tests, with coverage, etc.)
3. Actually execute tests to verify understanding
4. Create a reusable `.claude/skills/privacylrs-test-runner.md` skill
5. Provide clear documentation for future testing needs

## Scope

**In Scope:**
- Exploring `PrivacyLRS/src/test/` and all test directories
- Identifying test frameworks and tools used
- Learning test execution commands
- Running tests to verify they work
- Creating detailed working notes
- Creating test runner skill file
- Testing the skill to ensure it works

**Out of Scope:**
- Writing new tests
- Fixing failing tests (just document them)
- Security analysis of test code (that's a separate task)
- Modifying test infrastructure
- Performance optimization of tests

## Implementation Steps

### Phase 1: Discovery (2-3 hours)
1. Explore `PrivacyLRS/src/test/` directory
2. Find all test files in codebase
3. Identify test framework(s) (pytest, unittest, etc.)
4. Locate test configuration files
5. Find test documentation
6. Check CI/CD configs for test commands

### Phase 2: Execution (1-2 hours)
1. Identify test commands from configs/docs
2. Try running all tests
3. Try running specific test files
4. Try different test options (verbose, coverage, etc.)
5. Document prerequisites and dependencies
6. Note any errors or issues

### Phase 3: Documentation (1-2 hours)
1. Create detailed working notes
2. Document test infrastructure overview
3. Write step-by-step test execution guide
4. List common commands and options

### Phase 4: Skill Creation (1 hour)
1. Design skill based on common use cases
2. Write `.claude/skills/privacylrs-test-runner.md`
3. Test the skill by using it
4. Refine based on testing
5. Send completion report to manager

## Success Criteria

- [ ] All test directories and files identified
- [ ] Test framework(s) documented
- [ ] Successfully run at least one test suite
- [ ] Working notes created with:
  - Test infrastructure overview
  - Step-by-step execution guide
  - Prerequisites and dependencies
  - Common commands and troubleshooting
- [ ] Test runner skill created and working
- [ ] Skill tested and verified
- [ ] Completion report sent to manager

## Estimated Time

4-6 hours

## Priority Justification

Medium priority - Important for supporting security analysis work but not blocking current analysis tasks. Having test infrastructure in place will be valuable for verifying security fixes and ensuring patches don't break functionality.

## Notes

**Deliverables:**
1. Working notes (personal documentation)
2. `.claude/skills/privacylrs-test-runner.md` skill file
3. Completion report to manager

**Questions to Answer:**
- What test framework(s) are used?
- How many test files/tests exist?
- Do all tests currently pass?
- What are the test dependencies?
- How long does the full suite take?
- Are there different test categories?
- Is coverage reporting available?

**Reference Examples:**
Look at existing skills for format:
- `.claude/skills/build-sitl.md`
- `.claude/skills/sitl-arm.md`
