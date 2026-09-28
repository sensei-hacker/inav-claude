---
description: Fly real INAV SITL against JSBSim's full-aerodynamics model to test your own mainline changes
triggers:
  - jsbsim sitl
  - jsbsim testing
  - full aerodynamics sitl
  - inav-sitl-bench
  - test with jsbsim
---

# JSBSim SITL Testing

Real INAV firmware, running as SITL, flown against [JSBSim](https://github.com/JSBSim-Team/jsbsim)
— actual airspeed/lift/drag/stall aerodynamics, not the simple rigid-body plant
SITL uses by default. It works over the stock `MSP_SIMULATOR`/HITL sensor-injection
path (synthetic gyro/acc/baro -> real AHRS -> real controller -> mixer outputs ->
back into the model), which is ordinary mainline INAV — there's nothing exotic
about the mechanism itself.

Use this any time a test needs real flight physics: airspeed-dependent behavior,
stall, energy management, control-surface authority — anything the built-in
rigid-body SITL plant can't represent.

See the **install-jsbsim** skill first if JSBSim itself isn't installed yet.

## Quick Start (testing your own mainline changes)

```bash
# 1. Build SITL from mainline the normal way — inav/inav2/inav3, whichever
#    checkout has your changes. Use the inav-builder agent (-DSITL=ON), never
#    cmake/make directly.

# 2. Start it
cd inav3/build_sitl && ./bin/SITL.elf &     # binds tcp:127.0.0.1:5760

# 3. Provision the FC for HITL/JSBSim testing (see sample script below —
#    write your own, scoped to mainline settings + your feature's mode range)
python3 provision_mainline.py
# then restart SITL: pkill -9 SITL.elf; relaunch it (eeprom save requires a
# reboot to take effect)

# 4. Fly it against JSBSim (see scenario-script sketch below)
python3 your_feature_test.py
```

The pieces you need — `msp.py` (MSPv2/TCP client), `hitl.py` (`MSP_SIMULATOR`
pack/unpack), and `jsbsim_plant.py` (JSBSim-as-plant wrapper) — already exist and
are fully generic. Rather than reinvent them, copy or import them from
`inav-sitl-bench` (`~/inavflight/inav-sitl-bench`,
`github.com/swissembedded/inav-sitl-bench`) — none of those three files contain
anything specific to any one feature. What you write yourself is a small
provisioning function and a scenario script scoped to whatever you're testing.

No `podman`/container is required if you're already on Linux — running `SITL.elf`
directly, the 1 kHz MSP/JSBSim coupling this needs held its slot with 0 overruns
and ~0.4 ms round-trip per cycle in testing on this machine. (A container matters
more on Windows, where cygwin `SITL.exe` is capped at ~64 Hz by the timer tick and
breaks the coupling.)

## What's Mainline-Safe vs. What's Specific to the Existing Example

`inav-sitl-bench` ships one full worked example (`bench.py` + `jsbsim_fly.py`),
built to test a specific unmerged feature
(`swissembedded/inav`'s `feature/quaternion-attitude-hold` branch). It's useful to
read for structure, but most of its *provisioning values* only make sense for
that feature. **Verified against mainline `inav/src/main/fc/settings.yaml` and
`src/main/flight/servos.h` (2026-07-12):**

| Mainline-safe (reuse as-is) | Specific to the quaternion-attitude-hold example — will fail against mainline |
|---|---|
| `receiver_type`, `platform_type`, `small_angle`, `baro_hardware`, `mag_hardware`, `init_gyro_cal`, `pitot_hardware`, `gps_provider`, `inav_default_alt_sensor` | `fig_assist_z_gain`, `fig_assist_vz_gain`, `fig_assist_max`, `fig_roll_rate`, `fig_loop_rate`, `ohold_*` (6 settings), `tvc_gain`, `tvc_thrust_comp` — don't exist in mainline `settings.yaml` |
| Servo mixer inputs 0/1/2 (stabilized roll/pitch/yaw) | Servo mixer input 62 (TVC pitch) — mainline's `inputSource_e` maxes out at `INPUT_MIXER_SWITCH_HELPER = 60`; there's no TVC input at all |
| `PERM_ARM = 0`, `PERM_ANGLE = 1` (stable, standard permanent box IDs) | `PERM_INVERTED`/`PERM_KNIFELEFT`/`PERM_KNIFERIGHT`/`PERM_PROPHANG`/`PERM_ALTFLOOR`/`PERM_FIG*` — not registered in mainline `fc_msp_box.c` |
| `msp.py`, `hitl.py`, `jsbsim_plant.py` wholesale | `bench.py`'s scenario functions (`smoke`/`scenarios`/`edge`/`floor`/`tvc`/`figures`/`sequence`) and all of `jsbsim_fly.py`'s maneuver logic — every assertion in them is orientation-hold-specific |

For whatever mode your own feature needs (RTH, a new nav mode, a new failsafe
behavior, ...), look up its real permanent box ID in mainline's
`inav/src/main/fc/fc_msp_box.c` (or query `MSP_BOXIDS`/`MSP_BOXNAMES` at runtime)
— don't guess a number or reuse one of the example's `PERM_FIG*` values.

## Sample: Trimmed `provision()` for Mainline

```python
# provision_mainline.py — mainline-safe subset of inav-sitl-bench's bench.py
# provision(). Reuses msp.py from inav-sitl-bench; add your own feature's
# mode range(s) where marked.
import struct
from msp import MspClient

def provision_mainline(extra_mode_ranges=()):
    msp = MspClient()
    print("API", msp.api_version())

    msp.set_setting("receiver_type", struct.pack("<B", 3))     # SIM (SITL)
    msp.set_setting("platform_type", struct.pack("<B", 1))     # AIRPLANE
    msp.set_setting("small_angle", struct.pack("<B", 180))
    msp.set_setting("baro_hardware", struct.pack("<B", 12))    # FAKE
    msp.set_setting("mag_hardware", struct.pack("<B", 0))      # NONE
    msp.set_setting("init_gyro_cal", struct.pack("<B", 0))     # skip: no real
                                                                # sensors behind HITL
    msp.set_setting("pitot_hardware", struct.pack("<B", 0))    # NONE
    msp.enable_feature(1 << 7)                                 # FEATURE_GPS
    msp.set_setting("gps_provider", struct.pack("<B", 1))      # MSP-driven

    # Standard airplane servo mixer (S1 aileron, S2 elevator, S3 rudder) —
    # without this, isMixerUsingServos() is false and the MSP_SIMULATOR
    # reply's stabilized outputs stay 0 (see Troubleshooting).
    msp.set_servo_mixer_rule(0, 0, 0)   # servo 0 <- stabilized roll
    msp.set_servo_mixer_rule(1, 1, 1)   # servo 1 <- stabilized pitch
    msp.set_servo_mixer_rule(2, 2, 2)   # servo 2 <- stabilized yaw

    PERM_ARM, PERM_ANGLE = 0, 1
    CH_ARM, CH_ANGLE = 4, 5              # AUX1/AUX2 in an AETR+AUX1..4 layout
    msp.set_mode_range(0, PERM_ARM, CH_ARM - 4, 1700, 2100)
    msp.set_mode_range(1, PERM_ANGLE, CH_ANGLE - 4, 1700, 2100)

    # Your own feature's mode range(s) go here, e.g.:
    # msp.set_mode_range(2, YOUR_PERM_BOX_ID, YOUR_AUX_CHANNEL - 4, 1700, 2100)
    for i, (perm_id, aux_ch, start_pwm, end_pwm) in enumerate(extra_mode_ranges, start=2):
        msp.set_mode_range(i, perm_id, aux_ch - 4, start_pwm, end_pwm)

    msp.save_eeprom()
    print("provisioned + saved, SITL reboots now")

if __name__ == "__main__":
    provision_mainline()
```

## Sketch: Your Own Scenario Script

`jsbsim_plant.py`'s `JSBSimPlant` class works unmodified against mainline — pass
a JSBSim-bundled aircraft (`JSBSimPlant(model="c172p")`) instead of the example's
custom `aerobat3d`/`funjet`, unless your feature specifically needs unusual
aerodynamics. The pattern (borrow from `jsbsim_fly.py`'s `loop()`):

```python
from msp import MspClient
from hitl import sim_step
from jsbsim_plant import JSBSimPlant

m = MspClient()
plant = JSBSimPlant(model="c172p", alt_ft=1500, kts=60)

def loop(secs, rc):
    import time
    t0 = time.time()
    while time.time() - t0 < secs:
        r = sim_step(m, plant.acc_mg(), plant.gyro_dps16(), rc, baro_pa=plant.baro_pa())
        # ail/ele/rud/thr from r.stab_roll/stab_pitch/stab_yaw/stab_throttle,
        # feed into plant.set_controls(...), then plant.step(dt=0.001)
        # ... your feature's assertions go here, checking FC state via MSP
        # or the RC/mode you're driving
```

Wait for boot gyro calibration to clear before sending the first `MSP_SIMULATOR`
frame (see Troubleshooting) — that gotcha isn't feature-specific, it applies to
any HITL/JSBSim test against any INAV build.

## Troubleshooting

| Issue | Likely cause / fix |
|---|---|
| Gyro boot calibration never finishes | The first `MSP_SIMULATOR` frame arrived before boot gyro cal finished — `gyroUpdate()` early-returns under HITL. Wait for `armingFlags` bit 9 to clear before streaming HITL frames. Applies to any INAV build, not just the fork example. |
| Stabilized outputs stay 0 in the `MSP_SIMULATOR` reply | No servo mixer rules provisioned — `isMixerUsingServos()` is false so `servoMixer()` never runs. Confirm your provisioning ran and the FC was restarted after (`save_eeprom()` needs a reboot to take effect). |
| `bench.py provision` / a fork-style `set_setting` call rejected | You're using the example's `provision()` (fork-specific settings/box IDs) against a mainline build. Use the mainline-safe subset above instead. |
| `struct.error: argument out of range` in `hitl.py pack_request` (`baro_pa`) | Simulated altitude/IAS diverged to an extreme value (integer overflow packing it) — a numerical-instability symptom in the plant/controller loop, not a wiring bug. Seen in testing during a wind-gust disturbance segment on the quaternion-attitude-hold example specifically; if you hit it on your own feature, that's a real finding about your control loop, not this harness. |
| SITL port 5760 already in use | `pkill -9 SITL.elf` before relaunching. |
| `ModuleNotFoundError: jsbsim` | Run the **install-jsbsim** skill first. |

## Reference: The Existing Quaternion-Attitude-Hold Example

`inav-sitl-bench`'s own `bench.py`/`jsbsim_fly.py` is a complete worked example —
useful to read for structure and for the SITL/HITL gotchas documented in its
README — but it targets one specific unmerged feature and needs a different SITL
build than your own work:

- **Build target:** `github.com/swissembedded/inav`'s `feature/quaternion-attitude-hold`
  branch, not `iNavFlight/inav` mainline:
  ```bash
  git remote add swissembedded https://github.com/swissembedded/inav.git   # once
  git fetch swissembedded feature/quaternion-attitude-hold
  git checkout -b <local-branch-name> swissembedded/feature/quaternion-attitude-hold
  ```
  Build via `inav-builder` (`-DSITL=ON`, target `SITL.elf`) on a temporary local
  branch of one of the existing `inav`/`inav2`/`inav3` checkouts (acquire the
  matching `claude/locks/inav*.lock` first) — restore the checkout's original
  branch and release the lock when done.
- **Run it:** `python3 bench.py provision` (then restart SITL) → `python3
  bench.py smoke` (rigid-body plant, fast wiring check) → `python3 jsbsim_fly.py
  inverted` (or `knife_left`/`knife_right`/`hang`/`roll_hold`/`floor_dive`/
  `flat_spin`/`tvc_hang`) for the actual JSBSim closed loop → `python3
  animate_jsbsim.py <maneuver>` / `python3 plot_jsbsim.py` to visualize.
- **Verified 2026-07-11/12:** `bench.py provision` + restart + `smoke` → clean,
  repeatable `SMOKE PASS`. `jsbsim_fly.py inverted` ran the full settle → cal →
  arm → level → manual → inverted sequence, then diverged numerically during the
  wind-gust segment. `jsbsim_fly.py roll_hold` completed with clean 1 kHz timing
  (0 slot overruns) but the FC's attitude estimate and JSBSim ground truth never
  converged to the expected `|roll| ~ 180` hold. Read this as: the mechanism
  (MSP wiring, JSBSim-as-plant swap, real-time coupling) is solid; this
  particular feature branch's controller isn't reliably converging run-to-run
  yet. That matches the bench's own README, which documents several "cost hours,
  do not rediscover" gotchas and calls one bailout mode "known-flaky." Fixing the
  controller is out of scope here — treat `inav-sitl-bench` and the fork as
  external references, like `mspapi2`.

## Reference: Other Developers' Example Scripts

`claude/developer/scripts/testing/inav/sitl/jsbsim_examples/` collects sample
scripts from other INAV developers' own JSBSim test frameworks — separate
from `inav-sitl-bench`, each with its own `Bench`-style API and support
files. See that directory's README before using one.

- **`plane_runway_takeoff.py`** (from `xznhj8129/Inav_jsbsim`, also the
  `mspapi2` author) — Cessna 172 runway takeoff -> climb -> level-off ->
  ANGLE + NAV ALTHOLD, flown by hand in ACRO up to level-off because (per its
  original docstring) INAV's pitch estimate read ~12 deg high during the
  takeoff roll's acceleration. That symptom matches a bug fixed by
  https://github.com/iNavFlight/inav/pull/12055 (merged into
  `maintenance-10.x`): `imuCalculateTurnRateacceleration()` in
  `src/main/flight/imu.c` was only reapplying the GPS3Dspeed turn-rate filter
  on a new GPS heartbeat instead of every IMU loop tick, giving it the wrong
  time constant during acceleration. Re-verify against current mainline
  before assuming the ACRO workaround is still needed. Needs `inavbench.py`
  from the same upstream repo (not vendored here) to actually run.

## Related Skills

- **install-jsbsim** — install/verify the JSBSim Python package (do this first)
- **build-sitl** — build INAV SITL firmware
- **sitl-arm** — general SITL arming via MSP
- **xplane-sitl** — the other full-aerodynamics SITL path (X-Plane); heavier
  (GUI, license) but mature and not tied to any one feature branch

## Resources

- `claude/developer/scripts/testing/inav/sitl/jsbsim_examples/README.md` —
  other developers' example scripts (see above)
- `inav-sitl-bench/README.md` — full command reference, SITL/HITL gotchas, JSBSim
  section, aircraft descriptions
- `inav-sitl-bench/docs/rc_3d_flying_quick_guide.md` — maps real RC 3D-flying
  technique onto attitude-hold behavior (relevant mainly to the existing example)
- [JSBSim](https://github.com/JSBSim-Team/jsbsim) upstream project
