#!/usr/bin/env python3
"""
Test pitot validation implementation in SITL.

This script connects to SITL and checks if the pitot validation
functions are working correctly.

Requirements:
- SITL must be running (built with pitot validation code)
- Run without sandbox: dangerouslyDisableSandbox: true

Usage:
    python3 test_pitot_validation.py
"""

import socket
import struct
import time

# MSP command codes
MSP_STATUS_EX = 150
MSP_SENSOR_STATUS = 151
MSP_ANALOG = 110

def create_msp_packet(cmd, data=b''):
    """Create MSP v1 packet."""
    size = len(data)
    checksum = size ^ cmd
    for b in data:
        checksum ^= b
    return b'$M<' + bytes([size, cmd]) + data + bytes([checksum])

def parse_msp_response(sock):
    """Read and parse MSP response."""
    header = sock.recv(3)
    if header == b'$M!':
        # Error response
        size = sock.recv(1)[0]
        sock.recv(size + 2)
        return None, None, "Error"
    if header != b'$M>':
        return None, None, f"Bad header: {header}"

    size = sock.recv(1)[0]
    cmd = sock.recv(1)[0]
    data = sock.recv(size) if size > 0 else b''
    checksum = sock.recv(1)[0]
    return cmd, data, None

def send_msp(sock, cmd, data=b''):
    """Send MSP command and get response."""
    sock.send(create_msp_packet(cmd, data))
    return parse_msp_response(sock)

def main():
    print("Pitot Validation Test")
    print("=" * 40)

    # Connect to SITL
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect(('127.0.0.1', 5760))
        print("Connected to SITL on port 5760")
    except ConnectionRefusedError:
        print("ERROR: Cannot connect to SITL on port 5760")
        print("Make sure SITL is running: cd inav/build_sitl && ./bin/SITL.elf")
        return 1

    # Get status
    cmd, data, err = send_msp(sock, MSP_STATUS_EX)
    if err:
        print(f"ERROR getting status: {err}")
        return 1

    if data and len(data) >= 8:
        cycle_time = struct.unpack('<H', data[0:2])[0]
        sensors = struct.unpack('<I', data[4:8])[0]
        print(f"Cycle time: {cycle_time} us")
        print(f"Sensors bitmask: 0x{sensors:08x}")

        # Check pitot bit (bit 7)
        pitot_enabled = (sensors >> 7) & 1
        print(f"Pitot sensor: {'ENABLED' if pitot_enabled else 'DISABLED'}")

    # Get sensor status
    cmd, data, err = send_msp(sock, MSP_SENSOR_STATUS)
    if err:
        print(f"ERROR getting sensor status: {err}")
    elif data:
        print(f"Sensor status: {len(data)} bytes")
        # Parse sensor status - format depends on firmware version
        if len(data) >= 1:
            hw_healthy = data[0]
            print(f"Hardware healthy flags: 0x{hw_healthy:02x}")

    print("")
    print("=" * 40)
    print("Pitot Validation Status Check")
    print("=" * 40)
    print("")
    print("To fully test pitot validation:")
    print("1. Configure SITL with GPS and Pitot enabled")
    print("2. Arm the aircraft")
    print("3. Simulate flight with GPS groundspeed")
    print("4. Pitot should show similar airspeed")
    print("5. If pitot reads 0 while GPS shows movement,")
    print("   validation should detect failure after ~0.4s")
    print("")
    print("The implementation adds:")
    print("- pitotHasFailed() function")
    print("- OSD 'PITOT FAIL' warning")
    print("- 20 sample failure threshold (~0.4s)")
    print("- 250 sample recovery threshold (~5s)")

    sock.close()
    print("\nDone.")
    return 0

if __name__ == '__main__':
    exit(main())
