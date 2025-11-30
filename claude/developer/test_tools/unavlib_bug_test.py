#!/usr/bin/env python3
"""
Test to confirm uNAVlib bug with MSP response handling.
"""

import sys
import time
# Use the installed version, not the cloned one
# sys.path.insert(0, 'uNAVlib')

from unavlib.main import MSPy

MSP_RX_CONFIG = 44
MSP_RC = 105
MSP2_INAV_STATUS = 0x2000

def test_library(port):
    print(f"Connecting to SITL on port {port}...")

    # Test with default timeout (should fail)
    with MSPy(device=port, use_tcp=True, loglevel='WARNING') as board:
        if board == 1:
            print("Connection failed!")
            return

        print(f"Connected! FC: {board.CONFIG.get('flightControllerIdentifier', 'Unknown')}")

        # Test 1: MSP_RX_CONFIG (known to fail)
        print("\n=== Test 1: MSP_RX_CONFIG (code 44) ===")
        board.send_RAW_msg(MSP_RX_CONFIG, data=[])
        time.sleep(0.2)  # Give extra time
        dataHandler = board.receive_msg()
        print(f"dataHandler['code']: {dataHandler['code']}")
        print(f"dataHandler['packet_error']: {dataHandler['packet_error']}")
        print(f"dataHandler['dataView']: {len(dataHandler['dataView']) if dataHandler['dataView'] else 0} bytes")
        print(f"dataHandler['state']: {dataHandler['state']}")

        # Test 2: MSP_RC (known to fail)
        print("\n=== Test 2: MSP_RC (code 105) ===")
        board.send_RAW_msg(MSP_RC, data=[])
        time.sleep(0.2)
        dataHandler = board.receive_msg()
        print(f"dataHandler['code']: {dataHandler['code']}")
        print(f"dataHandler['packet_error']: {dataHandler['packet_error']}")
        print(f"dataHandler['dataView']: {len(dataHandler['dataView']) if dataHandler['dataView'] else 0} bytes")
        print(f"dataHandler['state']: {dataHandler['state']}")

        # Test 3: MSP2_INAV_STATUS (known to work)
        print("\n=== Test 3: MSP2_INAV_STATUS (code 0x2000) ===")
        board.send_RAW_msg(MSP2_INAV_STATUS, data=[])
        time.sleep(0.2)
        dataHandler = board.receive_msg()
        print(f"dataHandler['code']: {dataHandler['code']}")
        print(f"dataHandler['packet_error']: {dataHandler['packet_error']}")
        print(f"dataHandler['dataView']: {len(dataHandler['dataView']) if dataHandler['dataView'] else 0} bytes")
        print(f"dataHandler['state']: {dataHandler['state']}")

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else "5761"
    test_library(port)
