#!/usr/bin/env python3
"""Bench-arm setup for the FC305_H7 real-card test. `apply` saves originals to $TMPDIR/hw_orig_settings.json then sets
receiver_type=MSP, ARM on AUX1 (1700-2100), saves.
`restore` puts the originals back (receiver_type, clears mode slot 0). Does not touch card contents."""
import sys, json, os, struct, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hw_msp import Msp
STORE = os.path.join(os.environ.get('TMPDIR', '/home/raymorris/Documents/planes/inavflight/tmp'), 'hw_orig_settings.json')
def getv(m, n):
    r = m.request(0x1003, n.encode() + b'\0'); assert r is not None, n; return r[0]
def setv(m, n, v):
    assert m.request(0x1004, n.encode() + b'\0' + bytes([v])) is not None, n
def main():
    m = Msp()
    assert m.request(1) is not None, 'FC not responding (CLI mode? configurator open? sandbox?)'
    if sys.argv[1] == 'apply':
        if not os.path.exists(STORE):
            json.dump({k: getv(m, k) for k in ('receiver_type',)}, open(STORE, 'w'))
        print('originals', open(STORE).read())
        setv(m, 'receiver_type', 2)
        assert m.request(35, bytes([0, 0, 0, 32, 48])) is not None
    else:
        o = json.load(open(STORE))
        for k, v in o.items(): setv(m, k, v)
        assert m.request(35, bytes([0, 0, 0, 0, 0])) is not None
    assert m.request(250, timeout=3) is not None, 'EEPROM write failed'
    print('saved; readback:', getv(m, 'receiver_type'))
main()
