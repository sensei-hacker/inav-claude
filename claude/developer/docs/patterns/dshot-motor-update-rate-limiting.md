# Pattern: DShot Motor-Update Rate Limiting (Non-Blocking)

## The Problem

DShot's bit rate (150/300/600/1200 kbit/s) limits how fast a full frame can physically be
transmitted. A naive implementation that tries to push a new frame every PID-loop iteration
at a high loop rate (e.g. 8 kHz) with a slow protocol (DSHOT150) would either corrupt frames
by restarting DMA mid-transfer, or require blocking the scheduler until the previous frame
finishes.

## The Existing Solution (predates any specific PR)

INAV already caps the motor-frame send rate per protocol, independent of the PID loop rate,
via a non-blocking deferred-return check — not a busy-wait:

`inav/src/main/drivers/pwm_output.c`:
- `getEscUpdateFrequency()` (~line 625): hardcoded per-protocol cap —
  DSHOT150 → 4 kHz (250 µs), DSHOT300 → 8 kHz (125 µs), DSHOT600 → 16 kHz (62.5 µs).
- `pwmCompleteMotorUpdate()` (~line 531): `if ((currentTimeUs - digitalMotorLastUpdateUs) <=
  digitalMotorUpdateIntervalUs) { return; }` — called every PID loop iteration from
  `fc/fc_core.c`; if the interval hasn't elapsed, it just returns. No spin, no scheduler stall.
  Loop iterations faster than the cap simply skip sending a new frame that tick.

**Implication:** running DSHOT150 on an 8 kHz loop already silently caps motor updates to
4 kHz today, with zero telemetry involved. This is expected, pre-existing behavior, not a bug.

## Applying This When Evaluating New DShot Features (e.g. bidirectional telemetry, PR #11605)

When a new DShot feature (like bidirectional/GCR telemetry) adds a data-dependent wait (e.g.
a turnaround deadtime before the port can be reused), check it against the *existing*
per-protocol cap above rather than assuming DSHOT150 is automatically the riskiest case:

| Protocol | Existing cap | Bidir GCR deadtime (PR #11605, `35µs + 1e6*(16*20)/dshotHz`) | Margin |
|---|---|---|---|
| DSHOT150 | 250 µs | ~141.7 µs | ~43% headroom |
| DSHOT300 | 125 µs | ~88.3 µs | ~29% headroom |
| DSHOT600 | 62.5 µs | ~61.7 µs | **~1% headroom** |

Counterintuitively, DSHOT600 — not DSHOT150 — runs closest to its own rate-cap edge once a
bidir turnaround cost is added, because its existing cap was set with the least slack over
raw frame time. Don't assume "the slowest protocol is the one at risk" without doing this
comparison; the existing caps already absorb most of DSHOT150's disadvantage.

## Related Files

- `inav/src/main/drivers/pwm_output.c:521-577` — `pwmCompleteMotorUpdate()`
- `inav/src/main/drivers/pwm_output.c:625-650` — `getEscUpdateFrequency()`
- `claude/developer/docs/patterns/` — other INAV driver patterns
