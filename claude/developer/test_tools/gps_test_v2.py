#!/usr/bin/env python3
"""
Mock MSP GPS sender for testing GPS recovery after signal loss.

This tool sends MSP_SET_RAW_GPS messages to a SITL or real flight controller
to simulate GPS fix, loss, and recovery scenarios.

Usage:
    python3 mock_msp_gps.py /dev/ttyUSB0  # For real FC
    python3 mock_msp_gps.py localhost:5760  # For SITL TCP

Test scenario:
    1. Sends GPS fix for 10 seconds (establishes home position)
    2. Sends GPS loss for 5 seconds (simulates signal loss)
    3. Sends GPS fix recovery for 10 seconds
    4. Monitor if distance-to-home recovers properly
"""

import struct
import socket
import serial
import time
import sys
import argparse

# MSP protocol constants
MSP_SET_RAW_GPS = 201
MSP_RAW_GPS = 106  # Request GPS data including distance to home
MSP_COMP_GPS = 107  # Request distance/direction to home

def calculate_crc(data):
    """Calculate MSP v1 checksum (XOR of all bytes)."""
    crc = 0
    for b in data:
        crc ^= b
    return crc

def create_msp_message(cmd, payload):
    """Create an MSP v1 message."""
    header = b'$M<'
    size = len(payload)
    data = bytes([size, cmd]) + payload
    crc = calculate_crc(data)
    return header + data + bytes([crc])

def create_gps_message(fix_type, num_sat, lat, lon, alt_m, ground_speed):
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
    payload = struct.pack('<BBiiHH',
        fix_type,
        num_sat,
        lat,
        lon,
        alt_m,
        ground_speed
    )
    return create_msp_message(MSP_SET_RAW_GPS, payload)

class MSPConnection:
    """Handle MSP connection over serial or TCP."""

    def __init__(self, target):
        self.target = target
        self.conn = None

    def connect(self):
        if ':' in self.target:
            # TCP connection (SITL)
            host, port = self.target.split(':')
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((host, int(port)))
            self.conn.settimeout(1.0)
            print(f"Connected to SITL at {self.target}")
        else:
            # Serial connection
            self.conn = serial.Serial(self.target, 115200, timeout=1)
            print(f"Connected to serial port {self.target}")

    def send(self, data):
        if isinstance(self.conn, socket.socket):
            self.conn.send(data)
        else:
            self.conn.write(data)

    def recv(self, size):
        if isinstance(self.conn, socket.socket):
            return self.conn.recv(size)
        else:
            return self.conn.read(size)

    def query_distance_to_home(self):
        """Query MSP_COMP_GPS to get distance and direction to home."""
        # Send MSP request (no payload)
        msg = create_msp_message(MSP_COMP_GPS, b'')
        self.send(msg)

        try:
            # Read response header
            header = self.recv(3)
            if header != b'$M>':
                return None, None

            # Read size and command
            size = self.recv(1)[0]
            cmd = self.recv(1)[0]

            if cmd != MSP_COMP_GPS or size != 5:
                # Drain remaining bytes
                self.recv(size + 1)
                return None, None

            # Read payload: distance (u16), direction (u16), update (u8)
            payload = self.recv(size)
            crc = self.recv(1)[0]

            distance = struct.unpack('<H', payload[0:2])[0]
            direction = struct.unpack('<H', payload[2:4])[0]

            return distance, direction
        except Exception as e:
            return None, None

    def close(self):
        if self.conn:
            self.conn.close()

def run_gps_recovery_test(connection, base_lat, base_lon, base_alt):
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
        # Simulate slight movement
        elapsed = time.time() - start_time
        lat = base_lat + int(elapsed * 100)  # Drift north slightly
        lon = base_lon + int(elapsed * 50)   # Drift east slightly

        msg = create_gps_message(
            fix_type=2,       # 3D fix
            num_sat=12,
            lat=lat,
            lon=lon,
            alt_m=base_alt,
            ground_speed=500  # 5 m/s
        )
        connection.send(msg)
        time.sleep(0.1)  # 10 Hz

    # Query distance to home
    time.sleep(0.5)
    dist, direction = connection.query_distance_to_home()
    print(f"  -> GPS fix established. Distance to home: {dist}m, direction: {direction}")

    # Phase 2: GPS signal loss
    print("\n[Phase 2] Simulating GPS loss for 5 seconds...")
    start_time = time.time()
    while time.time() - start_time < 5:
        msg = create_gps_message(
            fix_type=0,       # No fix
            num_sat=0,
            lat=0,
            lon=0,
            alt_m=0,
            ground_speed=0
        )
        connection.send(msg)
        time.sleep(0.1)

    # Query distance to home after loss
    time.sleep(0.5)
    dist, direction = connection.query_distance_to_home()
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

        msg = create_gps_message(
            fix_type=2,       # 3D fix
            num_sat=10,
            lat=lat,
            lon=lon,
            alt_m=base_alt + 10,  # Slightly different altitude
            ground_speed=300  # 3 m/s
        )
        connection.send(msg)
        time.sleep(0.1)

    # Query distance to home after recovery - THIS IS THE KEY TEST
    time.sleep(0.5)
    dist, direction = connection.query_distance_to_home()
    print(f"  -> GPS recovered. Distance to home: {dist}m, direction: {direction}")

    print("\n=== Test Complete ===")
    if dist is not None and dist > 0:
        print(f"SUCCESS: Distance to home = {dist}m (non-zero)")
        print("The GPS recovery fix is working correctly.")
    elif dist == 0:
        print("BUG CONFIRMED: Distance to home = 0 (stuck at zero)")
        print("This confirms issue #11049 - GPS recovery bug is present.")
    else:
        print(f"INCONCLUSIVE: Could not read distance (got {dist})")

def run_continuous_gps(connection, base_lat, base_lon, base_alt, duration=60):
    """Send continuous GPS data for manual testing."""
    print(f"\nSending continuous GPS data for {duration} seconds...")
    print("Press Ctrl+C to stop.\n")

    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            # Simulate flying in a circle
            import math
            radius = 1000  # ~10m radius in lat/lon units
            lat = base_lat + int(radius * math.sin(elapsed * 0.5))
            lon = base_lon + int(radius * math.cos(elapsed * 0.5))

            msg = create_gps_message(
                fix_type=2,
                num_sat=12,
                lat=lat,
                lon=lon,
                alt_m=base_alt,
                ground_speed=400
            )
            connection.send(msg)

            if int(elapsed) % 5 == 0 and elapsed - int(elapsed) < 0.1:
                print(f"  Elapsed: {int(elapsed)}s, lat={lat/1e7:.6f}, lon={lon/1e7:.6f}")

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped by user.")

def main():
    parser = argparse.ArgumentParser(description='Mock MSP GPS for testing GPS recovery')
    parser.add_argument('target', help='Serial port or host:port for SITL')
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

    conn = MSPConnection(args.target)
    try:
        conn.connect()

        if args.mode == 'test':
            run_gps_recovery_test(conn, base_lat, base_lon, args.alt)
        else:
            run_continuous_gps(conn, base_lat, base_lon, args.alt, args.duration)

    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        conn.close()

    return 0

if __name__ == '__main__':
    sys.exit(main())
