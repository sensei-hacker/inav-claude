#!/usr/bin/env python3
"""
MSP Mock Responder - Simulates INAV firmware responding to MSP requests

This script acts as a mock flight controller, receiving MSP requests
and sending back valid responses to test the benchmark client.
"""

import serial
import struct
import sys
import time

# MSP message format
MSP_HEADER_REQUEST = b'$M<'
MSP_HEADER_RESPONSE = b'$M>'

# MSP commands and their typical response sizes
MSP_RESPONSES = {
    100: b'\x07INAV900',  # MSP_IDENT - 7 bytes (multiWiiVersion, multiType, MSP_VERSION, capability, 7 bytes total)
    101: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',  # MSP_STATUS - 11 bytes
    102: b'\x00\x00' * 9,  # MSP_RAW_IMU - 18 bytes (9 int16 values)
    103: b'\x00\x00' * 8,  # MSP_SERVO - 16 bytes (8 servos)
    104: b'\x00\x00' * 8,  # MSP_MOTOR - 16 bytes (8 motors)
    105: b'\x00\x00' * 8,  # MSP_RC - 16 bytes (8 channels)
    106: b'\x00' * 16,     # MSP_RAW_GPS - 16 bytes
    107: b'\x00' * 5,      # MSP_COMP_GPS - 5 bytes
    108: b'\x00\x00\x00\x00\x00\x00',  # MSP_ATTITUDE - 6 bytes (roll, pitch, yaw)
    109: b'\x00\x00\x00\x00',  # MSP_ALTITUDE - 4 bytes
    110: b'\x00\x00\x00\x00\x00\x00\x00',  # MSP_ANALOG - 7 bytes
    114: b'\x00' * 22,     # MSP_MISC - 22 bytes
    119: b'\x00' * 10,     # MSP_BOXIDS - 10 bytes
}


def calculate_checksum(size: int, cmd: int, data: bytes = b'') -> int:
    """Calculate MSPv1 checksum (XOR)"""
    checksum = size ^ cmd
    for byte in data:
        checksum ^= byte
    return checksum


def build_msp_response(cmd: int, data: bytes) -> bytes:
    """Build MSPv1 response packet"""
    size = len(data)
    checksum = calculate_checksum(size, cmd, data)
    return MSP_HEADER_RESPONSE + struct.pack('BB', size, cmd) + data + struct.pack('B', checksum)


def parse_msp_request(data: bytes) -> tuple:
    """
    Parse MSP request from buffer.
    Returns: (cmd, consumed_bytes) or (None, 0) if incomplete
    """
    if len(data) < 6:  # Minimum MSP packet size
        return None, 0

    # Look for MSP header
    if data[0:3] != MSP_HEADER_REQUEST:
        return None, 1  # Skip this byte

    size = data[3]
    cmd = data[4]

    # Check if we have the full packet
    packet_len = 3 + 1 + 1 + size + 1  # header + size + cmd + data + checksum
    if len(data) < packet_len:
        return None, 0  # Need more data

    # Extract and verify checksum
    expected_checksum = calculate_checksum(size, cmd, data[5:5+size])
    actual_checksum = data[5 + size]

    if expected_checksum != actual_checksum:
        print(f"[MOCK] Checksum error: cmd={cmd}, expected={expected_checksum}, got={actual_checksum}")
        return None, packet_len  # Skip bad packet

    return cmd, packet_len


def run_mock_responder(port_name: str, baudrate: int, verbose: bool = False):
    """Run the mock MSP responder"""

    ser = serial.Serial(port_name, baudrate, timeout=0.01)

    try:
        print(f"[MOCK] Mock INAV responder listening on {port_name} at {baudrate} baud")
        print(f"[MOCK] Press Ctrl+C to stop")

        buffer = b''
        requests_received = 0
        responses_sent = 0

        while True:
            # Read incoming data
            chunk = ser.read(1024)
            if chunk:
                buffer += chunk

            # Process all complete requests in buffer
            while len(buffer) >= 6:
                cmd, consumed = parse_msp_request(buffer)

                if consumed > 0:
                    buffer = buffer[consumed:]

                    if cmd is not None:
                        requests_received += 1

                        # Send response
                        if cmd in MSP_RESPONSES:
                            response_data = MSP_RESPONSES[cmd]
                            response_packet = build_msp_response(cmd, response_data)
                            ser.write(response_packet)
                            responses_sent += 1

                            if verbose and responses_sent % 50 == 0:
                                print(f"[MOCK] Requests: {requests_received}, Responses: {responses_sent}")
                        else:
                            print(f"[MOCK] Unknown command: {cmd}")
                else:
                    break  # Need more data

            # Prevent buffer from growing too large
            if len(buffer) > 10000:
                print(f"[MOCK] WARNING: Buffer overflow, clearing {len(buffer)} bytes")
                buffer = b''

            time.sleep(0.001)  # Small sleep to prevent CPU spinning

    except KeyboardInterrupt:
        print(f"\n[MOCK] Stopped. Total requests: {requests_received}, responses: {responses_sent}")

    finally:
        ser.close()


def main():
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = '/dev/ttyACM0'

    if len(sys.argv) > 2:
        baudrate = int(sys.argv[2])
    else:
        baudrate = 115200

    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    try:
        run_mock_responder(port, baudrate, verbose)
    except KeyboardInterrupt:
        print("\n[MOCK] Interrupted by user")
        sys.exit(0)


if __name__ == '__main__':
    main()
