#!/usr/bin/env python3
"""Quick test to read GPS status once."""

import time
from mspapi2 import MSPApi

print("Connecting to SITL on port 5760...")
api = MSPApi(tcp_endpoint='localhost:5760')

time.sleep(1)

print("Reading GPS data...")
try:
    gps_data = api.get_raw_gps()
    print(f"GPS Data: {gps_data}")
except Exception as e:
    print(f"Error: {e}")

print("Closing connection...")
api.close()
print("Done.")
