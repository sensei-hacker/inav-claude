#!/usr/bin/env python3
"""
Benchmark MSP2_INAV_DEBUG Query Rate

Tests maximum reliable query rate for MSP2_INAV_DEBUG while sending:
- RC at 50 Hz
- GPS at 10 Hz

This helps determine if we can capture 198 Hz navEPH fluctuations.

Usage:
    python3 benchmark_msp2_debug_rate.py --target-rate 200
    python3 benchmark_msp2_debug_rate.py --target-rate 400 --duration 10
"""

import sys
import time
import struct
import argparse
from mspapi2 import MSPApi, InavMSP

# RC values
RC_MID = 1500
RC_LOW = 1000
RC_HIGH = 2000

# MSP commands
MSP_SET_RAW_RC = 200
MSP_SET_RAW_GPS = 201
MSP_SIMULATOR = 0x201F
MSP2_INAV_DEBUG = int(InavMSP.MSP2_INAV_DEBUG.value)
MSP2_COMMON_SET_SETTING = 0x1004

# Debug modes
DEBUG_POS_EST = 20


def send_rc(api, throttle=RC_LOW, aux1=RC_HIGH):
    """Send RC data (AETR order)."""
    channels = [RC_MID, RC_MID, throttle, RC_MID, aux1] + [RC_MID] * 11
    data = []
    for ch in channels:
        data.extend([ch & 0xFF, (ch >> 8) & 0xFF])
    api._serial.send(MSP_SET_RAW_RC, bytes(data))


def send_gps(api, altitude_cm):
    """Send GPS data."""
    altitude_m = altitude_cm // 100
    data = struct.pack('<BBiiHH', 3, 10, 0, 0, altitude_m, 0)
    api._serial.send(MSP_SET_RAW_GPS, data)


def query_debug(api):
    """Query MSP2_INAV_DEBUG and return (success, latency_ms)."""
    start = time.perf_counter()
    try:
        code, response = api._serial.request(MSP2_INAV_DEBUG)
        latency = (time.perf_counter() - start) * 1000

        if response and len(response) >= 32:
            return True, latency
        else:
            return False, latency
    except Exception:
        latency = (time.perf_counter() - start) * 1000
        return False, latency


def set_debug_mode(api, mode):
    """Set debug mode."""
    setting_name = b'debug_mode\0'
    payload = setting_name + struct.pack('<B', mode)
    api._serial.send(MSP2_COMMON_SET_SETTING, payload)
    time.sleep(0.2)


def main():
    parser = argparse.ArgumentParser(description='Benchmark MSP2_INAV_DEBUG query rate')
    parser.add_argument('--target-rate', type=int, default=200,
                        help='Target query rate in Hz (default: 200)')
    parser.add_argument('--duration', type=int, default=5,
                        help='Test duration in seconds (default: 5)')
    parser.add_argument('--port', type=int, default=5760,
                        help='MSP port (default: 5760)')

    args = parser.parse_args()

    print("=" * 70)
    print("MSP2_INAV_DEBUG Query Rate Benchmark")
    print("=" * 70)
    print(f"\nTarget Rate:  {args.target_rate} Hz")
    print(f"Duration:     {args.duration}s")
    print(f"MSP Port:     {args.port}")
    print()

    # Calculate intervals
    query_interval = 1.0 / args.target_rate
    rc_interval = 0.02  # 50 Hz
    gps_interval = 0.1  # 10 Hz

    print(f"Query interval: {query_interval*1000:.3f} ms ({args.target_rate} Hz)")
    print(f"RC interval:    {rc_interval*1000:.1f} ms (50 Hz)")
    print(f"GPS interval:   {gps_interval*1000:.1f} ms (10 Hz)")
    print()

    try:
        # Connect
        api = MSPApi(tcp_endpoint=f'localhost:{args.port}')
        api.open()
        time.sleep(0.5)
        print("✓ Connected to SITL")

        # Set debug mode
        print(f"Setting debug_mode to DEBUG_POS_EST ({DEBUG_POS_EST})...")
        set_debug_mode(api, DEBUG_POS_EST)

        # Enable HITL
        print("Enabling HITL mode...")
        api._serial.send(MSP_SIMULATOR, struct.pack('<B', 1))
        time.sleep(0.5)

        print()
        print("Starting benchmark...")
        print()

        # Statistics
        query_count = 0
        success_count = 0
        total_latency = 0.0
        min_latency = float('inf')
        max_latency = 0.0
        missed_deadlines = 0

        latencies = []

        start_time = time.perf_counter()
        last_rc = start_time
        last_gps = start_time
        last_query = start_time

        while (time.perf_counter() - start_time) < args.duration:
            current_time = time.perf_counter()
            elapsed = current_time - start_time

            # Send RC at 50 Hz
            if current_time - last_rc >= rc_interval:
                send_rc(api)
                last_rc = current_time

            # Send GPS at 10 Hz
            if current_time - last_gps >= gps_interval:
                send_gps(api, 5000)  # 50m altitude
                last_gps = current_time

            # Query MSP2_INAV_DEBUG at target rate
            if current_time - last_query >= query_interval:
                expected_time = last_query + query_interval
                actual_time = current_time
                timing_error = (actual_time - expected_time) * 1000

                if timing_error > query_interval * 1000 * 0.1:  # >10% late
                    missed_deadlines += 1

                success, latency = query_debug(api)

                query_count += 1
                if success:
                    success_count += 1
                    total_latency += latency
                    min_latency = min(min_latency, latency)
                    max_latency = max(max_latency, latency)
                    latencies.append(latency)

                last_query = current_time

                # Print progress every second
                if query_count % args.target_rate == 0:
                    success_rate = (success_count / query_count * 100)
                    avg_latency = total_latency / success_count if success_count > 0 else 0
                    print(f"[{elapsed:5.1f}s] Queries: {query_count:5d} | "
                          f"Success: {success_rate:5.1f}% | "
                          f"Latency: {avg_latency:5.2f}ms avg")

            # Small sleep to prevent busy loop
            time.sleep(0.0001)

        # Final statistics
        print()
        print("=" * 70)
        print("Results")
        print("=" * 70)
        print()
        print(f"Total Queries:      {query_count}")
        print(f"Successful:         {success_count} ({success_count/query_count*100:.1f}%)")
        print(f"Failed:             {query_count - success_count}")
        print(f"Missed Deadlines:   {missed_deadlines} ({missed_deadlines/query_count*100:.1f}%)")
        print()

        if success_count > 0:
            avg_latency = total_latency / success_count
            print(f"Latency (ms):")
            print(f"  Average:   {avg_latency:.3f}")
            print(f"  Min:       {min_latency:.3f}")
            print(f"  Max:       {max_latency:.3f}")
            print()

            # Calculate percentiles
            latencies.sort()
            p50 = latencies[len(latencies) // 2]
            p95 = latencies[int(len(latencies) * 0.95)]
            p99 = latencies[int(len(latencies) * 0.99)]

            print(f"Latency Percentiles:")
            print(f"  50th:      {p50:.3f} ms")
            print(f"  95th:      {p95:.3f} ms")
            print(f"  99th:      {p99:.3f} ms")
            print()

            # Calculate achieved rate
            actual_duration = query_count / args.target_rate
            achieved_rate = success_count / args.duration

            print(f"Achieved Rate:      {achieved_rate:.1f} Hz (target: {args.target_rate} Hz)")
            print(f"Rate Accuracy:      {achieved_rate/args.target_rate*100:.1f}%")
            print()

            # Assessment
            print("Assessment:")
            if success_count / query_count > 0.99 and missed_deadlines / query_count < 0.05:
                print(f"  ✓ {args.target_rate} Hz is RELIABLE")
            elif success_count / query_count > 0.95 and missed_deadlines / query_count < 0.10:
                print(f"  ⚠ {args.target_rate} Hz is MARGINAL (some timing jitter)")
            else:
                print(f"  ✗ {args.target_rate} Hz is UNRELIABLE")
                print(f"    Try a lower rate (e.g., {args.target_rate // 2} Hz)")

        api.close()
        return 0

    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
