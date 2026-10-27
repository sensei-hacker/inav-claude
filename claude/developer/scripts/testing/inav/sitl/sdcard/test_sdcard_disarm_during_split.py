#!/usr/bin/env python3
"""Disarm while an SD blackbox log is being split (PR #12150 review finding 1).

blackboxSplitting is set when a log is closed for a split and cleared only on entering RUNNING. If the pilot disarms
before RUNNING returns, processBlackbox() calls blackboxFinish() every loop; after SHUTTING_DOWN the still-set flag sends
the state machine back to PREPARE_LOG_FILE, so it keeps opening and discarding logs and never reaches STOPPED.

Crafted card: oldest log exactly 1 supercluster (512 KB) at the freefile, so each flight reclaims it and splits after
~512 KB. Probe mode (--disarm-at -1) prints the SD timeline so the split instant is known; sweep mode disarms at each
time in --sweep (seconds after arm). After the disarm, the newest LOG number is read from the image 2 s and 6 s later;
growth between the two reads = stuck loop. Also checks that a re-arm afterwards still creates a log.
The window is under 10 ms in a plain SITL build, so a sweep cannot reliably hit it. Build SITL with
disarm_split_hold_test.patch (test only: holds the 2nd freefile relocation 3 s) and run with --sweep 16.5. Without the fix
blackbox alternates SHUTTING_DOWN/PREPARE_LOG_FILE forever (visible only as state traces, not as log numbers; a re-arm
masks it); with the fix it reaches STOPPED and a re-arm logs normally.
Usage: test_sdcard_disarm_during_split.py --elf X.elf --workdir ABSDIR [--disarm-at -1 | --sweep 6.0,6.1,...]"""
import argparse, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', '..', 'blackbox'))
import sdcard_wraparound_lib as lib
import fat_inspect, craft_card, test_sdcard_evict_cases as ev

CS, SC = 4096, 128
LAYOUT = ([ev.L(5, 128, 256), ev.L(1, 640, SC, SC * CS), ev.L(2, 768, 256), ev.L(3, 1024, 256), ev.L(4, 1280, 256)],
          (640, 0), 1536)


def snap_info(img):
    s = img + '.snap'; shutil.copyfile(img, s)
    return ev.view(fat_inspect.inspect(s), LAYOUT[2])


def trial(elf, crafted, work, port, disarm_at, tag):
    img = os.path.join(work, 'run_%s.img' % tag); shutil.copyfile(crafted, img)
    eeprom = os.path.join(work, 'eeprom_%s.bin' % tag)
    if os.path.exists(eeprom): os.remove(eeprom)
    sitl = lib.SitlProcess(elf, eeprom, img, port, os.path.join(work, 'sitl_%s.log' % tag)); sitl.start()
    out = {'tag': tag}
    try:
        if not lib.wait_for_port(port, 20): raise RuntimeError('port')
        time.sleep(1)
        with lib.MspClient('localhost', port) as c:
            lib.set_receiver_type_msp(c); lib.setup_arm_mode(c); lib.enable_feature_blackbox(c)
            lib.set_setting(c, 'blackbox_device', 2); lib.set_setting(c, 'blackbox_arm_control', 0); lib.save_and_reboot(c)
        time.sleep(3)
        if not lib.wait_for_port(port, 20): raise RuntimeError('no port after reboot')
        time.sleep(1)
        with lib.MspClient('localhost', port) as c:
            time.sleep(3.0); lib.enable_hitl(c); lib.rc_pump(c, 4.0)
            n0 = snap_info(img)['maxnum']
            if not lib.wait_for_arm_state(c, True, lib.RC_LOW, lib.RC_HIGH, timeout=3.0): raise RuntimeError('did not arm')
            t0 = time.time(); tl = []; last_free = None; split_t = None
            lim = disarm_at if disarm_at >= 0 else 20.0
            while time.time() - t0 < lim:
                lib.send_rc(c, aux1=lib.RC_HIGH); lib.send_gps(c)
                s = lib.query_sdcard_summary(c); t = round(time.time() - t0, 3)
                if s:
                    tl.append((t, s['state'], s['freeKB']))
                    if last_free is not None and s['freeKB'] > last_free + 256 and split_t is None: split_t = t
                    last_free = s['freeKB']
                    if disarm_at < 0 and split_t is not None and t > split_t + 1.0: break
                time.sleep(0.005)
            out['timeline'] = tl; out['split_t'] = split_t
            lib.wait_for_arm_state(c, False, lib.RC_LOW, lib.RC_LOW, timeout=3.0)
            lib.rc_pump(c, 2.0, aux1=lib.RC_LOW); a = snap_info(img)
            lib.rc_pump(c, 4.0, aux1=lib.RC_LOW); b = snap_info(img)
            summ = lib.query_sdcard_summary(c)
            # re-arm: does a new log appear?
            ok = lib.wait_for_arm_state(c, True, lib.RC_LOW, lib.RC_HIGH, timeout=3.0)
            lib.rc_pump(c, 1.5, aux1=lib.RC_HIGH); lib.wait_for_arm_state(c, False, lib.RC_LOW, lib.RC_LOW, timeout=3.0)
            lib.rc_pump(c, 2.0, aux1=lib.RC_LOW); r = snap_info(img)
            out.update(n0=n0, after2=a['maxnum'], after6=b['maxnum'], loop=b['maxnum'] > a['maxnum'], summary=summ,
                       rearm_armed=ok, after_rearm=r['maxnum'], rearm_new_log=r['maxnum'] > b['maxnum'], viol=b['viol'])
    finally:
        sitl.terminate_clean()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--elf', required=True); ap.add_argument('--workdir', required=True)
    ap.add_argument('--disarm-at', type=float, default=-1); ap.add_argument('--sweep', default='')
    ap.add_argument('--port', type=int, default=5800)
    a = ap.parse_args(); os.makedirs(a.workdir, exist_ok=True)
    init = os.path.join(a.workdir, 'init.img'); ev.make_init_image(init, a.elf, a.port, a.workdir)
    crafted = os.path.join(a.workdir, 'crafted.img'); shutil.copyfile(init, crafted)
    craft_card.craft(crafted, LAYOUT[0], LAYOUT[1], LAYOUT[2])
    times = [float(x) for x in a.sweep.split(',')] if a.sweep else [a.disarm_at]
    bad = 0
    for d in times:
        r = trial(a.elf, crafted, a.workdir, a.port, d, 'd%s' % d)
        if d < 0:
            tl = r['timeline']; ch = [(tl[i][0], tl[i-1][1:], tl[i][1:]) for i in range(1, len(tl)) if tl[i][1:] != tl[i-1][1:] and (tl[i][1] != tl[i-1][1] or abs(tl[i][2] - tl[i-1][2]) > 64)]
            print('probe: split_t=%s; SD changes (t, before, after): %s' % (r['split_t'], ch[:20]))
        print('disarm@%.2f: LOG %d -> %d(+2s) -> %d(+6s) loop=%s | re-arm armed=%s new_log=%s | sd=%s viol=%s'
              % (d, r['n0'], r['after2'], r['after6'], r['loop'], r['rearm_armed'], r['rearm_new_log'], r['summary'], r['viol']))
        bad += r['loop'] or not r['rearm_new_log']
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main())
