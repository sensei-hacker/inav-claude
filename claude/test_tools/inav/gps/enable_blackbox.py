#!/usr/bin/env python3
"""Enable blackbox logging in SITL."""

import struct
import time
from mspapi2 import MSPApi, InavMSP

def enable_blackbox():
    """Configure SITL for blackbox logging."""
    print("Connecting to SITL on port 5760...")
    api = MSPApi(tcp_endpoint='localhost:5760')
    api.open()

    time.sleep(0.5)

    print("\nEnabling blackbox logging...")

    # Set blackbox_device to FILE (3) - SITL-specific feature
    print("  Setting blackbox_device = FILE (3)")
    setting_name = b'blackbox_device\0'
    value = 3  # FILE (SITL-specific)
    payload = setting_name + struct.pack('<B', value)
    api._serial.send(int(InavMSP.MSP2_COMMON_SET_SETTING), payload)
    time.sleep(0.2)

    # Set blackbox rate (log every frame for maximum detail)
    print("  Setting blackbox_rate_num = 1")
    setting_name = b'blackbox_rate_num\0'
    value = 1
    payload = setting_name + struct.pack('<B', value)
    api._serial.send(int(InavMSP.MSP2_COMMON_SET_SETTING), payload)
    time.sleep(0.2)

    print("  Setting blackbox_rate_denom = 16")
    setting_name = b'blackbox_rate_denom\0'
    value = 16  # Log every 16th frame (~62Hz at 1kHz loop rate)
    payload = setting_name + struct.pack('<B', value)
    api._serial.send(int(InavMSP.MSP2_COMMON_SET_SETTING), payload)
    time.sleep(0.2)

    # Save settings
    print("  Saving settings...")
    api._serial.send(int(InavMSP.MSP_EEPROM_WRITE), b'')
    time.sleep(1)

    print("\n✓ Blackbox configured to log to FILE")
    print("  Blackbox will create timestamped .TXT files in build_sitl/ directory")
    print("  Format: YYYY_MM_DD_HHMMSS.TXT")
    print("\nTo start logging:")
    print("  1. Arm SITL (blackbox starts on arm)")
    print("  2. Run GPS simulator")
    print("  3. Disarm SITL (blackbox stops on disarm)")
    print("  4. Find .TXT file in inav/build_sitl/")
    print("\nNote: BLACKBOX feature must also be enabled (via configurator or feature flag)")

    api.close()

if __name__ == '__main__':
    enable_blackbox()
