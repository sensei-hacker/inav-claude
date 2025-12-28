#!/usr/bin/env python3
"""Check current GPS configuration in SITL."""

import time
from mspapi2 import MSPApi, InavMSP

def check_gps_status():
    """Check GPS status and configuration."""
    print("Connecting to SITL on port 5761...")
    api = MSPApi(tcp_endpoint='localhost:5761')

    try:
        time.sleep(0.5)

        print("\nRequesting GPS status (MSP_RAW_GPS)...")

        # Request raw GPS data to see current state
        response = api.request(InavMSP.MSP_RAW_GPS)

        if response:
            print(f"GPS Response: {response}")
        else:
            print("No GPS data received - GPS may not be configured")

        print("\nRequesting status...")
        status = api.request(InavMSP.MSP_STATUS)
        if status:
            print(f"FC Status: {status}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close connection
        del api

if __name__ == '__main__':
    check_gps_status()
