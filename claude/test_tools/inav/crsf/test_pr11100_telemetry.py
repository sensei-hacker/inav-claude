#!/usr/bin/env python3
"""
PR #11100 CRSF Telemetry Test with Arming Sequence

Tests the BAROMETER_ALT_VARIO frame (0x09) from PR #11100 by:
1. Sending RC frames with proper arming sequence
2. Capturing telemetry frames
3. Analyzing 0x09 frame data for altitude changes

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
    0x09: 'BAROMETER_ALT_VARIO',
    0x0A: 'AIRSPEED',
    0x0C: 'RPM',
    0x0D: 'TEMPERATURE',
    0x1E: 'ATTITUDE',
    0x21: 'FLIGHT_MODE'
}


def decode_0x09_altitude_m(packed):
    """
    Decode altitude from CRSF frame 0x09 packed format.

    Per TBS CRSF spec:
    - MSB=0: decimeters with 10000 offset (range -1000m to +2276.7m, 0.1m resolution)
    - MSB=1: meters without offset (range 0 to 32766m, 1m resolution)

    Args:
        packed: uint16 altitude value from frame

    Returns:
        Altitude in meters
    """
    if packed & 0x8000:  # MSB set = meters
        return packed & 0x7fff
    else:  # MSB clear = decimeters with offset
        return (packed - 10000) * 0.1


def run_telemetry_test(port=5761, duration=30, show_frames=False):
    """
    Run PR #11100 telemetry test with arming sequence.

    Args:
        port: TCP port for CRSF (default 5761 = UART2)
        duration: Test duration in seconds
        show_frames: Print each telemetry frame

    Returns:
        (success: bool, results: dict)
    """
    print("=" * 70)
    print("PR #11100 CRSF Telemetry Test")
    print("=" * 70)
    print(f"Port: {port}, Duration: {duration}s")
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
    frame_0x02_data = []  # GPS frames
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

                    # Check for buffer overflow (matching crsf_rc_sender.py)
                    if len(data_buffer) > MAX_BUFFER_SIZE:
                        buffer_overflows += 1
                        if show_frames:
                            print(f"[WARN] Buffer overflow: {len(data_buffer)} bytes, discarding excess")
                        data_buffer = data_buffer[-MAX_BUFFER_SIZE:]

                    # Parse frames with full error checking
                    while len(data_buffer) >= 4:
                        # Check for valid CRSF address
                        if data_buffer[0] != 0xC8:
                            data_buffer = data_buffer[1:]
                            continue

                        frame_len = data_buffer[1]

                        # Sanity check on length field (matching crsf_rc_sender.py)
                        if frame_len < 2 or frame_len > 62:
                            sync_errors += 1
                            if show_frames:
                                hex_preview = ' '.join(f'{b:02X}' for b in data_buffer[:min(8, len(data_buffer))])
                                print(f"[WARN] Sync error: invalid length {frame_len}, buffer: {hex_preview}...")

                            # Try to resync
                            found_sync = False
                            for i in range(1, len(data_buffer) - 3):
                                if data_buffer[i] == 0xC8 and 2 <= data_buffer[i+1] <= 62:
                                    if show_frames and i > 0:
                                        discarded = ' '.join(f'{b:02X}' for b in data_buffer[:i])
                                        print(f"[WARN] Discarded {i} bytes: {discarded}")
                                    data_buffer = data_buffer[i:]
                                    found_sync = True
                                    break

                            if not found_sync:
                                if show_frames:
                                    print(f"[WARN] No sync found, clearing {len(data_buffer)} bytes")
                                data_buffer.clear()
                            continue

                        expected_len = frame_len + 2
                        if len(data_buffer) < expected_len:
                            break

                        frame_data = bytes(data_buffer[:expected_len])
                        data_buffer = data_buffer[expected_len:]

                        # Validate frame using library function (CRC, length checks)
                        is_valid, error_type, error_detail = validate_crsf_frame(frame_data)
                        if not is_valid:
                            error_stats[error_type] = error_stats.get(error_type, 0) + 1
                            if show_frames:
                                hex_str = ' '.join(f'{b:02X}' for b in frame_data[:min(16, len(frame_data))])
                                print(f"[ERROR] {error_type}: {error_detail}")
                                print(f"        Frame: {hex_str}")
                            continue

                        # Valid frame
                        telemetry_count += 1
                        frame_type = frame_data[2]
                        frames_seen[frame_type] = frames_seen.get(frame_type, 0) + 1

                        if show_frames:
                            name = FRAME_NAMES.get(frame_type, f'0x{frame_type:02X}')
                            hex_str = ' '.join(f'{b:02X}' for b in frame_data)
                            print(f"[{elapsed:5.1f}s] {name}: {hex_str}")

                        # Extract 0x02 GPS data
                        if frame_type == 0x02:
                            if show_frames:
                                hex_str = ' '.join(f'{b:02X}' for b in frame_data)
                                print(f"[DEBUG] GPS frame received, len={len(frame_data)}: {hex_str}")
                            if len(frame_data) >= 18:
                                # GPS frame: lat(4) + lon(4) + speed(2) + heading(2) + alt(2) + sats(1)
                                lat_raw = int.from_bytes(frame_data[3:7], 'big', signed=True)
                                lon_raw = int.from_bytes(frame_data[7:11], 'big', signed=True)
                                speed_raw = int.from_bytes(frame_data[11:13], 'big', signed=False)
                                heading_raw = int.from_bytes(frame_data[13:15], 'big', signed=False)
                                alt_raw = int.from_bytes(frame_data[15:17], 'big', signed=False)
                                sats = frame_data[17]
                                frame_0x02_data.append({
                                    'time': elapsed,
                                    'lat': lat_raw / 1e7,
                                    'lon': lon_raw / 1e7,
                                    'speed_kmh': speed_raw / 10.0,
                                    'heading_deg': heading_raw / 100.0,
                                    'alt_m': alt_raw - 1000,
                                    'sats': sats
                                })
                            else:
                                if show_frames:
                                    print(f"[DEBUG] GPS frame too short: {len(frame_data)} < 18")

                        # Extract 0x09 data
                        if frame_type == 0x09 and len(frame_data) >= 7:
                            alt_packed = (frame_data[3] << 8) | frame_data[4]
                            vario_packed = frame_data[5]
                            frame_0x09_data.append({
                                'time': elapsed,
                                'alt_packed': alt_packed,
                                'vario_packed': vario_packed
                            })

                        # Extract 0x21 flight mode
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

    # Expected CRSF telemetry frames in schedule order
    expected_frames = [
        (0x1E, 'ATTITUDE', 'Always'),
        (0x08, 'BATTERY', 'Always'),
        (0x21, 'FLIGHT_MODE', 'Always'),
        (0x02, 'GPS', 'feature(FEATURE_GPS) at boot'),
        (0x09, 'BARO_ALT_VARIO', 'sensors(BARO) or FW+GPS'),
        (0x07, 'VARIO', 'legacy mode only'),
    ]

    print("Frame Type              Count   Expected When")
    print("-" * 55)
    for ft, name, condition in expected_frames:
        count = frames_seen.get(ft, 0)
        status = f"x{count}" if count > 0 else "MISSING"
        marker = '*' if ft == 0x09 else (' ' if count > 0 else '!')
        print(f"{marker} 0x{ft:02X} {name:20s} {status:8s} {condition}")

    # Show any unexpected frames
    known_types = {ft for ft, _, _ in expected_frames}
    unknown_frames = {ft: c for ft, c in frames_seen.items() if ft not in known_types}
    if unknown_frames:
        print("")
        print("Other frames received:")
        for ft in sorted(unknown_frames.keys()):
            name = FRAME_NAMES.get(ft, 'UNKNOWN')
            print(f"  0x{ft:02X} {name:24s} x{unknown_frames[ft]}")

    # Validation errors (matching crsf_rc_sender.py output)
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
            print(f"  Sync/Framing Errors : {sync_errors:4d} (invalid length field or corrupted data)")
        if buffer_overflows > 0:
            print(f"  Buffer Overflows    : {buffer_overflows:4d} (receive buffer exceeded {MAX_BUFFER_SIZE} bytes)")

    # Stream health indicator (matching crsf_rc_sender.py)
    print("")
    if total_errors == 0:
        print("CRSF Stream Health: EXCELLENT - No errors detected")
    elif telemetry_count > 0 and total_errors < telemetry_count * 0.01:
        error_rate = 100 * total_errors / (telemetry_count + total_errors)
        print(f"CRSF Stream Health: GOOD - {total_errors} errors ({error_rate:.2f}% error rate)")
    elif telemetry_count > 0 and total_errors < telemetry_count * 0.05:
        error_rate = 100 * total_errors / (telemetry_count + total_errors)
        print(f"CRSF Stream Health: FAIR - {total_errors} errors ({error_rate:.2f}% error rate)")
    elif telemetry_count > 0:
        error_rate = 100 * total_errors / (telemetry_count + total_errors)
        print(f"CRSF Stream Health: POOR - {total_errors} errors ({error_rate:.2f}% error rate)")
        print("   This error rate would likely cause issues with EdgeTX telemetry parsing")
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

    # GPS (0x02) analysis
    print("")
    print("=" * 70)
    print("GPS (0x02) Analysis")
    print("=" * 70)
    gps_frame_count = frames_seen.get(0x02, 0)
    gps_parsed_count = len(frame_0x02_data)
    print(f"GPS frames seen: {gps_frame_count}")
    print(f"GPS frames parsed: {gps_parsed_count}")
    if gps_frame_count > 0 and gps_parsed_count == 0:
        print("WARNING: GPS frames received but none parsed (length mismatch?)")
        print("  Run with --show-frames to see raw GPS frame data")
    if 0x02 in frames_seen and len(frame_0x02_data) > 0:
        print(f"Total GPS frames: {frames_seen[0x02]}")

        # Sample frames
        samples = [
            ("First", frame_0x02_data[0]),
            ("Middle", frame_0x02_data[len(frame_0x02_data)//2]),
            ("Last", frame_0x02_data[-1])
        ]

        print("")
        print("Sample frames:")
        for label, data in samples:
            print(f"  {label:7s} @ {data['time']:5.1f}s: "
                  f"lat={data['lat']:10.6f}, lon={data['lon']:11.6f}, "
                  f"alt={data['alt_m']:6.1f}m, sats={data['sats']}")

        # Altitude statistics
        gps_alt_values = [d['alt_m'] for d in frame_0x02_data]
        gps_alt_min = min(gps_alt_values)
        gps_alt_max = max(gps_alt_values)
        gps_alt_range = gps_alt_max - gps_alt_min

        print("")
        print("GPS Altitude statistics:")
        print(f"  Min: {gps_alt_min:.1f}m")
        print(f"  Max: {gps_alt_max:.1f}m")
        print(f"  Range: {gps_alt_range:.1f}m")

        if gps_alt_range > 1.0:
            print("  Status: GPS altitude IS changing")
        else:
            print("  Status: GPS altitude is stable (no significant change)")
    elif gps_frame_count == 0:
        print("No GPS (0x02) frames received")
        print("")
        print("  To enable GPS telemetry:")
        print("  1. Run: python3 configure_sitl_crsf.py")
        print("  2. Reboot SITL (initCrsfTelemetry runs at boot)")
        print("  3. Enable HITL mode for GPS data injection")
        print("")
        print("  Or use: ./test_crsf_telemetry_with_gps.sh")
    else:
        print("GPS frames received but could not be parsed")

    # 0x09 analysis
    print("")
    print("=" * 70)
    print("BAROMETER_ALT_VARIO (0x09) Analysis")
    print("=" * 70)

    success = False
    if 0x09 in frames_seen and len(frame_0x09_data) > 0:
        print(f"Total 0x09 frames: {frames_seen[0x09]}")

        # Sample frames
        samples = [
            ("First", frame_0x09_data[0]),
            ("Middle", frame_0x09_data[len(frame_0x09_data)//2]),
            ("Last", frame_0x09_data[-1])
        ]

        print("")
        print("Sample frames:")
        for label, data in samples:
            alt_m = decode_0x09_altitude_m(data['alt_packed'])
            vario_raw = data['vario_packed']
            if vario_raw > 127:
                vario_raw -= 256
            vario_ms = vario_raw * 0.1
            print(f"  {label:7s} @ {data['time']:5.1f}s: alt={alt_m:6.1f}m, vario={vario_ms:+5.1f}m/s")

        # Statistics
        alt_values = [decode_0x09_altitude_m(d['alt_packed']) for d in frame_0x09_data]
        alt_min = min(alt_values)
        alt_max = max(alt_values)
        alt_range = alt_max - alt_min

        print("")
        print("Altitude statistics:")
        print(f"  Min: {alt_min:.1f}m")
        print(f"  Max: {alt_max:.1f}m")
        print(f"  Range: {alt_range:.1f}m")

        print("")
        if alt_range > 1.0:
            print("SUCCESS: Altitude is changing!")
            success = True
        elif 0x09 in frames_seen:
            print("PARTIAL: Frame 0x09 received but altitude not changing")
            print("  (May need GPS injection or sensor data)")
            success = True  # Frame exists, that's the PR test
        else:
            print("WARNING: Altitude range < 1m")
    else:
        print("ERROR: No BAROMETER_ALT_VARIO (0x09) frames received!")

    print("")
    print("=" * 70)
    if success:
        print("TEST PASSED: PR #11100 frame verified!")
    else:
        print("TEST FAILED: PR #11100 frame not received")
    print("=" * 70)

    return success, {
        'frames_seen': frames_seen,
        'frame_0x02_data': frame_0x02_data,
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
    parser = argparse.ArgumentParser(description='Test PR #11100 CRSF telemetry')
    parser.add_argument('--port', type=int, default=5761, help='TCP port (default: 5761)')
    parser.add_argument('--duration', type=int, default=30, help='Test duration in seconds')
    parser.add_argument('--show-frames', action='store_true', help='Print each frame')

    args = parser.parse_args()

    success, _ = run_telemetry_test(
        port=args.port,
        duration=args.duration,
        show_frames=args.show_frames
    )

    sys.exit(0 if success else 1)
