# Email to Manager

**Date:** 2025-11-28
**From:** Developer
**To:** Manager
**Subject:** SITL Arming Project - Blocked by uNAVlib Library Bug

---

## Summary

The SITL MSP Arming project is paused due to a bug in the uNAVlib Python library that we've been using for MSP communication.

## Issue Discovered

The uNAVlib library fails to correctly receive responses from certain MSP commands (MSP_RX_CONFIG, MSP_RC), returning empty data even though the flight controller is sending valid responses.

I verified this by implementing raw MSP protocol communication, which correctly receives all responses. The problem is specifically in the uNAVlib library's message parsing/handling.

## Impact

This bug was causing false debugging signals - it appeared that the FC wasn't responding to commands when it actually was. This led us down the wrong path investigating FC-side issues.

## Good News

Through debugging with raw MSP protocol, I confirmed that:
1. MSP_SET_RX_CONFIG correctly sets receiver type to MSP (value 2)
2. MSP_EEPROM_WRITE correctly saves the configuration
3. After reboot, receiver type persists as MSP
4. MSP_RC returns 34 channels of RC data when receiver is configured as MSP

## Decision Needed

Please advise on how to proceed:

**Option A:** I implement a minimal raw MSP protocol handler to replace uNAVlib for SITL testing (estimated 1-2 hours of work)

**Option B:** We find/evaluate an alternative Python MSP library

**Option C:** We debug and fix uNAVlib (would need to understand their codebase)

## Documentation

Full issue details documented at:
`claude/developer/work_in_progress/unavlib_issue.md`

Raw MSP debug tool created at:
`claude/developer/test_tools/msp_debug.py`

---

**Status:** PAUSED - Awaiting decision on library approach
