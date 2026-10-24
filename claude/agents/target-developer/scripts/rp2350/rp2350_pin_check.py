#!/usr/bin/env python3
"""rp2350_pin_check.py -- static pin/peripheral checks for an INAV RP2350/RP2354 target.

Usage: rp2350_pin_check.py <path/to/target_dir> [--package A|B]
  (target_dir contains target.h / target.c; it need not be inside the inav tree.)

Checks (each finding is tagged; nothing is a pass/fail gate, a human reads the output):
  PIN_FUNC   SPIn_SCK/MOSI/MISO, I2Cn_SDA/SCL, UART1/2 TX/RX (hardware UARTs) really carry
             that function on that GPIO (rp2350-gpio-functions.tsv, from datasheet Table 3),
             all three pins of a bus are on the SAME instance, and the instance matches what
             the INAV driver will choose (bus_spi_rp2350.c: (gpio>>3)&1 -> spi1;
             bus_i2c_rp2350.c: (gpio/2)&1 -> i2c1).
  PIO_RANGE  PIO1 (PIO UART3/4) and PIO0 (DShot) are hard-wired to GPIO base 0 in the INAV
             drivers: pins must be <32.  PIO2 (LED strip / OSD) needs GPIOBASE 16 as soon as
             any user needs a pin >=32, and then EVERY pin on it must be >=16.
  ADC        ADC_CHANNEL_n_PIN must be GPIO(26+n-1) on A, GPIO(40+n-1) on B.  NOTE: the INAV
             driver (adc_rp2350.c) ignores these macros and is positional (ADC_CHN_n = ADC(n-1)).
  PWM_SLICE  hardware slice/channel of every timerHardware[] pin (SDK pwm.h formula) and
             other used pins sharing that slice+channel (only a conflict if both are PWM).
  PIN_REUSE  one GPIO named by several macros.
Pin naming in INAV RP2350: P<A|B|C><n> = GPIO (port*16 + n), A=0,B=1,C=2.
"""
import re, sys, os
here = os.path.dirname(os.path.abspath(__file__))
tsv = [l.rstrip('\n').split('\t') for l in open(os.path.join(here, 'rp2350-gpio-functions.tsv'))][1:]
FUNC = {int(r[0]): r[1:] for r in tsv}

def gp(pin):
    m = re.fullmatch(r'P([ABC])(\d{1,2})', pin)
    return ('ABC'.index(m.group(1)) * 16 + int(m.group(2))) if m else None

def strip_comments(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    return re.sub(r'//[^\n]*', '', s)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    d = args[0]
    th = strip_comments(open(os.path.join(d, 'target.h'), errors='ignore').read())
    tc = strip_comments(open(os.path.join(d, 'target.c'), errors='ignore').read()) if os.path.exists(os.path.join(d, 'target.c')) else ''
    defs = dict(re.findall(r'^\s*#\s*define\s+(\w+)\s+(P[ABC]\d{1,2})\b', th, flags=re.M))
    allnums = {k: gp(v) for k, v in defs.items()}
    pkg = None
    for a in sys.argv[1:]:
        if a.startswith('--package'):
            pkg = a.split('=')[-1] if '=' in a else None
    if pkg is None:
        pkg = 'B' if any(v >= 30 for v in allnums.values()) else 'A'
    print('package assumed: %s' % pkg)
    out = []
    def F(g): return FUNC[g]
    def has(g, name): return any(name == x for x in F(g))
    # ---- buses
    for n, bus in ((1, 'SPI'), (2, 'SPI')):
        k = [f'SPI{n}_SCK_PIN', f'SPI{n}_MOSI_PIN', f'SPI{n}_MISO_PIN']
        if all(x in allnums for x in k):
            want = [('SCK', allnums[k[0]]), ('TX', allnums[k[1]]), ('RX', allnums[k[2]])]
            inst = set()
            for sig, g in want:
                m = [x for x in F(g) if re.fullmatch(r'SPI\d %s' % sig, x)]
                if not m: out.append('PIN_FUNC  SPI%d %s on GP%d: no SPI %s function (has %s)' % (n, sig, g, sig, [x for x in F(g) if x]))
                else: inst.add(m[0][3])
            if len(inst) > 1: out.append('PIN_FUNC  SPI%d pins span several RP2350 SPI instances %s' % (n, sorted(inst)))
            drv = '1' if (allnums[k[0]] >> 3) & 1 else '0'
            if inst and drv not in inst: out.append('PIN_FUNC  driver would pick spi%s for SCK GP%d but pins are SPI%s' % (drv, allnums[k[0]], sorted(inst)))
            elif inst: out.append('ok        INAV SPI%d -> rp2350 spi%s (GP%s)' % (n, drv, [g for _, g in want]))
    k = ['I2C1_SDA', 'I2C1_SCL']
    for n in (1, 2):
        k = ['I2C%d_SDA' % n, 'I2C%d_SCL' % n]
        if all(x in allnums for x in k):
            inst = set()
            for sig, x in (('SDA', k[0]), ('SCL', k[1])):
                g = allnums[x]
                m = [y for y in F(g) if re.fullmatch(r'I2C\d %s' % sig, y)]
                if not m: out.append('PIN_FUNC  I2C%d %s on GP%d: no I2C %s function' % (n, sig, g, sig))
                else: inst.add(m[0][3])
            drv = '1' if (allnums[k[0]] // 2) & 1 else '0'
            if len(inst) > 1: out.append('PIN_FUNC  I2C%d SDA/SCL on different instances' % n)
            if inst and drv not in inst: out.append('PIN_FUNC  driver would pick i2c%s, pins are I2C%s' % (drv, sorted(inst)))
            elif inst: out.append('ok        INAV I2C%d -> rp2350 i2c%s' % (n, drv))
    for n in (1, 2):   # hardware UARTs only: INAV UART1->uart0, UART2->uart1
        for sig in ('TX', 'RX'):
            x = 'UART%d_%s_PIN' % (n, sig)
            if x in allnums:
                g = allnums[x]
                want = 'UART%d %s' % (n - 1, sig)
                if not has(g, want): out.append('PIN_FUNC  %s=GP%d does not carry %s (has %s)' % (x, g, want, [y for y in F(g) if y.startswith('UART')]))
                else:
                    slot = 'F11' if F(g)[11] == want else 'F2'
                    out.append('ok        %s=GP%d %s on %s' % (x, g, want, slot))
    # ---- PIO ranges
    pio_users = {0: [], 1: [], 2: []}
    for m in re.finditer(r'DEF_TIM\(\s*\w+\s*,\s*\w+\s*,\s*(P[ABC]\d+)', tc):
        pio_users[0].append(('DShot-capable output', gp(m.group(1))))   # only motors use PIO0
    for n in (3, 4):
        for sig in ('TX', 'RX'):
            x = 'UART%d_%s_PIN' % (n, sig)
            if x in allnums: pio_users[1].append((x, allnums[x]))
    if 'WS2811_PIN' in allnums:
        idx = int((re.search(r'#\s*define\s+PIO_LEDSTRIP_INDEX\s+(\d)', th) or [0, 2])[1])
        pio_users[idx].append(('WS2811_PIN', allnums['WS2811_PIN']))
    for x, g in allnums.items():
        if x.startswith('OSD_') and x.endswith('_PIN'): pio_users[2].append((x, g))
    for p in (0, 1):
        for x, g in pio_users[p]:
            if g >= 32: out.append('PIO_RANGE PIO%d user %s on GP%d: INAV driver uses GPIO base 0 (pins 0-31 only)' % (p, x, g))
    hi = [(x, g) for x, g in pio_users[2] if g >= 32]
    lo = [(x, g) for x, g in pio_users[2] if g < 16]
    if hi: out.append('PIO_RANGE PIO2 needs GPIOBASE=16 (pins >=32: %s). Must be set BEFORE the first pio_add_program on PIO2 (pio_set_gpio_base fails with INVALID_STATE otherwise); fc_init.c initialises OSD before ledStripInit.' % hi)
    if hi and lo: out.append('PIO_RANGE PIO2 base 16 cannot reach GP<16: %s' % lo)
    # ---- ADC
    base = 26 if pkg == 'A' else 40
    for n in range(1, 9):
        x = 'ADC_CHANNEL_%d_PIN' % n
        if x in allnums and allnums[x] != base + n - 1:
            out.append('ADC       %s=GP%d but ADC%d is GP%d on package %s' % (x, allnums[x], n - 1, base + n - 1, pkg))
        elif x in allnums:
            out.append('ok        %s=GP%d is ADC%d' % (x, allnums[x], n - 1))
    # ---- PWM
    seen = {}
    for m in re.finditer(r'DEF_TIM\(\s*(\w+)\s*,\s*(\w+)\s*,\s*(P[ABC]\d+)', tc):
        g = gp(m.group(3)); sl = ((g >> 1) & 7) if g < 32 else 8 + ((g >> 1) & 3)
        seen[g] = (sl, 'AB'[g & 1])
    used = {g: x for x, g in allnums.items()}
    for g, (sl, ch) in sorted(seen.items()):
        mates = [(x, h) for h, x in used.items() if h != g and h in range(48) and ((((h >> 1) & 7) if h < 32 else 8 + ((h >> 1) & 3)), 'AB'[h & 1]) == (sl, ch)]
        out.append('PWM_SLICE GP%d -> hw slice %d ch %s%s' % (g, sl, ch, ('; same slice+ch as ' + ', '.join('%s(GP%d)' % m for m in mates)) if mates else ''))
    # ---- reuse
    byg = {}
    for x, g in allnums.items(): byg.setdefault(g, []).append(x)
    for g, xs in sorted(byg.items()):
        if len(xs) > 1: out.append('PIN_REUSE GP%d: %s' % (g, ', '.join(xs)))
    print('\n'.join(out))
main()
