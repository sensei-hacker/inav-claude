#!/usr/bin/env python3
"""
Simple CRSF Telemetry Reader - Quick Test

Connects to SITL UART2 (port 5761) and reads raw bytes to verify telemetry is transmitting.
This is a minimal test to confirm telemetry frames are being sent.

Usage:
    python3 test_telemetry_simple.py

Expected Output:
    - Connection confirmation
    - Hexdump of received bytes (CRSF frames start with 0xC8)
    - Frame count

Prerequisites:
    - SITL running with CRSF telemetry configured
    - RC sender active on port 5761 (sending RC frames to trigger telemetry)
"""

import socket
import time
import sys

PORT = 5761
TIMEOUT = 10  # seconds

print("=" * 70)
print("SIMPLE CRSF TELEMETRY TEST")
print("=" * 70)
print()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(TIMEOUT)

try:
    print(f"Connecting to 127.0.0.1:{PORT}...")
    sock.connect(('127.0.0.1', PORT))
    print(f"✓ Connected")
    print()
    print(f"Reading for {TIMEOUT} seconds...")
    print("(CRSF frames start with 0xC8)")
    print()

    byte_count = 0
    frame_count = 0
    start_time = time.time()

    while (time.time() - start_time) < TIMEOUT:
        try:
            data = sock.recv(128)
            if data:
                byte_count += len(data)
                # Count potential frame starts (0xC8 = CRSF address)
                frame_count += data.count(0xC8)

                # Print hexdump
                hex_str = ' '.join(f'{b:02X}' for b in data)
                print(f"[{byte_count:04d} bytes] {hex_str}")

        except socket.timeout:
            continue

    print()
    print("=" * 70)
    print(f"Received {byte_count} bytes total")
    print(f"Found {frame_count} potential frame starts (0xC8)")
    print("=" * 70)

except ConnectionRefusedError:
    print(f"✗ Connection refused - is SITL running?")
    sys.exit(1)
except socket.timeout:
    print(f"✗ Connection timeout")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
finally:
    sock.close()
