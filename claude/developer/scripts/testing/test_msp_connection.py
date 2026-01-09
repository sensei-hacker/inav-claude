#!/usr/bin/env python3
"""Test MSP connection to SITL and check sensor status."""

import socket
import struct

def send_msp(sock, cmd, data=b''):
    """Send MSP v1 command"""
    size = len(data)
    checksum = size ^ cmd
    for b in data:
        checksum ^= b
    msg = b'$M<' + bytes([size, cmd]) + data + bytes([checksum])
    sock.send(msg)
    return receive_msp(sock)

def receive_msp(sock):
    """Receive MSP response"""
    try:
        header = sock.recv(3)
        if not header or header != b'$M>':
            if header == b'$M!':
                size = sock.recv(1)[0]
                sock.recv(size + 2)  # data + checksum
                return None, "Error response"
            return None, f"Bad header: {header}"
        size = sock.recv(1)[0]
        cmd = sock.recv(1)[0]
        data = sock.recv(size) if size > 0 else b''
        checksum = sock.recv(1)[0]
        return data, cmd
    except socket.timeout:
        return None, "Timeout"

def main():
    # Connect to SITL (try IPv6 first since SITL binds to [::])
    sock = None
    for family, addr in [(socket.AF_INET6, '::1'), (socket.AF_INET, '127.0.0.1')]:
        try:
            sock = socket.socket(family, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect((addr, 5760))
            print(f"Connected via {addr}")
            break
        except (ConnectionRefusedError, OSError):
            sock.close()
            sock = None
            continue

    if sock is None:
        print("ERROR: Could not connect to SITL on port 5760")
        return

    # MSP_STATUS_EX = 150
    data, cmd = send_msp(sock, 150)
    if data:
        print(f"MSP_STATUS_EX: {len(data)} bytes received")
        if len(data) >= 2:
            cycle_time = struct.unpack('<H', data[0:2])[0]
            print(f"  Cycle time: {cycle_time} us")
        if len(data) >= 8:
            sensors = struct.unpack('<I', data[4:8])[0]
            print(f"  Sensors: 0x{sensors:08x}")
            pitot_enabled = (sensors >> 7) & 1  # Bit 7 is usually PITOT
            print(f"  Pitot sensor bit: {pitot_enabled}")

    # MSP_SENSOR_STATUS = 151
    data, cmd = send_msp(sock, 151)
    if data:
        print(f"MSP_SENSOR_STATUS: {len(data)} bytes")

    sock.close()
    print("Done")

if __name__ == '__main__':
    main()
