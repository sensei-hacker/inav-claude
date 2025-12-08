#!/usr/bin/env python3
"""
Simple MSP RC debug script to diagnose why MSP_SET_RAW_RC isn't working.

This script:
1. Connects to SITL
2. Sends MSP_SET_RAW_RC with known values
3. Immediately queries MSP_RC to see if values are reflected
4. Monitors if rxSignalReceived changes

Usage:
    python3 msp_rc_debug.py [port]
"""

import socket
import struct
import time
import sys

# MSP constants
MSP_RC = 105
MSP_SET_RAW_RC = 200
MSP_STATUS_EX = 150

# RC values
RC_MID = 1500
RC_LOW = 1000
RC_HIGH = 2000


def create_msp_packet(code, data=[]):
    """Create MSP v1 packet."""
    size = len(data)
    checksum = size ^ code
    for byte in data:
        checksum ^= byte

    packet = bytes([ord('$'), ord('M'), ord('<'), size, code])
    packet += bytes(data)
    packet += bytes([checksum])
    return packet


def parse_msp_response(sock, timeout=1.0):
    """Parse MSP v1 response."""
    sock.settimeout(timeout)
    try:
        # Read header
        header = sock.recv(5)
        if len(header) < 5:
            return None, None

        if header[0:3] != b'$M>':
            print(f"    Invalid header: {header}")
            return None, None

        size = header[3]
        code = header[4]

        # Read data + checksum
        data = sock.recv(size + 1) if size > 0 else sock.recv(1)

        return code, data[:-1] if size > 0 else []

    except socket.timeout:
        return None, None


def send_rc_data(sock, channels, verbose=True):
    """Send MSP_SET_RAW_RC with given channels and consume response."""
    data = []
    for ch in channels:
        data.extend([ch & 0xFF, (ch >> 8) & 0xFF])

    packet = create_msp_packet(MSP_SET_RAW_RC, data)
    sock.sendall(packet)
    if verbose:
        print(f"  Sent MSP_SET_RAW_RC: {channels[:8]}")

    # Consume the acknowledgment response
    code, _ = parse_msp_response(sock, timeout=0.2)
    if verbose and code is not None:
        print(f"    -> Got response code {code}")


def query_rc(sock):
    """Query MSP_RC to read current RC values."""
    packet = create_msp_packet(MSP_RC, [])
    sock.sendall(packet)

    code, data = parse_msp_response(sock)
    if code == MSP_RC and data:
        channels = []
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                channels.append(data[i] | (data[i+1] << 8))
        print(f"  MSP_RC response: {channels[:8]}")
        return channels
    else:
        print(f"  MSP_RC: No data (code={code})")
        return None


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5761

    print(f"Connecting to SITL on port {port}...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', port))
    print("Connected!")

    # Test RC values
    test_channels = [
        RC_MID,   # Roll
        RC_MID,   # Pitch
        RC_MID,   # Yaw
        RC_LOW,   # Throttle
        RC_HIGH,  # AUX1
        RC_MID,   # AUX2
        RC_MID,   # AUX3
        RC_MID,   # AUX4
        RC_MID, RC_MID, RC_MID, RC_MID,  # AUX5-8
        RC_MID, RC_MID, RC_MID, RC_MID,  # AUX9-12
    ]

    print("\n[Test 1] Query RC before sending any data:")
    query_rc(sock)

    print("\n[Test 2] Send MSP_SET_RAW_RC once, then query:")
    send_rc_data(sock, test_channels)
    time.sleep(0.1)
    query_rc(sock)

    print("\n[Test 3] Send MSP_SET_RAW_RC 10 times at 50ms intervals:")
    for i in range(10):
        send_rc_data(sock, test_channels)
        time.sleep(0.05)

    print("\n[Test 4] Query RC after continuous sending:")
    query_rc(sock)

    print("\n[Test 5] Query RC 5 times over 500ms (while sending):")
    for i in range(5):
        send_rc_data(sock, test_channels)
        time.sleep(0.05)
        query_rc(sock)
        time.sleep(0.05)

    print("\n[Test 6] Check status flags:")
    packet = create_msp_packet(MSP_STATUS_EX, [])
    sock.sendall(packet)
    code, data = parse_msp_response(sock)
    if data and len(data) >= 17:
        # armingDisableFlags is at offset 13, 2 bytes
        arming_flags = data[13] | (data[14] << 8)
        print(f"  armingDisableFlags: 0x{arming_flags:04X}")
        if arming_flags & (1 << 18 >> 16):  # RC_LINK bit in 16-bit field
            print("  -> RC_LINK blocker is SET (no valid RC)")
        else:
            print("  -> RC_LINK blocker is CLEAR")

    sock.close()
    print("\nDone.")


if __name__ == '__main__':
    main()
