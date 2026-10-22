#!/usr/bin/env python3
"""Arm a bench FC (no props/motors) over MSP, log to SD with the blackbox, and watch for the PR #12150 wraparound
split (freefile exhausted -> evict oldest LOG, new LOG while still armed). Records a timeline of
MSP_SDCARD_SUMMARY (state, free KB) so the write rate, time-to-full and split instants are known.
The actual frame gap is measured afterwards by blackbox_split_gap.py on the LOG*.TXT files read off the card.

Prereqs: `hw_setup.py apply` (receiver_type=MSP, ARM on AUX1). Props OFF, no ESC power. Configurator closed.
Exit: 0 split observed + clean disarm; 2 no split in time; 1 setup/connection failure.
Sandbox note: if /dev/ttyACM0 cannot be opened it may be a sandbox restriction (allowlisted; ask the user), or the
FC is in CLI/MSC mode, or another program holds the port."""
import argparse, json, os, struct, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hw_msp import Msp
ARMED = 1 << 2
ARM_NAMES = {6: 'GEOZONE', 7: 'FAILSAFE', 8: 'NOT_LEVEL', 9: 'SENSORS_CALIBRATING', 10: 'OVERLOAD', 11: 'NAV_UNSAFE', 12: 'COMPASS',
             13: 'ACC', 14: 'ARM_SWITCH', 15: 'HWFAIL', 16: 'BOXFAILSAFE', 18: 'RX', 19: 'THROTTLE', 20: 'CLI', 21: 'CMS', 22: 'OSDMENU',
             23: 'ROLLPITCH', 24: 'SERVOAUTOTRIM', 25: 'OOM', 26: 'BADSETTING', 27: 'PWMERR', 28: 'NOPREARM', 29: 'DSHOT_BEEPER', 30: 'LANDING'}

class Rig:
    def __init__(self, port):
        self.m = Msp(port); self.aux1 = 1000; self.thr = 1000; self.next_rc = 0
    def rc(self):
        ch = [1500, 1500, self.thr, 1500, self.aux1, 1500, 1500, 1500]
        self.m.send(200, struct.pack('<8H', *ch))
    def tick(self):
        """Keep the 50 Hz RC stream alive; call between every request."""
        now = time.time()
        if now >= self.next_rc:
            self.rc(); self.next_rc = now + 0.02
        self.m.pump()
    def status(self):
        r = self.m.request(0x2000)
        if r is None or len(r) < 13: return None
        return struct.unpack_from('<I', r, 9)[0]
    def sd(self):
        r = self.m.request(79)
        if r is None or len(r) < 11: return None
        sup, st, err, free, tot = struct.unpack_from('<BBBII', r, 0)
        return st, err, free, tot
    def stream(self, secs):
        end = time.time() + secs
        while time.time() < end:
            self.tick(); time.sleep(0.005)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', default='/dev/ttyACM0')
    ap.add_argument('--max-seconds', type=float, default=900, help='abort (disarm) after this long armed')
    ap.add_argument('--splits', type=int, default=1, help='stop after this many splits seen')
    ap.add_argument('--after-split-s', type=float, default=5.0)
    ap.add_argument('--probe-seconds', type=float, default=0, help='only arm this long to measure write rate, then disarm (no split wait)')
    ap.add_argument('--out', default=os.path.join(os.environ.get('TMPDIR', '.'), 'split_timeline.json'))
    a = ap.parse_args()
    try:
        rig = Rig(a.port)
    except Exception as e:
        print('FAIL cannot open %s: %s' % (a.port, e)); print('  Check: FC plugged in? Configurator closed? CLI/MSC mode? sandbox restriction (ask the user)?'); return 1
    if rig.m.request(1) is None:
        print('FAIL FC does not answer MSP (stuck in CLI? send exit)'); return 1
    sd0 = rig.sd()
    if not sd0 or sd0[0] != 4:
        print('FAIL SD card not READY: %s' % (sd0,)); return 1
    print('OK  SD READY, free %.1f MB of %.1f MB' % (sd0[2] / 1024, sd0[3] / 1024))
    rig.stream(2.5)  # disarmed RC stream so RX link is up (and the >2s post-boot gyro cal settles)
    fl = rig.status()
    print('arming flags before: 0x%x %s' % (fl or 0, [n for b, n in ARM_NAMES.items() if fl and fl & (1 << b)]))
    rig.aux1 = 2000
    t0 = time.time(); armed = False
    while time.time() - t0 < 6:
        rig.tick(); fl = rig.status()
        if fl is not None and fl & ARMED: armed = True; break
        time.sleep(0.02)
    if not armed:
        print('FAIL did not arm; flags 0x%x %s' % (fl or 0, [n for b, n in ARM_NAMES.items() if fl and fl & (1 << b)]))
        rig.aux1 = 1000; rig.stream(1); return 1
    print('OK  ARMED, blackbox logging to SD'); t_arm = time.time()
    tl = []; splits = []; last = None; peak_free = sd0[2]; t_split_done = None; rc = 2; last_prog = 0
    try:
        while True:
            rig.tick()
            s = rig.sd(); now = time.time() - t_arm
            if s is None: tl.append((now, None)); continue
            tl.append((round(now, 3), s[0], s[2]))
            if last is not None and s[2] > last[2] + 4096:  # free space jumped UP: freefile relocated
                splits.append({'t': round(now, 3), 'free_before_kb': last[2], 'free_after_kb': s[2], 'state': s[0]}); t_split_done = time.time()
                print('SPLIT #%d at t=%.1fs free %d -> %d KB' % (len(splits), now, last[2], s[2]))
            if last is not None and s[0] != last[0]: print('  sd state %d -> %d at t=%.2fs' % (last[0], s[0], now))
            last = s
            if now - last_prog > 10: last_prog = now; print('  t=%5.0fs free=%.1f MB' % (now, s[2] / 1024))
            if a.probe_seconds and now > a.probe_seconds: break
            if len(splits) >= a.splits and time.time() - t_split_done > a.after_split_s: rc = 0; break
            if now > a.max_seconds: print('TIMEOUT without enough splits'); break
            time.sleep(0.05)
    finally:
        rig.aux1 = 1000; rig.thr = 1000
        t1 = time.time(); fl = None
        while time.time() - t1 < 8:
            rig.tick(); fl = rig.status()
            if fl is not None and not fl & ARMED: break
            time.sleep(0.02)
        disarmed = fl is not None and not fl & ARMED
        print('%s disarmed' % ('OK ' if disarmed else 'FAIL NOT'))
        rig.stream(1.5)
    sdn = rig.sd()
    fr = [x for x in tl if len(x) == 3]
    rate = None
    if len(fr) > 20:
        i0 = next(i for i, x in enumerate(fr) if x[0] > 2); xs = [x for x in fr[i0:]]
        # consider only the monotone-falling stretch before the first split
        end = len(xs)
        for j in range(1, len(xs)):
            if xs[j][2] > xs[j - 1][2] + 4096: end = j; break
        xs = xs[:end]
        if len(xs) > 10 and xs[-1][0] > xs[0][0]: rate = (xs[0][2] - xs[-1][2]) / (xs[-1][0] - xs[0][0])
    print('write rate: %s KB/s' % ('%.1f' % rate if rate else 'n/a'))
    if rate: print('time to fill the current %.0f MB of freefile: %.0f s' % (sd0[2] / 1024, sd0[2] / rate))
    json.dump({'sd_before': sd0, 'sd_after': sdn, 'splits': splits, 'rate_kBps': rate, 'timeline': tl, 'disarmed': disarmed}, open(a.out, 'w'))
    print('timeline saved to', a.out, '| splits observed:', len(splits))
    return rc if disarmed else 1
if __name__ == '__main__':
    sys.exit(main())
