#!/usr/bin/env python3
"""Check RX configuration details"""

import sys
import os

# Add uNAVlib to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))))
unavlib_path = os.path.join(project_root, 'uNAVlib')
sys.path.insert(0, unavlib_path)
from unavlib.main import MSPy

with MSPy(device='/dev/ttyACM1', baudrate=115200, use_tcp=False, loglevel='WARNING') as board:
    # Query RX config
    board.send_RAW_msg(44, data=[])
    board.receive_msg()

    if 'RX_CONFIG' in board.CONFIG:
        rx_config = board.CONFIG['RX_CONFIG']
        print(f"RX_CONFIG length: {len(rx_config)} bytes")
        print(f"Raw data: {list(rx_config)}")

        if len(rx_config) >= 24:
            print(f"\nByte 23 (receiver type): {rx_config[23]} (2=MSP)")

        # Try to decode structure
        # Typical RX_CONFIG format varies by INAV version
        print("\nTrying to decode fields...")
