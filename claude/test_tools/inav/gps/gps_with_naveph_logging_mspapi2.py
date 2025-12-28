#!/usr/bin/env python3
"""
GPS Injection + navEPH Logging (using mspapi2)

Combines GPS altitude injection with continuous RC and navEPH data collection.
Queries navEPH via MSP2_INAV_DEBUG and logs to CSV for analysis.

Usage:
    python3 gps_with_naveph_logging_mspapi2.py --profile climb --duration 60 --output naveph_climb.csv
"""

import sys
import time
import struct
import argparse
import math
import csv
from mspapi2 import MSPApi, InavMSP

# RC values
RC_MID = 1500
RC_LOW = 1000
RC_HIGH = 2000

# MSP commands
MSP_SET_RAW_RC = 200
MSP_SET_RAW_GPS = 201
MSP_SIMULATOR = 0x201F
MSP2_INAV_DEBUG = int(InavMSP.MSP2_INAV_DEBUG.value)  # 0x2019
MSP2_COMMON_SET_SETTING = 0x1004

# Debug modes
DEBUG_POS_EST = 20  # Position estimator debug mode


def send_rc(api, throttle=RC_LOW, aux1=RC_HIGH):
    """Send RC data (AETR order) - AUX1=HIGH to keep armed."""
    channels = [RC_MID, RC_MID, throttle, RC_MID, aux1] + [RC_MID] * 11
    data = []
    for ch in channels:
        data.extend([ch & 0xFF, (ch >> 8) & 0xFF])
    api._serial.send(MSP_SET_RAW_RC, bytes(data))


def send_gps(api, altitude_cm, lat=0, lon=0, fix_type=3, num_sats=10):
    """Send GPS data via MSP_SET_RAW_GPS."""
    altitude_m = altitude_cm // 100
    data = struct.pack('<BBiiHH', fix_type, num_sats, lat, lon, altitude_m, 0)
    api._serial.send(MSP_SET_RAW_GPS, data)


def set_debug_mode(api, mode):
    """Set debug mode via MSP2_COMMON_SET_SETTING."""
    setting_name = b'debug_mode\0'
    payload = setting_name + struct.pack('<B', mode)
    api._serial.send(MSP2_COMMON_SET_SETTING, payload)
    time.sleep(0.2)


def get_naveph(api):
    """
    Query navEPH via MSP2_INAV_DEBUG.

    Returns tuple: (navEPH, navEPV, success)

    navEPH and navEPV are encoded in debug[7]:
      Bits 10-19: navEPH (max 1000)
      Bits 0-9:   navEPV (max 1000)
      Bits 20-26: posEstimator flags
    """
    try:
        code, response = api._serial.request(MSP2_INAV_DEBUG)

        # Response should be 8 x uint32 (32 bytes)
        if response and len(response) >= 32:
            # Unpack 8 uint32 values
            debug_values = struct.unpack('<8I', response[:32])

            # debug[7] contains encoded navEPH/navEPV
            debug7 = debug_values[7]

            # Extract navEPH (bits 10-19) and navEPV (bits 0-9)
            navEPV = debug7 & 0x3FF  # Lower 10 bits
            navEPH = (debug7 >> 10) & 0x3FF  # Bits 10-19
            flags = (debug7 >> 20) & 0x7F  # Bits 20-26

            return navEPH, navEPV, True
        else:
            return 0, 0, False

    except Exception as e:
        print(f"DEBUG: navEPH query error: {e}")
        return 0, 0, False


def check_armed(api):
    """Check if SITL is armed."""
    try:
        code, response = api._serial.request(101)  # MSP_STATUS
        if response and len(response) >= 11:
            # MSP_STATUS format: cycleTime(u16), i2cError(u16), sensor(u16), flag(u32), currentSet(u8)
            # flag at offset 4 contains ARMED bit (bit 0)
            flag = struct.unpack('<I', response[4:8])[0]
            armed = (flag & 0x01) != 0
            return armed
        return False
    except:
        return False


def main():
    parser = argparse.ArgumentParser(description='GPS injection with navEPH logging (mspapi2)')
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
    print("GPS Injection + navEPH Logging (mspapi2)")
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

        # Connect to SITL
        api = MSPApi(tcp_endpoint=f'localhost:{args.port}')
        api.open()
        time.sleep(1)
        print("✓ Connected")

        # Set debug mode to POS_EST
        print(f"Setting debug_mode to DEBUG_POS_EST ({DEBUG_POS_EST})...")
        set_debug_mode(api, DEBUG_POS_EST)
        time.sleep(0.5)

        # Enable HITL mode
        print("Enabling HITL mode...")
        hitl_data = struct.pack('<B', 1)
        api._serial.send(MSP_SIMULATOR, hitl_data)
        time.sleep(0.5)

        print(f"Starting GPS injection ({args.profile}) + RC sending...")
        print()

        # Send RC with AUX1=HIGH and wait for arming
        print("Sending RC to arm SITL...")
        arm_start = time.time()
        armed = False

        while not armed and (time.time() - arm_start) < 5.0:
            send_rc(api, aux1=RC_HIGH)
            time.sleep(0.02)

            # Check arming status every 0.5s
            if int((time.time() - arm_start) * 10) % 5 == 0:
                armed = check_armed(api)

        if armed:
            print("✓ SITL is ARMED!")
        else:
            print("✗ SITL failed to arm - check ARM mode configuration")
            api.close()
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
                send_rc(api)
                last_rc = current_time

            # Send GPS at 10Hz
            if current_time - last_gps >= gps_interval:
                send_gps(api, int(altitude_m * 100))
                current_altitude = altitude_m
                last_gps = current_time

            # Query navEPH at specified rate
            if current_time - last_naveph >= naveph_interval:
                navEPH, navEPV, success = get_naveph(api)
                last_naveph = current_time

                if success:
                    # Log to CSV
                    csv_writer.writerow([
                        f"{current_time:.6f}",
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

        api.close()
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
