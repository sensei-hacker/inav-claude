#!/usr/bin/env python3
"""Check current GPS configuration in SITL."""

import time
from mspapi2 import MSPApi, InavMSP

def check_gps_status():
    """Check GPS status and configuration."""
    print("Connecting to SITL on port 5761...")

    with MSPApi(tcp_endpoint='localhost:5761') as api:
        try:
            time.sleep(0.5)

            print("\nRequesting GPS status (MSP_RAW_GPS)...")

            # Request raw GPS data to see current state
            response = api.get_raw_gps()

            if response:
                print(f"GPS Response: {response}")
            else:
                print("No GPS data received - GPS may not be configured")

            print("\nRequesting status...")
            status = api.get_status()
            if status:
                print(f"FC Status: {status}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    check_gps_status()
