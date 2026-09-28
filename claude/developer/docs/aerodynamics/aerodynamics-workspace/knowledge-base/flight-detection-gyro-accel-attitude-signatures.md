# Flight-Detection Signatures: Gyro/Accel "Character", Attitude, and Other Sensors

**Topic:** Follow-up to the fixed-wing "is this plane genuinely flying during GPS loss"
consult (airspeed / IMU velocity / baro rate / gyro rate). Addresses a colleague's objection
that "low gyro rate = stable cruise" fails to distinguish a plane sitting on a table from a
plane in trimmed cruise, and asks whether the *character* of sensor noise (not just magnitude),
plus attitude and other sensors, can do better.

**Scope note (read first):** the 5th edition of Houghton & Carpenter is a fluid-mechanics /
aerodynamic-force-generation text (units/dimensions, aerofoil & wing theory, compressible flow,
boundary layers, propellers — confirmed against the full table of contents). It contains **no
flight-dynamics, stability-and-control, atmospheric-turbulence/gust-spectrum, or
attitude-dynamics chapter**. Everything below about gust/turbulence frequency content, dynamic
stability modes (phugoid/short period), bank-angle lift geometry, and IMU/AHRS signal
processing is general flight-mechanics / signal-processing reasoning, clearly flagged as such.
H&C is cited only where it supports the underlying force/lift/AoA facts.

---

## 1. Is "quiet gyro" alone able to distinguish "on a table" from "in cruise"?

**Colleague is correct — gyro-rate magnitude alone cannot discriminate the two states.** A
motionless, level airframe on a bench and a well-trimmed airframe in steady cruise are *both*,
by definition, near-zero-angular-rate states; that's what "trimmed" and "stationary" both mean
kinematically.

**A further correction worth folding into the written response:** the same failure applies to
raw accelerometer *magnitude*, not just gyro rate, and for a specific physical reason. In
**trimmed, unaccelerated, wings-level cruise**, lift very nearly equals weight, so the load
factor `n = L/W ≈ 1` and the body-Z accelerometer reads **~1 g**, essentially the same DC value
as a level aircraft sitting still on a bench (H&C's lift/weight force balance, §1.5.1, printed
p.26, and Eqn 1.45a, p.28, underlie why level, unaccelerated flight is a ~1 g equilibrium — this
is the same `n = L/W` relationship used in the companion note `banked-turn-altitude-loss.md`).
So neither "gyro is quiet" nor "accel reads ~1 g" is, by itself, discriminating — both states
produce both readings.

**What is a real physical difference is the AC/noise content superimposed on those DC values,
and, more powerfully, whether that noise correlates with commanded control-surface deflections:**

| State | Gyro/accel DC level | AC/noise content | Correlation with control output |
|---|---|---|---|
| On table, unpowered | ~0 deg/s, ~1 g | Sensor noise floor only (no aerodynamic input exists) | None — moving a control surface with no airflow produces no aerodynamic moment, so no correlated IMU response |
| On table/bench, motor running | ~0 deg/s, ~1 g plus periodic vibration | Narrowband, discrete tones at motor/prop rotation frequency and harmonics (comb spectrum) | None from control surfaces (still no airflow); vibration tracks motor RPM, not stick/AP input |
| Being hand-carried/handled | Large, irregular excursions | Broadband, low-frequency (~0.5–3 Hz), non-stationary, bounded episode (starts/stops with pick-up/carry) | None — autopilot control-surface commands (if any) have no aerodynamic authority with no relative airflow, so IMU motion is decoupled from AP output |
| Genuine trimmed cruise | ~0 deg/s (mean), ~1 g (mean) | Continuous, statistically stationary, low-amplitude stochastic content from gust/turbulence response, plus motor/prop vibration if powered | Present — small AP trim/control corrections produce a delayed, sign-consistent aerodynamic response in gyro rate; this coupling has no analogue when the aircraft is stationary or hand-held |

The key, physically meaningful discriminator the colleague is reaching for is exactly this:
**not the size of the noise, but (a) its stationarity/persistence over many seconds, and (b)
whether it is causally coupled to commanded control-surface deflection.** A stationary or
carried aircraft cannot show that coupling because there is no relative airflow for the control
surfaces to act on; a flying aircraft's small corrective control inputs *always* produce a
correlated (if delayed and low-amplitude) aerodynamic moment. This causal-correlation test is a
stronger and more physically grounded criterion than any single sensor's raw magnitude or
variance, and it directly answers "how do you tell two 'quiet' states apart."

*(General flight-dynamics/signal-processing reasoning — not from H&C, which does not address
vehicle dynamic response, vibration, or control-surface aerodynamics in the trimmed/perturbed
sense used here.)*

---

## 2. Does gust/turbulence response have a characteristic frequency band distinct from human handling?

**General flight-dynamics/signal-processing reasoning throughout this section — H&C has no
turbulence-spectrum, gust-response, or dynamic-stability content to cite.**

- Atmospheric turbulence energy (as characterized in the standard Dryden/von Kármán gust models
  used in flight-dynamics work, not in H&C) is concentrated at large spatial length scales.
  Converted to a frequency band by dividing by a small FPV/fixed-wing's cruise speed
  (~10–25 m/s), the *forcing* input is mostly sub-1–2 Hz, with a falling tail at higher
  frequency. A small, light airframe's own **short-period pitch/gust-response mode** typically
  sits in roughly the 0.5–3 Hz range with moderate damping, so the aircraft's measured
  perturbation spectrum in calm-to-moderate turbulence is dominated by this same low-single-digit-Hz
  band, riding on top of whatever discrete motor/prop vibration tones exist (which are much
  higher frequency and tied to RPM, not turbulence).
- Human hand tremor (physiological, essentially always present when holding an object) sits
  around **8–12 Hz**, i.e. *above* the typical small-fixed-wing gust-response band. Deliberate
  hand/arm movement (walking to the launch point, adjusting grip, gesturing) is lower frequency,
  roughly **0.5–3 Hz**, but — importantly — this overlaps the same band as gust/short-period
  response, and it is larger in amplitude, irregular/non-stationary (bounded start-stop
  episodes, not a persistent stochastic process), and, per §1, uncorrelated with any control
  output.
- **Net assessment:** frequency content alone is not a clean separator, because deliberate
  handling motion and gust response occupy overlapping bands. Physiological tremor is a cleaner
  higher-frequency signature but is a weak/optional cue by itself. The separation that actually
  holds up physically is a **composite** of (a) amplitude/energy scale (handling excursions are
  typically much larger, tenths-of-g/tens-of-deg/s vs. hundredths-of-g/single-digit-deg/s in
  calm-air cruise), (b) persistence/stationarity over many seconds to minutes (turbulence
  response is a continuing stochastic process; handling is a bounded episode with a clear
  before/after), and (c) the control-correlation test from §1.
- **Feasibility on FC-grade MEMS IMUs:** typical MEMS gyro noise density is well below the
  amplitude of calm-air turbulence-band perturbations, so the raw signal-to-noise-floor is not
  the limiting factor — this is physically detectable in principle. However, running a true
  power-spectral-density (FFT) estimator on flight-controller-class hardware purely for this
  purpose is more complexity than the use case warrants. A **windowed variance/RMS estimate**
  (e.g., gyro and accel RMS over a rolling 0.5–2 s window, already cheap to compute) captures
  "sustained low-but-nonzero motion" without needing frequency decomposition, and is the
  pragmatic INAV-appropriate implementation — full PSD analysis would be overengineering
  relative to both the sensor noise floor and the decision this signal feeds.

---

## 3. Is attitude (pitch/roll, inverted) informative evidence of flight state?

**Yes for the typical INAV target airframe (long-range/FPV/cruise fixed-wing with nav/RTH
logic), no as a universal rule (3D/aerobatic aircraft genuinely sustain inverted/extreme
attitude for many seconds as normal operation).** Two distinct physical arguments support
treating sustained extreme attitude as an out-of-normal-envelope signal for the *non-aerobatic*
use case this flight-detection logic targets:

**(a) Lift-vector/bank-angle geometry (closely related to the existing
`banked-turn-altitude-loss.md` derivation).** Lift acts perpendicular to the flight direction/
relative wind (H&C §1.5.1, printed p.26, Fig. 1.7). The vertical component available to support
weight is `L·cos φ` for bank angle φ; at large bank this collapses (e.g., ~50% at 60°, ~0% at
90°). A conventional (non-3D, typically cambered-aerofoil) cruise/FPV wing does not have the
thrust-to-weight ratio or the (uncambered/symmetric) aerofoil section needed to sustain that
geometry, or to generate useful lift while inverted (an inverted cambered wing needs a much
larger, reversed-sense angle of attack relative to its designed camber to produce positive lift
at all — a condition normal cruise trim never approaches; see aerofoil-characteristics /
C_L–α discussion, H&C §1.5.9, printed pp.44–50). So for this class of airframe, **many seconds
of sustained large bank or inverted attitude is aerodynamically inconsistent with sustaining
altitude** — it is much more consistent with a spiral dive, spin, post-impact tumble, or the
airframe being carried/flipped by a person than with controlled cruise flight. *(The bank-angle
lift-fraction relationship itself is general flight-mechanics, following from H&C's stated
force geometry but not derived in H&C itself — same caveat as in the companion turn-loss note.)*

**(b) Nav/state-estimator validity, independent of literal aerodynamic possibility.** Even
if an extreme attitude were momentarily aerodynamically sustainable, INAV's position/altitude
estimator (accel/baro/GPS fusion, body-to-earth frame transforms, climb-rate integration) is
built around the small-perturbation, near-wings-level assumptions of normal cruise/climb/descent.
At extreme or inverted attitude those linearizations and frame conventions are no longer
trustworthy regardless of whether the wing is literally still producing lift. So, scoped to
"should the nav/RTH logic trust and act on its normal flight-state assumptions," sustained
extreme attitude is a reasonable disqualifying signal *for this estimator's purpose*, separate
from the stricter question of "is the aircraft aerodynamically airborne." *(General
flight-controller/estimator-design reasoning, not from H&C.)*

**Practical recommendation:** gate this on the *target airframe class* the flight-detection
logic is meant to serve (cruise/FPV/long-range nav missions), and treat it as a "don't trust
normal flight-mode logic in this attitude regime" flag rather than an absolute "not flying"
determination, so it does not misfire for genuinely different use cases (3D/aerobatic) that may
run different flight-mode logic entirely.

---

## 4. Other sensor-derived signals worth considering

| Signal | Physical rationale |
|---|---|
| **Magnetometer heading-rate vs. roll (turn coordination check)** | In a coordinated turn, `tan φ ≈ V·ψ̇/g`. Genuine flight produces heading changes consistent with the commanded/measured bank angle; a stationary or hand-spun airframe produces heading changes with no physically consistent bank-angle relationship (or none at all if truly still). Useful as a *corroborating* check only — magnetometer noise/EMI from nearby motors or bench ferrous objects limits it as a primary signal. |
| **ESC/motor RPM or current draw (powered aircraft)** | Confirms propulsion is engaged, but a bench-run motor produces similar basic telemetry, so by itself it is necessary but not sufficient. More informative: propeller thrust/torque depend on advance ratio `J = V/(nD)` (H&C Ch.9, blade-element and momentum theory, §9.2–9.4, printed pp.533–549), so the RPM-vs-current relationship at a given throttle differs measurably between static/zero-airflow (bench) operation and loaded forward-flight operation — a genuine, H&C-grounded physical discriminator for powered aircraft specifically. |
| **Accelerometer transient deviation from 1 g (as opposed to its DC magnitude, see §1)** | Sustained 1 g tells you nothing (both stationary and cruise read ~1 g), but characteristic *transients* — e.g., the sustained body-X acceleration signature of a hand or bungee launch — are already physically informative and already exploited elsewhere in INAV's launch-assist logic; the same transient-recognition approach (not steady-state magnitude) is the useful part of this signal. |
| **Airspeed-sensor (pitot) noise character** | A genuinely ventilated pitot in real airflow shows a nonzero mean IAS with small, bounded, persistent variance tied to turbulence; a stationary pitot exposed to ambient wind gusts shows near-zero mean with occasional non-sustained excursions. The same "sustained nonzero mean + bounded stationary variance" pattern used for gyro/accel in §1 applies here too, and avoids false positives from a stationary sensor catching a gust. |
| **Cross-consistency between baro climb rate and accel-derived vertical acceleration** | True climb/descent is smooth and consistent with double-integrating body-to-earth-frame vertical acceleration over the same window; bench/indoor baro noise (doors, HVAC, hand over the static port) is typically a single-shot transient uncorrelated with any accelerometer event. This cross-correlation is a stronger discriminator than a baro-rate threshold alone. |

---

## Summary for the written engineering response

1. Colleague's objection is correct: raw gyro (and accel) magnitude cannot distinguish
   "stationary/level" from "trimmed cruise" because both are, by construction, near-zero-rate,
   ~1 g states. The real discriminator is **noise character**: persistence/stationarity over
   many seconds, and — most powerfully — **causal correlation between small IMU perturbations
   and commanded control-surface deflection**, which can only exist when there is relative
   airflow for the surfaces to act on.
2. Gust/turbulence response and human handling motion occupy **overlapping**, not cleanly
   separated, frequency bands for a small fixed-wing (~0.5–3 Hz for both gust-response and
   deliberate handling); physiological tremor (~8–12 Hz) is a cleaner but weaker cue. A
   composite check (amplitude + persistence + control-correlation) is more robust than a
   frequency-band test alone, and a rolling-window variance/RMS estimator is the
   right-sized implementation for FC-grade hardware — full PSD/FFT would be overengineering.
3. Attitude is informative for the typical cruise/FPV/long-range fixed-wing this logic targets
   (sustained extreme bank or inverted attitude is aerodynamically inconsistent with sustaining
   altitude for that airframe class, and separately invalidates the nav estimator's small-
   perturbation assumptions), but is a **false indicator** for 3D/aerobatic aircraft that
   sustain such attitudes as normal operation — scope this check to the intended airframe class.
4. Additional worthwhile signals: turn-coordination cross-check via magnetometer heading-rate
   vs. roll (corroborating only); ESC RPM/current-vs-advance-ratio behavior for powered
   aircraft (H&C Ch.9); accelerometer *transient* signatures (e.g., launch) rather than steady
   magnitude; pitot noise-character check analogous to §1; and baro-vs-accel vertical-rate
   cross-correlation.

## References

- H&C §1.5.1, p.26 & Fig. 1.7, p.27 — lift direction relative to flight path/relative wind.
- H&C §1.5.2, Eqn 1.45a, p.28 — `L = C_L·½ρV²S`.
- H&C §1.5.9, pp.44–50 — aerofoil characteristics, C_L–α curve, stalling point.
- H&C Ch.9, §9.2–9.4, pp.533–549 — propeller thrust/torque coefficients, blade-element theory,
  dependence on advance ratio (basis for the RPM/current-vs-airflow-load discriminator).
- Related: `banked-turn-altitude-loss.md` (same lift/bank-angle geometry, load factor n = 1/cosφ).
- Dryden/von Kármán gust models, dynamic-stability short-period mode, and turn-coordination
  relation `tanφ ≈ Vψ̇/g` are standard flight-dynamics content (e.g., Etkin, *Dynamics of
  Flight*; Nelson, *Flight Stability and Automatic Control*) — **not** covered in H&C, and are
  used here as general engineering knowledge, flagged accordingly throughout.

## Limitations

- No quantitative sensor noise-floor numbers were pulled from a specific MEMS datasheet; the
  "detectable above noise floor" claim in §2 is a qualitative order-of-magnitude judgment, not a
  verified number for any specific FC IMU part.
- The gust-frequency-band and short-period natural-frequency figures are representative ranges
  for small/light fixed-wing airframes, not derived from first principles here; airframe mass,
  wing loading, and stiffness will shift them.
- The control-correlation test in §1 assumes the autopilot is actively commanding small trim
  corrections during the window under test; a fully hands-off, perfectly-trimmed glider in dead
  air could show weaker correlation and would rely more on §2's persistence/amplitude criteria.
