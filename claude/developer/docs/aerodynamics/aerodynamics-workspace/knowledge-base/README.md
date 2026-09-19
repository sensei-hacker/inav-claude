# Aerodynamics Knowledge Base

This directory contains accumulated aerodynamic knowledge organized by topic, with citations to Houghton & Carpenter "Aerodynamics for Engineering Students" (5th Edition) and applications to INAV flight controller development.

## Contents

### Flight Dynamics

1. **[pitch-airspeed-relationship.md](pitch-airspeed-relationship.md)**
   - Topic: How pitch angle affects airspeed at constant throttle
   - Key equation: V ∝ 1/√CL ∝ 1/√α
   - INAV application: Fixed-wing altitude/speed control coupling
   - References: H&C pages 26-49, 62-67

2. **[power-flight-path-angle.md](power-flight-path-angle.md)**
   - Topic: Power required to maintain constant airspeed during climbs/descents
   - Key equation: P = P_level × (1 + [L/D] × sin(γ))
   - INAV application: Throttle optimization, energy management, range estimation
   - References: H&C pages 26-44, 62-67
   - Includes: Small angle linearity analysis (sin(γ) ≈ γ for |γ| < 15°)

3. **[banked-turn-altitude-loss.md](banked-turn-altitude-loss.md)**
   - Topic: Steady coordinated turn — load factor, lift split, altitude loss in tight loiters
   - Key equation: n = L/W = 1/cos(φ); tan(φ) = V²/(g·R); V_stall,turn = V_stall,level·√n
   - INAV application: Why a hard bank (e.g. 35°) at max climb pitch (10°) loses altitude;
     mitigations (reduce roll limit, enlarge loiter radius, raise climb angle, add throttle);
     accelerometer centripetal-acceleration bias in sustained turns
   - References: H&C §1.5.1 p.26 (lift def, Fig. 1.7(d)), §1.5.2 p.28 (Eqn 1.45a),
     §1.5.7–1.5.8 pp.41–44 (induced drag ∝ C_L²), §1.5.9 pp.44–46 (C_Lmax/stall),
     §3.3.11 p.136 & §5.2.3 p.221 (centripetal force mV²/r)
   - Note: load factor n = 1/cos φ is derived (5th ed. has no flight-performance chapter)

### Related Topics

These two documents are complementary:

**Constant Throttle Scenario (pitch-airspeed-relationship.md):**
- Pitch changes → angle of attack changes → lift coefficient changes → airspeed changes
- Aircraft exchanges altitude for airspeed (or vice versa)
- Phugoid oscillation behavior

**Constant Airspeed Scenario (power-flight-path-angle.md):**
- Flight path angle changes → power requirement changes
- Gravity assists in descent, opposes in climb
- Throttle adjustments needed to maintain airspeed

**Combined Understanding:**
In real flight, pilot/autopilot controls:
1. **Pitch** - Primary control of angle of attack and instantaneous lift
2. **Throttle** - Primary control of energy state (altitude + speed)

These are coupled - changing one affects both airspeed and altitude over time.

### `nav_fw_pitch2thr` (Fixed-Wing Pitch-to-Throttle)

The reviewed, canonical analysis of INAV's `nav_fw_pitch2thr` setting —
including the three disagreeing theoretical gain estimates and why they
disagree — lives at `inav/docs/development/fixed-wing-pitch2thr-tuning.md`
(dev-facing) and `inav/docs/Fixed Wing Pitch To Throttle Tuning.md`
(user-facing flight-test procedure), not in this directory. Two exploratory
calculator scripts and plots from the underlying constant-T/W-envelope
derivation remain here as derivation aids, not shipped documentation:
`calculate-envelopes-tw-below-1.py`, `calculate-local-derivative.py`, and
the `equal-airspeed-*.gnuplot`/`.png` outputs.

## Organization

Each knowledge base entry includes:

1. **Summary** - Quick reference of key concepts
2. **Key Equations** - Mathematical relationships with variable definitions
3. **Derivation** - Where equations come from (when relevant)
4. **Textbook Citations** - Specific page references to Houghton & Carpenter
5. **INAV Applications** - How theory applies to flight controller code
6. **Practical Examples** - Worked problems with realistic numbers
7. **Limitations** - Assumptions and when they break down
8. **References** - Sources and related topics

## Contributing

When adding new knowledge base entries:

1. Use clear, descriptive filenames (lowercase, hyphens, .md extension)
2. Include H&C page citations where applicable
3. Provide INAV-specific applications
4. Cross-reference related topics
5. Update this README with new entries

## Quick Reference: Most Useful Pages

From Houghton & Carpenter (5th Edition):

| Pages | Topic | INAV Use Cases |
|-------|-------|----------------|
| 1-14 | Fundamental definitions | General reference |
| 15-19 | Wing/aerofoil geometry | Aircraft configuration |
| 19-26 | Reynolds number, scaling | Environmental effects |
| 26-49 | Basic aerodynamics, force coefficients | Flight dynamics modeling |
| 35-44 | Drag types (induced, parasitic) | Mission planning, efficiency |
| 47-48 | Aspect ratio effects | L/D estimation, glide performance |
| 62-67 | Pitot-static tube & airspeed | Sensor calibration, IAS/TAS |
| 62-63 | Lift curves, stall characteristics | Stall protection, angle of attack |
| 64-65 | Drag characteristics, drag polar | Performance optimization |

## Index Access

Pre-built keyword index available at:
```
/home/raymorris/Documents/planes/inavflight/claude/developer/docs/aerodynamics/Houghton-Carpenter-Index/search-index/
```

Most relevant indexed terms:
- `aerofoil.txt` (545 occurrences)
- `boundary-layer.txt` (501 occurrences)
- `Reynolds-number.txt` (136 occurrences)
- `drag-coefficient.txt` (67 occurrences)
- `aspect-ratio.txt` (67 occurrences)
- `lift-coefficient.txt` (59 occurrences)
- `induced-drag.txt` (45 occurrences)
- `stall.txt` (39 occurrences)

See `../QUICK-START.md` for search instructions.

---

*Knowledge base maintained by: aerodynamics-expert agent*
*Last updated: 2026-07-22*
