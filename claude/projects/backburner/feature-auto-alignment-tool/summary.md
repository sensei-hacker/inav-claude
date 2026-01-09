# Project: Auto Alignment Tool

**Status:** BACKBURNER
**Priority:** Medium
**Type:** Feature Enhancement
**Created:** 2025-12-12
**PR:** [#2158](https://github.com/iNavFlight/inav-configurator/pull/2158) (OPEN, "Don't merge" label)
**Branch:** From `maintenance-9.x`

## Overview

Wizard-style tool that automatically detects and sets flight controller and compass alignment by having the user perform simple physical movements with the aircraft.

## How It Works

1. User points aircraft north
2. User lifts the nose
3. Tool reads accelerometer and magnetometer data
4. Tool calculates and sets correct alignment values

## Current State

- PR #2158 created Aug 2024
- Basic implementation complete
- Video demo available in PR
- Labeled "Don't merge" - needs review/polish before merge

## Objectives

1. Review and update PR #2158 for current codebase
2. Ensure compatibility with maintenance-9.x
3. Add user guidance/instructions in UI
4. Test with various FC orientations
5. Handle edge cases (no mag, inverted mounting, etc.)

## Success Criteria

- [ ] Works for common FC mounting orientations
- [ ] Works for external compass alignment
- [ ] Clear user instructions during process
- [ ] Graceful handling of errors/invalid data
- [ ] PR ready for merge

## Why Backburner

- Functional but needs polish
- Lower priority than bug fixes
- Can be picked up when time permits

## Files

Key files from PR #2158:
- New alignment wizard UI component
- Sensor data reading logic
- Alignment calculation algorithm
