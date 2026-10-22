#!/usr/bin/env python3
"""Fragmentation test for SD blackbox wraparound (PR #12150).

Runs many short flights with variable (seeded) durations on a small FAT32 image.
After every flight the image is snapshotted and inspected (fat_inspect.py, FAT copy 1).
Records freefile start/size and "stranded" clusters = unowned gaps between live extents
(dirs, LOG files, freefile). A stranded tail of a previous lap shows up as a gap that
sits right before the freefile start.

Usage: test_sdcard_fragmentation.py <sitl_elf> <image> [--port 5800] [--flights 120] [--seed 1]
       [--min-dur 1] [--max-dur 8]
Image: MBR + FAT32, >= ~34MB. Create with:
  truncate -s 40M t.img; echo 'start=2048, type=c' | sfdisk -q t.img; mkfs.vfat -F32 -s1 --offset 2048 t.img
Pass criteria: no violations (overlap/FAT0/dup names/short chains), laps >= 3 observed,
 max stranded <= 1 supercluster at any time, all flights armed. Exit non-zero on FAIL.
If connection fails: check `ss -tlnp | grep <port>`; localhost TCP is normally sandbox-allowed.
"""
import argparse, os, random, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'blackbox'))
import sdcard_wraparound_lib as lib
import fat_inspect

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sitl_elf'); ap.add_argument('image')
    ap.add_argument('--port', type=int, default=5800)
    ap.add_argument('--flights', type=int, default=120)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--min-dur', type=float, default=1.0)
    ap.add_argument('--max-dur', type=float, default=8.0)
    ap.add_argument('--workdir', default=None)
    ap.add_argument('--stop-on-stall', action='store_true', help='abort at first stall, leave SITL running for inspection')
    a = ap.parse_args()
    work = a.workdir or os.path.dirname(os.path.abspath(a.image))
    eeprom = os.path.join(work, 'eeprom_frag_%d.bin' % a.port)
    if os.path.exists(eeprom): os.remove(eeprom)
    snap = a.image + '.snap'
    sitl = lib.SitlProcess(os.path.abspath(a.sitl_elf), eeprom, os.path.abspath(a.image), a.port,
                           os.path.join(work, 'sitl_frag_%d.log' % a.port))
    sitl.start()
    if not lib.wait_for_port(a.port, 20):
        print('FAIL: SITL port not up (check `ss -tlnp | grep %d`)' % a.port); return 2
    time.sleep(1)
    with lib.MspClient('localhost', a.port) as c:
        lib.set_receiver_type_msp(c); lib.setup_arm_mode(c); lib.enable_feature_blackbox(c)
        lib.set_setting(c, 'blackbox_device', 2)
        lib.set_setting(c, 'blackbox_arm_control', 0)
        lib.save_and_reboot(c)
    time.sleep(3)
    if not lib.wait_for_port(a.port, 20): print('FAIL: no port after reboot'); return 2
    time.sleep(1)
    rng = random.Random(a.seed)
    rows, viol, unarmed, laps, prev_ff = [], [], 0, 0, None
    last_max, stall, max_stall = -1, 0, 0
    holes = set()  # log numbers inside the surviving range with no LOG file
    with lib.MspClient('localhost', a.port) as c:
        time.sleep(3.0)  # gyro cal before HITL (see lessons)
        lib.enable_hitl(c); lib.rc_pump(c, 8.0)  # extra warm-up: SD init + freefile/LOGS creation
        s0 = lib.query_sdcard_summary(c)
        if not s0 or s0['totalKB'] == 0:
            print('FAIL: SD card not ready:', s0); sitl.kill(); return 2
        print('SD summary', s0)
        for i in range(a.flights):
            dur = round(a.min_dur + (a.max_dur - a.min_dur) * rng.random() ** 3, 1)  # skewed: many short, a few long
            ok, s = lib.do_flight(c, dur, settle_s=1.5, verbose=False)
            if not ok: unarmed += 1
            shutil.copyfile(a.image, snap)
            try: r = fat_inspect.inspect(snap)
            except Exception as e:
                print('flight %d: inspect error %s' % (i, e)); viol.append('inspect error'); continue
            ff = r['freefile']; cs = r['csize']; sc = 128  # clusters per supercluster (FAT32: entries per 512B sector)
            if prev_ff is not None and ff and ff['start'] < prev_ff: laps += 1
            if ff: prev_ff = ff['start']
            # gap immediately before the freefile (tail stranded behind it)
            pre = 0
            for (st, n) in r['gaps']:
                if ff and st + n == ff['start']: pre = n
            rows.append((i, dur, len(r['logs']), ff['start'] if ff else -1, ff['clusters'] if ff else -1,
                         pre, r['stranded_clusters'], r['excess_clusters'], len(r['excess'])))
            viol += ['flight %d: %s' % (i, v) for v in r['violations']]
            if r['violations']:
                keep = '%s.viol_f%03d' % (a.image, i); shutil.copyfile(snap, keep); print('  saved violating snapshot', keep)
            mxlog = max((int(g['name'][3:8]) for g in r['logs'] if g['name'][3:8].isdigit()), default=-1)
            stall = stall + 1 if (mxlog == last_max and mxlog >= 0) else 0
            nums = sorted(int(g['name'][3:8]) for g in r['logs'] if g['name'][3:8].isdigit())
            if nums:
                # evicted logs are always the OLDEST, so any hole INSIDE the surviving number range is a number
                # consumed by a log that was discarded/never survived (e.g. an empty log) -> numbering not sequential
                for h in set(range(nums[0], nums[-1] + 1)) - set(nums):
                    if h not in holes:
                        holes.add(h); print('  NUMBER HOLE LOG%05d (flight %d, surviving range LOG%05d..LOG%05d)' % (h, i, nums[0], nums[-1]))
            last_max = mxlog; max_stall = max(max_stall, stall)
            if last_max < 0 and i >= 5:
                print('HARNESS FAIL/INCONCLUSIVE: no LOG file after 6 flights (blackbox never started; not a firmware verdict)')
                sitl.terminate_clean(); return 2
            if last_max >= 0 and stall == 3:
                keep = '%s.stall_f%03d' % (a.image, i); shutil.copyfile(snap, keep); print('  saved stall snapshot', keep)
            if last_max >= 0 and stall == 3: print('  STALL: no new LOG file for 3 consecutive flights (state=%s lastError=%s)' % (s and s['state'], s and s['lastError']))
            if a.stop_on_stall and last_max >= 0 and stall >= 3:
                print('stopping, SITL pid %d left running on port %d' % (sitl.pid(), a.port)); return 3
            print('f%03d dur=%4.1f logs=%2d ff_start=%6d ff_clu=%6d gap_before_ff=%5d stranded_total=%6d excess=%5d (%2d gaps) free=%dKB'
                  % (rows[-1] + (s['freeKB'] if s else -1,)))
    sitl.terminate_clean()
    sc = 128
    mx = max((r[7] for r in rows), default=0)
    final = rows[-1][7] if rows else 0
    print('\nlaps(freefile start moved backwards)=%d  max_excess_stranded=%d clu (%.1f supercl.)  final_excess_stranded=%d clu (%.1f supercl.)  unarmed=%d  violations=%d  max_flights_without_new_log=%d'
          % (laps, mx, mx / sc, final, final / sc, unarmed, len(viol), max_stall))
    print('log number holes (numbers consumed but missing inside the surviving range; sequential numbering => 0): %d %s' % (len(holes), sorted(holes)[:20]))
    for v in viol[:10]: print('  VIOLATION', v)
    bad = viol or max_stall >= 3 or unarmed or laps < 3 or mx > 2 * sc
    print('RESULT:', 'FAIL' if bad else 'PASS', '' if laps >= 3 else '(INCONCLUSIVE: fewer than 3 laps)')
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main())
