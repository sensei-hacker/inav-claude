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
                    # Parse the response (new API already converts units)
                    # fixType is now an enum, get numeric value or name
                    fix_type = gps_data.get('fixType')
                    fix_str = fix_type.value if hasattr(fix_type, 'value') else fix_type

                    print(f"[{time.strftime('%H:%M:%S')}] GPS Fix: {fix_str} | "
                          f"Sats: {gps_data.get('numSat', 0)} | "
                          f"Lat: {gps_data.get('latitude', 0):.6f} | "  # Already in decimal degrees
                          f"Lon: {gps_data.get('longitude', 0):.6f} | "  # Already in decimal degrees
                          f"Alt: {gps_data.get('altitude', 0):.1f}m | "  # Already in meters
                          f"Speed: {gps_data.get('speed', 0):.1f}m/s")  # Already in m/s
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] No GPS data")

                # Also get GPS statistics
                try:
                    stats = api.get_gps_statistics()
                    if stats:
                        # GPS stats are already converted (hdop, eph, epv already scaled)
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
