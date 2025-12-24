# Project: Fix I2C Speed Warning Bug

**Status:** 📋 TODO
**Priority:** MEDIUM
**Type:** Bug Fix
**Created:** 2025-12-16
**Estimated Time:** 1-2 hours

## Overview

Fix incorrect warning message "This I2C speed is too low!" that appears in the INAV Configurator Configuration tab even when I2C speed is set to the maximum possible value.

## Problem

**Symptom:**
- User sets I2C speed to maximum value
- Warning message "This I2C speed is too low!" still appears
- Warning should not display when speed is at maximum

**Location:**
- File: `tabs/configuration.html`
- Component: I2C speed configuration section

**Impact:**
- Confusing UX - users think they need to increase speed further
- Warning loses credibility when shown incorrectly
- Minor but annoying bug

## Objectives

1. Locate the I2C speed validation logic in configuration.html
2. Identify why warning triggers at maximum value
3. Fix the validation condition
4. Test with minimum, medium, and maximum I2C speed values
5. Verify warning appears correctly (only when speed is actually too low)

## Scope

**In Scope:**
- Fix validation logic for I2C speed warning
- Test warning appears/disappears correctly
- Verify across different I2C speed values

**Out of Scope:**
- Changing what "too low" means (threshold value)
- Redesigning I2C configuration UI
- Other configuration warnings

## Implementation Steps

1. Locate I2C speed UI code in `tabs/configuration.html`
2. Find the validation logic that triggers "This I2C speed is too low!"
3. Identify the bug in the condition
   - Off-by-one error?
   - Incorrect comparison operator (>= vs >)?
   - Wrong threshold value?
4. Fix the condition
5. Test with various I2C speed values
6. Create PR to `maintenance-9.x`

## Success Criteria

- [ ] Warning does NOT appear when I2C speed is at maximum
- [ ] Warning DOES appear when I2C speed is genuinely too low
- [ ] Warning appears/disappears correctly as user adjusts speed
- [ ] No console errors or JavaScript issues
- [ ] PR created and ready for review

## Estimated Time

1-2 hours:
- Locate code: 15-30 minutes
- Identify bug: 15-30 minutes
- Fix and test: 30-60 minutes

## Priority Justification

MEDIUM priority - Annoying UX bug that confuses users, but doesn't break functionality. Quick fix that improves user experience.
