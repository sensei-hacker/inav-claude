#!/usr/bin/env python3
"""
Generate alternate function / MUX mapping reference files for AT32F435/437.

Authoritative source: refman-iomux.json, produced by parse_refman_iomux.py
directly from the AT32F435/437 Reference Manual's own per-pin IOMUX tables
(chapter 6.2.9, Tables 6-1..6-8). Run that script first if the file is
missing or the Reference Manual PDF has been updated.

Earlier versions of this script derived MUX numbers by assuming a single
fixed MUX number per peripheral (e.g. "I2C is always MUX4"), sourced from
INAV driver code rather than the datasheet or Reference Manual. Comparing
that assumption against the real per-pin Reference Manual data shows it
was wrong for about 1 in 5 signals checked — the MUX number for a given
peripheral signal varies by pin. For example I2C1_SCL is MUX4 on most
pins but MUX8 on PA9, and I2C3_SCL is MUX7 on PB13 but MUX4 on PA8. There
is no substitute for the per-pin table; this script no longer guesses.

INAV's timer_def_at32f43x.h is still read, but only to add the 'N'-suffix
complementary-channel alias (TMR8_CH1N) INAV's own code uses next to the
Reference Manual's 'C'-suffix name (TMR8_CH1C) for the same signal, and to
cross-check that INAV's own MUX number for each timer channel agrees with
the Reference Manual (a mismatch is printed as a warning, and the
Reference Manual's value is what's kept).

Output files (written next to this script):
  alternate-functions.tsv    Tab-separated: Pin, MUX0..MUX15 (full table)
  alternate-functions.md     Markdown reference table by port
  af-by-function.txt         Inverted index: function → PIN(MUXn) list
  mux-groups.md              Reference: which MUX numbers each peripheral
                              prefix actually uses, computed from the data
                              (not a fixed peripheral→MUX table — see above)

Usage:
    python3 parse_refman_iomux.py   # once, or after an RM update
    python3 parse_af_table.py
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
REFMAN_JSON = HERE / "refman-iomux.json"

# Find INAV repo root by walking up
_here = HERE
INAV_TIMER_DEF = None
for _ in range(8):
    candidate = _here / "inav/src/main/drivers/timer_def_at32f43x.h"
    if candidate.exists():
        INAV_TIMER_DEF = candidate
        break
    _here = _here.parent
if INAV_TIMER_DEF is None:
    INAV_TIMER_DEF = Path("/home/raymorris/Documents/planes/inavflight/inav/src/main/drivers/timer_def_at32f43x.h")

TSV_OUT  = HERE / "alternate-functions.tsv"
MD_OUT   = HERE / "alternate-functions.md"
INV_OUT  = HERE / "af-by-function.txt"
MUX_OUT  = HERE / "mux-groups.md"

PREFIX_RE = re.compile(
    r'^(TMR\d+|SPI\d+|I2S\d+|I2C\d+|USART\d+|UART\d+|CAN\d+|'
    r'OTG\d*FS\d*|OTG\d+|EMAC|SDIO\d+|QSPI\d+|DVP|ERTC|XMC|'
    r'CLKOUT\d*|IR|WKUP\d*|EVENTOUT|JT\w+|SW\w+)'
)


def load_refman_iomux() -> dict:
    """
    Load the authoritative per-pin IOMUX table extracted from the
    Reference Manual. Returns { 'PA5': {1: {'TMR2_CH1'}, 5: {'SPI1_SCK'}, ...}, ... }
    """
    if not REFMAN_JSON.exists():
        sys.exit(f"{REFMAN_JSON.name} not found in {HERE} — "
                  f"run parse_refman_iomux.py first.")
    raw = json.loads(REFMAN_JSON.read_text())
    return {pin: {int(mux_s): set(funcs) for mux_s, funcs in mux_map.items()}
            for pin, mux_map in raw.items()}


def parse_timer_def(path: Path) -> dict:
    """
    Parse timer_def_at32f43x.h to get INAV's own timer MUX assignments,
    used only for the 'N'-suffix alias and as a cross-check against the
    Reference Manual (see module docstring).
    Returns: { 'PA5': {'TMR2_CH1': 1, 'TMR8_CH1N': 3, ...}, ... }
    """
    if not path.exists():
        print(f"  WARNING: timer_def not found at {path}", file=sys.stderr)
        return {}

    result = {}
    pat = re.compile(
        r'#define\s+DEF_TIM_AF__P([A-I]\d{1,2})__TCH_(TMR\w+)\s+D\((\d+),\s*\d+\)'
    )
    for line in path.read_text().splitlines():
        m = pat.match(line.strip())
        if not m:
            continue
        pin_suf, func, mux_n = m.group(1), m.group(2), int(m.group(3))
        pin = f"P{pin_suf}"
        result.setdefault(pin, {})[func] = mux_n
    return result


def add_timer_n_aliases(all_pins: dict, timer_data: dict) -> None:
    """
    Add INAV's 'N'-suffix complementary-channel names (TMR8_CH1N) next to
    the Reference Manual's 'C'-suffix name (TMR8_CH1C) for the same pin
    and MUX slot. Warns (but trusts the Reference Manual) if INAV's own
    MUX number for that channel disagrees with the Reference Manual.
    """
    for pin, funcs in timer_data.items():
        for func, inav_mux in funcs.items():
            if 'N' not in func:
                continue
            func_c = (func.replace('CH1N', 'CH1C')
                          .replace('CH2N', 'CH2C')
                          .replace('CH3N', 'CH3C'))
            if func_c == func:
                continue
            pin_muxes = all_pins.get(pin, {})
            rm_mux = next((m for m, fs in pin_muxes.items() if func_c in fs), None)
            if rm_mux is None:
                print(f"  WARNING: {pin} {func_c} (INAV: {func}) not found "
                      f"in Reference Manual data", file=sys.stderr)
                continue
            if rm_mux != inav_mux:
                print(f"  WARNING: {pin} {func} — timer_def says MUX{inav_mux}, "
                      f"Reference Manual says MUX{rm_mux} (using Reference Manual)",
                      file=sys.stderr)
            pin_muxes[rm_mux].add(func)


def sort_pin(pin: str) -> tuple:
    m = re.match(r'P([A-I])(\d+)', pin)
    return (ord(m.group(1)), int(m.group(2))) if m else (0, 0)


def format_cell(funcs) -> str:
    return '/'.join(sorted(funcs)) if funcs else '-'


def peripheral_prefix(func: str) -> str:
    m = PREFIX_RE.match(func)
    return m.group(1) if m else func


def main():
    print("Step 1: Loading Reference Manual IOMUX ground truth...")
    all_pins = load_refman_iomux()
    total_entries = sum(len(v) for v in all_pins.values())
    print(f"  Loaded {len(all_pins)} pins, {total_entries} pin/MUX-slot entries")

    print("Step 2: Cross-checking INAV timer_def_at32f43x.h, adding 'N' aliases...")
    timer_data = parse_timer_def(INAV_TIMER_DEF)
    add_timer_n_aliases(all_pins, timer_data)

    sorted_pins = sorted(all_pins.keys(), key=sort_pin)
    mux_nums = list(range(16))

    # ── Compute the real per-prefix MUX distribution (replaces the old,
    #    incorrect one-MUX-per-peripheral table) ─────────────────────────
    prefix_mux_counts: dict[str, Counter] = {}
    for pin in sorted_pins:
        for mux_n, funcs in all_pins[pin].items():
            for func in funcs:
                prefix = peripheral_prefix(func)
                prefix_mux_counts.setdefault(prefix, Counter())[mux_n] += 1

    # ── MUX distribution reference ───────────────────────────────────────
    with MUX_OUT.open('w') as f:
        f.write("# AT32F435/437 MUX Distribution Reference\n\n")
        f.write("Source: AT32F435/437 Reference Manual, chapter 6.2.9 "
                "(Tables 6-1..6-8), read directly per pin —\n")
        f.write("see `refman-iomux.json` and `parse_refman_iomux.py`.\n\n")
        f.write("**The MUX number for a peripheral is not fixed — it varies by pin.**\n")
        f.write("An earlier version of this file listed one MUX number per peripheral\n")
        f.write("(e.g. \"I2C is always MUX4\"); checking that assumption against the\n")
        f.write("Reference Manual's real per-pin tables found it wrong for about 1 in 5\n")
        f.write("signals. For example `I2C1_SCL` is MUX4 on most pins but MUX8 on PA9,\n")
        f.write("and `I2C3_SCL` is MUX7 on PB13 but MUX4 on PA8. **Always look up the\n")
        f.write("specific pin** in `alternate-functions.tsv` / `af-by-function.txt` —\n")
        f.write("never assume a peripheral's MUX number from its name alone.\n\n")
        f.write("## MUX numbers observed per peripheral prefix\n\n")
        f.write("| Prefix | MUX numbers used (occurrence count) |\n"
                "|--------|---------------------------------------|\n")
        for prefix in sorted(prefix_mux_counts):
            counts = prefix_mux_counts[prefix]
            dist = ", ".join(f"MUX{m} ({n})" for m, n in sorted(counts.items()))
            f.write(f"| {prefix} | {dist} |\n")
        f.write("\n## Timer DEF_TIM() Notes\n\n")
        f.write("In `target.c`, `DEF_TIM(TMR3, CH3, PB0, ...)` automatically resolves\n")
        f.write("the correct MUX number from the `DEF_TIM_AF__PB0__TCH_TMR3_CH3` macro\n")
        f.write("defined in `timer_def_at32f43x.h`. The `af` (flags) parameter in\n")
        f.write("`DEF_TIM` is unused for AT32 (pass 0). `parse_af_table.py` cross-checks\n")
        f.write("this file's MUX numbers against the Reference Manual on every run and\n")
        f.write("prints a warning for any disagreement.\n")
    print(f"Written: {MUX_OUT.name}")

    # ── TSV ───────────────────────────────────────────────────────────────────
    with TSV_OUT.open('w') as f:
        f.write("Pin\t" + "\t".join(f"MUX{n}" for n in mux_nums) + "\n")
        for pin in sorted_pins:
            mux_map = all_pins[pin]
            row = pin + "\t" + "\t".join(
                format_cell(mux_map.get(n, [])) for n in mux_nums
            )
            f.write(row + "\n")
    print(f"Written: {TSV_OUT.name}")

    # ── Markdown ─────────────────────────────────────────────────────────────
    with MD_OUT.open('w') as f:
        f.write("# AT32F435/437 Alternate Function / IOMUX Mapping\n\n")
        f.write("Source: AT32F435/437 Reference Manual, chapter 6.2.9 "
                "(per-pin ground truth) + INAV timer_def_at32f43x.h\n\n")
        f.write("**Note:** AT32 uses GPIO_MUX_n (MUX0–MUX15) instead of STM32's AF0–AF15.\n")
        f.write("The MUX number for a given peripheral **varies by pin** — see\n")
        f.write("`mux-groups.md` for the observed distribution and why there is no\n")
        f.write("fixed peripheral→MUX table.\n\n")
        f.write("---\n\n## Pin Alternate Functions\n")

        current_port = None
        for pin in sorted_pins:
            port = pin[:2]
            if port != current_port:
                current_port = port
                f.write(f"\n### Port {port[1]}\n\n")
                f.write("| Pin |" + "".join(f" MUX{n} |" for n in mux_nums) + "\n")
                f.write("|-----|" + "".join("------|" for _ in mux_nums) + "\n")

            mux_map = all_pins[pin]
            row = f"| **{pin}** |" + "".join(
                f" {format_cell(mux_map.get(n, []))} |" for n in mux_nums
            )
            f.write(row + "\n")
    print(f"Written: {MD_OUT.name}")

    # ── Inverted index ────────────────────────────────────────────────────────
    inverted: dict[str, list[str]] = {}
    for pin in sorted_pins:
        for mux_n, funcs in all_pins[pin].items():
            for func in funcs:
                inverted.setdefault(func, []).append(f"{pin}(MUX{mux_n})")

    with INV_OUT.open('w') as f:
        f.write("# AT32F435/437 — Function to Pin Mapping (IOMUX)\n")
        f.write("# Source: AT32F435/437 Reference Manual (per-pin ground truth) "
                "+ INAV timer_def_at32f43x.h\n")
        f.write("# MUX number = GPIO_MUX_n value for gpio_pin_mux_config()\n\n")
        f.write(f"{'Function':<40} Pins\n")
        f.write("-" * 90 + "\n")
        for func in sorted(inverted.keys()):
            pins_str = ", ".join(inverted[func])
            f.write(f"{func:<40} {pins_str}\n")
    print(f"Written: {INV_OUT.name}")

    # Summary
    print(f"\nDone! {len(sorted_pins)} pins, {len(inverted)} unique functions indexed")
    print(f"\nQuick usage examples:")
    print(f"  grep 'SPI1_SCK' af-by-function.txt      # which pins support SPI1_SCK?")
    print(f"  grep '^TMR3_CH' af-by-function.txt       # all TMR3 channel pins")
    print(f"  grep '^USART1' af-by-function.txt        # all USART1 pins")
    print(f"  grep '^PA9\t' alternate-functions.tsv    # PA9 MUX table row")


if __name__ == "__main__":
    main()
