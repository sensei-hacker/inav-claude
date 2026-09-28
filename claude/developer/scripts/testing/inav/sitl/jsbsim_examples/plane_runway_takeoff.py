#!/usr/bin/env python3
"""Example: a Cessna 172 takes off from a runway, climbs out and levels off.

    python3 examples/plane_runway_takeoff.py /path/to/inav/build_sitl/bin/SITL.elf

This script is the pilot. Everything up to level-off is flown in ACRO: while
the plane accelerates, INAV's pitch estimate reads high (about 12 deg by
rotation speed), so ANGLE would hold the wrong attitude -- this may now be
fixed by the GPS3Dspeed turn-rate-acceleration filter fix merged into
maintenance-10.x (imuCalculateTurnRateacceleration() in src/main/flight/imu.c
was only reapplying that filter when a new GPS heartbeat arrived instead of
every IMU loop tick, giving it the wrong time constant during acceleration --
see PR https://github.com/iNavFlight/inav/pull/12055). Re-verify against
current mainline before assuming ACRO is still required here. The pilot keeps
the centreline with rudder (which also steers the nosewheel), rotates at 55
kts, climbs at 8 deg nose up, levels off and lets the speed settle, then hands
over to ANGLE + NAV ALTHOLD.

Prints the flight once a second and writes it to plane_runway_takeoff.csv.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inavbench import Bench

RUNWAY_HEADING = 0.0    # the plane starts on the centreline, facing north
ROTATE_KTS = 55
CLIMB_PITCH = 8.0       # degrees, nose up
LEVEL_OFF_M = 150


def clamp(v, lim=1.0):
    return max(-lim, min(lim, v))


def heading_error(b):
    return (RUNWAY_HEADING - b.truth()["yaw"] + 180.0) % 360.0 - 180.0


def report(b, phase):
    t = b.truth()
    alt, _ = b.altitude()
    modes = ", ".join(sorted(b.active_modes() - {"ARM"})) or "-"
    print(f"{b.elapsed:5.0f}s  {phase:<9} {t['ias_kts']:5.1f} kts  height {t['agl_m']:6.1f} m (FC {alt:6.1f})  "
          f"along runway {t['north_m']:6.0f} m, off centreline {t['east_m']:+5.1f} m  "
          f"heading {t['yaw']:5.1f}  pitch {t['pitch']:+5.1f} (FC {b.fc.pitch:+5.1f})  [{modes}]")


def pilot(b, phase, until, pitch_target=CLIMB_PITCH, seconds=120.0):
    """Fly `phase` by hand at 20 Hz until `until(b)` is true."""
    next_report = b.elapsed
    end = b.elapsed + seconds
    while not until(b):
        if b.elapsed > end:
            raise RuntimeError(f"{phase} did not finish within {seconds:.0f} s")
        t = b.truth()
        # rudder and nosewheel hold the centreline: heading plus a little for sideways drift
        yaw = clamp(0.06 * heading_error(b) - 0.05 * t["east_m"], 0.8)
        roll = clamp(-0.04 * t["roll"], 0.5)                     # wings level
        if phase == "roll":
            pitch = 0.0
        else:                                                    # pitch stick back is negative
            pitch = clamp(-0.06 * (pitch_target - t["pitch"]), 0.6)
        b.sticks(roll=roll, pitch=pitch, yaw=yaw)
        b.run(0.05)
        if b.elapsed >= next_report:
            report(b, phase)
            next_report += 1.0


def takeoff(b, level_off_m):
    """Runway takeoff in ACRO, climb, then level off near level_off_m and let the speed settle.
    Needs a ground start."""
    report(b, "lined up")
    b.mode("ANGLE", on=False)            # no mode on = ACRO
    b.arm()
    b.sticks(throttle=1.0)

    pilot(b, "roll", until=lambda b: b.truth()["ias_kts"] >= ROTATE_KTS)
    pilot(b, "rotate", until=lambda b: b.truth()["agl_m"] > 1.33 + 3)       # 1.33 m is the gear height
    print(f"--- airborne {b.truth()['north_m']:.0f} m down the runway")
    pilot(b, "climb", until=lambda b: b.truth()["agl_m"] > level_off_m)

    b.sticks(throttle=0.7)
    level_until = b.elapsed + 8
    pilot(b, "level off", pitch_target=2.0, until=lambda b: b.elapsed > level_until)
    b.sticks(roll=0, pitch=0, yaw=0)


if __name__ == "__main__":
    with Bench("plane", sitl=sys.argv[1], airborne=False, heading_deg=RUNWAY_HEADING,
               log="plane_runway_takeoff.csv") as b:
        takeoff(b, LEVEL_OFF_M)
        b.mode("ANGLE")
        b.mode("NAV ALTHOLD")
        for _ in range(15):
            b.run(1)
            report(b, "ALTHOLD")

    print("flight log: plane_runway_takeoff.csv")
