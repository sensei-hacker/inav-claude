#!/usr/bin/env python3
"""
Arm SITL via MSP

Configures SITL for arming and sends ARM command via RC channels.
Uses HITL mode to bypass sensor calibration requirements.
"""

import sys
import time
import struct
import os

# Add uNAVlib to path (relative to this script's location)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
unavlib_path = os.path.join(project_root, 'uNAVlib')
sys.path.insert(0, unavlib_path)
from unavlib.main import MSPy
from unavlib.enums.msp_codes import MSPCodes

def arm_sitl(port=5760):
    """Arm SITL via MSP"""

    print("Connecting to SITL MSP...")
    with MSPy(device=str(port), use_tcp=True, loglevel='WARNING') as board:
        if board == 1:
            print("✗ Failed to connect")
            return False

        print("✓ Connected")

        # Enable HITL mode (bypasses sensor calibration)
        print("Enabling HITL mode...")
        hitl_data = struct.pack('<B', 1)
        board.send_RAW_msg(MSPCodes['MSP_SIMULATOR'], data=list(hitl_data))
        board.receive_msg()
        time.sleep(0.5)

        # Send RC channels with ARM enabled (channel 5 > 1500)
        print("Sending ARM command...")
        channels = [1500] * 18  # All channels at midpoint
        channels[4] = 1800  # AUX1 (channel 5) high = ARM

        rc_data = struct.pack('<' + 'H' * 18, *channels)

        # Send RC frames at 50Hz for 2 seconds to arm
        for i in range(100):
            board.send_RAW_msg(MSPCodes['MSP_SET_RAW_RC'], data=list(rc_data))
            board.receive_msg()
            time.sleep(0.02)

        print("✓ ARM command sent")
        return True

if __name__ == '__main__':
    success = arm_sitl()
    sys.exit(0 if success else 1)
