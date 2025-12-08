#!/usr/bin/env python3
"""
Mock MSP GPS sender for testing GPS recovery after signal loss.

This tool sends MSP_SET_RAW_GPS messages to a SITL or real flight controller
to simulate GPS fix, loss, and recovery scenarios.

Uses the uNAVlib library for proper MSP communication.

Usage:
    python3 mock_msp_gps.py /dev/ttyUSB0  # For real FC
    python3 mock_msp_gps.py 5761  # For SITL TCP (port number only)

Test scenario:
    1. Sends GPS fix for 10 seconds (establishes home position)
    2. Sends GPS loss for 5 seconds (simulates signal loss)
    3. Sends GPS fix recovery for 10 seconds
    4. Monitor if distance-to-home recovers properly

Requirements:
    pip3 install git+https://github.com/xznhj8129/uNAVlib
"""

import struct
import time
import sys
import argparse

# MSP protocol constants
MSP_SET_RAW_GPS = 201
MSP_RAW_GPS = 106
MSP_COMP_GPS = 107


def create_gps_payload(fix_type, num_sat, lat, lon, alt_m, ground_speed):
    """
    Create MSP_SET_RAW_GPS payload.

    Args:
        fix_type: 0=no fix, 1=2D, 2=3D
        num_sat: number of satellites
        lat: latitude in degrees * 10^7 (e.g., 51.5074 -> 515074000)
        lon: longitude in degrees * 10^7 (e.g., -0.1278 -> -1278000)
        alt_m: altitude in meters
        ground_speed: ground speed in cm/s
    """
    return list(struct.pack('<BBiiHH',
        fix_type,
        num_sat,
        lat,
        lon,
        alt_m,
        ground_speed
    ))


def run_gps_recovery_test(board, base_lat, base_lon, base_alt):
    """
    Run the GPS recovery test scenario.

    Simulates:
    1. Normal GPS operation (establishes home)
    2. GPS signal loss
    3. GPS signal recovery
    """

    print("\n=== GPS Recovery Test ===")
    print(f"Base position: lat={base_lat/1e7:.6f}, lon={base_lon/1e7:.6f}, alt={base_alt}m")

    # Phase 1: Normal GPS operation - establish home
    print("\n[Phase 1] Sending GPS fix for 10 seconds (establish home position)...")
    start_time = time.time()
    while time.time() - start_time < 10:
        elapsed = time.time() - start_time
        lat = base_lat + int(elapsed * 100)  # Drift north slightly
        lon = base_lon + int(elapsed * 50)   # Drift east slightly

        payload = create_gps_payload(
            fix_type=2,       # 3D fix
            num_sat=12,
            lat=lat,
            lon=lon,
            alt_m=base_alt,
            ground_speed=500  # 5 m/s
        )
        board.send_RAW_msg(MSP_SET_RAW_GPS, data=payload)
        time.sleep(0.1)  # 10 Hz

    # Query distance to home
    time.sleep(0.5)
    board.send_RAW_msg(MSP_COMP_GPS, data=[])
    dataHandler = board.receive_msg()
    board.process_recv_data(dataHandler)
    dist = board.GPS_DATA.get('distanceToHome', None)
    direction = board.GPS_DATA.get('directionToHome', None)
    print(f"  -> GPS fix established. Distance to home: {dist}m, direction: {direction}")
    phase1_dist = dist

    # Phase 2: GPS signal loss
    print("\n[Phase 2] Simulating GPS loss for 5 seconds...")
    start_time = time.time()
    while time.time() - start_time < 5:
        payload = create_gps_payload(
            fix_type=0,       # No fix
            num_sat=0,
            lat=0,
            lon=0,
            alt_m=0,
            ground_speed=0
        )
        board.send_RAW_msg(MSP_SET_RAW_GPS, data=payload)
        time.sleep(0.1)

    # Query distance to home after loss
    time.sleep(0.5)
    board.send_RAW_msg(MSP_COMP_GPS, data=[])
    dataHandler = board.receive_msg()
    board.process_recv_data(dataHandler)
    dist = board.GPS_DATA.get('distanceToHome', None)
    print(f"  -> GPS lost. Distance to home: {dist}m (may still show last known)")

    # Phase 3: GPS recovery
    print("\n[Phase 3] Sending GPS fix recovery for 10 seconds...")
    # Simulate having moved during GPS loss
    recovery_lat = base_lat + 5000  # ~50m north
    recovery_lon = base_lon + 3000  # ~30m east

    start_time = time.time()
    while time.time() - start_time < 10:
        elapsed = time.time() - start_time
        lat = recovery_lat + int(elapsed * 50)
        lon = recovery_lon + int(elapsed * 30)

        payload = create_gps_payload(
            fix_type=2,       # 3D fix
            num_sat=10,
            lat=lat,
            lon=lon,
            alt_m=base_alt + 10,  # Slightly different altitude
            ground_speed=300  # 3 m/s
        )
        board.send_RAW_msg(MSP_SET_RAW_GPS, data=payload)
        time.sleep(0.1)

    # Query distance to home after recovery - THIS IS THE KEY TEST
    time.sleep(0.5)
    board.send_RAW_msg(MSP_COMP_GPS, data=[])
    dataHandler = board.receive_msg()
    board.process_recv_data(dataHandler)
    dist = board.GPS_DATA.get('distanceToHome', None)
    direction = board.GPS_DATA.get('directionToHome', None)
    print(f"  -> GPS recovered. Distance to home: {dist}m, direction: {direction}")

    print("\n=== Test Complete ===")
    if dist is not None and dist > 0:
        print(f"SUCCESS: Distance to home = {dist}m (non-zero)")
        print("The GPS recovery fix is working correctly.")
        return True
    elif dist == 0:
        print("BUG CONFIRMED: Distance to home = 0 (stuck at zero)")
        print("This confirms issue #11049 - GPS recovery bug is present.")
        return False
    else:
        print(f"INCONCLUSIVE: Could not read distance (got {dist})")
        return None


def run_continuous_gps(board, base_lat, base_lon, base_alt, duration=60):
    """Send continuous GPS data for manual testing."""
    import math

    print(f"\nSending continuous GPS data for {duration} seconds...")
    print("Press Ctrl+C to stop.\n")

    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            # Simulate flying in a circle
            radius = 1000  # ~10m radius in lat/lon units
            lat = base_lat + int(radius * math.sin(elapsed * 0.5))
            lon = base_lon + int(radius * math.cos(elapsed * 0.5))

            payload = create_gps_payload(
                fix_type=2,
                num_sat=12,
                lat=lat,
                lon=lon,
                alt_m=base_alt,
                ground_speed=400
            )
            board.send_RAW_msg(MSP_SET_RAW_GPS, data=payload)

            if int(elapsed) % 5 == 0 and elapsed - int(elapsed) < 0.1:
                # Query GPS data periodically
                board.send_RAW_msg(MSP_COMP_GPS, data=[])
                dataHandler = board.receive_msg()
                board.process_recv_data(dataHandler)
                dist = board.GPS_DATA.get('distanceToHome', 'N/A')
                print(f"  Elapsed: {int(elapsed)}s, lat={lat/1e7:.6f}, lon={lon/1e7:.6f}, dist_home={dist}m")

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped by user.")


def main():
    parser = argparse.ArgumentParser(description='Mock MSP GPS for testing GPS recovery (uses uNAVlib)')
    parser.add_argument('target', help='Serial port or TCP port number for SITL')
    parser.add_argument('--lat', type=float, default=51.5074,
                        help='Base latitude in degrees (default: 51.5074 - London)')
    parser.add_argument('--lon', type=float, default=-0.1278,
                        help='Base longitude in degrees (default: -0.1278 - London)')
    parser.add_argument('--alt', type=int, default=100,
                        help='Base altitude in meters (default: 100)')
    parser.add_argument('--mode', choices=['test', 'continuous'], default='test',
                        help='Mode: test (GPS loss/recovery) or continuous')
    parser.add_argument('--duration', type=int, default=60,
                        help='Duration for continuous mode in seconds')

    args = parser.parse_args()

    # Convert lat/lon to INAV format (degrees * 10^7)
    base_lat = int(args.lat * 1e7)
    base_lon = int(args.lon * 1e7)

    # Import uNAVlib
    try:
        from unavlib.main import MSPy
    except ImportError:
        print("Error: uNAVlib not installed. Install with:")
        print("  pip3 install git+https://github.com/xznhj8129/uNAVlib")
        return 1

    # Determine if TCP or serial
    try:
        port = int(args.target)
        use_tcp = True
        device = str(port)
    except ValueError:
        use_tcp = False
        device = args.target

    print(f"Connecting to {'TCP port' if use_tcp else 'serial'} {device}...")

    try:
        with MSPy(device=device, use_tcp=use_tcp, loglevel='WARNING') as board:
            if board == 1:
                print(f"Error: Could not connect to {device}")
                return 1

            print(f"Connected! FC: {board.CONFIG.get('flightControllerIdentifier', 'Unknown')}")
            print(f"API Version: {board.CONFIG.get('apiVersion', 'Unknown')}")

            if args.mode == 'test':
                result = run_gps_recovery_test(board, base_lat, base_lon, args.alt)
                return 0 if result else 1
            else:
                run_continuous_gps(board, base_lat, base_lon, args.alt, args.duration)
                return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
