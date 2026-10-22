#!/usr/bin/env python3
"""Shrink INAV's FREESPAC.E freefile directory entry on a card exposed as a block device (FC in `msc` mode, or a reader),
so a bench run reaches the wraparound split in minutes instead of hours (a 4 GB freefile at ~100 KB/s takes ~11 h).
Only the 4-byte size field of that one directory entry is changed. The FAT chain is left alone (afatfs treats the
freefile as a contiguous range from the dirent's start cluster + size, and its own relocation leaves the old chain stale too).
The original 512-byte sector is saved to --backup; `--restore` writes it back. Never touches LOG files.
Usage: shrink_freefile.py /dev/sdX --superclusters 3 [--dry-run]    |  shrink_freefile.py /dev/sdX --restore"""
import argparse, os, struct, sys, json

def locate(dev):
    f = open(dev, 'rb'); mbr = f.read(512)
    if mbr[510:512] != b'\x55\xaa': raise SystemExit('FAIL no MBR on %s' % dev)
    pstart = struct.unpack_from('<I', mbr, 446 + 8)[0] * 512
    f.seek(pstart); b = f.read(512)
    bps, spc, rsv, nf = struct.unpack_from('<HBHB', b, 11); fatsz = struct.unpack_from('<I', b, 36)[0]; rootc = struct.unpack_from('<I', b, 44)[0]
    csize = bps * spc; data = pstart + (rsv + nf * fatsz) * bps
    f.seek(pstart + rsv * bps); fat = struct.unpack('<%dI' % (fatsz * bps // 4), f.read(fatsz * bps))
    c = rootc
    while 2 <= c < 0x0FFFFFF8:
        base = data + (c - 2) * csize; f.seek(base); blk = f.read(csize)
        for i in range(0, csize, 32):
            e = blk[i:i + 32]
            if e[0] == 0: break
            if e[:8] == b'FREESPAC' and e[0] != 0xE5:
                start = (struct.unpack_from('<H', e, 20)[0] << 16) | struct.unpack_from('<H', e, 26)[0]
                return base + i, struct.unpack_from('<I', e, 28)[0], start, csize, spc
        c = fat[c] & 0x0FFFFFFF
    raise SystemExit('FAIL FREESPAC.E not found in root dir')

ap = argparse.ArgumentParser(); ap.add_argument('dev'); ap.add_argument('--superclusters', type=int, default=4)
ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--restore', action='store_true')
ap.add_argument('--backup', default=os.path.join(os.environ.get('TMPDIR', '.'), 'freefile_dirent_backup.json'))
a = ap.parse_args()
off, size, start, csize, spc = locate(a.dev)
print('freefile dirent at byte %d: start cluster %d, size %d bytes (%.1f MB)' % (off, start, size, size / 1e6))
if a.restore:
    bk = json.load(open(a.backup)); new = bk['size']
else:
    sc = 128 * csize  # INAV supercluster = FAT32 entries per FAT sector (128) clusters
    new = a.superclusters * sc
    if new >= size: raise SystemExit('FAIL requested size %d >= current %d' % (new, size))
print('new size: %d bytes (%.1f MB)%s' % (new, new / 1e6, ' [dry run]' if a.dry_run else ''))
if a.dry_run: sys.exit(0)
if not a.restore: json.dump({'dev_offset': off, 'size': size}, open(a.backup, 'w'))
fd = os.open(a.dev, os.O_RDWR | os.O_SYNC)
os.lseek(fd, off + 28, os.SEEK_SET); n = os.write(fd, struct.pack('<I', new)); os.fsync(fd)
assert n == 4
os.lseek(fd, off + 28, os.SEEK_SET); assert struct.unpack('<I', os.read(fd, 4))[0] == new; os.close(fd)
print('OK  wrote and verified; original size saved in', a.backup)
