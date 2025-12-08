#!/usr/bin/env python3
"""
CRSF Telemetry Stream Parser and Validator

Connects to INAV SITL, captures CRSF telemetry frames, and validates:
- Frame structure and CRC
- Frame boundaries
- Adjacent frame integrity
- Missing sensor handling
"""

import socket
import struct
import sys
from typing import List, Tuple, Optional

# CRSF Constants
CRSF_ADDRESS_BROADCAST = 0x00
CRSF_ADDRESS_FLIGHT_CONTROLLER = 0xC8
CRSF_PAYLOAD_SIZE_MAX = 62
CRSF_FRAME_SIZE_MAX = 64

# Frame types
CRSF_FRAMETYPE_GPS = 0x02
CRSF_FRAMETYPE_VARIO_SENSOR = 0x07
CRSF_FRAMETYPE_BATTERY_SENSOR = 0x08
CRSF_FRAMETYPE_BAROMETER_ALTITUDE = 0x09
CRSF_FRAMETYPE_AIRSPEED_SENSOR = 0x0A
CRSF_FRAMETYPE_RPM = 0x0C
CRSF_FRAMETYPE_TEMP = 0x0D
CRSF_FRAMETYPE_ATTITUDE = 0x1E

FRAME_NAMES = {
    0x02: "GPS",
    0x07: "VARIO",
    0x08: "BATTERY",
    0x09: "BAROMETER",
    0x0A: "AIRSPEED",
    0x0C: "RPM",
    0x0D: "TEMPERATURE",
    0x1E: "ATTITUDE",
}

def crc8_dvb_s2(crc: int, data: bytes) -> int:
    """Calculate CRC8 DVB-S2 (matches INAV implementation)"""
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0xD5) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc

class CRSFFrame:
    """Parsed CRSF frame"""
    def __init__(self, address: int, frame_type: int, payload: bytes, crc: int, valid: bool):
        self.address = address
        self.type = frame_type
        self.payload = payload
        self.crc = crc
        self.valid = valid
        self.size = 2 + 1 + len(payload) + 1  # addr + len + type + payload + crc

    def __str__(self):
        name = FRAME_NAMES.get(self.type, f"UNKNOWN(0x{self.type:02X})")
        status = "✓" if self.valid else "✗ CRC FAIL"
        return f"[{status}] {name:12s} addr=0x{self.address:02X} len={len(self.payload):2d} crc=0x{self.crc:02X}"

def parse_frame(data: bytes) -> Optional[Tuple[CRSFFrame, int]]:
    """
    Parse a CRSF frame from byte stream.
    Returns (frame, bytes_consumed) or None if not enough data.
    """
    if len(data) < 4:  # Minimum: addr + len + type + crc
        return None

    address = data[0]
    length = data[1]

    # Validate length
    if length < 2:  # At least type + crc
        print(f"ERROR: Invalid length {length} (must be >= 2)")
        return None, 1  # Skip 1 byte and try again

    if length > CRSF_PAYLOAD_SIZE_MAX + 2:
        print(f"ERROR: Length {length} exceeds max {CRSF_PAYLOAD_SIZE_MAX + 2}")
        return None, 1

    frame_size = 2 + length  # addr + len + length bytes

    if len(data) < frame_size:
        return None  # Need more data

    frame_type = data[2]
    payload_size = length - 2  # Subtract type and crc
    payload = data[3:3+payload_size]
    crc = data[2 + length]

    # Validate CRC (covers type + payload)
    calculated_crc = crc8_dvb_s2(0, data[2:2+length])
    valid = (calculated_crc == crc)

    frame = CRSFFrame(address, frame_type, payload, crc, valid)
    return frame, frame_size

def connect_to_sitl(uart_num: int = 2) -> socket.socket:
    """
    Connect to SITL UART via TCP.
    UART2 is typically used for CRSF telemetry (port 5761).
    """
    port = 5760 + (uart_num - 1)  # UART1=5760, UART2=5761, etc.
    print(f"Connecting to SITL UART{uart_num} on port {port}...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)

    try:
        sock.connect(('127.0.0.1', port))
        print(f"✓ Connected to 127.0.0.1:{port}")
        return sock
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)

def main():
    import sys
    print("=" * 70)
    print("CRSF Telemetry Stream Parser - PR #11025 Testing")
    print("=" * 70)

    # Try UART1 first, then UART2
    uart_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    sock = connect_to_sitl(uart_num=uart_num)

    buffer = bytearray()
    frames_received = []
    frame_count = 0
    error_count = 0
    frame_types_seen = set()

    print("\nListening for CRSF frames... (Press Ctrl+C to stop)\n")

    try:
        while True:
            # Read data from SITL
            try:
                data = sock.recv(4096)
                if not data:
                    print("Connection closed by SITL")
                    break

                buffer.extend(data)
            except socket.timeout:
                continue

            # Parse all complete frames in buffer
            while len(buffer) >= 4:
                result = parse_frame(buffer)

                if result is None:
                    break  # Need more data

                frame, consumed = result

                if frame is None:
                    # Parse error, skip one byte
                    buffer = buffer[consumed:]
                    error_count += 1
                    continue

                # Got a valid frame
                print(f"#{frame_count:04d} {frame}")

                if not frame.valid:
                    error_count += 1
                    print(f"  ERROR: CRC mismatch! Expected 0x{frame.crc:02X}")

                frames_received.append(frame)
                frame_types_seen.add(frame.type)
                frame_count += 1

                # Remove consumed bytes
                buffer = buffer[consumed:]

                # Check for frame boundary corruption
                if len(buffer) > 0 and consumed > 0:
                    # Next byte should be a valid address
                    next_addr = buffer[0]
                    if next_addr not in [CRSF_ADDRESS_BROADCAST, CRSF_ADDRESS_FLIGHT_CONTROLLER]:
                        print(f"  WARNING: Invalid address 0x{next_addr:02X} at frame boundary!")

                # Report every 10 frames
                if frame_count % 10 == 0:
                    print(f"\n--- Stats: {frame_count} frames, {error_count} errors, Types seen: {sorted(frame_types_seen)} ---\n")

    except KeyboardInterrupt:
        print("\n\nStopped by user.")

    finally:
        sock.close()

    # Final report
    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)
    print(f"Total frames received: {frame_count}")
    print(f"Errors detected: {error_count}")
    print(f"Frame types seen: {', '.join(FRAME_NAMES.get(t, f'0x{t:02X}') for t in sorted(frame_types_seen))}")

    # Check for new frame types from PR #11025
    new_frames = {0x0A, 0x0C, 0x0D}  # Airspeed, RPM, Temperature
    found_new = new_frames & frame_types_seen

    if found_new:
        print(f"\n✓ NEW FRAMES from PR #11025 detected: {', '.join(FRAME_NAMES[t] for t in sorted(found_new))}")
    else:
        print(f"\n⚠ No new frames from PR #11025 detected yet (Airspeed, RPM, Temp)")

    print("\nFrame boundary integrity: ", end="")
    if error_count == 0:
        print("✓ PASS - No corruption detected")
    else:
        print(f"✗ FAIL - {error_count} errors detected")

if __name__ == "__main__":
    main()
