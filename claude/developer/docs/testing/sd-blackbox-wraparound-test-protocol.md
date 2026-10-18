# Test protocol: PR #12150 SD blackbox ring wraparound (+ planned fragmentation fix)

Status: protocol only, nothing run, no scripts written. Drives the open concerns in review.md.
Subject: eviction of the oldest LOG*.TXT, freefile relocation, mid-flight split.
Fix under test (F): when the freefile leftover tail < 1 supercluster, extend the freefile from its current start over the evicted log if that log directly follows the freefile end; otherwise use the existing relocation; wrap case uses existing relocation.

## 0. Existing tooling to reuse (do not rewrite)
- `blackbox/sdcard_wraparound_lib.py`: SITL launch on `--sdcard` image + tcpbaseport, raw MSP client, `MSP_SDCARD_SUMMARY`, `do_flight()`, `mtools_*`, `run_fsck()`, `copy_image()`, `SitlProcess.kill(SIGKILL)`.
- `blackbox/test_sdcard_wraparound_phase1_basic.py`, `..._forensic_singlewrap.py`: starting templates. Reuse their SITL start pattern (wait >2 s after reboot before HITL; one SITL PID; check `ss -tlnp`).
- Known trap: `fsck.vfat`/mtools check FAT copy #2, which afatfs never writes. All FAT checks here must use our own raw walker on copy #1 (section 2), fsck is only a secondary, advisory signal.
- Known trap: a FAT32 image needs >= ~35 MB (65525 clusters at 512 B/cluster); smaller images are rejected by afatfs.
- New files go under `claude/developer/scripts/testing/inav/blackbox/` (SD-card blackbox already lives there) with SITL-only drivers symlink-free; the task brief suggested `sitl/` and `hardware/`, so: shared lib + SITL drivers in `sitl/sdcard/`, rig scripts in `hardware/sdcard/`. (Decide once; do not split the lib.)

## 1. Shared building blocks to write (all full automation, host only)
| Script | Purpose |
|---|---|
| `sitl/sdcard/fat_inspect.py` | Pure-python FAT32 reader of an image (partition offset from MBR). Reads BPB, FAT copy #1 only, root + `LOGS` directory entries incl. deleted (0xE5) entries and the `FREESPAC.E` freefile. Outputs JSON: cluster size, LOG list (name, start cluster, size, chain), freefile (start, size, chain), free clusters, leaked clusters (allocated in FAT, owned by nobody). Also exposes `check()` returning a list of violations (section 2). |
| `sitl/sdcard/make_card_image.py` | Build a fresh FAT32 image with params: size MB, cluster size (512 B..32 KB), partition offset, pre-fill N logs of given sizes. Uses mkfs.vfat; then lets INAV create freefile itself on first SITL boot. Also can build a *crafted* layout (see 3.x) by writing LOG files via mtools then letting SITL carve the freefile. |
| `sitl/sdcard/sdcard_sitl_flights.py` | Library on top of `sdcard_wraparound_lib`: `run_flights(image, n, duration_fn)`, returns per-flight snapshot via `fat_inspect` after each clean shutdown (stop SITL SIGTERM, copy image, inspect). Variable duration generators (fixed, random, short/long mix). |
| `sitl/sdcard/run_matrix.py` | Runs the matrix in section 3 and prints a pass/fail table, non-zero exit on failure. |
| `sitl/sdcard/baseline_vs_fix.sh` | Runs the same matrix against two prebuilt SITL.elf paths (PR head vs PR head + fix F) and prints stranded-bytes deltas. Builds are done by inav-builder; this script only takes `--sitl-a --sitl-b`. |

Note: never ship a frozen copy of the pre-fix logic as test machinery; the A/B is two real binaries compared once at authoring time.

## 2. FAT consistency checker (runs after EVERY SITL run / lap / crash)  -- full automation
Implemented as `fat_inspect.check()`. Violations (any = FAIL):
1. FAT[0] and FAT[1] reserved entries intact (media byte 0xFFFFFFF8 / EOC flags), never overwritten (guards the cluster-0 erase bug).
2. Every file in LOGS and the freefile: chain from start cluster terminates in EOC, no loop, chain length*cluster_size >= size and < size + cluster_size, except freefile and evicted-log leftovers (see 4).
3. No cluster appears in two chains (cross-link); no live file chain intersects the freefile span (address range or chain).
4. FAT chain of the freefile may legitimately be stale over an evicted log (review.md section 1). Check instead: (freefile start..start+size) is wholly covered by clusters that are either free (FAT=0), freefile-owned, or belong to no live file. Record "stale chain" as info, not failure.
5. Root dir and LOGS dir parse; no entry with start cluster 0 and size > 0; no entry with start >= total clusters; names are unique (no duplicate LOGnnnnn).
6. Leaked clusters (allocated, unowned) total, reported as bytes: the accounting metric in section 3.
7. Advisory: `fsck.vfat -n` output saved; flag only errors not explained by the FAT-copy-2 mismatch. Never the sole verdict.
8. Boot test: start SITL on the image, wait for MSP, `MSP_SDCARD_SUMMARY` reports state READY (not FATAL/FS error) and free space >= 0.

## 3. Fragmentation / space accounting  -- full automation (SITL)
Purpose: show stranded bytes per lap are bounded and total contiguous reclaim is not lost; compare PR head vs fix F.
Metrics per lap (from `fat_inspect`): `freefile_size`, `leaked_bytes`, `sum(log sizes)`, `free_clusters`, `stranded = card_data_bytes - freefile - sum(logs) - dirs`. After the first full lap (steady state) `stranded` must be non-decreasing only up to bounded cumulative value, tested below.

Matrix (each run N laps = >= 12 wraps, ~300 flights as the author did, durations random 1-60 s unless stated):
| Case | Layout / how forced | Pass |
|---|---|---|
| A. leftover < supercluster, evicted log adjacent | Fill so freefile tail < 1 supercluster (supercluster = 4096 clusters*? read from `fat_inspect`, do not hardcode; use `sdcard summary` + image geometry), evicted log immediately after freefile end | With F: freefile start unchanged, new size = old + evicted span; stranded added this lap <= 1 cluster. PR head: record stranded (expected > 0, the bug); the test passes F only. |
| B. leftover >= supercluster, adjacent | tail >= 1 SC | Both versions: no stranding beyond rounding to 1 SC; freefile never shrinks below one SC; reclaim = log span. |
| C. evicted log NOT adjacent (small log between, or deleted-gap) | Craft with `make_card_image.py` (log A, gap-log B, evicted C) | F falls back to relocation; no overlap; stranded <= tail leftover; fsck-check clean. |
| D. wrap case (no log after freefile, evict lowest-address log) | freefile at end of data area | existing relocation path; freefile after = evicted span; chain valid; next lap normal. |
| E. variable lengths | random lengths incl. 1 s and 300 s logs | stranded per lap <= 1 SC (+ 1 cluster/log slack) over 300 flights; cumulative stranded does NOT grow monotonically per lap (bounded sawtooth, max <= 2 SC). |
| F. short flights only | 100 flights of 2 s each | each lap evicts exactly as many logs as needed; no hang; log count stable; no zero-size-log accumulation. |
| G. geometry sweep | cluster 512 B / 4 KB / 32 KB; card 35 MB, 128 MB, 1 GB (sparse image) , 2 GB sparse | all of A-F pass for each (use A, D, E at minimum on all; sparse images keep disk use small). |
Thresholds are proposals: tighten after first baseline run. Scripts: `run_matrix.py` + `fat_inspect.py`. Also compute `reclaimed_contiguous` = largest free contiguous run after each eviction; PASS if >= evicted log span (F) vs record for head.

Authoring-time red/green: run matrix A on PR-head SITL (expect fail on stranded bound), then F SITL (expect pass). Keep results in the workspace only.

## 4. Gap-case regressions (SITL, full automation)
Each: one script `sitl/sdcard/test_regress_<name>.py`, uses `fat_inspect.check()` after.
| # | Check | Steps | Pass |
|---|---|---|---|
| R1 | Log number skip (error414) | Fill, wrap, flight 1 s with empty/discarded log in the middle (arm/disarm < 1 s) | Log numbers of surviving logs contiguous ascending, no gap > 1 caused by discarded empty log. (PR head: expected FAIL = known finding; file as info if author declines patch.) |
| R2 | fopen failure hang | Force handles busy: run with MSC/open dir handles via `MSP_SDCARD_*` or an extra open (e.g. repeatedly requesting `MSP_DATAFLASH_*`/dir listing while the split state machine runs). If SITL cannot make a handle busy, mark manual/inspect | Blackbox returns to logging within 5 s of handle release; state never stuck WAITING forever. Report PASS only if the stuck scenario was actually induced (check via `fat_inspect`: no new LOG created while handles busy). |
| R3 | PAUSED across split | Arm with a mode mapped to blackbox pause (BOXBLACKBOX/PAUSE), pause during the split window, resume | Log continues; no duplicate LOG file; no state hang; file count +1 only. |
| R4 | Short flights | see case F | pass per F. |
| R5 | Cluster-0 entries | Image containing a LOG entry with start cluster 0 / size 0 (craft via mtools), card full | Entry never selected as eviction candidate; FAT[0]/[1] intact; no hang. |
| R6 | Concurrent createFile | Trigger split while an `MSP` command that creates/walks the root dir is repeated (e.g. repeated sdcard summary / OSD? use CLI `dump`), or in-unit via the SITL stress | No dir-entry corruption; no duplicate names; checker clean. Semi: depends on being able to cause a second createFile; if not, mark "code review only" explicitly. |
| R7 | Disk full, nothing reclaimable | Image with freefile tiny and only live non-LOG files / LOGS with only cluster-0 entries | Blackbox gives up (gaveUp), no hang, no crash, no endless retry in `MSP_SDCARD_SUMMARY`; flight continues without logging; image unmodified except as designed. Negative: normal card with logs still wraps. |
| R8 | Negative control | Card with free space, no wrap needed | No log deleted, no relocation; file count +1. |

## 5. Power-cut safety
### 5a. SITL crash injection  -- semi automation (needs a debug hook; fully automatable once one exists)
Purpose: crash consistency at each phase: SCAN, before DELETE, DELETE written but not flushed, DELETE flushed/pre-RELOCATE, RELOCATE freefile-entry written, post-RELOCATE, create-log, first header write.
Mechanism options, in order:
1. **Preferred (needs small test-only firmware hook, requested from developer):** env var / CLI setting `blackbox_crash_phase=N` in SITL only (compiled under `SITL_BUILD`) that `kill(getpid(), SIGKILL)` when the state machine reaches phase N. Deterministic. Developer must provide; test engineer must not edit src/.
2. **No firmware change:** a host watcher polls the image every 5 ms (mtime/mmap diff of directory-sector and FAT-sector bytes) and `kill -9` the SITL PID the moment a specific on-disk transition appears (e.g. LOGS entry byte0 becomes 0xE5 = delete reached disk; freefile start-cluster field changes = relocate reached disk). SITL writes to the image through a file so the host sees writes in order. Phases reached only via on-disk transition: after-delete, after-relocate-dirent, after-new-log-entry. SCAN and pre-delete are covered by timed kills. Script: `sitl/sdcard/crash_watch_kill.py`.
3. Torn-write variant: copy image before the kill, then on the copy zero or revert the last N sectors written (parse write order from the watcher log) to emulate a card that lost the most recent sector(s). Script: `sitl/sdcard/torn_write_replay.py`. This is the one that tests FAT/dirent ordering (delete before freefile) and is the strongest SITL power-cut evidence.
Per crash point, per variant (head, F): `fat_inspect.check()` on the crashed image with violations 1-3, 5 mandatory; leak bytes recorded (must be <= one log span, per review.md); then boot SITL on it, run 3 flights, expect all next laps normal and `check()` clean and leak bounded (does not accumulate across 5 repeated crashes in a row = loop 5 times at the same phase).
Pass: zero cross-links/overlap at any crash point (overlap freefile vs live file = FAIL, severity blocker); leaks bounded; SITL boots and logs afterwards. Run >= 200 randomised kill points (seed logged) plus each named phase x 10.

### 5b. Attached FC, real SD card  -- MANUAL/semi (human moves power)
Purpose: real card write ordering, internal card caching (cards can reorder writes), SPI/SDIO timing.
Rig needs:
- FC with SD slot (SPI or SDIO), USB data cable (`/dev/ttyACM*` via sandbox allowlist; ask user if blocked), bench supply or battery + a **relay/MOSFET power switch** controlled by an Arduino/ESP32/Pi GPIO (or a USB-controllable power strip) cutting FC VCC *and* SD, not USB-only (USB alone doesn't cut the SD if FC is battery-powered). Fully manual alternative: pull the battery connector at a verbal cue.
- Spare cards (2): known-good, brand/class recorded (cards differ drastically); card reader on the host for read-back; 4+ GB; also test a slow class-4 card.
- Props off, no motors.
Marker mechanism: make the firmware's state transitions visible externally. Options: (a) `debug_mode=BLACKBOX`? (if developer adds `DEBUG_SET` slots with the sdcard state and eviction phase, read via `MSP2_INAV_DEBUG` at >=100 Hz); (b) toggle a spare GPIO/LED per phase (needs firmware); (c) no firmware change: poll `MSP_SDCARD_SUMMARY` fs state + `MSP2_INAV_STATUS` and have the script pulse the relay N ms after it sees blackbox size reset / log count change. Phase timing then is statistical: sweep the delay 0..800 ms in 20 ms steps relative to the trigger, repeat until each delay bin had >= 3 trials.
Procedure per trial (script `hardware/sdcard/power_cut_trial.py` drives all but the card swap):
1. [auto] Pre-check: card inserted, MSP OK, SD state READY, FS consistent (read back via 4).
2. [auto] Fill card to just before a wrap using `hardware/sdcard/fill_card_to_wrap.py` (HITL arm/disarm loops over MSP like SITL: MSP_SIMULATOR works on real FC; wait >2 s after boot before HITL).
3. [auto] Arm via HITL, wait trigger (log size nearing full / eviction), relay cut at scripted delay.
4. [human] Wait 2 s, restore power, optionally swap to reader. Only needed if reading back requires the reader.
5. [auto/semi] Read-back: either (a) remove card, insert in host reader, `dd` full image to `$TMPDIR`, run `fat_inspect.py`, `fsck.vfat -n` (b) or, no card removal: put FC in MSC mode (`msc` CLI command, if target supports) and read `/dev/sdX` read-only; `msc` is much faster, use it.
6. [auto] Reconnect FC, check boot, SD READY, fly 3 HITL loops, re-run read-back, check log numbering advanced.
Pass: same as 5a; plus FC boots without needing a card reformat on 50/50 trials at >= 3 cards-trials per delay bin; any case needing the user to reformat = FAIL. Record card model and per-trial image hash set.
Count: >= 100 trials total (~2 min each = 3-4 h with human present; relay rig makes it unattended except step 4 if MSC is used).

## 6. In-flight gap measurement during a split  -- semi automation (real card), partial SITL
Purpose: measure the data gap while the state machine scans/deletes/relocates.
Setup: real card (try 3 cards incl. a slow one) with 200+ LOG files filled using small logs, one case with 4 GB and one with 32 GB cards, then arm to trigger a split mid-"flight" with LOGS directory scan needed.
Instrumentation (choose first available):
1. **Log content (no firmware change, best):** log at 500 Hz or max rate with `looptime`-derived frame times. After the run, parse the new LOG file with `blackbox_decode`/`analysis/decode_blackbox_frames.py`, compute max delta of `time(us)` between consecutive main frames at the split (the gap is the interval between last frame in old file and first in new; the split starts a new file so the gap is reconstructed from the *last frame of the previous log* and the *first frame of the new one* — both are retrievable since both files stay on the card, unless the previous was the evicted one; the previous log is the current one so it always survives). Script: `blackbox/analysis/blackbox_split_gap.py`.
2. Firmware counter: `debug_mode=BLACKBOX` slot with a dropped-frame counter and state-machine dwell times (needs developer help).
3. External: logic analyzer on SD CLK/CS lines (manual) to see the physical write pause.
Also measure `idle→split` using the arm→first-frame latency from `MSP_SDCARD_SUMMARY` polling timeline.
Metrics and proposed thresholds:
- `gap_max_ms` across the split: PASS < 250 ms (at 1 kHz: <= 250 lost frames), WARN 250-1000 ms, FAIL > 1 s. Compare with a baseline flight without a split (control) to separate the normal ~ms jitter.
- Looptime / `cycle_time_max`/`task` stats during the split: no scheduler stall > 2 ms on main loop (blackbox runs in a task; check `MSP_...` task stats or `status` CLI max cycle).
- Frame loss total at split: < 0.5 s worth.
- Repeated 10 times per card; report max/median. Gap should not scale with LOG count: plot gap vs number of LOG files (10, 50, 200); FAIL if growing steeply (> linear 1 ms per 10 files is the proposed alarm).
- Armed-state safety: confirm flight controller loop unaffected (gyro task period unchanged) and no OSD/failsafe artifacts. For fixed-wing-style tests keep props off.

## 7. Attached-FC rig checklist (items for `hardware/sdcard/README.md`)
- Port: `/dev/ttyACM*` USB (MSP); SITL-style `MSP_SIMULATOR` HITL arm works on real FC if the target doesn't `#undef USE_SIMULATOR`; check `target.h` first.
- SD prep: format FAT32 with the INAV CLI/Configurator `Format` or `mkfs.vfat -F 32 -s <spc>` on the card in a reader, 4+ GB card, **no leftover logs** unless a case demands; label card. Record cluster size (`fat_inspect.py`). Record the card CID via `/sys/block/mmcblk*/device/cid` when on an SD reader.
- Read back: preferably `msc` (CLI; FC reboots into MSC) + `dd if=/dev/sdX of=$TMPDIR/img bs=1M status=progress` then `fat_inspect.py`; else physical reader with a write-blocker or `mount -o ro`. NEVER let the host mount rw (it would repair/modify the FAT).
- Power rig for 5b: relay on battery/5 V FC input, GPIO driven from host via serial (Arduino) or `uhubctl`/smart plug; timing control to ~10 ms.
- Timing aids: `MSP_SDCARD_SUMMARY` polling at 20 Hz; blackbox debug fields if provided.
- Safety: props off, no ESCs powered or ESC power disconnected, battery fused.
- Wait 2 s after power-on before HITL (gyro calibration), stream RC at 50 Hz.
- After each trial, exit CLI mode (CLI/MSC blocks MSP).

## 8. Scripts to write (summary, none exist yet)
`sitl/sdcard/`: `fat_inspect.py`, `make_card_image.py`, `sdcard_sitl_flights.py`, `run_matrix.py`, `baseline_vs_fix.sh`, `crash_watch_kill.py`, `torn_write_replay.py`, `test_regress_{numbering,fopen_busy,paused_split,cluster0,concurrent_create,full_unreclaimable,control}.py`.
`hardware/sdcard/`: `README.md` (rig), `fill_card_to_wrap.py`, `power_cut_trial.py`, `read_back_card.sh` (MSC + dd + inspect), `measure_split_gap.py` (wraps `blackbox/analysis/blackbox_split_gap.py`).
Developer help requested (test engineer cannot edit src/): (1) SITL-only `blackbox_crash_phase` hook, (2) debug slots for blackbox sd state/dropped frames, (3) the fix F build + PR-head build as two SITL.elf paths.

## 9. Run order and exit criteria
1. fat_inspect + make_card_image + a sanity run on PR head (verify the checker flags a deliberately corrupted image: negative control for the checker).
2. Matrix section 3 on head, then fix F; commit numbers.
3. Regressions section 4.
4. SITL crash points 5a.
5. Real-card 5b and 6 (human-assisted); only these two give merge confidence for the unknowns listed in review.md section 4.
Release criterion: no overlap/cross-link at any crash point; stranded bounded <= 2 SC; gap_max < 250 ms (or documented); regressions pass or findings reported.
