#!/usr/bin/env python3
"""
Enable TELEMETRY feature in SITL via MSP
"""

import sys
import time
import os

# Add uNAVlib to path (relative to this script's location)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
unavlib_path = os.path.join(project_root, 'uNAVlib')
sys.path.insert(0, unavlib_path)

from unavlib.main import MSPy
from unavlib.enums.msp_codes import MSPCodes

# Connect to SITL
print("Connecting to SITL...")

with MSPy(device="5760", use_tcp=True, loglevel='WARNING') as board:
    if board == 1:
        print("✗ Connection failed!")
        sys.exit(1)

    print("✓ Connected to SITL")

    print("Getting current feature mask...")
    if board.send_RAW_msg(MSPCodes['MSP_FEATURE'], data=[]):
        features_msg = board.receive_msg()

        if features_msg and 'dataView' in features_msg:
            # Parse the 4-byte feature mask from dataView
            data = features_msg['dataView']
            current_features = int.from_bytes(data, byteorder='little')
            print(f"Current features: 0x{current_features:08X}")

            # FEATURE_TELEMETRY is bit 10 (0x400)
            FEATURE_TELEMETRY = 0x400

            if current_features & FEATURE_TELEMETRY:
                print("✓ TELEMETRY feature already enabled")
            else:
                print("Enabling TELEMETRY feature...")
                new_features = current_features | FEATURE_TELEMETRY
                print(f"New features: 0x{new_features:08X}")

                # Send new feature mask
                feature_data = list(new_features.to_bytes(4, byteorder='little'))
                board.send_RAW_msg(MSPCodes['MSP_SET_FEATURE'], data=feature_data)
                time.sleep(0.1)

                # Save to EEPROM
                print("Saving to EEPROM...")
                board.send_RAW_msg(MSPCodes['MSP_EEPROM_WRITE'], data=[])
                time.sleep(0.5)

                # Reboot
                print("Rebooting SITL...")
                board.send_RAW_msg(MSPCodes['MSP_REBOOT'], data=[])

                print("✓ TELEMETRY feature enabled. Wait 15 seconds for SITL to restart...")
        else:
            print("Failed to parse feature data from response")
            sys.exit(1)
    else:
        print("Failed to send MSP_FEATURE")
        sys.exit(1)

print("Done!")
