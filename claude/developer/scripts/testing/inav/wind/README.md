# Wind Estimator / JSBSim Wind-Injection Testing

Tools for testing INAV's fixed-wing wind estimator (`src/main/flight/wind_estimator.c`)
against a **known, controlled wind vector** injected into JSBSim — including a
vertical (Z-axis) component, which no other documented simulator path
(X-Plane HITL, RealFlight) currently exposes a scripted way to set.

Built on the `jsbsim-sitl-testing` skill's MSP/HITL loop
(`~/inavflight/inav-sitl-bench`'s `msp.py`/`hitl.py`/`jsbsim_plant.py`) — read
that skill first if you haven't used the JSBSim SITL path before.

**Origin:** written for PR #11855 review (empirically settling whether
`getEstimatedWindSpeed(Z)`'s sign convention changed) — see
`claude/projects/*/review-pr11855-wind-estimator-timing/` or search git log
for that task's completion report for the full investigation writeup and
result. The scripts themselves are general-purpose despite the
PR-specific names below.

## Scripts

- **`provision_wind_z_sign_test.py`** — one-time FC provisioning for a
  fixed-wing SITL/HITL wind test: `platform_type=AIRPLANE`, GPS via MSP,
  standard aileron/elevator/rudder servo mixer, ARM/ANGLE mode ranges,
  blackbox-to-FILE. Mainline-safe subset of `jsbsim-sitl-testing`'s
  `provision_mainline()` pattern — reuse as a starting point for any new
  fixed-wing JSBSim wind test, not just this one.
- **`wind_z_sign_test.py`** — flies a configurable scenario: settle → arm
  → level cruise → N repeats of a climb/dive pitch maneuver at zero wind →
  inject a known, steady wind (magnitude and axis via
  `atmosphere/wind-down-fps`/`wind-north-fps`/`wind-east-fps`) → N more
  climb/dive repeats under that wind → recover/disarm. Tunable via CLI:
  `--wind-down-fps`, `--pitch-hold-secs`, `--repeats`,
  `--elevator-deflection`. Writes a CSV flight trace and a JSON phase-timing
  sidecar (phase boundaries + JSBSim ground-truth pitch/climb-rate at each
  phase end — use JSBSim's own truth, not the FC's attitude estimate, for
  interpreting results; see Gotchas below).
- **`analyze_wind_z_blackbox.py`** — decodes the SITL blackbox `.TXT` log
  (via `blackbox_decode`, or an already-decoded `.csv`) and reads the raw,
  **unconverted** per-axis `wind[i]` field (`blackbox.c:1491`,
  `slow->wind[i] = getEstimatedWindSpeed(i)`) per phase from the sidecar
  JSON. No MSP field exposes this raw value directly — `MSP2_INAV_WIND`
  only gives the combined horizontal magnitude+angle — so blackbox is the
  only way to see the true, unconverted per-axis estimate.

## Why this exists / what it's for

Any time a change touches `wind_estimator.c`'s math, its timing, or any of
its consumers (`flight/rth_estimator.c`, `io/osd.c`,
`sensors/pitotmeter.c`'s virtual-airspeed path), and the question is "does
the firmware actually produce/consume the right wind value" — not just "is
the algebra internally consistent" — this is the tool. Manual sign/frame
derivation (NED vs. NEU, earth-frame conventions) is error-prone even when
done carefully; injecting a *known* wind and reading back the *raw* result
answers it empirically.

## JSBSim wind-injection reference

Confirmed directly (2026-09-06) on a standalone `c172p` JSBSim model —
these properties exist, are read-write, and visibly affect aircraft motion:

| Property | Convention | Notes |
|---|---|---|
| `atmosphere/wind-down-fps` | NED (positive = downdraft, air moving down) | Matches `gpsSol.velNED[Z]`'s own naming/convention directly |
| `atmosphere/wind-north-fps` | positive = wind blowing toward north | |
| `atmosphere/wind-east-fps` | positive = wind blowing toward east | |
| `atmosphere/total-wind-{down,north,east}-fps` | (read-only) | Effective wind actually applied — use to verify the commanded value took effect |

Verified: commanding `wind-down-fps = 10.0` held and read back exactly via
`total-wind-down-fps`, and `velocities/h-dot-fps` (climb rate) responded
(went negative/descending) within a few sim steps.

## Gotchas (learned running this against PR #11855)

- **Keep pitch maneuvers gentle.** A first attempt at
  `--elevator-deflection 400` (near-max, RC_MID ±400) in ANGLE mode drove
  JSBSim into large uncontrolled oscillations (±85° pitch swings) — almost
  certainly because the degraded FC attitude estimate (see next point)
  fought the attitude controller. Result: `wind[0]`/`wind[1]`/`wind[2]`
  stayed at **exactly 0.0 for the entire flight** — every candidate
  estimate was silently rejected by `wind_estimator.c`'s spike filter
  (designed for realistic, not violent, attitude changes), which looks
  identical to "no signal" rather than a harness bug. Dropping to
  `--elevator-deflection 120 --pitch-hold-secs 10` produced a clean,
  controlled maneuver (single digits to ~30° pitch) and a real, moving
  wind estimate. **If a run comes back with a flat/zero result across all
  three axes for the whole flight, suspect an over-aggressive maneuver
  before suspecting the firmware.**
- **GPS injection biases the FC's own attitude estimate.**
  `inav-sitl-bench`'s own `jsbsim_fly.py` avoids injecting GPS during fine
  attitude-hold tests for exactly this reason. This test *must* inject GPS
  every step (`wind_estimator.c`'s Z-axis math directly consumes
  `gpsSol.velNED[Z]`/`posEstimator.gps.vel.z` and is hard-gated on
  `gpsSol.flags.validVelNE`/`validVelD` and `isGPSHeadingValid()`), so the
  bias is unavoidable — use JSBSim's own ground-truth attitude
  (`attitude/theta-deg`) for interpreting results, not the FC's estimate.
- **Don't assume `attitude.values.pitch`'s sign matches intuition.** A
  past investigation on this project found INAV's own pitch-estimate sign
  is counter-intuitive in places (e.g. `io/osd.c` draws `SYM_PITCH_DOWN`
  for `pitch > 0`). This is exactly the kind of confusion this harness
  exists to sidestep — always read climb-vs-dive off JSBSim's own
  `attitude/theta-deg`, standard aviation convention (positive = nose up),
  not off the FC's telemetry.
- **The `wind` blackbox slow-field only logs on change**
  (`blackbox.c` `writeSlowFrameIfNeeded()`). A phase with zero samples in
  the analyzer's output isn't necessarily a failure — check the phase
  sidecar's ground-truth pitch/climb-rate to confirm the maneuver actually
  happened before concluding anything from an empty phase.
- **`blackbox_decode` can produce multiple CSVs from one log** (a
  `.01.csv` with the main flight fields, plus a `.01.gps.csv` GPS-only
  side-file) — make sure you're reading `wind[2]` from the main one, not
  whichever file `blackbox_decode` happens to print last.

## Usage

See the docstring at the top of `wind_z_sign_test.py` (`--help`) and this
task's own run sequence, roughly:

```bash
# 1. Build SITL (-DSITL=ON) from whichever branch you're testing, via inav-builder
cd <build-dir>/bin && ./SITL.elf &
sleep 3

# 2. Provision once, then restart to apply EEPROM changes
python3 provision_wind_z_sign_test.py
pkill -9 SITL.elf; ./SITL.elf & ; sleep 3

# 3. Fly the scenario (tune flags if the default maneuver doesn't clear
#    the estimator's diffLengthSq gate or trips the spike filter -- see
#    Gotchas above)
python3 wind_z_sign_test.py --wind-down-fps 12 --elevator-deflection 120 --pitch-hold-secs 10

# 4. Find + analyze the blackbox log it produced (written to SITL's cwd)
ls -t *.TXT | head -1
python3 analyze_wind_z_blackbox.py <newest>.TXT ./wind_z_sign_test_phases.json
```
