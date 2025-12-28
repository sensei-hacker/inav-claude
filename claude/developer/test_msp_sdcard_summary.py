#!/usr/bin/env python3
"""
Test MSP_SDCARD_SUMMARY command directly to see if FC is actually responding.
"""

import sys
import time

sys.path.insert(0, '/home/raymorris/Documents/planes/inavflight/mspapi2')

from mspapi2 import MSPSerial

# MSP command codes
MSP_SDCARD_SUMMARY = 79
MSP_SENSOR_STATUS = 151
MSPV2_INAV_STATUS = 0x2000  # 8192
MSP_ACTIVEBOXES = 113
MSPV2_INAV_ANALOG = 0x2002  # 8194

def test_sdcard_summary():
    """Test MSP_SDCARD_SUMMARY command."""

    print("Opening serial port /dev/ttyACM0 at 115200 baud...")
    try:
        # Connect to FC with shorter read timeout
        msp = MSPSerial("/dev/ttyACM0", 115200, read_timeout=0.1)
        msp.open()
        print("✓ Serial port opened successfully")
    except Exception as e:
        print(f"✗ FAILED to open serial port: {e}")
        return

    print("\nTesting MSP_SDCARD_SUMMARY (79)...\n")

    try:
        # Test 1: Single request
        print("Test 1: Single MSP_SDCARD_SUMMARY request")
        start = time.time()
        try:
            code, payload, ver = msp.request(MSP_SDCARD_SUMMARY, b"", timeout=1.5)
            elapsed = time.time() - start
            print(f"  ✓ Response received in {elapsed*1000:.1f}ms")
            print(f"  Response: code={code}, payload_len={len(payload)}, version={ver}")
        except Exception as e:
            elapsed = time.time() - start
            print(f"  ✗ FAILED after {elapsed*1000:.1f}ms: {e}")

        # Test 2: Multiple sequential requests
        print("\nTest 2: Five consecutive MSP_SDCARD_SUMMARY requests")
        for i in range(5):
            start = time.time()
            try:
                code, payload, ver = msp.request(MSP_SDCARD_SUMMARY, b"", timeout=1.5)
                elapsed = time.time() - start
                print(f"  Request {i+1}: OK in {elapsed*1000:.1f}ms (payload_len={len(payload)})")
            except Exception as e:
                elapsed = time.time() - start
                print(f"  Request {i+1}: FAILED after {elapsed*1000:.1f}ms - {e}")
            time.sleep(0.1)

        # Test 3: Interleaved with other commands (like configurator does)
        print("\nTest 3: MSP_SDCARD_SUMMARY + periodic status commands (simulating configurator)")
        commands = [
            ('MSP_SDCARD_SUMMARY', MSP_SDCARD_SUMMARY),
            ('MSP_SENSOR_STATUS', MSP_SENSOR_STATUS),
            ('MSPV2_INAV_STATUS', MSPV2_INAV_STATUS),
            ('MSP_ACTIVEBOXES', MSP_ACTIVEBOXES),
            ('MSPV2_INAV_ANALOG', MSPV2_INAV_ANALOG),
        ]

        for name, cmd_code in commands:
            start = time.time()
            try:
                code, payload, ver = msp.request(cmd_code, b"", timeout=1.5)
                elapsed = time.time() - start
                print(f"  {name} ({cmd_code}): OK in {elapsed*1000:.1f}ms (payload_len={len(payload)})")
            except Exception as e:
                elapsed = time.time() - start
                print(f"  {name} ({cmd_code}): FAILED after {elapsed*1000:.1f}ms - {e}")

    finally:
        msp.close()
        print("\nDone!")

if __name__ == '__main__':
    test_sdcard_summary()
