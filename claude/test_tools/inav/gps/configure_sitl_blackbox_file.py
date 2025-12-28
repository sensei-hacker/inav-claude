#!/usr/bin/env python3
"""
Configure SITL for FILE Blackbox Logging

Sets up SITL to log navEPH data to .TXT file at 500 Hz.

Usage:
    python3 configure_sitl_blackbox_file.py --port 5760 --rate-denom 2
"""

import sys
import time
import struct
import argparse
from mspapi2 import MSPApi

# MSP commands
MSP_EEPROM_WRITE = 250
MSP_REBOOT = 68
MSP2_COMMON_SET_SETTING = 0x1004

# Debug modes
DEBUG_POS_EST = 20  # Position estimator (navEPH is in debug[7])

# Blackbox settings
BLACKBOX_DEVICE_FILE = 3
BLACKBOX_RATE_NUM = 1


def set_setting(api, name, value):
    """Set a configuration setting via MSP2_COMMON_SET_SETTING."""
    setting_name = name.encode('ascii') + b'\0'

    # Determine value format based on type
    if isinstance(value, bool):
        payload = setting_name + struct.pack('<B', 1 if value else 0)
    elif isinstance(value, int):
        if -128 <= value <= 127:
            payload = setting_name + struct.pack('<b', value)
        elif 0 <= value <= 255:
            payload = setting_name + struct.pack('<B', value)
        elif -32768 <= value <= 32767:
            payload = setting_name + struct.pack('<h', value)
        else:
            payload = setting_name + struct.pack('<i', value)
    else:
        raise ValueError(f"Unsupported value type: {type(value)}")

    api._serial.send(MSP2_COMMON_SET_SETTING, payload)
    time.sleep(0.1)


def main():
    parser = argparse.ArgumentParser(description='Configure SITL for FILE blackbox logging')
    parser.add_argument('--port', type=int, default=5760,
                        help='MSP port (default: 5760)')
    parser.add_argument('--rate-denom', type=int, default=2,
                        help='Blackbox rate denominator (default: 2 = 500 Hz)')

    args = parser.parse_args()

    logging_rate = 1000 // args.rate_denom

    print("=" * 70)
    print("SITL Blackbox FILE Configuration")
    print("=" * 70)
    print()
    print(f"MSP Port:           {args.port}")
    print(f"Blackbox Device:    FILE")
    print(f"Blackbox Rate:      {BLACKBOX_RATE_NUM}/{args.rate_denom} ({logging_rate} Hz @ 1000 Hz PID)")
    print(f"Debug Mode:         DEBUG_POS_EST ({DEBUG_POS_EST})")
    print(f"Output Location:    build_sitl/YYYY_MM_DD_HHMMSS.TXT")
    print()

    try:
        # Connect to SITL
        api = MSPApi(tcp_endpoint=f'localhost:{args.port}')
        api.open()
        time.sleep(0.5)
        print("✓ Connected to SITL")
        print()

        # Configure blackbox settings
        print("Configuring blackbox...")

        set_setting(api, 'blackbox_device', BLACKBOX_DEVICE_FILE)
        print(f"  ✓ blackbox_device = FILE ({BLACKBOX_DEVICE_FILE})")

        set_setting(api, 'blackbox_rate_num', BLACKBOX_RATE_NUM)
        print(f"  ✓ blackbox_rate_num = {BLACKBOX_RATE_NUM}")

        set_setting(api, 'blackbox_rate_denom', args.rate_denom)
        print(f"  ✓ blackbox_rate_denom = {args.rate_denom}")

        # Set debug mode
        print()
        print("Configuring debug mode...")
        set_setting(api, 'debug_mode', DEBUG_POS_EST)
        print(f"  ✓ debug_mode = DEBUG_POS_EST ({DEBUG_POS_EST})")

        print()
        print("Saving configuration...")
        api._serial.send(MSP_EEPROM_WRITE, b'')
        time.sleep(1.0)
        print("  ✓ Configuration saved")

        print()
        print("Rebooting SITL...")
        api._serial.send(MSP_REBOOT, b'')
        time.sleep(0.5)
        print("  ✓ Reboot command sent")

        api.close()

        print()
        print("=" * 70)
        print("Configuration Complete")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Wait 10s for SITL to reboot")
        print("2. Enable BLACKBOX feature (if not already enabled)")
        print("3. Run: python3 claude/test_tools/inav/gps/run_gps_blackbox_test.sh climb 60")
        print("4. Check build_sitl/ for .TXT file")
        print("5. Decode: blackbox_decode <file>.TXT")
        print()

        return 0

    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
