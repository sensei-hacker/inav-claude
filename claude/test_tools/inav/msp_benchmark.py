#!/usr/bin/env python3
"""
MSP Benchmark Tool for SITL Testing

Tests MSP request throughput by sending multiple requests
and measuring response times.
"""

import socket
import struct
import time
import sys
from typing import List, Tuple

# MSP message format: $M<SIZE><CMD><CRC>
MSP_HEADER = b'$M<'

# Common MSP commands to test (read-only, safe commands)
MSP_COMMANDS = {
    'MSP_IDENT': 100,
    'MSP_STATUS': 101,
    'MSP_RAW_IMU': 102,
    'MSP_SERVO': 103,
    'MSP_MOTOR': 104,
    'MSP_RC': 105,
    'MSP_RAW_GPS': 106,
    'MSP_COMP_GPS': 107,
    'MSP_ATTITUDE': 108,
    'MSP_ALTITUDE': 109,
    'MSP_ANALOG': 110,
    'MSP_MISC': 114,
    'MSP_BOXIDS': 119,
}


def calculate_checksum(size: int, cmd: int, data: bytes = b'') -> int:
    """Calculate MSPv1 checksum (XOR)"""
    checksum = size ^ cmd
    for byte in data:
        checksum ^= byte
    return checksum


def build_msp_request(cmd: int, data: bytes = b'') -> bytes:
    """Build MSPv1 request packet"""
    size = len(data)
    checksum = calculate_checksum(size, cmd, data)
    return MSP_HEADER + struct.pack('BB', size, cmd) + data + struct.pack('B', checksum)


def send_msp_requests(host: str, port: int, commands: List[int], count: int = 10) -> Tuple[float, int, int]:
    """
    Send MSP requests as fast as possible and measure firmware processing throughput.
    Uses async sending and reply counting.

    Returns: (total_time, requests_sent, responses_received)
    """
    import threading

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.settimeout(5.0)

    try:
        sock.connect((host, port))
        print(f"Connected to {host}:{port}")

        # Allow connection to stabilize
        time.sleep(0.5)

        requests_sent = 0
        responses_received = 0
        response_data = b''
        receiving = True

        # Async receiver thread
        def receive_responses():
            nonlocal response_data, receiving
            sock.settimeout(0.1)
            while receiving:
                try:
                    chunk = sock.recv(4096)
                    if chunk:
                        response_data += chunk
                except socket.timeout:
                    continue
                except Exception:
                    break

        # Start receiver thread
        receiver = threading.Thread(target=receive_responses, daemon=True)
        receiver.start()

        start_time = time.time()

        # Send all requests as fast as possible
        for i in range(count):
            for cmd in commands:
                packet = build_msp_request(cmd)
                sock.sendall(packet)
                requests_sent += 1

        send_time = time.time()

        # Wait for firmware to process all requests
        # At ~100 Hz processing rate, 250 requests needs 2.5+ seconds
        time.sleep(3.0)
        receiving = False
        receiver.join(timeout=1.0)

        end_time = time.time()
        total_time = end_time - start_time

        # Count responses (crude - count $M> markers)
        responses_received = response_data.count(b'$M>')
        bytes_received = len(response_data)

        print(f"  Send time: {send_time - start_time:.3f}s | Wait time: {end_time - send_time:.3f}s")
        print(f"  Bytes received: {bytes_received} | Responses counted: {responses_received}")

        return total_time, requests_sent, responses_received

    finally:
        sock.close()


def run_benchmark(host: str, port: int, iterations: int = 3):
    """Run benchmark test"""

    # Select subset of commands for testing
    test_commands = [
        MSP_COMMANDS['MSP_IDENT'],
        MSP_COMMANDS['MSP_STATUS'],
        MSP_COMMANDS['MSP_ATTITUDE'],
        MSP_COMMANDS['MSP_ANALOG'],
        MSP_COMMANDS['MSP_ALTITUDE'],
    ]

    requests_per_iteration = 50

    print(f"\n{'='*60}")
    print(f"MSP Benchmark Test")
    print(f"{'='*60}")
    print(f"Target: {host}:{port}")
    print(f"Commands per iteration: {len(test_commands)}")
    print(f"Iterations: {requests_per_iteration}")
    print(f"Total requests: {len(test_commands) * requests_per_iteration}")
    print(f"Runs: {iterations}")
    print(f"{'='*60}\n")

    times = []

    for run in range(iterations):
        print(f"Run {run + 1}/{iterations}...", end=' ', flush=True)

        try:
            total_time, sent, received = send_msp_requests(
                host, port, test_commands, requests_per_iteration
            )
            times.append(total_time)

            print(f"Time: {total_time:.3f}s | Sent: {sent} | Received: {received}")

            # Small delay between runs
            time.sleep(1.0)

        except Exception as e:
            print(f"ERROR: {e}")
            return None

    if not times:
        return None

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"  Average time: {avg_time:.3f}s")
    print(f"  Min time:     {min_time:.3f}s")
    print(f"  Max time:     {max_time:.3f}s")
    print(f"  Throughput:   {len(test_commands) * requests_per_iteration / avg_time:.1f} req/sec")
    print(f"{'='*60}\n")

    return avg_time


def main():
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = 'localhost'

    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    else:
        port = 5761

    iterations = 3

    try:
        result = run_benchmark(host, port, iterations)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)


if __name__ == '__main__':
    main()
