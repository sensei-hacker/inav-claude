#!/usr/bin/env python3
"""
analyze_wind_z_blackbox.py -- read out the raw wind[2] (Z-axis) blackbox
field per test phase, for the PR #11855 vertical-wind sign question.

Usage:
    python3 analyze_wind_z_blackbox.py <blackbox-log>.TXT wind_z_sign_test_phases.json
    python3 analyze_wind_z_blackbox.py <already-decoded>.01.csv wind_z_sign_test_phases.json

Decodes the raw blackbox .TXT (via blackbox_decode, if not already a .csv),
loads the "wind[2]" column (blackbox.c:1491/1503 --
slow->wind[i] = getEstimatedWindSpeed(i); the SAME raw value the estimator
computes internally, logged BEFORE any of the NED<->NEU conversions applied
by rth_estimator.c/osd.c), and prints its value across each phase of the
flight recorded by wind_z_sign_test.py's phases JSON sidecar.

This script does not decide the answer for you -- it prints the numbers and
a fixed interpretation guide (also printed by wind_z_sign_test.py at the end
of the flight) so a human can read the sign off directly.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys

BLACKBOX_DECODE_CANDIDATES = [
    os.path.expanduser("~/.local/bin/blackbox_decode"),
    "/usr/local/bin/blackbox_decode",
    "blackbox_decode",  # fall back to PATH
]


def find_blackbox_decode():
    for c in BLACKBOX_DECODE_CANDIDATES:
        if os.path.isabs(c) and os.path.exists(c):
            return c
    from shutil import which
    found = which("blackbox_decode")
    if found:
        return found
    return None


def decode_if_needed(log_path: str) -> str:
    if log_path.endswith(".csv"):
        if not os.path.exists(log_path):
            print(f"ERROR: {log_path} does not exist.")
            sys.exit(1)
        return log_path

    if not os.path.exists(log_path):
        print(f"ERROR: blackbox log not found: {log_path}")
        print("Hint: check SITL's cwd for the newest *.TXT, or `ls -lt ~/*.TXT`.")
        sys.exit(1)

    decoder = find_blackbox_decode()
    if not decoder:
        print("ERROR: blackbox_decode not found (checked ~/.local/bin, /usr/local/bin, PATH).")
        print("Either install/build it, or decode the log yourself and pass the resulting .csv instead.")
        sys.exit(1)

    print(f"Decoding {log_path} with {decoder} ...")
    result = subprocess.run([decoder, log_path], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("ERROR: blackbox_decode failed:")
        print(result.stderr)
        sys.exit(1)

    stem = os.path.splitext(os.path.basename(log_path))[0]
    directory = os.path.dirname(os.path.abspath(log_path)) or "."
    candidates = sorted(
        (f for f in os.listdir(directory) if f.startswith(stem) and f.endswith(".csv")),
        key=lambda f: os.path.getmtime(os.path.join(directory, f)),
        reverse=True,
    )
    if not candidates:
        print(f"ERROR: blackbox_decode ran but no <stem>*.csv was found next to {log_path}.")
        print(f"Files in {directory}: {os.listdir(directory)}")
        sys.exit(1)
    csv_path = os.path.join(directory, candidates[0])
    print(f"Using decoded CSV: {csv_path}")
    return csv_path


def load_wind_z_series(csv_path: str):
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            print(f"ERROR: {csv_path} has no header row -- is this really a decoded blackbox CSV?")
            sys.exit(1)
        fieldnames = [n.strip() for n in reader.fieldnames]
        time_col = next((c for c in fieldnames if c.strip().lower().startswith("time")), None)
        wind_col = next((c for c in fieldnames if c.strip() == "wind[2]"), None)
        if time_col is None or wind_col is None:
            print("ERROR: expected columns 'time (us)' and 'wind[2]' not found in decoded CSV.")
            print(f"Columns present: {fieldnames}")
            print("Hint: was FEATURE_BLACKBOX enabled and blackbox_device=FILE during the flight? "
                  "(see provision_wind_z_sign_test.py). 'wind[2]' is only present in newer INAV "
                  "builds -- confirm the PR #11855 branch was actually what was flashed/built.")
            sys.exit(1)
        rows = []
        for raw_row in reader:
            row = {k.strip(): v for k, v in raw_row.items()}
            try:
                t_s = float(row[time_col]) / 1e6
                wz = float(row[wind_col])
            except (TypeError, ValueError, KeyError):
                continue
            rows.append((t_s, wz))
    if not rows:
        print(f"ERROR: {csv_path} decoded but contained no usable data rows.")
        print("The flight may never have armed, or blackbox logging never started.")
        sys.exit(1)
    return rows


def summarize_phase(rows, t_start, t_end, label):
    vals = [(t, wz) for (t, wz) in rows if t_start <= t < t_end]
    if not vals:
        print(f"  {label:26s}: NO SAMPLES in blackbox time [{t_start:7.1f}, {t_end:7.1f})s")
        print(f"    (the 'wind' slow-frame field is only re-logged when its value CHANGES --")
        print(f"     see blackbox.c writeSlowFrameIfNeeded() -- so a flat/unchanged phase can")
        print(f"     legitimately have zero new samples if the estimator never produced a fresh")
        print(f"     update in this window. Check the phases JSON's js_pitch_deg_at_end / ")
        print(f"     js_hdot_fps_at_end to confirm the maneuver actually happened as intended.)")
        return None
    wz_vals = [wz for (_, wz) in vals]
    print(f"  {label:26s}: n={len(vals):3d}  first={wz_vals[0]:+9.1f}  last={wz_vals[-1]:+9.1f}  "
          f"min={min(wz_vals):+9.1f}  max={max(wz_vals):+9.1f}   (raw wind[2], cm/s, unconverted)")
    return wz_vals[-1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("blackbox_log", help="Path to a SITL .TXT blackbox log, or an already-decoded .csv")
    ap.add_argument("phases_json", help="Phase-timing sidecar written by wind_z_sign_test.py")
    args = ap.parse_args()

    if not os.path.exists(args.phases_json):
        print(f"ERROR: phases JSON not found: {args.phases_json}")
        sys.exit(1)
    with open(args.phases_json) as f:
        phases = json.load(f)
    if not phases:
        print(f"ERROR: {args.phases_json} is empty -- did wind_z_sign_test.py actually run to completion?")
        sys.exit(1)

    csv_path = decode_if_needed(args.blackbox_log)
    rows = load_wind_z_series(csv_path)
    print(f"Loaded {len(rows)} wind[2] samples spanning "
          f"[{rows[0][0]:.1f}, {rows[-1][0]:.1f}]s of blackbox time.\n")

    print("=" * 88)
    print("Raw wind[2] (Z-axis) per phase -- BEFORE any NED<->NEU conversion")
    print("(see blackbox.c:1491 slow->wind[i]=getEstimatedWindSpeed(i); wind_estimator.c)")
    print("=" * 88)

    last_by_label = {}
    downdraft_labels, zero_wind_labels = [], []
    for i, ph in enumerate(phases):
        t_start = ph["t_start"]
        t_end = phases[i + 1]["t_start"] if i + 1 < len(phases) else rows[-1][0] + 1.0
        js_pitch = ph.get("js_pitch_deg_at_end")
        extra = f"  [JSBSim pitch at phase end: {js_pitch:+.1f} deg, +=nose-up/climb]" if js_pitch is not None else ""
        print(f"\n{ph['label']} (wind_down_fps={ph.get('wind_down_fps', 0):+.1f}){extra}")
        last_by_label[ph["label"]] = summarize_phase(rows, t_start, t_end, ph["label"])
        if "downdraft" in ph["label"]:
            downdraft_labels.append(ph["label"])
        elif "zero_wind" in ph["label"]:
            zero_wind_labels.append(ph["label"])

    print("\n" + "=" * 88)
    print("INTERPRETATION GUIDE")
    print("=" * 88)
    print("""
A downdraft is, physically, air moving DOWNWARD -- that is +Z in the
standard NED (North-East-Down) earth-frame convention.

Look at the 'last'/'min'/'max' raw wind[2] values printed above for the
phases containing 'downdraft' in their label (listed below). Ignore the
'zero_wind' phases for this part -- they only confirm the harness/maneuver
works (estimate should stay near 0 there), they do not carry the sign
information by themselves.
""")
    print(f"Downdraft-phase labels found: {downdraft_labels or '(none -- did the flight reach this phase?)'}")
    print(f"Zero-wind-phase labels found: {zero_wind_labels or '(none -- did the flight reach this phase?)'}")
    print("""
  * If raw wind[2] comes out POSITIVE during the downdraft phases:
      -> getEstimatedWindSpeed(Z)'s native convention is NED (Z-down-positive).
      -> rth_estimator.c:156 and osd.c:3768's
             "-getEstimatedWindSpeed(Z) // from NED to NEU"
         are doing a correct conversion. PR #11855 did NOT introduce a sign
         regression in these two consumers.

  * If raw wind[2] comes out NEGATIVE during the downdraft phases:
      -> getEstimatedWindSpeed(Z)'s native convention has become NEU
         (Z-up-positive).
      -> That same "-getEstimatedWindSpeed(Z) // from NED to NEU" negation
         now takes an already-NEU value and flips it AGAIN, producing a
         sign-inverted vertical wind speed in RTH glide-distance planning
         and the OSD vertical-wind indicator. This confirms the suspected
         regression from the notes doc.

Cross-check with the zero-wind phases: their raw wind[2] should stay small
(near 0, some residual/noise is expected -- this is a real filtered estimate,
not a perfect zero) regardless of which convention is in play. If the
zero-wind phases show a LARGE persistent nonzero value, treat that as a
harness problem (maneuver too weak to clear the diffLengthSq > 0.2^2 gate,
GPS gating not satisfied, etc.) and re-run with --pitch-hold-secs or
--elevator-deflection increased before trusting the downdraft-phase readout.

sensors/pitotmeter.c:339's getWindEstimatedVirtualAirspeed() consumer is not
covered by this test's interpretation above (it has no explicit NED/NEU
comment and was flagged in the notes doc as needing its own check of
posControl.actualState.abs.vel.z's convention) -- out of scope here.
""")


if __name__ == "__main__":
    main()
