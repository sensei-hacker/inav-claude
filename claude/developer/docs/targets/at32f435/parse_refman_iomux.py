#!/usr/bin/env python3
"""
Extract the authoritative per-pin IOMUX (GPIO_MUX0-15) table from the
AT32F435/437 Reference Manual, chapter 6.2.9 "IOMUX input/output"
(Tables 6-1 through 6-8, one per GPIO port A-H).

Unlike the datasheet (which only lists which functions exist on a pin,
not which MUX number selects them) and unlike guessing MUX numbers from
INAV driver source, this reads the Reference Manual's own per-pin MUX
tables directly — the only fully authoritative source for this mapping.

The RM's tables are borderless (no gridlines pdfplumber can detect), and
a naive pdftotext -layout reconstruction misassigns wrapped multi-line
cells to the wrong pin row (a cell's first line can render above the
pin-name line it belongs to). This script instead uses pdfplumber's
per-word (x, top) coordinates and assigns each word to its nearest pin
row by vertical position and to its column by nearest MUX-header x0,
which matches the PDF's real cell geometry regardless of text wrapping.

Output: refman-iomux.json — { "PA0": {"1": ["TMR2_CH1", ...], "4": [...]}, ... }
        (MUX numbers as string keys, functions as sorted lists)

Known limitation: a compound signal name that wraps across two PDF text lines
(e.g. "QSPI1_CS" printed as "QSPI1_C" then "S" on the next line within the same
cell) is extracted as two separate tokens rather than being rejoined, since nothing
distinguishes that from two genuinely different signals stacked in one cell. This
affects a handful of QSPI/XMC signals only; core signals (TMR/SPI/I2C/USART/UART/CAN)
were spot-checked against the raw PDF and are unaffected.

Usage:
    pip install pdfplumber
    python3 parse_refman_iomux.py
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
PDF = (HERE / "datasheets_application_notes/reference-manaul-RM_AT32F435_437_EN_V2.06.pdf").resolve()
OUT = HERE / "refman-iomux.json"

PIN_RE = re.compile(r'^P[A-H]\d{1,2}$')
MUX_HDR_RE = re.compile(r'^MUX(\d{1,2})$')
# Real cell content is always a signal/function name in caps (TMR2_CH1,
# OTG2_D-, USART2_RTS_DE, ...) — filters out stray prose words that leak
# in from the note/heading text immediately following the last table.
FUNC_TOKEN_RE = re.compile(r'^[A-Z][A-Z0-9_+\-/]*$')
# Every real IOMUX signal name carries a peripheral instance number or an
# underscore-separated suffix (TMR2_CH1, I2C3_SMBA, CLKOUT1, IR_OUT) except
# for this small closed set of bare debug/system signals — this rejects
# bare all-caps prose words (GPIO, IOMUX, MUX) from trailing note text
# without a per-word denylist.
BARE_FUNC_WHITELIST = {
    "JTMS", "JTCK", "JTDI", "JTDO", "JTRST",
    "SWDIO", "SWCLK", "SWO", "EVENTOUT",
}


def looks_like_signal(token: str) -> bool:
    if not FUNC_TOKEN_RE.match(token):
        return False
    if token in BARE_FUNC_WHITELIST:
        return True
    return any(c.isdigit() or c == "_" for c in token)


def pin_rank(pin: str) -> tuple:
    m = re.match(r'P([A-H])(\d+)', pin)
    return (ord(m.group(1)), int(m.group(2)))

# Pin-column words sit at the page's leftmost text x0; a "Pin" header word
# confirms it. Anything past this x is a data column, not the pin name.
PIN_COLUMN_MAX_X = 115.0

# Section 6.2.9 starts with "Table 6-1 Port A ..." and ends where 6.2.10 begins.
START_MARKER = "Table 6-1"
END_MARKER = "6.2.10"


TOC_DOTS_RE = re.compile(r'\.{5,}')


def find_page_range(pdf) -> tuple[int, int]:
    start = end = None
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        if start is None and START_MARKER in text:
            idx = text.index(START_MARKER)
            # Skip the front-matter "List of Tables" entry, which repeats
            # this same title followed by a dot-leader and a page number.
            if not TOC_DOTS_RE.search(text[idx:idx + 200]):
                start = i
        if start is not None and END_MARKER in text:
            end = i
            break
    if start is None or end is None:
        sys.exit(f"Could not locate IOMUX table page range "
                  f"(start={start}, end={end}) — RM layout may have changed.")
    return start, end


def cluster_rows(words: list, tol: float = 1.5) -> list:
    """Group words into text-rows by 'top' coordinate (within tol points)."""
    rows = []
    for w in sorted(words, key=lambda w: w["top"]):
        placed = False
        for row in rows:
            if abs(row["top"] - w["top"]) <= tol:
                row["words"].append(w)
                placed = True
                break
        if not placed:
            rows.append({"top": w["top"], "words": [w]})
    return rows


def extract_page(page, carry_pin: str | None, min_rank: tuple):
    """
    Returns (entries, last_pin, last_rank) where entries is a list of
    (pin, mux_num, function_token) tuples found on this page, last_pin is
    the last pin anchor seen (to carry into the next page), and last_rank
    is its pin_rank() (to reject any out-of-order anchor on later pages —
    the RM's per-page trailing notes/heading text can contain a real pin
    name like "PA0" as prose, which would otherwise be mistaken for a new
    table row).
    """
    words = page.extract_words()
    rows = cluster_rows(words)
    rows.sort(key=lambda r: r["top"])

    # The RM immediately follows the last table (end of Port H, MUX8-15)
    # with a "Note: ..." footnote and then the next section's heading, all
    # on the same physical page — drop everything from the first such
    # marker onward so it can't be swept into the last pin's row.
    for row in rows:
        texts = [w["text"] for w in row["words"]]
        if any(t.startswith("Note:") or t in ("6.2.10", "6.2.11") for t in texts):
            rows = [r for r in rows if r["top"] < row["top"]]
            break

    # Pass 1: find header rows (mux column x-positions).
    headers = []       # list of (top, {mux_num: x0})
    for row in rows:
        mux_cols = {}
        for w in row["words"]:
            m = MUX_HDR_RE.match(w["text"])
            if m:
                mux_cols[int(m.group(1))] = w["x0"]
        if len(mux_cols) >= 4:
            headers.append((row["top"], mux_cols))

    if not headers:
        return [], carry_pin, min_rank

    # Pass 2: pin anchors, monotonic within each header's span but reset
    # at every header boundary — a MUX0-7 table is immediately followed
    # by that same port's MUX8-15 continuation table, which restarts back
    # at its lowest pin (e.g. PA0 again), which is not an ordering
    # violation. Only a backward jump *within* one header's span (e.g. a
    # stray "PA0" in trailing prose reusing the last real header) is noise.
    anchors = []        # list of (top, pin_name)
    header_idx = -1
    for row in rows:
        while header_idx + 1 < len(headers) and headers[header_idx + 1][0] <= row["top"] + 0.5:
            header_idx += 1
            min_rank = (0, 0)
        pin_here = None
        for w in row["words"]:
            if PIN_RE.match(w["text"]) and w["x0"] < PIN_COLUMN_MAX_X:
                pin_here = w["text"]
        if pin_here and pin_rank(pin_here) >= min_rank:
            anchors.append((row["top"], pin_here))
            min_rank = pin_rank(pin_here)

    if carry_pin is not None:
        # Virtual anchor far above the page so top-of-page wrapped
        # continuation lines (before the first real anchor) still
        # attach to the previous page's last pin.
        anchors = [(-10_000.0, carry_pin)] + anchors

    entries = []
    for row in rows:
        # Active header = the last header whose top <= this row's top.
        active = None
        for h_top, h_cols in headers:
            if h_top <= row["top"] + 0.5:
                active = h_cols
            else:
                break
        if active is None:
            continue

        # Nearest pin anchor by vertical distance.
        if not anchors:
            continue
        row_pin = min(anchors, key=lambda a: abs(a[0] - row["top"]))[1]

        header_xs = sorted(active.items(), key=lambda kv: kv[1])
        for w in row["words"]:
            if MUX_HDR_RE.match(w["text"]):
                continue
            if PIN_RE.match(w["text"]):
                continue  # a pin name is never itself a MUX function value
            if w["text"] in ("Pin",):
                continue
            if not looks_like_signal(w["text"]):
                continue
            # Column = header with the largest x0 <= word x0 (+tolerance),
            # falling back to the nearest header if the word starts left
            # of every header (shouldn't normally happen post pin-column).
            best_mux = None
            for mux_n, x0 in header_xs:
                if x0 <= w["x0"] + 2.0:
                    best_mux = mux_n
                else:
                    break
            if best_mux is None:
                best_mux = header_xs[0][0]
            entries.append((row_pin, best_mux, w["text"]))

    last_pin = anchors[-1][1] if anchors else carry_pin
    return entries, last_pin, min_rank


def main():
    try:
        import pdfplumber
    except ImportError:
        sys.exit("pdfplumber not installed. Run: pip install pdfplumber")

    if not PDF.exists():
        sys.exit(f"PDF not found: {PDF}")

    result: dict[str, dict[int, set]] = {}

    with pdfplumber.open(PDF) as pdf:
        start, end = find_page_range(pdf)
        print(f"Scanning RM pages {start + 1}-{end + 1} "
              f"(0-indexed {start}-{end}) for IOMUX tables...")

        carry_pin = None
        min_rank = (0, 0)
        for i in range(start, end + 1):
            entries, carry_pin, min_rank = extract_page(pdf.pages[i], carry_pin, min_rank)
            for pin, mux_n, token in entries:
                result.setdefault(pin, {}).setdefault(mux_n, set()).add(token)

    out = {pin: {str(mux_n): sorted(funcs) for mux_n, funcs in mux_map.items()}
           for pin, mux_map in result.items()}

    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    total_entries = sum(len(v) for v in out.values())
    print(f"Extracted {len(out)} pins, {total_entries} pin/MUX-slot entries "
          f"-> {OUT.name}")


if __name__ == "__main__":
    main()
