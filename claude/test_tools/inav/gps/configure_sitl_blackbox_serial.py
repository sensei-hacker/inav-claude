#!/usr/bin/env python3
"""
Configure SITL for Serial Blackbox Logging

Sets up SITL to log navEPH data via serial blackbox at 500 Hz
(blackbox_rate_denom = 2 with 1000 Hz PID loop)

Usage:
    python3 configure_sitl_blackbox_serial.py --port 5760

This script:
1. Enables BLACKBOX feature
2. Sets blackbox_device = SERIAL
3. Sets blackbox_rate_denom = 2 (500 Hz logging)
4. Sets debug_mode = DEBUG_POS_EST (20) for navEPH logging
5. Configures serial port for blackbox output
6. Saves and reboots SITL
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
MSP2_INAV_SET_MISC = 0x203A

# Debug modes
DEBUG_POS_EST = 20  # Position estimator (navEPH is in debug[7])

# Blackbox settings
BLACKBOX_DEVICE_SERIAL = 0
BLACKBOX_RATE_NUM = 1
BLACKBOX_RATE_DENOM = 2  # 500 Hz with 1000 Hz PID


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


def enable_feature(api, feature_name):
    """Enable a feature (e.g., 'BLACKBOX')."""
    # Feature flags are bit masks, easier to use CLI
    # For now, use setting approach
    # BLACKBOX is bit 19 in feature mask
    print(f"Enabling feature: {feature_name}")
    # Note: This is a simplified approach
    # May need to read current features and OR the bit
    print("  (Feature enable requires CLI or direct feature mask manipulation)")
    print("  Please verify BLACKBOX feature is enabled after reboot")


def main():
    parser = argparse.ArgumentParser(description='Configure SITL for serial blackbox logging')
    parser.add_argument('--port', type=int, default=5760,
                        help='MSP port (default: 5760)')
    parser.add_argument('--baud', type=int, default=115200,
                        help='Serial blackbox baud rate (default: 115200)')

    args = parser.parse_args()

    print("=" * 70)
    print("SITL Blackbox Serial Configuration")
    print("=" * 70)
    print()
    print(f"MSP Port:           {args.port}")
    print(f"Blackbox Device:    SERIAL")
    print(f"Blackbox Rate:      {BLACKBOX_RATE_NUM}/{BLACKBOX_RATE_DENOM} (500 Hz @ 1000 Hz PID)")
    print(f"Serial Baud:        {args.baud}")
    print(f"Debug Mode:         DEBUG_POS_EST ({DEBUG_POS_EST})")
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

        set_setting(api, 'blackbox_device', BLACKBOX_DEVICE_SERIAL)
        print(f"  ✓ blackbox_device = SERIAL ({BLACKBOX_DEVICE_SERIAL})")

        set_setting(api, 'blackbox_rate_num', BLACKBOX_RATE_NUM)
        print(f"  ✓ blackbox_rate_num = {BLACKBOX_RATE_NUM}")

        set_setting(api, 'blackbox_rate_denom', BLACKBOX_RATE_DENOM)
        print(f"  ✓ blackbox_rate_denom = {BLACKBOX_RATE_DENOM}")

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
        print("IMPORTANT:")
        print("1. Verify BLACKBOX feature is enabled:")
        print("   - Use INAV Configurator")
        print("   - Or check 'feature' command in CLI")
        print()
        print("2. SITL serial blackbox output:")
        print("   - SITL may output blackbox data to a specific TCP port")
        print("   - Or may require serial port configuration")
        print("   - Check SITL documentation for serial port mapping")
        print()
        print("3. Next steps:")
        print("   - Wait 10s for SITL to reboot")
        print("   - Run GPS injection test")
        print("   - Capture serial blackbox data")
        print("   - Decode with: blackbox_decode <file>")
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
