#!/usr/bin/env python3
"""
GPS Signal Fluctuation Simulator for Issue #11202

Simulates the GPS signal instability reported in INAV issue #11202 using synthetic
MSP GPS data. This script helps reproduce EPH spikes, HDOP fluctuations, and satellite
count variations to understand and debug the issue.

ISSUE: https://github.com/iNavFlight/inav/issues/11202

PROBLEM DESCRIPTION:
- Recurring EPH (estimated position error) spikes in flight logs
- Wild HDOP fluctuations (2-5 range instead of stable ~1.3)
- Reduced satellite acquisition (15-18 sats instead of 25+)
- Periodic positional corrections during navigation

KEY FINDING:
- `gps_ublox_nav_hz` setting affects performance significantly
- Default 10Hz with 4 constellations: Unstable, low sat count
- Reduced to 6Hz (M10) or 9Hz (M9): Improved sat count, HDOP stable

USAGE:
    python3 simulate_gps_fluctuation_issue_11202.py [OPTIONS]

OPTIONS:
    --port PORT         Serial port or TCP address (default: tcp:localhost:5761)
    --duration SEC      Duration in seconds (default: 60)
    --update-rate HZ    GPS update rate in Hz (default: 10)
                        Options: 5, 6, 9, 10
    --scenario NAME     Test scenario (default: fluctuating)
                        Options: stable, fluctuating, spike, workaround
    --lat LAT          Latitude in degrees (default: 37.7749)
    --lon LON          Longitude in degrees (default: -122.4194)

SCENARIOS:
    stable       - Ideal GPS: 25 sats, HDOP 1.3, EPH 100cm
    fluctuating  - Problem case: 15-18 sats, HDOP 2-5, EPH spikes
    spike        - Severe EPH spikes every 5 seconds (198Hz pattern)
    workaround   - M9/M10 workaround: 9Hz/6Hz with stable metrics

EXAMPLES:
    # Simulate the reported problem at 10Hz (default)
    python3 simulate_gps_fluctuation_issue_11202.py --scenario fluctuating

    # Test stable GPS for comparison
    python3 simulate_gps_fluctuation_issue_11202.py --scenario stable

    # Test workaround at 9Hz (M9 fix)
    python3 simulate_gps_fluctuation_issue_11202.py --scenario workaround --update-rate 9

    # Test workaround at 6Hz (M10 fix)
    python3 simulate_gps_fluctuation_issue_11202.py --scenario workaround --update-rate 6

    # Connect to SITL via TCP
    python3 simulate_gps_fluctuation_issue_11202.py --port tcp:localhost:5761

    # Connect to real FC via serial
    python3 simulate_gps_fluctuation_issue_11202.py --port /dev/ttyACM0

PREREQUISITES:
    - SITL running with GPS provider set to MSP (set gps_provider = MSP)
      OR real FC configured for MSP GPS
    - mspapi2 library installed (pip install -e /path/to/mspapi2)
    - Flight controller must have USE_GPS_PROTO_MSP compiled in

MSP MESSAGE:
    Uses MSP2_SENSOR_GPS (0x1F03 / 7939) to inject:
    - GPS fix type (3 = 3D fix)
    - Number of satellites (varies by scenario)
    - Horizontal/Vertical position accuracy (EPH/EPV)
    - HDOP value
    - Latitude/Longitude
    - Altitude and velocity
    - Time data

METRICS EXPLANATION:
    EPH (Horizontal Position Accuracy): Lower is better
        - Good: 100-200 cm (1-2m)
        - Acceptable: 200-300 cm (2-3m)
        - Poor: 400-500+ cm (4-5m+)
        - Spikes: Sudden jumps to 400-500 cm

    HDOP (Horizontal Dilution of Precision): Lower is better
        - Excellent: 1.0-1.3 (HDOP * 100 = 100-130)
        - Good: 1.3-2.0 (130-200)
        - Moderate: 2.0-3.0 (200-300)
        - Poor: 3.0-5.0+ (300-500+)
        - Issue reports HDOP 2-5 range instead of stable ~1.3

    Satellite Count:
        - Optimal: 25+ satellites
        - Good: 18-25 satellites
        - Issue reports: 15-18 satellites (instead of 25+)

MONITORING:
    Monitor the GPS data in INAV:
    - Use CLI: `status` command to see GPS fix and satellite count
    - Use configurator GPS tab to see real-time data
    - Use blackbox logs to analyze EPH/HDOP over time
    - Check navigation behavior in flight modes

TESTING APPROACH:
    1. Build SITL with MSP GPS support
    2. Configure: set gps_provider = MSP
    3. Run this script with different scenarios and update rates
    4. Monitor EPH, HDOP, and satellite count in configurator
    5. Compare behavior at 5Hz, 6Hz, 9Hz, and 10Hz
    6. Look for differences between INAV versions (6.0 vs 7.0+)
"""

import sys
import time
import argparse
import math
import struct
from datetime import datetime
from typing import Tuple

# Add mspapi2 to path
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '../../../../'))
mspapi2_path = os.path.join(project_root, 'mspapi2')
sys.path.insert(0, mspapi2_path)

try:
    from mspapi2 import MSPApi, InavMSP
except ImportError as e:
    print(f"Error importing mspapi2: {e}")
    print(f"Make sure mspapi2 is installed:")
    print(f"  cd {mspapi2_path} && pip install -e .")
    sys.exit(1)


class GPSScenario:
    """GPS test scenario defining signal characteristics"""

    def __init__(self, name: str, sat_count_range: Tuple[int, int],
                 hdop_range: Tuple[int, int], eph_range: Tuple[int, int],
                 fluctuation_period: float = None):
        self.name = name
        self.sat_count_range = sat_count_range
        self.hdop_range = hdop_range
        self.eph_range = eph_range
        self.fluctuation_period = fluctuation_period

    def get_values(self, timestamp: float) -> Tuple[int, int, int]:
        """
        Get GPS values for current timestamp

        Returns:
            (sat_count, hdop, eph) tuple
        """
        if self.fluctuation_period:
            # Calculate fluctuation phase (0.0 to 1.0)
            phase = (timestamp % self.fluctuation_period) / self.fluctuation_period

            # Use sine wave to smoothly transition between min and max
            sat_min, sat_max = self.sat_count_range
            hdop_min, hdop_max = self.hdop_range
            eph_min, eph_max = self.eph_range

            # Sine gives smooth transitions
            sine_factor = (math.sin(phase * 2 * math.pi) + 1) / 2  # 0.0 to 1.0

            sat_count = int(sat_min + (sat_max - sat_min) * sine_factor)
            hdop = int(hdop_min + (hdop_max - hdop_min) * sine_factor)
            eph = int(eph_min + (eph_max - eph_min) * sine_factor)
        else:
            # Static values (use midpoint)
            sat_count = (self.sat_count_range[0] + self.sat_count_range[1]) // 2
            hdop = (self.hdop_range[0] + self.hdop_range[1]) // 2
            eph = (self.eph_range[0] + self.eph_range[1]) // 2

        return sat_count, hdop, eph


# Define test scenarios
SCENARIOS = {
    'stable': GPSScenario(
        name='Stable GPS (Ideal)',
        sat_count_range=(25, 25),
        hdop_range=(130, 130),  # HDOP 1.3
        eph_range=(100, 100),   # 1m accuracy
        fluctuation_period=None
    ),
    'fluctuating': GPSScenario(
        name='Fluctuating GPS (Issue #11202)',
        sat_count_range=(15, 18),  # Reduced sat count
        hdop_range=(200, 500),      # HDOP 2.0-5.0
        eph_range=(150, 450),       # 1.5m - 4.5m accuracy
        fluctuation_period=10.0     # 10 second cycle
    ),
    'spike': GPSScenario(
        name='EPH Spikes (Severe)',
        sat_count_range=(16, 16),
        hdop_range=(130, 450),      # Spike from 1.3 to 4.5
        eph_range=(100, 500),       # Spike from 1m to 5m
        fluctuation_period=5.0      # 5 second spikes (close to reported 5.06ms = 198Hz)
    ),
    'workaround': GPSScenario(
        name='Workaround (9Hz/6Hz fix)',
        sat_count_range=(25, 27),   # Improved sat count
        hdop_range=(130, 130),      # Stable HDOP 1.3
        eph_range=(100, 120),       # Stable accuracy
        fluctuation_period=None
    ),
}


def send_rc_data(api: MSPApi):
    """Send RC data to keep MSP receiver active and SITL armed."""
    import struct
    # AETR order: Roll, Pitch, Throttle, Yaw, AUX1...
    channels = [1500, 1500, 1000, 1500, 1800] + [1500] * 13  # AUX1=1800 for ARM
    data = struct.pack('<' + 'H' * 18, *channels)
    api._serial.send(int(InavMSP.MSP_SET_RAW_RC), data)


def send_gps_data(api: MSPApi, scenario: GPSScenario, timestamp: float,
                  lat: float, lon: float, alt_cm: int = 10000):
    """
    Send synthetic GPS data via MSP2_SENSOR_GPS

    Args:
        api: MSPApi connection
        scenario: GPS scenario defining signal characteristics
        timestamp: Current timestamp for fluctuation calculation
        lat: Latitude in degrees
        lon: Longitude in degrees
        alt_cm: Altitude in centimeters (default 100m)
    """
    # Get scenario values
    sat_count, hdop, eph_cm = scenario.get_values(timestamp)

    # Convert lat/lon to degrees * 1e7
    lat_e7 = int(lat * 1e7)
    lon_e7 = int(lon * 1e7)

    # Get current UTC time
    now = datetime.utcnow()

    # Build MSP2_SENSOR_GPS message
    # Message code: 0x1F03 (7939)
    gps_data = {
        'instance': 0,                          # uint8_t
        'gpsWeek': 0xFFFF,                      # uint16_t (not available)
        'msTOW': 0,                             # uint32_t
        'fixType': 3,                           # uint8_t (3 = 3D fix)
        'satellitesInView': sat_count,          # uint8_t
        'hPosAccuracy': eph_cm * 10,            # uint16_t (convert cm to mm)
        'vPosAccuracy': eph_cm * 10,            # uint16_t (convert cm to mm)
        'hVelAccuracy': 50,                     # uint16_t (cm/s)
        'hdop': hdop,                           # uint16_t (HDOP * 100)
        'longitude': lon_e7,                    # int32_t
        'latitude': lat_e7,                     # int32_t
        'mslAltitude': alt_cm,                  # int32_t (cm)
        'nedVelNorth': 0,                       # int32_t (cm/s)
        'nedVelEast': 0,                        # int32_t (cm/s)
        'nedVelDown': 0,                        # int32_t (cm/s)
        'groundCourse': 0,                      # uint16_t (deg * 100)
        'trueYaw': 65535,                       # uint16_t (65535 = not available)
        'year': now.year,                       # uint16_t
        'month': now.month,                     # uint8_t
        'day': now.day,                         # uint8_t
        'hour': now.hour,                       # uint8_t
        'min': now.minute,                      # uint8_t
        'sec': now.second,                      # uint8_t
    }

    try:
        # Send MSP2_SENSOR_GPS (0x1F03 = 7939) - one-way command, no response
        payload = api._pack_request(InavMSP.MSP2_SENSOR_GPS, gps_data)
        api._serial.send(int(InavMSP.MSP2_SENSOR_GPS), payload)

        # Print status
        hdop_float = hdop / 100.0
        eph_m = eph_cm / 100.0
        print(f"[{now.strftime('%H:%M:%S')}] Sats: {sat_count:2d} | "
              f"HDOP: {hdop_float:4.2f} | EPH: {eph_m:5.2f}m | "
              f"Fix: 3D | Scenario: {scenario.name}")

        return True
    except Exception as e:
        print(f"Error sending GPS data: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Simulate GPS fluctuation issue #11202',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--port', default='tcp:localhost:5761',
                        help='Serial port or TCP address (default: tcp:localhost:5761)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Duration in seconds (default: 60)')
    parser.add_argument('--update-rate', type=int, default=10, choices=[5, 6, 9, 10],
                        help='GPS update rate in Hz (default: 10)')
    parser.add_argument('--scenario', default='fluctuating', choices=list(SCENARIOS.keys()),
                        help='Test scenario (default: fluctuating)')
    parser.add_argument('--lat', type=float, default=37.7749,
                        help='Latitude in degrees (default: 37.7749 / San Francisco)')
    parser.add_argument('--lon', type=float, default=-122.4194,
                        help='Longitude in degrees (default: -122.4194 / San Francisco)')
    parser.add_argument('--alt', type=int, default=100,
                        help='Altitude in meters (default: 100)')
    parser.add_argument('--arm', action='store_true',
                        help='Send RC data to keep SITL armed (for blackbox logging)')

    args = parser.parse_args()

    # Get scenario
    scenario = SCENARIOS[args.scenario]

    # Calculate update interval
    update_interval = 1.0 / args.update_rate

    print("="*70)
    print("GPS Fluctuation Simulator for Issue #11202")
    print("="*70)
    print(f"Port:        {args.port}")
    print(f"Duration:    {args.duration} seconds")
    print(f"Update Rate: {args.update_rate} Hz ({update_interval*1000:.1f}ms interval)")
    print(f"Scenario:    {scenario.name}")
    print(f"Location:    {args.lat}, {args.lon}")
    print(f"Altitude:    {args.alt}m")
    print()
    print("Scenario Characteristics:")
    print(f"  Satellites:  {scenario.sat_count_range[0]}-{scenario.sat_count_range[1]}")
    print(f"  HDOP:        {scenario.hdop_range[0]/100:.2f}-{scenario.hdop_range[1]/100:.2f}")
    print(f"  EPH:         {scenario.eph_range[0]/100:.2f}-{scenario.eph_range[1]/100:.2f}m")
    if scenario.fluctuation_period:
        print(f"  Fluctuation: {scenario.fluctuation_period:.1f}s period")
    else:
        print(f"  Fluctuation: None (stable)")
    print()
    print("="*70)
    print()

    # Connect to flight controller
    try:
        print(f"Connecting to {args.port}...")

        if args.port.startswith('tcp:'):
            # TCP connection (SITL)
            host_port = args.port[4:]  # Remove 'tcp:' prefix
            if ':' in host_port:
                host, port = host_port.rsplit(':', 1)
                tcp_endpoint = f"{host}:{port}"
            else:
                tcp_endpoint = f"{host_port}:5761"

            api = MSPApi(tcp_endpoint=tcp_endpoint)
        else:
            # Serial connection (real FC)
            api = MSPApi(port=args.port, baudrate=115200)

        api.open()
        print("Connected!")
        print()

        # Enable HITL mode if --arm flag is set (bypasses sensor calibration)
        if args.arm:
            import struct
            print("Enabling HITL mode for arming...")
            hitl_data = struct.pack('<B', 1)
            api._serial.send(int(InavMSP.MSP_SIMULATOR), hitl_data)
            time.sleep(0.5)
            print("HITL mode enabled")
            print()

    except Exception as e:
        print(f"Error connecting: {e}")
        print()
        print("Troubleshooting:")
        print("  - For SITL: Make sure SITL is running and listening on the port")
        print("  - For real FC: Check the serial port and permissions")
        print("  - Ensure GPS provider is set to MSP: set gps_provider = MSP")
        sys.exit(1)

    # Send GPS data
    try:
        start_time = time.time()
        iteration = 0

        print("Sending GPS data... (Press Ctrl+C to stop)")
        print()

        while True:
            current_time = time.time()
            elapsed = current_time - start_time

            # Check duration
            if elapsed >= args.duration:
                print()
                print(f"Duration {args.duration}s reached. Stopping.")
                break

            # Send GPS data
            send_gps_data(
                api=api,
                scenario=scenario,
                timestamp=elapsed,
                lat=args.lat,
                lon=args.lon,
                alt_cm=args.alt * 100
            )

            # Send RC data to keep armed (if --arm flag set)
            if args.arm:
                send_rc_data(api)

            iteration += 1

            # If armed, send additional RC frames at 50Hz until next GPS update
            # GPS at 10Hz = 100ms interval, RC at 50Hz = 20ms interval
            # So we need ~4 more RC frames between GPS updates
            if args.arm:
                rc_interval = 0.02  # 50Hz = 20ms
                next_gps = start_time + (iteration * update_interval)
                rc_count = 0
                while time.time() < next_gps - 0.005 and rc_count < 4:
                    time.sleep(rc_interval)
                    send_rc_data(api)
                    rc_count += 1

            # Sleep until next update
            next_update = start_time + (iteration * update_interval)
            sleep_time = next_update - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

        print()
        print("="*70)
        print(f"Sent {iteration} GPS updates in {elapsed:.1f}s")
        print(f"Average rate: {iteration/elapsed:.2f} Hz")
        print("="*70)

    except KeyboardInterrupt:
        print()
        print()
        print("Stopped by user.")
    except Exception as e:
        print(f"Error during GPS transmission: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close connection
        try:
            api.close()
        except:
            pass


if __name__ == '__main__':
    main()
