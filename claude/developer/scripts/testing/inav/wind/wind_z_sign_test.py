#!/usr/bin/env python3
"""
wind_z_sign_test.py -- empirical test for the PR #11855 vertical-wind
(Z-axis) sign question.

See notes-vertical-wind-sign-investigation.md (one directory up) for the
full background. Short version: PR #11855 changes
fuselageDirection[Z] in src/main/flight/wind_estimator.c. Two of the three
consumers of getEstimatedWindSpeed(Z) (flight/rth_estimator.c:156,
io/osd.c:3768) are unchanged and still do
    -getEstimatedWindSpeed(Z) // from NED to NEU
This test measures, empirically, what raw sign convention
getEstimatedWindSpeed(Z) actually has after the PR's change, by injecting a
KNOWN-direction vertical wind into JSBSim and reading back the firmware's
own raw (unconverted) wind[Z] estimate from its blackbox log.

WHAT THIS SCRIPT DOES NOT DO: it does not compute or guess the answer. It
flies a controlled scenario and leaves the raw numbers in a blackbox log for
analyze_wind_z_blackbox.py (or manual inspection) to read out.

--------------------------------------------------------------------------
Prerequisites (see this directory's README.md for the full sequence):
  1. Build SITL from the PR #11855 branch.
  2. Start SITL.elf (binds tcp:127.0.0.1:5760).
  3. Run provision_wind_z_sign_test.py once, then restart SITL.elf.
  4. Run this script: python3 wind_z_sign_test.py
--------------------------------------------------------------------------

Ground-truth conventions used by this script (verified independently, not
assumed from wind_estimator.c's own algebra -- see the notes doc):
  - JSBSim `attitude/theta-deg` (pitch): standard aviation convention,
    POSITIVE = nose up = climbing. This script uses this (not the FC's own
    attitude.pitch estimate) as the authoritative "climb vs dive" reference
    for interpreting results, because a past investigation on this project
    found the FC's *estimated* attitude.values.pitch is the opposite sign
    (io/osd.c: pitch > 0 draws SYM_PITCH_DOWN) -- exactly the kind of sign
    confusion this test exists to avoid propagating.
  - JSBSim `atmosphere/wind-down-fps`: NED convention, POSITIVE = downdraft
    (air mass moving downward). Verified standalone 2026-09-06: commanding
    wind-down-fps=+10 made velocities/h-dot-fps go negative (aircraft pushed
    into a descent) -- physically consistent with "positive = downdraft".

Interpretation guide (also printed at the end of the run, and by
analyze_wind_z_blackbox.py):
  A downdraft is, physically, air moving in the +Z-down direction. If the
  firmware's raw wind[Z] estimate comes out POSITIVE during the downdraft
  phases, its native convention is NED (Z-down-positive) -- meaning
  rth_estimator.c/osd.c's `-getEstimatedWindSpeed(Z) // from NED to NEU`
  negation is still doing the correct conversion. If it comes out NEGATIVE,
  the convention has become NEU (Z-up-positive) -- meaning that same
  negation now flips a NEU value back to a NED-looking one while believing
  it is doing the opposite, i.e. the suspected regression is real.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

BENCH_DIR = os.path.expanduser("~/inavflight/inav-sitl-bench")
if not os.path.isdir(BENCH_DIR):
    print(f"ERROR: inav-sitl-bench not found at {BENCH_DIR}")
    print("This script reuses its msp.py/hitl.py/jsbsim_plant.py -- see the "
          "jsbsim-sitl-testing skill for setup instructions.")
    sys.exit(1)
sys.path.insert(0, BENCH_DIR)

try:
    from msp import MspClient
    from hitl import sim_step
    from jsbsim_plant import JSBSimPlant
    # Reuse the proven boot-calibration/arming-flags helpers rather than
    # re-deriving them (see jsbsim_fly.py, which uses the same pattern).
    from bench import wait_boot_calibration, arming_flags, FLAG_ARMED, FLAG_SENSORS_CALIBRATING
except ImportError as e:
    print(f"ERROR: failed to import inav-sitl-bench modules: {e}")
    print(f"Checked: {BENCH_DIR}")
    sys.exit(1)

RC_LOW, RC_MID, RC_HIGH = 1000, 1500, 2000
# RC layout matches provision_wind_z_sign_test.py: AETR + ARM(AUX1) + ANGLE(AUX2)
CH_ROLL, CH_PITCH, CH_THROTTLE, CH_YAW, CH_ARM, CH_ANGLE = 0, 1, 2, 3, 4, 5

FT2M = 0.3048
DT = 0.001   # fixed integration/coupling step -- see jsbsim_plant.py's warning
             # that coarser steps (>10ms) blow up numerically. Matches the
             # proven 1kHz coupling rate from jsbsim_fly.py.


def rc_ch(thr=RC_LOW, arm=RC_LOW, angle=RC_LOW, ele=RC_MID, ail=RC_MID, rud=RC_MID):
    return [ail, ele, thr, rud, arm, angle, RC_MID, RC_MID]


class Recorder:
    """Collects the phase-timing sidecar (for analyze_wind_z_blackbox.py) and
    a full CSV trace of the flight (for manual cross-checking without
    needing to decode blackbox at all)."""

    def __init__(self, csv_path: str, phases_path: str):
        self.csv_path = csv_path
        self.phases_path = phases_path
        self._csv = open(csv_path, "w")
        self._csv.write("t,phase,wind_down_fps,fc_pitch_deg_estimate,js_pitch_deg_truth,"
                         "js_hdot_fps,gps_vd_cms_injected,ele_rc,armed\n")
        self.phases = []
        self.t0 = None

    def start_clock(self):
        self.t0 = time.time()

    def t(self):
        return 0.0 if self.t0 is None else time.time() - self.t0

    def mark_phase_start(self, label: str, wind_down_fps: float):
        entry = {"label": label, "t_start": round(self.t(), 3), "wind_down_fps": wind_down_fps}
        self.phases.append(entry)
        return entry

    def row(self, phase, wind_down_fps, fc_pitch, js_pitch, js_hdot_fps, gps_vd_cms, ele_rc, armed):
        self._csv.write(f"{self.t():.3f},{phase},{wind_down_fps:.2f},{fc_pitch:.2f},"
                         f"{js_pitch:.2f},{js_hdot_fps:.2f},{gps_vd_cms:.1f},{ele_rc},{int(armed)}\n")

    def finalize_phase(self, entry, js_pitch_deg_now, js_hdot_fps_now):
        entry["js_pitch_deg_at_end"] = round(js_pitch_deg_now, 2)
        entry["js_hdot_fps_at_end"] = round(js_hdot_fps_now, 2)

    def close(self):
        self._csv.close()
        with open(self.phases_path, "w") as f:
            json.dump(self.phases, f, indent=2)
        print(f"Wrote flight trace:   {self.csv_path}")
        print(f"Wrote phase sidecar:  {self.phases_path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5760)
    ap.add_argument("--wind-down-fps", type=float, default=12.0,
                     help="Steady downdraft magnitude to inject, NED wind-down-fps convention "
                          "(positive = downdraft). Default 12 fps (~3.66 m/s).")
    ap.add_argument("--pitch-hold-secs", type=float, default=6.0,
                     help="How long to hold each climb/dive elevator command "
                          "(must span multiple ~1Hz wind-estimator update cycles).")
    ap.add_argument("--repeats", type=int, default=2,
                     help="Number of climb/dive cycles per wind condition (zero-wind and downdraft).")
    ap.add_argument("--elevator-deflection", type=int, default=400,
                     help="RC elevator deflection from center (RC_MID +/- this) used to command "
                          "climb/dive in ANGLE mode. Default 400 (i.e. 1100/1900).")
    ap.add_argument("--outdir", default=".", help="Directory to write the CSV trace + phases JSON.")
    args = ap.parse_args()

    csv_path = os.path.join(args.outdir, "wind_z_sign_test_trace.csv")
    phases_path = os.path.join(args.outdir, "wind_z_sign_test_phases.json")
    rec = Recorder(csv_path, phases_path)

    # ---- Connection verification (mandatory: don't fail silently) --------
    print(f"Connecting to SITL at {args.host}:{args.port} ...")
    try:
        m = MspClient(host=args.host, port=args.port)
    except (ConnectionRefusedError, OSError) as e:
        print(f"FAILED to connect: {e}")
        print("Is SITL.elf running? Was it restarted after provision_wind_z_sign_test.py "
              "(EEPROM changes need a reboot)?")
        print("Note: if running in a sandbox, localhost TCP should be allowlisted; "
              "if it's still blocked, ask the user rather than disabling the sandbox.")
        sys.exit(1)

    try:
        api = m.api_version()
    except Exception as e:
        print(f"FAILED: SITL did not respond to MSP_API_VERSION: {e}")
        sys.exit(1)
    print(f"Connected. MSP API version: {api}")

    try:
        flags = arming_flags(m)
    except Exception as e:
        print(f"FAILED: could not read arming flags via MSP2_INAV_STATUS: {e}")
        print("Was provision_wind_z_sign_test.py run and SITL restarted afterward?")
        sys.exit(1)
    print(f"Initial arming flags: 0x{flags:08X}")

    plant = JSBSimPlant(model="c172p", alt_ft=1500, kts=60)

    def loop(secs, phase_label, rc, wind_down_fps=0.0, freeze=False, print_every=1.0):
        """Advance the sim `secs` seconds at fixed 1kHz coupling, streaming
        MSP_SIMULATOR each step. GPS is injected every step once we're past
        the freeze/settle/arm phases (freeze=False) -- required for the wind
        estimator's gating (isGPSHeadingValid/validVelNE/validVelD)."""
        last_print = 0.0
        t_end = time.time() + secs
        r = None
        while time.time() < t_end:
            it0 = time.perf_counter()
            gps = None if freeze else plant.gps()
            r = sim_step(m, plant.acc_mg(), plant.gyro_dps16(), rc, baro_pa=plant.baro_pa(), gps=gps)
            if freeze:
                plant._a_earth = (0.0, 0.0, 0.0)
            else:
                plant.set_controls(r.stab_roll, r.stab_pitch, r.stab_yaw, (r.stab_throttle + 1.0) / 2.0)
                plant.step(dt=DT)
            js_r, js_p, js_y = plant.rpy()
            js_hdot_fps = plant.fdm["velocities/h-dot-fps"]
            gps_vd_cms = plant.gps()["vel_ned_cms"][2] if not freeze else 0.0
            if time.time() - last_print > print_every:
                print(f"  [{phase_label:24s}] t={rec.t():6.1f}s  FC pitch~{r.att_pitch_deg:+6.1f}  "
                      f"JS pitch {js_p:+6.1f}  hdot {js_hdot_fps:+6.1f}fps  wind_down {wind_down_fps:+5.1f}fps  "
                      f"armed={r.armed}")
                last_print = time.time()
            rec.row(phase_label, wind_down_fps, r.att_pitch_deg, js_p, js_hdot_fps, gps_vd_cms,
                     rc[CH_PITCH], r.armed)
            # hold the fixed 1ms slot
            while True:
                rem = DT - (time.perf_counter() - it0)
                if rem <= 0:
                    break
                if rem > 0.002:
                    time.sleep(rem - 0.002)
        return r

    def run_phase(secs, label, rc, wind_down_fps=0.0, freeze=False, print_every=1.0):
        entry = rec.mark_phase_start(label, wind_down_fps)
        r = loop(secs, label, rc, wind_down_fps=wind_down_fps, freeze=freeze, print_every=print_every)
        js_r, js_p, js_y = plant.rpy()
        rec.finalize_phase(entry, js_p, plant.fdm["velocities/h-dot-fps"])
        return r

    # ---- Boot calibration ---------------------------------------------------
    print("\n=== Waiting for boot gyro calibration to clear ===")
    try:
        wait_boot_calibration(m)
    except TimeoutError as e:
        print(f"FAILED: {e}")
        print("Check: did SITL actually restart after provisioning? Is another process "
              "already talking MSP to this port (e.g. a leftover configurator/test session)?")
        sys.exit(1)
    print("Boot calibration cleared.")

    rec.start_clock()

    # ---- Settle AHRS against the static JSBSim IC (plant frozen) ----------
    print("\n=== SETTLE (AHRS converges to JSBSim's static IC) ===")
    run_phase(6, "settle", rc_ch(), freeze=True)

    # ---- Confirm calibration really is clear, then arm ---------------------
    print("\n=== ARM ===")
    t_end = time.time() + 20
    armed = False
    while time.time() < t_end and not armed:
        run_phase(1.0, "arm_low", rc_ch(thr=RC_LOW, arm=RC_LOW, angle=RC_HIGH), freeze=True, print_every=5)
        r = run_phase(1.2, "arm_high", rc_ch(thr=RC_LOW, arm=RC_HIGH, angle=RC_HIGH), freeze=True, print_every=5)
        armed = bool(arming_flags(m) & FLAG_ARMED)
    if not armed:
        print(f"FAILED to arm within timeout. arming_flags=0x{arming_flags(m):08X}")
        print("Common causes: provisioning wasn't saved/rebooted, or a sensor/GPS "
              "arming blocker is still set (check MSP2_INAV_STATUS arming flags bit meanings).")
        rec.close()
        sys.exit(1)
    print(f"ARMED. arming_flags=0x{arming_flags(m):08X}")

    # From here on, plant is released from the frozen IC and GPS is injected
    # every step (required for the wind estimator's gating).
    print("\n=== LEVEL (release from frozen IC, let cruise + AHRS settle) ===")
    run_phase(6, "level_settle", rc_ch(thr=1650, arm=RC_HIGH, angle=RC_HIGH), print_every=2)

    # ---- Phase 1: zero-wind pitch maneuvers (secondary sanity check) ------
    # Prediction (does NOT resolve the NED/NEU sign question by itself, see
    # notes doc section 4): with true wind = 0, estimatedWind[Z] should stay
    # near 0 regardless of which convention is in play, since 0 == -0.
    print(f"\n=== ZERO-WIND PITCH MANEUVERS ({args.repeats}x climb/dive, wind=0) ===")
    ele_hi = RC_MID + args.elevator_deflection
    ele_lo = RC_MID - args.elevator_deflection
    for i in range(1, args.repeats + 1):
        run_phase(args.pitch_hold_secs, f"pitch_A_zero_wind_{i}",
                  rc_ch(thr=1650, arm=RC_HIGH, angle=RC_HIGH, ele=ele_hi), print_every=2)
        run_phase(args.pitch_hold_secs, f"pitch_B_zero_wind_{i}",
                  rc_ch(thr=1650, arm=RC_HIGH, angle=RC_HIGH, ele=ele_lo), print_every=2)
    run_phase(4, "level_between", rc_ch(thr=1650, arm=RC_HIGH, angle=RC_HIGH), print_every=2)

    # ---- Phase 2: inject known downdraft, let it propagate into steady ----
    # level flight before starting the pitch maneuver, so the airframe's
    # velocity has actually responded to the wind before we start changing
    # attitude (equations 10-12 need a real velocity difference to work with).
    print(f"\n=== INJECT DOWNDRAFT: wind-down-fps = +{args.wind_down_fps:.1f} "
          f"(NED convention, positive = downdraft) ===")
    plant.set_wind(down_ms=args.wind_down_fps * FT2M)
    run_phase(5, "downdraft_settle", rc_ch(thr=1650, arm=RC_HIGH, angle=RC_HIGH),
              wind_down_fps=args.wind_down_fps, print_every=2)

    print(f"\n=== DOWNDRAFT PITCH MANEUVERS ({args.repeats}x climb/dive, wind=+{args.wind_down_fps:.1f}fps) ===")
    for i in range(1, args.repeats + 1):
        run_phase(args.pitch_hold_secs, f"pitch_A_downdraft_{i}",
                  rc_ch(thr=1650, arm=RC_HIGH, angle=RC_HIGH, ele=ele_hi),
                  wind_down_fps=args.wind_down_fps, print_every=2)
        run_phase(args.pitch_hold_secs, f"pitch_B_downdraft_{i}",
                  rc_ch(thr=1650, arm=RC_HIGH, angle=RC_HIGH, ele=ele_lo),
                  wind_down_fps=args.wind_down_fps, print_every=2)

    print("\n=== RECOVER (wind off, wings level) ===")
    plant.set_wind()  # clears all wind components back to 0
    run_phase(4, "recover_level", rc_ch(thr=1650, arm=RC_HIGH, angle=RC_HIGH), print_every=2)

    print("\n=== DISARM ===")
    run_phase(2, "disarm", rc_ch(thr=RC_LOW, arm=RC_LOW, angle=RC_HIGH), print_every=2)
    # Give the SLOW state machine + blackbox a moment to flush/close the file
    # (BLACKBOX_STATE_SHUTTING_DOWN) before we exit the script.
    time.sleep(2.0)

    rec.close()
    m.close()

    print("\n" + "=" * 78)
    print("Flight complete. This script does NOT read blackbox itself.")
    print("Next steps:")
    print("  1. Find the newest .TXT blackbox log (SITL's cwd, or `ls -lt ~/*.TXT`).")
    print("  2. Run:")
    print(f"       python3 analyze_wind_z_blackbox.py <path-to-log>.TXT {phases_path}")
    print("  3. Read the sign of raw wind[2] during the 'pitch_*_downdraft_*' phases.")
    print("     A downdraft is air moving DOWNWARD (+Z in NED convention).")
    print("     raw wind[2] > 0 during downdraft  => firmware output is NED-native")
    print("       (rth_estimator.c/osd.c's '-getEstimatedWindSpeed(Z) // NED to NEU' is correct)")
    print("     raw wind[2] < 0 during downdraft  => firmware output has become NEU-native")
    print("       (that same negation now double-flips the sign -- confirms the suspected bug)")
    print("  Cross-check the 'pitch_*_zero_wind_*' phases: raw wind[2] there should stay")
    print("  small/near-zero regardless of which convention is in play (sanity check only,")
    print("  does not by itself answer the NED-vs-NEU question).")
    print("=" * 78)


if __name__ == "__main__":
    main()
