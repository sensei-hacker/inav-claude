# Task Assignment: Fix uNAVlib MSP Response Handling

**Date:** 2025-11-28 12:40
**Project:** fix-unavlib-msp-response
**Priority:** High
**Estimated Effort:** 2-4 hours
**Blocks:** sitl-msp-arming → fix-gps-recovery-issue-11049

## Task

Fix the bug in uNAVlib where certain MSP commands fail to return response data.

## Background

You discovered this bug while working on sitl-msp-arming. Raw MSP protocol works correctly, but uNAVlib fails to receive responses from MSP_RX_CONFIG (44) and MSP_RC (105). This is blocking SITL arming testing.

## Library Location

**Local clone:** `uNAVlib/`

## What to Do

1. **Study the codebase:**
   - `unavlib/modules/boardconn.py` - Board connection, MSP communication
   - `unavlib/modules/msp_ctrl.py` - MSP control functions
   - `unavlib/main.py` - Main interface

2. **Trace the issue:**
   - Compare how working commands (MSP2_INAV_STATUS) are handled vs failing commands (MSP_RX_CONFIG)
   - Add debug logging if needed
   - Identify where data is lost

3. **Fix the bug:**
   - Implement fix for MSP response handling
   - Ensure both MSP v1 and MSP v2 work correctly

4. **Test:**
   - Verify MSP_RX_CONFIG returns 24 bytes
   - Verify MSP_RC returns 68 bytes
   - Verify existing working commands still function
   - Test sitl_arm_test.py with the fixed library

## Reference Materials

- Issue documentation: `claude/developer/work_in_progress/unavlib_issue.md`
- Raw MSP debug tool: `claude/developer/test_tools/msp_debug.py`

## Success Criteria

- [ ] MSP_RX_CONFIG returns correct 24-byte response
- [ ] MSP_RC returns correct 68-byte response
- [ ] Existing commands still work
- [ ] sitl_arm_test.py functions correctly

## Notes

- This unblocks sitl-msp-arming, which unblocks GPS recovery testing
- You already have working raw MSP code to compare against
- The library is a local clone, so you can modify it directly

---
**Manager**
