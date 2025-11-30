# Project: Fix uNAVlib MSP Response Handling

**Status:** 📋 TODO
**Priority:** High
**Type:** Bug Fix
**Created:** 2025-11-28
**Estimated Effort:** 2-4 hours
**Blocks:** sitl-msp-arming → fix-gps-recovery-issue-11049

## Overview

Fix a bug in the uNAVlib Python library where certain MSP commands fail to return response data, even though the flight controller is sending valid responses.

## Problem

The uNAVlib library fails to correctly receive responses from certain MSP commands:

| Command | Code | Expected | Actual |
|---------|------|----------|--------|
| MSP_RX_CONFIG | 44 | 24 bytes | Empty/None |
| MSP_RC | 105 | 68 bytes | Empty/None |

Raw MSP protocol communication (bypassing uNAVlib) correctly receives all responses, proving the issue is in the library's message parsing/handling.

## Evidence

**Raw MSP works:**
```
MSP_RX_CONFIG: 24 bytes (receiverType at byte 23)
MSP_RC: 68 bytes (34 channels × 2 bytes each)
```

**uNAVlib fails:**
```python
board.send_RAW_msg(MSP_RX_CONFIG, data=[])
dataHandler = board.receive_msg()
# dataHandler.data is empty or None
```

## Commands That DO Work in uNAVlib

- MSP2_INAV_STATUS (code 0x2000)
- MSP_SET_RX_CONFIG (code 45) - write only
- MSP_EEPROM_WRITE (code 250)
- MSP_REBOOT (code 68)

## Suspected Cause

1. Message parsing issues for certain MSP v1 response codes
2. Buffer handling that causes responses to be missed/discarded
3. Possible race condition in receive handling

## Library Location

**Local clone:** `uNAVlib/`

**Key files to investigate:**
- `unavlib/modules/boardconn.py` - Board connection and MSP communication
- `unavlib/modules/msp_ctrl.py` - MSP control functions
- `unavlib/main.py` - Main library interface

## Objectives

1. Identify root cause of failed MSP response handling
2. Fix the bug so MSP_RX_CONFIG and MSP_RC return correct data
3. Verify fix doesn't break other MSP commands
4. Test with SITL

## Success Criteria

- [ ] MSP_RX_CONFIG returns 24 bytes of data
- [ ] MSP_RC returns 68 bytes of RC channel data
- [ ] Existing working commands still function
- [ ] sitl_arm_test.py works with fixed library
