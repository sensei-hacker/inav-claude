# JSBSim Example Scripts (External)

Sample scripts from other INAV developers' JSBSim test frameworks, kept here
for reference/reuse. These are a different framework than `inav-sitl-bench`
(`~/inavflight/inav-sitl-bench`, `swissembedded/inav-sitl-bench` — see the
`jsbsim-sitl-testing` skill) — don't mix the two; each has its own `Bench`
API and support files.

## `plane_runway_takeoff.py`

Source: https://github.com/xznhj8129/Inav_jsbsim/blob/master/examples/plane_runway_takeoff.py
(xznhj8129, also the author of `mspapi2`). Fetched 2026-09-28.

Cessna 172 runway takeoff -> climb -> level-off -> ANGLE + NAV ALTHOLD,
flown by hand in ACRO up to level-off. Depends on `inavbench.py` (a `Bench`
class) from the same upstream repo, not included here — fetch it from
`xznhj8129/Inav_jsbsim` before trying to run this script.

The script's docstring originally noted INAV's pitch estimate reads ~12 deg
high during the takeoff roll's acceleration, which is why it avoids ANGLE
mode until level-off. That symptom matches a bug fixed by
https://github.com/iNavFlight/inav/pull/12055 (merged into
`maintenance-10.x`): `imuCalculateTurnRateacceleration()` in
`src/main/flight/imu.c` was only reapplying the GPS3Dspeed turn-rate filter
when a new GPS heartbeat arrived instead of every IMU loop tick, giving it
the wrong time constant during acceleration. Noted in the script's docstring
as "may now be fixed" — re-verify against current mainline rather than
assuming the ACRO workaround is still required.
