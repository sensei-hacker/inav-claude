#!/usr/bin/env python3
"""find_dead_motor_fix.py -- given one or more targets, find a safe
PIN REMAP (a different timer/channel for the SAME physical pin) that clears
SILENT_DEAD_MOTOR hazards, verified by full simulation.

WHY THIS EXISTS
================
SILENT_DEAD_MOTOR (see simulate_pwm_roles.py) means a (timer, channel) has
NO DMA request line AT ALL on this MCU -- e.g. TIM12_CH1/CH2, TIM9, TIM10,
TIM11 and TIM4_CH4 on STM32F405 are all `NONE` in
drivers/timer_def_stm32f4xx.h. No `dmavar` value can help, because there is
no option list to choose from. So find_shared_dma_fix.py, which only
searches dmavar reassignments, structurally CANNOT fix one of these, and
they have historically been written off as "dead, nothing to do".

That conclusion skips the actual question: most STM32 pins reach SEVERAL
timers. PB14 on F405 is TIM12_CH1 (no DMA) but ALSO TIM1_CH2N (AF1) and
TIM8_CH2N (AF3), both of which have real DMA request lines. Moving the
DEF_TIM entry to one of those keeps the same physical pad and the same
silkscreen output number while restoring DSHOT. Nobody had checked, so this
tool does.

SEVERITY: which of these are worth fixing
==========================================
A DMA-less output is NOT unusable -- it still works for servo, Multishot
and analog PWM; it only loses DSHOT. What matters is WHERE it sits in the
motor bucket (`position`, the order pwm_mapping.c hands outputs to the
mixer):
  position 0-3   S1-S4, the basic-quad range: a quad genuinely loses a
                 primary motor under DSHOT. Fix these.
  position 4-7   worth fixing if a clean remap exists, not urgent.
  position >= 8  routinely intentional -- boards deliberately put
                 servo-only pads at the end. Confirm, don't "fix".
--min-position (default 0) and --max-position filter on this.

THE THREE HARD RULES A CANDIDATE MUST PASS
===========================================
1. DATASHEET-CONFIRMED. The (timer, channel) must actually be routable to
   that pin per claude/developer/docs/targets/<mcu>/alternate-functions.tsv.
   This cannot be inferred from how OTHER targets use the pin: "F4" pools
   F405/F411/F446, which have DIFFERENT AF tables, and on F4 the firmware
   derives the AF from the TIMER NAME alone (timer_def_stm32f4xx.h:25,
   `GPIO_AF_ ## tim`) with no per-pin table -- so an invalid pairing
   COMPILES SILENTLY and merely misconfigures the pad. The compiler will
   not catch a mistake here; the datasheet is the only check. See
   af_tables.py, and check_timer_pin_af.py for the same table used as a
   standalone audit of existing targets.
2. NO (timer, channel) DUPLICATE. Two pins on one compare register can only
   mirror each other -- the second output is unusable for EVERY protocol,
   strictly worse than merely losing DSHOT. Checked on the DE-N'd channel:
   TIM8_CH2N and TIM8_CH2 are one compare register (timer_def.h aliases
   BTCH_TIMn_CHmN to BTCH_TIMn_CHm). This is the trap that makes the
   obvious-looking remaps wrong: on a board already driving TIM8_CH2 on
   PC7, PB14 -> TIM8_CH2N looks perfect and every DMA check stays clean.
3. NO NEW HAZARD ANYWHERE IN THE SWEEP. The candidate is simulated across
   the whole motorCount range and compared against baseline; any new
   DMA_STREAM_COLLISION / BURST_STREAM_COLLISION / SHARED_TIMER_DMA_REQUEST
   / SILENT_DEAD_MOTOR / TIMER_CHANNEL_DUPLICATE at any motor count
   disqualifies it. Pre-existing hazards are allowed to remain (they are
   not this fix's job), but must not get WORSE -- a hazard that starts
   biting at a lower motorCount than baseline is treated as new.

Both dmavar options are tried for every candidate channel, and all dead
entries on a target are searched IN COMBINATION (smallest number of entries
moved first), since two remaps can compete for the same DMA stream.

WHAT IT CANNOT DO
==================
- Reordering. Some targets have no valid remap at all (STM32F405 PB9 is
  only TIM4_CH4 and TIM11_CH1, and BOTH are DMA-less), so the only
  remaining mitigation is to move that entry LATER in timerHardware[] so
  the dead pad falls outside S1-S4. That changes which pad is motor 1 --
  a user-visible, documentation-affecting change -- so it is deliberately
  left to a human. This tool reports NO_REMAP_POSSIBLE and says so.
- Conditional targets. If timerHardware[] has #if/#ifdef-guarded DEF_TIM
  lines, parse_target_c() flattens every branch into one array and
  positions become meaningless. Those are reported N/A -- isolate each
  variant with make_pwm_shadow.sh and re-run against the shadow.
- MCUs with no indexed datasheet (F411, F427, H7, RP2350). Reported
  explicitly as unverifiable rather than guessed. Note H7/F7/AT32 also
  need the pairing present in their firmware DEF_TIM_AF table or the build
  fails -- loudly, unlike F4.

Usage
=====
  ./find_dead_motor_fix.py <inav_root> --target NAME [--target NAME ...]
  ./find_dead_motor_fix.py <inav_root> --targets-file FILE
  ./find_dead_motor_fix.py <inav_root> --all-f4      (scan every target)

  --min-position N   only consider dead outputs at bucket position >= N (default 0)
  --max-position N   only consider dead outputs at bucket position <= N
                     (default 3, the basic-quad range; use 7 to include the
                     "okay if needed" band, or a large number for everything)

Output is a report only -- it never edits target.c. Apply the printed
DEF_TIM line by hand, then re-run simulate_pwm_roles.py --sweep to confirm.
"""
import argparse
import itertools
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import simulate_pwm_roles as sim  # noqa: E402
import classify_collisions as cc  # noqa: E402
import af_tables as af  # noqa: E402

DEAD_RE = re.compile(r"^SILENT_DEAD_MOTOR: (\w+)_(\w+) \(([^)]*)\)")


def _sweep(entries, remaps, adc_pins, led_strip, dma_resolver, max_mc,
           dmavar_only=None):
    """remaps: {entry.index: (tim, ch, dmavar)} -- full pin remaps.
    dmavar_only: {entry.index: dmavar} -- co-fix dmavar nudges on entries
    that are NOT themselves dead (see find_cofix()). Returns {mc: hazards}."""
    dmavar_only = dmavar_only or {}
    out = {}
    for mc in range(1, max_mc + 1):
        cloned = sim.clone_entries(entries)
        for e in cloned:
            if e.index in remaps:
                e.tim, e.ch, e.dmavar = remaps[e.index]
            elif e.index in dmavar_only:
                e.dmavar = dmavar_only[e.index]
        result = sim.simulate(cloned, mc, None, adc_pins, led_strip,
                              dma_resolver, True, {})
        out[mc] = set(result.hazards)
    return out


def _kind(h):
    return h.split(":", 1)[0]


def _first_mc(sweep, pred):
    """Lowest motorCount at which any hazard matching pred appears, or None."""
    for mc in sorted(sweep):
        if any(pred(h) for h in sweep[mc]):
            return mc
    return None


def _regressed(baseline, trial):
    """True if `trial` has a hazard baseline never had, OR has a hazard
    baseline did have but starting at a LOWER motorCount (biting sooner is
    a regression even though the hazard string is not new)."""
    base_all = set().union(*baseline.values()) if baseline else set()
    trial_all = set().union(*trial.values()) if trial else set()
    if trial_all - base_all:
        return True
    for h in trial_all:
        b = _first_mc(baseline, lambda x, h=h: x == h)
        t = _first_mc(trial, lambda x, h=h: x == h)
        if b is not None and t is not None and t < b:
            return True
    return False


def dead_entries(entries, adc_pins, led_strip, dma_resolver, max_mc):
    """{entry.index: {'tim','ch','label','positions'}} for every entry that
    triggers SILENT_DEAD_MOTOR anywhere in the sweep."""
    by_tc = {}
    for mc in range(1, max_mc + 1):
        result = sim.simulate(entries, mc, None, adc_pins, led_strip,
                              dma_resolver, True, {})
        pos = {(r["entry"].tim, r["entry"].ch): (r["position"], r["entry"].index)
               for r in result.rows}
        for h in result.hazards:
            m = DEAD_RE.match(h)
            if not m:
                continue
            tim, ch, label = m.groups()
            got = pos.get((tim, ch))
            if got is None:
                continue
            p, idx = got
            rec = by_tc.setdefault(idx, {"tim": tim, "ch": ch, "label": label,
                                          "positions": set(), "first_mc": mc})
            if p is not None:
                rec["positions"].add(p)
    return by_tc


def candidates_for(entry, entries, index_name, dma_resolver, fw_pairs=None):
    """Datasheet-valid, non-duplicating, DMA-capable (tim, ch, dmavar)
    alternatives for this entry's pin. Returns (list, rejections, needs_macro).

    fw_pairs (from af_tables.firmware_af_pairs) is the F7/H7/AT32 firmware
    per-pin AF table. A candidate missing from it is still returned -- the
    silicon supports it -- but flagged in needs_macro, because the build
    will fail until a DEF_TIM_AF__P<pin>__TCH_<TIM>_<CH> line is added to
    the family's timer_def header. F4 has no such table (fw_pairs is None),
    which is exactly why a wrong triple is silent there rather than a
    compile error."""
    opts = af.options_for_pin(index_name, entry.pin)
    taken = {}
    for other in entries:
        if other.index == entry.index:
            continue
        taken.setdefault((other.tim, af.base_channel(other.ch)), []).append(other)

    cands, rejected, needs_macro = [], [], {}
    for token in sorted(opts):
        tim, ch = token.split("_", 1)
        if (tim, ch) == (entry.tim, entry.ch):
            continue
        clash = taken.get((tim, af.base_channel(ch)))
        if clash:
            rejected.append((token, "would DUPLICATE the compare register already "
                                    f"used by {clash[0].tim}_{clash[0].ch} on "
                                    f"{clash[0].pin} ({clash[0].label}) -- that "
                                    "output could never be driven independently"))
            continue
        dma_opts = dma_resolver._lookup(tim, af.base_channel(ch))
        if not dma_opts:
            rejected.append((token, "also has NO DMA request line on this MCU"))
            continue
        if fw_pairs is not None and (entry.pin, tim, ch) not in fw_pairs:
            needs_macro[token] = (
                f"#define DEF_TIM_AF__{entry.pin}__TCH_{tim}_{ch}   "
                f"D(<af>, {tim[3:]})  // add to the family's timer_def header"
            )
        for dv in range(len(dma_opts)):
            cands.append((tim, ch, dv))
    return cands, rejected, needs_macro


HAZ_TC_RE = re.compile(r"\b(TIM\d+)_(CH\d+N?)\b")


def find_cofix(entries, remaps, baseline, adc_pins, led_strip, dma_resolver,
               max_mc, dead_idx, max_extra=2):
    """A remap can be blocked purely because the new channel's only free DMA
    stream is already spoken for by a DIFFERENT, perfectly healthy entry --
    which may itself have an unused alternate dmavar. That entry is not
    dead, so the remap-only search never touches it and the whole target
    looks unfixable.

    Real example: CLRACINGF4AIR (V2/V3 branch). PB15 is stuck on DMA-less
    TIM12_CH2; its only non-duplicating escape is TIM1_CH3N, whose BOTH
    dmavar options land on DMA2 Stream6 -- already held by TIM1_CH1 (PA8)
    at dmavar 0. But TIM1_CH1 has two more options (D(2,1,6) and D(2,3,6),
    Streams 1 and 3, both free), so moving PA8's dmavar frees Stream6 and
    the remap becomes clean. Verdict flips from "no safe remap" to fixable
    by changing one number on an unrelated line.

    So: take the entries actually NAMED in the newly-introduced hazards,
    and try their alternate dmavars (up to max_extra of them at once,
    fewest first). Only non-dead, non-remapped entries are eligible --
    a dead entry is the remap search's own business. Returns
    {entry.index: dmavar} or None."""
    trial = _sweep(entries, remaps, adc_pins, led_strip, dma_resolver, max_mc)
    base_all = set().union(*baseline.values()) if baseline else set()
    new_haz = set().union(*trial.values()) - base_all
    if not new_haz:
        return {}

    by_tc = {}
    for e in entries:
        if e.index in remaps or e.index in dead_idx:
            continue
        by_tc.setdefault((e.tim, af.base_channel(e.ch)), e)

    involved = []
    for h in new_haz:
        for tim, ch in HAZ_TC_RE.findall(h):
            e = by_tc.get((tim, af.base_channel(ch)))
            if e is not None and e not in involved:
                involved.append(e)
    if not involved:
        return None

    per = {}
    for e in involved:
        opts = dma_resolver._lookup(e.tim, af.base_channel(e.ch)) or []
        alts = [i for i in range(len(opts)) if i != e.dmavar]
        if alts:
            per[e.index] = alts
    if not per:
        return None

    idxs = sorted(per)
    for k in range(1, min(max_extra, len(idxs)) + 1):
        for subset in itertools.combinations(idxs, k):
            for combo in itertools.product(*(per[i] for i in subset)):
                nudge = dict(zip(subset, combo))
                t2 = _sweep(entries, remaps, adc_pins, led_strip, dma_resolver,
                            max_mc, dmavar_only=nudge)
                if not _regressed(baseline, t2):
                    still = set()
                    for hz in t2.values():
                        for h in hz:
                            m = DEAD_RE.match(h)
                            if m:
                                still.add((m.group(1), m.group(2)))
                    if not any((tim, ch) in still for (tim, ch, _dv) in remaps.values()):
                        return nudge
    return None


def solve(target, root, min_pos, max_pos):
    cc.ROOT = root
    loaded = cc._load(target)
    if loaded is None:
        return {"status": "LOAD_FAILED"}
    family, entries, adc_pins, led_strip, dshot_dmar, dma_resolver, max_mc = loaded
    if sim.has_conditional_tim(entries):
        return {"status": "CONDITIONAL"}

    tdir = root / "src" / "main" / "target" / target
    mcu, index_name = af.mcu_index_for_target(tdir)
    if index_name is None:
        return {"status": "NO_DATASHEET", "mcu": mcu}

    dead = dead_entries(entries, adc_pins, led_strip, dma_resolver, max_mc)
    by_idx = {e.index: e for e in entries}
    in_scope = {i: d for i, d in dead.items()
                if d["positions"] and min_pos <= min(d["positions"]) <= max_pos}
    if not in_scope:
        return {"status": "NOTHING_IN_SCOPE", "mcu": mcu,
                "all_dead": {i: d for i, d in dead.items()}, "by_idx": by_idx}

    baseline = _sweep(entries, {}, adc_pins, led_strip, dma_resolver, max_mc)

    fw_pairs = af.firmware_af_pairs(root, family)
    per_entry, rejections, needs_macro = {}, {}, {}
    for idx in in_scope:
        c, r, nm = candidates_for(by_idx[idx], entries, index_name,
                                  dma_resolver, fw_pairs)
        per_entry[idx] = c
        rejections[idx] = r
        needs_macro[idx] = nm

    keys = sorted(in_scope)
    # Include "leave unchanged" (None) so partial fixes are reachable.
    choices = [[None] + per_entry[k] for k in keys]
    combos = list(itertools.product(*choices))

    def n_changed(combo):
        return sum(1 for c in combo if c is not None)

    def n_fixed(combo):
        return sum(1 for c in combo if c is not None)

    # Prefer fixing the most entries; among equals, fewest total changes.
    combos.sort(key=lambda c: (-n_fixed(c), n_changed(c)))

    def _accept(remaps, nudge):
        trial = _sweep(entries, remaps, adc_pins, led_strip, dma_resolver,
                       max_mc, dmavar_only=nudge)
        if _regressed(baseline, trial):
            return None
        still_dead = set()
        for hz in trial.values():
            for h in hz:
                m = DEAD_RE.match(h)
                if m:
                    still_dead.add((m.group(1), m.group(2)))
        if any((in_scope[k]["tim"], in_scope[k]["ch"]) in still_dead for k in remaps):
            return None
        return trial

    best = None
    # Pass 1: remaps alone. Pass 2 (only if pass 1 finds nothing): allow a
    # co-fix dmavar nudge on an unrelated, healthy entry that happens to be
    # holding the stream the remap needs -- see find_cofix()'s docstring.
    for allow_cofix in (False, True):
        for combo in combos:
            if n_changed(combo) == 0:
                continue
            remaps = {k: c for k, c in zip(keys, combo) if c is not None}
            trial = _accept(remaps, None)
            if trial is not None:
                best = (remaps, trial, {})
                break
            if not allow_cofix:
                continue
            nudge = find_cofix(entries, remaps, baseline, adc_pins, led_strip,
                               dma_resolver, max_mc, set(dead))
            if nudge:
                trial = _accept(remaps, nudge)
                if trial is not None:
                    best = (remaps, trial, nudge)
                    break
        if best is not None:
            break

    return {"status": "OK", "mcu": mcu, "index": index_name, "family": family,
            "entries": entries, "by_idx": by_idx, "in_scope": in_scope,
            "all_dead": dead, "baseline": baseline, "best": best,
            "per_entry": per_entry, "rejections": rejections,
            "needs_macro": needs_macro, "max_mc": max_mc}


def _def_tim_span(line):
    """(start, end) covering `DEF_TIM(...)` in `line`, found by counting
    parentheses from the opening one. A regex cannot be trusted here: these
    lines routinely carry trailing comments containing their own parens and
    digits (e.g. `// S5 D(2,4,7)`), and a greedy `.*` pattern happily
    rewrites a digit inside the COMMENT instead of the real dmavar
    argument -- silently emitting a "suggestion" identical to the original
    line but with a corrupted comment. Found exactly that way on
    MATEKF405SE."""
    i = line.find("DEF_TIM(")
    if i < 0:
        return None
    depth = 0
    for j in range(i + len("DEF_TIM") , len(line)):
        if line[j] == "(":
            depth += 1
        elif line[j] == ")":
            depth -= 1
            if depth == 0:
                return i, j + 1
    return None


def rewrite_line(entry, tim, ch, dmavar):
    """The entry's original source line with tim/ch/dmavar substituted, so
    the printed suggestion is copy-pasteable and keeps the original
    comment verbatim. Falls back to a synthesized line if it doesn't
    parse."""
    line = entry.line or ""
    span = _def_tim_span(line)
    fallback = (f"DEF_TIM({tim}, {ch}, {entry.pin}, <usage>, <flags>, {dmavar}),"
                f"  // {entry.label}")
    if span is None:
        return fallback
    start, end = span
    inner = line[start + len("DEF_TIM("):end - 1]
    # Split on top-level commas only (a usage expression can contain none
    # here, but be safe about nested parens).
    parts, depth, buf = [], 0, ""
    for chx in inner:
        if chx == "(":
            depth += 1
        elif chx == ")":
            depth -= 1
        if chx == "," and depth == 0:
            parts.append(buf)
            buf = ""
        else:
            buf += chx
    parts.append(buf)
    if len(parts) != 6:
        return fallback

    def sub(part, value):
        stripped = part.strip()
        return part.replace(stripped, str(value), 1) if stripped else f" {value}"

    parts[0] = sub(parts[0], tim)
    parts[1] = sub(parts[1], ch)
    parts[5] = sub(parts[5], dmavar)
    return line[:start] + "DEF_TIM(" + ",".join(parts) + ")" + line[end:]


def report(target, res, min_pos, max_pos):
    print(f"\n{'=' * 74}\n{target}")
    st = res["status"]
    if st == "LOAD_FAILED":
        print("  SKIPPED: could not load target (no target.c, or unsupported family)")
        return
    if st == "CONDITIONAL":
        print("  N/A: timerHardware[] has #if/#ifdef-guarded DEF_TIM lines, so "
              "positions from the flattened array are unreliable.\n"
              "       Isolate each build variant with make_pwm_shadow.sh and "
              "re-run against the shadow.")
        return
    if st == "NO_DATASHEET":
        print(f"  UNVERIFIABLE: no indexed datasheet for MCU '{res['mcu']}' "
              f"(see af_tables.MCU_TO_INDEX). Pin capability cannot be "
              f"confirmed; do NOT guess from another F4 variant's table.")
        return
    if st == "NOTHING_IN_SCOPE":
        n = len(res.get("all_dead", {}))
        print(f"  no SILENT_DEAD_MOTOR at bucket position {min_pos}..{max_pos} "
              f"({n} dead output(s) outside that range)")
        return

    by_idx, in_scope = res["by_idx"], res["in_scope"]
    print(f"  MCU {res['mcu']} (datasheet index: {res['index']})")
    for idx in sorted(in_scope):
        d, e = in_scope[idx], by_idx[idx]
        print(f"\n  DEAD: {d['tim']}_{d['ch']} on {e.pin} "
              f"(label {d['label']}, position {sorted(d['positions'])}, "
              f"first dead at motorCount={d['first_mc']})")
        opts = af.options_for_pin(res["index"], e.pin)
        print(f"    datasheet AF options for {e.pin}: "
              + ", ".join(f"{k} (AF{v})" for k, v in sorted(opts.items(), key=lambda kv: kv[1])))
        for token, why in res["rejections"][idx]:
            print(f"    rejected {token}: {why}")

    best = res["best"]
    if best is None:
        print("\n  VERDICT: NO SAFE REMAP FOUND.")
        print("    Either the pin reaches no DMA-capable timer channel at all, or "
              "every option\n    duplicates an existing compare register or "
              "introduces a new hazard.\n    The only remaining mitigation is to "
              "move the entry LATER in timerHardware[]\n    so the dead pad falls "
              "outside S1-S4 -- that renumbers the outputs, so it is a\n    "
              "documentation-affecting decision left to a human.")
        return
    remaps, trial, nudge = best
    print("\n  VERDICT: FIXABLE. Proposed DEF_TIM line(s):")
    for idx, (tim, ch, dv) in sorted(remaps.items()):
        e = by_idx[idx]
        print(f"    {e.pin}: {in_scope[idx]['tim']}_{in_scope[idx]['ch']} "
              f"-> {tim}_{ch} (dmavar {dv})")
        print(f"      {rewrite_line(e, tim, ch, dv).strip()}")
        nm = res.get("needs_macro", {}).get(idx, {}).get(f"{tim}_{ch}")
        if nm:
            print(f"      NOTE: this family has a per-pin firmware AF table and "
                  f"does NOT list {e.pin}/{tim}_{ch};\n            the build will "
                  f"fail until you add:  {nm}")
    if nudge:
        print("    plus a co-fix dmavar change on (an) unrelated, currently-healthy "
              "entry\n    that is holding the DMA stream the remap needs:")
        for idx, dv in sorted(nudge.items()):
            e = by_idx[idx]
            print(f"      {e.pin}: {e.tim}_{e.ch} dmavar {e.dmavar} -> {dv}")
            print(f"        {rewrite_line(e, e.tim, e.ch, dv).strip()}")
    unfixed = [k for k in in_scope if k not in remaps]
    if unfixed:
        print("    still dead (no safe option): "
              + ", ".join(f"{in_scope[k]['tim']}_{in_scope[k]['ch']} on {by_idx[k].pin}"
                          for k in sorted(unfixed)))
    base_all = set().union(*res["baseline"].values())
    trial_all = set().union(*trial.values())
    cleared = sorted({_kind(h) + ": " + h.split(") ")[0].split(": ", 1)[1] + ")"
                      for h in base_all - trial_all})
    print(f"    hazard delta: {len(base_all - trial_all)} cleared, "
          f"{len(trial_all - base_all)} new (must be 0)")
    for c in cleared:
        print(f"      cleared: {c}")


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("inav_root")
    p.add_argument("--target", action="append", default=[])
    p.add_argument("--targets-file")
    p.add_argument("--all-f4", action="store_true",
                   help="Scan every target with an indexed datasheet")
    p.add_argument("--min-position", type=int, default=0)
    p.add_argument("--max-position", type=int, default=3,
                   help="Default 3 = the basic-quad S1-S4 range")
    args = p.parse_args()

    root = Path(args.inav_root).expanduser().resolve()
    targets = list(args.target)
    if args.targets_file:
        targets += [l.strip() for l in Path(args.targets_file).read_text().splitlines()
                    if l.strip() and not l.startswith("#")]
    if args.all_f4:
        tdir = root / "src" / "main" / "target"
        for d in sorted(tdir.iterdir()):
            if d.is_dir() and (d / "target.c").is_file():
                _, idx = af.mcu_index_for_target(d)
                if idx is not None:
                    targets.append(d.name)
    if not targets:
        p.error("no targets given (use --target / --targets-file / --all-f4)")

    for t in targets:
        try:
            res = solve(t, root, args.min_position, args.max_position)
        except Exception as ex:  # noqa: BLE001
            print(f"\n{'=' * 74}\n{t}\n  ERROR: {ex}", file=sys.stderr)
            continue
        report(t, res, args.min_position, args.max_position)


if __name__ == "__main__":
    sys.exit(main() or 0)
