#!/usr/bin/env python3
"""Enable BLACKBOX feature in SITL."""

import struct
import time
from mspapi2 import MSPApi, InavMSP

FEATURE_BLACKBOX = 1 << 19  # Bit 19

def enable_blackbox_feature():
    """Enable BLACKBOX feature flag in SITL."""
    print("Connecting to SITL on port 5760...")
    api = MSPApi(tcp_endpoint='localhost:5760')
    api.open()

    time.sleep(0.5)

    print("\nReading current feature flags...")

    # Read current features (MSP_FEATURE returns uint32)
    response = api._serial.request(int(InavMSP.MSP_FEATURE))
    # response is a tuple: (metadata_dict, payload_bytes)
    payload = response[1] if isinstance(response, tuple) else response
    current_features = struct.unpack('<I', payload)[0]

    print(f"  Current features: 0x{current_features:08X}")
    print(f"  BLACKBOX enabled: {bool(current_features & FEATURE_BLACKBOX)}")

    if current_features & FEATURE_BLACKBOX:
        print("\n✓ BLACKBOX feature already enabled!")
    else:
        print("\n  Enabling BLACKBOX feature...")
        new_features = current_features | FEATURE_BLACKBOX
        print(f"  New features: 0x{new_features:08X}")

        # Set features
        payload = struct.pack('<I', new_features)
        api._serial.send(int(InavMSP.MSP_SET_FEATURE), payload)
        time.sleep(0.2)

        # Save to EEPROM
        print("  Saving to EEPROM...")
        api._serial.send(int(InavMSP.MSP_EEPROM_WRITE), b'')
        time.sleep(1)

        print("\n✓ BLACKBOX feature enabled!")

    print("\nBlackbox is now ready to log.")
    print("Logging will start when SITL is armed.")

    api.close()

if __name__ == '__main__':
    enable_blackbox_feature()
