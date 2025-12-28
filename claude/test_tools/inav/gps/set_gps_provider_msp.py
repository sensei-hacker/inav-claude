#!/usr/bin/env python3
"""Set GPS provider to MSP via MSP2_COMMON_SET_SETTING command."""

import struct
import time
from mspapi2 import MSPApi, InavMSP

def set_gps_provider_to_msp():
    """Configure SITL to use MSP GPS."""
    print("Connecting to SITL on port 5760...")
    api = MSPApi(tcp_endpoint='localhost:5760')
    api.open()

    time.sleep(0.5)

    # Build MSP2_COMMON_SET_SETTING payload
    # Format: setting_name\0 + value (uint8)
    setting_name = b'gps_provider\0'
    gps_provider_msp = 1  # 0=UBLOX, 1=MSP, 2=FAKE

    payload = setting_name + struct.pack('<B', gps_provider_msp)

    print(f"Sending MSP2_COMMON_SET_SETTING...")
    print(f"  Setting: gps_provider")
    print(f"  Value: {gps_provider_msp} (MSP)")
    print(f"  Payload: {payload.hex()}")

    try:
        # Send the command
        api._serial.send(int(InavMSP.MSP2_COMMON_SET_SETTING), payload)
        time.sleep(0.2)

        print("✓ Command sent")

        # Now save to EEPROM
        print("\nSaving to EEPROM...")
        api._serial.send(int(InavMSP.MSP_EEPROM_WRITE), b'')
        time.sleep(1)

        print("✓ Settings saved")
        print("\nSITL will reboot with MSP GPS enabled.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        api.close()

if __name__ == '__main__':
    set_gps_provider_to_msp()
