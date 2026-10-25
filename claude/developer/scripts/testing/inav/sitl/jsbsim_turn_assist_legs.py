#!/usr/bin/env python3
"""Fly INAV SITL (JSBSim Cessna 172 via inavbench) in ANGLE + TURN ASSIST through
three banked-turn legs (level / climbing / diving) and compare the measured
earth-frame heading rate to g*tan(bank)/V (V = true airspeed from JSBSim).

Run (needs the inavbench venv, jsbsim 1.3.1):
  cd ~/inavflight/Inav_jsbsim
  PYTHONPATH=. .venv/bin/python <this file> /path/to/SITL.elf [--port 5760] [--leg-s 14] [--bb-dir DIR]

Exit code 1 if a leg diverges/stalls/loses the bank, or the bench fails.
Writes per-leg CSV (t,roll,pitch,hdg,rate,tas,beta,ay,...) to --out (default ./turn_assist_legs.csv).
"""
import argparse, math, os, sys, csv
sys.path.insert(0, os.path.expanduser("~/inavflight/Inav_jsbsim"))
from inavbench import Bench

G = 9.80665
KT = 0.514444
clamp = lambda v, l=1.0: max(-l, min(l, v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sitl")
    ap.add_argument("--port", type=int, default=5760)
    ap.add_argument("--leg-s", type=float, default=14.0)
    ap.add_argument("--bank", type=float, default=30.0, help="target bank angle, deg (pilot closes on it with the roll stick)")
    ap.add_argument("--out", default="turn_assist_legs.csv")
    ap.add_argument("--bb-dir", default=None, help="keep SITL workdir here (blackbox FILE device output lands there)")
    ap.add_argument("--no-turn-assist", action="store_true", help="control run: ANGLE without TURN ASSIST")
    ap.add_argument("--cli", action="append", default=[], help="extra INAV CLI line (repeatable), e.g. \"set fw_turn_assist_yaw_gain = 0\"")
    a = ap.parse_args()

    if not os.path.isfile(a.sitl):
        print(f"FAIL: SITL binary not found: {a.sitl}"); return 1
    cli = (["aux 6 35 1 1300 2100"] if not a.no_turn_assist else []) + [   # TURN ASSIST on AUX2 (same switch as ANGLE)
           "feature BLACKBOX", "set blackbox_device = FILE", "set blackbox_rate_denom = 1",
           "set blackbox_rate_num = 1"] + a.cli
    if a.bb_dir:
        a.bb_dir = os.path.abspath(a.bb_dir); os.makedirs(a.bb_dir, exist_ok=True)
    rows = []
    results = []
    fails = 0
    with Bench("plane", sitl=a.sitl, port=a.port, pitot=True, alt_m=1800, speed_kts=70,
               heading_deg=0, cli=cli, workdir=a.bb_dir) as b:
        b.release()
        f = b.plant.fdm
        print("airborne bench up; arming")
        b.sticks(throttle=0.6)
        b.arm()
        b.mode("ANGLE")
        if not a.no_turn_assist:
            b.mode("TURN ASSIST")
        b.run(0.5)
        modes = b.active_modes()
        print("active modes:", sorted(modes))
        if "ANGLE" not in modes or (not a.no_turn_assist and "TURN ASSIST" not in modes):
            print("FAIL: required modes not active"); return 1

        integ = [0.0]; thr_i = [0.6]

        state = dict(roll_i=0.0, pit_i=0.0)
        PRE = {"level": 6, "climb": 6, "dive": 10}
        KTS = {"level": 65, "climb": 65, "dive": 65}   # dive leg: throttle idle (no speed loop), speed builds
        FF = {"level": 0.55, "climb": 0.95, "dive": 0.0, "trim": 0.55}

        def fly(label, pitch_tgt, secs, bank_tgt, log, thr_ff=0.55, tgt_kts=65):
            """20 Hz pilot. Roll stick: P+I on true bank toward bank_tgt (closes on 30 deg).
            Pitch stick: P+I on true pitch. Throttle: leg feed-forward + P on IAS. Tune the PILOT, not the FC."""
            t_end = b.elapsed + secs
            while b.elapsed < t_end:
                t = b.truth()
                perr = pitch_tgt - t["pitch"]
                state["pit_i"] = clamp(state["pit_i"] + 0.01 * perr * 0.05, 0.8)
                b.sticks(pitch=clamp(-(0.05 * perr + state["pit_i"])))
                rerr = bank_tgt - t["roll"]
                state["roll_i"] = clamp(state["roll_i"] + 0.01 * rerr * 0.05, 0.8)
                b.sticks(roll=clamp(0.04 * rerr + state["roll_i"]))
                b.sticks(throttle=max(0.0, min(1.0, thr_ff + (0.03 if label.startswith("dive") is False else 0.0) * (tgt_kts - t["ias_kts"]))))
                b.run(0.05)
                if log is not None:
                    log.append(dict(
                        leg=label, t=b.elapsed, roll=t["roll"], pitch=t["pitch"], hdg=t["yaw"], ias=t["ias_kts"],
                        tas=f["velocities/vt-fps"] * 0.3048, beta=f["aero/beta-deg"], alpha=f["aero/alpha-deg"],
                        ay=f["accelerations/Ny"], p=f["velocities/p-rad_sec"], q=f["velocities/q-rad_sec"], r=f["velocities/r-rad_sec"],
                        agl=t["agl_m"], thr=b.rc[2], stick_p=b.rc[1], stick_r=b.rc[0], fc_roll=b.fc.roll, fc_pitch=b.fc.pitch))

        # trim straight and level first
        fly("trim", 0, 6, 0.0, None)

        for label, ptgt in (("level", 0.0), ("climb", 17.0), ("dive", -15.0)):
            state["pit_i"] = 0.0; state["roll_i"] = 0.0
            log = []
            ff = FF[label]
            # entry: wings level, establish pitch attitude, then roll into the turn and let it settle
            fly(label + "_pre", ptgt, PRE[label], 0.0, None, ff, KTS[label])
            fly(label + "_roll", ptgt, 8, a.bank, None, ff, KTS[label])
            fly(label, ptgt, a.leg_s, a.bank, log, ff, KTS[label])
            # analysis
            n = len(log)
            if n < 20:
                print(f"FAIL {label}: too few samples"); fails += 1; continue
            # unwrapped heading
            hd = [log[0]["hdg"]]
            for r in log[1:]:
                d = (r["hdg"] - hd[-1] + 180) % 360 - 180
                hd.append(hd[-1] + d)
            dt = log[-1]["t"] - log[0]["t"]
            meas = (hd[-1] - hd[0]) / dt                               # deg/s, +ve = right turn
            mean = lambda k: sum(r[k] for r in log) / n
            sd = lambda k: math.sqrt(sum((r[k] - mean(k)) ** 2 for r in log) / n)
            bank = mean("roll"); V = mean("tas")
            # roll stick right -> positive roll truth? use signed bank
            expected = math.degrees(G * math.tan(math.radians(bank)) / V)
            # p-p heading-rate ripple over 1 s windows
            ok = True; why = []
            if abs(bank) < 20: ok = False; why.append("bank not held")
            if sd("roll") > 4: ok = False; why.append("roll oscillation")
            if sd("pitch") > 4: ok = False; why.append("pitch oscillation")
            if mean("ias") < 45 or min(r["ias"] for r in log) < 40: ok = False; why.append("slow/stall")
            if max(abs(r["beta"]) for r in log) > 15: ok = False; why.append("large sideslip")
            if abs(meas) < 0.5 * abs(expected): ok = False; why.append("turn rate far from expected")
            res = dict(leg=label, bank=bank, pitch=mean("pitch"), pitch_sd=sd("pitch"), roll_sd=sd("roll"), tas=V,
                       ias=mean("ias"), meas=meas, exp=expected, ratio=meas / expected if expected else float("nan"),
                       beta=mean("beta"), beta_max=max(abs(r["beta"]) for r in log), ay=mean("ay"),
                       alt_change=log[-1]["agl"] - log[0]["agl"], ok=ok, why=why)
            results.append(res)
            rows += log
            if not ok: fails += 1
        # disarm through the running loop
        b.disarm()
        print("armed after disarm:", b.fc.armed)

    keys = list(rows[0].keys()) if rows else []
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, keys); w.writeheader(); w.writerows(rows)
    print()
    print(f"{'leg':6} {'bank':>6} {'pitch':>6} {'IAS':>5} {'TAS m/s':>7} {'meas d/s':>8} {'g tan/V':>8} {'ratio':>6} {'beta':>6} {'|b|max':>6} {'ay g':>7} {'roll sd':>7} {'pit sd':>6} {'dAGL':>6} ok")
    for r in results:
        print(f"{r['leg']:6} {r['bank']:6.1f} {r['pitch']:6.1f} {r['ias']:5.1f} {r['tas']:7.1f} {r['meas']:8.2f} {r['exp']:8.2f} {r['ratio']:6.3f} {r['beta']:6.2f} {r['beta_max']:6.2f} {r['ay']:7.3f} {r['roll_sd']:7.2f} {r['pitch_sd']:6.2f} {r['alt_change']:6.0f} {'OK' if r['ok'] else 'FAIL '+','.join(r['why'])}")
    print("CSV:", os.path.abspath(a.out))
    return 1 if fails or len(results) < 3 else 0


if __name__ == "__main__":
    sys.exit(main())
