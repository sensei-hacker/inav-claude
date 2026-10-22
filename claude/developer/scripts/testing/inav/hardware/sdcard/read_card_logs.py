#!/usr/bin/env python3
"""READ-ONLY: copy LOG*.TXT (or list them) from an INAV SD card exposed as a block device (FC in `msc` mode / reader) or image.
Walks FAT copy #1 (afatfs never writes copy #2). Opens the device O_RDONLY only. Never mounts.
Usage: read_card_logs.py /dev/sdX --list | read_card_logs.py /dev/sdX --out DIR [--only LOG00011,LOG00012] [--min-number N]"""
import argparse, os, struct, sys

class Card:
    def __init__(s, path):
        s.f = open(path, 'rb'); mbr = s.f.read(512)
        if mbr[510:512] != b'\x55\xaa': raise SystemExit('FAIL no MBR on %s' % path)
        p = struct.unpack_from('<I', mbr, 454)[0] * 512
        s.f.seek(p); b = s.f.read(512)
        bps, spc, rsv, nf = struct.unpack_from('<HBHB', b, 11); fatsz = struct.unpack_from('<I', b, 36)[0]
        s.root = struct.unpack_from('<I', b, 44)[0]; s.cs = bps * spc
        s.data = p + (rsv + nf * fatsz) * bps
        s.f.seek(p + rsv * bps); s.fat = struct.unpack('<%dI' % (fatsz * bps // 4), s.f.read(fatsz * bps))
    def chain(s, c):
        out = []
        while 2 <= c < 0x0FFFFFF8 and len(out) < len(s.fat): out.append(c); c = s.fat[c] & 0x0FFFFFFF
        return out
    def readchain(s, c, size):
        buf = bytearray(); runs = []
        for cl in s.chain(c):
            if runs and runs[-1][0] + runs[-1][1] == cl: runs[-1][1] += 1
            else: runs.append([cl, 1])
        for st, n in runs:
            s.f.seek(s.data + (st - 2) * s.cs); buf += s.f.read(n * s.cs)
            if len(buf) >= size: break
        return bytes(buf[:size])
    def entries(s, c):
        data = b''.join(s.readchain(x, s.cs) for x in s.chain(c)); out = []
        for i in range(0, len(data), 32):
            e = data[i:i + 32]
            if e[0] == 0: break
            if e[0] == 0xE5 or e[11] == 0x0F or e[11] & 8: continue
            out.append((e[:11].decode('latin1'), e[11], (struct.unpack_from('<H', e, 20)[0] << 16) | struct.unpack_from('<H', e, 26)[0], struct.unpack_from('<I', e, 28)[0]))
        return out

ap = argparse.ArgumentParser(); ap.add_argument('dev'); ap.add_argument('--list', action='store_true'); ap.add_argument('--out')
ap.add_argument('--only'); ap.add_argument('--min-number', type=int, default=0)
a = ap.parse_args(); c = Card(a.dev)
logs = None
for n, at, st, sz in c.entries(c.root):
    if n.strip() == 'LOGS' and at & 0x10: logs = st
if logs is None: raise SystemExit('FAIL no LOGS directory')
ents = [e for e in c.entries(logs) if e[0].startswith('LOG') and e[0].endswith('TXT')]
only = set(a.only.split(',')) if a.only else None
for n, at, st, sz in sorted(ents):
    num = int(n[3:8]); base = n[:8]
    sel = num >= a.min_number and (only is None or base in only)
    print('%s start=%d size=%d %s' % (n, st, sz, '' if sel else '(skipped)'))
    if a.out and sel:
        os.makedirs(a.out, exist_ok=True); d = c.readchain(st, sz)
        if len(d) != sz: print('  FAIL short read %d/%d' % (len(d), sz)); sys.exit(1)
        open(os.path.join(a.out, base + '.TXT'), 'wb').write(d)
