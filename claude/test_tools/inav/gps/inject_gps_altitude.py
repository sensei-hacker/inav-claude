#!/usr/bin/env python3
"""
GPS Altitude Injection Script

Injects simulated GPS altitude data into SITL via MSP_SET_RAW_GPS command.
Designed to run concurrently with CRSF RC sender on separate ports.

IMPORTANT: Port Separation
===========================
This script uses MSP protocol on port 5760 (UART1).
It can run concurrently with CRSF telemetry on port 5761 (UART2).
Port separation ensures zero interference between protocols.

USAGE:
    python3 inject_gps_altitude.py [--profile PROFILE] [--duration SEC] [--port PORT]

ARGUMENTS:
    --profile PROFILE   Motion profile (default: climb)
                        Options: climb, descent, hover, sine
    --duration SEC      Duration in seconds (default: 20)
    --port PORT         MSP port number (default: 5760)

PROFILES:
    climb     - Gradual climb from 0m to 100m at 5 m/s
    descent   - Gradual descent from 100m to 0m at 3 m/s
    hover     - Stationary at 50m altitude
    sine      - Oscillating altitude ±30m around 50m

EXAMPLES:
    # Simulate 30-second climb
    python3 inject_gps_altitude.py --profile climb --duration 30

    # Simulate oscillating altitude for 60 seconds
    python3 inject_gps_altitude.py --profile sine --duration 60

    # Custom MSP port
    python3 inject_gps_altitude.py --profile hover --port 5760

CONCURRENT OPERATION:
    This script can run alongside the CRSF RC sender:

    Terminal 1:  python3 inject_gps_altitude.py --profile climb --duration 30
    Terminal 2:  python3 ../crsf/crsf_rc_sender.py 2 --rate 50 --duration 30

PREREQUISITES:
    - SITL must be running with MSP enabled on port 5760
    - uNAVlib must be installed and accessible
    - No other MSP clients connected to port 5760

PROTOCOL:
    Uses MSP_SET_RAW_GPS (command 201) to inject:
    - GPS fix type (3 = 3D fix)
    - Number of satellites (10)
    - Altitude in meters
    - Latitude/Longitude (default 0,0)
    - Ground speed (default 0)
"""

import sys
import time
import struct
import argparse
import math
import os

# Add uNAVlib to path (relative to this script's location)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))))
unavlib_path = os.path.join(project_root, 'uNAVlib')
sys.path.insert(0, unavlib_path)
from unavlib.main import MSPy
from unavlib.enums.msp_codes import MSPCodes


def inject_gps_altitude(board, altitude_cm, lat=0, lon=0, fix_type=3, num_sats=10):
    """
    Inject simulated GPS altitude via MSP_SET_RAW_GPS

    Args:
        board: MSPy board connection
        altitude_cm: Altitude in centimeters
        lat: Latitude (degrees * 1e7), default 0
        lon: Longitude (degrees * 1e7), default 0
        fix_type: GPS fix type (0=no fix, 3=3D fix), default 3
        num_sats: Number of satellites, default 10
    """
    # Convert altitude from cm to meters for MSP message
    altitude_m = altitude_cm // 100

    # Pack GPS data
    data = struct.pack('<BBiiHH',
                       fix_type,
                       num_sats,
                       lat,
                       lon,
                       altitude_m,  # MSP wants meters, INAV converts to cm
                       0)  # groundSpeed (cm/s)

    # Send MSP command - must call receive_msg() even for SET commands
    if board.send_RAW_msg(MSPCodes['MSP_SET_RAW_GPS'], data=list(data)):
        board.receive_msg()  # Required for proper MSP communication


def main():
    parser = argparse.ArgumentParser(description='Inject GPS altitude motion via MSP')
    parser.add_argument('--profile', choices=['climb', 'descent', 'hover', 'sine'],
                        default='climb', help='Motion profile (default: climb)')
    parser.add_argument('--duration', type=int, default=20,
                        help='Duration in seconds (default: 20)')
    parser.add_argument('--port', type=int, default=5760,
                        help='MSP port (default: 5760)')

    args = parser.parse_args()

    print("=" * 70)
    print("GPS Altitude Injection (MSP)")
    print("=" * 70)
    print(f"\nProfile: {args.profile}")
    print(f"Duration: {args.duration}s")
    print(f"MSP Port: {args.port}")
    print()

    # Connect to MSP using context manager
    print(f"Connecting to SITL MSP (port {args.port})...")
    try:
        with MSPy(device=str(args.port), use_tcp=True, loglevel='WARNING') as board:
            if board == 1:
                print("✗ MSP connection failed!")
                return 1

            print("✓ MSP connected")
            print("Waiting for SITL to stabilize...")
            time.sleep(2)

            print()
            print(f"Starting GPS altitude injection ({args.profile} profile)...")
            print()

            start_time = time.time()
            injection_count = 0

            while (time.time() - start_time) < args.duration:
                current_time = time.time() - start_time

                # Calculate altitude based on profile
                if args.profile == 'climb':
                    altitude_m = min(100, current_time * 5)  # 5 m/s climb to 100m
                elif args.profile == 'descent':
                    altitude_m = max(0, 100 - current_time * 2)  # 2 m/s descent from 100m
                elif args.profile == 'hover':
                    altitude_m = 50  # Stationary at 50m
                elif args.profile == 'sine':
                    altitude_m = 50 + 30 * math.sin(current_time * 0.5)  # ±30m around 50m
                else:
                    altitude_m = 0

                # Print every 0.5s
                if injection_count % 5 == 0:
                    print(f"[{current_time:5.1f}s] Injecting altitude: {altitude_m:6.1f}m")

                # Inject GPS altitude
                inject_gps_altitude(board, int(altitude_m * 100))
                injection_count += 1

                time.sleep(0.1)  # 10 Hz injection rate

            print()
            print(f"✓ Completed {injection_count} GPS injections over {args.duration}s")
            print()
            return 0

    except KeyboardInterrupt:
        print()
        print("✗ Test interrupted by user")
        print()
        return 1
    except Exception as e:
        print()
        print(f"✗ Error: {e}")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
