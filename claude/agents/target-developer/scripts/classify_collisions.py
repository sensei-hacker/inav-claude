#!/usr/bin/env python3
"""Classify DMA_STREAM_COLLISION hazards by severity.

Firmware ownership model (confirmed in timer_impl_stdperiph.c +
pwm_mapping.c:pwmInitMotors): motors are initialized strictly in position
order (idx = 0..motorCount-1); the FIRST entry to reach a shared DMA
descriptor claims it (dmaInit -> owner = OWNER_TIMER); every later entry
resolving to the same (dma,stream) tuple hits `owner != OWNER_FREE` and
silently fails to configure. So within one collision group, the LOWEST
position always wins and stays alive; every OTHER (higher) position in the
group is a loser and goes dead.

Severity is therefore about the losers, not the group as a whole:
  CERTAIN - the second-lowest position in the group (the best-case loser)
            is < 4, i.e. an S1-S4 output actually goes dead.
  NOTICE  - all losers are at position >= 4; the S1-S4 member of the group
            (if any) is the winner and keeps working fine.

On USE_DSHOT_DMAR targets, simulate_pwm_roles.py additionally emits
BURST_STREAM_COLLISION instead of (or alongside) DMA_STREAM_COLLISION for
groups affected by burst mode's per-PHYSICAL-TIMER (not per-channel) DMA
claim -- see that script's module docstring for the full model. This
script treats both hazard types identically for severity purposes (same
"loser position < 4" rule, same winner-always-lower-position guarantee),
since simulate_pwm_roles.py's BURST_STREAM_COLLISION text embeds the same
"TIM_CH" substrings this script matches positions against.

KNOWN BLIND SPOT, FIXED 2026-08-21: a MOTOR-vs-LED_STRIP collision can
NEVER be surfaced by the CERTAIN/NOTICE machinery above, structurally --
LED-strip rows never get a `position` (simulate_pwm_roles.py's per-row
loop only assigns `pos` for the MOTOR and SERVO buckets; the LED branch
leaves it None), and this function's `involved` list filters out any
tim_ch whose looked-up position is None before the `len(involved) < 2`
check even runs. So a real motor-vs-LED collision always collapses to a
1-element `involved` list and is silently dropped -- not misclassified,
just invisible, from every prior run of this tool. Found by hand while
using this script's output as a work list for Phase 2 step 3 of
investigate-shared-tim-dma-request-lines (AIKONF7's TIM3_CH2 vs TIM2_CH1
collision, where TIM2_CH1 is TIM_USE_LED, never appeared in any NOTICE
list despite firing at every motorCount from 4 up). A full re-sweep this
same pass found FURYF4OSD has the same previously-invisible pattern too
(TIM3_CH4 vs TIM5_CH1/LED_STRIP) -- both now correctly reported below by
`led_collisions()`, a structurally separate detection pass (LED-vs-motor
severity is always deterministic -- motors init before ledStripInit() in
fc_init.c, so a MOTOR side always wins and the LED silently just doesn't
light; never flight-critical, so there's no CERTAIN/NOTICE split to make
here, just a single LED_COLLISION bucket).

SAME-(TIM,CH) BLIND SPOT, FIXED 2026-09-04: classify() keyed its
`positions` dict by f"{tim}_{ch}", so when one target declared the SAME
(timer, channel) twice on different pins, the second row overwrote the
first, `involved` collapsed to a single element, and the
`len(involved) < 2` guard discarded the hazard -- invisible, exactly like
the LED case above. Found while merging the two shared-DMA PRs: WARPF7
declares TIM3_CH3 on both PB0 and PC8 unconditionally and had never been
reported by any sweep. Rows are now matched against the hazard text by
their full "TIM_CH(label)" token instead, which is how simulate() renders
each claimer -- per-entry, so neither the overwrite nor the converse
over-match (one (tim,ch) present twice on DIFFERENT streams, where a bare
substring test would absorb an unrelated entry's position and could invent
a bogus CERTAIN) can happen. Surfaced a real previously-invisible CERTAIN
on FURYF4OSD: TIM2_CH3 is declared on both PA2 and PB10, and at
motorCount=4 both resolve to MOTOR on DMA1 Stream1, so a basic quad
silently loses an output.

SEVERITY NOTE (2026-09-04, per Ray): a (timer, channel) duplicate is
strictly WORSE than any DMA collision and is now reported above CERTAIN.
Losing DMA only costs an output DSHOT -- it still works as a servo or with
Multishot. Two pins sharing one compare register can only ever emit the
same waveform, so the second output is unusable for every protocol. The
CERTAIN/NOTICE/LED tiers below rank DMA damage only; see
timer_channel_duplicates().

CONDITIONAL-COMPILATION BLIND SPOT, FIXED 2026-08-21: parser-gap targets
(conditional-compilation flattening -- see simulate_pwm_roles.py's
parse_target_c() docstring) used to silently surface same-(tim,ch)-twice
false hits here (or, worse on MAMBAF405US, silently mask a real hazard
behind a clean #ifdef branch) with no way to tell from this script's
output alone. parse_target_c() is now preprocessor-aware (entry.conditional
/ entry.conditional_expr); main() checks sim.has_conditional_tim() per
target before calling classify()/led_collisions() and reports those
targets in a separate N/A bucket instead of feeding them through the
CERTAIN/NOTICE/LED_COLLISION machinery.

Usage: python3 classify_collisions.py <inav-checkout-root> <targets-file>
<targets-file> lists one target name per line, F4/F7/AT32 only. Build it
with simulate_pwm_roles.detect_family() in ("F4","F7","AT32") to exclude
H7 (out of scope -- separate hazard model, handled by check_dma_conflicts.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import simulate_pwm_roles as sim  # noqa: E402

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else None
TARGETS_FILE = Path(sys.argv[2]) if len(sys.argv) > 2 else None


def _load(target_name):
    """Shared parse/setup for one target. Returns None if not applicable,
    else (family, entries, adc_pins, led_strip, dshot_dmar, dma_resolver,
    max_mc)."""
    target_dir = ROOT / "src" / "main" / "target" / target_name
    target_c = target_dir / "target.c"
    target_h = target_dir / "target.h"
    cmake = target_dir / "CMakeLists.txt"
    if not target_c.is_file() or not cmake.is_file():
        return None
    family = sim.detect_family(cmake.read_text(errors="ignore"))
    if family is None:
        return None
    entries = sim.parse_target_c(target_c.read_text(errors="ignore"))
    if not entries:
        return None
    adc_pins, led_strip, dshot_dmar = (set(), False, False)
    if target_h.is_file():
        adc_pins, led_strip, dshot_dmar = sim.parse_target_h(target_h.read_text(errors="ignore"))
    dma_resolver = sim.DmaResolver(family, target_dir,
                                    target_h.read_text(errors="ignore") if target_h.is_file() else "",
                                    dshot_dmar)
    max_mc = max(12, len(entries))
    return family, entries, adc_pins, led_strip, dshot_dmar, dma_resolver, max_mc


def classify(target_name):
    loaded = _load(target_name)
    if loaded is None:
        return None
    _family, entries, adc_pins, led_strip, dshot_dmar, dma_resolver, max_mc = loaded

    worst = None  # None, "NOTICE", or "CERTAIN"
    detail = []
    for mc in range(4, max_mc + 1):
        result = sim.simulate(entries, mc, None, adc_pins, led_strip, dma_resolver, True, {})
        for h in result.hazards:
            if not (h.startswith("DMA_STREAM_COLLISION") or h.startswith("BURST_STREAM_COLLISION")):
                continue
            # Match each row against the hazard text by its FULL
            # "TIM_CH(label)" token, which is exactly how simulate() renders
            # each claimer (see the `names` join in its collision loop).
            #
            # Keying by the bare f"{tim}_{ch}" was wrong twice over:
            #   1. As a dict key it silently dropped same-(tim,ch)-twice
            #      targets -- the second row overwrote the first, `involved`
            #      collapsed to one element, and the `len(involved) < 2`
            #      guard below discarded the hazard entirely (WARPF7,
            #      FURYF4OSD; see the module docstring).
            #   2. As a substring test it OVER-matched: one (tim,ch) can
            #      appear twice on DIFFERENT streams, so a hazard on stream X
            #      would wrongly absorb the position of the entry sitting on
            #      stream Y and could manufacture a bogus CERTAIN from it.
            # The label disambiguates both cases, since it is per-entry.
            involved = sorted(
                (row["position"], f'{row["entry"].tim}_{row["entry"].ch}')
                for row in result.rows
                if row["claims_dma"] and row["position"] is not None
                and f'{row["entry"].tim}_{row["entry"].ch}({row["entry"].label})' in h)
            if len(involved) < 2:
                continue  # need at least a winner + a loser to say anything
            losers = involved[1:]  # everything but the lowest position (the winner)
            worst_loser_pos = losers[0][0]  # best-case loser = lowest among losers
            sev = "CERTAIN" if worst_loser_pos < 4 else "NOTICE"
            if sev == "CERTAIN":
                worst = "CERTAIN"
            elif worst is None:
                worst = "NOTICE"
            detail.append((mc, sev, involved, dshot_dmar))
    return worst, detail, dshot_dmar


def timer_channel_duplicates(target_name):
    """Detect two DEF_TIM entries sharing one (timer, channel) on DIFFERENT pins.

    This outranks every DMA hazard in this file. A DMA collision only costs
    the loser its DMA, so the output drops to non-DSHOT but still works for
    servo/Multishot. Two pins on ONE timer channel share a single compare
    register, so they can only ever emit the SAME waveform -- the second
    output cannot be driven independently at all, for any protocol. Unusable
    beats degraded, so these are reported above CERTAIN.

    Conditional (#if-guarded) entries are skipped: mutually exclusive build
    variants legitimately reuse a (tim,ch) across branches, and
    parse_target_c() flattens them into one array. main() already routes
    those targets to the N/A bucket.

    Returns [(tim_ch, [pins...]), ...] or None.
    """
    loaded = _load(target_name)
    if loaded is None:
        return None
    _family, entries, _adc, _led, _dmar, _res, _mc = loaded

    seen = {}
    for e in entries:
        if e.conditional:
            continue
        seen.setdefault((e.tim, e.ch), []).append(e)

    dupes = []
    for (tim, ch), group in sorted(seen.items()):
        pins = [e.pin for e in group]
        # Distinct pins only: the same pin repeated is a source duplicate,
        # not two physical outputs fighting over one compare register.
        if len(group) >= 2 and len(set(pins)) >= 2:
            dupes.append((f"{tim}_{ch}", pins))
    return dupes or None


def led_collisions(target_name):
    """Detect MOTOR-vs-LED_STRIP DMA collisions -- structurally invisible to
    classify()'s CERTAIN/NOTICE machinery, see module docstring. Returns
    (first_mc, motor_tim_ch, led_tim_ch) for the first motorCount at which a
    real (non-parser-gap-duplicate) hit occurs, or None."""
    loaded = _load(target_name)
    if loaded is None:
        return None
    _family, entries, adc_pins, led_strip, dshot_dmar, dma_resolver, max_mc = loaded
    if not led_strip:
        return None  # target has no LED strip at all, can't collide with one

    for mc in range(4, max_mc + 1):
        result = sim.simulate(entries, mc, None, adc_pins, led_strip, dma_resolver, True, {})
        led_tim_ch = {row["entry"].tim + "_" + row["entry"].ch
                      for row in result.rows if "LED" in row["bucket"]}
        if not led_tim_ch:
            continue
        for h in result.hazards:
            if not (h.startswith("DMA_STREAM_COLLISION") or h.startswith("BURST_STREAM_COLLISION")):
                continue
            hit_led = [tc for tc in led_tim_ch if tc in h]
            if not hit_led:
                continue
            # Identify the non-LED (motor) participant for the report line.
            # Same-(tim,ch)-twice parser-gap duplicates show up as the LED
            # tim_ch appearing twice with different labels in the hazard
            # text; that's not a real motor partner, so guard against it.
            motor_tim_ch = None
            for row in result.rows:
                e = row["entry"]
                tc = f"{e.tim}_{e.ch}"
                if tc in hit_led:
                    continue
                if tc in h and row.get("claims_dma"):
                    motor_tim_ch = tc
                    break
            return (mc, motor_tim_ch, hit_led[0])
    return None


def main():
    certain, notice, led, conditional, timch = [], [], [], [], []
    for line in TARGETS_FILE.read_text().splitlines():
        t = line.strip()
        if not t:
            continue
        # Run the (tim,ch)-duplicate check BEFORE the conditional skip below:
        # it ignores #if-guarded entries itself, so a target that is N/A for
        # the DMA machinery can still have its unconditional duplicates
        # reported rather than vanishing entirely.
        try:
            dup = timer_channel_duplicates(t)
        except Exception as ex:
            print(f"ERROR (tim/ch dup check) {t}: {ex}", file=sys.stderr)
            dup = None
        if dup:
            timch.append((t, dup))

        loaded = _load(t)
        if loaded is not None and sim.has_conditional_tim(loaded[1]):
            # DEF_TIM lines guarded by #if/#ifdef/#ifndef: parse_target_c()
            # flattens every build variant into one array, so any verdict
            # derived from it here could be a self-collision false positive
            # or a hazard masked by another variant's clean line. Report
            # N/A instead of silently including or excluding this target --
            # see simulate_pwm_roles.py's parse_target_c() docstring.
            conditional.append(t)
            continue
        try:
            res = classify(t)
        except Exception as ex:
            print(f"ERROR {t}: {ex}", file=sys.stderr)
            continue
        if res is not None:
            worst, detail, dshot_dmar = res
            if worst == "CERTAIN":
                first = next(d for d in detail if d[1] == "CERTAIN")
                certain.append((t, first[0], first[2], dshot_dmar))
            elif worst == "NOTICE":
                first = detail[0]
                notice.append((t, first[0], first[2], dshot_dmar))
        try:
            led_hit = led_collisions(t)
        except Exception as ex:
            print(f"ERROR (LED check) {t}: {ex}", file=sys.stderr)
            led_hit = None
        if led_hit is not None:
            led.append((t,) + led_hit)

    def fmt(pairs):
        return ",".join(f"{tc}@pos{p}" for p, tc in pairs)

    print(f"=== TIMER_CHANNEL_DUPLICATE (WORST: two pins on one compare register -- the later output cannot be driven independently AT ALL, for any protocol, not merely DSHOT): {len(timch)} targets ===")
    for t, dups in timch:
        for tim_ch, pins in dups:
            print(f"  {t}  {tim_ch}  pins={'/'.join(pins)}")
    print()
    print(f"=== CERTAIN (a loser sits at position < 4 -- a basic-quad output actually goes dead): {len(certain)} targets ===")
    for t, mc, pairs, dmar in certain:
        print(f"  {t}  (first at motorCount={mc})  {fmt(pairs)}{'  [USE_DSHOT_DMAR]' if dmar else ''}")
    print(f"\n=== NOTICE (all losers at position >= 4; any S1-S4 member wins and stays alive): {len(notice)} targets ===")
    for t, mc, pairs, dmar in notice:
        print(f"  {t}  (first at motorCount={mc})  {fmt(pairs)}{'  [USE_DSHOT_DMAR]' if dmar else ''}")
    print(f"\n=== LED_COLLISION (MOTOR always wins over LED strip specifically; LED silently doesn't light, never flight-critical): {len(led)} targets ===")
    for t, mc, motor_tc, led_tc in led:
        print(f"  {t}  (first at motorCount={mc})  motor={motor_tc} led={led_tc}")
    print(f"\n=== N/A (timerHardware[] has #if/#ifdef/#ifndef-guarded DEF_TIM lines -- needs manual per-build-variant review): {len(conditional)} targets ===")
    for t in conditional:
        print(f"  {t}")


if __name__ == "__main__":
    main()
