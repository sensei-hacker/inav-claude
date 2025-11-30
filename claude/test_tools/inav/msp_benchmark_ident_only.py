#!/usr/bin/env python3
"""
MSP Benchmark Tool - MSP_IDENT Only

Test with only MSP_IDENT (7-byte response) to determine if limit is:
- Byte-count based (should get ~457 responses if 3200-byte limit)
- Response-count based (should get 200 responses)
"""

import socket
import struct
import time
import sys
from typing import List, Tuple

# MSP message format: $M<SIZE><CMD><CRC>
MSP_HEADER = b'$M<'

# Only MSP_IDENT for this test
MSP_IDENT = 100


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


def send_msp_requests(host: str, port: int, count: int = 250) -> Tuple[float, int, int]:
    """
    Send MSP requests as fast as possible and measure firmware processing throughput.
    Uses async sending and reply counting.

    Returns: (total_time, requests_sent, responses_received)
    """
    import threading

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)

    rcvbuf = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    sndbuf = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    print(f"[CLIENT] Socket buffers: RX={rcvbuf} TX={sndbuf}")

    sock.settimeout(10.0)

    try:
        sock.connect((host, port))
        print(f"[CLIENT] Connected to {host}:{port}")

        time.sleep(0.5)

        requests_sent = 0
        responses_received = 0
        response_data = b''
        receiving = True
        read_count = [0]

        # Async receiver thread
        def receive_responses():
            nonlocal response_data, receiving
            sock.settimeout(0.1)
            print("[RX] Receiver thread started")

            while receiving:
                try:
                    chunk = sock.recv(8192)
                    if chunk:
                        response_data += chunk
                        read_count[0] += 1
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[RX] Error: {e}")
                    break

            # Final drain
            print(f"[RX] Main loop exited, draining socket...")
            sock.settimeout(0.01)
            drain_count = 0
            try:
                while True:
                    chunk = sock.recv(8192)
                    if not chunk:
                        break
                    response_data += chunk
                    drain_count += 1
            except socket.timeout:
                pass

            print(f"[RX] Receiver thread exiting. Reads: {read_count[0]}, Drain: {drain_count}, Bytes: {len(response_data)}")

        receiver = threading.Thread(target=receive_responses, daemon=True)
        receiver.start()

        start_time = time.time()

        # Send all requests (only MSP_IDENT)
        for i in range(count):
            packet = build_msp_request(MSP_IDENT)
            sock.sendall(packet)
            requests_sent += 1

        send_time = time.time()

        print(f"[CLIENT] Sent {requests_sent} MSP_IDENT requests in {send_time - start_time:.3f}s, waiting 10s...")
        time.sleep(10.0)
        receiving = False
        receiver.join(timeout=2.0)

        end_time = time.time()
        total_time = end_time - start_time

        # Count responses
        responses_received = response_data.count(b'$M>')
        bytes_received = len(response_data)

        print(f"[CLIENT] Bytes received: {bytes_received} | Responses counted: {responses_received}")
        print(f"[CLIENT] Expected bytes for {responses_received} responses: {responses_received * 13}")  # 7 data + 6 overhead

        return total_time, requests_sent, responses_received

    finally:
        sock.close()


def run_benchmark(host: str, port: int):
    """Run benchmark test"""

    print(f"\n{'='*60}")
    print(f"MSP Benchmark Test - MSP_IDENT Only")
    print(f"{'='*60}")
    print(f"Target: {host}:{port}")
    print(f"Command: MSP_IDENT (7-byte response)")
    print(f"Total requests: 250")
    print(f"Expected if byte-limit (3200): ~246 responses")
    print(f"Expected if count-limit (200): 200 responses")
    print(f"{'='*60}\n")

    try:
        total_time, sent, received = send_msp_requests(host, port, 250)

        print(f"\n[RESULT] Time: {total_time:.3f}s | Sent: {sent} | Received: {received}")

        if received == 200:
            print(f"\n*** RESULT: Response-COUNT limit (exactly 200 responses) ***")
        elif 240 <= received <= 250:
            print(f"\n*** RESULT: Byte-COUNT limit (~3200 bytes) ***")
        else:
            print(f"\n*** RESULT: Unknown pattern ({received} responses) ***")

        return total_time

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = 'localhost'

    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    else:
        port = 5761

    try:
        result = run_benchmark(host, port)
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)


if __name__ == '__main__':
    main()
