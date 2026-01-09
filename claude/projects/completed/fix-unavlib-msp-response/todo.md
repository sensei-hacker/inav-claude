# Todo List: Fix uNAVlib MSP Response Handling

## Phase 1: Investigation

- [ ] Study uNAVlib codebase structure
- [ ] Trace MSP receive flow in `unavlib/modules/boardconn.py`
- [ ] Trace message parsing in `unavlib/modules/msp_ctrl.py`
- [ ] Compare working commands (MSP2_INAV_STATUS) vs failing commands (MSP_RX_CONFIG)
- [ ] Identify difference in handling

## Phase 2: Root Cause Analysis

- [ ] Add debug logging to receive path
- [ ] Test with SITL to capture actual behavior
- [ ] Identify exactly where data is lost or discarded
- [ ] Document root cause

## Phase 3: Fix Implementation

- [ ] Implement fix for MSP response handling
- [ ] Ensure fix handles both MSP v1 and MSP v2
- [ ] Test MSP_RX_CONFIG returns correct data
- [ ] Test MSP_RC returns correct data
- [ ] Verify existing commands still work

## Phase 4: Testing

- [ ] Run msp_debug.py to compare raw vs library behavior
- [ ] Run sitl_arm_test.py with fixed library
- [ ] Verify SITL arming works end-to-end

## Completion

- [ ] Root cause documented
- [ ] Fix implemented and tested
- [ ] Send completion report to manager
