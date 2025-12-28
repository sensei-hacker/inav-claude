#!/usr/bin/env python3
"""
Test MSP commands that timeout during Blackbox tab switching.
"""

import sys
import time
sys.path.append('/home/raymorris/Documents/planes/inavflight/mspapi2')

from mspapi2.transport import TCPTransport
from mspapi2.msp import MSPv2

# Commands that timeout during Blackbox tab switch
TEST_COMMANDS = [
    79,    # MSP_SDCARD_SUMMARY
    151,   # MSP_SENSOR_STATUS
    8192,  # MSPV2_INAV_STATUS
    113,   # MSP_ACTIVEBOXES
    8194,  # MSPV2_INAV_ANALOG
]

def test_commands():
    """Test MSP commands with SITL."""
    transport = TCPTransport('localhost', 5760)
    msp = MSPv2(transport)

    try:
        transport.connect()
        print("Connected to SITL on TCP 5760")

        for cmd in TEST_COMMANDS:
            print(f"\nSending MSP command {cmd}...")
            start = time.time()
            try:
                response = msp.send_request(cmd, timeout=2.0)
                elapsed = time.time() - start
                print(f"  ✓ Response received in {elapsed*1000:.1f}ms, {len(response)} bytes")
            except Exception as e:
                elapsed = time.time() - start
                print(f"  ✗ TIMEOUT/ERROR after {elapsed*1000:.1f}ms: {e}")

        # Now send them all rapidly to simulate what configurator does
        print("\n\nRapid-fire test (like configurator global_data_refresh)...")
        for i in range(3):
            print(f"\nRound {i+1}:")
            for cmd in [151, 8192, 113, 8194]:  # The 4 global refresh commands
                try:
                    response = msp.send_request(cmd, timeout=2.0)
                    print(f"  {cmd}: OK ({len(response)} bytes)")
                except Exception as e:
                    print(f"  {cmd}: TIMEOUT - {e}")
            time.sleep(0.3)  # 300ms interval

    finally:
        transport.close()

if __name__ == '__main__':
    test_commands()
