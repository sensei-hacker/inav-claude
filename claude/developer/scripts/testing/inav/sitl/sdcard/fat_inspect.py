#!/usr/bin/env python3
"""Small pure-python FAT32 inspector (FAT copy #1 only; afatfs never writes copy #2).
Image must have an MBR with one partition. Usage: fat_inspect.py <image>  (prints JSON)."""
import json, struct, sys

def _chain(fat, start, limit):
    out, c = [], start
    while 2 <= c < limit and len(out) <= limit:
        out.append(c)
        c = fat[c] & 0x0FFFFFFF
        if c >= 0x0FFFFFF8 or c < 2:
            break
    return out

def inspect(path):
    f = open(path, 'rb')
    mbr = f.read(512)
    if mbr[510:512] != b'\x55\xaa':
        raise ValueError("no MBR signature")
    pstart = struct.unpack_from('<I', mbr, 446 + 8)[0] * 512
    f.seek(pstart); bpb = f.read(512)
    bps, spc, rsv, nfats = struct.unpack_from('<HBHB', bpb, 11)
    fatsz = struct.unpack_from('<I', bpb, 36)[0]
    total = struct.unpack_from('<I', bpb, 32)[0]
    rootc = struct.unpack_from('<I', bpb, 44)[0]
    csize = bps * spc
    datastart = pstart + (rsv + nfats * fatsz) * bps
    nclusters = (total - rsv - nfats * fatsz) // spc
    f.seek(pstart + rsv * bps); rawfat = f.read(fatsz * bps)
    fat = struct.unpack('<%dI' % (len(rawfat) // 4), rawfat)
    limit = nclusters + 2
    def readc(c):
        f.seek(datastart + (c - 2) * csize); return f.read(csize)
    def readdir(start):
        ents, data = [], b''
        for c in _chain(fat, start, limit): data += readc(c)
        for i in range(0, len(data), 32):
            e = data[i:i+32]
            if e[0] == 0: break
            if e[0] == 0xE5 or e[11] == 0x0F or (e[11] & 0x08): continue
            hi, = struct.unpack_from('<H', e, 20); lo, = struct.unpack_from('<H', e, 26)
            ents.append({'name': e[:11].decode('latin1').strip(), 'attr': e[11],
                         'start': (hi << 16) | lo, 'size': struct.unpack_from('<I', e, 28)[0]})
        return ents
    root = readdir(rootc)
    r = {'csize': csize, 'nclusters': nclusters, 'fat0': fat[0], 'fat1': fat[1],
         'rootchain': _chain(fat, rootc, limit), 'logs': [], 'freefile': None, 'dirs': []}
    for e in root:
        if e['name'].startswith('FREESPAC'):
            r['freefile'] = e
        if e['name'] == 'LOGS' and e['attr'] & 0x10:
            r['logsdirchain'] = _chain(fat, e['start'], limit)
            for g in readdir(e['start']):
                if g['name'] not in ('.', '..') and g['start']:
                    g['clusters'] = (g['size'] + csize - 1) // csize
                    g['chain_len'] = len(_chain(fat, g['start'], limit))
                    r['logs'].append(g)
    r['rootfiles'] = [e for e in root if not e['attr'] & 0x10 and not e['name'].startswith('FREESPAC') and e['start']]
    ff = r['freefile']
    if ff:
        ff['clusters'] = ff['size'] // csize
    # extents (start, count, label) for everything that owns clusters
    ext = [(c, 1, 'dir') for c in r['rootchain'] + r.get('logsdirchain', [])]
    ext += [(g['start'], g['clusters'], g['name']) for g in r['logs']]
    if ff: ext.append((ff['start'], ff['clusters'], 'FREEFILE'))
    ext += [(e['start'], (e['size'] + csize - 1) // csize, e['name']) for e in r['rootfiles']]
    ext.sort()
    r['extents'] = ext
    # violations
    v = []
    if (r['fat0'] & 0x0FFFFFFF) < 0x0FFFFFF8: v.append('FAT[0] damaged')
    for a, b in zip(ext, ext[1:]):
        if a[0] + a[1] > b[0]: v.append('overlap %s/%s' % (a[2], b[2]))
    for g in r['logs']:
        if g['size'] and g['chain_len'] < g['clusters']: v.append('short chain ' + g['name'])
    names = [g['name'] for g in r['logs']]
    if len(names) != len(set(names)): v.append('duplicate names')
    r['violations'] = v
    # stranded = clusters between extents (gaps), ignoring the region before first extent
    gaps = [(a[0] + a[1], b[0] - (a[0] + a[1])) for a, b in zip(ext, ext[1:]) if b[0] > a[0] + a[1]]
    r['gaps'] = gaps
    # Excess stranded: a log ends mid-supercluster, so (-end mod 128) clusters of slack after
    # every log is normal. Anything beyond that in a gap after a LOG file is genuinely stranded.
    SC = 128
    excess = []
    for a, b in zip(ext, ext[1:]):
        end = a[0] + a[1]
        if a[2].startswith('LOG') and b[0] > end:
            ex = (b[0] - end) - ((-end) % SC)  # superclusters are aligned to cluster numbers that are multiples of SC
            if ex > 0: excess.append((end, ex, a[2]))
    r['excess'] = excess
    r['excess_clusters'] = sum(e for _, e, _ in excess)
    r['stranded_clusters'] = sum(n for _, n in gaps)
    return r

if __name__ == '__main__':
    r = inspect(sys.argv[1]); r.pop('extents'); print(json.dumps(r, indent=1))
