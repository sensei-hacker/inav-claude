#!/usr/bin/env python3
"""Power-cut trial driver for PR #12150 (needs the power-cut TEST firmware, which holds 40 s between the log delete and
the freefile relocation, and a freefile shrunk with shrink_freefile.py). Arms the bench FC, logs to SD, and when the
freefile is exhausted prints CUE lines: the human pulls USB during the hold. Props/motors/ESC OFF.
Exit: 0 cue given and link lost (cut happened), 2 no cue in time, 1 setup failure."""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_split_gap import Rig, ARMED

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--port', default='/dev/ttyACM0'); ap.add_argument('--max-seconds', type=float, default=600)
    a = ap.parse_args()
    rig = Rig(a.port)
    sd0 = rig.sd()
    if not sd0 or sd0[0] != 4: print('FAIL SD not READY %s' % (sd0,), flush=True); return 1
    rig.stream(2.5); rig.aux1 = 2000; t0 = time.time(); armed = False
    while time.time() - t0 < 6:
        rig.tick(); fl = rig.status()
        if fl is not None and fl & ARMED: armed = True; break
        time.sleep(0.02)
    if not armed: print('FAIL did not arm', flush=True); return 1
    print('ARMED free=%.1f MB' % (sd0[2] / 1024), flush=True)
    t_arm = time.time(); last_print = 0; cue_at = None; lost = 0
    while time.time() - t_arm < a.max_seconds:
        try:
            rig.tick(); s = rig.sd()
        except Exception as e:
            print('LINK LOST (%s) at +%.0fs, cut happened' % (type(e).__name__, time.time() - t_arm), flush=True); return 0
        if s is None:
            lost += 1
            if lost > 20: print('NO MSP ANSWER at +%.0fs, treating as cut' % (time.time() - t_arm), flush=True); return 0
        else:
            lost = 0
            if s[2] == 0 and cue_at is None:
                cue_at = time.time(); print('INFO: free space exhausted; split expected within ~2 min, pull USB when BOTH LEDs light', flush=True)
        if time.time() - last_print > 5:
            last_print = time.time(); print('t=%.0f free=%s cue=%s' % (last_print - t_arm, s and s[2] // 1024, cue_at is not None), flush=True)
        time.sleep(0.05)
    print('NO CUT within max-seconds; disarming', flush=True); rig.aux1 = 1000; rig.stream(1); return 2
if __name__ == "__main__":
    sys.exit(main())
