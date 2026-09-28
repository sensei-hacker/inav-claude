# SITL / Real-Hardware MSP Test Scripts

## Start here: `hitl_msp_serial.py`

**Reusable library** for driving a **real flight controller over USB VCP
serial** (not SITL) via the `MSP_SIMULATOR` / `SIMULATOR_MODE_HITL`
facility. This lets you exercise arming and nav-mode logic on a bench FC
(no props/motors/battery attached) with fully synthetic gyro/accel/baro/GPS
data injected over MSP -- "HITL on real hardware," on the actual target
firmware, not just SITL.

Import it (`import hitl_msp_serial as h`) and use `h.MspSerialClient`,
`h.HitlState`, `h.HitlSender`, `h.provision()`, `h.wait_armable()`,
`h.arm()`, `h.safe_shutdown()`. Full worked example (3 test scenarios) at
`claude/developer/workspace/investigate-fw-inflight-detection-dead-reckoning/hw_test_launch_mode_emerg_rearm.py`
(issue #11644 -- also a good reference for the *test design*, not just the
transport: it includes a "trivial control" scenario pattern worth reusing
whenever you need to prove a live MSP-consulted code path isn't secretly
reading a stale, pre-computed cache).

**Read the module docstring before writing a new HITL hardware script** --
it documents six real-hardware-specific pitfalls that are easy to
rediscover the hard way (compile-time `USE_SIMULATOR` gating, MSP-over-
serial reply reordering, thread-safety of the serial port, gyro-calibration
timing, the box-mode-flags bit-ordering trap, and safe-shutdown ordering).
The `test-engineer` agent's lessons file (`.claude/agents/test-engineer.md`)
has the same lessons in one-line form plus the debugging story behind each.

**Key facts worth internalizing:**
- `USE_SIMULATOR` is defined by default for nearly every target
  (`src/main/target/common.h`) -- check `target.h` for `#undef
  USE_SIMULATOR` before assuming HITL isn't available on a given board.
- Arming via MSP **does** work on real hardware with the full HITL sensor
  payload (`SIMULATOR_MSP_VERSION = 2`, all sensor fields populated) plus a
  correctly-timed gyro-calibration wait (>2000ms after boot, before the
  first `MSP_SIMULATOR` frame) and a normal arm-switch RC sequence. This
  contradicts the older `HARDWARE_FC_MSP_RX_STATUS.md` in this directory,
  which concluded arming via MSP was blocked by an
  `ARMING_DISABLED_MSP`-type flag on a different board (BROTHERHOBBYH743)
  -- that investigation used only a 1-byte minimal HITL payload (see
  `arm_fc_physical.py`) without the calibration-timing fix, which is the
  much more likely explanation than a hardware-specific safety flag.
- `MSP_STATUS_EX` / `MSP2_INAV_STATUS`'s box-mode-flags bitmask is **not**
  the `flightModeFlags_e` enum -- see the module docstring / lessons file.

## Other real-hardware scripts

- `arm_fc_physical.py` -- minimal single-thread arm-via-MSP example
  (1-byte HITL payload, `mspapi2`-based). Good quick smoke test; use
  `hitl_msp_serial.py` for anything needing real sensor override (nav
  modes, GPS-dependent logic, etc.).
- `configure_fc_msp_rx.py`, `query_fc_sensors.py`, `check_rx_config.py` --
  older diagnostic/config scripts from the BROTHERHOBBYH743 GPS-fluctuation
  investigation (issue #11202). See `HARDWARE_FC_MSP_RX_STATUS.md` for that
  session's notes (now partially superseded -- see note above).

## JSBSim example scripts

`jsbsim_examples/` -- sample scripts from other INAV developers' JSBSim test
frameworks (a different framework than `inav-sitl-bench`; see that
directory's README before using one).

## SITL scripts

Everything else in this directory (`sitl_arm_test.py`,
`test_althold_*.py`, `test_fw_wp_turn_mode_gate.py`,
`probe_nav_pos_estimator_health.py`, etc.) targets SITL over TCP, not real
hardware. See the top-level `claude/developer/scripts/testing/inav/README.md`
for the full index.
