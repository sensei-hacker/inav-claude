#!/usr/bin/env python3
"""Does disarming before the log has any data corrupt the FAT? (base-branch afatfs_funlink of a file with no cluster)

A new SD blackbox log has firstCluster == 0 until its first write. If the log is discarded in that state,
afatfs_ftruncate() starts at cluster 0; a contiguous file then fills FAT[0 .. freefile start) with the
"unterminated chain" pattern, wiping the reserved entries, the root dir and LOGS chains.
Arms for a short time (--durs), disarms, snapshots the image and reports FAT[0], FAT[1], root/LOGS chains.
Usage: test_sdcard_empty_log_unlink.py --elf X.elf --workdir DIR [--durs 0,0.02,0.05,0.1,0.3] [--port 5800]"""
import argparse, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', '..', 'blackbox'))
import sdcard_wraparound_lib as lib
import fat_inspect, test_sdcard_evict_cases as ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--elf', required=True); ap.add_argument('--workdir', required=True)
    ap.add_argument('--durs', default='0,0.02,0.05,0.1,0.3'); ap.add_argument('--port', type=int, default=5800)
    a = ap.parse_args(); os.makedirs(a.workdir, exist_ok=True)
    init = os.path.join(a.workdir, 'init.img')
    ev.make_init_image(init, a.elf, a.port, a.workdir)
    for d in [float(x) for x in a.durs.split(',')]:
        img = os.path.join(a.workdir, 'run_%s.img' % d); shutil.copyfile(init, img)
        before = fat_inspect.inspect(img)
        r = ev.run_sitl(a.elf, img, a.port, a.workdir, 1, d, 'dur%s' % d)
        after = r['rows'][0]['r']
        print('armed %.2fs: logs %d->%d  fat0 %#x->%#x fat1 %#x->%#x  rootchain %s->%s  freefile %s->%s  alive=%s' % (
            d, len(before['logs']), len(after['logs']), before['fat0'], after['fat0'], before['fat1'], after['fat1'],
            before['rootchain'], after['rootchain'], before['freefile'] and before['freefile']['start'],
            after['freefile'] and after['freefile']['start'], r['alive']))
if __name__ == '__main__':
    main()
