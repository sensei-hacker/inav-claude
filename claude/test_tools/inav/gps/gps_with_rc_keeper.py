#!/usr/bin/env python3
"""
GPS Injection + RC Keeper

Combines GPS altitude injection with continuous RC sending to keep SITL armed.
Uses existing functions from inject_gps_altitude.py and sitl_arm_test.py.

Usage:
    python3 gps_with_rc_keeper.py --profile climb --duration 60
"""

import sys
import time
import struct
import argparse
import math
import os

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


def main():
    parser = argparse.ArgumentParser(description='GPS injection with continuous RC (for arming)')
    parser.add_argument('--profile', choices=['climb', 'descent', 'hover', 'sine'],
                        default='climb', help='Motion profile (default: climb)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Duration in seconds (default: 60)')
    parser.add_argument('--port', type=str, default='5760',
                        help='MSP port (default: 5760 for TCP, or /dev/ttyACM0 for serial)')

    args = parser.parse_args()

    print("=" * 70)
    print("GPS Injection + RC Keeper")
    print("=" * 70)
    print(f"\nProfile: {args.profile}")
    print(f"Duration: {args.duration}s")
    print(f"MSP Port: {args.port}")
    print()

    # Detect if TCP (numeric port) or serial (device path)
    use_tcp = args.port.isdigit()
    device = args.port if not use_tcp else str(args.port)

    try:
        with MSPy(device=device, use_tcp=use_tcp, loglevel='WARNING') as board:
            if board == 1:
                print("✗ Connection failed")
                return 1

            connection_type = "TCP" if use_tcp else "Serial"
            print(f"✓ Connected ({connection_type})")
            time.sleep(1)

            # Enable HITL mode
            print("Enabling HITL mode...")
            hitl_data = struct.pack('<B', 1)
            board.send_RAW_msg(MSP_SIMULATOR, data=list(hitl_data))
            board.receive_msg()
            time.sleep(0.5)

            print(f"Starting GPS injection ({args.profile}) + RC sending...")
            print()

            # Arming sequence: ARM channel must go LOW -> HIGH
            print("Arming sequence:")
            print("  Step 1: Sending ARM channel LOW for 3 seconds...")
            arm_phase_start = time.time()

            # Phase 1: Send ARM LOW for 3 seconds
            while (time.time() - arm_phase_start) < 3.0:
                send_rc(board, throttle=RC_LOW, aux1=RC_LOW)  # ARM channel LOW
                time.sleep(0.02)

            print("  Step 2: Switching ARM channel HIGH...")
            arm_start = time.time()
            armed = False
            last_status_print = 0

            # Phase 2: Send ARM HIGH and wait for arming
            while not armed and (time.time() - arm_start) < 15.0:
                send_rc(board, throttle=RC_LOW, aux1=RC_HIGH)  # ARM channel HIGH
                time.sleep(0.02)

                # Check arming status every 1s
                elapsed = time.time() - arm_start
                if elapsed - last_status_print >= 1.0:
                    board.send_RAW_msg(0x2000, data=[])
                    try:
                        board.receive_msg()
                        mode = board.CONFIG.get('mode', 0)
                        flags = board.CONFIG.get('armingDisableFlags', 0)
                        armed = (mode & 0x01) != 0

                        if not armed:
                            print(f"  t={elapsed:.1f}s: flags=0x{flags:04X}", end='')
                            # Decode key flags
                            if flags & 0x04000:
                                print(" [RC_LINK]", end='')
                            if flags & 0x40000:
                                print(" [MSP]", end='')
                            if flags & 0x00080:
                                print(" [ARM_SWITCH]", end='')
                            print()

                        last_status_print = elapsed
                    except:
                        pass

            if armed:
                print("✓ FC is ARMED!")
            else:
                print("✗ FC failed to arm - check ARM mode configuration")
                print("  Final flags: 0x{:04X}".format(board.CONFIG.get('armingDisableFlags', 0)))
                return 1

            print()

            start_time = time.time()
            iteration = 0

            # RC at 50Hz, GPS at 10Hz
            rc_interval = 0.02  # 50Hz
            gps_interval = 0.1  # 10Hz
            last_rc = 0
            last_gps = 0

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
                    last_gps = current_time
                    iteration += 1

                    # Print every 5 GPS updates (0.5s)
                    if iteration % 5 == 0:
                        print(f"[{elapsed:5.1f}s] Alt: {altitude_m:6.1f}m")

                time.sleep(0.001)  # Small sleep to prevent busy loop

            print()
            print(f"✓ Completed {iteration} GPS updates over {args.duration}s")
            return 0

    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
