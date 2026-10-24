#!/usr/bin/env python3
"""Build rp2350-gpio-functions.tsv (GPIO0-47 x F0-F11) from the RP2350 datasheet text.

Input: `pdftotext -layout RP-008373-DS-2-rp2350-datasheet.pdf rp2350.txt` (the PDF is in
~/Documents/planes/rpi_pico_2350_port/, also reachable as claude/developer/docs/targets/rp2350/).
Source table: datasheet "Table 3. General Purpose Input/Output (GPIO) Bank 0 Functions"
(section 1.2.3; same data as Table 645 in the GPIO chapter). GPIO30-47 are QFN-80 (B) only;
ADC is GPIO26-29 on QFN-60 (A) and GPIO40-47 on QFN-80 (B) (datasheet note after Table 4).

Usage: build_gpio_table.py rp2350.txt > rp2350-gpio-functions.tsv
Function slots are assigned by name pattern because blank cells make column positions
unreliable in the text layout: F1 SPI, F2 first UART, F3 I2C, F4 PWM, F5 SIO, F6-F8 PIO0-2,
F9 QMI/TRACE/CLOCK, F10 USB, F11 second UART entry, F0 HSTX.
"""
import re, sys
txt = open(sys.argv[1], errors='ignore').read().splitlines()
start = next(i for i, l in enumerate(txt) if 'Table 3. General' in l)
end = next(i for i, l in enumerate(txt) if i > start and 'Table 4. GPIO bank 0' in l)
rows = {}
for l in txt[start:end]:
    m = re.match(r'^\s*(\d{1,2})\s{2,}(\S.*)$', l)
    if not m:
        continue
    g = int(m.group(1))
    if g > 47 or g in rows:
        continue
    toks = [t.strip() for t in re.split(r'\s{2,}', m.group(2).strip()) if t.strip()]
    # GPIO label lines inside the first row of a page may start with a pin number only; skip junk
    if not any(t.startswith(('SPI', 'UART', 'I2C', 'PWM')) for t in toks):
        continue
    f = [''] * 12
    uarts = []
    for t in toks:
        if t == 'HSTX': f[0] = t
        elif t.startswith('SPI'): f[1] = t
        elif t.startswith('UART'): uarts.append(t)
        elif t.startswith('I2C'): f[3] = t
        elif t.startswith('PWM'): f[4] = t
        elif t == 'SIO': f[5] = t
        elif t in ('PIO0', 'PIO1', 'PIO2'): f[6 + int(t[-1])] = t
        elif t.startswith(('QMI', 'TRACE', 'CLOCK')): f[9] = t
        elif t.startswith('USB'): f[10] = t
    if uarts: f[2] = uarts[0]
    if len(uarts) > 1: f[11] = uarts[1]
    rows[g] = f
print('gpio\t' + '\t'.join('F%d' % i for i in range(12)))
for g in sorted(rows):
    print('%d\t%s' % (g, '\t'.join(rows[g])))
missing = [g for g in range(48) if g not in rows]
if missing:
    sys.stderr.write('WARNING: missing rows %s\n' % missing)
