#!/usr/bin/env python3
"""
MSP Debug Script - Raw MSP communication test.
Tests MSP protocol directly without uNAVlib processing.
"""

import socket
import struct
import time
import sys

# MSP constants
MSP_RC = 105
MSP_RX_CONFIG = 44
MSP_STATUS_EX = 150
MSP2_INAV_STATUS = 0x2000

def crc8_dvb_s2(data):
    """Calculate CRC8 DVB-S2 checksum."""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0xD5
            else:
                crc <<= 1
            crc &= 0xFF
    return crc

def make_msp1_request(code):
    """Create MSP v1 request packet."""
    # MSP v1: $M<  direction, size, code, checksum
    # direction: '<' (60) for request from host
    size = 0
    checksum = size ^ code
    return bytes([ord('$'), ord('M'), ord('<'), size, code, checksum])

def make_msp2_request(code):
    """Create MSP v2 request packet."""
    # MSP v2: $X<  flag, code_lo, code_hi, size_lo, size_hi, [data...], crc8
    flag = 0
    size = 0
    header = bytes([flag, code & 0xFF, (code >> 8) & 0xFF, size & 0xFF, (size >> 8) & 0xFF])
    crc = crc8_dvb_s2(header)
    return bytes([ord('$'), ord('X'), ord('<')]) + header + bytes([crc])

def recv_with_timeout(sock, timeout=0.5):
    """Receive all available data with timeout."""
    sock.settimeout(timeout)
    data = b''
    try:
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            data += chunk
            sock.settimeout(0.1)  # Short timeout for additional data
    except socket.timeout:
        pass
    return data

def parse_msp_response(data):
    """Parse MSP response and extract payload."""
    if len(data) < 6:
        return None, f"Too short: {len(data)} bytes"

    # Check for MSP v1 response: $M> or $M!
    if data[0:2] == b'$M':
        direction = chr(data[2])
        if direction not in ('>', '!'):
            return None, f"Unknown direction: {direction}"

        size = data[3]
        code = data[4]

        if direction == '!':
            return None, f"Error response for code {code}"

        if len(data) < 6 + size:
            return None, f"Incomplete: need {6+size} bytes, got {len(data)}"

        payload = data[5:5+size]
        checksum = data[5+size]

        # Verify checksum
        calc_checksum = size ^ code
        for b in payload:
            calc_checksum ^= b

        if calc_checksum != checksum:
            return None, f"Checksum mismatch: calc={calc_checksum:02X} recv={checksum:02X}"

        return payload, f"MSP v1, code={code}, size={size}"

    # Check for MSP v2 response: $X> or $X!
    elif data[0:2] == b'$X':
        direction = chr(data[2])
        if direction not in ('>', '!'):
            return None, f"Unknown direction: {direction}"

        if len(data) < 9:
            return None, f"MSP v2 too short: {len(data)} bytes"

        flag = data[3]
        code = data[4] | (data[5] << 8)
        size = data[6] | (data[7] << 8)

        if direction == '!':
            return None, f"Error response for code {code}"

        if len(data) < 9 + size:
            return None, f"Incomplete: need {9+size} bytes, got {len(data)}"

        payload = data[8:8+size]
        crc = data[8+size]

        # Verify CRC
        header_for_crc = bytes([flag, code & 0xFF, (code >> 8) & 0xFF,
                                size & 0xFF, (size >> 8) & 0xFF])
        calc_crc = crc8_dvb_s2(header_for_crc + payload)

        if calc_crc != crc:
            return None, f"CRC mismatch: calc={calc_crc:02X} recv={crc:02X}"

        return payload, f"MSP v2, code={code}, size={size}"

    else:
        return None, f"Unknown header: {data[:3].hex()}"

def test_msp_command(sock, name, code, use_v2=False):
    """Send an MSP command and print the response."""
    print(f"\n=== Testing {name} (code {code}, {'MSPv2' if use_v2 else 'MSPv1'}) ===")

    if use_v2:
        request = make_msp2_request(code)
    else:
        request = make_msp1_request(code)

    print(f"Request: {request.hex()}")
    sock.send(request)

    response = recv_with_timeout(sock)
    print(f"Response: {response.hex() if response else '(empty)'} ({len(response)} bytes)")

    if response:
        payload, info = parse_msp_response(response)
        print(f"Parse result: {info}")
        if payload is not None:
            print(f"Payload ({len(payload)} bytes): {payload.hex()}")
            if name == "MSP_RX_CONFIG" and len(payload) >= 24:
                rx_type = payload[23]
                print(f"  receiverType (byte 23): {rx_type}")
            elif name == "MSP_RC" and len(payload) > 0:
                channels = []
                for i in range(min(8, len(payload)//2)):
                    ch = payload[i*2] | (payload[i*2+1] << 8)
                    channels.append(ch)
                print(f"  RC channels: {channels}")

    return response

def make_msp1_command(code, payload):
    """Create MSP v1 command packet with payload."""
    size = len(payload)
    checksum = size ^ code
    for b in payload:
        checksum ^= b
    return bytes([ord('$'), ord('M'), ord('<'), size, code]) + bytes(payload) + bytes([checksum])

def set_rx_config(sock, rx_type=2):
    """Send MSP_SET_RX_CONFIG to set receiver type."""
    MSP_SET_RX_CONFIG = 45

    # Build 24-byte payload (matches fc_msp.c expectations)
    # Use current values from MSP_RX_CONFIG response, just change receiver type
    payload = [
        0,              # byte 0: serialrx_provider
        0x6C, 0x07,     # bytes 1-2: maxcheck = 1900 (little endian)
        0xDC, 0x05,     # bytes 3-4: midrc = 1500 (ignored, but needs value)
        0x4C, 0x04,     # bytes 5-6: mincheck = 1100
        0,              # byte 7: spektrum_sat_bind
        0x75, 0x03,     # bytes 8-9: rx_min_usec = 885
        0x43, 0x08,     # bytes 10-11: rx_max_usec = 2115
        0,              # byte 12: rcInterpolation (ignored)
        0,              # byte 13: rcInterpolationInterval (ignored)
        0, 0,           # bytes 14-15: airModeActivateThreshold (ignored)
        0,              # byte 16: ignored
        0, 0, 0, 0,     # bytes 17-20: ignored u32
        0,              # byte 21: ignored
        0,              # byte 22: fpvCamAngleDegrees (ignored)
        rx_type         # byte 23: receiverType (RX_TYPE_MSP = 2)
    ]

    print(f"\n=== Setting receiver type to {rx_type} ===")
    request = make_msp1_command(MSP_SET_RX_CONFIG, payload)
    print(f"Request: {request.hex()} ({len(payload)} byte payload)")
    sock.send(request)

    response = recv_with_timeout(sock)
    print(f"Response: {response.hex() if response else '(empty)'}")

    return response

def save_config(sock):
    """Send MSP_EEPROM_WRITE to save configuration."""
    MSP_EEPROM_WRITE = 250
    print(f"\n=== Saving configuration to EEPROM ===")
    request = make_msp1_request(MSP_EEPROM_WRITE)
    print(f"Request: {request.hex()}")
    sock.send(request)
    time.sleep(0.5)  # EEPROM write takes time
    response = recv_with_timeout(sock)
    print(f"Response: {response.hex() if response else '(empty)'}")
    return response

def reboot_fc(sock):
    """Send MSP_REBOOT."""
    MSP_REBOOT = 68
    print(f"\n=== Rebooting FC ===")
    request = make_msp1_request(MSP_REBOOT)
    print(f"Request: {request.hex()}")
    sock.send(request)
    time.sleep(0.1)
    return True

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5761
    host = "127.0.0.1"
    mode = sys.argv[2] if len(sys.argv) > 2 else "query"

    print(f"Connecting to SITL at {host}:{port}...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print("Connected!")

    # Wait a moment for connection to stabilize
    time.sleep(0.2)

    if mode == "query":
        # Just query status
        test_msp_command(sock, "MSP_STATUS_EX", MSP_STATUS_EX, use_v2=False)
        test_msp_command(sock, "MSP_RX_CONFIG", MSP_RX_CONFIG, use_v2=False)
        test_msp_command(sock, "MSP_RC", MSP_RC, use_v2=False)
        test_msp_command(sock, "MSP2_INAV_STATUS", MSP2_INAV_STATUS, use_v2=True)

    elif mode == "set":
        # Set receiver type, save, and verify
        print("\n--- Before setting ---")
        test_msp_command(sock, "MSP_RX_CONFIG", MSP_RX_CONFIG, use_v2=False)

        set_rx_config(sock, rx_type=2)  # RX_TYPE_MSP

        print("\n--- After SET (before save) ---")
        test_msp_command(sock, "MSP_RX_CONFIG", MSP_RX_CONFIG, use_v2=False)

        save_config(sock)

        print("\n--- After save (before reboot) ---")
        test_msp_command(sock, "MSP_RX_CONFIG", MSP_RX_CONFIG, use_v2=False)

        reboot_fc(sock)
        sock.close()

        print("\nWaiting 10s for FC to reboot...")
        time.sleep(10)

        print(f"\nReconnecting to {host}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print("Reconnected!")
        time.sleep(0.2)

        print("\n--- After reboot ---")
        test_msp_command(sock, "MSP_RX_CONFIG", MSP_RX_CONFIG, use_v2=False)
        test_msp_command(sock, "MSP_RC", MSP_RC, use_v2=False)

    sock.close()
    print("\nDone!")

if __name__ == '__main__':
    main()
