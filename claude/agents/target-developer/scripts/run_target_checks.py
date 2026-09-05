#!/usr/bin/env python3
"""
run_target_checks.py -- runs the standard set of static target-config checks
in one pass.

Runs, in order:
  1. check_macro_typos.py    -- flags target.h #defines that look like typos
                                 of a real INAV macro (e.g. BEEPER_PIN instead
                                 of BEEPER)
  2. check_dma_conflicts.py  -- flags STM32H7 DMA stream (dmaopt) collisions,
                                 both timer-vs-timer and timer-vs-ADC's
                                 hardwired stream, with CERTAIN/NOTICE severity
  3. check_pin_conflicts.py  -- flags a single physical pin assigned to more
                                 than one peripheral macro
  4. check_default_features.py -- flags a target.h with no DEFAULT_FEATURES
                                 macro at all (every feature silently off) or
                                 one that looks suspiciously thin
  5. check_board_identifier.py -- flags a TARGET_BOARD_IDENTIFIER that isn't
                                 exactly 4 chars, or collides with another
                                 target's
  6. check_serial_port_count.py -- flags a SERIAL_PORT_COUNT that doesn't
                                 match the VCP/UART/softserial macros actually
                                 defined, and a dead FEATURE_SOFTSERIAL bit
                                 with no backing USE_SOFTSERIALn
  7. check_target_invariants.py -- three small single-rule regression guards:
                                 BEEPER_PWM_FREQUENCY needs a DEF_TIM entry,
                                 GYRO_n_EXTI_PIN needs BUSDEV_REGISTER_SPI_TAG,
                                 AT32 UARTs need an explicit TX_PIN
  8. check_timer_pin_af.py   -- flags a DEF_TIM(tim, ch, pin) triple whose
                                 (timer, channel) is not routable to that pin
                                 per the indexed datasheet AF table. On F4
                                 this class of bug COMPILES CLEANLY (no
                                 per-pin AF table exists in the firmware --
                                 the AF is derived from the timer name alone)
                                 and just leaves the output silently dead

None of these are pass/fail gates -- each prints a checklist for a human to
verify; false positives are expected and explained in each script's own
docstring (read that script's --help / top-of-file comment for what a given
finding does and doesn't prove). Run this before opening a PR for a new or
modified target, and whenever fixing one of these classes of bug, to confirm
the fix is actually clean rather than just fixing the one reported instance.

Usage: ./run_target_checks.py <inav_checkout_root> [--target NAME]
Example: ./run_target_checks.py ~/Documents/planes/inavflight/inav --target AXISFLYINGH743PRO

Options:
  --target NAME   only check this target directory name (passed through to
                   every check below; omit to scan the whole tree)

Add new standard checks by appending to the CHECKS list below -- each entry
is (title, script filename), and every listed script must accept the same
`<inav_root> [--target NAME]` calling convention as the checks above.
"""
import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

CHECKS = [
    ("Macro typos", "check_macro_typos.py"),
    ("DMA/dmaopt collisions (STM32H7)", "check_dma_conflicts.py"),
    ("Pin reuse across peripherals", "check_pin_conflicts.py"),
    ("DEFAULT_FEATURES missing/thin", "check_default_features.py"),
    ("TARGET_BOARD_IDENTIFIER length/uniqueness", "check_board_identifier.py"),
    ("SERIAL_PORT_COUNT / softserial feature bit", "check_serial_port_count.py"),
    ("Misc target invariants", "check_target_invariants.py"),
    ("DEF_TIM pin/timer/channel vs datasheet AF table", "check_timer_pin_af.py"),
]


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("inav_root", nargs="?", default=".", help="Path to an INAV checkout")
    ap.add_argument("--target", help="Only check this target directory name")
    args, extra = ap.parse_known_args()

    errored = []
    for title, script in CHECKS:
        path = SCRIPT_DIR / script
        # flush=True: without it, these prints sit in Python's block buffer
        # (stdout isn't a tty once piped/captured) while the subprocess below
        # writes straight to the inherited fd -- headers would all appear
        # after every check's actual output instead of in front of it.
        print(f"\n{'=' * 70}\n{title} ({script})\n{'=' * 70}", flush=True)
        if not path.is_file():
            print(f"SKIPPED -- script not found: {path}", flush=True)
            continue
        cmd = [sys.executable, str(path), args.inav_root]
        if args.target:
            cmd += ["--target", args.target]
        cmd += extra
        result = subprocess.run(cmd)
        if result.returncode != 0:
            errored.append(title)

    print(f"\n{'=' * 70}")
    if errored:
        print(
            f"{len(errored)} check(s) hit an error (a script/setup problem, not "
            f"the same as 'found findings'): {', '.join(errored)}"
        )
    else:
        print(
            "All checks ran to completion. Review any findings above by hand -- "
            "these are checklists, not a pass/fail gate."
        )


if __name__ == "__main__":
    main()
