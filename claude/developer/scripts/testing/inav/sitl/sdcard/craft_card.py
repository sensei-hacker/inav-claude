#!/usr/bin/env python3
"""Rewrite a SITL-initialised afatfs SD image (MBR + FAT32, has FREESPAC.E + LOGS) into an
exact, hand-specified layout, so eviction behaviour can be tested at a chosen geometry
instead of hoping a random flight sequence reaches it.

Usage as library:
    craft(image, logs=[(number, start_cluster, chain_clusters, file_size_bytes), ...],
          freefile=(start_cluster, size_bytes), stale_from=<cluster>)
Everything in LOGS is replaced by `logs`. Each log gets a contiguous FAT chain
(start..start+chain-1, EOC at the end), as afatfs writes them. The freefile directory entry
is set to `freefile`. FAT is zeroed for every cluster >= 4 first (clusters 2,3 = root, LOGS),
then clusters from `stale_from` to the end of the card are marked allocated (one EOC-terminated
chain per 128-cluster supercluster, like stale chains of evicted logs). That makes the card
"really full": the only space afatfs may hand out is the freefile. It also matters on boot:
afatfs re-scans the FAT for a free block when the freefile size is 0, so a zero-FAT area
would silently turn a "full" card into an empty one.

FAT copy #1 and #2 are both written (afatfs only reads/writes #1).
"""
import struct, sys

EOC = 0x0FFFFFFF

class Geo:
    def __init__(self, f):
        f.seek(0); mbr = f.read(512)
        if mbr[510:512] != b'\x55\xaa': raise ValueError('no MBR')
        self.pstart = struct.unpack_from('<I', mbr, 446 + 8)[0] * 512
        f.seek(self.pstart); b = f.read(512)
        self.bps, self.spc, rsv, nfats = struct.unpack_from('<HBHB', b, 11)
        self.fatsz = struct.unpack_from('<I', b, 36)[0]
        self.total = struct.unpack_from('<I', b, 32)[0]
        self.rootc = struct.unpack_from('<I', b, 44)[0]
        self.nfats = nfats
        self.csize = self.bps * self.spc
        self.fat0 = self.pstart + rsv * self.bps
        self.datastart = self.pstart + (rsv + nfats * self.fatsz) * self.bps
        self.nclusters = (self.total - rsv - nfats * self.fatsz) // self.spc
        self.sc = self.bps // 4  # clusters per supercluster (FAT entries per sector)
    def coff(self, c): return self.datastart + (c - 2) * self.csize

def _read_fat(f, g):
    f.seek(g.fat0); raw = f.read(g.fatsz * g.bps)
    return list(struct.unpack('<%dI' % (len(raw) // 4), raw))

def _write_fat(f, g, fat):
    raw = struct.pack('<%dI' % len(fat), *fat)
    for i in range(g.nfats):
        f.seek(g.fat0 + i * g.fatsz * g.bps); f.write(raw)

def craft(image, logs, freefile, stale_from):
    with open(image, 'r+b') as f:
        g = Geo(f)
        fat = _read_fat(f, g)
        if (fat[3] & 0x0FFFFFFF) < 0x0FFFFFF8:
            raise ValueError('LOGS dir expected to be a single cluster at 3 (fat[3]=%#x)' % fat[3])
        # --- root dir: find FREESPAC.E and LOGS ---
        f.seek(g.coff(g.rootc)); root = bytearray(f.read(g.csize))
        ffpos = logspos = None
        for i in range(0, len(root), 32):
            nm = bytes(root[i:i+11])
            if nm.startswith(b'FREESPAC'): ffpos = i
            if nm == b'LOGS       ': logspos = i
        if ffpos is None or logspos is None:
            raise ValueError('image not initialised by SITL (no FREESPAC.E / LOGS)')
        logs_start = (struct.unpack_from('<H', root, logspos + 20)[0] << 16) | struct.unpack_from('<H', root, logspos + 26)[0]
        if logs_start != 3: raise ValueError('LOGS dir at %d, expected 3' % logs_start)
        # --- LOGS dir: keep . and .., rebuild the rest ---
        f.seek(g.coff(3)); d = bytearray(f.read(g.csize))
        tmpl = None
        for i in range(64, len(d), 32):
            if d[i] not in (0, 0xE5) and d[i+11] == 0x20: tmpl = bytes(d[i:i+32]); break
        newd = bytearray(g.csize); newd[0:64] = d[0:64]
        pos = 64
        for (num, start, chain, size) in logs:
            e = bytearray(tmpl) if tmpl else bytearray(32)
            e[0:11] = ('LOG%05dTXT' % num).encode(); e[11] = 0x20
            struct.pack_into('<H', e, 20, start >> 16); struct.pack_into('<H', e, 26, start & 0xFFFF)
            struct.pack_into('<I', e, 28, size)
            if size > chain * g.csize: raise ValueError('log %d size exceeds chain' % num)
            newd[pos:pos+32] = e; pos += 32
        f.seek(g.coff(3)); f.write(newd)
        # --- freefile entry ---
        fstart, fsize = freefile
        struct.pack_into('<H', root, ffpos + 20, fstart >> 16); struct.pack_into('<H', root, ffpos + 26, fstart & 0xFFFF)
        struct.pack_into('<I', root, ffpos + 28, fsize)
        f.seek(g.coff(g.rootc)); f.write(root)
        # --- FAT ---
        for c in range(4, len(fat)): fat[c] = 0
        def chain(start, n):
            for c in range(start, start + n - 1): fat[c] = c + 1
            fat[start + n - 1] = EOC
        occupied = []
        for (num, start, ch, size) in logs:
            chain(start, ch); occupied.append((start, ch))
        fcl = (fsize + g.csize - 1) // g.csize
        if fcl:
            # like afatfs: each supercluster of the freefile is its own EOC-terminated chain
            c = fstart
            while c < fstart + fcl:
                n = min(g.sc, fstart + fcl - c); chain(c, n); c += n
            occupied.append((fstart, fcl))
        occupied.sort()
        for a, b in zip(occupied, occupied[1:]):
            if a[0] + a[1] > b[0]: raise ValueError('crafted layout overlaps: %s %s' % (a, b))
        c = stale_from
        end = g.nclusters + 2
        while c < end:
            n = min(g.sc, end - c); chain(c, n); c += n
        if occupied and occupied[-1][0] + occupied[-1][1] > stale_from: raise ValueError('stale_from inside layout')
        _write_fat(f, g, fat)
    return g

if __name__ == '__main__':
    print(__doc__)
