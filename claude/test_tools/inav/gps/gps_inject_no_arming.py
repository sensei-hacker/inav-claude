#!/usr/bin/env python3
"""
GPS Injection Without Arming

Injects GPS data via MSP without attempting to arm.
Use with blackbox_arm_control = -1 to log from boot.

Usage:
    python3 gps_inject_no_arming.py --port /dev/ttyACM0 --profile climb --duration 30
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

# MSP commands
MSP_SET_RAW_GPS = 201
MSP_SIMULATOR = 0x201F


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
    parser = argparse.ArgumentParser(description='GPS injection without arming (for blackbox_arm_control = -1)')
    parser.add_argument('--profile', choices=['climb', 'descent', 'hover', 'sine'],
                        default='climb', help='Motion profile (default: climb)')
    parser.add_argument('--duration', type=int, default=30,
                        help='Duration in seconds (default: 30)')
    parser.add_argument('--port', type=str, default='5760',
                        help='MSP port (default: 5760 for TCP, or /dev/ttyACM0 for serial)')

    args = parser.parse_args()

    print("=" * 70)
    print("GPS Injection (No Arming Required)")
    print("=" * 70)
    print(f"\nProfile: {args.profile}")
    print(f"Duration: {args.duration}s")
    print(f"MSP Port: {args.port}")
    print()
    print("⚠️  IMPORTANT: Blackbox must be configured with:")
    print("   blackbox_arm_control = -1 (log from boot)")
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
            try:
                board.receive_msg()
            except:
                pass
            time.sleep(0.5)

            print(f"Starting GPS injection ({args.profile})...")
            print()
            print("Note: FC does NOT need to be armed!")
            print("      Blackbox will log if blackbox_arm_control = -1")
            print()

            start_time = time.time()
            iteration = 0

            # GPS at 10Hz
            gps_interval = 0.1
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
            print()
            print("Next steps:")
            print("1. Download blackbox log via INAV Configurator → Logging tab")
            print("2. Decode: blackbox_decode <file.TXT>")
            print("3. Analyze navEPH frequency spectrum")
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
