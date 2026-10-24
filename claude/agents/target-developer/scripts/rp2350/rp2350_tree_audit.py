#!/usr/bin/env python3
"""rp2350_tree_audit.py -- does a draft RP2350/RP2354 target dir hit the known gaps of the
RP2350 port in an INAV tree?  Static greps only; nothing is built.

Usage: rp2350_tree_audit.py <inav_root> <target_dir>
Each line is [GAP], [ok] or [info] with the file:line evidence.  The checks encode problems
found while reviewing RP2354B_FC (2026-10-14); re-run on every new RP2350 target and ADD a
check here whenever a review finds a new class of gap.  They describe the tree as of
inav checkout 1fd4b9d90c (10.x merge branch) and will go stale as the port matures.
"""
import re, sys, os
root, tdir = sys.argv[1], sys.argv[2]
def rd(p):
    try: return open(p, errors='ignore').read()
    except OSError: return ''
def ln(text, pat):
    for i, l in enumerate(text.splitlines(), 1):
        if re.search(pat, l): return i
cm = rd(os.path.join(root, 'cmake/rp2350.cmake'))
th = rd(os.path.join(tdir, 'target.h')); tc = rd(os.path.join(tdir, 'target.c'))
th_nc = re.sub(r'//[^\n]*|/\*.*?\*/', '', th, flags=re.S)
def d(name): return re.search(r'^\s*#\s*define\s+%s\b' % name, th_nc, re.M) is not None
out = []
def gap(s): out.append('[GAP]  ' + s)
def ok(s): out.append('[ok]   ' + s)
def info(s): out.append('[info] ' + s)

# 1 package / flash defines
if re.search(r'PICO_RP2350A=1', cm): gap('cmake/rp2350.cmake:%s hard-codes PICO_RP2350A=1 (30 GPIO, ADC base 26, PIO gpio-base code compiled out). QFN-80 targets need it undefined.' % ln(cm, 'PICO_RP2350A=1'))
m = re.search(r'PICO_FLASH_SIZE_BYTES=(\d+)', cm)
if m: info('cmake/rp2350.cmake:%s PICO_FLASH_SIZE_BYTES=%s (RP2354 internal flash is 2097152; SDK flash_range_* assert against it)' % (ln(cm, 'PICO_FLASH_SIZE_BYTES'), m.group(1)))
if 'MCU_FLASH_SIZE' not in cm: gap('MCU_FLASH_SIZE is not defined for RP2350: target/common.h:441/462 treat the build as <=512 KB (no Spektrum, MAVLink, geozones, 1 mixer profile, no CLI help). TARGET_FLASH_SIZE in target.h is read by nothing.')
ld = rd(os.path.join(root, 'src/main/target/link/rp2350_flash.ld'))
mm = re.search(r'FLASH_CONFIG\(r\)\s*:\s*ORIGIN\s*=\s*(0x[0-9a-fA-F]+)', ld)
if mm: info('linker FLASH_CONFIG origin %s (4 MB part; 2 MB part needs 0x101F0000 and FLASH LENGTH 1984K)' % mm.group(1))
# 2 per-target files
if not os.path.exists(os.path.join(tdir, 'pico/version.h')): gap('target dir lacks pico/version.h (pico.h:27 includes it; only RP2350_PICO ships a hand-written copy)')
if d('USE_TARGET_IMU_HARDWARE_DESCRIPTORS') and 'BUSDEV_REGISTER' not in tc: gap('USE_TARGET_IMU_HARDWARE_DESCRIPTORS set but target.c has no BUSDEV_REGISTER_SPI*: target/common_hardware.c:26 then registers NO IMU -> never detected')
if d('BIND_PIN') and not d('USE_SPEKTRUM_BIND'): gap('BIND_PIN without USE_SPEKTRUM_BIND is dead code (Matek defines both); also dead while MCU_FLASH_SIZE undefined (common.h:464 undefs USE_SERIALRX_SPEKTRUM)')
if not d('USE_ESC_SENSOR'): info('USE_ESC_SENSOR not defined (12/12 Matek define it; it also enables USE_RPM_FILTER via common_post.h)')
# 3 subsystems vs cmake
if d('USE_SDCARD') and 'sdcard' not in cm: gap('USE_SDCARD but cmake/rp2350.cmake has no drivers/sdcard/*.c or io/asyncfatfs/*.c (only cmake/stm32.cmake:44-49,326 and sitl.cmake add them) -> blackbox/SD link errors')
if d('USE_USB_DETECT') or d('USB_DETECT_PIN'): info('USB_DETECT: usb_io.c is not in rp2350.cmake, and usbCableDetectInit/usbCableIsInserted have no callers anywhere in the tree: the define is a no-op')
if d('USE_PINIO'):
    gap('USE_PINIO: drivers/pinio.c is compiled for RP2350 but calls timerGetByTag/timerGetTCH/timerConfigBase/timerPWM*/timerEnable/timerCCR which live in drivers/timer.c (excluded in rp2350.cmake RP2350_COMMON_SRC_EXCLUDES) -> undefined references; also ws2811SetIdleHigh (pinio.c:199) is not in light_ws2811strip_rp2350.c when USE_LED_STRIP')
if d('USE_ADC'):
    ad = rd(os.path.join(root, 'src/main/drivers/adc_rp2350.c'))
    if re.search(r'ADC_BASE_GPIO\s+26u', ad): gap('adc_rp2350.c:%s ADC_BASE_GPIO 26u, 4 channels, adc_gpio_init(26..29); ADC_CHANNEL_n_PIN macros are not read. On a QFN-80 board this disables GP26-29 digital functions and never isolates GP40+.' % ln(ad, 'ADC_BASE_GPIO'))
if d('BEEPER') and 'beeperPwmInit' in rd(os.path.join(root, 'src/main/drivers/pwm_output_rp2350.c')): info('beeper PWM (passive buzzer, BEEPER_PWM_FREQUENCY) is a stub returning false in pwm_output_rp2350.c; only GPIO on/off works. IOCFG_OUT_OD == push-pull on RP2350.')
tm = rd(os.path.join(root, 'src/main/drivers/timer.h'))
n_tim = len(set(re.findall(r'DEF_TIM\(\s*(\w+)', tc)))
mm = re.search(r'RP2350\)\s*\n#define HARDWARE_TIMER_DEFINITION_COUNT (\d+)', tm)
if mm and n_tim > int(mm.group(1)): gap('target.c uses %d PWM slice tokens but timer.h HARDWARE_TIMER_DEFINITION_COUNT is %s (and timer_rp2350.c timer2id() knows only TIM4/5/6/7/10)' % (n_tim, mm.group(1)))
elif mm: info('PWM slice tokens in use: %d of HARDWARE_TIMER_DEFINITION_COUNT %s' % (n_tim, mm.group(1)))
w = rd(os.path.join(root, 'src/main/drivers/light_ws2811strip_rp2350.c'))
if d('USE_LED_STRIP') and re.search(r'OSD_\w*_PIN', th_nc): info('LED strip (PIO2) and an OSD sharing PIO2: light_ws2811strip_rp2350.c:%s only sets pio_set_gpio_base(16) for its own pin >=32 and ignores the return value; fc_init.c inits OSD (line ~631-639) before ledStripInit (~658), so whichever loads a PIO2 program first decides the base.' % ln(w, 'gpio >= 32'))
if d('HARDWARE_TIMER_DEFINITION_COUNT'): pass
if re.search(r'set_sys_clock_khz\((\d+)', rd(os.path.join(root, 'src/main/drivers/system_rp2350.c'))): info('system_rp2350.c sets sys clock to 192 MHz; datasheet maximum is 150 MHz (RP2350 datasheet 1.x / 8.1)')
if not d('USE_HARDWARE_PREBOOT_SETUP') and (d('PINIO1_PIN')): info('PINIO pins default LOW (pinio.c GPIO fallback) until a box is bound; use USE_HARDWARE_PREBOOT_SETUP + hardware_setup.c (KROOZX pattern) if a pin needs an early defined level')
print('\n'.join(out))
