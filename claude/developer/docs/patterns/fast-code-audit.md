# FAST_CODE Candidate Audit

For each candidate, answer three questions before adding FAST_CODE:
1. **Rate** — is it called more often than the underlying data changes?
2. **Cache** — can an intermediate result be stored to avoid repeated work?
3. **Needed** — does it need to be called at all, or can the caller be restructured?

If the answer to Q1 or Q3 opens an optimization, do that *instead of* FAST_CODE.
If the function is tiny enough (~4 instrs), consider making it `static inline` in the
header — that eliminates both the veneer and the call overhead entirely.

---

## Already resolved

| Function | File | Resolution |
|---|---|---|
| `GPS3DspeedFiltered` / `calc_length_pythagorean_3D` | imu.c / maths.c | Moved into `imuCalculateTurnRateacceleration`, gated on GPS heartbeat (~10 Hz). Commit bb02220. |
| `getAxisRcCommand` | fc_core.c | RC data cached; now only called at ~50 Hz (when `isRXDataNew`). Caller `processPilotAndFailSafeActions` is not FAST_CODE — no veneer issue. |
| `failsafeShouldApplyControlInput` | failsafe.c | Caller (`processPilotAndFailSafeActions`) is not FAST_CODE. No veneer. Drop from list. |
| `sin_approx` / `cos_approx` | maths.c | Only callers are `imuMahonyAHRSupdate` and `imuUpdateEulerAngles`, neither FAST_CODE. No veneer. Drop from list. |
| `fast_fsqrtf` | maths.c | All hot-path callers audited: imu.c (FAST_CODE removed), mixer.c (`applyTurtleModeToMotors` — not FAST_CODE), servos.c (not FAST_CODE), navigation/sqrt_controller.c (not FAST_CODE), sensors/acceleration.c (not FAST_CODE). No FAST_CODE callers remain. Drop from list. |
| All imu.c functions below `taskMainPidLoop` | imu.c | `taskMainPidLoop` is NOT FAST_CODE (confirmed). All imu.c callees therefore have no veneer issue. Drop entire imu.c list. |
| `getPidSumLimit` | pid.c | Returns 400 or 500 based on `STATE(MULTIROTOR)` + axis — **constant during flight**. Precomputed in `pidInit()` loop, stored as `pidState[axis].pidSumLimit`. Hot-path calls replaced with struct field. Function kept for `pid_autotune.c` (not hot). No FAST_CODE needed. |

---

## Final verdicts — `pidController` callee chain — pid.c

`pidController` is FAST_CODE in HEAD. Its callees that are NOT yet FAST_CODE create
veneers. All run at the PID rate (1 kHz multirotor, configured rate fixed-wing).

| Function | Q1: Rate OK? | Q2: Cache? | Q3: Needed? | **Verdict** |
|---|---|---|---|---|
| `pTermProcess` | Gyro data changes every cycle — yes | No obvious cache | Yes | **FAST_CODE** |
| `dTermProcess` | Same | No | Yes | **FAST_CODE** |
| `applyItermLimiting` | Changes with error — yes | No | Yes | **FAST_CODE** |
| `pidApplySetpointRateLimiting` | Rate target changes each cycle | No | Yes | **FAST_CODE** |
| `checkItermLimitingActive` | Checks `STATE(ANTI_WINDUP)` + `mixerIsOutputSaturated()` — both cheap flag/register reads | No cache needed | Yes — sets per-axis bool used by iterm | **FAST_CODE** — body is cheap; no architectural optimization available |
| `checkItermFreezingActive` | Fixed-wing yaw only; checks bank angle from attitude struct | Bank angle changes every cycle in flight | Yes — only meaningful on PIFF + yaw axis | **FAST_CODE** — body is short; runs only for yaw on fixed-wing |
| `pidRcCommandToAngle` | RC only changes at ~50 Hz but function is tiny (constrain + scaleRangef) | Could gate on `isRXDataNew` but body is 2 ops — not worth the complexity | Yes | **FAST_CODE** — too small to benefit from gating; eliminates veneer |
| `pidRcCommandToRate` | Same as above | Same | Yes | **FAST_CODE** — same reasoning |

### `applySmithPredictor` — smith_predictor.c

Called from `pidController` (FAST_CODE) once per axis per PID cycle.

| Q1: Rate OK? | Q2: Cache? | Q3: Needed? | **Verdict** |
|---|---|---|---|
| Delay line must run each cycle on new gyro sample | No — delay line is inherently stateful | Only when `predictor->enabled` — already gated | **FAST_CODE** — confirms veneer from FAST_CODE caller |

### `pt1ComputeRC` — filter.c

Called from `pt1FilterApply4` (FAST_CODE) inside `if (!filter->RC)` guard.

| Q1: Rate OK? | Q2: Cache? | **Verdict** |
|---|---|---|
| Guard `if (!filter->RC)` means this runs only **once per filter instance** (first call) | Already effectively cached by the guard — `RC` is stored in the filter struct | **Keep `static FAST_CODE` as-is** — `static` means inlined by GCC anyway; no true veneer possible for static functions. Guard prevents repeated work. |

### `constrain` / `constrainf` / `scaleRangef` — maths.c

Called from multiple FAST_CODE pid.c functions (`pidRcCommandToAngle`, `pidRcCommandToRate`,
`pTermProcess`, `dTermProcess`, `applyItermLimiting`, etc.).

| Function | Body size | **Verdict** |
|---|---|---|
| `constrain` | 3 instrs | **FAST_CODE** — eliminates veneer from FAST_CODE callers. Candidate for `static inline` in maths.h (future refactor) which would also eliminate call overhead. |
| `constrainf` | 3 instrs | **FAST_CODE** — same reasoning |
| `scaleRangef` | ~6 instrs | **FAST_CODE** — larger body makes inline less attractive; FAST_CODE is the right choice |

---

## Functions removed from FAST_CODE (no FAST_CODE callers)

| Function | File | Reason |
|---|---|---|
| `sin_approx` | maths.c | Callers `imuMahonyAHRSupdate` and `imuUpdateEulerAngles` are not FAST_CODE |
| `cos_approx` | maths.c | Same |
| `fast_fsqrtf` | maths.c | No FAST_CODE callers — see "Already resolved" table above |
| `failsafeShouldApplyControlInput` | failsafe.c | Caller `processPilotAndFailSafeActions` is not FAST_CODE |

---

## Summary: what goes in each commit

### Commit A — "don't recompute" (algorithmic changes)
- `fc_core.c`: gate `getAxisRcCommand` / rcCommand processing on `isRXDataNew` (~50 Hz instead of PID rate)
- `pid.c`: add `pidState[axis].pidSumLimit`, set in `pidInit()`, replace 2 hot-path `getPidSumLimit()` calls

### Commit B — FAST_CODE additions
- `maths.c`: add FAST_CODE to `constrain`, `constrainf`, `scaleRangef`; remove from `sin_approx`, `cos_approx`, `fast_fsqrtf`
- `filter.c`: `pt1ComputeRC` already `static FAST_CODE` (no change needed)
- `smith_predictor.c`: `applySmithPredictor` already FAST_CODE (no change needed)
- `failsafe.c`: remove FAST_CODE from `failsafeShouldApplyControlInput`
- `pid.c`: add FAST_CODE to `pTermProcess`, `dTermProcess`, `applyItermLimiting`, `pidApplySetpointRateLimiting`, `checkItermLimitingActive`, `checkItermFreezingActive`, `pidRcCommandToAngle`, `pidRcCommandToRate`
- `fc_core.c`: add FAST_CODE to `getAxisRcCommand`
