#!/usr/bin/env python3
"""
simulate_pwm_roles.py -- deterministic simulation of INAV's motor/servo timer
role-resolution algorithm (pwmClaimTimer / pwmEnsureEnoughtMotors /
pwmBuildTimerOutputList in drivers/pwm_mapping.c), plus the DMA availability
and DMA-stream-collision checks that ride on top of it.

WHY THIS EXISTS
================
The role-resolution algorithm is genuinely hard to hand-trace correctly, and
getting it wrong has real consequences: pwmClaimTimer() unconditionally
overwrites usageFlags on EVERY timerHardware[] entry sharing a physical
timer, so a channel's OWN declared usage flag (TIM_USE_SERVO,
TIM_USE_OUTPUT_AUTO, ...) does NOT protect it from being forced into MOTOR
or SERVO role by a sibling channel on the same physical timer -- the final
role is decided by array declaration order + the mixer's live motor count
(getMotorCount(), NOT a target.h setting) + which channels share a timer.
This script was written after a session hand-traced this algorithm for
DAKEFPVF405WING and got it wrong on a late verification pass, having gotten
it wrong once already earlier in the same session -- see the
target-developer README's lessons for the incident. A deterministic port of
the actual C algorithm is the only reliable way to answer "what role does
output N resolve to at motor count M", and this script is that port.

Two additional hazards are checked, both invisible at compile time and at
boot:

1. SILENT_DEAD_MOTOR -- a channel that resolves to MOTOR and is genuinely
   initialized this build (its position within the resolved motor list is
   < the configured motor count) can still have NO DMA request line at all
   for that specific (timer, channel) pair on this MCU (e.g. TIM12 on
   STM32F405 -- see DEF_TIM_DMA__BTCH_TIM12_CH1/CH2 = NONE in
   timer_def_stm32f4xx.h). motorConfigDshot() silently fails to arm DMA in
   this case, but pwmMotorConfig()/pwmMotorAndServoInit() still report
   success -- see drivers/pwm_output.c. The motor output is dead, but
   nothing in the boot log or OSD says so.

2. DMA_STREAM_COLLISION -- two channels that both actually claim a DMA
   stream (i.e. both are genuinely initialized this build, not just
   sitting in the resolved-but-uninitialized tail of the motor/servo list)
   and whose only available DMA option resolves to the same
   (DMA controller, stream) pair will silently fight over that stream --
   only the first claimant to actually initialize keeps it, every other
   claimant's DSHOT/LED output just never works. Only entries that
   ACTUALLY claim DMA count for this check: pure SERVO-resolved channels
   never touch DMA at all (pwm_output.c only calls
   timerPWMConfigChannelDMA/DMABurst from the DSHOT motor path), and a
   MOTOR-resolved channel whose bucket position is >= the configured motor
   count is never initialized either, so it can't collide with anything.
   Under USE_DSHOT_DMAR, grouping MOTOR claimers by their raw per-channel
   dmavar/dmaopt value is WRONG -- see BURST_STREAM_COLLISION below, whose
   resolve_dmar_cascade() walk supersedes it for MOTOR claimers (this
   script groups by each MOTOR row's cascade-resolved effective_stream
   instead, see the dshot_dmar branch in simulate()); DMA_STREAM_COLLISION
   itself is still the right check and still uses each row's raw resolved
   stream for LED strip (LED strip never goes through the burst path) and
   for the final MOTOR-vs-LED / MOTOR-vs-MOTOR grouping once MOTOR rows
   have been substituted with their cascade-resolved stream.

3. BURST_STREAM_COLLISION / SILENT_DEAD_MOTOR under USE_DSHOT_DMAR --
   burst mode (impl_timerPWMConfigDMABurst()) claims one DMA stream per
   PHYSICAL TIMER, not per channel: `tch->timCtx->dmaBurstRef` lives on
   the timer-shared context (timCtx is one struct shared by all 4 channels
   of a timer -- timer.c timerGetTCH()). Both hazard classes -- a
   NONE-resolving channel's SILENT_DEAD_MOTOR status, and cross-claim
   collisions -- depend on the SAME real per-timer/per-channel ownership
   cascade, replayed once by resolve_dmar_cascade() and reused by both
   checks (see that function's docstring for the full derivation). The
   two backend implementations of impl_timerPWMConfigDMABurst() genuinely
   differ in a way that changes the answer, confirmed by direct comparison
   of timer_impl_stdperiph.c (F4) against timer_impl_hal.c (F7/H7, a
   shared backend file):
     - F4: the dmaGetByTag()/ownership check sits INSIDE
       `if (!tch->timCtx->dmaBurstRef) { ... }`. Once an earlier channel of
       a physical timer has succeeded, every LATER channel of that SAME
       timer skips the check entirely and unconditionally rides the
       winning channel's stream for free -- a NONE-resolving free rider is
       genuinely safe (no SILENT_DEAD_MOTOR), and it can't independently
       collide with anything either, since it never makes its own claim
       attempt.
     - F7/H7 (timer_impl_hal.c): the ownership check happens
       UNCONDITIONALLY, BEFORE that guard -- every channel, including a
       later channel of an already-locked timer, must independently pass
       its own dmaGetByTag()/dmaGetOwner() check using ITS OWN resolved
       stream. There is NO free ride on this family: a NONE-resolving
       channel is a genuine SILENT_DEAD_MOTOR regardless of position (this
       is why H7's real TIM4_CH4 needed the explicit DMA_REQUEST_TIM4_UP
       workaround, commit 657651bedf7c7bea2632c72f2a0c59bdcc37b26e -- F7's
       timer_def_stm32f7xx.h has no equivalent workaround, so an F7 target
       hitting a NONE-resolving channel under DMAR is still flagged), and
       an already-claimed stream fails this channel's own attempt too --
       whether the earlier claimant is a DIFFERENT timer (a genuine
       cross-timer BURST_STREAM_COLLISION) or, a degenerate edge case, the
       SAME timer reusing an identical dmavar-resolved stream
       (dmaGetOwner() only tracks "is this DMA object free", not "which
       timer already owns it").
   CORRECTION TO AN EARLIER CONCLUSION: a first pass at this model was
   built and verified only against F4's timer_impl_stdperiph.c semantics,
   then applied uniformly to F4 AND F7/H7 DMAR targets alike. That
   under-modeled F7/H7's lack of a free ride and produced false "cleared,
   false positive" verdicts for real F7 hazards -- confirmed empirically:
   NEXUSX and VANTAC_RF007 (both F7) have a genuine CERTAIN
   BURST_STREAM_COLLISION (TIM2_CH1 at position 3, inside the S1-S4
   range) that a family-aware resolve_dmar_cascade() correctly restores;
   AOCODARCF7MINI, TMOTORVELOXF7V2, and FLYDRAGONPRO (all F7) have real
   NOTICE-level BURST_STREAM_COLLISIONs the F4-only model had wrongly
   cleared. The F4 DMAR targets in the original six
   (FOXEERF405V2, RADIOLINKF405, SKYSTARSF405V2, TUNERCF405) remain
   correctly clean -- the free-ride reasoning was right for them, just
   wrongly generalized to F7/H7. See
   claude/projects/active/investigate-shared-tim-dma-request-lines/
   phase1-findings.md for the full corrected target list.
   Severity (CERTAIN/NOTICE) uses the same "loser position < 4" rule as
   DMA_STREAM_COLLISION (classify_collisions.py), since by construction
   the cascade walk processes strictly ascending position and only
   reports a channel that actually, individually failed its own attempt.

WHAT THIS SCRIPT DOES NOT MODEL (documented limitations, not bugs)
====================================================================
- checkPwmTimerConflicts()'s UART/softserial pin-sharing skip is gated on
  the LIVE runtime serial port configuration (doesConfigurationUsePort(),
  feature(FEATURE_SOFTSERIAL)), not anything visible in target.c/target.h.
  This is not statically knowable from a target checkout, so it is not
  modeled -- a channel that happens to double as an in-use UART TX/RX pin
  will be reported as available for motor/servo role assignment even though
  a live UART on that port would make pwm_mapping.c skip it entirely.
- checkPwmTimerConflicts()'s LED-strip-shares-timer skip (any OTHER channel
  on the same physical timer as a TIM_USE_LED entry gets permanently
  excluded from role assignment whenever FEATURE_LED_STRIP is active) IS
  modeled, but conservatively: it's treated as active whenever target.h
  defines USE_LED_STRIP at all, regardless of whether FEATURE_LED_STRIP is
  actually in DEFAULT_FEATURES. This matches check_dma_conflicts.py's
  existing convention for the same reason -- LED strip is commonly toggled
  on by users regardless of shipped default, so treating it as "always
  potentially active" is the safe assumption for hazard-finding. Pass
  --no-led-strip to disable this if you specifically want the
  LED-strip-off picture.
- (RESOLVED, see below) timerOverrides()/CLI `timer_output_mode` per-timer
  runtime overrides ARE modeled via --timer-output-mode, added specifically
  to answer whether forcing a shared-channel timer (e.g. TIM3, whose two
  channels S2/S3 on DAKEFPVF405WING cannot be split -- pwmClaimTimer()
  force-syncs usageFlags across every timerHardware[] entry on one physical
  timer) to OUTPUT_MODE_SERVOS keeps BOTH its channels out of the MOTOR
  bucket entirely (and therefore off DMA) even though the mixer's live
  motor count would otherwise have pulled the first channel in. Without
  --timer-output-mode, default is OUTPUT_MODE_AUTO for every timer (no
  override), matching a freshly flashed board. Pass 1 of
  pwmEnsureEnoughtMotors() counts each physical timer's motor-only group
  exactly once: a per-physical-timer `timerCounted[]` dedup guard
  (mirrored here as `counted_timers`, see pwm_ensure_enough_motors())
  keeps a sibling that an earlier pwmClaimTimer() broadcast already
  promoted from being re-counted when the loop later reaches its own
  index, and after the claim sync the whole group shares one role, so the
  group contributes its TRUE size -- every non-conflicted motor-only pad
  on the timer -- not "1 + pads changed by the claim" (which would
  undercount an already-motor-only group to 1) and not one per sibling
  turn (which would overcount to 2n-1). This script models this algorithm
  unconditionally -- there is no flag to reproduce older behavior; see
  git history if you need it.
- DSHOT vs plain PWM/Oneshot/Multishot motor protocol is a runtime
  motor_pwm_protocol CLI setting, not a target.c/target.h fact. This script
  defaults to assuming DSHOT (by far the common case, and the case the
  SILENT_DEAD_MOTOR/DMA_STREAM_COLLISION hazards are about -- plain PWM
  motors never touch DMA at all) -- pass --no-dshot to model a plain-PWM
  motor build instead, which suppresses both hazard classes for the motor
  bucket (LED still claims DMA either way, since led_strip.c always uses
  DMA when active).
- ADC's *conflict* check (checkPwmTimerConflicts skipping any timer pin
  that's also wired to an ADC_CHANNEL_n_PIN) IS modeled, since that one is
  fully static (gated only on USE_ADC being compiled, not a runtime
  feature() bit). ADC's *own* DMA stream (STM32H7 only, hardwired in
  adc_stm32h7xx.c, not read from target.h) is also modeled by reusing
  check_dma_conflicts.py's ADC_RESERVED_DMAOPT table.
- Servo count: pwmInitServos() only initializes the first
  min(servoCount, maxTimServoCount) entries of the resolved servo bucket,
  exactly mirroring the motor count truncation. This script accepts an
  optional --servo-count; if omitted, every resolved-SERVO entry is treated
  as "driven" (i.e. assumes the mixer wants at least as many servos as the
  target exposes) since under-provisioning servos is a far less common
  real-world gotcha than the motor case this script was built to catch.

MCU FAMILY SUPPORT
===================
F4/F7/AT32 share one DMA addressing scheme: DEF_TIM_DMA__BTCH_<TIM>_<CH> in
the family's timer_def_*.h expands to either NONE or a comma list of
D(dma,stream,channel) tuples, and target.c's DEF_TIM(...) trailing numeric
arg ("dmavar") is a 0-based index into that list. AT32 additionally has a
DMAMUX indirection (DEF_TIM_DMA_FULL -- 14 interchangeable options, same
list for nearly every channel) which is resolved the same way; per the
target-developer lessons, AT32 conflict analysis really just becomes "did
two entries pick the same literal dmavar index", since the list itself
doesn't distinguish channels.

H7 uses a different, flatter scheme (already implemented by
check_dma_conflicts.py, imported here rather than re-implemented): dmaopt
is a flat 0-15 index directly addressing DMA1 Stream0-7 / DMA2 Stream0-7,
with a fixed small set of (timer, channel) pairs that have NO DMA request
line at all (NO_DMA_CHANNELS) plus the USE_DSHOT_DMAR-conditional TIM4_CH4
special case.

Usage
=====
  ./simulate_pwm_roles.py <inav_root> --target NAME --motor-count N
      Print the fully resolved per-output table for exactly this motor
      count: bucket (MOTOR/SERVO/LED/none), position within that bucket,
      whether it's actually driven this build, whether it claims DMA, and
      which (controller, stream) it claims if so.

  ./simulate_pwm_roles.py <inav_root> --target NAME
  ./simulate_pwm_roles.py <inav_root> --target NAME --sweep 1:8
      Sweep every motor count in range (default: 1..total DEF_TIM entries)
      and report only the hazards found at each count -- this is the "find
      the safe motorCount values" mode that motivated this script.

  ./simulate_pwm_roles.py --selftest <inav_root>
      Run the built-in regression cases (see SELFTEST_CASES below) and
      print PASS/FAIL. Run this after touching the simulation logic.

Options:
  --servo-count N   cap the servo bucket the same way --motor-count caps
                     the motor bucket (default: unlimited, see above)
  --no-dshot         assume plain PWM/Oneshot/Multishot motors (suppresses
                     motor-side DMA hazards; LED still claims DMA)
  --no-led-strip     assume FEATURE_LED_STRIP is never enabled, even though
                     USE_LED_STRIP is compiled in (see limitations above)
  --timer-output-mode TIMn=MODE
                     Simulate a timerOverridesMutable(timer2id(TIMn))
                     ->outputMode = OUTPUT_MODE_MODE override (as set via
                     CLI `timer_output_mode` or in a target's config.c),
                     WITHOUT editing any file on disk. MODE is one of AUTO,
                     MOTORS, SERVOS, LED. Repeatable, e.g.
                     --timer-output-mode TIM3=SERVOS. TIMn must match a
                     `tim` token used in this target's DEF_TIM(...) entries
                     (e.g. TIM3, TIM8) -- every entry on that physical timer
                     is affected identically, matching pwmClaimTimer()'s
                     force-sync behavior, and the timer's whole motor-only
                     group is counted once at its true size (see pass-1
                     description above).
  --verbose          show the full per-output table even in --sweep mode
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_dma_conflicts as _h7  # reuse NO_DMA_CHANNELS / ADC_RESERVED_DMAOPT

# ---------------------------------------------------------------------------
# usage-flag bit values, copied from drivers/timer.h
# ---------------------------------------------------------------------------
TIM_USE_ANY = 0
TIM_USE_PPM = 1 << 0
TIM_USE_PWM = 1 << 1
TIM_USE_MOTOR = 1 << 2
TIM_USE_SERVO = 1 << 3
TIM_USE_MC_CHNFW = 1 << 4  # deprecated, never set by any live target
TIM_USE_LED = 1 << 24
TIM_USE_BEEPER = 1 << 25
TIM_USE_OUTPUT_AUTO = TIM_USE_MOTOR | TIM_USE_SERVO

USAGE_TOKENS = {
    "TIM_USE_ANY": TIM_USE_ANY,
    "TIM_USE_PPM": TIM_USE_PPM,
    "TIM_USE_PWM": TIM_USE_PWM,
    "TIM_USE_MOTOR": TIM_USE_MOTOR,
    "TIM_USE_SERVO": TIM_USE_SERVO,
    "TIM_USE_MC_CHNFW": TIM_USE_MC_CHNFW,
    "TIM_USE_LED": TIM_USE_LED,
    "TIM_USE_BEEPER": TIM_USE_BEEPER,
    "TIM_USE_OUTPUT_AUTO": TIM_USE_OUTPUT_AUTO,
}


def is_motor(flags):
    return bool(flags & TIM_USE_MOTOR)


def is_servo(flags):
    return bool(flags & TIM_USE_SERVO)


def is_led(flags):
    return bool(flags & TIM_USE_LED)


def is_motor_only(flags):
    return is_motor(flags) and not is_servo(flags)


# ---------------------------------------------------------------------------
# timer_output_mode overrides (timerHardwareOverride() in pwm_mapping.c) --
# a per-PHYSICAL-TIMER runtime override (CLI `timer_output_mode` / a
# target's config.c timerOverridesMutable(...)->outputMode), applied to
# EVERY timerHardware[] entry on that timer identically, regardless of that
# entry's own declared usage flags. OUTPUT_MODE_AUTO (the default, value 0)
# is a deliberate no-op -- see the switch in timerHardwareOverride() itself,
# which has no `case OUTPUT_MODE_AUTO`.
# ---------------------------------------------------------------------------
OUTPUT_MODE_TOKENS = ("AUTO", "MOTORS", "SERVOS", "LED")


def apply_timer_output_mode_override(entry, mode):
    """Mirrors timerHardwareOverride() in pwm_mapping.c exactly, including
    leaving flags untouched for AUTO/None (no case in the real switch)."""
    if not mode or mode == "AUTO":
        return
    if mode == "MOTORS":
        entry.flags &= ~(TIM_USE_SERVO | TIM_USE_LED)
        entry.flags |= TIM_USE_MOTOR
    elif mode == "SERVOS":
        entry.flags &= ~(TIM_USE_MOTOR | TIM_USE_LED)
        entry.flags |= TIM_USE_SERVO
    elif mode == "LED":
        entry.flags &= ~(TIM_USE_MOTOR | TIM_USE_SERVO)
        entry.flags |= TIM_USE_LED


def parse_usage(usage_text, warn_prefix=""):
    flags = 0
    for tok in usage_text.split("|"):
        tok = tok.strip()
        if not tok:
            continue
        if tok not in USAGE_TOKENS:
            print(f"{warn_prefix}warning: unknown usage token {tok!r}, treating as 0",
                  file=sys.stderr)
            continue
        flags |= USAGE_TOKENS[tok]
    return flags


# ---------------------------------------------------------------------------
# target.c parsing
# ---------------------------------------------------------------------------
DEF_TIM_RE = re.compile(
    r'DEF_TIM\(\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)\s*,'
    r'\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*(\d+)\s*\)'
)
COMMENT_RE = re.compile(r'//\s*(.+?)\s*$')
IF_DIRECTIVE_RE = re.compile(r'^\s*#\s*(if|ifdef|ifndef)\b\s*(.*)$')
ELSE_DIRECTIVE_RE = re.compile(r'^\s*#\s*(else|elif)\b\s*(.*)$')
ENDIF_DIRECTIVE_RE = re.compile(r'^\s*#\s*endif\b')


class Entry:
    __slots__ = ("index", "tim", "ch", "pin", "flags", "orig_flags", "dmavar",
                 "label", "line", "conditional_expr")

    def __init__(self, index, tim, ch, pin, flags, dmavar, label, line,
                 conditional_expr=None):
        self.index = index
        self.tim = tim
        self.ch = ch
        self.pin = pin
        self.flags = flags
        self.orig_flags = flags
        self.dmavar = dmavar
        self.label = label
        self.line = line
        # Non-None when this DEF_TIM line was found nested inside a
        # #if/#ifdef/#ifndef block in timerHardware[] -- see parse_target_c().
        self.conditional_expr = conditional_expr

    @property
    def conditional(self):
        return self.conditional_expr is not None

    def usage_str(self):
        parts = []
        if self.flags & TIM_USE_MOTOR:
            parts.append("MOTOR")
        if self.flags & TIM_USE_SERVO:
            parts.append("SERVO")
        if self.flags & TIM_USE_LED:
            parts.append("LED")
        if self.flags & TIM_USE_BEEPER:
            parts.append("BEEPER")
        if self.flags & TIM_USE_PWM:
            parts.append("PWM")
        if self.flags & TIM_USE_PPM:
            parts.append("PPM")
        return "|".join(parts) if parts else "ANY(0)"

    def __repr__(self):
        return f"{self.tim}_{self.ch}({self.label})"


def parse_target_c(text):
    """Parse DEF_TIM(...) lines into Entry objects.

    Preprocessor-aware: a #if/#ifdef/#ifndef/#elif/#else/#endif stack is
    tracked while scanning, and any DEF_TIM line found while that stack is
    non-empty gets entry.conditional_expr set to a best-effort description
    of the guarding condition(s) (joined with " && " when nested). This
    function still flattens every branch into one flat list -- a single
    build only compiles one branch, so a target with conditional DEF_TIM
    lines can have entries here that never coexist on real hardware (e.g.
    two branches both declaring TIM4_CH2 look like a self-collision, or a
    hazard hidden in one branch is masked by a clean line in the other).
    Callers MUST check entry.conditional before trusting collision/hazard
    verdicts derived from these entries -- see has_conditional_tim() and
    run_target()/classify_collisions.py's N/A handling.
    """
    entries = []
    cond_stack = []
    for i, line in enumerate(text.splitlines()):
        stripped = line.strip()

        m_if = IF_DIRECTIVE_RE.match(stripped)
        if m_if:
            kind, rest = m_if.groups()
            rest = rest.strip()
            cond_stack.append(f"!{rest}" if kind == "ifndef" else rest)
            continue
        m_else = ELSE_DIRECTIVE_RE.match(stripped)
        if m_else and cond_stack:
            kind, rest = m_else.groups()
            if kind == "else":
                cond_stack[-1] = f"!({cond_stack[-1]})"
            else:  # elif
                cond_stack[-1] = rest.strip() or cond_stack[-1]
            continue
        if ENDIF_DIRECTIVE_RE.match(stripped):
            if cond_stack:
                cond_stack.pop()
            continue

        if stripped.startswith("//"):
            continue
        m = DEF_TIM_RE.search(line)
        if not m:
            continue
        tim, ch, pin, usage_text, _flags_field, dmavar = m.groups()
        cm = COMMENT_RE.search(line)
        if cm:
            # Comments are often "S4 - long explanation ..." -- take just the
            # leading token (the S-number / short name) as the label so
            # tables stay compact; the full comment is still in entry.line.
            label = cm.group(1).split()[0].rstrip(",;")
        else:
            label = f"{tim}_{ch}"
        flags = parse_usage(usage_text, warn_prefix=f"line {i+1}: ")
        conditional_expr = " && ".join(cond_stack) if cond_stack else None
        entries.append(Entry(len(entries), tim, ch, pin, flags, int(dmavar),
                              label, stripped, conditional_expr))
    return entries


def has_conditional_tim(entries):
    """True if any entry (from parse_target_c) came from inside a
    #if/#ifdef/#ifndef block -- see parse_target_c()'s docstring for why
    that makes the flattened entry list unsafe to draw hazard verdicts
    from without manual per-build-variant review."""
    return any(e.conditional for e in entries)


def apply_dmavar_overrides(entries, overrides):
    """Mutate entries in place, setting entry.dmavar for each label in
    `overrides` (a dict of label -> new dmavar int). Raises SystemExit if a
    label doesn't match any parsed entry, so a typo'd --dmavar-override
    fails loudly instead of silently simulating the unmodified board.
    Returns the list of (label, old, new) changes actually applied, in
    override-argument order, for print-back/audit purposes."""
    by_label = {e.label: e for e in entries}
    applied = []
    for label, new_val in overrides.items():
        if label not in by_label:
            known = ", ".join(sorted(by_label))
            raise SystemExit(
                f"--dmavar-override: no DEF_TIM entry labeled {label!r}. "
                f"Known labels: {known}"
            )
        e = by_label[label]
        applied.append((label, e.dmavar, new_val))
        e.dmavar = new_val
    return applied


def clone_entries(entries):
    out = []
    for e in entries:
        ne = Entry(e.index, e.tim, e.ch, e.pin, e.orig_flags, e.dmavar, e.label, e.line,
                   e.conditional_expr)
        out.append(ne)
    return out


# ---------------------------------------------------------------------------
# target.h parsing (ADC conflict pins + USE_LED_STRIP + USE_DSHOT_DMAR + family)
# ---------------------------------------------------------------------------
ADC_PIN_RE = re.compile(r'^\s*#\s*define\s+ADC_CHANNEL_\d+_PIN\s+(\w+)', re.M)


def parse_target_h(text):
    adc_pins = set()
    if "USE_ADC" in text:
        adc_pins = set(ADC_PIN_RE.findall(text))
    led_strip = "USE_LED_STRIP" in text
    dshot_dmar = "USE_DSHOT_DMAR" in text
    return adc_pins, led_strip, dshot_dmar


FAMILY_RE = {
    "F4": re.compile(r'target_stm32f4\w*\('),
    "F7": re.compile(r'target_stm32f7\w*\('),
    "H7": re.compile(r'target_stm32h7\w*\('),
    "AT32": re.compile(r'target_at32f43x\w*\(', re.IGNORECASE),
}


def detect_family(cmake_text):
    for family, rx in FAMILY_RE.items():
        if rx.search(cmake_text):
            return family
    return None


# ---------------------------------------------------------------------------
# DMA option tables, F4/F7/AT32 (list-of-options addressed by dmavar index)
# ---------------------------------------------------------------------------
BTCH_DEFINE_RE = re.compile(
    r'#\s*define\s+(DEF_TIM_DMA__BTCH_[A-Za-z0-9]+_(?:CH\d N?|CH\dN|CH\d))\s+(.+)'
)
# The channel-suffix alternation above is fiddly to get exactly right with
# regex; simpler and robust: just capture the macro name greedily up to
# whitespace, then split off the CH-suffix separately.
BTCH_DEFINE_RE = re.compile(r'#\s*define\s+(DEF_TIM_DMA__BTCH_\S+)\s+(.+)')
DMA_FULL_RE = re.compile(r'#\s*define\s+(DEF_TIM_DMA_FULL)\s+(.+)')
D_TUPLE_RE = re.compile(r'D\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)')


def load_option_table(header_text):
    """Returns {(TIM, CH): [(dma, stream, chan), ...]} for F4/F7/AT32-style
    headers. Empty list means NONE (no DMA request line at all)."""
    collapsed = re.sub(r'\\\r?\n', ' ', header_text)
    macros = {}
    for m in BTCH_DEFINE_RE.finditer(collapsed):
        name, body = m.group(1), m.group(2)
        body = body.split("//")[0].strip()
        macros[name] = body
    full_m = DMA_FULL_RE.search(collapsed)
    full_body = full_m.group(2).split("//")[0].strip() if full_m else ""

    table = {}
    for name, body in macros.items():
        if body == "DEF_TIM_DMA_FULL":
            body = full_body
        if body == "NONE":
            options = []
        else:
            options = [(int(d), int(s), int(c)) for d, s, c in D_TUPLE_RE.findall(body)]
        # name looks like DEF_TIM_DMA__BTCH_TIM3_CH4 or ..._BTCH_TMR3_CH4
        rest = name[len("DEF_TIM_DMA__BTCH_"):]
        # split off trailing _CHx / _CHxN / _UP
        cm = re.match(r'(.+)_(CH\d N?|CH\d|UP)$', rest)
        cm = re.match(r'(.+)_(CH\dN?|UP)$', rest)
        if not cm:
            continue
        tim_tok, ch_tok = cm.group(1), cm.group(2)
        table[(tim_tok, ch_tok)] = options
    return table


def stream_label_f4(dma, stream):
    return f"DMA{dma} Stream{stream}"


# ---------------------------------------------------------------------------
# H7: flat dmaopt addressing (delegates to check_dma_conflicts.py's tables)
# ---------------------------------------------------------------------------
def h7_dma_options(tim_tok, ch_tok, dmaopt, dshot_dmar):
    if (tim_tok, ch_tok) == ("TIM4", "CH4"):
        if not dshot_dmar:
            return []
    elif (tim_tok, ch_tok) in _h7.NO_DMA_CHANNELS:
        return []
    dma = 1 if dmaopt < 8 else 2
    stream = dmaopt if dmaopt < 8 else dmaopt - 8
    return [(dma, stream, 0)]


def stream_label_h7(dma, stream):
    return _h7.stream_label(stream + (0 if dma == 1 else 8))


# ---------------------------------------------------------------------------
# DMA resolver: given family + entry, return list of (dma,stream,chan)
# options and which one dmavar actually picks (or None if index invalid /
# channel has no DMA at all).
# ---------------------------------------------------------------------------
class DmaResolver:
    def __init__(self, family, target_dir, target_h_text, dshot_dmar):
        self.family = family
        self.dshot_dmar = dshot_dmar
        self.table = None
        if family in ("F4", "F7", "AT32"):
            header_name = {
                "F4": "timer_def_stm32f4xx.h",
                "F7": "timer_def_stm32f7xx.h",
                "AT32": "timer_def_at32f43x.h",
            }[family]
            header_path = target_dir.parents[1] / "drivers" / header_name
            self.table = load_option_table(header_path.read_text(errors="ignore"))

    def _lookup(self, tim, ch):
        """F4/F7/AT32 option-list lookup, with the CHxN -> CHx alias that
        timer_def.h applies before the DEF_TIM_DMA__ prefix is concatenated
        on (see BTCH_TIM1_CH1N -> BTCH_TIM1_CH1 etc there): an N-channel
        (complementary output, e.g. TIM1_CH1N) shares its base channel's DMA
        request line, since DMA is driven by the timer's compare-match event
        which is the same for CHx and CHxN. Returns None if truly not found
        after trying both the exact key and its de-N'd fallback."""
        if (tim, ch) in self.table:
            return self.table[(tim, ch)]
        if ch.endswith("N") and (tim, ch[:-1]) in self.table:
            return self.table[(tim, ch[:-1])]
        return None

    def options_for(self, entry):
        """Returns list of (dma, stream, chan) options for this entry's
        (tim, ch); empty list means no DMA request line exists at all."""
        if self.family == "H7":
            return h7_dma_options(entry.tim, entry.ch, entry.dmavar, self.dshot_dmar)
        return self._lookup(entry.tim, entry.ch)  # None = unknown (tim/ch not found)

    def claimed_stream(self, entry):
        """Returns (dma, stream) the entry actually claims given its dmavar,
        or None if it has no DMA at all. Returns ('?', dmavar) sentinel if
        the (tim,ch) pair wasn't found in the header table (parser gap --
        report, don't silently treat as safe)."""
        if self.family == "H7":
            opts = h7_dma_options(entry.tim, entry.ch, entry.dmavar, self.dshot_dmar)
            return (opts[0][0], opts[0][1]) if opts else None
        opts = self._lookup(entry.tim, entry.ch)
        if opts is None:
            return ("?", entry.dmavar)  # unknown channel -- flagged separately
        if not opts:
            return None
        if entry.dmavar >= len(opts):
            return ("?", entry.dmavar)  # dmavar out of range -- shouldn't happen
        d, s, _c = opts[entry.dmavar]
        return (d, s)

    def stream_label(self, dma, stream):
        if dma == "?":
            return f"<unresolved dmavar={stream}>"
        if self.family == "H7":
            return stream_label_h7(dma, stream)
        return stream_label_f4(dma, stream)

    def is_shared_multichannel_request(self, entry, active_siblings):
        """True if this entry's chosen dmavar resolves to a (dma,stream,chan)
        tuple that is ALSO listed as an option for a DIFFERENT channel of the
        same physical timer, AND at least one of those other channels is
        genuinely driven this build (its own `ch` token is in
        `active_siblings`, the set of channel tokens on this entry's timer
        that simulate() determined are actually initialized at this
        motorCount/servoCount -- see its precompute block above `simulate()`'s
        main per-row loop). That exact-tuple-reuse is the generic fingerprint
        of an F4-family "combined" DMA request line -- e.g. DMA2 Stream6
        channel 0 is listed as an option for TIM1_CH1, TIM1_CH2, AND TIM1_CH3
        alike (DEF_TIM_DMA__BTCH_TIM1_CH1/CH2/CH3 in timer_def_stm32f4xx.h all
        include D(2,6,0)). Firing that request only tells the DMA controller
        "one of this timer's channels compare-matched", not which one -- but
        if NO sibling channel of that combined group is actually configured
        as a live output this build (the SOLO pattern), the shared line only
        ever sees THIS channel's own compare events and behaves exactly like
        a dedicated one, so it is not a defect. It only becomes one (the
        SPURIOUS TRIGGERS pattern) once a sibling is genuinely active too,
        injecting its own compare events onto the same line and corrupting
        this channel's DSHOT bitstream -- unless the timer is driven in
        USE_DSHOT_DMAR burst mode (which reads all channels' CCRs together
        off the timer's *update* event instead, a completely different
        mechanism this check doesn't apply to, see the `not
        dma_resolver.dshot_dmar` guard at the call site). See
        investigate-shared-tim-dma-request-lines/summary.md's SOLO (73,
        harmless) vs. SPURIOUS TRIGGERS (10, genuine) full-tree
        classification for the original derivation of this distinction.
        Confirmed via upstream commit ab07785fa9 ("Fix channel selection for
        DMA2 Stream6"), which changed exactly this -- TIM1_CH3 dmavar 0 -> 1
        -- on 4 real boards (DALRCF405, FLYWOOF411, HAKRCF405V2,
        HAKRCF722V2) after the dmavar=0 option produced no signal (all 4 are
        genuine SPURIOUS TRIGGERS cases, confirmed hardware-tested). Only
        meaningful for F4/F7/AT32 (self.table is None on H7, which has no
        such shared-request-line quirk)."""
        if self.table is None:
            return False
        if self.family == "AT32":
            # AT32F435 is DMAMUX-based: DEF_TIM_DMA__BTCH_* for every single
            # channel of every timer expands to the literal same macro
            # (DEF_TIM_DMA_FULL, a ~14-entry list of generic DMAMUX channel
            # numbers -- see timer_def_at32f43x.h). Since that identical list
            # is repeated verbatim for every (tim,ch), "this tuple also
            # appears in a sibling channel's list" is true for nearly any
            # dmavar and carries no meaning -- there is no F4-style
            # hardwired "combined CH1/CH2/CH3 request line" concept on a
            # DMAMUX part; each DMA channel's request source is independently
            # muxed. Real AT32 conflict analysis is "too many concurrent
            # users of the 14 DMAMUX channels", not this.
            return False
        opts = self._lookup(entry.tim, entry.ch)
        if not opts or entry.dmavar >= len(opts):
            return False
        chosen = opts[entry.dmavar]
        # Restrict to channel-selector 0: that's the specific slot F4/F8-style
        # advanced-timer tables in this codebase consistently use for the
        # combined CH1/CH2/CH3 request (see TIM1_CH1/CH2/CH3 and
        # TIM8_CH1/CH2/CH3 in timer_def_stm32f4xx.h, all listing D(dma,stream,0)
        # as their FIRST/dmavar-0 option). Sibling channels can legitimately
        # share a physical (dma,stream,chan!=0) tuple as plain alternate
        # routing options (e.g. TIM2_CH2 and TIM2_CH4 both list D(1,6,3)) --
        # that's an ordinary DMA_STREAM_COLLISION risk only if BOTH are
        # actually chosen simultaneously, not this "unusable in isolation"
        # defect class, so don't flag chan!=0 here to avoid false positives.
        if chosen[2] != 0:
            return False
        group_siblings = set()
        # De-N the entry's OWN channel before excluding it. The header
        # table is keyed on BASE channels only (there is no ('TIM1','CH2N')
        # key -- see _lookup()'s CHxN -> CHx fallback), so comparing the raw
        # 'CH2N' against key 'CH2' never matches and the entry's own base
        # channel gets counted as a "sibling". Since active_siblings is
        # itself de-N'd (see simulate()'s active_ch_by_tim precompute), that
        # produced a guaranteed self-match: EVERY N-channel entry using a
        # combined request line was flagged, even when it was the only
        # channel of that timer in the whole target (the SOLO case this
        # check exists to exclude).
        entry_ch_norm = entry.ch[:-1] if entry.ch.endswith("N") else entry.ch
        for (tim_tok, ch_tok), other_opts in self.table.items():
            if tim_tok != entry.tim or ch_tok == entry_ch_norm:
                continue
            if chosen in other_opts:
                group_siblings.add(ch_tok)
        if not group_siblings:
            return False
        # SOLO vs. SPURIOUS TRIGGERS: only a defect if a sibling that could
        # actually share this line is genuinely driven this build, not just
        # theoretically able to per the header table.
        return bool(group_siblings & active_siblings)


# ---------------------------------------------------------------------------
# Faithful port of pwm_mapping.c
# ---------------------------------------------------------------------------
def base_channel_token(ch):
    """CH2N -> CH2. An N-channel is the complementary output of the SAME
    capture/compare register, not a separate channel -- see timer_def.h's
    `#define BTCH_TIM1_CH2N BTCH_TIM1_CH2`. Anything asking "is this the
    same hardware channel" (duplicate detection, DMA request lookup,
    active-sibling sets) must collapse an N-channel onto its base."""
    return ch[:-1] if ch.endswith("N") else ch


def check_pwm_timer_conflicts(entry, entries, adc_pins, led_strip_active):
    if entry.pin in adc_pins:
        return True
    if led_strip_active:
        for e in entries:
            if e.tim == entry.tim and is_led(e.flags):
                return True
    return False


def pwm_claim_timer(entries, tim, usage_flags):
    changed = 0
    for e in entries:
        if e.tim == tim and e.flags != usage_flags:
            e.flags = usage_flags
            changed += 1
    return changed


def pwm_ensure_enough_motors(entries, motor_count, adc_pins, led_strip_active,
                              timer_output_modes=None):
    timer_output_modes = timer_output_modes or {}
    motor_only_outputs = 0
    # Fixed in pwm_mapping.c (fix-pwm-motor-double-counting, 2026-08-17): pass 1
    # now dedups per physical timer via a timerCounted[] guard, so a sibling
    # promoted by an earlier pwm_claim_timer() broadcast is not re-counted when
    # the loop later reaches its own index. Mirrored here with a plain set --
    # e.tim is a hashable per-physical-timer token, same role as the C fix's
    # timer2id(timHw->tim) index into timerCounted[].
    counted_timers = set()
    for e in entries:
        # timerHardwareOverride(): applied per-entry, lazily, exactly here --
        # BEFORE any sibling on the same physical timer has necessarily been
        # visited yet.
        apply_timer_output_mode_override(e, timer_output_modes.get(e.tim))
        if check_pwm_timer_conflicts(e, entries, adc_pins, led_strip_active):
            continue
        if is_motor_only(e.flags) and e.tim not in counted_timers:
            counted_timers.add(e.tim)
            pwm_claim_timer(entries, e.tim, e.flags)
            # Count every non-conflicted pad on this physical timer after the
            # claim sync: each one now carries the same motor-only flags, so the
            # group contributes its TRUE size n. Counting "1 + claim changes"
            # would undercount an all-motor-only group (the claim changes
            # nothing there) to 1 instead of n, which then over-promotes AUTO
            # outputs in pass 2 and silently removes servo-capable outputs.
            for s in entries:
                if (s.tim == e.tim
                        and not check_pwm_timer_conflicts(s, entries, adc_pins, led_strip_active)
                        and is_motor_only(s.flags)):
                    motor_only_outputs += 1

    for e in entries:
        if check_pwm_timer_conflicts(e, entries, adc_pins, led_strip_active):
            continue
        if is_motor(e.flags) and not is_motor_only(e.flags):
            if motor_only_outputs < motor_count:
                e.flags = (e.flags & ~TIM_USE_SERVO) | TIM_USE_MOTOR
                motor_only_outputs += 1
                motor_only_outputs += pwm_claim_timer(entries, e.tim, e.flags)
            else:
                e.flags = e.flags & ~TIM_USE_MOTOR
                pwm_claim_timer(entries, e.tim, e.flags)


def pwm_build_timer_output_list(entries, motor_count, adc_pins, led_strip_active,
                                 timer_output_modes=None):
    pwm_ensure_enough_motors(entries, motor_count, adc_pins, led_strip_active,
                              timer_output_modes)

    motor_idx = 0
    tim_motors = []
    tim_servos = []
    bucket = {}       # entry.index -> "MOTOR" | "SERVO" | "LED" | None
    skipped = set()   # entry.index that hit checkPwmTimerConflicts here

    for e in entries:
        if check_pwm_timer_conflicts(e, entries, adc_pins, led_strip_active):
            skipped.add(e.index)
            continue

        if is_motor(e.flags) and motor_idx < motor_count:
            e.flags &= ~TIM_USE_SERVO
            pwm_claim_timer(entries, e.tim, e.flags)
            motor_idx += 1

        has_motor_on_tim = any(m.tim == e.tim for m in tim_motors)
        has_servo_on_tim = any(s.tim == e.tim for s in tim_servos)

        typ = None
        if is_servo(e.flags) and not has_motor_on_tim:
            typ = "SERVO"
        elif is_motor(e.flags) and not has_servo_on_tim:
            typ = "MOTOR"
        elif is_led(e.flags) and not has_motor_on_tim and not has_servo_on_tim:
            typ = "LED"

        if typ == "MOTOR":
            e.flags &= TIM_USE_MOTOR
            tim_motors.append(e)
            pwm_claim_timer(entries, e.tim, e.flags)
        elif typ == "SERVO":
            e.flags &= TIM_USE_SERVO
            tim_servos.append(e)
            pwm_claim_timer(entries, e.tim, e.flags)
        elif typ == "LED":
            e.flags &= TIM_USE_LED
            pwm_claim_timer(entries, e.tim, e.flags)

        bucket[e.index] = typ

    return tim_motors, tim_servos, bucket, skipped


class SimResult:
    def __init__(self):
        self.rows = []       # list of dicts, one per entry, in declaration order
        self.hazards = []    # list of strings



def resolve_dmar_cascade(rows, family):
    """Faithfully replays impl_timerPWMConfigDMABurst()'s real per-timer/
    per-channel DMA ownership cascade for a USE_DSHOT_DMAR target, walking
    live DMA-claiming MOTOR rows in POSITION order (== pwmInitMotors()'s
    real idx=0..motorCount-1 init order, since `rows` preserves declaration
    order and position was assigned by that same walk). This is the single
    authoritative source of "what DMA resource does this channel actually,
    really end up sharing" -- used for BOTH the SILENT_DEAD_MOTOR and
    DMA_STREAM_COLLISION/BURST_STREAM_COLLISION hazards below, replacing two
    previously-divergent code paths (a naive per-channel dma_claims dict and
    a separately-hand-rolled walk) that happened to agree on the one
    real-world case (FLYDRAGONPRO) they were checked against but were not
    guaranteed to agree in general.

    Confirmed via direct comparison of timer_impl_stdperiph.c (F4) against
    timer_impl_hal.c (F7/H7, a shared backend file -- see the
    target-developer README's lessons for why a fix/bug found on one of
    F7/H7 is strong evidence for the other but not F4/AT32):

    - F4 (timer_impl_stdperiph.c): the dmaGetByTag()/dmaGetOwner() ownership
      check sits INSIDE `if (!tch->timCtx->dmaBurstRef) { ... }`. Once ANY
      earlier channel of a physical timer has SUCCEEDED (dmaBurstRef set),
      every LATER channel of that SAME timer skips the whole block --
      including the check -- and unconditionally returns true, riding the
      winning channel's stream for free. Its own dmaTag/dmavar is never
      consulted at all: a NONE-resolving free-rider is genuinely safe (no
      SILENT_DEAD_MOTOR), and it can't independently collide with anything
      either (it never makes its own claim attempt). If the timer's FIRST
      channel's own attempt instead FAILS (no DMA line, or the stream is
      already owned by some earlier, different timer's winner), dmaBurstRef
      stays unset, so the NEXT channel of that SAME timer gets its own,
      fully independent attempt -- this is why "free rider" must be
      computed from a live per-timer "has this timer succeeded YET"
      cascade, not simply "is this the lowest-position channel of its
      timer".
    - F7/H7 (timer_impl_hal.c, shared backend): the ownership check happens
      UNCONDITIONALLY, BEFORE that guard -- every channel, including a later
      channel of an already-locked timer, must independently pass its own
      dmaGetByTag()/dmaGetOwner() check using ITS OWN resolved stream. There
      is no free ride on this family: a NONE-resolving channel fails
      regardless of position (this is why H7's real TIM4_CH4 needed the
      explicit DMA_REQUEST_TIM4_UP workaround, commit
      657651bedf7c7bea2632c72f2a0c59bdcc37b26e -- without it, TIM4_CH4 would
      fail this gate even riding a timer some earlier channel already
      locked). An already-claimed stream fails this channel's own attempt
      too, whether the earlier claimant is a DIFFERENT timer (a genuine
      cross-timer hazard) or even -- a degenerate edge case -- the SAME
      timer reusing an identical dmavar-resolved stream (dmaGetOwner() only
      tracks "is this DMA object free", not "which timer already owns it").
      Confirmed empirically: real H7/F7 USE_DSHOT_DMAR targets (e.g.
      AXISFLYINGH743PRO's TIM4 CH1-4) assign each channel of a burst timer
      a genuinely DISTINCT dmaopt/stream, not a shared one -- so this
      "always checks its own value" model matches how these targets are
      actually built, not just how the C code technically allows.

    Returns {entry.index: {
        "free_rider": bool,             # F4 only; always False on F7/H7
        "no_dma_at_all": bool,          # this row's own dmaGetByTag() would
                                         # find nothing -- SILENT_DEAD_MOTOR
                                         # candidate (see caller for the
                                         # family-aware suppression rule)
        "attempted_stream": (dma,stream) or None,
                                         # the raw per-channel stream this
                                         # row's own attempt used, if it made
                                         # one at all (None for a free rider,
                                         # which never touches its own value,
                                         # or a no_dma_at_all row)
        "effective_stream": (dma,stream) or None,
                                         # the DMA resource this row ACTUALLY
                                         # ends up sharing with other live
                                         # claimers (its own stream on
                                         # success, the timer's winner's
                                         # stream if riding for free, None if
                                         # its own attempt failed or was
                                         # never made) -- this is what
                                         # DMA_STREAM_COLLISION should group
                                         # claimers by, NOT attempted_stream
        "collision_winner": Entry or None,
                                         # set iff this row made its own real
                                         # attempt and it collided with an
                                         # earlier winner (BURST_STREAM_
                                         # COLLISION candidate)
    }}. Only rows that are actually live DMA-claiming (or DMA-attempting)
    MOTOR outputs this build are included -- LED never goes through this
    cascade at all (light_ws2811strip.c's own DMA config is a completely
    separate call path, never impl_timerPWMConfigDMABurst)."""
    cascade = {}
    stream_owner = {}   # (dma,stream) -> winning Entry, across ALL timers
    timer_locked = {}   # tim token -> (dma,stream), set only on real success
    for row in rows:
        if row["bucket"] != "MOTOR" or not row["driven"]:
            continue
        if not (row["claims_dma"] or row["no_dma_at_all"]):
            continue
        e = row["entry"]
        tim = e.tim

        if family == "F4" and tim in timer_locked:
            cascade[e.index] = {
                "free_rider": True, "no_dma_at_all": False,
                "attempted_stream": None,
                "effective_stream": timer_locked[tim],
                "collision_winner": None,
            }
            continue

        if row["no_dma_at_all"]:
            cascade[e.index] = {
                "free_rider": False, "no_dma_at_all": True,
                "attempted_stream": None, "effective_stream": None,
                "collision_winner": None,
            }
            continue

        own_stream = row["stream"]
        if own_stream in stream_owner:
            cascade[e.index] = {
                "free_rider": False, "no_dma_at_all": False,
                "attempted_stream": own_stream, "effective_stream": None,
                "collision_winner": stream_owner[own_stream],
            }
            continue

        # Real success: this channel claims the stream, locking its whole
        # physical timer onto it (F4's free-ride shortcut) / at minimum
        # establishing "this timer has a winner" bookkeeping (F7/H7, where
        # that bookkeeping is informational only -- never consulted to skip
        # a later channel's own check).
        stream_owner[own_stream] = e
        timer_locked.setdefault(tim, own_stream)
        cascade[e.index] = {
            "free_rider": False, "no_dma_at_all": False,
            "attempted_stream": own_stream, "effective_stream": own_stream,
            "collision_winner": None,
        }
    return cascade


def simulate(entries_orig, motor_count, servo_count, adc_pins, led_strip_active,
             dma_resolver, dshot, timer_output_modes=None):
    entries = clone_entries(entries_orig)
    tim_motors, tim_servos, bucket, skipped = pwm_build_timer_output_list(
        entries, motor_count, adc_pins, led_strip_active, timer_output_modes)

    motor_pos = {e.index: i for i, e in enumerate(tim_motors)}
    servo_pos = {e.index: i for i, e in enumerate(tim_servos)}

    # LED strip is NOT driven through pwmBuildTimerOutputList's bucket system
    # at all -- light_ws2811strip.c's ws2811LedStripInit() does its own
    # timerGetByTag/timerGetByUsageFlag(TIM_USE_LED) lookup directly against
    # the ORIGINAL (as-declared) timerHardware[] entry, independent of
    # whatever pwm_mapping.c did with it. In fact checkPwmTimerConflicts()
    # makes the LED entry match itself (same tim, TIM_USE_LED flag) whenever
    # led_strip_active, so pwm_build_timer_output_list() always SKIPs it --
    # this is by design, not a modeling gap: it keeps pwm_mapping.c from also
    # handing that channel out as a servo/motor, while led_strip.c claims it
    # through its own separate path. So LED DMA-claim status is computed
    # here from the entry's ORIGINAL declared flags, not the resolved bucket.
    led_entry_indices = {e.index for e in entries_orig if e.orig_flags & TIM_USE_LED}

    # Precomputed once, up front (bucket/motor_pos/servo_pos/led_entry_indices
    # are all already fully known) so is_shared_multichannel_request() below
    # can tell a SOLO combined-DMA-request-line usage (no sibling channel of
    # the timer is genuinely driven this build -> the request line only ever
    # sees this channel's own compare events -> not a defect) from a real
    # SPURIOUS-TRIGGERS one (a sibling IS driven -> its compare events also
    # land on the shared line, corrupting this channel's DSHOT transfer).
    def _driven_for(idx):
        if idx in led_entry_indices and led_strip_active:
            return True
        b_ = bucket.get(idx)
        if b_ == "MOTOR":
            return motor_pos[idx] < motor_count
        if b_ == "SERVO":
            return True if servo_count is None else servo_pos[idx] < servo_count
        return False

    active_ch_by_tim = {}
    for oe in entries:
        if _driven_for(oe.index):
            # De-N the channel token (CH2N -> CH2) to match the header
            # table's keys -- see DmaResolver._lookup()'s docstring: an
            # N-channel shares its base channel's compare-match event, so it
            # must count as that same base channel being active.
            ch_norm = oe.ch[:-1] if oe.ch.endswith("N") else oe.ch
            active_ch_by_tim.setdefault(oe.tim, set()).add(ch_norm)

    result = SimResult()
    dma_claims = {}  # (dma,stream) -> list of entry describing string

    # ---- TIMER_CHANNEL_DUPLICATE ---------------------------------------
    # Two DEF_TIM entries on DIFFERENT pins sharing ONE compare register.
    # Strictly worse than any DMA hazard: a DMA collision only costs the
    # loser DSHOT (it still works as servo/Multishot/analog PWM), whereas
    # two pins on one CCR can only ever mirror each other -- the second
    # output cannot be driven independently for ANY protocol.
    #
    # This needs its own hazard class because every DMA check here can be
    # completely silent about it: if the two entries pick different
    # dmavars they resolve to different streams, so DMA_STREAM_COLLISION
    # never fires. Found while evaluating TIM8_CH3N on PB15 as an escape
    # route from DMA-less TIM12_CH2 on a board already driving TIM8_CH3 on
    # PC8 -- the whole sweep came back clean on a change that would have
    # bricked an output.
    #
    # Keyed on the DE-N'd channel: CH2N is the complementary output of the
    # SAME compare register as CH2 (timer_def.h aliases BTCH_TIMn_CHmN to
    # BTCH_TIMn_CHm), so CH2/CH2N on two pins is a duplicate even though
    # the raw tokens differ. Conditional (#if-guarded) entries are skipped:
    # mutually exclusive build variants legitimately reuse a (tim,ch)
    # across branches and parse_target_c() flattens them together.
    _dup_seen = {}
    for e in entries:
        if e.conditional:
            continue
        _dup_seen.setdefault((e.tim, base_channel_token(e.ch)), []).append(e)
    for (dup_tim, dup_ch), group in sorted(_dup_seen.items()):
        pins = [g.pin for g in group]
        # Distinct pins only -- the same pin repeated is a source-level
        # duplicate line, not two physical pads fighting over one CCR.
        if len(group) >= 2 and len(set(pins)) >= 2:
            spelled = ", ".join(f"{g.tim}_{g.ch} on {g.pin} ({g.label})" for g in group)
            result.hazards.append(
                f"TIMER_CHANNEL_DUPLICATE: {dup_tim}_{dup_ch} is declared on "
                f"{len(set(pins))} different pins -- {spelled}. These share ONE "
                f"compare register, so they can only ever emit the SAME "
                f"waveform: the later output cannot be driven independently "
                f"for any protocol (not merely DSHOT). This is invisible to "
                f"every DMA check in this script whenever the entries resolve "
                f"to different DMA streams."
            )

    for e in entries:
        b = bucket.get(e.index)
        is_led_entry = e.index in led_entry_indices
        if is_led_entry and led_strip_active:
            b_display = "LED (own path in light_ws2811strip.c, bypasses pwm_mapping bucket)"
        elif e.index in skipped:
            b_display = "SKIPPED(ADC/LED-timer conflict)"
        elif b is None:
            b_display = "unclaimed"
        else:
            b_display = b

        driven = False
        pos = None
        if is_led_entry and led_strip_active:
            driven = True
        elif b == "MOTOR":
            pos = motor_pos[e.index]
            driven = pos < motor_count
        elif b == "SERVO":
            pos = servo_pos[e.index]
            driven = True if servo_count is None else pos < servo_count

        claims_dma = False
        stream = None
        no_dma_at_all = False
        if is_led_entry and led_strip_active:
            claims_dma = True
        elif driven and b == "MOTOR" and dshot:
            claims_dma = True

        if claims_dma:
            resolved = dma_resolver.claimed_stream(e)
            if resolved is None:
                no_dma_at_all = True
                claims_dma = False
            else:
                stream = resolved
                dma_claims.setdefault(resolved, []).append(e)

        row = {
            "entry": e, "bucket": b_display, "position": pos, "driven": driven,
            "claims_dma": claims_dma, "stream": stream, "no_dma_at_all": no_dma_at_all,
        }
        result.rows.append(row)

        if no_dma_at_all and b == "MOTOR" and driven and dshot and not dma_resolver.dshot_dmar:
            # Under USE_DSHOT_DMAR this is handled below instead, via the
            # resolve_dmar_cascade() walk -- whether a NONE-resolving
            # channel is actually a hazard is family- and cascade-position-
            # dependent there (see that function's docstring), not a flat
            # rule this per-row loop can decide in isolation.
            result.hazards.append(
                f"SILENT_DEAD_MOTOR: {e.tim}_{e.ch} ({e.label}) resolves to MOTOR "
                f"and IS initialized at motorCount={motor_count} (bucket position "
                f"{pos}), but this (timer,channel) has NO DMA request line at all "
                f"on this MCU -- motorConfigDshot() will silently fail to arm DMA "
                f"while pwmMotorConfig() still reports success. This output will "
                f"not spin under DSHOT despite no boot-time error."
            )

        if (claims_dma and b == "MOTOR" and driven and dshot
                and not dma_resolver.dshot_dmar
                and dma_resolver.is_shared_multichannel_request(
                    e, active_ch_by_tim.get(e.tim, set()))):
            result.hazards.append(
                f"SHARED_TIMER_DMA_REQUEST: {e.tim}_{e.ch} ({e.label}) dmavar="
                f"{e.dmavar} resolves to a DMA request line ALSO shared with "
                f"another channel of {e.tim} (a combined multi-channel "
                f"compare-event request, not one dedicated to this channel). "
                f"Without USE_DSHOT_DMAR this typically means the DMA transfer "
                f"never fires specifically for this channel's own compare "
                f"events and the output stays silent even though "
                f"pwmMotorConfig() reports success -- see upstream commit "
                f"ab07785fa9 (\"Fix channel selection for DMA2 Stream6\"), "
                f"which hit exactly this on 4 real boards. Try a different "
                f"dmavar for this channel."
            )

    # ---- USE_DSHOT_DMAR: single authoritative cascade resolution ---------
    # resolve_dmar_cascade() (see its docstring) replays the real per-timer/
    # per-channel DMA ownership cascade ONCE and is reused for BOTH hazard
    # classes below -- a channel's DMA-VISIBLE resource for collision
    # purposes is its cascade-resolved effective_stream, not its raw
    # per-channel dmavar/dmaopt value, and whether a NONE-resolving channel
    # is a real SILENT_DEAD_MOTOR hazard depends on family + cascade
    # position, not a flat per-row rule.
    cascade = {}
    if dma_resolver.dshot_dmar:
        cascade = resolve_dmar_cascade(result.rows, dma_resolver.family)

        for row in result.rows:
            if row["bucket"] != "MOTOR":
                continue
            e = row["entry"]
            c = cascade.get(e.index)
            if c is None:
                continue

            if c["no_dma_at_all"]:
                if dma_resolver.family in ("F7", "H7"):
                    gate_note = (
                        f"{dma_resolver.family}'s impl_timerPWMConfigDMABurst() "
                        f"(timer_impl_hal.c) checks every channel's own "
                        f"dmaGetByTag() UNCONDITIONALLY, before the "
                        f"already-locked-timer guard -- there is no free ride "
                        f"on this family, regardless of position"
                    )
                else:
                    gate_note = (
                        f"on {dma_resolver.family} this channel is the first "
                        f"live channel of its physical timer still needing a "
                        f"claim, so timer_impl_stdperiph.c's already-locked-"
                        f"timer free ride does not apply yet -- its own "
                        f"dmaGetByTag() is reached and finds nothing"
                    )
                result.hazards.append(
                    f"SILENT_DEAD_MOTOR: {e.tim}_{e.ch} ({e.label}) resolves to "
                    f"MOTOR and IS initialized at motorCount={motor_count} "
                    f"(bucket position {row['position']}), but this "
                    f"(timer,channel) has NO DMA request line at all on this "
                    f"MCU. Under USE_DSHOT_DMAR, {gate_note} -- "
                    f"motorConfigDshot() will silently fail to arm DMA for "
                    f"this channel while pwmMotorConfig() still reports "
                    f"success. This output will not spin under DSHOT despite "
                    f"no boot-time error."
                )
            elif c["collision_winner"] is not None:
                winner = c["collision_winner"]
                dma, s = c["attempted_stream"]
                label = dma_resolver.stream_label(dma, s)
                backend_file = ("timer_impl_hal.c" if dma_resolver.family in ("F7", "H7")
                                 else "timer_impl_stdperiph.c")
                if winner.tim == e.tim:
                    relation = (
                        f"is on the SAME physical timer ({e.tim}), reusing an "
                        f"identical dmavar-resolved stream as an earlier "
                        f"channel of that same timer (dmaGetOwner() only "
                        f"tracks whether the DMA object is free, not which "
                        f"timer already owns it, so this collides too)"
                    )
                else:
                    relation = f"is on a DIFFERENT physical timer ({e.tim})"
                if dma_resolver.family == "F4":
                    retry_note = (
                        f"Any LATER channel of {e.tim} not yet reached would "
                        f"get its own independent retry (dmaBurstRef stays "
                        f"unset on failure); this is the specific channel "
                        f"actually affected, not necessarily every channel of "
                        f"{e.tim}."
                    )
                else:
                    retry_note = (
                        f"On {dma_resolver.family} every channel (including "
                        f"this one) always makes its own independent attempt "
                        f"regardless of whether its timer already has a "
                        f"winner, so this channel specifically is the one "
                        f"affected -- not necessarily every channel of "
                        f"{e.tim}."
                    )
                result.hazards.append(
                    f"BURST_STREAM_COLLISION: {label} locked in first by "
                    f"{winner.tim} (via {winner.tim}_{winner.ch}({winner.label})); "
                    f"{e.tim}_{e.ch}({e.label}) at position {row['position']} "
                    f"{relation} and its own DMAR burst claim attempt to the "
                    f"same stream fails at motorCount={motor_count} -- under "
                    f"USE_DSHOT_DMAR a stream is claimed once per PHYSICAL "
                    f"TIMER (impl_timerPWMConfigDMABurst, {backend_file}), not "
                    f"per channel: this channel's own dmaGetByTag()/ownership "
                    f"check fails, and this output stays silent even though "
                    f"pwmMotorConfig() reports success. {retry_note}"
                )

    # DMA_STREAM_COLLISION -- two channels that both actually claim a DMA
    # stream and whose only available DMA option resolves to the same
    # (DMA controller, stream) pair. Without DMAR this is the plain
    # per-channel model (impl_timerPWMConfigChannelDMA claims a stream per
    # CHANNEL, timer_impl_stdperiph.c ~line 300) and dma_claims (built
    # per-row above from each entry's OWN resolved stream) is already
    # authoritative. Under DMAR, grouping must instead use each MOTOR row's
    # cascade-resolved effective_stream (resolve_dmar_cascade() above) --
    # NOT its raw per-channel value -- since a free rider's raw value was
    # never actually consulted by the real firmware at all. LED strip never
    # goes through the burst path (light_ws2811strip.c does its own DMA
    # config directly against the entry's raw resolved stream), so LED
    # claims are read from dma_claims/row["stream"] the same way regardless
    # of DMAR.
    if dma_resolver.dshot_dmar:
        collision_claims = {}
        for row in result.rows:
            e = row["entry"]
            if row["bucket"] == "MOTOR":
                c = cascade.get(e.index)
                if c and c["effective_stream"] is not None:
                    collision_claims.setdefault(c["effective_stream"], []).append(e)
            elif row["claims_dma"]:  # LED (or any future non-MOTOR DMA claimer)
                collision_claims.setdefault(row["stream"], []).append(e)
    else:
        collision_claims = dma_claims

    for stream, claimers in collision_claims.items():
        if len(claimers) < 2:
            continue
        if dma_resolver.dshot_dmar:
            all_motor = all(bucket.get(c.index) == "MOTOR" for c in claimers)
            same_timer = len({c.tim for c in claimers}) == 1
            if all_motor and same_timer:
                # By construction (resolve_dmar_cascade only ever assigns
                # ONE winning stream per physical timer, and a losing
                # attempt's effective_stream is None so it never enters this
                # dict), an all-motor group sharing one effective_stream is
                # always exactly one timer's winner + its free riders -- the
                # intended combined-request sharing burst mode exists for,
                # not a bug. A genuine cross-timer hazard is reported as
                # BURST_STREAM_COLLISION above instead, with the correct
                # winner/loser and blast radius.
                continue
        dma, s = stream
        label = dma_resolver.stream_label(dma, s)
        names = ", ".join(f"{c.tim}_{c.ch}({c.label})" for c in claimers)
        result.hazards.append(
            f"DMA_STREAM_COLLISION: {label} claimed by {len(claimers)} live DMA "
            f"users at motorCount={motor_count}: {names} -- only the first "
            f"claimant to actually initialize keeps the stream; every other "
            f"output in this group silently never works despite no boot-time "
            f"error. Among MOTOR outputs the LOWEST array position wins "
            f"(pwmInitMotors() claims DMA in strict position order, "
            f"pwm_mapping.c); a MOTOR output always wins over LED strip "
            f"specifically, since pwmMotorAndServoInit() runs before "
            f"ledStripInit() in fc_init.c."
        )

    for row in result.rows:
        if row["stream"] == ("?", row["entry"].dmavar) or (
            row["claims_dma"] and row["stream"] and row["stream"][0] == "?"
        ):
            e = row["entry"]
            result.hazards.append(
                f"PARSER_GAP: could not resolve DMA option table for "
                f"{e.tim}_{e.ch} ({e.label}) -- verify manually against "
                f"timer_def_*.h, this script's header parsing didn't find it."
            )

    return result


def print_table(result, motor_count, servo_count):
    print(f"\n--- motorCount={motor_count}"
          f"{'' if servo_count is None else f', servoCount={servo_count}'} ---")
    hdr = f'{"pos":>3}  {"tim_ch":<12} {"label":<10} {"bucket":<28} {"driven":<7} {"dma":<20}'
    print(hdr)
    print("-" * len(hdr))
    for row in result.rows:
        e = row["entry"]
        dma_str = "-"
        if row["claims_dma"]:
            d, s = row["stream"]
            dma_str = f"DMA{d} Stream{s}" if d != "?" else f"<unresolved:{s}>"
        elif row["no_dma_at_all"]:
            dma_str = "NONE (hazard!)"
        print(f'{e.index:>3}  {e.tim + "_" + e.ch:<12} {e.label:<10} '
              f'{row["bucket"]:<28} {str(row["driven"]):<7} {dma_str:<20}')
    if result.hazards:
        print("\nHazards:")
        for h in result.hazards:
            print(f"  - {h}")
    else:
        print("\nNo hazards found at this motor count.")


def run_target(inav_root, target_name, motor_count, servo_count, sweep_range,
               dshot, led_strip_override, verbose, dmavar_overrides=None,
               timer_output_modes=None):
    target_dir = inav_root / "src" / "main" / "target" / target_name
    target_c = target_dir / "target.c"
    target_h = target_dir / "target.h"
    cmake = target_dir / "CMakeLists.txt"
    if not target_c.is_file():
        raise SystemExit(f"No target.c under {target_dir}")

    family = detect_family(cmake.read_text(errors="ignore")) if cmake.is_file() else None
    if family is None:
        raise SystemExit(
            f"Could not detect MCU family from {cmake}. Supported: F4, F7, H7, AT32."
        )

    entries = parse_target_c(target_c.read_text(errors="ignore"))
    if not entries:
        raise SystemExit(f"No DEF_TIM(...) entries parsed from {target_c}")

    if has_conditional_tim(entries):
        print(f"\n*** N/A: {target_name}'s timerHardware[] has DEF_TIM line(s) "
              "guarded by #if/#ifdef/#ifndef. parse_target_c() flattens every "
              "build variant into one array, so the collision/hazard verdicts "
              "below can be a false positive (two variants' lines colliding "
              "with each other, never coexisting on real hardware) or a false "
              "negative (a hazard hidden in one variant, masked by a clean "
              "line from another). Treat this target as N/A until reviewed "
              "by hand, one build variant at a time. Guarded lines:")
        for e in entries:
            if e.conditional:
                print(f"      [{e.conditional_expr}] {e.tim}_{e.ch} ({e.label})")
        print()

    if dmavar_overrides:
        applied = apply_dmavar_overrides(entries, dmavar_overrides)
        print("Applying --dmavar-override (simulated only, target.c on disk "
              "is NOT modified):")
        for label, old_val, new_val in applied:
            print(f"  {label}: dmavar {old_val} -> {new_val}")

    timer_output_modes = timer_output_modes or {}
    if timer_output_modes:
        known_tims = {e.tim for e in entries}
        unknown = sorted(set(timer_output_modes) - known_tims)
        if unknown:
            raise SystemExit(
                f"--timer-output-mode: no DEF_TIM entry uses timer(s) "
                f"{unknown} in {target_c}. Known timers: {sorted(known_tims)}"
            )
        print("Applying --timer-output-mode (simulated only, no file on disk "
              "is modified):")
        for tim, mode in timer_output_modes.items():
            affected = sorted(e.label for e in entries if e.tim == tim)
            print(f"  {tim} -> OUTPUT_MODE_{mode} (affects: {', '.join(affected)})")

    adc_pins, led_strip, dshot_dmar = (set(), False, False)
    if target_h.is_file():
        adc_pins, led_strip, dshot_dmar = parse_target_h(target_h.read_text(errors="ignore"))
    if led_strip_override is not None:
        led_strip = led_strip_override

    dma_resolver = DmaResolver(family, target_dir, target_h.read_text(errors="ignore")
                                if target_h.is_file() else "", dshot_dmar)

    print(f"Target: {target_name}  MCU family: {family}  "
          f"USE_LED_STRIP: {led_strip}  DSHOT assumed: {dshot}")
    print(f"Parsed {len(entries)} DEF_TIM entries; ADC-conflict pins: "
          f"{sorted(adc_pins) if adc_pins else 'none'}")

    if motor_count is not None:
        result = simulate(entries, motor_count, servo_count, adc_pins, led_strip,
                           dma_resolver, dshot, timer_output_modes)
        print_table(result, motor_count, servo_count)
        return

    lo, hi = sweep_range
    print(f"\nSweeping motorCount {lo}..{hi}:")
    any_hazard = False
    for mc in range(lo, hi + 1):
        result = simulate(entries, mc, servo_count, adc_pins, led_strip,
                           dma_resolver, dshot, timer_output_modes)
        if verbose:
            print_table(result, mc, servo_count)
        elif result.hazards:
            any_hazard = True
            print(f"\nmotorCount={mc}:")
            for h in result.hazards:
                print(f"  - {h}")
        else:
            print(f"motorCount={mc}: clean")
    if not any_hazard and not verbose:
        print("\nNo hazards found across the swept range.")


# ---------------------------------------------------------------------------
# Self-test / regression cases (see the email that spawned this script for
# the full derivation of each reference point -- reproduced here so future
# edits to the simulation logic can be checked against known-correct answers
# without re-deriving them by hand).
# ---------------------------------------------------------------------------
DAKEFPVF405WING_ORIGINAL_TARGET_C = '''
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM2,   CH2, PA1,  TIM_USE_OUTPUT_AUTO,   1, 0), // S1
    DEF_TIM(TIM3,   CH3, PB0,  TIM_USE_OUTPUT_AUTO,   1, 0), // S2
    DEF_TIM(TIM3,   CH4, PB1,  TIM_USE_OUTPUT_AUTO,   1, 0), // S3
    DEF_TIM(TIM12,  CH1, PB14, TIM_USE_OUTPUT_AUTO,   1, 0), // S4
    DEF_TIM(TIM12,  CH2, PB15, TIM_USE_OUTPUT_AUTO,   1, 0), // S5
    DEF_TIM(TIM8,   CH3, PC8,  TIM_USE_OUTPUT_AUTO,   1, 0), // S6
    DEF_TIM(TIM8,   CH4, PC9,  TIM_USE_OUTPUT_AUTO,   1, 0), // S7
    DEF_TIM(TIM1,   CH1, PA8,  TIM_USE_OUTPUT_AUTO,   0, 0), // S8
    DEF_TIM(TIM1,   CH2, PA9,  TIM_USE_OUTPUT_AUTO,   0, 0), // S9
    DEF_TIM(TIM1,   CH3, PA10, TIM_USE_OUTPUT_AUTO,   0, 0), // S10
    DEF_TIM(TIM5,   CH1, PA0,  TIM_USE_LED,   1, 0), // 2812LED
    DEF_TIM(TIM5,   CH3, PA2,  TIM_USE_ANY,   0, 0), // TX2  softserial1_Tx
};
'''

# The dakefpvf405wing-hardware-bringup fix (2026-08-15), verbatim from
# `git show ecca02aff6:src/main/target/DAKEFPVF405WING/target.c` in the inav2
# checkout -- embedded rather than read from disk because DAKEFPVF405WING no
# longer exists as a target directory (superseded upstream by a differently
# laid-out DAKEFPVF405), which used to make this whole self-test crash with
# FileNotFoundError before it ever reached the SHARED_TIMER_DMA_REQUEST
# regression check below.
DAKEFPVF405WING_EDITED_TARGET_C = '''
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM2,   CH2, PA1,  TIM_USE_OUTPUT_AUTO,   1, 0), // S1

    DEF_TIM(TIM3,   CH3, PB0,  TIM_USE_OUTPUT_AUTO,   1, 0), // S2
    DEF_TIM(TIM3,   CH4, PB1,  TIM_USE_OUTPUT_AUTO,   1, 0), // S3

    DEF_TIM(TIM12,  CH1,PB14, TIM_USE_SERVO,   1, 0), // S4 - TIM12 has no DMA on F405, servo-only
    DEF_TIM(TIM12,  CH2,PB15, TIM_USE_SERVO,   1, 0), // S5 - TIM12 has no DMA on F405, servo-only

    DEF_TIM(TIM8,   CH3, PC8,  TIM_USE_OUTPUT_AUTO,   1, 1), // S6
    DEF_TIM(TIM8,   CH4, PC9,  TIM_USE_OUTPUT_AUTO,   1, 0), // S7

    DEF_TIM(TIM1,   CH1, PA8,  TIM_USE_OUTPUT_AUTO,   0, 1), // S8 - DMA2 Stream1)
    DEF_TIM(TIM1,   CH2, PA9,  TIM_USE_OUTPUT_AUTO,   0, 1), // S9 - DMA2 Stream2
    DEF_TIM(TIM1,   CH3, PA10, TIM_USE_OUTPUT_AUTO,   0, 1), // S10 - Stream6

    DEF_TIM(TIM5,   CH1, PA0,  TIM_USE_LED,   1, 0), // 2812LED
    DEF_TIM(TIM5,   CH3, PA2,  TIM_USE_ANY,   0, 0), // TX2  softserial1_Tx
};
'''


def _selftest(inav_root):
    ok = True

    def check(desc, cond):
        nonlocal ok
        mark = "PASS" if cond else "FAIL"
        if not cond:
            ok = False
        print(f"[{mark}] {desc}")

    # F4 header parsing sanity
    header = (inav_root / "src/main/drivers/timer_def_stm32f4xx.h").read_text()
    table = load_option_table(header)
    check("TIM3_CH4 has exactly one DMA option (DMA1 Stream2)",
          table.get(("TIM3", "CH4")) == [(1, 2, 5)])
    check("TIM5_CH1 has exactly one DMA option (DMA1 Stream2)",
          table.get(("TIM5", "CH1")) == [(1, 2, 6)])
    check("TIM12_CH1 has NO DMA option", table.get(("TIM12", "CH1")) == [])
    check("TIM12_CH2 has NO DMA option", table.get(("TIM12", "CH2")) == [])

    dma_resolver = DmaResolver("F4", inav_root / "src/main/target/DAKEFPVF405WING",
                                "", False)

    # --- Reference point 1: original (pre-edit) target.c, motorCount=2 ---
    entries = parse_target_c(DAKEFPVF405WING_ORIGINAL_TARGET_C)
    result = simulate(entries, motor_count=2, servo_count=None, adc_pins=set(),
                       led_strip_active=False, dma_resolver=dma_resolver, dshot=True)
    by_label = {r["entry"].label: r for r in result.rows}
    check("original target.c, mc=2: S1 is a driven MOTOR",
          by_label["S1"]["bucket"] == "MOTOR" and by_label["S1"]["driven"])
    check("original target.c, mc=2: S2 is a driven MOTOR",
          by_label["S2"]["bucket"] == "MOTOR" and by_label["S2"]["driven"])
    check("original target.c, mc=2: S3 resolves MOTOR but is NOT driven (dead)",
          by_label["S3"]["bucket"] == "MOTOR" and not by_label["S3"]["driven"])
    for s in ("S4", "S5", "S6", "S7", "S8", "S9", "S10"):
        check(f"original target.c, mc=2: {s} force-demoted to SERVO",
              by_label[s]["bucket"] == "SERVO")

    # --- Reference point 2: current (edited) target.c, S3 cascade ---
    entries2 = parse_target_c(DAKEFPVF405WING_EDITED_TARGET_C)
    for mc in (2, 3, 5):
        r = simulate(entries2, motor_count=mc, servo_count=None, adc_pins=set(),
                     led_strip_active=False, dma_resolver=dma_resolver, dshot=True)
        s3 = {row["entry"].label: row for row in r.rows}["S3"]
        check(f"edited target.c, mc={mc}: S3 still resolves MOTOR (never SERVO, "
              f"despite S4/S5 explicit TIM_USE_SERVO not protecting it)",
              s3["bucket"] == "MOTOR")

    # S4/S5 themselves should now genuinely be usable SERVOs regardless of mc
    for mc in (2, 3):
        r = simulate(entries2, motor_count=mc, servo_count=None, adc_pins=set(),
                     led_strip_active=False, dma_resolver=dma_resolver, dshot=True)
        rows = {row["entry"].label: row for row in r.rows}
        check(f"edited target.c, mc={mc}: S4 resolves SERVO and is driven",
              rows["S4"]["bucket"] == "SERVO" and rows["S4"]["driven"])
        check(f"edited target.c, mc={mc}: S5 resolves SERVO and is driven",
              rows["S5"]["bucket"] == "SERVO" and rows["S5"]["driven"])

    # --- Reference point 3: S3 vs LED DMA1 Stream2 collision when S3 is live ---
    r_mc2 = simulate(entries2, motor_count=2, servo_count=None, adc_pins=set(),
                      led_strip_active=True, dma_resolver=dma_resolver, dshot=True)
    check("edited target.c, mc=2, LED active: NO collision yet (S3 not driven)",
          not any("DMA_STREAM_COLLISION" in h for h in r_mc2.hazards))

    r_mc3 = simulate(entries2, motor_count=3, servo_count=None, adc_pins=set(),
                      led_strip_active=True, dma_resolver=dma_resolver, dshot=True)
    check("edited target.c, mc=3, LED active: S3 vs LED DMA1 Stream2 COLLISION found",
          any("DMA_STREAM_COLLISION" in h and "Stream2" in h for h in r_mc3.hazards))

    # --- Reference point 4: dedup fix verification for --timer-output-mode
    # TIMn=MOTORS on a shared multi-channel timer. Layout: TIM_A has 2
    # channels (A1, A2), forced to OUTPUT_MODE_MOTORS; TIM_B has 1 channel
    # (B1), left AUTO. Pre-fix, this reproduced the 2n-1 inflation bug
    # (motor_only_outputs went to 3 instead of 2 for the n=2 TIM_A group,
    # silently demoting B1 to SERVO at motorCount=3). Post-fix (the
    # `counted_timers` dedup guard in pwm_ensure_enough_motors()), the group
    # correctly counts as exactly 2, so B1 promotes to MOTOR at the naively
    # expected motorCount=3 -- same as the no-override control case.
    SYNTHETIC_INFLATION_TARGET_C = """
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM_A,  CH1, PA1,  TIM_USE_OUTPUT_AUTO,   1, 0), // A1
    DEF_TIM(TIM_A,  CH2, PA2,  TIM_USE_OUTPUT_AUTO,   1, 0), // A2
    DEF_TIM(TIM_B,  CH1, PA3,  TIM_USE_OUTPUT_AUTO,   1, 0), // B1
};
"""
    synth_entries = parse_target_c(SYNTHETIC_INFLATION_TARGET_C)
    synth_resolver = DmaResolver("F4", inav_root / "src/main/target/DAKEFPVF405WING",
                                  "", False)
    modes = {"TIM_A": "MOTORS"}

    r2 = simulate(synth_entries, motor_count=2, servo_count=None, adc_pins=set(),
                  led_strip_active=False, dma_resolver=synth_resolver, dshot=False,
                  timer_output_modes=modes)
    rows2 = {row["entry"].label: row for row in r2.rows}
    check("dedup fix, motorCount=2: A1 and A2 (the TIM_A group) are MOTOR and "
          "driven, filling both slots",
          rows2["A1"]["bucket"] == "MOTOR" and rows2["A1"]["driven"] and
          rows2["A2"]["bucket"] == "MOTOR" and rows2["A2"]["driven"])
    check("dedup fix, motorCount=2: B1 is NOT promoted (both slots correctly "
          "consumed by the n=2 TIM_A group -- confirms the guard doesn't "
          "UNDER-count either)",
          rows2["B1"]["bucket"] == "SERVO")

    r3 = simulate(synth_entries, motor_count=3, servo_count=None, adc_pins=set(),
                  led_strip_active=False, dma_resolver=synth_resolver, dshot=False,
                  timer_output_modes=modes)
    rows3 = {row["entry"].label: row for row in r3.rows}
    check("dedup fix, motorCount=3: A1 and A2 are MOTOR and driven",
          rows3["A1"]["bucket"] == "MOTOR" and rows3["A1"]["driven"] and
          rows3["A2"]["bucket"] == "MOTOR" and rows3["A2"]["driven"])
    check("dedup fix, motorCount=3: B1 IS now promoted to MOTOR and driven "
          "(the TIM_A group correctly counts as 2, not the pre-fix inflated "
          "3 -- this is the bug fix; pre-fix, B1 stayed SERVO here)",
          rows3["B1"]["bucket"] == "MOTOR" and rows3["B1"]["driven"])

    # Control: same layout, but TIM_A left at AUTO (no override) -- matches
    # the override case exactly now that both are dedup'd correctly.
    r3_noverride = simulate(synth_entries, motor_count=3, servo_count=None,
                             adc_pins=set(), led_strip_active=False,
                             dma_resolver=synth_resolver, dshot=False)
    rows3n = {row["entry"].label: row for row in r3_noverride.rows}
    check("dedup fix control (no override): motorCount=3 gives B1 as "
          "MOTOR+driven, same as the MOTORS-override case above",
          rows3n["B1"]["bucket"] == "MOTOR" and rows3n["B1"]["driven"])

    # --- Reference point 4b: undercount regression (all-motor-only group).
    # The timerCounted[] dedup guard must NOT turn an n-pad group that is
    # ALREADY motor-only at pass-1 entry into a count of 1: pwmClaimTimer()
    # returns 0 when nothing changed, so "1 + claim changes" undercounts the
    # group to 1, pass 2 then promotes the AUTO output at a motorCount the
    # user never asked for, claiming the whole timer as motor-only and
    # silently removing servo capability. The corrected pass 1 counts every
    # non-conflicted motor-only pad on the timer after the claim sync.
    SYNTHETIC_ALL_MOTOR_ONLY_TARGET_C = """
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM_A,  CH1, PA1,  TIM_USE_MOTOR,            1, 0), // A1
    DEF_TIM(TIM_A,  CH2, PA2,  TIM_USE_MOTOR,            1, 0), // A2
    DEF_TIM(TIM_B,  CH1, PA3,  TIM_USE_OUTPUT_AUTO,      1, 0), // B1
};
"""
    synth_all_motor = parse_target_c(SYNTHETIC_ALL_MOTOR_ONLY_TARGET_C)

    r_am2 = simulate(synth_all_motor, motor_count=2, servo_count=None,
                     adc_pins=set(), led_strip_active=False,
                     dma_resolver=synth_resolver, dshot=False)
    rows_am2 = {row["entry"].label: row for row in r_am2.rows}
    check("undercount fix, all-motor-only group, motorCount=2: A1 and A2 "
          "both resolve to driven MOTOR (the n=2 group counts as 2, not 1)",
          rows_am2["A1"]["bucket"] == "MOTOR" and rows_am2["A1"]["driven"] and
          rows_am2["A2"]["bucket"] == "MOTOR" and rows_am2["A2"]["driven"])
    check("undercount fix, all-motor-only group, motorCount=2: B1 stays a "
          "driven SERVO (NOT stolen into a dead MOTOR by the undercount -- "
          "this is the regression the fix removes)",
          rows_am2["B1"]["bucket"] == "SERVO" and rows_am2["B1"]["driven"])

    r_am3 = simulate(synth_all_motor, motor_count=3, servo_count=None,
                     adc_pins=set(), led_strip_active=False,
                     dma_resolver=synth_resolver, dshot=False)
    rows_am3 = {row["entry"].label: row for row in r_am3.rows}
    check("undercount fix, all-motor-only group, motorCount=3: B1 IS "
          "promoted to driven MOTOR only when the user actually asks for 3",
          rows_am3["B1"]["bucket"] == "MOTOR" and rows_am3["B1"]["driven"])

    # --- Reference point 4c: mixed group (1 pad declared motor-only + 1 AUTO
    # sibling on the same timer) still counts exactly n -- guards against both
    # the original 2n-1 overcount and any overcount re-introduced by the
    # corrected pass 1.
    SYNTHETIC_MIXED_TARGET_C = """
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM_A,  CH1, PA1,  TIM_USE_MOTOR,            1, 0), // A1
    DEF_TIM(TIM_A,  CH2, PA2,  TIM_USE_OUTPUT_AUTO,      1, 0), // A2
    DEF_TIM(TIM_B,  CH1, PA3,  TIM_USE_OUTPUT_AUTO,      1, 0), // B1
};
"""
    synth_mixed = parse_target_c(SYNTHETIC_MIXED_TARGET_C)

    r_mx2 = simulate(synth_mixed, motor_count=2, servo_count=None,
                     adc_pins=set(), led_strip_active=False,
                     dma_resolver=synth_resolver, dshot=False)
    rows_mx2 = {row["entry"].label: row for row in r_mx2.rows}
    check("mixed group, motorCount=2: A1 and A2 are driven MOTOR (group "
          "counts as 2, not 2n-1=3), B1 stays SERVO",
          rows_mx2["A1"]["bucket"] == "MOTOR" and rows_mx2["A1"]["driven"] and
          rows_mx2["A2"]["bucket"] == "MOTOR" and rows_mx2["A2"]["driven"] and
          rows_mx2["B1"]["bucket"] == "SERVO")

    r_mx3 = simulate(synth_mixed, motor_count=3, servo_count=None,
                     adc_pins=set(), led_strip_active=False,
                     dma_resolver=synth_resolver, dshot=False)
    rows_mx3 = {row["entry"].label: row for row in r_mx3.rows}
    check("mixed group, motorCount=3: B1 promoted to driven MOTOR (group "
          "counted exactly 2, so pass 2 promotes at mc=3 -- the 2n-1 "
          "overcount would have left B1 SERVO here)",
          rows_mx3["B1"]["bucket"] == "MOTOR" and rows_mx3["B1"]["driven"])

    # --- Reference point 5: DAKEFPVF405WING LED-preserving multi-motor
    # config -- TIM3 forced to OUTPUT_MODE_SERVOS protects BOTH S2 and S3
    # (pwmClaimTimer force-syncs them) from ever entering the MOTOR bucket,
    # so S3 can never claim DMA1 Stream2 and collide with the LED strip
    # (also DMA1 Stream2), at ANY motor count. ---
    dak_modes = {"TIM3": "SERVOS"}
    any_collision = False
    for mc in range(1, 9):
        r = simulate(entries2, motor_count=mc, servo_count=None, adc_pins=set(),
                     led_strip_active=True, dma_resolver=dma_resolver, dshot=True,
                     timer_output_modes=dak_modes)
        if any("DMA_STREAM_COLLISION" in h for h in r.hazards):
            any_collision = True
    check("DAKEFPVF405WING, TIM3=SERVOS override: NO DMA_STREAM_COLLISION "
          "at any motorCount 1..8 (LED preserved unconditionally)",
          not any_collision)

    r_mc6 = simulate(entries2, motor_count=6, servo_count=None, adc_pins=set(),
                      led_strip_active=True, dma_resolver=dma_resolver, dshot=True,
                      timer_output_modes=dak_modes)
    rows6 = {row["entry"].label: row for row in r_mc6.rows}
    check("DAKEFPVF405WING, TIM3=SERVOS, motorCount=6: S1,S6,S7,S8,S9,S10 all "
          "driven MOTOR (the max LED-preserving motor count)",
          all(rows6[s]["bucket"] == "MOTOR" and rows6[s]["driven"]
              for s in ("S1", "S6", "S7", "S8", "S9", "S10")))
    check("DAKEFPVF405WING, TIM3=SERVOS, motorCount=6: S2 and S3 are SERVO "
          "(never MOTOR), confirming both channels of the forced timer are "
          "protected, not just the one a naive per-channel fix would target",
          rows6["S2"]["bucket"] == "SERVO" and rows6["S3"]["bucket"] == "SERVO")

    # --- Real-world regression: 2026-08-14 bench report. Board flashed with
    # S1/S6/S7/S8/S9/S10 all resolving to driven MOTOR (matches the table
    # above) reported NO SIGNAL on S10 specifically, while S8/S9 worked.
    # pwmClaimTimer's cross-channel cascade makes a split MOTOR/SERVO outcome
    # within one shared-timer group (S8/S9/S10 all share TIM1) structurally
    # impossible -- confirmed above, all three always move together -- so the
    # role-resolution layer this script already modeled was never the cause.
    # Root cause (confirmed against upstream commit ab07785fa9, "Fix channel
    # selection for DMA2 Stream6", which made this exact change to 4 other
    # real boards): target.c's S10 used dmavar=0, i.e. D(2,6,0), which
    # timer_def_stm32f4xx.h also lists as an option for TIM1_CH1 and
    # TIM1_CH2 -- the combined/shared multi-channel request line, not a
    # request dedicated to CH3's own compare event. dmavar=1 (D(2,6,6)) is
    # the CH3-specific line and is what every other real F4-family INAV
    # target uses. This is the SHARED_TIMER_DMA_REQUEST hazard.
    #
    # UPDATE 2026-08-15 (dakefpvf405wing-hardware-bringup, unrelated to this
    # fix): target.c's S10 dmavar was changed 0 -> 1 as part of that task, so
    # the hazard this reference point exists to catch no longer reproduces
    # against the current file -- that's the fix working as intended, not a
    # regression in this script. Assertion updated to match; kept as a
    # regression guard against the dmavar reverting to 0.
    check("DAKEFPVF405WING, TIM3=SERVOS, motorCount=6: S10 (TIM1_CH3) no "
          "longer triggers SHARED_TIMER_DMA_REQUEST now that target.c uses "
          "dmavar=1 (the CH3-dedicated line) -- confirms the dakefpvf405wing "
          "-hardware-bringup fix is still in place",
          not any("SHARED_TIMER_DMA_REQUEST" in h and "TIM1_CH3" in h
                  for h in r_mc6.hazards))

    r_mc3 = simulate(entries2, motor_count=3, servo_count=None, adc_pins=set(),
                      led_strip_active=True, dma_resolver=dma_resolver, dshot=True,
                      timer_output_modes=dak_modes)
    rows3d = {row["entry"].label: row for row in r_mc3.rows}
    check("DAKEFPVF405WING, TIM3=SERVOS, motorCount=3: exactly S1,S6,S7 are "
          "live MOTORs (no inflation at this config -- no MOTORS override is "
          "used, only SERVOS on TIM3, which never triggers pass 1's "
          "double-count since SERVOS-forced entries never satisfy "
          "TIM_IS_MOTOR_ONLY); S8/S9/S10 fall back to SERVO as a group "
          "(the whole TIM1 group demotes together, all-or-nothing, since "
          "motor_only_outputs(3) < motorCount(3) is false at S8)",
          rows3d["S1"]["bucket"] == "MOTOR" and rows3d["S1"]["driven"]
          and rows3d["S6"]["bucket"] == "MOTOR" and rows3d["S6"]["driven"]
          and rows3d["S7"]["bucket"] == "MOTOR" and rows3d["S7"]["driven"]
          and rows3d["S8"]["bucket"] == "SERVO"
          and rows3d["S9"]["bucket"] == "SERVO"
          and rows3d["S10"]["bucket"] == "SERVO")

    # --- Reference point 6: SHARED_TIMER_DMA_REQUEST SOLO vs. SPURIOUS
    # TRIGGERS (Phase 2 step 5, investigate-shared-tim-dma-request-lines).
    # Isolated minimal targets, not the DAKEFPVF405WING fixture above, so
    # each scenario exercises exactly one thing: whether a combined-line
    # user (dmavar=0 on TIM1_CH1, a real F4 advanced-timer channel) is
    # flagged depends ONLY on whether a sibling channel of that same
    # combined group is also genuinely declared+driven, not merely on
    # whether the header table says the tuple COULD be shared.
    SOLO_SHARED_LINE_TARGET_C = '''
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM1,  CH1, PA8,  TIM_USE_OUTPUT_AUTO,  0, 0), // S1
};
'''
    solo_entries = parse_target_c(SOLO_SHARED_LINE_TARGET_C)
    r_solo = simulate(solo_entries, motor_count=1, servo_count=None, adc_pins=set(),
                       led_strip_active=False, dma_resolver=dma_resolver, dshot=True)
    check("SOLO: lone TIM1_CH1 dmavar=0 (combined line), no sibling TIM1 "
          "channel declared at all -- NOT flagged (nothing else can ever "
          "trigger this line)",
          not any("SHARED_TIMER_DMA_REQUEST" in h for h in r_solo.hazards))

    SPURIOUS_SHARED_LINE_TARGET_C = '''
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM1,  CH1, PA8,  TIM_USE_OUTPUT_AUTO,  0, 0), // S1
    DEF_TIM(TIM1,  CH2, PA9,  TIM_USE_OUTPUT_AUTO,  0, 1), // S2
};
'''
    spurious_entries = parse_target_c(SPURIOUS_SHARED_LINE_TARGET_C)
    r_spurious = simulate(spurious_entries, motor_count=2, servo_count=None,
                           adc_pins=set(), led_strip_active=False,
                           dma_resolver=dma_resolver, dshot=True)
    check("SPURIOUS TRIGGERS: TIM1_CH1 dmavar=0 (combined line) with sibling "
          "TIM1_CH2 declared AND driven on its own dedicated line (dmavar=1, "
          "a different DMA stream -- so no DMA_STREAM_COLLISION masks this) "
          "-- IS flagged (S2's compare events also land on S1's shared line)",
          any("SHARED_TIMER_DMA_REQUEST" in h and "TIM1_CH1" in h
              for h in r_spurious.hazards))
    check("SPURIOUS TRIGGERS scenario: confirms S1/S2 resolve to genuinely "
          "different DMA streams (S2 on its dedicated line, not colliding "
          "with S1 -- so the flag above is SHARED_TIMER_DMA_REQUEST doing "
          "its job, not DMA_STREAM_COLLISION firing instead)",
          not any("DMA_STREAM_COLLISION" in h for h in r_spurious.hazards))

    # --- Reference point 7: the SOLO check must survive an N-CHANNEL entry.
    # The header table is keyed on BASE channels only (no ('TIM1','CH2N')
    # key -- _lookup() falls back by stripping the N), while
    # active_ch_by_tim is de-N'd too. Before the fix, group_siblings
    # excluded only the RAW 'CH2N' key, so the entry's own base 'CH2'
    # counted as a sibling and matched itself: every lone N-channel on a
    # combined request line was reported as SHARED_TIMER_DMA_REQUEST. That
    # false positive is not academic -- TIM1_CH2N/TIM1_CH3N on PB14/PB15 is
    # the standard F405 escape route off DMA-less TIM12, so the bogus flag
    # landed squarely on the fix for a real SILENT_DEAD_MOTOR.
    SOLO_NCHANNEL_TARGET_C = '''
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM1,  CH2N, PB14, TIM_USE_OUTPUT_AUTO,  0, 0), // S1
};
'''
    solo_n_entries = parse_target_c(SOLO_NCHANNEL_TARGET_C)
    r_solo_n = simulate(solo_n_entries, motor_count=1, servo_count=None,
                         adc_pins=set(), led_strip_active=False,
                         dma_resolver=dma_resolver, dshot=True)
    check("SOLO, N-channel: lone TIM1_CH2N dmavar=0 (combined line), no other "
          "TIM1 channel declared -- NOT flagged (regression guard: the raw "
          "'CH2N' key must be de-N'd before excluding the entry's own "
          "channel from the sibling set, or it self-matches)",
          not any("SHARED_TIMER_DMA_REQUEST" in h for h in r_solo_n.hazards))
    check("SOLO, N-channel: TIM1_CH2N still resolves to a real DMA stream "
          "(confirms the case above is a genuine SOLO combined-line user, "
          "not silently skipped for having no DMA at all)",
          not any("SILENT_DEAD_MOTOR" in h for h in r_solo_n.hazards))

    SPURIOUS_NCHANNEL_TARGET_C = '''
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM1,  CH2N, PB14, TIM_USE_OUTPUT_AUTO,  0, 0), // S1
    DEF_TIM(TIM1,  CH1,  PA8,  TIM_USE_OUTPUT_AUTO,  0, 1), // S2
};
'''
    spur_n_entries = parse_target_c(SPURIOUS_NCHANNEL_TARGET_C)
    r_spur_n = simulate(spur_n_entries, motor_count=2, servo_count=None,
                         adc_pins=set(), led_strip_active=False,
                         dma_resolver=dma_resolver, dshot=True)
    check("SPURIOUS TRIGGERS, N-channel: TIM1_CH2N dmavar=0 (combined line) "
          "WITH a genuinely driven sibling TIM1_CH1 on its own dedicated "
          "line -- IS still flagged (the de-N fix must not blanket-suppress "
          "N-channels, only stop them matching themselves)",
          any("SHARED_TIMER_DMA_REQUEST" in h and "TIM1_CH2N" in h
              for h in r_spur_n.hazards))

    # --- Reference point 8: TIMER_CHANNEL_DUPLICATE. Two pins declared on
    # one compare register cannot be driven independently for ANY protocol,
    # which is strictly worse than any DMA hazard -- yet the DMA checks can
    # be completely silent about it when the two entries pick different
    # dmavars (different streams => no DMA_STREAM_COLLISION). Found while
    # evaluating TIM8_CH3N on PB15 as an escape from DMA-less TIM12_CH2 on
    # a board that already drove TIM8_CH3 on PC8: every DMA check came back
    # clean on a change that would have bricked an output.
    DUP_TARGET_C = '''
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM8,  CH3N, PB15, TIM_USE_OUTPUT_AUTO,  0, 1), // S1
    DEF_TIM(TIM8,  CH3,  PC8,  TIM_USE_OUTPUT_AUTO,  0, 0), // S2
};
'''
    dup_entries = parse_target_c(DUP_TARGET_C)
    r_dup = simulate(dup_entries, motor_count=2, servo_count=None,
                      adc_pins=set(), led_strip_active=False,
                      dma_resolver=dma_resolver, dshot=True)
    check("TIMER_CHANNEL_DUPLICATE: TIM8_CH3N (PB15) and TIM8_CH3 (PC8) are "
          "the same compare register -- flagged even though their dmavars "
          "resolve to different DMA streams, so no DMA check fires",
          any("TIMER_CHANNEL_DUPLICATE" in h for h in r_dup.hazards))
    check("TIMER_CHANNEL_DUPLICATE scenario: confirms no DMA_STREAM_COLLISION "
          "fires here (the duplicate is invisible to every DMA check -- that "
          "is exactly why it needs its own hazard class)",
          not any("DMA_STREAM_COLLISION" in h for h in r_dup.hazards))

    NODUP_TARGET_C = '''
timerHardware_t timerHardware[] = {
    DEF_TIM(TIM8,  CH2N, PB14, TIM_USE_OUTPUT_AUTO,  0, 1), // S1
    DEF_TIM(TIM8,  CH3,  PC8,  TIM_USE_OUTPUT_AUTO,  0, 1), // S2
};
'''
    nodup_entries = parse_target_c(NODUP_TARGET_C)
    r_nodup = simulate(nodup_entries, motor_count=2, servo_count=None,
                        adc_pins=set(), led_strip_active=False,
                        dma_resolver=dma_resolver, dshot=True)
    check("TIMER_CHANNEL_DUPLICATE control: TIM8_CH2N and TIM8_CH3 are "
          "DIFFERENT compare registers on the same timer -- NOT flagged "
          "(the check must key on the de-N'd channel, not on the timer)",
          not any("TIMER_CHANNEL_DUPLICATE" in h for h in r_nodup.hazards))

    print()
    print("SELFTEST " + ("PASSED" if ok else "FAILED"))
    return ok


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("inav_root", help="Path to an INAV checkout")
    ap.add_argument("--target", help="Target directory name (required unless --selftest)")
    ap.add_argument("--motor-count", type=int, help="Simulate exactly this motor count")
    ap.add_argument("--servo-count", type=int, default=None,
                     help="Cap the servo bucket the same way --motor-count caps the "
                          "motor bucket (default: unlimited)")
    ap.add_argument("--sweep", default=None,
                     help="MIN:MAX motor count range to sweep (default: 1..entry count)")
    ap.add_argument("--no-dshot", action="store_true",
                     help="Assume plain PWM/Oneshot/Multishot motors, not DSHOT")
    ap.add_argument("--no-led-strip", action="store_true",
                     help="Assume FEATURE_LED_STRIP is never enabled")
    ap.add_argument("--force-led-strip", action="store_true",
                     help="Assume FEATURE_LED_STRIP is active even if not obviously so")
    ap.add_argument("--verbose", action="store_true",
                     help="Print the full per-output table for every swept motor count")
    ap.add_argument("--selftest", action="store_true",
                     help="Run built-in regression cases instead of checking a target")
    ap.add_argument("--dmavar-override", action="append", default=[],
                     metavar="LABEL=N",
                     help="Simulate changing an entry's dmavar (the DEF_TIM "
                          "trailing DMA-option index) WITHOUT editing target.c "
                          "on disk. LABEL is the entry's // comment label "
                          "(e.g. S8), N is the new dmavar. Repeatable, e.g. "
                          "--dmavar-override S8=1 --dmavar-override S9=1. "
                          "Use this to answer 'does moving entry X to a "
                          "different DMA option eliminate collision Y across "
                          "a motorCount sweep' before touching the real file.")
    ap.add_argument("--timer-output-mode", action="append", default=[],
                     metavar="TIMn=MODE",
                     help="Simulate a timer_output_mode CLI/config.c override "
                          "(timerOverridesMutable(timer2id(TIMn))->outputMode) "
                          "WITHOUT editing any file on disk. TIMn is the `tim` "
                          "token used in this target's DEF_TIM(...) entries "
                          "(e.g. TIM3); MODE is AUTO, MOTORS, SERVOS, or LED. "
                          "Repeatable, e.g. --timer-output-mode TIM3=SERVOS.")
    args = ap.parse_args()

    inav_root = Path(args.inav_root).expanduser().resolve()

    if args.selftest:
        ok = _selftest(inav_root)
        sys.exit(0 if ok else 1)

    if not args.target:
        raise SystemExit("--target NAME is required (or use --selftest)")

    led_override = None
    if args.no_led_strip:
        led_override = False
    if args.force_led_strip:
        led_override = True

    sweep_range = None
    if args.sweep:
        lo, hi = args.sweep.split(":")
        sweep_range = (int(lo), int(hi))

    target_dir = inav_root / "src" / "main" / "target" / args.target
    if sweep_range is None and args.motor_count is None:
        entry_count = len(parse_target_c((target_dir / "target.c").read_text(errors="ignore")))
        sweep_range = (1, entry_count)

    dmavar_overrides = {}
    for spec in args.dmavar_override:
        if "=" not in spec:
            raise SystemExit(f"--dmavar-override must be LABEL=N, got {spec!r}")
        label, val = spec.split("=", 1)
        label = label.strip()
        try:
            dmavar_overrides[label] = int(val.strip())
        except ValueError:
            raise SystemExit(f"--dmavar-override: N must be an integer, got {spec!r}")

    timer_output_modes = {}
    for spec in args.timer_output_mode:
        if "=" not in spec:
            raise SystemExit(f"--timer-output-mode must be TIMn=MODE, got {spec!r}")
        tim, mode = spec.split("=", 1)
        tim = tim.strip().upper()
        mode = mode.strip().upper()
        if mode not in OUTPUT_MODE_TOKENS:
            raise SystemExit(
                f"--timer-output-mode: MODE must be one of {OUTPUT_MODE_TOKENS}, "
                f"got {mode!r} (from {spec!r})"
            )
        timer_output_modes[tim] = mode

    run_target(inav_root, args.target, args.motor_count, args.servo_count,
               sweep_range, not args.no_dshot, led_override, args.verbose,
               dmavar_overrides=dmavar_overrides,
               timer_output_modes=timer_output_modes)


if __name__ == "__main__":
    main()
