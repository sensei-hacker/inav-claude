#!/usr/bin/env python3
"""Monitor GPS status from SITL while GPS simulator runs."""

import time
from mspapi2 import MSPApi, InavMSP

def monitor_gps():
    """Monitor GPS data from SITL."""
    print("Connecting to SITL on port 5760 (UART1 - MSP)...")
    api = MSPApi(tcp_endpoint='localhost:5760')

    try:
        time.sleep(0.5)

        print("\nMonitoring GPS status (press Ctrl+C to stop)...\n")

        while True:
            try:
                # Get raw GPS data using the correct API method
                gps_data = api.get_raw_gps()

                if gps_data:
                    # Parse the response
                    print(f"[{time.strftime('%H:%M:%S')}] GPS Fix: {gps_data.get('fixType', 'N/A')} | "
                          f"Sats: {gps_data.get('numSat', 0)} | "
                          f"Lat: {gps_data.get('lat', 0)/1e7:.6f} | "
                          f"Lon: {gps_data.get('lon', 0)/1e7:.6f} | "
                          f"Alt: {gps_data.get('alt', 0)/100:.1f}m | "
                          f"HDOP: {gps_data.get('hdop', 0)/100:.2f} | "
                          f"EPH: {gps_data.get('eph', 0)/100:.2f}m")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] No GPS data")

                # Also get GPS statistics
                try:
                    stats = api.get_gps_statistics()
                    if stats:
                        print(f"              GPS Stats: {stats}")
                except:
                    pass

                time.sleep(1)  # Check once per second

            except KeyboardInterrupt:
                print("\n\nMonitoring stopped.")
                break
            except Exception as e:
                print(f"Error reading GPS data: {e}")
                time.sleep(1)

    finally:
        # Close connection
        api.close()

if __name__ == '__main__':
    monitor_gps()
