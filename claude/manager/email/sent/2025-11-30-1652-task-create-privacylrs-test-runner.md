# Task Assignment: Create PrivacyLRS Test Runner Skill

**Date:** 2025-11-30 16:52
**Project:** PrivacyLRS Test Infrastructure & Skill Creation
**Priority:** Medium
**Estimated Effort:** 4-6 hours
**Branch:** N/A (exploration and skill creation)

---

## Task

Explore the PrivacyLRS testing infrastructure, learn how to run tests, and create a reusable test runner skill for automated testing workflows.

## Background

Understanding and being able to run tests is critical for:
- Verifying security fixes don't break functionality
- Regression testing after security patches
- Validating cryptographic implementations
- Ensuring code quality during security reviews

## What to Do

### Phase 1: Discover Testing Infrastructure

1. **Read testing code**
   - Explore `PrivacyLRS/src/test/` directory
   - Find all test files throughout the codebase
   - Identify test frameworks being used (pytest, unittest, etc.)
   - Locate test configuration files (pytest.ini, tox.ini, etc.)

2. **Document test structure**
   - What types of tests exist? (unit, integration, functional)
   - How are tests organized?
   - What are the test dependencies?
   - Are there fixtures or test utilities?

3. **Find test documentation**
   - Look for README files in test directories
   - Check for testing documentation in docs/
   - Review CI/CD configurations (.github/workflows/, .gitlab-ci.yml, etc.)

### Phase 2: Learn How to Run Tests

4. **Identify test commands**
   - What commands run the tests?
   - Are there make targets? (make test, make check)
   - Python commands? (pytest, python -m unittest)
   - Shell scripts?

5. **Test the test suite**
   - Try running all tests
   - Try running individual test files
   - Try running specific test cases
   - Note any setup requirements (environment variables, config files)

6. **Document what you learn**
   - Create detailed notes in your working directory
   - Include:
     - Prerequisites (dependencies, environment setup)
     - Commands to run tests
     - Common options and flags
     - How to run specific test subsets
     - Expected output format
     - Common errors and solutions

### Phase 3: Create Test Runner Skill

7. **Design the skill**
   - Determine what functionality the skill should provide
   - Consider these use cases:
     - Run all tests
     - Run tests in specific directory
     - Run specific test file
     - Run with coverage reporting
     - Run with verbose output
     - Quick smoke tests vs full suite

8. **Write the skill file**
   - Create `.claude/skills/privacylrs-test-runner.md`
   - Follow the skill format used by other skills
   - Include clear instructions for Claude
   - Provide command examples
   - Document common options

9. **Test the skill**
   - Use the skill to run tests
   - Verify it works correctly
   - Ensure instructions are clear
   - Add troubleshooting tips

## Success Criteria

- [ ] All test directories and files identified
- [ ] Test framework(s) documented
- [ ] Test execution commands documented and verified
- [ ] Successfully run at least one test suite
- [ ] Working notes created documenting:
  - Test infrastructure overview
  - How to run tests (step-by-step)
  - Prerequisites and dependencies
  - Common commands and options
- [ ] Test runner skill created at `.claude/skills/privacylrs-test-runner.md`
- [ ] Skill tested and verified working
- [ ] Completion report sent to manager

## Files to Explore

Start with these locations:

```bash
# Primary test directory
ls -la PrivacyLRS/src/test/

# Find all test files
find PrivacyLRS -name "*test*.py" -o -name "test_*" -o -name "*_test.py"

# Look for test configuration
find PrivacyLRS -name "pytest.ini" -o -name "tox.ini" -o -name ".coveragerc" -o -name "setup.cfg"

# Check for CI/CD configs
ls -la PrivacyLRS/.github/workflows/
ls -la PrivacyLRS/.gitlab-ci.yml 2>/dev/null

# Look for Makefile test targets
grep -n "test" PrivacyLRS/Makefile 2>/dev/null

# Check for test documentation
find PrivacyLRS -name "README*" | grep -i test
find PrivacyLRS/docs -name "*test*" 2>/dev/null
```

## Test Execution Examples to Try

```bash
# Try common test commands (from PrivacyLRS root)
cd PrivacyLRS

# Python unittest
python -m unittest discover

# Pytest (if used)
pytest
pytest src/test/
pytest -v  # verbose
pytest --cov  # with coverage

# Make targets (if they exist)
make test
make check

# Tox (if configured)
tox

# Check for test scripts
./run_tests.sh 2>/dev/null
./test.sh 2>/dev/null
```

## Notes

### Expected Deliverables

1. **Working notes document** - Your personal notes on the test infrastructure
   - Save in your workspace, doesn't need to be a formal report
   - Include everything you learned
   - Make it detailed enough that you could run tests 6 months from now

2. **Test runner skill** - `.claude/skills/privacylrs-test-runner.md`
   - Clear, concise instructions for running tests
   - Common use cases covered
   - Example commands
   - Troubleshooting section

3. **Completion report** - To manager via email
   - Summary of test infrastructure
   - How to run tests (brief version)
   - Location of skill file
   - Any issues or concerns discovered

### Skill Format Reference

Look at existing skills for format examples:
- `.claude/skills/build-sitl.md`
- `.claude/skills/sitl-arm.md`

Skills should:
- Start with clear description of what the skill does
- Provide step-by-step instructions
- Include example commands
- Have troubleshooting tips
- Be written for Claude to follow autonomously

### Questions to Answer in Your Notes

- What test framework(s) are used?
- How many test files exist?
- Do all tests pass currently?
- How long does the full suite take?
- Are there different test categories?
- Is there test coverage reporting?
- Are tests run automatically in CI/CD?
- What are the test dependencies?

## Important Reminders

1. **You're exploring, not analyzing for security** - This task is about understanding the test infrastructure, not performing security analysis of test code
2. **Document as you go** - Take notes while exploring, don't wait until the end
3. **Actually run tests** - Don't just read about them, execute them to verify your understanding
4. **Make the skill useful** - Think about what you'd want to know when running tests in the future

---

**Manager**
