#!/usr/bin/env python3
"""Send MSP_REBOOT command to SITL"""

import sys
import time
import os

# Add uNAVlib to path (relative to this script's location)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))))
unavlib_path = os.path.join(project_root, 'uNAVlib')
sys.path.insert(0, unavlib_path)
from unavlib.main import MSPy
from unavlib.enums.msp_codes import MSPCodes

with MSPy(device="5760", use_tcp=True, loglevel='WARNING') as board:
    if board == 1:
        print("✗ Connection failed")
        sys.exit(1)

    if board.send_RAW_msg(MSPCodes['MSP_REBOOT'], data=[]):
        time.sleep(0.2)
    print('✓ Reboot command sent')
