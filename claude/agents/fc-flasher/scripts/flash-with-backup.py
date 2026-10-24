#!/usr/bin/env python3
"""
Brief: Back up an INAV FC's config over CLI, reboot it to DFU with the CLI 'dfu'
       command, flash it without erasing settings, and wait for it to come back.
Usage: flash-with-backup.py <firmware.hex> [serial_port] [--backup-dir DIR]
Example: flash-with-backup.py ~/inavflight/inav2/build_review/inav_10.0.0_SKYSTARSF405V2.hex /dev/ttyACM0

What problem this solves: flashing used to be several manual steps, and the settings were
only protected by the flasher's selective page erase. This takes a text backup first
('diff all' + 'version'), so a bad flash or a config-format change can be recovered.
When to use it: any time the FC is running (not already in DFU mode). If the FC is
already in DFU mode there is nothing to back up; the script says so and flashes anyway.

Steps:
  1. If 0483:df11 (or AT32 2e3c:df11) is already present: skip to flashing, warn no backup.
  2. Else enter CLI on the serial port, save 'version' and 'diff all' to the backup dir.
     Abort (no flash) if the backup is missing or implausibly short, unless --no-backup.
  3. Send 'dfu' and wait up to 15 s for the DFU device.
  4. Run flash-dfu-node.js (selective page erase, verify, reboot).
  5. Wait for a /dev/ttyACM* or /dev/ttyUSB* port to reappear and report it.

Needs hardware access: run outside the sandbox (serial + USB).
Dependencies: pyserial, dfu-util, node with node-usb installed in claude/developer/scripts/build.
"""

import argparse
import datetime
import glob
import os
import re
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
FLASHER = os.path.join(REPO, 'claude', 'developer', 'scripts', 'build', 'flash-dfu-node.js')
DEFAULT_BACKUP_DIR = os.path.join(REPO, 'claude', 'developer', 'workspace', 'fc-backups')
DFU_IDS = ('0483:df11', '2e3c:df11')


def dfu_present():
    try:
        out = subprocess.run(['dfu-util', '-l'], capture_output=True, text=True, timeout=10).stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return any(i in out for i in DFU_IDS)


def read_until_quiet(ser, quiet=1.5, limit=60):
    data = b''
    start = last = time.time()
    while time.time() - start < limit:
        n = ser.in_waiting
        if n:
            data += ser.read(n)
            last = time.time()
        elif time.time() - last > quiet:
            break
        time.sleep(0.05)
    return data.decode('ascii', errors='replace')


def backup_config(port, backup_dir):
    import serial
    ser = serial.Serial(port, 115200, timeout=0.5)
    try:
        time.sleep(0.2)
        ser.reset_input_buffer()
        ser.write(b'####\r\n')
        ser.flush()
        banner = read_until_quiet(ser, quiet=0.8, limit=5)
        if 'CLI' not in banner and '#' not in banner:
            raise RuntimeError('no CLI prompt: ' + banner[-200:])
        ser.write(b'version\r\n')
        version = read_until_quiet(ser, quiet=0.8, limit=5)
        ser.write(b'diff all\r\n')
        diff = read_until_quiet(ser, quiet=2.0, limit=90)
    except Exception:
        ser.close()
        raise
    # Leave the serial port open for the 'dfu' command
    return ser, version, diff


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('hex')
    ap.add_argument('port', nargs='?', default='/dev/ttyACM0')
    ap.add_argument('--backup-dir', default=DEFAULT_BACKUP_DIR)
    ap.add_argument('--no-backup', action='store_true', help='flash even if the backup fails')
    args = ap.parse_args()

    if not os.path.isfile(args.hex):
        sys.exit(f'ERROR: hex file not found: {args.hex}')

    if dfu_present():
        print('FC is already in DFU mode: no backup possible, skipping to flash.')
    else:
        try:
            ser, version, diff = backup_config(args.port, args.backup_dir)
        except Exception as e:
            print(f'Backup failed: {e}')
            if not args.no_backup:
                sys.exit('Aborting before flashing. Re-run with --no-backup to flash anyway.')
            ser = None
            version = diff = ''
        if ser is not None:
            name = re.search(r'INAV/(\w+)', version)
            tag = name.group(1) if name else 'fc'
            os.makedirs(args.backup_dir, exist_ok=True)
            path = os.path.join(args.backup_dir, '%s-%s.txt' % (tag, datetime.datetime.now().strftime('%Y%m%d-%H%M%S')))
            ok = diff.count('\n') > 20    # a real 'diff all' is far longer; a short reply is an error
            with open(path, 'w') as f:
                f.write(version + '\n' + diff)
            print(f'Backup written: {path} ({diff.count(chr(10))} lines)')
            if not ok and not args.no_backup:
                ser.close()
                sys.exit('Backup looks incomplete. Aborting before flashing.')
            print('Sending dfu command...')
            ser.write(b'dfu\r\n')
            ser.flush()
            time.sleep(0.3)
            ser.close()
            for _ in range(15):
                time.sleep(1)
                if dfu_present():
                    break
            else:
                sys.exit('ERROR: FC did not appear in DFU mode within 15 s.')

    print('Flashing (settings preserved: only firmware pages are erased)...')
    rc = subprocess.call(['node', FLASHER, args.hex])
    if rc != 0:
        sys.exit(f'ERROR: flasher exited with {rc}')

    for _ in range(20):
        time.sleep(1)
        ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
        if ports:
            print('SUCCESS: FC is back as ' + ', '.join(ports))
            return
    sys.exit('WARNING: flash finished but no serial port reappeared within 20 s.')


if __name__ == '__main__':
    main()
