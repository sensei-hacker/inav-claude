# Banked Turn Altitude Loss (Steady Coordinated Turn, Load Factor)

**Topic:** Why a fixed-wing model loses altitude when it banks hard in a tight loiter even while
still commanding its maximum nose-up pitch — and whether this is real aerodynamics or an
attitude-estimation artifact.

**INAV issue context:** iNavFlight/inav #11770 — 700 mm twin-motor elevon flying wing on an
autonomous waypoint mission. Climbs fine in straight flight at `nav_fw_climb_angle = 10°`.
Enters a waypoint "altitude adjustment" phase, banks up to `max_angle_inclination_rll = 35°`
to hold a tight loiter, still commands 10° nose-up, and loses altitude.

**Bottom line:** Expected aerodynamics. At a 35° bank the wing must produce **22% more lift**
than in wings-level flight *just to hold altitude* (and more to climb), while its vertical
lift component is reduced to **~82%** of what the same pitch gives wings-level. If the
nose-up pitch is already capped at 10°, the airframe cannot command that extra lift, so it
sinks. The accelerometer "gravity" bias in a sustained turn is a real secondary effect, but it
does not explain the altitude loss — the loss is a genuine lift shortfall.

---

## 1. How total lift splits in a steady banked turn (load factor n = 1/cos φ)

Houghton & Carpenter define **lift** as "the component of force acting upwards,
**perpendicular to the direction of flight**" (H&C §1.5.1, printed p.26), and their
**Fig. 1.7(d) "Banked circling flight"** (printed p.27) explicitly shows the lift vector tilting
away from the vertical when the aircraft banks, while the weight `W` remains vertical. This
vector geometry is the whole story:

In a steady, **level, coordinated turn** at bank angle φ:

- **Vertical component** of lift balances weight:  `L·cos φ = W`
- **Horizontal component** of lift supplies the centripetal force:  `L·sin φ = m·V²/r`

H&C invoke exactly this centripetal relation — "centripetal force = mass × centripetal
acceleration" and "centripetal acceleration is (velocity)²/radius" (H&C §3.3.11, printed
p.136; §5.2.3, printed p.221). Dividing the two force balances gives the load factor:

```
n = L / W = 1 / cos φ
```

and the required centripetal acceleration / turn rate:

```
L·sin φ = m·V²/r  →  tan φ = V²/(g·r)
```

**Load factor vs. bank angle (n = 1/cos φ):**

| Bank φ | n = 1/cos φ | Required lift vs. level | Vertical lift at *fixed* total lift L=W | Stall-speed factor √n |
|--------|-------------|-------------------------|------------------------------------------|------------------------|
| 0° (level) | 1.000 | — | 100.0% | 1.000 |
| 15° (shallow) | 1.035 | +3.5% | 96.6% | 1.017 |
| 25° | 1.103 | +10.3% | 90.6% | 1.050 |
| 30° | 1.155 | +15.5% | 86.6% | 1.075 |
| **35° (issue limit)** | **1.221** | **+22.1%** | **81.9%** | **1.105** |
| 45° | 1.414 | +41.4% | 70.7% | 1.189 |
| 60° | 2.000 | +100% | 50.0% | 1.414 |

**Reading the numbers for the reported case (φ = 35°):**

- The wing must generate **n = 1.22× its wings-level lift** just to hold altitude.
- Equivalently, if total lift were held at the same value as wings-level flight, the vertical
  component falls to `cos 35° = 0.819`, i.e. **only ~82% of the weight is supported** → the
  aircraft sinks at an initial vertical acceleration of `g·(1 − cos φ) ≈ 0.18 g`.
- Contrast: 45° needs +41% lift (vertical component down to 71%); a shallow 15° bank needs
  only +3.5% lift (vertical component 97%).
- Because required lift is higher, the **stall speed rises by √n** (H&C §1.5.9, printed p.45:
  C_Lmax "determines the minimum speed at which an aeroplane can fly"): at 35° bank stall
  speed is ~10.5% higher, at 45° it is ~19% higher. Near a loiter's low speed this margin
  disappears quickly.

> **Scope note (important):** the 5th edition of Houghton & Carpenter is a *fluid-mechanics /
> aerodynamics* text (Ch.1–9: flows, wing theory, boundary layers, propulsion). It has **no
> dedicated "aircraft performance / manoeuvre" chapter**, so the closed-form `n = 1/cos φ`
> and the bank-angle table are derived here from the force balance H&C states on pp.26–27
> (lift direction, Fig. 1.7) plus Newton's second law / centripetal force on pp.136 & 221.
> The relationship itself is standard flight mechanics and is cross-checkable in any
> performance text (e.g. Anderson, *Introduction to Flight*; Etkin, *Dynamics of Flight*).

---

## 2. Can it hold altitude or climb at 10° pitch + 35° bank?

**No — not while the pitch command is capped at 10°.** Two independent reasons:

**(a) Lift shortfall (primary).** `nav_fw_climb_angle` is a *pitch-angle* command (nose-up
body attitude), which the controller was already using at its 10° maximum to climb in straight
flight. Banking 35° tilts the lift vector; to keep the vertical component equal to weight the
airframe must develop 1.22× the straight-flight lift, i.e. a higher **angle of attack** and
thus a higher C_L (H&C Eqn 1.45a, `C_L = L/(½ρV²S)`, printed p.28). A fixed 10° pitch ceiling
— while rolled — cannot command that extra AoA, so `L·cos φ < W` and the aircraft accelerates
downward (descends). It will keep sinking until a new, steeper equilibrium (effectively a
descending spiral) is reached, or until it stalls.

**(b) Drag/power shortfall (secondary but compounding).** The higher C_L needed in the turn
raises **induced drag ∝ C_L²** (H&C §1.5.7, printed pp.41–43; total drag `C_D = C_D0 + k·C_L²`,
§1.5.8, printed p.44). Turning is "draggy": at 35° bank, induced drag rises ~(1.22)² ≈ 1.5× its
level value. Without extra throttle, airspeed bleeds off, lift `L = C_L·½ρV²S` falls further
(speed enters squared), and the sink steepens. On a small elevon flying wing the extra elevon
deflection to hold the tight loiter adds further trim/profile drag.

**What must be done to hold altitude in a steep turn:**

1. **Raise the angle of attack** (more nose-up) until `L·cos φ ≥ W` — i.e. let the pitch
   command exceed 10° in the turn (or reduce bank, see §4).
2. **Add power/throttle** to overcome the ~1.5× induced drag and keep airspeed (and thus
   dynamic pressure ½ρV²) up, otherwise speed decays and lift decays with it.

**What happens when neither is possible (pitch already limited):** the aircraft **must
descend** — there is no way around `L·cos φ < W`. If the controller keeps pushing toward
C_Lmax to try to compensate, it approaches stall (H&C §1.5.9, printed p.45: lift peaks at
C_Lmax "at an incidence of α_s, known as the stalling point", then falls). Because stall speed
is elevated by √n in the turn, a low-speed tight loiter is exactly where a stall/snap is most
likely.

---

## 3. Does the turn bias a strapdown accelerometer's apparent "gravity"?

**Yes, qualitatively and quantitatively.** A strapdown accelerometer does not sense gravity
directly; it measures **specific force** `f = a − g` (the non-gravitational acceleration, or
equivalently the reaction that "holds up" its proof mass). In a steady, level, **coordinated
turn** the aircraft is not in an inertial frame — it is accelerating toward the turn centre at
`a_c = V²/r = g·tan φ` (H&C §5.2.3, printed p.221; §3.3.11, printed p.136). Therefore:

- The accelerometer's specific-force vector is the vector sum of `−g` (up, magnitude g) plus
  the horizontal centripetal term `g·tan φ`.
- Its magnitude is `|f| = g/cos φ = n·g` (≈ **1.22 g** at 35° bank), and its direction is
  **tilted by φ from the true vertical** — it points along the aircraft's local "down" (into
  the seat), i.e. along the tilted lift axis.

Consequence for an attitude estimator that uses the accelerometer to level the horizon (e.g. a
complementary/Mahony filter with a non-zero accelerometer correction time constant): in a
sustained turn it reads an apparent "gravity-down" that is tilted by φ toward the turn centre,
so it **pulls the estimated roll (and pitch) toward the bank angle** — a classic "turning
error" / centripetal-acceleration bias. In a *brief* transient the gyro dominates and this is
small, but in a **tight, sustained loiter the bias persists**, so the controller's notion of
"level" and of its own pitch can be systematically wrong by up to ~φ (35° here).

**Caveats / relevance to the issue:**

- H&C is an aerodynamics text and does not discuss IMU/AHRS filtering; the physics above is the
  *source* of the accelerometer bias, and the accelerometer side is standard strapdown-inertial
  practice, not an H&C citation.
- This bias is a **secondary contributor**, not the primary cause of the altitude loss: the
  sink is already fully explained by the real lift shortfall in §1–§2. But a bank-induced
  attitude bias could *mask* the true pitch (e.g. the FC believing it is more nose-up than it
  is) or corrupt the horizon, so it should be checked in logs — however, fixing it will not by
  itself stop the descent; the airframe still lacks lift at 10° pitch + 35° bank.

---

## 4. Practical conclusion and mitigating config changes

**Conclusion: "banked hard at 10° pitch → altitude loss" is expected aerodynamics, not an
estimation bug.** At 35° bank the vertical lift component drops to ~82% and the wing needs
+22% lift just to stay level; the 10° pitch ceiling cannot supply it, so the aircraft descends.
(This is exactly the aerodynamics of Fig. 1.7(d), H&C printed p.27.)

**Config changes that mitigate it (in rough order of effectiveness):**

1. **Reduce the bank limit** — lower `max_angle_inclination_rll` from 35° to ~25–30° for the
   loiter/turn phase. At 25° the load factor is only 1.10 (+10% lift needed) instead of 1.22,
   and at 30° it is 1.15. This is the most direct lever because load factor is `1/cos φ`.
2. **Enlarge the loiter radius** — from `tan φ = V²/(g·R)`, a larger radius reduces the bank
   angle needed to hold the circle at a given speed, which lowers both the lift shortfall and
   the sustained centripetal acceleration (and thus the AHRS bias). Often the cleanest fix and
   gentle on a small airframe. (Illustration at V = 12 m/s: 35° bank ⇒ R ≈ 21 m; 25° bank ⇒
   R ≈ 31 m.)
3. **Raise the climb-angle limit** — increase `nav_fw_climb_angle` so the controller *can*
   command more nose-up inside the turn. Note this is a pitch-angle limit, not AoA, and on a
   flying wing near C_Lmax it has diminishing returns and rising stall risk; it works best
   **combined with** (1) and/or (2).
4. **Add turn throttle** — more power in the turn raises airspeed and dynamic pressure, so the
   same C_L produces more lift (`L = C_L·½ρV²S`, H&C Eqn 1.45a, p.28), and it covers the ~1.5×
   induced drag. Verify INAV's turn/loiter throttle compensation is active and adequate.
5. **Optional: verify the attitude estimate in the log** — if the horizon/pitch is visibly
   biased during the sustained loiter (centripetal acceleration, §3), confirm the firmware's
   accelerometer turn/centrifugal compensation is enabled; but do not expect this alone to
   recover altitude — the lift shortfall is physical.

---

## Key equations

```
L = C_L · ½ρV²S                      (lift; H&C Eqn 1.45a, printed p.28)
C_D = C_D0 + k·C_L²                  (total drag incl. induced ∝ C_L²; H&C §1.5.7–1.5.8, pp.41–44)

Steady level coordinated turn (φ = bank angle):
  n = L/W = 1/cos φ                  (load factor)
  L·sin φ = m·V²/r                    (centripetal; H&C pp.136, 221)
  tan φ = V²/(g·r)                    (turn radius/speed/bank)
  V_stall,turn = V_stall,level · √n   (stall-speed rise in the turn)

Vertical lift at fixed total lift:  L_vert = L·cos φ → W·cos φ when L = W.
At φ = 35°:  cos 35° = 0.819  (≈82% of weight supported; −18% deficit)
             n = 1/cos 35° = 1.221  (+22% lift required; |f| ≈ 1.22 g)

Accelerometer specific force in a coordinated turn:
  f = a − g,  |f| = g/cos φ = n·g,  tilted φ from true vertical.
```

## Textbook citations (Houghton & Carpenter, *Aerodynamics for Engineering Students*, 5th ed.)

Printed-page numbers (the book's own page numbers, as in its running headers and TOC; the PDF
physical page = printed page + 17):

- §1.5.1, **p.26** — lift defined as perpendicular to the flight direction; weight vertical.
- Fig. 1.7(d), **p.27** — "Banked circling flight": lift vector tilts with bank.
- §1.5.2, Eqn 1.45a/b, **p.28** — lift and drag coefficients; `L = C_L·½ρV²S`.
- §1.5.7, **pp.41–43** — induced drag; induced drag coefficient ∝ C_L².
- §1.5.8, **p.44** — lift-dependent drag; total drag `C_D = C_D0 + k·C_L²`.
- §1.5.9, **pp.44–46** — aerofoil characteristics; C_Lmax and the stalling point; "C_Lmax …
  determines the minimum speed at which an aeroplane can fly" (**p.45**).
- §3.3.11, **p.136** — centripetal force = mass × centripetal acceleration (rotational flow).
- §5.2.3, **p.221** — centripetal acceleration = (velocity)²/radius.

## Related knowledge-base entries

- `pitch-airspeed-relationship.md` — pitch vs. airspeed at constant throttle (V ∝ 1/√C_L).
- `power-flight-path-angle.md` — power required vs. flight-path angle in climb/descent.

## Limitations

- The closed-form load-factor/turn relations are derived, not printed verbatim, because the 5th
  edition has no flight-performance chapter; they follow from H&C's own force definitions and
  centripetal-force statements.
- "Pitch angle" (body attitude, what `nav_fw_climb_angle` limits) is not the same as
  "angle of attack" (chord vs. airflow); the lift shortfall is governed by AoA, which a pitch
  ceiling only indirectly bounds.
- The accelerometer/AHRS discussion is standard strapdown-inertial practice, outside H&C's
  scope; it is included only to answer the "estimation bug?" half of the question.
