# JSBSim Example Scripts (External)

Sample scripts from other INAV developers' JSBSim test frameworks, kept here
for reference/reuse. These are a different framework than `inav-sitl-bench`
(`~/inavflight/inav-sitl-bench`, `swissembedded/inav-sitl-bench` — see the
`jsbsim-sitl-testing` skill) — don't mix the two; each has its own API and
support files. `inavbench` (`~/inavflight/Inav_jsbsim`) is the one with a
ready-made `Bench` class.

## `plane_runway_takeoff.py`

Source: https://github.com/xznhj8129/Inav_jsbsim/blob/master/examples/plane_runway_takeoff.py
(xznhj8129, also the author of `mspapi2`). Fetched 2026-09-28.

Cessna 172 runway takeoff -> climb -> level-off -> ANGLE + NAV ALTHOLD,
flown by hand in ACRO up to level-off. Depends on the `inavbench` package
(a `Bench` class), which is cloned at `~/inavflight/Inav_jsbsim`
(git-ignored, upstream `xznhj8129/Inav_jsbsim`).

### Running it

```bash
cd ~/inavflight/Inav_jsbsim
PYTHONPATH=. .venv/bin/python examples/plane_runway_takeoff.py <path to SITL.elf>
```

- Use the `.venv` there: the system jsbsim (1.2.3) is too old, `inavbench`
  needs `jsbsim>=1.3` (the venv has 1.3.1). If the clone or venv is missing:
  `git clone https://github.com/xznhj8129/Inav_jsbsim ~/inavflight/Inav_jsbsim`,
  `python3 -m venv --system-site-packages .venv`, `.venv/bin/pip install "jsbsim>=1.3"`.
- `Bench` starts and stops its own SITL from the `.elf` path you give it. Build
  it from the checkout under test with the inav-builder agent; don't use the
  sibling `inav/` build if another session holds its lock.
- `Bench(port=...)` sets SITL's first TCP port (default 5760; it uses one
  per UART, so space parallel benches 10 apart). Check `ps aux | grep SITL.elf`
  first: another session's SITL may already own 5760, so pass a free port.
- Smoke-tested 2026-10-03 against a SITL built from the
  `fix-fw-flight-detection-dead-reckoning` branch: arms, takes off, levels off
  and hands over to ANGLE + NAV ALTHOLD (about 80 s wall time, 74 s simulated).

### What `Bench` provides

`Bench(vehicle, sitl, port=, airborne=, pitot=, ...)`: `run()`, `arm()`,
`disarm()`, `sticks()`, `mode()`, `wind()`, `arming_flags()`,
`arming_blockers()`, `active_modes()`, `altitude()`, `airspeed()`,
`nav_status()`, `truth()` (JSBSim ground truth) and a per-run CSV log.
`airborne=False` starts on the ground, `pitot=True` configures a fake pitot,
baro is always sent, and `gps_fix = False` stops the GPS fix. Not provided:
degraded GPS (satellite count, phantom velocity; `hitl.pack` takes them, so
it's a small addition) and any view of INAV-internal state such as the
fixed-wing flight latch (use a debug mode or infer it from behavior).

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
