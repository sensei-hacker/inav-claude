# Cppcheck Work Plan - INAV Firmware Code Review

## Summary Statistics

| Severity | Count | Action |
|----------|-------|--------|
| Error | 78 | Review - many are false positives |
| Warning | 97 | Review selectively |
| Style | 339 | Low priority |
| Portability | 5 | Quick fixes |

## Real Bugs Found (Fix These)

### Priority 1: CRITICAL

1. **`sensors/temperature.c:101` - Buffer overflow**
   ```c
   memset(sensorStatus, 0, sizeof(sensorStatus) * sizeof(*sensorStatus));
   ```
   - BUG: Multiplies size twice, writes beyond buffer
   - FIX: `memset(sensorStatus, 0, sizeof(sensorStatus));`

2. **`fc/config.h:66` - Integer overflow**
   ```c
   FEATURE_FW_AUTOTRIM = 1 << 31,
   ```
   - BUG: Signed integer overflow (undefined behavior)
   - FIX: `FEATURE_FW_AUTOTRIM = 1U << 31,`

### Priority 2: Potential null pointer issues

3. **`drivers/serial_uart.c:139-159`** - NULL dereference if unsupported UART
4. **`drivers/serial_uart_hal.c`** - Same pattern
5. **`drivers/serial_uart_hal_at32f43x.c`** - Same pattern

These may be safe in practice (only called with valid UARTs) but should add null checks.

---

## Work Sessions Plan

Each session should be self-contained and focus on one area.

### Session 1: Quick Fixes
- [ ] Fix `sensors/temperature.c:101` sizeof bug
- [ ] Fix `fc/config.h:66` integer overflow
- [ ] Create PR for these two fixes

### Session 2: GPS/Navigation (Safety Critical)
**Files:** `src/main/navigation/` (12,050 lines)
**cppcheck findings:** 2 errors (false positives), 10 style issues

Focus areas:
- [ ] Review `navigation_pos_estimator_agl.c` duplicate branch (line 101)
- [ ] Manual review of `navigation.c` core logic
- [ ] Manual review of `navigation_pos_estimator.c` GPS fusion
- [ ] Check `navigation_fixedwing.c` and `navigation_multicopter.c`

### Session 3: Flight Control (Safety Critical)
**Files:** `src/main/flight/` (7,052 lines)
**cppcheck findings:** 4 errors (false positives), 7 style issues

Focus areas:
- [ ] Review `pid.c` - PID controller logic
- [ ] Review `failsafe.c` - Failsafe behavior
- [ ] Review `mixer.c` - Motor mixing, shadow variable at line 662
- [ ] Review `servos.c` - Servo control

### Session 4: FC Core (Safety Critical)
**Files:** `src/main/fc/` (16,200 lines)
**cppcheck findings:** 8 errors, many style issues

Focus areas:
- [ ] Review `fc_core.c` - Main flight loop
- [ ] Review `cli.c:659` null pointer check
- [ ] Review `runtime_config.c` - Arming logic
- [ ] Review `rc_controls.c` - Stick commands

### Session 5: Sensors
**Files:** `src/main/sensors/` (5,292 lines)
**cppcheck findings:** 3 errors (false positives), several style

Focus areas:
- [ ] Review `diagnostics.c` dead code (lines 244, 247)
- [ ] Review `acceleration.c` - IMU fusion
- [ ] Review `compass.c` - Magnetometer
- [ ] Review `gyro.c` - Gyroscope processing

### Session 6: RX (Radio)
**Files:** `src/main/rx/` (5,201 lines)
**cppcheck findings:** 1 error

Focus areas:
- [ ] Review `rx.c` - Main receiver logic
- [ ] Review failsafe signal handling
- [ ] Review CRSF/SBUS/etc protocol handlers

### Session 7: Drivers - UART
**Files:** `src/main/drivers/serial_uart*.c`
**cppcheck findings:** 46 errors (many null pointer)

Focus areas:
- [ ] Add null checks to `serial_uart.c`
- [ ] Add null checks to `serial_uart_hal.c`
- [ ] Add null checks to `serial_uart_hal_at32f43x.c`

### Session 8: IO - Warnings Heavy
**Files:** `src/main/io/` (28,000 lines)
**cppcheck findings:** 49 warnings, 1 error

Focus areas:
- [ ] Review `gps.c` redundant assignment
- [ ] Review OSD code
- [ ] Review serial/MSP handling

---

## False Positives (Ignore)

These are cppcheck limitations, not real bugs:

1. **`PG_RESET_TEMPLATE` / `RESET_CONFIG` macro errors** - INAV's parameter group macros
2. **`IO_CONFIG` macro errors** - GPIO configuration macros
3. **`DEFINE_DMA_IRQ_HANDLER` unknown macro** - DMA interrupt handlers
4. **`comparePointers` in config_eeprom.c** - Intentional linker section iteration
5. **`uninitvar` in time.c** - Variables assigned inside `ATOMIC_BLOCK` macro

---

## Notes

- Start each session by reading this plan
- Each session: focus on ONE area, complete it, document findings
- Create separate PRs for each logical group of fixes
- Don't try to fix style issues unless they indicate real bugs
- Safety-critical code (navigation, flight, fc) gets priority
- If any unrelated bugs are spotted during investigation, flag them
