#!/usr/bin/env python3
"""Measure the logging gap at SD blackbox log splits (PR #12150 wraparound) from LOG*.TXT files read off the card.
For each consecutive pair of logs: gap = first main-frame time of the new log - last main-frame time of the old log
(both are on the boot-relative micros clock, which keeps running across a split), and lost frames = gap / median frame period - 1.
Also reports the biggest intra-log jump per log (a stall that is NOT at a boundary). Needs `blackbox_decode` on PATH.
Usage: blackbox_split_gap.py LOG00011.TXT LOG00012.TXT ... [--warn-ms 250 --fail-ms 1000 --json out.json]
Exit 0 all boundary gaps < warn, 3 any warn, 4 any >= fail, 1 error. Pass logs from ONE boot (time resets at reboot)."""
import argparse, csv, json, os, shutil, statistics, subprocess, sys, tempfile

def decode(path, work):
    d = tempfile.mkdtemp(dir=work); base = os.path.join(d, os.path.basename(path)); shutil.copy(path, base)
    p = subprocess.run(['blackbox_decode', base], capture_output=True, text=True)
    if p.returncode != 0: raise SystemExit('FAIL blackbox_decode %s: %s' % (path, p.stderr[-300:]))
    outs = sorted(f for f in os.listdir(d) if f.endswith('.csv') and '.gps.' not in f)
    if not outs: raise SystemExit('FAIL no CSV produced for %s (empty/undecodable log? headers: %s)' % (path, p.stdout[-300:]))
    rows = []
    for o in outs:
        with open(os.path.join(d, o)) as f:
            r = csv.reader(f); hdr = [h.strip() for h in next(r)]
            ti = hdr.index('time (us)'); li = hdr.index('loopIteration')
            for row in r:
                try: rows.append((int(row[li]), int(row[ti])))
                except (ValueError, IndexError): pass
    return rows

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('logs', nargs='+'); ap.add_argument('--warn-ms', type=float, default=250)
    ap.add_argument('--fail-ms', type=float, default=1000); ap.add_argument('--json'); a = ap.parse_args()
    work = tempfile.mkdtemp(prefix='bbgap_', dir=os.environ.get('TMPDIR')); res = {'logs': [], 'splits': []}
    prev = None
    for p in a.logs:
        rows = decode(p, work)
        if len(rows) < 3: print('WARN %s: only %d frames' % (p, len(rows))); res['logs'].append({'file': p, 'frames': len(rows)}); continue
        t = []; off = 0
        for i, (_, tm) in enumerate(rows):  # unwrap u32 micros
            if i and tm + off < t[-1] - 2**31: off += 2**32
            t.append(tm + off)
        dts = [b - a_ for a_, b in zip(t, t[1:])]; med = statistics.median(dts)
        worst = max(range(len(dts)), key=lambda i: dts[i])
        info = {'file': os.path.basename(p), 'frames': len(rows), 'first_us': t[0], 'last_us': t[-1], 'median_dt_us': med,
                'max_intra_dt_ms': dts[worst] / 1000, 'max_intra_at_s': (t[worst] - t[0]) / 1e6, 'duration_s': (t[-1] - t[0]) / 1e6}
        res['logs'].append(info)
        print('%s: %d frames, %.1fs, median dt %.0fus, biggest intra-log jump %.2f ms at +%.1fs' % (info['file'], info['frames'], info['duration_s'], med, info['max_intra_dt_ms'], info['max_intra_at_s']))
        if prev:
            gap = t[0] - prev['last']; lost = gap / prev['med'] - 1
            sp = {'from': prev['name'], 'to': info['file'], 'gap_ms': gap / 1000, 'lost_frames': round(lost, 1), 'median_dt_us': prev['med'],
                  'iter_gap': rows[0][0] - prev['iter']}
            res['splits'].append(sp)
            print('  SPLIT %s -> %s: gap %.2f ms (~%.0f frames at %.0f us/frame)' % (sp['from'], sp['to'], sp['gap_ms'], lost, prev['med']))
        prev = {'last': t[-1], 'med': med, 'name': info['file'], 'iter': rows[-1][0]}
    worst = max([s['gap_ms'] for s in res['splits']] or [0])
    res['verdict'] = 'FAIL' if worst >= a.fail_ms else 'WARN' if worst >= a.warn_ms else 'PASS'
    print('splits measured: %d, worst gap %.2f ms -> %s (pass < %g ms, fail >= %g ms)' % (len(res['splits']), worst, res['verdict'], a.warn_ms, a.fail_ms))
    if a.json: json.dump(res, open(a.json, 'w'), indent=1)
    shutil.rmtree(work, ignore_errors=True)
    return {'PASS': 0, 'WARN': 3, 'FAIL': 4}[res['verdict']]
sys.exit(main())
