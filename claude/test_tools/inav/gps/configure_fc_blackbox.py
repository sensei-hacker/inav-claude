#!/usr/bin/env python3
"""
Configure Hardware Flight Controller for Blackbox Logging

Sets up FC to log navEPH data at 500 Hz to onboard storage.

Usage:
    python3 configure_fc_blackbox.py --port /dev/ttyACM0 --rate-denom 2
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
MSP2_COMMON_SETTING = 0x1003

# Debug modes
DEBUG_POS_EST = 20  # Position estimator (navEPH is in debug[7])

# Blackbox settings
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


def get_setting(api, name):
    """Get a configuration setting value."""
    setting_name = name.encode('ascii') + b'\0'

    try:
        code, response = api._serial.request(MSP2_COMMON_SETTING, setting_name)
        if response and len(response) > len(setting_name):
            # Response format: name\0 + value
            # Extract value (skip name)
            value_data = response[len(setting_name):]
            if len(value_data) >= 4:
                return struct.unpack('<i', value_data[:4])[0]
            elif len(value_data) >= 2:
                return struct.unpack('<h', value_data[:2])[0]
            elif len(value_data) >= 1:
                return struct.unpack('<b', value_data[:1])[0]
    except:
        pass

    return None


def main():
    parser = argparse.ArgumentParser(description='Configure FC for blackbox logging')
    parser.add_argument('--port', type=str, default='/dev/ttyACM0',
                        help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--baud', type=int, default=115200,
                        help='Baud rate (default: 115200)')
    parser.add_argument('--rate-denom', type=int, default=2,
                        help='Blackbox rate denominator (default: 2 = 500 Hz)')
    parser.add_argument('--device', type=str, default='auto',
                        help='Blackbox device: auto, spiflash, sdcard, serial (default: auto)')

    args = parser.parse_args()

    logging_rate = 1000 // args.rate_denom

    print("=" * 70)
    print("Hardware FC Blackbox Configuration")
    print("=" * 70)
    print()
    print(f"Serial Port:        {args.port}")
    print(f"Baud Rate:          {args.baud}")
    print(f"Blackbox Rate:      {BLACKBOX_RATE_NUM}/{args.rate_denom} ({logging_rate} Hz @ 1000 Hz PID)")
    print(f"Debug Mode:         DEBUG_POS_EST ({DEBUG_POS_EST})")
    print()

    try:
        # Connect to FC
        api = MSPApi(port=args.port, baudrate=args.baud)
        api.open()
        time.sleep(1)

        # Get FC info
        code, response = api._serial.request(2)  # MSP_FC_VARIANT
        variant = response[:4].decode('ascii', errors='ignore') if response else "Unknown"

        code, response = api._serial.request(3)  # MSP_FC_VERSION
        if response and len(response) >= 3:
            version = f"{response[0]}.{response[1]}.{response[2]}"
        else:
            version = "Unknown"

        print(f"✓ Connected to {variant} {version}")
        print()

        # Determine blackbox device
        if args.device == 'auto':
            print("Detecting blackbox storage...")
            # Try to read current blackbox_device setting
            current_device = get_setting(api, 'blackbox_device')
            if current_device is not None:
                device_names = {0: 'SERIAL', 1: 'SPIFLASH', 2: 'SDCARD', 3: 'FILE'}
                device_name = device_names.get(current_device, f'UNKNOWN({current_device})')
                print(f"  Current device: {device_name}")

                # Use current device if it's storage (not SERIAL or FILE)
                if current_device in [1, 2]:  # SPIFLASH or SDCARD
                    blackbox_device = current_device
                    print(f"  Using: {device_names[blackbox_device]}")
                else:
                    # Default to SPIFLASH for hardware
                    blackbox_device = 1
                    print(f"  Switching to: SPIFLASH (common on hardware)")
            else:
                blackbox_device = 1  # SPIFLASH
                print(f"  Defaulting to: SPIFLASH")
        else:
            device_map = {'spiflash': 1, 'sdcard': 2, 'serial': 0, 'file': 3}
            blackbox_device = device_map.get(args.device.lower(), 1)
            print(f"  Using: {args.device.upper()}")

        print()
        print("Configuring blackbox...")

        set_setting(api, 'blackbox_device', blackbox_device)
        print(f"  ✓ blackbox_device = {blackbox_device}")

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
        print("Configuring logging to start on boot (no arming required)...")
        set_setting(api, 'blackbox_arm_control', -1)
        print(f"  ✓ blackbox_arm_control = -1 (log from boot to power-off)")

        print()
        print("Saving configuration...")
        api._serial.send(MSP_EEPROM_WRITE, b'')
        time.sleep(1.0)
        print("  ✓ Configuration saved")

        print()
        print("Rebooting FC...")
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
        print("1. Wait 10s for FC to reboot")
        print("2. Verify BLACKBOX feature is enabled (via configurator)")
        print("3. Run GPS injection test:")
        print(f"   python3 claude/test_tools/inav/gps/gps_with_rc_keeper.py \\")
        print(f"     --port {args.port} --profile climb --duration 30")
        print("4. Download blackbox log (via configurator or CLI)")
        print("5. Decode: blackbox_decode <file>")
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
