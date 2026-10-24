#!/usr/bin/env python3
"""compare_matek_macros.py -- which macros do the 12 MATEK* targets define that a draft target.h lacks?

Usage: compare_matek_macros.py <inav_root> <draft_target.h> [min_count=6] [--glob 'MATEK*']
Prints (1) macros defined by >= min_count of the reference targets (default: all 12 MATEK*)
and absent from the draft, (2) a count table for a fixed list of feature macros.
Counts consider target.h and target.c/config.c of each reference target (comments stripped for
(1), raw text for (2)).  Use --glob to compare against another family (e.g. 'KROOZX', 'AIKON*').
Origin: RP2354B_FC review 2026-10-14 (Matek counts: USB_DETECT_PIN 3, VBUS_SENSING_PIN 5,
PINIO1_PIN 8, USE_MAX7456 10, USE_ESC_SENSOR 12, BEEPER_INVERTED 12, USE_SDCARD 9).
"""
import re, glob, os, sys, collections
args = [a for a in sys.argv[1:] if not a.startswith('--')]
root, draft = args[0], args[1]
minc = int(args[2]) if len(args) > 2 else 6
pat = 'MATEK*'
if '--glob' in sys.argv: pat = sys.argv[sys.argv.index('--glob') + 1]
def macros(path):
    s = re.sub(r'/\*.*?\*/', '', open(path, errors='ignore').read(), flags=re.S)
    return set(m.group(2) for m in re.finditer(r'^\s*#\s*(define|undef)\s+([A-Za-z_0-9]+)', s, re.M))
dirs = sorted(glob.glob(os.path.join(root, 'src/main/target', pat) + '/'))
d = macros(draft)
cnt = collections.Counter()
for t in dirs:
    m = set()
    for f in glob.glob(t + '*.h'): m |= macros(f)
    for k in m: cnt[k] += 1
print('%d reference targets (%s)' % (len(dirs), pat))
print('--- defined by >=%d reference targets, missing from draft:' % minc)
for k, c in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
    if c >= minc and k not in d: print('%2d  %s' % (c, k))
names = ['USB_DETECT_PIN', 'USE_USB_DETECT', 'VBUS_SENSING_PIN', 'PINIO1_PIN', 'PINIO2_PIN', 'BIND_PIN', 'USE_SPEKTRUM_BIND', 'USE_SDCARD',
         'SDCARD_DETECT_PIN', 'LED1', 'BEEPER', 'BEEPER_INVERTED', 'BEEPER_PWM_FREQUENCY', 'AIRSPEED_ADC_CHANNEL', 'USE_MAX7456', 'USE_ESC_SENSOR',
         'USE_FLASHFS', 'USE_DUAL_GYRO', 'USE_SOFTSERIAL1', 'CURRENT_METER_SCALE', 'VBAT_SCALE_DEFAULT', 'USE_SERIAL_4WAY_BLHELI_INTERFACE',
         'ENABLE_BLACKBOX_LOGGING_ON_SDCARD_BY_DEFAULT', 'USE_TARGET_IMU_HARDWARE_DESCRIPTORS', 'USE_DSHOT_DMAR', 'DEFAULT_FEATURES']
print('--- counts (raw text of *.h and *.c per target):')
for n in names:
    c = 0
    for t in dirs:
        s = ''.join(open(f, errors='ignore').read() for f in glob.glob(t + '*.[hc]'))
        if re.search(r'#\s*define\s+' + n + r'\b', s): c += 1
    print('%3d/%d  %s' % (c, len(dirs), n))
