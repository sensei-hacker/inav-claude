#!/usr/bin/env python3
"""
check_timer_pin_af.py -- flags a DEF_TIM(tim, ch, pin, ...) triple in
target.c whose (timer, channel) is NOT routable to that pin on that MCU,
checked against the indexed datasheet alternate-function table
(claude/developer/docs/targets/<mcu>/alternate-functions.tsv).

WHY THIS CANNOT BE LEFT TO THE COMPILER (STM32F4 ONLY)
=======================================================
On F4 there is no per-pin AF table in the firmware. drivers/
timer_def_stm32f4xx.h line 25 builds the AF number straight from the timer
NAME:

    #define DEF_TIM(tim, ch, pin, usage, flags, dmavar) \
        { tim, IO_TAG(pin), DEF_TIM_CHNL_ ## ch, ..., GPIO_AF_ ## tim, ... }

GPIO_AF_TIM1 == 1, GPIO_AF_TIM8 == 3, GPIO_AF_TIM12 == 9 and so on. Nothing
checks that the (timer, channel) named actually reaches the pin named, so a
wrong triple BUILDS CLEANLY and silently misconfigures the pad: the GPIO is
muxed to that timer's AF -- i.e. to whatever signal of that timer the
silicon routes to that pad -- while the driver goes on to program the
compare register and output-enable bit of the channel the firmware *thinks*
it asked for. Result: an output that never drives, with no compile error, no
boot error, and nothing in the OSD.

F7 / H7 / AT32 use per-pin DEF_TIM_AF__P<pin>__TCH_<TIM>_<CH> tables
(timer_def_stm32f7xx.h / _stm32h7xx.h / _at32f43x.h), so a bad triple there
is a build failure instead. Findings on those families are still reported
(the datasheet is the better authority for WHICH channel is right), but they
are labelled as compile-time-caught rather than silent.

THREE FINDING KINDS
====================
  N_MISMATCH     the pin carries the COMPLEMENTARY output (TIMn_CHmN) but
                 the target declares TIMn_CHm (or vice versa). This is not
                 cosmetic: impl_timerPWMConfigChannel() (drivers/
                 timer_impl_stdperiph.c) branches on TIMER_OUTPUT_N_CHANNEL,
                 which DEF_TIM_OUTPUT__CH<m>N sets, to decide whether to
                 enable CCxE (main output) or CCxNE (complementary output)
                 and which polarity register to use. Declare the wrong one
                 and the enable bit for the signal that physically reaches
                 the pad is never set -- the pad stays idle. The DMA request
                 line is shared between CHx and CHxN (timer_def.h aliases
                 BTCH_TIMn_CHmN to BTCH_TIMn_CHm), so DMA analysis will look
                 perfectly healthy while the output is dead.
  WRONG_CHANNEL  the timer IS on the pin, but on a different channel than
                 declared (e.g. PB0 is TIM3_CH3, not TIM3_CH4). The AF mux
                 is right by luck -- both channels of the same timer share
                 one AF number -- so the pad is connected to the timer, but
                 to the other channel's compare output, which this entry
                 never enables or feeds.
  TIMER_NOT_ON_PIN  the pin has no route to that timer at all.

Usage: ./check_timer_pin_af.py <inav_checkout_root> [--target NAME]
Example: ./check_timer_pin_af.py ~/Documents/planes/inavflight/inav --target BLUEJAYF4

Options:
  --target NAME    only check this target directory name
  --show-unknown   also list targets skipped because their MCU has no
                   indexed datasheet here (F411/F427/H7/RP2350) -- these are
                   NOT verified, and F4 members among them have the same
                   silent-failure exposure, so they need a manual pass

Findings are a checklist, not a pass/fail gate, but this check has a much
lower false-positive rate than its siblings: the datasheet AF table is
authoritative, and the only expected noise is a pin/format the TSV parser
did not recognise (reported as an explicit parse gap, never as a finding).
"""
import argparse
import sys
from pathlib import Path

import af_tables as af


def check_target(target_dir: Path):
    """Returns (mcu_token, index_name, findings, parse_gaps).

    index_name None -> not checkable (no datasheet indexed for this MCU);
    findings is a list of (lineno, pin, declared, kind, detail, raw_line)."""
    mcu, index = af.mcu_index_for_target(target_dir)
    target_c = target_dir / "target.c"
    if index is None or not target_c.is_file():
        return mcu, index, [], []

    table = af.load_af_table(index)
    findings, gaps = [], []
    for lineno, raw, tim, ch, pin in af.iter_def_tim(
        target_c.read_text(errors="ignore")
    ):
        declared = f"{tim}_{ch}"
        opts = table.get(pin)
        if not opts:
            gaps.append((lineno, pin, "pin not present in the parsed AF table"))
            continue
        if declared in opts:
            continue
        # CHx <-> CHxN: same compare register, DIFFERENT output-enable bit.
        flipped = declared[:-1] if declared.endswith("N") else declared + "N"
        if flipped in opts:
            findings.append((lineno, pin, declared, "N_MISMATCH",
                             f"pin carries {flipped} (AF{opts[flipped]}), not {declared}",
                             raw))
            continue
        same_timer = sorted(o for o in opts if o.startswith(tim + "_"))
        if same_timer:
            findings.append((lineno, pin, declared, "WRONG_CHANNEL",
                             f"{tim} reaches this pin only as {', '.join(same_timer)}",
                             raw))
        else:
            findings.append((lineno, pin, declared, "TIMER_NOT_ON_PIN",
                             f"pin offers only {', '.join(sorted(opts))}",
                             raw))
    return mcu, index, findings, gaps


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("inav_root", nargs="?", default=".")
    ap.add_argument("--target", help="Only check this target directory name")
    ap.add_argument("--show-unknown", action="store_true",
                    help="List targets skipped for lack of an indexed datasheet")
    args = ap.parse_args()

    root = Path(args.inav_root).expanduser().resolve() / "src" / "main" / "target"
    if not root.is_dir():
        print(f"error: no target dir under {args.inav_root}", file=sys.stderr)
        return 2

    dirs = sorted(d for d in root.iterdir() if d.is_dir() and (d / "target.c").is_file())
    if args.target:
        dirs = [d for d in dirs if d.name == args.target]
        if not dirs:
            print(f"error: no such target: {args.target}", file=sys.stderr)
            return 2

    total_findings = 0
    checked = skipped = 0
    unknown = []
    all_gaps = []
    for d in dirs:
        mcu, index, findings, gaps = check_target(d)
        if index is None:
            skipped += 1
            unknown.append((d.name, mcu or "unknown"))
            continue
        checked += 1
        all_gaps += [(d.name,) + g for g in gaps]
        if not findings:
            continue
        silent = index in af.SILENT_AF_FAMILIES
        tag = ("SILENT at build time -- F4 has no per-pin AF table, this compiles"
               if silent else "would fail to compile -- per-pin AF table exists on this family")
        print(f"\n{d.name}  [{mcu}]  ({tag})")
        for lineno, pin, declared, kind, detail, raw in findings:
            total_findings += 1
            print(f"  target.c:{lineno}: {kind}: {pin} declared as {declared} -- {detail}")
            print(f"      {raw.strip()}")

    print(f"\n{'-' * 70}")
    print(f"checked {checked} target(s) against indexed datasheets; "
          f"{total_findings} finding(s)")
    if all_gaps:
        print(f"{len(all_gaps)} AF-table parse gap(s) (NOT findings -- the pin was "
              f"not found in the TSV, so nothing was verified for that line):")
        for name, lineno, pin, why in all_gaps:
            print(f"  {name} target.c:{lineno} {pin}: {why}")
    if skipped:
        print(f"{skipped} target(s) skipped -- no datasheet indexed for their MCU. "
              f"F411/F427 targets among these have the SAME silent-failure exposure "
              f"as F405 and are unverified.")
        if args.show_unknown:
            for name, mcu in unknown:
                print(f"  {name}  [{mcu}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
