# target-developer Tools

**Purpose:** Permanent tools and scripts for the target-developer agent

## Scripts

### check_macro_typos.py
**Purpose:** Flags target.h #defines that look like typos of a real INAV macro (e.g. `BEEPER_PIN` instead of `BEEPER`) -- a wrong name compiles cleanly but silently disables whatever feature it was supposed to guard.
**Usage:** `./scripts/check_macro_typos.py <inav_checkout_root> --target TARGETNAME`
**Created:** 2026-07-05 -- after DAKEFPVH743_SLIM's beeper was silently dead for exactly this reason; see the target-developer lessons-learned entry for the full incident and known false-positive patterns.

### check_dma_conflicts.py
**Purpose:** Flags STM32H7 DMA stream (`dmaopt`) collisions in a target's `timerHardware[]` table -- both timer-vs-timer (e.g. LED strip and a motor sharing a stream) and timer-vs-ADC (ADC1/2/3's DMA stream is hardcoded outside target.h, so nothing else catches this). Reports two severities: CERTAIN (a quad's first 4 motor/servo positions, or an always-active LED/ADC -- affects every build) vs NOTICE (position 4+ only, e.g. extra servo outputs -- not required for a quad but still worth fixing).
**Usage:** `./scripts/check_dma_conflicts.py <inav_checkout_root> [--target TARGETNAME]` (omit `--target` to scan every STM32H7 target at once)
**Created:** 2026-07-07 -- after a UART8/ADC/beeper investigation on AXISFLYINGH743PRO led to discovering this same bug class already confirmed on AEDROXH7 and DAKEFPVH743PRO. A full-tree run immediately found the AEDROXH7 fix (PR #11629/#11630) had itself introduced a *new* instance of the bug -- see the README's "Cross-target pin matches confirm AF-validity, not board wiring" pattern entry for how that was traced. Also found 4 more previously-unknown CERTAIN cases (KAKUTEH7WING, SEQUREH7, TBS_LUCID_H7_WING, TBS_LUCID_H7_WING_MINI) on the first full-tree run -- reported to the manager for tracking rather than fixed inline.

### check_pin_conflicts.py
**Purpose:** Flags a single physical MCU pin assigned to more than one peripheral macro in the same target's target.h (e.g. `UART8_RX_PIN` and `SPI4_MISO_PIN` both `PE0`) -- a compiler can't catch this since each macro is an independent #define. Common benign case: two alternate chip variants (e.g. `MPU6000_CS_PIN`/`ICM42605_CS_PIN`) sharing one CS pin by design.
**Usage:** `./scripts/check_pin_conflicts.py <inav_checkout_root> [--target TARGETNAME]`
**Created:** 2026-07-07, alongside check_dma_conflicts.py.

### check_default_features.py
**Purpose:** Flags a target.h with no `DEFAULT_FEATURES` macro at all (falls back to `0` -- every feature silently off, per `fc/config.c`'s `#ifndef` default) or one whose value looks suspiciously thin (< 80 chars, usually a sign of a dropped feature set rather than a deliberately minimal board).
**Usage:** `./scripts/check_default_features.py <inav_checkout_root> [--target TARGETNAME]`
**Created:** 2026-07-07 -- after AXISFLYINGH743PRO's ADC and OSD both looked hardware-broken (pins/wiring were correct, verified against the vendor's own Betaflight source) but were actually just never turned on, because target.h had no `DEFAULT_FEATURES` line at all. `check_macro_typos.py` can't catch this class of bug -- there's no wrong name to flag, the line is just missing.

### check_board_identifier.py
**Purpose:** Flags a `TARGET_BOARD_IDENTIFIER` that isn't exactly 4 characters, or that's shared with another target (both cause silent board mis-identification at runtime -- see the [[target-developer]] lesson on this).
**Usage:** `./scripts/check_board_identifier.py <inav_checkout_root> [--target TARGETNAME]`
**Created:** 2026-07-07 -- a full-tree run found 36 targets with a non-4-char identifier and 15 groups of targets sharing one, none reported as causing an actual problem yet but worth fixing on sight, especially for new targets where a fresh collision is easy to avoid.

### check_serial_port_count.py
**Purpose:** Two checks: (1) `SERIAL_PORT_COUNT` doesn't match VCP + `USE_UARTn` + `USE_SOFTSERIALn` actually defined -- skips any target.h with more than one `SERIAL_PORT_COUNT` `#define` (multi-variant boards like CLRACINGF4AIR need real preprocessing to check correctly, so it's left alone rather than guessed at). (2) `DEFAULT_FEATURES` includes `FEATURE_SOFTSERIAL` but no `USE_SOFTSERIALn` is defined at all -- confirmed harmless (every consumer gates on `#if defined(USE_SOFTSERIALn)`), but a reliable sign of copy-paste cruft, reported as NOTICE.
**Usage:** `./scripts/check_serial_port_count.py <inav_checkout_root> [--target TARGETNAME]`
**Created:** 2026-07-07 -- full-tree run: 0 CERTAIN (count mismatches) after excluding 9 multi-variant files, 10 NOTICE (dead `FEATURE_SOFTSERIAL` bit).

### check_target_invariants.py
**Purpose:** Three small single-rule regression guards bundled in one script (each is a handful of lines, none has ever fired on the current tree): `BEEPER_PWM_FREQUENCY` requires a `DEF_TIM(...TIM_USE_BEEPER...)` entry in target.c; `GYRO_n_EXTI_PIN`/`USE_GYRO_EXTI` requires a `BUSDEV_REGISTER_SPI_TAG` entry (the legacy `USE_IMU_xxx` gyro path is polled and never reads an EXTI pin); AT32 targets (detected via `target_at32f43x*(...)` in CMakeLists.txt) need every UART's TX pin explicitly defined, even as `NONE`, for RX-only ports -- the AT32 driver dereferences it unconditionally.
**Usage:** `./scripts/check_target_invariants.py <inav_checkout_root> [--target TARGETNAME]`
**Created:** 2026-07-07. All three checks: 0 findings across 233 targets -- pure regression guards, not backlog.

### simulate_pwm_roles.py
**Purpose:** Deterministic simulation of INAV's motor/servo timer role-resolution algorithm (`pwmClaimTimer`/`pwmEnsureEnoughtMotors`/`pwmBuildTimerOutputList` in `drivers/pwm_mapping.c`), plus the two hazards that ride on top of it: a MOTOR-resolved, genuinely-initialized output with *no DMA request line at all* for its (timer, channel) on this MCU (silent DSHOT failure -- `pwmMotorConfig()` reports success anyway), and two genuinely-live DMA users (DSHOT motors and/or LED strip) whose only DMA option resolves to the same (controller, stream). Unlike hand-tracing, this actually runs the C algorithm's exact mutation order -- including the fact that `pwmClaimTimer()` force-overwrites `usageFlags` on every `timerHardware[]` entry sharing a physical timer, so a channel's own declared `TIM_USE_SERVO` does NOT protect it from being dragged into MOTOR role by a sibling on the same timer. Supports F4/F7/H7/AT32 (auto-detected from CMakeLists.txt); H7's DMA-stream addressing reuses `check_dma_conflicts.py`'s tables directly rather than duplicating them.
**Also emits `TIMER_CHANNEL_DUPLICATE`** (added 2026-09-04): two DEF_TIM entries on different pins sharing one compare register, keyed on the de-N'd channel so a `CHx`/`CHxN` pair counts. Strictly worse than any DMA hazard -- the second pad cannot be driven independently for *any* protocol -- and completely invisible to the DMA checks whenever the two entries pick different dmavars.
**Usage:** `./scripts/simulate_pwm_roles.py <inav_checkout_root> --target NAME [--motor-count N | --sweep MIN:MAX] [--servo-count N] [--no-dshot] [--no-led-strip]` -- omit both `--motor-count` and `--sweep` to sweep the full plausible range and print only the hazards found at each count. `./scripts/simulate_pwm_roles.py --selftest <inav_checkout_root>` runs the built-in regression cases.
**Created:** 2026-08-14 -- after a session hand-traced this exact algorithm for DAKEFPVF405WING and got it wrong twice in one conversation (including presenting an unachievable "S2 solo DSHOT + S3 working servo" recommendation as verified). Validated against DAKEFPVF405WING's shipped and in-session-edited target.c as regression cases (see the script's `--selftest`), and smoke-tested against all 213 non-SITL targets in the tree with zero crashes and zero unresolved DMA-table lookups.

### check_timer_pin_af.py
**Purpose:** Validates every `DEF_TIM(tim, ch, pin, ...)` triple in target.c against the indexed datasheet alternate-function table (`claude/developer/docs/targets/<mcu>/alternate-functions.tsv`, loaded through the shared `af_tables.py`). This is the *only* check for a bug class the compiler cannot catch on STM32F4: `drivers/timer_def_stm32f4xx.h:25` builds the pin's AF number from the TIMER NAME alone (`GPIO_AF_ ## tim`) with no per-pin table, so a wrong triple compiles cleanly and just leaves the pad silently dead -- the GPIO gets muxed to that timer's AF (i.e. to whichever of the timer's signals the silicon routes to that pad) while the driver programs the compare register and output-enable bit of a *different* channel. F7/H7/AT32 carry per-pin `DEF_TIM_AF__P<pin>__TCH_<TIM>_<CH>` tables so the same mistake is a build failure there; findings on those families are still reported but labelled as compile-time-caught. Three kinds: `N_MISMATCH` (pad carries `TIMn_CHmN` but target declares `TIMn_CHm` or vice versa -- wrong enable bit, and invisible to every DMA check since `timer_def.h` aliases the N-channel's DMA request to its base channel's), `WRONG_CHANNEL` (right timer, wrong channel -- the AF mux happens to be right since a timer's channels share one AF number), `TIMER_NOT_ON_PIN`.
**Usage:** `./scripts/check_timer_pin_af.py <inav_checkout_root> [--target TARGETNAME] [--show-unknown]`
**Created:** 2026-09-04, while auditing SILENT_DEAD_MOTOR outputs. First full-tree run: **9 findings across 90 F405 targets, 0 across the 90 F7/AT32 targets** -- `ALIENFLIGHTF4` (PB15 `TIM1_CH3` vs the pad's `TIM1_CH3N`, on the LED strip pin), `BLUEJAYF4` and `FF_PIKOF4` (PB0/PB1 declared with TIM3's channels swapped), `FLYCOLORF4` (PB14 `TIM1_CH3` vs `TIM1_CH2N`), `HAKRCF405D` (PB8 `TIM4_CH1` vs `TIM4_CH3`), `KROOZX` (PB14/PB15 on TIM4, which doesn't reach either pad). 56 targets skipped for lack of an indexed datasheet (F411/F427/H7/RP2350) -- the F411/F427 ones have the same silent exposure and remain unverified.

### find_dead_motor_fix.py
**Purpose:** The `SILENT_DEAD_MOTOR` counterpart to `find_shared_dma_fix.py`, searching **pin remaps** (a different timer/channel on the same physical pad) rather than dmavar reassignments. Necessary because `SILENT_DEAD_MOTOR` means the (timer, channel) has no DMA option list at all -- `TIM9`/`TIM10`/`TIM11`/`TIM12` and `TIM4_CH4` are all `NONE` on F405 -- so no dmavar can help and the dmavar-only searcher structurally cannot fix one. Most pads reach several timers and the alternates usually do have DMA. Every candidate must pass three hard rules: datasheet-confirmed routing, no `(timer, de-N'd channel)` duplicate with an existing entry (two pads on one compare register can only mirror each other -- worse than losing DSHOT, and invisible to every DMA check when the two entries pick different dmavars), and no new or earlier-biting hazard anywhere in the motorCount sweep. A second **co-fix pass** additionally tries alternate dmavars on unrelated healthy entries that happen to hold the stream the remap needs. Reports only; never edits target.c.
**Usage:** `./scripts/find_dead_motor_fix.py <inav_checkout_root> --target NAME [--target NAME ...] | --targets-file FILE | --all-f4 [--min-position N] [--max-position N]` (positions default to 0..3, the basic-quad S1-S4 range).
**Created:** 2026-09-04. Full-tree scan at position 0-3 found 6 non-conditional targets, 4 of them cleanly fixable (`FISHDRONEF4`, `SPARKY2`, `BLUEJAYF4`, `COLIBRI`). The unfixable ones all trace to one pin: **F405 PB9 offers only `TIM4_CH4` and `TIM11_CH1`, and both are DMA-less** (`ALIENFLIGHTF4`, `FF_F35_LIGHTNING`, and at higher positions `ANYFCF7`, `CORVON405V2`, `KROOZX`, `MICOAIR405MINI`, `MICOAIR405V2`).

### af_tables.py
**Purpose:** Shared library (not a standalone check) behind the two scripts above: loads the datasheet AF TSVs, maps a target directory to the right MCU index via its `CMakeLists.txt`, normalizes AT32's `TMRn` spelling and the `TIM2_CH1_ETR` / `TIM2_CH1/TIM2_ETR` cell formats, and parses the firmware-side `DEF_TIM_AF__*` tables for F7/H7/AT32. Deliberately returns `None` for MCUs with no indexed datasheet (F411, F427, H7, RP2350) so callers report "unverifiable" rather than substituting a different F4 variant's table -- "F4" pools parts with genuinely different AF tables, and assuming otherwise is the mistake the datasheet indexes exist to prevent.

### run_target_checks.py
**Purpose:** Driver that runs all of the above checks in one pass with consistent section headers. Run this before opening a PR for a new/modified target, or to verify a fix for any of these bug classes actually resolved it.
**Usage:** `./scripts/run_target_checks.py <inav_checkout_root> [--target TARGETNAME]`
**Created:** 2026-07-07. Add new standard checks by appending to its `CHECKS` list -- any script following the same `<inav_root> [--target NAME]` calling convention slots in directly.

## Data

### known_good_macros.txt
**Purpose:** Cached list of macro names confirmed to be both (a) defined by some target's target.h and (b) actually referenced elsewhere in core firmware source. Used by check_macro_typos.py so repeat runs don't re-scan the whole tree.
**Generated by:** `scripts/check_macro_typos.py` (automatically, on first run against a checkout)
**Regenerate with:** `--rebuild-cache` after a large core refactor, in case a macro that used to be real was removed

## Patterns

### New-target PRs: post the hardware bring-up checklist

For any PR that adds a **brand new** target (not an update to an existing
one), post a PR comment with the hardware bring-up checklist from
`raytools/fc_hardware_test_tools/checklist.txt`, trimmed to only the
buses/features that board actually has (e.g. drop `UARTn` entries for UARTs
the target doesn't define, drop `PINIO2` if the board only has one PINIO
pin). This gets used later during physical hardware testing -- see
`gh pr comment <PR> --repo iNavFlight/inav --body "..."` in the AXISFLYINGECOF4
PR (#11692, added 2026-07-06) for the pattern.

### Porting/updating a target from a Betaflight config.h
**See:** `claude/developer/docs/patterns/betaflight-config-to-inav-target.md` -- recurring
translation rules (PINIO -> config.c permanentId, CAMERA_CONTROL_PIN has no consuming driver
prior to 10.0 -- it becomes a PWM-capable PINIO pin from 10.0 forward, new-chip-on-existing-bus
pattern, MCU->CMakeLists mapping, reference-target selection) plus known gaps in the existing
`src/utils/bf2inav.py` generator. Created 2026-07-06 after three concurrent tasks (DAKEFPVF405
update, AxisFlying H743 PRO, AxisFlying ECO F4) turned out to share this exact pattern.

### Cross-target pin matches confirm AF-validity, not board wiring
When many unrelated vendors' targets use the same pin for the same peripheral (e.g. nearly every
STM32H7 target puts ADC1's channels on PC0/PC1), that widespread match rules out an AF-invalid
pin choice -- it couldn't compile/work on any of those boards otherwise -- but says nothing about
whether *this specific* physical board's traces/solder actually connect that MCU pin through to
the connector for that peripheral.

Matching one specific sibling target, even a field-verified working one, is *not* stronger
evidence, and it's tempting to think it is -- don't. New targets are routinely created by copying
an existing target's file and editing it for the new board (see the bf2inav.py / reference-target
pattern above); a pin left over from that copy, never actually updated for the new schematic,
matches the source target exactly. That's indistinguishable in target.h from a pin that's correct
because the boards genuinely share a schematic -- and "copied a working target, then didn't update
every pin for the new hardware" is itself one of the most common ways a target ships broken. So a
match against any other target, no matter how it's chosen, only ever establishes AF-validity; it
cannot establish that this physical board is wired the way its target.h claims. Only a
datasheet/schematic/continuity check against the specific board settles that. Created 2026-07-07
while investigating AXISFLYINGH743PRO's non-working UART8: firmware-level checks (pin/AF/RCC/IRQ
wiring matched several other H7 targets exactly) came back clean, which ruled out an AF-invalid
mapping but could not rule out this target's UART8 pins being an un-updated leftover from
whatever target it was based on -- exactly the failure mode a continuity or schematic check
against the real board is needed for.

### Avoid UART1/UART3 for the default receiver or GPS port
Some vendor reference designs (SpeedyBee in particular) default `SERIALRX_UART`/GPS wiring to
UART1 or UART3. Don't copy that as a pattern to emulate when authoring or reviewing a new target
-- a receiver or GPS connected there can interfere with flashing over the same UART. Prefer
UART2/UART4/etc. for these roles unless the board's physical wiring leaves no other option.
Raised 2026-08-15 during DAKEFPVF405WING bring-up, where a PR author's update moved
`SERIALRX_UART`/added `GPS_UART` off UART1/UART3 onto UART2/UART4 for exactly this reason.
