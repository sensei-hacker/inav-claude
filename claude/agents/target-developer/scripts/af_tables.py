#!/usr/bin/env python3
"""
af_tables.py -- shared loader for the indexed MCU alternate-function (AF)
tables under claude/developer/docs/targets/<mcu>/alternate-functions.tsv,
plus the MCU-detection logic that maps a target directory to the right one.

WHY THIS EXISTS
================
On STM32F4 there is NO per-pin AF table in the firmware at all. See
drivers/timer_def_stm32f4xx.h:

    #define DEF_TIM(tim, ch, pin, usage, flags, dmavar) \
        { tim, IO_TAG(pin), DEF_TIM_CHNL_ ## ch, ..., GPIO_AF_ ## tim, ... }

the pin's alternate-function number is derived purely from the TIMER NAME
(GPIO_AF_TIM1 == 1, GPIO_AF_TIM8 == 3, GPIO_AF_TIM12 == 9, ...), with no
cross-check whatsoever that the named (timer, channel) is actually routable
to the named pin. So a WRONG DEF_TIM(tim, ch, pin) triple on F4 COMPILES
CLEANLY and just misconfigures the pin at runtime: the GPIO gets muxed to
that timer's AF, but to whichever of that timer's signals the silicon
actually routes to that pad -- not the channel the firmware then goes on to
program the compare register and output-enable bit for. The output is dead
(or, in the CHx-vs-CHxN case, driven from the wrong enable bit), silently,
with no boot error.

F7 / H7 / AT32 do NOT have this hole: their timer_def_stm32f7xx.h /
timer_def_stm32h7xx.h / timer_def_at32f43x.h use a per-pin
DEF_TIM_AF__P<pin>__TCH_<TIM>_<CH> macro table, so an invalid triple fails
to compile. That firmware table is, however, only populated with the pairs
existing targets happen to use -- it is NOT a complete map of the chip, so
it answers "will this build" but not "what else could this pin do". For the
latter, the datasheet TSV loaded here is the authority.

TABLE FORMAT
=============
Tab-separated, first column `Pin`, then 16 AF columns:

    Pin   AF0   AF1          AF2        AF3         ...
    PB14  -     TIM1_CH2N    -          TIM8_CH2N   ...   TIM12_CH1 ...

Cells can hold several forms this module normalizes:
  - plain            TIM3_CH3
  - complementary    TIM1_CH2N          (CHxN: the inverted output of the
                                        SAME compare register as CHx -- NOT
                                        an independent channel; see
                                        timer_def.h's BTCH_TIM1_CH2N ->
                                        BTCH_TIM1_CH2 alias)
  - ETR-shared       TIM2_CH1_ETR   or  TIM2_CH1/TIM2_ETR   (both mean the
                                        channel IS available on that pin)
  - multi-function   A/B                (split on '/')
AT32's table uses TMRn rather than TIMn; both are normalized to TIMn here so
callers can compare against target.c tokens uniformly (AT32 target.c writes
DEF_TIM(TMR4, CH1, ...), so callers should normalize their own tokens with
norm_tim() too).

WHAT IS AND ISN'T INDEXED
==========================
Indexed (datasheet TSV present): stm32f405, stm32f722, stm32f745, stm32f765,
at32f435. NOT indexed: stm32f411, stm32f427, stm32h7, rp2350 -- for those,
mcu_index_for_target() returns None and callers MUST say so rather than
guess. Do not substitute a different F4 table for F411/F427: "F4" pools
parts with genuinely DIFFERENT AF tables, and assuming otherwise is exactly
the mistake that motivated indexing the datasheets in the first place.
"""
import csv
import re
from pathlib import Path

DOCS_ROOT = (
    Path(__file__).resolve().parents[3] / "developer" / "docs" / "targets"
)

# target_<token>(NAME ...) in a target's CMakeLists.txt -> docs/targets/<dir>
# None == deliberately known-unavailable (say so, never guess a near-match).
MCU_TO_INDEX = {
    "stm32f405xg": "stm32f405",
    "stm32f411xe": None,
    "stm32f427xg": None,
    "stm32f722xe": "stm32f722",
    "stm32f745xg": "stm32f745",
    "stm32f765xi": "stm32f765",
    "stm32f765xg": "stm32f765",
    "stm32h743xi": None,
    "at32f43x_xgt7": "at32f435",
    "at32f43x_xmt7": "at32f435",
    "rp2350": None,
}

# Families whose timer_def_*.h has NO per-pin AF table, so a wrong
# DEF_TIM(tim, ch, pin) triple compiles silently instead of erroring.
# Everything else gets caught by the compiler; a finding there means the
# target does not build at all, which is a different (louder) problem.
SILENT_AF_FAMILIES = {"stm32f405", "stm32f411", "stm32f427"}

_TARGET_MCU_RE = re.compile(r"\btarget_([a-z0-9_]+)\s*\(", re.I)
_TIMCH_RE = re.compile(r"^(?:TIM|TMR)(\d+)_(CH\d+N?)(?:_ETR)?$", re.I)


def norm_tim(tok: str) -> str:
    """TMR4 -> TIM4, tim4 -> TIM4. AT32 target.c and its AF table both spell
    timers TMRn; everything else spells them TIMn. Normalize so one lookup
    key works for every family."""
    m = re.fullmatch(r"(?:TIM|TMR)(\d+)", tok.strip(), re.I)
    return f"TIM{m.group(1)}" if m else tok.strip().upper()


def base_channel(ch: str) -> str:
    """CH2N -> CH2. An N-channel is the complementary output of the SAME
    compare register / same capture-compare event, not a separate channel --
    so for duplicate detection and DMA-request lookup it must collapse onto
    its base. See timer_def.h (#define BTCH_TIM1_CH2N BTCH_TIM1_CH2)."""
    ch = ch.strip().upper()
    return ch[:-1] if ch.endswith("N") else ch


def mcu_token_for_target(target_dir: Path):
    """The `target_<token>(...)` MCU token from a target's CMakeLists.txt,
    lowercased (e.g. 'stm32f405xg'), or None if it can't be determined."""
    cml = target_dir / "CMakeLists.txt"
    if not cml.is_file():
        return None
    for line in cml.read_text(errors="ignore").splitlines():
        if line.strip().startswith("#"):
            continue
        m = _TARGET_MCU_RE.search(line)
        if m:
            return m.group(1).lower()
    return None


def mcu_index_for_target(target_dir: Path):
    """(mcu_token, index_dir_name_or_None). index name None means either the
    token is unknown or that MCU has no indexed datasheet here -- callers
    must report that explicitly, not fall back to a different MCU's table."""
    token = mcu_token_for_target(target_dir)
    if token is None:
        return None, None
    return token, MCU_TO_INDEX.get(token)


_CACHE = {}


def load_af_table(index_name: str):
    """pin -> {normalized 'TIMn_CHm[N]' token: AF number}. Empty dict if the
    TSV is missing (caller should treat as 'unknown', not 'invalid')."""
    if index_name in _CACHE:
        return _CACHE[index_name]
    tsv = DOCS_ROOT / index_name / "alternate-functions.tsv"
    table = {}
    if tsv.is_file():
        with tsv.open(newline="") as fh:
            rd = csv.reader(fh, delimiter="\t")
            next(rd, None)  # header row: Pin, AF0..AF15
            for row in rd:
                if not row or not row[0].strip():
                    continue
                pin = row[0].strip().upper()
                slot = table.setdefault(pin, {})
                for af_idx, cell in enumerate(row[1:]):
                    for part in cell.split("/"):
                        m = _TIMCH_RE.match(part.strip())
                        if m:
                            slot.setdefault(f"TIM{m.group(1)}_{m.group(2).upper()}",
                                            af_idx)
    _CACHE[index_name] = table
    return table


def options_for_pin(index_name: str, pin: str):
    """{'TIMn_CHm[N]': af_number} for one pin; {} if pin/table unknown."""
    return dict(load_af_table(index_name).get(pin.strip().upper(), {}))


DEF_TIM_RE = re.compile(
    r"^\s*DEF_TIM\(\s*((?:TIM|TMR)\d+)\s*,\s*(CH\d+N?)\s*,\s*(P[A-K]\d{1,2})\s*,"
)


def iter_def_tim(target_c_text: str):
    """Yields (lineno, raw_line, TIMn, CHm[N], PXn) for each uncommented
    DEF_TIM line. Deliberately does NOT resolve #if/#ifdef branches -- every
    branch's lines are yielded, which is correct for AF validity (a wrong
    pin/timer pair is wrong in whichever variant contains it) even though it
    would be wrong for anything position-dependent (see
    simulate_pwm_roles.py's parse_target_c() docstring)."""
    for lineno, line in enumerate(target_c_text.splitlines(), 1):
        if line.lstrip().startswith("//"):
            continue
        m = DEF_TIM_RE.match(line)
        if m:
            tim, ch, pin = m.groups()
            yield lineno, line.rstrip(), norm_tim(tim), ch.upper(), pin.upper()


# ---------------------------------------------------------------------------
# Firmware-side per-pin AF tables (F7 / H7 / AT32 only)
# ---------------------------------------------------------------------------
# These families DO carry a per-pin table in the firmware:
#   #define DEF_TIM_AF__PA3__TCH_TIM5_CH4   D(2, 5)
# A DEF_TIM triple whose macro is absent simply fails to compile there. That
# makes the table a hard BUILD constraint, separate from (and narrower than)
# the datasheet: it is populated only with pairs existing targets happen to
# use, so "absent" means "you must add the macro", NOT "the silicon can't do
# it". F4 has no such table at all -- which is precisely why a wrong triple
# is silent there.
_FAMILY_TIMER_DEF = {
    "F7": "timer_def_stm32f7xx.h",
    "H7": "timer_def_stm32h7xx.h",
    "AT32": "timer_def_at32f43x.h",
}
_FW_AF_RE = re.compile(
    r"^\s*#\s*define\s+DEF_TIM_AF__(P[A-K]\d{1,2})__TCH_((?:TIM|TMR)\d+)_(CH\d+N?)\b",
    re.I,
)
_FW_CACHE = {}


def firmware_af_pairs(inav_root, family):
    """{(PIN, 'TIMn', 'CHm'): True} from the family's timer_def header, or
    None if that family has no per-pin table (F4) or the header is missing.
    Channels are NOT de-N'd here -- the macro name must match exactly for
    the build to succeed."""
    key = _FAMILY_TIMER_DEF.get(family)
    if key is None:
        return None
    path = Path(inav_root) / "src" / "main" / "drivers" / key
    cache_key = str(path)
    if cache_key in _FW_CACHE:
        return _FW_CACHE[cache_key]
    if not path.is_file():
        _FW_CACHE[cache_key] = None
        return None
    pairs = {}
    for line in path.read_text(errors="ignore").splitlines():
        m = _FW_AF_RE.match(line)
        if m:
            pin, tim, ch = m.groups()
            pairs[(pin.upper(), norm_tim(tim), ch.upper())] = True
    _FW_CACHE[cache_key] = pairs
    return pairs
