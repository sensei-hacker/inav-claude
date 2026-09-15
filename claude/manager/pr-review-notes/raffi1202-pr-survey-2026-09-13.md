# Raffi1202 PR Survey — 2026-09-13

Manager survey of all pull requests by GitHub user **Raffi1202** on `iNavFlight/inav` and
`iNavFlight/inav-configurator`, cross-referenced against our own active projects
(`claude/projects/INDEX.md`) and projects completed/cancelled in the last 30 days
(`claude/projects/completed/INDEX.md`, since 2026-08-14). One line of initial impression per PR,
based on title + PR description only (no code review, no testing). 39 inav PRs + 30 configurator
PRs = 69 total.

**7 PRs matched an open project of ours** — those project summaries were updated with a "Proposed
Solution (Untested)" note; see the list at the bottom of this file. Every PR here needs real
testing (by us or someone else) before its claims should be trusted — this is a first-pass skim,
not a review.

## iNavFlight/inav

- [#11850](https://github.com/iNavFlight/inav/pull/11850) — CRSF: selectable altitude source (ESTIMATED/MSL) for GPS frame. Reasonable-sounding compatibility knob following on from #11168; no project of ours.
- [#11851](https://github.com/iNavFlight/inav/pull/11851) — MAVLink: allow in-flight mission upload/clear when not executing, matching MSP's existing behavior since #10273. Sensible parity fix; no project of ours.
- [#11885](https://github.com/iNavFlight/inav/pull/11885) — Rewrites the Parameter Group Version Check CI tool in Python to fix false aborts/misses. Plausible CI-tooling fix; no project of ours, worth a look given we care about CI reliability generally.
- [#11887](https://github.com/iNavFlight/inav/pull/11887) — Adds custom Tramp VTX power levels + AUX pit mode. Narrow hardware-support feature; no project of ours.
- [#11888](https://github.com/iNavFlight/inav/pull/11888) — New `MSP2_INAV_COPY_PROFILE` command to copy a control/battery/mixer profile slot. Firmware half of a configurator feature pair (#2746); no project of ours, but touches MSP surface we've been hardening elsewhere.
- [#11894](https://github.com/iNavFlight/inav/pull/11894) — Adds user-defined names for control/battery/mixer profiles. Firmware half of #2747/#2750; no project of ours.
- [#11895](https://github.com/iNavFlight/inav/pull/11895) — Adds `gps_ublox_assistnow_autonomous` for u-blox orbit prediction. Firmware half of #2748; no project of ours.
- [#11896](https://github.com/iNavFlight/inav/pull/11896) — Three new OSD elements for profile names. Firmware half of #2750; no project of ours.
- [#11899](https://github.com/iNavFlight/inav/pull/11899) — **Matches `active/audit-msp-telemetry-corruption-reliability`** (fixes #11777-#11780, all four issues that project tracks). Project summary updated.
- [#11900](https://github.com/iNavFlight/inav/pull/11900) — Rejects JUMP waypoints whose 1-based `p1==0` silently becomes an out-of-range `-1` index. Sounds like a real input-validation gap; no project of ours.
- [#11901](https://github.com/iNavFlight/inav/pull/11901) — Derives timer IRQ context index from the timer table instead of `i-1` arithmetic; fixes an H7/AT32 out-of-bounds array read reachable via PWM-in/PPM/softserial interrupts. Credible hard-fault-class bug fix; no project of ours (different from the completed `fix-furyf4osd-timer-channel-duplicate`, which was a target-config duplicate-pin issue, not this indexing bug).
- [#11902](https://github.com/iNavFlight/inav/pull/11902) — Logs amperage for all current-meter types and fixes SD-only-target blackbox default. Two small blackbox-default bugs bundled; no project of ours.
- [#11903](https://github.com/iNavFlight/inav/pull/11903) — **Matches `active/investigate-sdmmc-cache-coherency-defects`** (fixes both defects the project describes, same issue #11562). Project summary updated.
- [#11904](https://github.com/iNavFlight/inav/pull/11904) — **Matches `active/fix-pid-tpa-pitch-compensation-sign`**, but with a conflicting docs-not-code diagnosis. Project summary updated with the conflict flagged.
- [#11905](https://github.com/iNavFlight/inav/pull/11905) — Scales gyro-cal movement threshold with configured sensitivity so calibration doesn't hang on high full-scale-range gyros. Plausible, reported by a named user (and-sh); no project of ours.
- [#11906](https://github.com/iNavFlight/inav/pull/11906) — Detects DPS310 baro on both possible I2C addresses (0x76/0x77) instead of hardcoding one. Straightforward driver fix; no project of ours.
- [#11907](https://github.com/iNavFlight/inav/pull/11907) — Fixes a beeper config (`beeper -HW_FAILURE`) that silences arming/disarming/battery beeps entirely, not just the hardware-fault beep. Sounds like a real safety-adjacent UX bug; no project of ours.
- [#11908](https://github.com/iNavFlight/inav/pull/11908) — Fixes DSHOT motor-test slider not spinning motors below idle threshold (MULTISHOT unaffected). Related in area but not the same bug as our recently-completed `fix-3d-motor-testing`/`fix-3d-dshot-motor-testing-firmware` (those were reverse-direction bugs); no open project of ours.
- [#11909](https://github.com/iNavFlight/inav/pull/11909) — Two housekeeping fixes: `clean_<target>` cleaning every target, and dead Spektrum RPM code removal. Low-risk cleanup; no project of ours.
- [#11910](https://github.com/iNavFlight/inav/pull/11910) — `status` command now reports UNCALIBRATED sensors instead of silently saying OK. Good diagnosability fix; no project of ours.
- [#11911](https://github.com/iNavFlight/inav/pull/11911) — Requires `nav_fw_launch_accel` for throw-launch detection after a report of launch mode self-triggering from a noisy GPS speed reading. Safety-relevant; no project of ours but worth a skim given our own autoland/launch investigations.
- [#11912](https://github.com/iNavFlight/inav/pull/11912) — Refuses assigning SBUS output to a second serial port instead of silently accepting a config that only half-works. Reasonable input-validation fix; no project of ours.
- [#11913](https://github.com/iNavFlight/inav/pull/11913) — Reports battery as unknown over MAVLink when none is connected, instead of spamming critical battery warnings on USB power. Believable UX fix; no project of ours.
- [#11914](https://github.com/iNavFlight/inav/pull/11914) — Hides the RX downlink-power OSD element when the link (e.g. ELRS) doesn't actually report it, instead of showing a permanent "0 mW". Plausible; no project of ours.
- [#11915](https://github.com/iNavFlight/inav/pull/11915) — Makes W25N flash erase wait for chip completion and report what happened, fixing "old log survives power cycle" reports from two users. Sounds like a real reliability fix for that flash chip; no project of ours.
- [#11916](https://github.com/iNavFlight/inav/pull/11916) — Sends the full page address on 2Gbit W25N devices; deliberately split from #11915 since it changes the SPI byte sequence. Author is being appropriately cautious about scope; no project of ours.
- [#11917](https://github.com/iNavFlight/inav/pull/11917) — Fixes VTOL tilt-servo snap when switching mixer profiles mid-transition before servos reach target. Narrow VTOL bug; no project of ours (tangential to our backburnered VTOL-transition follow-ups but not the same issue).
- [#11918](https://github.com/iNavFlight/inav/pull/11918) — Fixes a one-degree hue shift making "RED" render pink in the LED fixed-colour layer specifically (GPS layer unaffected). Small, well-scoped color fix; no project of ours.
- [#11919](https://github.com/iNavFlight/inav/pull/11919) — Fixes MSP-over-telemetry reply-framing corruption when a reply is discarded mid-send (stale `headerSent` static). Same general domain as our `active/audit-msp-telemetry-corruption-reliability` project but a different issue (#10667, not one of #11776-#11780) — not added to that project's proposed-solution note, but worth a look if that project's scope ever widens.
- [#11920](https://github.com/iNavFlight/inav/pull/11920) — Two small OSD number-formatting fixes (decimal separator on stats screen, battery-percentage damping). Cosmetic; no project of ours.
- [#11921](https://github.com/iNavFlight/inav/pull/11921) — Fixes UBX-NAV-SIG GPS frame buffer sizing (more signals than satellites, buffer sized for the wrong count). Credible GPS-parsing bug; no project of ours.
- [#11922](https://github.com/iNavFlight/inav/pull/11922) — **Matches `active/fix-geozones-eeprom-save-91`**, but with a conflicting root-cause diagnosis (read-back bugs, not a save-handler race). Project summary updated with the conflict flagged.
- [#11923](https://github.com/iNavFlight/inav/pull/11923) — Gives config-save-from-sticks a distinct confirmation beep sequence instead of the generic one. Small UX polish; no project of ours.
- [#11924](https://github.com/iNavFlight/inav/pull/11924) — Adds a MAG debug mode exposing raw (pre-calibration, pre-alignment) magnetometer samples to blackbox, for external hard/soft-iron ellipsoid fitting. Useful tooling; not the same thing as our `active/investigate-ardupilot-orientation-technique` (that's runtime auto-orientation detection, not raw-sample logging) — no project of ours.
- [#11925](https://github.com/iNavFlight/inav/pull/11925) — Documents NEXUSX target's ports/outputs/I2C buses in response to a user question. Docs-only; no project of ours.
- [#11926](https://github.com/iNavFlight/inav/pull/11926) — Fixes OSD sidebar (altitude/speed) scale scrolling the wrong direction relative to the Garmin-style reference it emulates. Believable, cites a side-by-side video comparison; no project of ours.
- [#11927](https://github.com/iNavFlight/inav/pull/11927) — Fixes a genuine one-byte stack out-of-bounds write in `osdHudDrawPoi()`, hit on every radar-POI draw; found via docs writing, not build-tested by the author (no ARM toolchain). Real memory-safety bug, small fix, but needs a build+test pass before trusting since the author says so themselves; no project of ours.
- [#11928](https://github.com/iNavFlight/inav/pull/11928) — Fixes EZ-Tune's expo slider reading the rate value instead of the expo value, so the slider currently does nothing. Credible, found while writing docs; no project of ours.
- [#11930](https://github.com/iNavFlight/inav/pull/11930) — CI fix so the size-report/PR-test-build bots don't misfire off the placeholder "no code change" workflow run sharing a name with the real build workflow. Plausible CI-tooling fix, author backs it with reproduction runs on their own fork; no project of ours.

## iNavFlight/inav-configurator

- [#2710](https://github.com/iNavFlight/inav-configurator/pull/2710) — MERGED. Add 3D terrain review to Mission Control. Already resolved via `completed/resolve-pr2710-2725-conflicts-qodo-review` (2026-09-05) — no action needed, just confirms that completed project's provenance.
- [#2717](https://github.com/iNavFlight/inav-configurator/pull/2717) — Select waypoints from a list, switch mission altitude reference. Reasonable UX feature building on the same 3D mission-control work as #2710/#2725/#2742; no project of ours.
- [#2721](https://github.com/iNavFlight/inav-configurator/pull/2721) — MERGED. Trivial label-text fix (trailing dot); no project of ours.
- [#2725](https://github.com/iNavFlight/inav-configurator/pull/2725) — MERGED. Simulate the flight path a fixed wing will actually fly. Already resolved via `completed/resolve-pr2710-2725-conflicts-qodo-review` (2026-09-05) — no action needed.
- [#2742](https://github.com/iNavFlight/inav-configurator/pull/2742) — Draws/terrain-checks JUMP return legs in the 3D mission view, follow-up to #2710. Companion piece to firmware #11900 (JUMP waypoint validation), same author, same week — worth reading together if either lands; no project of ours.
- [#2743](https://github.com/iNavFlight/inav-configurator/pull/2743) — Shows a human-readable unit conversion next to settings entered in raw firmware units. Nice-to-have UX polish, broad surface area (many settings) so higher review risk than it looks; no project of ours.
- [#2744](https://github.com/iNavFlight/inav-configurator/pull/2744) — Adds live per-motor ESC telemetry (RPM/temp/voltage/current) to the Outputs tab, reading an MSP command that's existed for years but was never surfaced there. Plausible, decent-sized feature; no project of ours.
- [#2745](https://github.com/iNavFlight/inav-configurator/pull/2745) — Adds openAIP airspace/airport overlays to Mission Control. Useful planning feature, likely needs an API-key/licensing/rate-limit review since it's a third-party data source; no project of ours.
- [#2746](https://github.com/iNavFlight/inav-configurator/pull/2746) — Copy-profile dialog for the header dropdowns, configurator half of firmware #11888. Depends on that firmware PR merging first; no project of ours.
- [#2747](https://github.com/iNavFlight/inav-configurator/pull/2747) — Shows profile names in header dropdowns, configurator half of #11894. Same dependency situation as #2746; no project of ours.
- [#2748](https://github.com/iNavFlight/inav-configurator/pull/2748) — AssistNow Autonomous checkbox on GPS tab, configurator half of #11895. Small, low-risk (falls back to "unknown setting removed" on old firmware); no project of ours.
- [#2749](https://github.com/iNavFlight/inav-configurator/pull/2749) — Fixes a GPS-tab console error/parse failure when firmware answers `MSP2_ADSB_LIMITS` with no payload (no `USE_ADSB`). Related subsystem to our completed-adjacent `active/fix-adsb-stale-slot-values` (a different, firmware-side stale-data bug) but not the same defect — no project of ours, not added to that project.
- [#2750](https://github.com/iNavFlight/inav-configurator/pull/2750) — OSD tab entries for the profile-name elements, configurator half of #11896. Same dependency chain as #2746-2748; no project of ours.
- [#2751](https://github.com/iNavFlight/inav-configurator/pull/2751) — **Matches `active/fix-configurator-manual-mode-acro-indicator`**, same root cause we identified. Project summary updated.
- [#2752](https://github.com/iNavFlight/inav-configurator/pull/2752) — Fixes compass-calibration countdown reading results before the firmware has finished when `mag_calibration_time` is raised above 30s. Believable, well-diagnosed; no project of ours (different from `active/investigate-ardupilot-orientation-technique`, which is about auto-orientation detection, not calibration-timer UI).
- [#2753](https://github.com/iNavFlight/inav-configurator/pull/2753) — Fixes blackbox rate dropdown breaking on denominators above 255 (endianness bug). Credible, narrow fix; no project of ours.
- [#2755](https://github.com/iNavFlight/inav-configurator/pull/2755) — Forward-ports a known-good macOS arm64 CI fix (`#2706`, already merged to `maintenance-9.x`) onto `maintenance-10.x`. Low-risk, mechanical port with a stated integration order for 4 other PRs; loosely related to our completed `fix-configurator-ci-macos-arm64-oom` (different specific bug, same CI area) — no project of ours, not added.
- [#2756](https://github.com/iNavFlight/inav-configurator/pull/2756) — Stops a stray `$M<` MSP artifact from printing at the top of CLI tab output. Cosmetic but easy first-impression fix; no project of ours.
- [#2757](https://github.com/iNavFlight/inav-configurator/pull/2757) — Fixes a 2014-era global keydown filter that blocked Ctrl+A/C/V/X/Z/Home/End on every numeric input across many tabs (root cause was misdiagnosed for years as "OSD fields don't accept typing"). Good find if accurate — wide blast radius (OSD 32 fields, PID tuning 98, advanced tuning 82+); worth a careful review given how many tabs it touches. No project of ours, though it may be one of the 97 issues behind `active/configurator-ui-polish`.
- [#2758](https://github.com/iNavFlight/inav-configurator/pull/2758) — Fixes a missing import causing "MSPChainerClass is not defined" crash when saving logic conditions from the Mixer tab overlay. Reproduced by two named users; credible; no project of ours.
- [#2760](https://github.com/iNavFlight/inav-configurator/pull/2760) — Fixes stale approach-length display in Mission Control after editing it elsewhere and saving/rebooting. Believable stale-cache UI bug; no project of ours.
- [#2761](https://github.com/iNavFlight/inav-configurator/pull/2761) — Warns when `pid_type` points at the unused nav PID bank (e.g. multirotor with `pid_type=PIFF` showing fixed-wing gains that do nothing). Good catch, prevents silent no-op tuning; no project of ours.
- [#2762](https://github.com/iNavFlight/inav-configurator/pull/2762) — Fixes mission files losing landing information on save between firmware versions 7.1 and 8.0. Credible regression fix; no project of ours.
- [#2763](https://github.com/iNavFlight/inav-configurator/pull/2763) — Fixes Mission Control ignoring the imperial/metric unit setting entirely. Confirmed by a named reviewer (breadoven) in the thread per the PR text; no project of ours.
- [#2764](https://github.com/iNavFlight/inav-configurator/pull/2764) — Robustness fixes for the Alignment Tool's load chain (unhandled rejection on unknown setting) plus evidence the originally-reported crash (#2380) is already fixed elsewhere. Careful, well-evidenced PR (SITL-replayed the MSP sequence against two firmware versions); loosely related to our `active/alignment-wizard-documentation` (docs, not code) and backburnered `feature-auto-alignment-tool` (#2158, a different wizard) — no project of ours, not added.
- [#2765](https://github.com/iNavFlight/inav-configurator/pull/2765) — Strengthens the "Select New Defaults" warning dialog after a user lost a custom motor mixer without realizing the scope of what gets overwritten. Sensible safety-copy fix; no project of ours.
- [#2766](https://github.com/iNavFlight/inav-configurator/pull/2766) — Fixes stale sensor-status header row surviving disconnect (dead code referencing a global that was removed in a module refactor). Same general "disconnect/reconnect" area as our completed `fix-configurator-disconnect-reconnect-hang` (2026-08-25) but a distinct bug (stale UI row, not a hang) — no open project of ours, not added.
- [#2767](https://github.com/iNavFlight/inav-configurator/pull/2767) — Fixes the ports-tab baud-rate dropdown losing/mangling a baud rate not in its preset list. Two-sided root cause per the author; no project of ours.

## Projects updated with a "Proposed Solution (Untested)" note

1. `active/audit-msp-telemetry-corruption-reliability` ← [#11899](https://github.com/iNavFlight/inav/pull/11899)
2. `active/investigate-sdmmc-cache-coherency-defects` ← [#11903](https://github.com/iNavFlight/inav/pull/11903)
3. `active/fix-pid-tpa-pitch-compensation-sign` ← [#11904](https://github.com/iNavFlight/inav/pull/11904) (conflicting theory)
4. `active/fix-geozones-eeprom-save-91` ← [#11922](https://github.com/iNavFlight/inav/pull/11922) (conflicting theory)
5. `active/fix-configurator-manual-mode-acro-indicator` ← [#2751](https://github.com/iNavFlight/inav-configurator/pull/2751)
6. `active/investigate-virtual-pitot-default` ← [#2754](https://github.com/iNavFlight/inav-configurator/pull/2754)
7. `active/fix-configurator-osd-orphaned-elements` ← [#2759](https://github.com/iNavFlight/inav-configurator/pull/2759)

None of these have been tested by us. Two (`fix-pid-tpa-pitch-compensation-sign`,
`fix-geozones-eeprom-save-91`) present a root-cause theory that conflicts with our own — resolve
that disagreement before writing any code, don't just take the newer analysis on faith.

## Overlap with third-party PRs (not us, not Raffi) from the last 30 days

Second pass: cross-checked Raffi's 69 PRs against every PR by an author other than Raffi1202 and
`sensei-hacker` (our own account — those PRs are what the project cross-reference above already
covers) that was **opened or merged since 2026-08-14** on either repo (132 + 58 opened, 79 + 31
merged, deduped — 162 distinct third-party PRs). Looking for pairs that touch the same bug/feature
rather than just the same file. Four pairs/groups worth comparing before merging anything in them;
nothing else in the 162 showed real overlap with Raffi's set.

### 1. LED strip hue bug vs. the rainbow overlay feature — HIGH confidence, ties to an existing project

- [Raffi #11918](https://github.com/iNavFlight/inav/pull/11918) — fixes a one-degree hue-offset bug
  in `applyLedFixedLayers()` (`ledstrip.c`) that affects every fixed-colour-driven LED layer
  (colour, flight mode, orientation, arm state, battery, RSSI).
- [HereComesWhitey #11820](https://github.com/iNavFlight/inav/pull/11820) (+ configurator companion
  [#2718](https://github.com/iNavFlight/inav-configurator/pull/2718)) — adds a rainbow/HSV-sweep LED
  overlay, same files (`ledstrip.c`/`colorconversion.c`).

Raffi already has a **separate** fix-up branch specifically for #11820
(`Raffi1202/inav:fix/led-rainbow-followups`, posted as a PR comment, not its own PR) covering
`COLOR_WHITE` and a CLI buffer overflow — and that branch's own changelog says "the rainbow layer
now builds its `hsvColor_t` directly instead of reading the LED colour first," meaning the rainbow
overlay's hue path and the fixed-layer hue-offset bug in #11918 are adjacent, possibly interacting,
code. This is exactly the pair our existing project `active/pr-review-11931-11484-11820` is already
tracking — that project's #11820 sub-task should pull in #11918 too, not just the followups branch,
before #2718 is unblocked to merge.

### 2. Gyro calibration state handling — MEDIUM confidence

- [Raffi #11905](https://github.com/iNavFlight/inav/pull/11905) — scales the gyro-cal movement
  threshold with configured sensitivity so calibration doesn't hang on high-full-scale-range gyros.
- [MrScothh #11932](https://github.com/iNavFlight/inav/pull/11932) — fixes `gyroUpdateAndCalibrate()`
  writing to `gyroCalibration[0]` directly instead of the passed-in `zeroCalibrationVector_t*`
  (latent today, matters once a second call site exists — author says they hit it while adding one).

Different specific bugs, same function/calibration-state area. Not a solution duplicate, but worth
reading together: if MrScothh's "a second call site" work lands, Raffi's threshold-scaling change
should be re-checked against whichever call site it touches.

### 3. VTOL mixer-profile-switch behavior — MEDIUM confidence

- [Raffi #11917](https://github.com/iNavFlight/inav/pull/11917) — fixes servo-speed carryover being
  dropped when switching a mixer profile back (`mixer.c`, `servoMixerSwitchHelper[]`), building on
  the existing #10986 carryover mechanism.
- [mart1npetroff #11871](https://github.com/iNavFlight/inav/pull/11871) (open) — improves VTOL RTH
  approach timing and post-transition capture, building on their own #11553 (merged) auto-transition
  state machine.

Different bugs (servo output continuity vs. RTH approach geometry), but both modify behavior around
a VTOL mixer-profile switch and both build on recent work by the same subsystem's primary author
(mart1npetroff owns #11553). Worth flying/testing together rather than assuming independence.

### 4. Mission Control map overlays — LOW-MEDIUM confidence, three-way

- [Raffi #2745](https://github.com/iNavFlight/inav-configurator/pull/2745) — openAIP airspace/airport
  overlays.
- [GenCodeInc #2727](https://github.com/iNavFlight/inav-configurator/pull/2727) (merged) — Google
  Location Services & Weather Conditions.
- [error414 #2569](https://github.com/iNavFlight/inav-configurator/pull/2569) (merged) — ADSB areas
  on the GPS map.

Three different contributors added map-layer-type features to Mission Control's map in the same
window. Not solving the same problem, but if there's a shared "Map Layers" overlay-registration
pattern (the PR #2745 description mentions a "Map Layers" box, same term #2727 uses), it's worth
checking Raffi's PR was built against the latest layer-registration shape rather than duplicating
plumbing GenCodeInc's or error414's PR already added.

None of these four have been tested against each other. Flagging for comparison, not concluding
either side is right.
