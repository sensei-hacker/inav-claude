#!/usr/bin/env python3
"""
CRSF Telemetry Frame Test with Multiple Modes

Tests CRSF telemetry frames with different validation modes:
- baseline: Just verify telemetry is working
- pr11025: Validate AIRSPEED (0x0A), RPM (0x0C), TEMPERATURE (0x0D)
- pr11100: Validate BAROMETER_ALT_VARIO (0x09)
- merged: Validate all 4 new frame types from both PRs

Uses crsf_rc_sender.py as a library for RC frame generation and validation.
"""

import socket
import time
import select
import sys
import argparse

# Import from crsf_rc_sender.py library
from crsf_rc_sender import (
    create_rc_frame,
    parse_telemetry_frame,
    validate_crsf_frame,
    crc8_dvb_s2
)

# Frame type definitions
FRAME_NAMES = {
    0x02: 'GPS',
    0x07: 'VARIO',
    0x08: 'BATTERY',
    0x09: 'BAROMETER_ALT_VARIO',  # PR #11100
    0x0A: 'AIRSPEED',              # PR #11025
    0x0C: 'RPM',                   # PR #11025
    0x0D: 'TEMPERATURE',           # PR #11025
    0x1E: 'ATTITUDE',
    0x21: 'FLIGHT_MODE'
}


def decode_0x09_altitude_m(packed):
    """
    Decode altitude from CRSF frame 0x09 packed format.

    Per TBS CRSF spec:
    - MSB=0: decimeters with 10000 offset (range -1000m to +2276.7m, 0.1m resolution)
    - MSB=1: meters without offset (range 0 to 32766m, 1m resolution)
    """
    if packed & 0x8000:  # MSB set = meters
        return packed & 0x7fff
    else:  # MSB clear = decimeters with offset
        return (packed - 10000) * 0.1

# Test mode configurations
TEST_MODES = {
    'baseline': {
        'name': 'Baseline CRSF Telemetry',
        'expected_frames': [],
        'description': 'Verify basic telemetry is working'
    },
    'pr11025': {
        'name': 'PR #11025 (AIRSPEED, RPM, TEMPERATURE)',
        'expected_frames': [0x0A, 0x0C, 0x0D],
        'description': 'Validate new sensor frames from PR #11025'
    },
    'pr11100': {
        'name': 'PR #11100 (BAROMETER_ALT_VARIO)',
        'expected_frames': [0x09],
        'description': 'Validate baro/vario frame from PR #11100'
    },
    'merged': {
        'name': 'Merged PRs (All 4 New Frames)',
        'expected_frames': [0x09, 0x0A, 0x0C, 0x0D],
        'description': 'Validate all new frames from coordinate-crsf-telemetry-pr-merge'
    }
}


def run_frame_test(port=5761, duration=10, mode='baseline', show_frames=False):
    """
    Run CRSF telemetry frame test with arming sequence.

    Args:
        port: TCP port for CRSF (default 5761 = UART2)
        duration: Test duration in seconds
        mode: Test mode (baseline, pr11025, pr11100, merged)
        show_frames: Print each telemetry frame

    Returns:
        (success: bool, results: dict)
    """
    if mode not in TEST_MODES:
        print(f"ERROR: Unknown mode '{mode}'")
        print(f"Valid modes: {', '.join(TEST_MODES.keys())}")
        return False, {}

    test_config = TEST_MODES[mode]
    expected_frames = test_config['expected_frames']

    print("=" * 70)
    print(f"CRSF Frame Test - {test_config['name']}")
    print("=" * 70)
    print(f"Port: {port}, Duration: {duration}s")
    print(f"Mode: {mode}")
    if expected_frames:
        print(f"Expected frames: {', '.join(f'0x{f:02X}' for f in expected_frames)}")
    print("")

    # Connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)

    try:
        sock.connect(('127.0.0.1', port))
    except Exception as e:
        print(f"ERROR: Failed to connect to port {port}: {e}")
        return False, {}

    sock.setblocking(False)
    print(f"Connected to 127.0.0.1:{port}")

    # Data collection
    frames_seen = {}
    frame_bytes = {}  # First instance of each frame
    frame_0x09_data = []
    flight_modes_seen = set()
    error_stats = {}
    data_buffer = bytearray()

    # Error tracking (matching crsf_rc_sender.py)
    sync_errors = 0
    buffer_overflows = 0
    MAX_BUFFER_SIZE = 512

    # RC frame timing
    RC_RATE_HZ = 50
    frame_interval = 1.0 / RC_RATE_HZ
    channels = [1500] * 16  # All mid-stick

    start = time.time()
    next_rc_time = start
    rc_frames_sent = 0
    telemetry_count = 0

    print("")
    print("Arming sequence: throttle low (0-3s) -> ARM (3-4s) -> throttle up (4s+)")
    print("Capturing telemetry...")
    print("")

    while time.time() - start < duration:
        current_time = time.time()
        elapsed = current_time - start

        # Update channels for arming sequence
        if elapsed > 4:
            channels[2] = 1600   # Throttle up
            channels[4] = 2000   # ARM high
        elif elapsed > 3:
            channels[2] = 1000   # Throttle low
            channels[4] = 2000   # ARM high
        else:
            channels[2] = 1000   # Throttle low
            channels[4] = 1000   # ARM low

        # Send RC frame
        if current_time >= next_rc_time:
            try:
                rc_frame = create_rc_frame(channels)
                sock.sendall(rc_frame)
                rc_frames_sent += 1
                next_rc_time += frame_interval
            except:
                pass

        # Read telemetry
        try:
            readable, _, _ = select.select([sock], [], [], 0.001)
            if readable:
                chunk = sock.recv(2048)
                if chunk:
                    data_buffer.extend(chunk)

                    # Check for buffer overflow
                    if len(data_buffer) > MAX_BUFFER_SIZE:
                        buffer_overflows += 1
                        if show_frames:
                            print(f"[WARN] Buffer overflow: {len(data_buffer)} bytes")
                        data_buffer = data_buffer[-MAX_BUFFER_SIZE:]

                    # Parse frames with full error checking
                    while len(data_buffer) >= 4:
                        if data_buffer[0] != 0xC8:
                            data_buffer = data_buffer[1:]
                            continue

                        frame_len = data_buffer[1]

                        # Sanity check on length
                        if frame_len < 2 or frame_len > 62:
                            sync_errors += 1
                            # Try to resync
                            found_sync = False
                            for i in range(1, len(data_buffer) - 3):
                                if data_buffer[i] == 0xC8 and 2 <= data_buffer[i+1] <= 62:
                                    data_buffer = data_buffer[i:]
                                    found_sync = True
                                    break
                            if not found_sync:
                                data_buffer.clear()
                            continue

                        expected_len = frame_len + 2
                        if len(data_buffer) < expected_len:
                            break

                        frame_data = bytes(data_buffer[:expected_len])
                        data_buffer = data_buffer[expected_len:]

                        # Validate frame using library function
                        is_valid, error_type, error_detail = validate_crsf_frame(frame_data)
                        if not is_valid:
                            error_stats[error_type] = error_stats.get(error_type, 0) + 1
                            if show_frames:
                                print(f"[ERROR] {error_type}: {error_detail}")
                            continue

                        # Valid frame
                        telemetry_count += 1
                        frame_type = frame_data[2]
                        frames_seen[frame_type] = frames_seen.get(frame_type, 0) + 1

                        # Store first instance
                        if frame_type not in frame_bytes:
                            frame_bytes[frame_type] = frame_data

                        if show_frames:
                            name = FRAME_NAMES.get(frame_type, f'0x{frame_type:02X}')
                            hex_str = ' '.join(f'{b:02X}' for b in frame_data)
                            print(f"[{elapsed:5.1f}s] {name}: {hex_str}")

                        # Extract 0x09 data for altitude analysis
                        if frame_type == 0x09 and len(frame_data) >= 7:
                            alt_packed = (frame_data[3] << 8) | frame_data[4]
                            vario_packed = frame_data[5]
                            frame_0x09_data.append({
                                'time': elapsed,
                                'alt_packed': alt_packed,
                                'vario_packed': vario_packed
                            })

                        # Extract flight mode
                        if frame_type == 0x21 and frame_len > 2:
                            payload_len = frame_len - 2
                            if len(frame_data) >= 3 + payload_len:
                                payload = frame_data[3:3 + payload_len]
                                null_pos = payload.find(b'\x00')
                                if null_pos > 0:
                                    mode_str = payload[:null_pos].decode('ascii', errors='replace')
                                elif payload:
                                    mode_str = payload.rstrip(b'\x00').decode('ascii', errors='replace')
                                else:
                                    mode_str = ''
                                if mode_str:
                                    flight_modes_seen.add(mode_str)
        except Exception as e:
            if show_frames:
                print(f"[ERROR] Socket error: {e}")

    sock.close()

    # Print results
    total_errors = sum(error_stats.values()) + sync_errors + buffer_overflows

    print("")
    print("=" * 70)
    print("Results")
    print("=" * 70)
    print(f"RC frames sent: {rc_frames_sent}")
    print(f"Telemetry frames received: {telemetry_count}")
    print(f"Unique frame types: {len(frames_seen)}")
    print("")

    for ft in sorted(frames_seen.keys()):
        name = FRAME_NAMES.get(ft, 'UNKNOWN')
        marker = '*' if ft in expected_frames else ' '
        print(f"{marker} 0x{ft:02X} {name:24s} x{frames_seen[ft]}")

    # Validation errors
    if error_stats:
        print("")
        print("Validation Errors:")
        for err, count in sorted(error_stats.items()):
            print(f"  {err:20s}: {count:4d} frames")

    # Stream errors
    if sync_errors > 0 or buffer_overflows > 0:
        print("")
        print("Stream Errors:")
        if sync_errors > 0:
            print(f"  Sync/Framing Errors : {sync_errors:4d}")
        if buffer_overflows > 0:
            print(f"  Buffer Overflows    : {buffer_overflows:4d}")

    # Stream health
    print("")
    if total_errors == 0:
        print("CRSF Stream Health: EXCELLENT - No errors detected")
    elif telemetry_count > 0 and total_errors < telemetry_count * 0.01:
        error_rate = 100 * total_errors / (telemetry_count + total_errors)
        print(f"CRSF Stream Health: GOOD - {total_errors} errors ({error_rate:.2f}%)")
    elif telemetry_count > 0 and total_errors < telemetry_count * 0.05:
        error_rate = 100 * total_errors / (telemetry_count + total_errors)
        print(f"CRSF Stream Health: FAIR - {total_errors} errors ({error_rate:.2f}%)")
    elif telemetry_count > 0:
        error_rate = 100 * total_errors / (telemetry_count + total_errors)
        print(f"CRSF Stream Health: POOR - {total_errors} errors ({error_rate:.2f}%)")
    else:
        print("CRSF Stream Health: UNKNOWN - No telemetry received")

    # Flight mode analysis
    print("")
    print("=" * 70)
    print("FLIGHT_MODE Analysis")
    print("=" * 70)
    if flight_modes_seen:
        print(f"Modes seen: {', '.join(sorted(flight_modes_seen))}")
        is_armed = any('ARM' in m.upper() for m in flight_modes_seen)
        print(f"Armed: {'YES' if is_armed else 'NO'}")
    else:
        print("No flight mode data captured")
        is_armed = False

    # Mode-specific validation
    print("")
    print("=" * 70)
    print(f"Mode Validation: {test_config['name']}")
    print("=" * 70)

    success = False

    if mode == 'baseline':
        total_frames = sum(frames_seen.values())
        print(f"Total frames received: {total_frames}")
        print(f"Unique frame types: {len(frames_seen)}")
        if total_frames > 0:
            print("")
            print("SUCCESS: CRSF telemetry is working")
            success = True
        else:
            print("")
            print("FAILURE: No telemetry frames received")

    elif mode == 'pr11025':
        print("PR #11025 Frame Validation:")
        success_count = 0
        for ft, name in [(0x0A, 'AIRSPEED'), (0x0C, 'RPM'), (0x0D, 'TEMPERATURE')]:
            if ft in frames_seen:
                print(f"  * {name} (0x{ft:02X}): {frames_seen[ft]} frames")
                success_count += 1
            else:
                print(f"  X {name} (0x{ft:02X}): NOT RECEIVED")

        print("")
        if success_count == 3:
            print("SUCCESS: All PR #11025 frames verified!")
            success = True
        elif success_count > 0:
            print(f"PARTIAL: {success_count}/3 frames received")
        else:
            print("FAILURE: No PR #11025 frames received")

    elif mode == 'pr11100':
        print("PR #11100 Frame Validation:")
        if 0x09 in frames_seen:
            print(f"  * BAROMETER_ALT_VARIO (0x09): {frames_seen[0x09]} frames")

            if 0x09 in frame_bytes:
                frame = frame_bytes[0x09]
                if len(frame) >= 7:
                    alt_packed = (frame[3] << 8) | frame[4]
                    vario_packed = frame[5]
                    print(f"    First frame: alt=0x{alt_packed:04X}, vario=0x{vario_packed:02X}")

            # Altitude analysis
            if len(frame_0x09_data) > 0:
                alt_values = [decode_0x09_altitude_m(d['alt_packed']) for d in frame_0x09_data]
                alt_range = max(alt_values) - min(alt_values)
                print(f"    Altitude range: {alt_range:.1f}m")

            print("")
            print("SUCCESS: PR #11100 frame verified!")
            success = True
        else:
            print("  X BAROMETER_ALT_VARIO (0x09): NOT RECEIVED")
            print("")
            print("FAILURE: PR #11100 frame not received")

    elif mode == 'merged':
        print("Merged PRs Frame Validation (All 4 New Frames):")
        success_count = 0
        frame_details = [
            (0x09, 'BAROMETER_ALT_VARIO', 'PR #11100'),
            (0x0A, 'AIRSPEED', 'PR #11025'),
            (0x0C, 'RPM', 'PR #11025'),
            (0x0D, 'TEMPERATURE', 'PR #11025')
        ]
        for ft, name, pr in frame_details:
            if ft in frames_seen:
                print(f"  * {name} (0x{ft:02X}): {frames_seen[ft]} frames [{pr}]")
                success_count += 1
            else:
                print(f"  X {name} (0x{ft:02X}): NOT RECEIVED [{pr}]")

        print("")
        if success_count == 4:
            print("SUCCESS: All 4 new frames from merged PRs verified!")
            success = True
        elif success_count > 0:
            print(f"PARTIAL: {success_count}/4 frames received")
        else:
            print("FAILURE: No new frames received")

    print("")
    print("=" * 70)
    if success:
        print(f"TEST PASSED: {test_config['name']}")
    else:
        print(f"TEST FAILED: {test_config['name']}")
    print("=" * 70)

    return success, {
        'frames_seen': frames_seen,
        'frame_bytes': frame_bytes,
        'frame_0x09_data': frame_0x09_data,
        'flight_modes': flight_modes_seen,
        'validation_errors': error_stats,
        'sync_errors': sync_errors,
        'buffer_overflows': buffer_overflows,
        'total_errors': total_errors,
        'rc_frames_sent': rc_frames_sent,
        'telemetry_count': telemetry_count
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test CRSF telemetry frames')
    parser.add_argument('--port', type=int, default=5761, help='TCP port (default: 5761)')
    parser.add_argument('--duration', type=int, default=10, help='Test duration in seconds')
    parser.add_argument('--mode', choices=['baseline', 'pr11025', 'pr11100', 'merged'],
                        default='baseline', help='Test mode')
    parser.add_argument('--show-frames', action='store_true', help='Print each frame')

    args = parser.parse_args()

    success, _ = run_frame_test(
        port=args.port,
        duration=args.duration,
        mode=args.mode,
        show_frames=args.show_frames
    )

    sys.exit(0 if success else 1)
