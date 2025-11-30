#!/usr/bin/env python3
"""
USB Throughput Test - Measure actual USB CDC transmission speed
"""

import serial
import time
import sys

def test_throughput(port_name, baudrate, data_size=10000):
    """Send data and measure throughput"""

    ser = serial.Serial(port_name, baudrate, timeout=1.0)

    try:
        print(f"Testing USB throughput on {port_name}")
        print(f"Sending {data_size} bytes...")

        # Prepare test data
        test_data = b'X' * data_size

        # Measure write time
        start_time = time.time()
        ser.write(test_data)
        ser.flush()  # Wait for all data to be sent
        end_time = time.time()

        elapsed = end_time - start_time
        throughput = data_size / elapsed

        print(f"  Time: {elapsed:.3f}s")
        print(f"  Throughput: {throughput:.0f} bytes/sec = {throughput*8/1000:.1f} Kbit/sec")
        print(f"  Per-byte time: {elapsed*1000/data_size:.3f} ms")

        # Calculate how long a 16-byte MSP response takes
        msp_response_time = (16 / throughput) * 1000
        print(f"  Estimated 16-byte MSP response time: {msp_response_time:.3f} ms")

        return throughput

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

    test_throughput(port, baudrate)


if __name__ == '__main__':
    main()
