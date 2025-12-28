#!/usr/bin/env python3
"""
GPS Injection + navEPH Logging

Combines GPS altitude injection with continuous RC and navEPH data collection.
Queries navEPH via MSP2_INAV_DEBUG and logs to CSV for analysis.

Usage:
    python3 gps_with_naveph_logging.py --profile climb --duration 60 --output naveph_climb.csv
"""

import sys
import time
import struct
import argparse
import math
import os
import csv

# Add uNAVlib to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))))
unavlib_path = os.path.join(project_root, 'uNAVlib')
sys.path.insert(0, unavlib_path)
from unavlib.main import MSPy
from unavlib.enums.msp_codes import MSPCodes

# RC values
RC_MID = 1500
RC_LOW = 1000
RC_HIGH = 2000

# MSP commands
MSP_SET_RAW_RC = 200
MSP_SET_RAW_GPS = 201
MSP_SIMULATOR = 0x201F
MSP2_INAV_DEBUG = 0x2009
MSP2_COMMON_SET_SETTING = 0x1004

# Debug modes
DEBUG_POS_EST = 20  # Position estimator debug mode


def send_rc(board, throttle=RC_LOW, aux1=RC_HIGH):
    """Send RC data (AETR order) - AUX1=HIGH to keep armed."""
    channels = [RC_MID, RC_MID, throttle, RC_MID, aux1] + [RC_MID] * 11
    data = []
    for ch in channels:
        data.extend([ch & 0xFF, (ch >> 8) & 0xFF])
    board.send_RAW_msg(MSP_SET_RAW_RC, data=data)
    try:
        board.receive_msg()
    except:
        pass


def send_gps(board, altitude_cm, lat=0, lon=0, fix_type=3, num_sats=10):
    """Send GPS data via MSP_SET_RAW_GPS."""
    altitude_m = altitude_cm // 100
    data = struct.pack('<BBiiHH', fix_type, num_sats, lat, lon, altitude_m, 0)
    board.send_RAW_msg(MSP_SET_RAW_GPS, data=list(data))
    try:
        board.receive_msg()
    except:
        pass


def set_debug_mode(board, mode):
    """Set debug mode via MSP2_COMMON_SET_SETTING."""
    setting_name = b'debug_mode\0'
    payload = setting_name + struct.pack('<B', mode)
    board.send_RAW_msg(MSP2_COMMON_SET_SETTING, data=list(payload))
    try:
        board.receive_msg()
    except:
        pass
    time.sleep(0.2)


def get_naveph(board):
    """
    Query navEPH via MSP2_INAV_DEBUG.

    Returns tuple: (navEPH, navEPV, success)

    navEPH and navEPV are encoded in debug[7]:
      Bits 10-19: navEPH (max 1000)
      Bits 0-9:   navEPV (max 1000)
      Bits 20-26: posEstimator flags
    """
    try:
        board.send_RAW_msg(MSP2_INAV_DEBUG, data=[])
        board.receive_msg()

        # debug is array of 8 uint32 values
        # We need debug[7] which contains encoded navEPH/navEPV
        if 'debug' in board.CONFIG and len(board.CONFIG['debug']) >= 8:
            debug7 = board.CONFIG['debug'][7]

            # Extract navEPH (bits 10-19) and navEPV (bits 0-9)
            navEPV = debug7 & 0x3FF  # Lower 10 bits
            navEPH = (debug7 >> 10) & 0x3FF  # Bits 10-19
            flags = (debug7 >> 20) & 0x7F  # Bits 20-26

            return navEPH, navEPV, True
        else:
            return 0, 0, False

    except Exception as e:
        return 0, 0, False


def main():
    parser = argparse.ArgumentParser(description='GPS injection with navEPH logging')
    parser.add_argument('--profile', choices=['climb', 'descent', 'hover', 'sine'],
                        default='climb', help='Motion profile (default: climb)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Duration in seconds (default: 60)')
    parser.add_argument('--port', type=int, default=5760,
                        help='MSP port (default: 5760)')
    parser.add_argument('--output', type=str, default='/tmp/naveph_log.csv',
                        help='Output CSV file (default: /tmp/naveph_log.csv)')
    parser.add_argument('--query-rate', type=int, default=10,
                        help='navEPH query rate in Hz (default: 10)')

    args = parser.parse_args()

    print("=" * 70)
    print("GPS Injection + navEPH Logging")
    print("=" * 70)
    print(f"\nProfile:     {args.profile}")
    print(f"Duration:    {args.duration}s")
    print(f"MSP Port:    {args.port}")
    print(f"Output CSV:  {args.output}")
    print(f"Query Rate:  {args.query_rate} Hz")
    print()

    csv_file = None
    csv_writer = None

    try:
        # Open CSV file
        csv_file = open(args.output, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['timestamp', 'elapsed', 'gps_altitude_m', 'navEPH_cm', 'navEPV_cm'])

        with MSPy(device=str(args.port), use_tcp=True, loglevel='WARNING') as board:
            if board == 1:
                print("✗ Connection failed")
                return 1

            print("✓ Connected")
            time.sleep(1)

            # Set debug mode to POS_EST
            print(f"Setting debug_mode to DEBUG_POS_EST ({DEBUG_POS_EST})...")
            set_debug_mode(board, DEBUG_POS_EST)
            time.sleep(0.5)

            # Enable HITL mode
            print("Enabling HITL mode...")
            hitl_data = struct.pack('<B', 1)
            board.send_RAW_msg(MSP_SIMULATOR, data=list(hitl_data))
            board.receive_msg()
            time.sleep(0.5)

            print(f"Starting GPS injection ({args.profile}) + RC sending...")
            print()

            # Send RC with AUX1=HIGH and wait for arming
            print("Sending RC to arm SITL...")
            arm_start = time.time()
            armed = False

            while not armed and (time.time() - arm_start) < 5.0:
                send_rc(board, aux1=RC_HIGH)
                time.sleep(0.02)

                # Check arming status every 0.5s
                if int((time.time() - arm_start) * 10) % 5 == 0:
                    board.send_RAW_msg(0x2000, data=[])
                    try:
                        board.receive_msg()
                        mode = board.CONFIG.get('mode', 0)
                        armed = (mode & 0x01) != 0
                    except:
                        pass

            if armed:
                print("✓ SITL is ARMED!")
            else:
                print("✗ SITL failed to arm - check ARM mode configuration")
                return 1

            print()
            print("Logging navEPH data...")
            print()

            start_time = time.time()
            iteration = 0

            # RC at 50Hz, GPS at 10Hz, navEPH query at user-specified rate
            rc_interval = 0.02  # 50Hz
            gps_interval = 0.1  # 10Hz
            naveph_interval = 1.0 / args.query_rate

            last_rc = 0
            last_gps = 0
            last_naveph = 0

            current_altitude = 0

            while (time.time() - start_time) < args.duration:
                current_time = time.time()
                elapsed = current_time - start_time

                # Calculate altitude based on profile
                if args.profile == 'climb':
                    altitude_m = min(100, elapsed * 5)  # 5 m/s climb
                elif args.profile == 'descent':
                    altitude_m = max(0, 100 - elapsed * 2)  # 2 m/s descent
                elif args.profile == 'hover':
                    altitude_m = 50  # Stationary
                elif args.profile == 'sine':
                    altitude_m = 50 + 30 * math.sin(elapsed * 0.5)
                else:
                    altitude_m = 0

                # Send RC at 50Hz
                if current_time - last_rc >= rc_interval:
                    send_rc(board)
                    last_rc = current_time

                # Send GPS at 10Hz
                if current_time - last_gps >= gps_interval:
                    send_gps(board, int(altitude_m * 100))
                    current_altitude = altitude_m
                    last_gps = current_time

                # Query navEPH at specified rate
                if current_time - last_naveph >= naveph_interval:
                    navEPH, navEPV, success = get_naveph(board)
                    last_naveph = current_time

                    if success:
                        # Log to CSV
                        csv_writer.writerow([
                            current_time,
                            f"{elapsed:.3f}",
                            f"{current_altitude:.1f}",
                            navEPH,
                            navEPV
                        ])
                        csv_file.flush()  # Flush to disk immediately

                        iteration += 1

                        # Print every 1 second
                        if iteration % args.query_rate == 0:
                            print(f"[{elapsed:5.1f}s] Alt: {current_altitude:6.1f}m | navEPH: {navEPH:4d}cm | navEPV: {navEPV:4d}cm")

                time.sleep(0.001)  # Small sleep to prevent busy loop

            print()
            print(f"✓ Logged {iteration} navEPH samples over {args.duration}s")
            print(f"✓ Data saved to: {args.output}")
            print()
            print("To analyze:")
            print(f"  column -t -s, {args.output} | less")
            print(f"  python3 -c 'import pandas as pd; df=pd.read_csv(\"{args.output}\"); print(df.describe())'")
            return 0

    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if csv_file:
            csv_file.close()


if __name__ == '__main__':
    sys.exit(main())
