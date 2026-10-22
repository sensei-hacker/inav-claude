#!/usr/bin/env python3
"""Crafted-layout eviction test for SD blackbox wraparound (PR #12150 + fixes A/B).

For each case a card image is REWRITTEN (craft_card.py) to an exact layout, then each SITL
binary is run on its own copy of that image for N short flights; fat_inspect.py is the oracle.

Geometry: 4 KB clusters (mkfs.vfat -s8), 300 MB sparse image => supercluster (SC) = 128 clusters
= 512 KB. A ~3 s SITL flight writes ~214 KB (< 1 SC) and takes exactly 1 SC from the freefile.
Cluster numbers below are absolute; dirs are 2,3; everything past `stale_from` is marked used.

Cases (log numbers follow ring order: lowest address >= freefile start is the OLDEST):
 A  freefile (640, 40 clusters = 0.31 SC) directly before oldest log O1 which starts at 680
    (=freefile end, deliberately NOT SC aligned; real tails are 1 cluster mod SC so any tail
    leaves the following log unaligned). Newer logs below, older ones beyond.
 A1 same with tail = 1 cluster (the "freefile is k*SC+1 clusters" form afatfs creates).
 B  freefile (640, size 0) directly before the LAST-addressed log S (640, 3 s flight, 214016 B
    < 1 SC), nothing beyond S. Newer logs below.
 C  control: freefile (640, size 0), oldest log O1 at 640 with 3 more logs beyond it.
 D  card full, freefile (640, size 0); oldest candidate log O1 at 640 is only 64 clusters (< 1 SC) before the
    next log (704) -- abnormal/unaligned layout. Expect base/fix/fix2 stall; fix3 discards O1, evicts another log.
 E  as D but TWO such unusable logs in a row (640 and 704, 64 clusters each, next at 768): discard loop must progress.
 F  card full, NO LOG files at all, nothing reclaimable (freefile (640,0), everything else allocated): all binaries must
    stop logging cleanly: no hang/crash/loop, SITL still answers MSP, process alive.

Observables per flight: LOG count, newest LOG number (new log == number+1), freefile start/size,
stranded clusters (= unowned clusters inside [128, layout_end)), MSP_SDCARD_SUMMARY.
Usage: test_sdcard_evict_cases.py --elf-dir DIR --workdir DIR [--cases A,A1,B,C] [--variants base,fix,fix2]
       [--flights 3] [--port 5800]
Exit non-zero on any harness failure/violation; verdicts per case are printed as a table (they are
observations, expectations are printed beside them but do not alter the exit code).
"""
import argparse, os, shutil, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'blackbox'))
import sdcard_wraparound_lib as lib
import fat_inspect, craft_card

SC = 128
CS = 4096
LOGSZ = 214016  # realistic 3 s flight


def L(n, start, chain, size=None):
    return (n, start, chain, size if size is not None else int(chain * CS * 0.8))


def layouts():
    low = [L(5, 128, 256), L(6, 384, 256)]  # newer logs at low addresses (ring wrapped)
    return {
        # name: (logs, freefile(start,size_bytes), stale_from, description)
        'A': (low + [L(1, 680, 344), L(2, 1024, 256), L(3, 1280, 256), L(4, 1536, 256)],
              (640, 40 * CS), 1792, 'freefile tail 40 clu (<1 SC) directly before oldest log@680'),
        'A1': (low + [L(1, 641, 383), L(2, 1024, 256), L(3, 1280, 256), L(4, 1536, 256)],
               (640, 1 * CS), 1792, 'freefile tail 1 clu directly before oldest log@641'),
        'B': (low + [L(1, 640, SC, LOGSZ)],
              (640, 0), 768, 'freefile size 0 before the last-addressed log (214016 B < 1 SC), nothing beyond'),
        'D': (low + [L(1, 640, 64), L(2, 704, 256), L(3, 960, 256), L(4, 1216, 256)],
              (640, 0), 1472, 'D: oldest log 64 clu (<1 SC) before next log; freefile size 0'),
        'E': (low + [L(1, 640, 64), L(2, 704, 64), L(3, 768, 256), L(4, 1024, 256)],
              (640, 0), 1280, 'E: two consecutive unusable (<1 SC) logs at 640,704; freefile size 0'),
        'F': ([], (640, 0), 128, 'F: card full, no LOG files, nothing reclaimable'),
        'G': ([], (128, 40 * CS), 168, 'G: freefile 40 clu (<1 SC, nonzero), NO LOG files, nothing reclaimable (fix4 new-condition gave-up path)'),
        'C': (low + [L(1, 640, 256), L(2, 896, 256), L(3, 1152, 256), L(4, 1408, 256)],
              (640, 0), 1664, 'control: freefile size 0, oldest log with 3 logs beyond'),
    }


def sh(cmd):
    subprocess.run(cmd, shell=True, check=True)


def make_init_image(path, elf, port, work):
    """Fresh 300MB image, let SITL create FREESPAC.E + LOGS with one short flight."""
    if os.path.exists(path): os.remove(path)
    sh('truncate -s 300M %s && echo "start=2048, type=c" | sfdisk -q %s && mkfs.vfat -F32 -s8 --offset 2048 %s >/dev/null'
       % (path, path, path))
    r = run_sitl(elf, path, port, work, flights=1, dur=1.5, tag='init', report=False)
    return r


def run_sitl(elf, image, port, work, flights, dur, tag, report=True, case_info=None):
    eeprom = os.path.join(work, 'eeprom_%s_%d.bin' % (tag, port))
    if os.path.exists(eeprom): os.remove(eeprom)
    log = os.path.join(work, 'sitl_%s.log' % tag)
    if os.path.exists(log): os.remove(log)
    out = subprocess.run(['bash', '-c', "ss -tlnp | grep -c ':%d '" % port], capture_output=True, text=True).stdout.strip()
    if out not in ('0', ''):
        raise RuntimeError('port %d already in use; another SITL running?' % port)
    sitl = lib.SitlProcess(os.path.abspath(elf), eeprom, os.path.abspath(image), port, log)
    sitl.start()
    rows = []
    try:
        if not lib.wait_for_port(port, 20): raise RuntimeError('SITL port not up (check ss -tlnp)')
        time.sleep(1)
        with lib.MspClient('localhost', port) as c:
            lib.set_receiver_type_msp(c); lib.setup_arm_mode(c); lib.enable_feature_blackbox(c)
            lib.set_setting(c, 'blackbox_device', 2); lib.set_setting(c, 'blackbox_arm_control', 0)
            lib.save_and_reboot(c)
        time.sleep(3)
        if not lib.wait_for_port(port, 20): raise RuntimeError('no port after reboot')
        time.sleep(1)
        with lib.MspClient('localhost', port) as c:
            s0 = lib.query_sdcard_summary(c)
            boot_ok = bool(s0 and s0['totalKB'] > 0 and s0['state'] == 4)
            time.sleep(3.0)  # gyro cal before HITL
            lib.enable_hitl(c); lib.rc_pump(c, 4.0)
            snap = image + '.snap'
            for i in range(flights):
                ok, s = lib.do_flight(c, dur, settle_s=1.5, verbose=False)
                shutil.copyfile(image, snap)
                r = fat_inspect.inspect(snap)
                rows.append({'flight': i + 1, 'armed': ok, 'sum': s, 'r': r})
        alive = sitl.is_running()
        post = None
        try:
            with lib.MspClient('localhost', port) as c2:
                post = lib.query_sdcard_summary(c2)
        except Exception as e:
            post = 'MSP EXC %s' % e
    finally:
        sitl.terminate_clean()
    return {'boot_ok': boot_ok, 's0': s0, 'rows': rows, 'log': log, 'alive': alive, 'post': post}


def view(r, layout_end):
    """Chain-based extents. gaps/stranded computed inside [128, layout_end)."""
    ff = r['freefile']
    ext = [(g['start'], g['chain_len'], g['name']) for g in r['logs']]
    if ff and ff['clusters']: ext.append((ff['start'], ff['clusters'], 'FREEFILE'))
    ext.sort()
    pos, stranded, gaps = 128, 0, []
    for st, n, nm in ext:
        if st > pos: stranded += st - pos; gaps.append((pos, st - pos, 'before ' + nm))
        pos = max(pos, st + n)
    if layout_end > pos: stranded += layout_end - pos; gaps.append((pos, layout_end - pos, 'tail'))
    nums = sorted(int(g['name'][3:8]) for g in r['logs'])
    return {'nlogs': len(nums), 'maxnum': nums[-1] if nums else 0, 'ffstart': ff['start'] if ff else None,
            'ffclu': ff['clusters'] if ff else None, 'stranded': stranded, 'gaps': gaps,
            'viol': r['violations'], 'ext': ext}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--elf-dir', required=True); ap.add_argument('--workdir', required=True)
    ap.add_argument('--cases', default='A,A1,B,C,D,E,F'); ap.add_argument('--variants', default='base,fix,fix2,fix3')
    ap.add_argument('--flights', type=int, default=3); ap.add_argument('--dur', type=float, default=3.0)
    ap.add_argument('--port', type=int, default=5800)
    a = ap.parse_args()
    os.makedirs(a.workdir, exist_ok=True)
    init = os.path.join(a.workdir, 'init.img')
    base_elf = os.path.join(a.elf_dir, 'SITL-base.elf')
    print('== creating initial image with SITL-base.elf')
    ri = make_init_image(init, base_elf, a.port, a.workdir)
    if not ri['boot_ok'] or ri['rows'][0]['r']['freefile'] is None or not ri['rows'][0]['r']['logs']:
        print('HARNESS FAIL: init image has no freefile/LOGS', ri['s0']); return 2
    L_ = layouts(); bad = 0; results = {}
    for case in a.cases.split(','):
        logs, ff, stale, desc = L_[case]
        crafted = os.path.join(a.workdir, 'crafted_%s.img' % case)
        shutil.copyfile(init, crafted)
        craft_card.craft(crafted, logs, ff, stale)
        v = view(fat_inspect.inspect(crafted), stale)
        print('\n== CASE %s: %s' % (case, desc))
        print('   crafted image check: logs=%d ff=(%s,%s clu) stranded_in_layout=%d violations=%s'
              % (v['nlogs'], v['ffstart'], v['ffclu'], v['stranded'], v['viol']))
        if v['viol'] or v['stranded'] != 0 or v['ffstart'] != ff[0]:
            print('   HARNESS FAIL: crafted image not as specified'); bad += 1; continue
        for var in a.variants.split(','):
            if not os.path.exists(os.path.join(a.elf_dir, 'SITL-%s.elf' % var)):
                print('   HARNESS FAIL: missing elf for', var); bad += 1; continue
            img = os.path.join(a.workdir, 'run_%s_%s.img' % (case, var))
            shutil.copyfile(crafted, img)
            elf = os.path.join(a.elf_dir, 'SITL-%s.elf' % var)
            print('-- %s / %s' % (case, var))
            try:
                res = run_sitl(elf, img, a.port, a.workdir, a.flights, a.dur, '%s_%s' % (case, var))
            except Exception as e:
                print('   HARNESS FAIL:', e); bad += 1; continue
            print('   boot_ok(crafted image mounts READY)=%s summary=%s' % (res['boot_ok'], res['s0']))
            print('   after flights: process alive=%s MSP summary=%s' % (res['alive'], res['post']))
            if not res['alive'] or not isinstance(res['post'], dict): bad += 1
            if not res['boot_ok']: bad += 1
            out = []
            for row in res['rows']:
                w = view(row['r'], stale + 0)
                s = row['sum'] or {}
                print('   flight %d armed=%s logs=%d newest=LOG%05d ff=(%s,%s clu) stranded=%d gaps=%s freeKB=%s viol=%s'
                      % (row['flight'], row['armed'], w['nlogs'], w['maxnum'], w['ffstart'], w['ffclu'], w['stranded'],
                         w['gaps'], s.get('freeKB'), w['viol']))
                if not row['armed'] or w['viol']: bad += 1
                out.append(w)
            # post-run reboot check on the final image
            try:
                rb = run_sitl(elf, img, a.port, a.workdir, 1, a.dur, '%s_%s_reboot' % (case, var))
                w2 = view(rb['rows'][0]['r'], stale)
                before = out[-1]['maxnum'] if out else 0
                print('   re-boot of final image mounts READY=%s; 1 more flight: armed=%s newest LOG%05d (before reboot LOG%05d) -> logging resumed=%s viol=%s alive=%s'
                      % (rb['boot_ok'], rb['rows'][0]['armed'], w2['maxnum'], before, w2['maxnum'] > before, w2['viol'], rb['alive']))
                if not rb['boot_ok'] or w2['viol']: bad += 1
            except Exception as e:
                print('   HARNESS FAIL(reboot):', e); bad += 1
            results[(case, var)] = out
    print('\n== SUMMARY (first-eviction flight = flight 1)')
    print('%-4s %-5s %-8s %-8s %-14s %-9s %s' % ('case', 'var', 'newLOG#', 'logs', 'freefile', 'stranded', 'newest LOG# after each flight (start: %d-ish)' % 0))
    for (case, var), out in results.items():
        w = out[0]
        created = [o['maxnum'] for o in out]  # newest LOG number after each flight (unchanged == no new log)
        print('%-4s %-5s %-8s %-8s %-14s %-9s %s' % (case, var, w['maxnum'], w['nlogs'], '%s,%s' % (w['ffstart'], w['ffclu']), w['stranded'], created))
    print('harness failures/violations: %d' % bad)
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main())
