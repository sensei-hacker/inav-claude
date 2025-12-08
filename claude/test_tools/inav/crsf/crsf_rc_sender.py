#!/usr/bin/env python3
"""
CRSF RC Frame Sender with Telemetry Reader

Simulates a CRSF transmitter sending RC channel data to the flight controller
and receiving telemetry responses on the same connection.

IMPORTANT: TCP Connection Limitation
=====================================
TCP ports accept only ONE client connection at a time. This script handles both
sending RC frames and receiving telemetry frames on the SAME bidirectional socket.
You CANNOT run a separate telemetry reader script while this is connected.

This matches real-world CRSF behavior where the transmitter and flight controller
communicate bidirectionally over a single serial link.

USAGE:
    python3 crsf_rc_sender.py <uart_num> [--rate HZ] [--duration SEC] [--show-telemetry]

ARGUMENTS:
    uart_num           UART number (1 or 2, default: 2)
    --rate HZ          Frame rate in Hz (default: 50)
    --duration SEC     Duration in seconds (default: infinite, use Ctrl+C to stop)
    --show-telemetry   Display received telemetry frames (default: off for cleaner output)

EXAMPLES:
    # Send RC frames and display telemetry on STDOUT
    python3 crsf_rc_sender.py 2 --rate 50 --show-telemetry

    # Send RC frames without telemetry output (cleaner)
    python3 crsf_rc_sender.py 2 --rate 50

    # Send to UART1 at 100Hz for 30 seconds with telemetry
    python3 crsf_rc_sender.py 1 --rate 100 --duration 30 --show-telemetry

PREREQUISITES:
    - SITL must be running with CRSF configured
    - Target UART must be set to SERIAL_RX function
    - Script will wait up to 30s for port to become available

BEHAVIOR:
    - Automatically retries connection if port not ready (useful when starting
      RC sender before/during SITL boot)
    - Sends all 16 channels at midpoint (1500us) at specified rate
    - Continuously reads telemetry frames from FC on same socket
    - Updates every 50 frames with actual send rate and telemetry stats
    - Optionally displays telemetry frames to STDOUT (use --show-telemetry)

ERROR DETECTION (EdgeTX-Compatible):
    The script validates all CRSF frames using the same checks as EdgeTX radios:
    - CRC8 DVB-S2 validation (detects corrupted frames)
    - Frame length consistency (detects truncated/malformed frames)
    - Payload length validation (detects invalid frame structures)
    - Sync/framing error detection (attempts resynchronization on corruption)
    - Buffer overflow protection (prevents unbounded memory growth)

    Error types detected and reported:
    - CRC_MISMATCH: Frame failed CRC check
    - LENGTH_TOO_SHORT: Frame shorter than minimum (4 bytes)
    - LENGTH_MISMATCH: Frame size doesn't match length field
    - LENGTH_EXCESS: Frame longer than length field indicates
    - FRAME_TOO_LARGE: Frame exceeds maximum CRSF size (64 bytes)
    - PAYLOAD_TOO_SHORT: Length field < 2 (Type + CRC minimum)
    - Sync/Framing Errors: Invalid length field, stream corruption
    - Buffer Overflows: Receive buffer exceeded 512 bytes

    Summary includes stream health indicator:
    - EXCELLENT: 0% error rate
    - GOOD: < 1% error rate
    - FAIR: < 5% error rate
    - POOR: ≥ 5% error rate (would affect EdgeTX parsing)

PORTS:
    UART1 = TCP port 5760
    UART2 = TCP port 5761

OUTPUT:
    The script displays telemetry data on STDOUT when --show-telemetry is enabled.
    Without this flag, only RC frame statistics are shown for cleaner output.

    With --show-telemetry:
    - Valid frames: [TELEM] FRAME_NAME (bytes, CRC:✓): hex dump
    - Error frames: [ERROR] ERROR_TYPE: detailed error message
    - Warning messages: [WARN] sync errors, buffer overflows

    Summary always shows:
    - Telemetry frame breakdown by type
    - Validation error counts by type
    - Stream error counts (sync/framing, buffer overflow)
    - Overall stream health indicator
"""

import socket
import struct
import time
import sys
import select

# CRSF Constants
CRSF_ADDRESS_FLIGHT_CONTROLLER = 0xC8
CRSF_ADDRESS_BROADCAST = 0x00
CRSF_FRAMETYPE_RC_CHANNELS_PACKED = 0x16
CRSF_FRAME_RC_CHANNELS_PAYLOAD_SIZE = 22  # 11 bits per channel * 16 channels = 22 bytes

# CRSF Telemetry Frame Types
CRSF_FRAMETYPE_GPS = 0x02
CRSF_FRAMETYPE_BATTERY_SENSOR = 0x08
CRSF_FRAMETYPE_LINK_STATISTICS = 0x14
CRSF_FRAMETYPE_FLIGHT_MODE = 0x21
CRSF_FRAMETYPE_ATTITUDE = 0x1E
CRSF_FRAMETYPE_VARIO = 0x07
CRSF_FRAMETYPE_HEARTBEAT = 0x0B

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

def pack_rc_channels(channels):
    """
    Pack 16 RC channels (11 bits each) into 22 bytes.

    Channel values: 172-1811 (988-2012us), center at 992 (1500us)
    """
    # Clamp and convert to 11-bit range
    packed = []
    for ch in channels:
        # Convert 1000-2000us to 172-1811 (11-bit range)
        # Formula: (value - 1000) * 1.639 + 172
        value = int((ch - 1000) * 1.639 + 172)
        value = max(172, min(1811, value))  # Clamp to valid range
        packed.append(value)

    # Pack 16 channels (11 bits each) into bytes
    bits = 0
    bit_count = 0
    result = bytearray()

    for ch_val in packed:
        bits |= (ch_val << bit_count)
        bit_count += 11

        while bit_count >= 8:
            result.append(bits & 0xFF)
            bits >>= 8
            bit_count -= 8

    # Add any remaining bits
    if bit_count > 0:
        result.append(bits & 0xFF)

    return bytes(result[:22])  # Should be exactly 22 bytes

def create_rc_frame(channels):
    """
    Create a CRSF RC channels frame.

    Frame structure:
    [Address][Length][Type][Payload (22 bytes)][CRC8]
    """
    # Pack channel data
    payload = pack_rc_channels(channels)

    # Build frame
    frame = bytearray()
    frame.append(CRSF_ADDRESS_FLIGHT_CONTROLLER)
    frame.append(CRSF_FRAME_RC_CHANNELS_PAYLOAD_SIZE + 2)  # Type + Payload + CRC
    frame.append(CRSF_FRAMETYPE_RC_CHANNELS_PACKED)
    frame.extend(payload)

    # Calculate CRC over Type + Payload
    crc = crc8_dvb_s2(0, bytes(frame[2:]))
    frame.append(crc)

    return bytes(frame)

def validate_crsf_frame(data):
    """
    Validate CRSF frame structure matching EdgeTX requirements.

    Returns:
        (is_valid: bool, error_type: str, error_detail: str)

    EdgeTX validation checks:
    - Minimum frame length (4 bytes: Address + Length + Type + CRC)
    - Valid address (0x00-0xFF, typically 0xC8 for FC, 0xEA for radio, 0xEC for receiver)
    - Length field consistency (matches actual frame size)
    - Valid payload length (Type + Payload + CRC = Length field)
    - CRC8 DVB-S2 validation
    - Frame size limits (max ~64 bytes for CRSF)
    """
    # Check minimum length
    if len(data) < 4:
        return (False, "LENGTH_TOO_SHORT", f"Frame too short: {len(data)} bytes (minimum 4)")

    address = data[0]
    length_field = data[1]  # This is Type(1) + Payload(N) + CRC(1)
    frame_type = data[2]

    # Calculate expected total frame size
    expected_total_len = length_field + 2  # +2 for Address and Length bytes

    # Check if we have complete frame
    if len(data) < expected_total_len:
        return (False, "LENGTH_MISMATCH",
                f"Incomplete frame: got {len(data)} bytes, expected {expected_total_len}")

    if len(data) > expected_total_len:
        return (False, "LENGTH_EXCESS",
                f"Frame too long: got {len(data)} bytes, expected {expected_total_len}")

    # Check maximum frame size (CRSF max payload is typically 60 bytes)
    if expected_total_len > 64:
        return (False, "FRAME_TOO_LARGE",
                f"Frame exceeds maximum size: {expected_total_len} bytes (max 64)")

    # Check minimum payload (at least Type + CRC = 2 bytes)
    if length_field < 2:
        return (False, "PAYLOAD_TOO_SHORT",
                f"Length field too small: {length_field} (minimum 2 for Type+CRC)")

    # Validate CRC
    # CRC is calculated over Type + Payload (exclude Address, Length, and CRC itself)
    crc_data = data[2:-1]  # Type + Payload
    expected_crc = data[-1]
    calculated_crc = crc8_dvb_s2(0, crc_data)

    if calculated_crc != expected_crc:
        return (False, "CRC_MISMATCH",
                f"CRC failed: expected 0x{expected_crc:02X}, calculated 0x{calculated_crc:02X}")

    # Check for valid address range (permissive - allow any address for now)
    # EdgeTX expects: FC=0xC8, Radio=0xEA, Receiver=0xEC, Broadcast=0x00
    # But we'll accept any address to be compatible

    # All checks passed
    return (True, None, None)


def parse_telemetry_frame(data, show_telemetry, error_stats):
    """
    Parse and validate a CRSF telemetry frame with EdgeTX-compatible error detection.

    Args:
        data: Raw frame bytes
        show_telemetry: Whether to display frame contents
        error_stats: Dictionary to track error counts

    Returns:
        Frame type string for statistics (or error type if validation fails)
    """
    # Validate frame structure
    is_valid, error_type, error_detail = validate_crsf_frame(data)

    if not is_valid:
        error_stats[error_type] = error_stats.get(error_type, 0) + 1
        if show_telemetry:
            hex_str = ' '.join(f'{b:02X}' for b in data[:min(len(data), 16)])
            if len(data) > 16:
                hex_str += "..."
            print(f"[ERROR] {error_type:20s}: {error_detail}")
            print(f"        Frame data: {hex_str}")
        return f"ERROR_{error_type}"

    # Frame is valid, extract fields
    address = data[0]
    length = data[1]
    frame_type = data[2]

    # Map frame types to names
    frame_types = {
        0x02: "GPS",
        0x08: "BATTERY",
        0x14: "LINK_STATS",
        0x21: "FLIGHT_MODE",
        0x1E: "ATTITUDE",
        0x07: "VARIO",
        0x0B: "HEARTBEAT",
        0x09: "BARO_ALT",
        0x0A: "BARO_VARIO"
    }

    frame_name = frame_types.get(frame_type, f"UNKNOWN_0x{frame_type:02X}")

    if show_telemetry:
        hex_str = ' '.join(f'{b:02X}' for b in data)
        crc_status = "✓"
        print(f"[TELEM] {frame_name:12s} ({len(data):2d} bytes, CRC:{crc_status}): {hex_str}")

    return frame_name

def send_rc_frames(uart_num=2, rate_hz=50, duration_sec=None, connect_timeout=30, show_telemetry=False):
    """
    Send CRSF RC frames to SITL and receive telemetry on same connection.

    Args:
        uart_num: UART number (default 2)
        rate_hz: Frame rate in Hz (default 50 - standard CRSF rate)
        duration_sec: Duration to send (None = infinite)
        connect_timeout: Max seconds to wait for port availability (default 30)
        show_telemetry: Display received telemetry frames (default False)
    """
    port = 5760 + (uart_num - 1)
    print(f"=== CRSF RC Frame Sender ===")
    print(f"Connecting to SITL UART{uart_num} on port {port}...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)

    # Retry connection with timeout
    connect_start = time.time()
    retry_count = 0
    connected = False

    while (time.time() - connect_start) < connect_timeout:
        try:
            sock.connect(('127.0.0.1', port))
            connected = True
            break
        except (ConnectionRefusedError, OSError) as e:
            retry_count += 1
            if retry_count == 1:
                print(f"Port not ready, polling...")
            elif retry_count % 5 == 0:
                elapsed = time.time() - connect_start
                print(f"  Still waiting... ({elapsed:.0f}s / {connect_timeout}s)")
            time.sleep(0.5)
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return 1

    if not connected:
        print(f"✗ Connection timeout after {connect_timeout}s - is SITL running?")
        return 1

    print(f"✓ Connected to 127.0.0.1:{port} (after {retry_count} retries)")

    # Set socket to non-blocking for select()
    sock.setblocking(False)

    print(f"\nSending RC frames at {rate_hz}Hz...")
    print("Channels: All at 1500us (midpoint)")
    print(f"Telemetry display: {'ENABLED' if show_telemetry else 'DISABLED (use --show-telemetry to enable)'}")
    if duration_sec:
        print(f"Duration: {duration_sec} seconds")
    else:
        print("Duration: Infinite (press Ctrl+C to stop)")
    print()

    # Default channels - all at midpoint (1500us)
    channels = [1500] * 16

    frame_interval = 1.0 / rate_hz
    frame_count = 0
    telemetry_count = 0
    telemetry_frames = {}  # Count by frame type
    error_stats = {}       # Count by error type
    rx_buffer = bytearray()
    sync_errors = 0        # Count framing/sync losses
    buffer_overflows = 0   # Count buffer overflow events
    start_time = time.time()
    next_send_time = start_time

    # Buffer management
    MAX_BUFFER_SIZE = 512  # Prevent buffer from growing unbounded

    try:
        while True:
            current_time = time.time()

            # Calculate time until next RC frame
            time_until_send = next_send_time - current_time

            # Check for incoming telemetry (non-blocking with timeout)
            if time_until_send > 0:
                # Wait for readable data with timeout
                readable, _, _ = select.select([sock], [], [], min(time_until_send, 0.01))
            else:
                # Time to send, check for data without blocking
                readable, _, _ = select.select([sock], [], [], 0)

            # Read telemetry if available
            if readable:
                try:
                    chunk = sock.recv(256)
                    if chunk:
                        rx_buffer.extend(chunk)

                        # Check for buffer overflow
                        if len(rx_buffer) > MAX_BUFFER_SIZE:
                            buffer_overflows += 1
                            if show_telemetry:
                                print(f"[WARN] Buffer overflow: {len(rx_buffer)} bytes, discarding excess")
                            # Keep only the most recent data
                            rx_buffer = rx_buffer[-MAX_BUFFER_SIZE:]

                        # Parse complete frames from buffer
                        while len(rx_buffer) >= 4:
                            # CRSF frame: [Address][Length][Type][Payload...][CRC]
                            # Length field is: Type + Payload + CRC
                            length_field = rx_buffer[1]
                            expected_len = length_field + 2  # +2 for Address and Length bytes

                            # Sanity check on length field
                            if length_field < 2 or expected_len > 64:
                                # Invalid length field - possible framing error
                                # Try to resync by looking for next valid frame start
                                sync_errors += 1
                                if show_telemetry:
                                    hex_preview = ' '.join(f'{b:02X}' for b in rx_buffer[:min(8, len(rx_buffer))])
                                    print(f"[WARN] Sync error: invalid length field {length_field}, buffer: {hex_preview}...")

                                # Try to find next potential frame (search for common addresses)
                                found_sync = False
                                for i in range(1, len(rx_buffer)-3):
                                    if rx_buffer[i+1] >= 2 and rx_buffer[i+1] <= 63:  # Valid length range
                                        # Discard garbage bytes
                                        if show_telemetry and i > 0:
                                            discarded = ' '.join(f'{b:02X}' for b in rx_buffer[:i])
                                            print(f"[WARN] Discarded {i} bytes: {discarded}")
                                        rx_buffer = rx_buffer[i:]
                                        found_sync = True
                                        break

                                if not found_sync:
                                    # No valid frame found, clear buffer
                                    if show_telemetry:
                                        print(f"[WARN] No sync found, clearing {len(rx_buffer)} bytes")
                                    rx_buffer.clear()
                                break

                            if len(rx_buffer) >= expected_len:
                                # Extract frame
                                frame_data = bytes(rx_buffer[:expected_len])
                                rx_buffer = rx_buffer[expected_len:]

                                # Parse and validate
                                frame_type = parse_telemetry_frame(frame_data, show_telemetry, error_stats)
                                telemetry_count += 1
                                telemetry_frames[frame_type] = telemetry_frames.get(frame_type, 0) + 1
                            else:
                                # Incomplete frame, wait for more data
                                break
                except BlockingIOError:
                    pass  # No data available

            # Send RC frame if it's time
            if current_time >= next_send_time:
                frame = create_rc_frame(channels)
                sock.sendall(frame)
                frame_count += 1
                next_send_time += frame_interval

                # Status update every 50 frames
                if frame_count % 50 == 0:
                    elapsed = time.time() - start_time
                    # Set throttle low, then arm, then raise throttle
                    if (elapsed > 4):
                      channels[2] = 1600
                      channels[4] = 2000
                    elif (elapsed > 3):
                      channels[2] = 1000
                      channels[4] = 2000
                    else:
                      channels[2] = 1000
                      channels[4] = 1000

                    actual_rate = frame_count / elapsed if elapsed > 0 else 0
                    telem_summary = ', '.join(f"{k}:{v}" for k, v in sorted(telemetry_frames.items()))
                    print(f"Sent {frame_count} frames ({actual_rate:.1f} Hz) | Received {telemetry_count} telemetry frames [{telem_summary}]")

                # Check duration
                if duration_sec and (time.time() - start_time) >= duration_sec:
                    break

    except KeyboardInterrupt:
        print("\n\n✓ Stopped by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1
    finally:
        sock.close()

    elapsed = time.time() - start_time
    total_errors = sum(error_stats.values()) + sync_errors + buffer_overflows

    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"RC Frames Sent: {frame_count} in {elapsed:.1f} seconds ({frame_count/elapsed:.1f} Hz avg)")
    print(f"Telemetry Received: {telemetry_count} frames")

    if telemetry_frames:
        print(f"\nTelemetry Frame Breakdown:")
        valid_frames = sum(count for name, count in telemetry_frames.items() if not name.startswith("ERROR_"))
        error_frames = sum(count for name, count in telemetry_frames.items() if name.startswith("ERROR_"))

        for frame_type, count in sorted(telemetry_frames.items()):
            if not frame_type.startswith("ERROR_"):
                print(f"  {frame_type:15s}: {count:4d} frames")

        if error_frames > 0:
            print(f"\n⚠ Validation Errors:")
            for frame_type, count in sorted(telemetry_frames.items()):
                if frame_type.startswith("ERROR_"):
                    error_name = frame_type.replace("ERROR_", "")
                    print(f"  {error_name:20s}: {count:4d} frames")
    else:
        print(f"\n⚠ WARNING: No telemetry frames received!")
        print(f"   Check CRSF configuration and TELEMETRY feature flag")

    # Display framing/stream errors
    if sync_errors > 0 or buffer_overflows > 0:
        print(f"\n⚠ Stream Errors:")
        if sync_errors > 0:
            print(f"  Sync/Framing Errors : {sync_errors:4d} (invalid length field or corrupted data)")
        if buffer_overflows > 0:
            print(f"  Buffer Overflows    : {buffer_overflows:4d} (receive buffer exceeded {MAX_BUFFER_SIZE} bytes)")

    # Overall health indicator
    if total_errors == 0:
        print(f"\n✓ CRSF Stream Health: EXCELLENT - No errors detected")
    elif total_errors < telemetry_count * 0.01:  # < 1% error rate
        print(f"\n✓ CRSF Stream Health: GOOD - {total_errors} errors ({100*total_errors/(telemetry_count+total_errors):.2f}% error rate)")
    elif total_errors < telemetry_count * 0.05:  # < 5% error rate
        print(f"\n⚠ CRSF Stream Health: FAIR - {total_errors} errors ({100*total_errors/(telemetry_count+total_errors):.2f}% error rate)")
    else:
        print(f"\n✗ CRSF Stream Health: POOR - {total_errors} errors ({100*total_errors/(telemetry_count+total_errors):.2f}% error rate)")
        print(f"   This error rate would likely cause issues with EdgeTX telemetry parsing")

    print(f"{'='*70}")

    return 0

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Send CRSF RC frames to SITL and receive telemetry')
    parser.add_argument('uart', type=int, nargs='?', default=2,
                       help='UART number (default: 2)')
    parser.add_argument('--rate', type=int, default=50,
                       help='Frame rate in Hz (default: 50)')
    parser.add_argument('--duration', type=int, default=None,
                       help='Duration in seconds (default: infinite)')
    parser.add_argument('--show-telemetry', action='store_true',
                       help='Display received telemetry frames on STDOUT')

    args = parser.parse_args()

    sys.exit(send_rc_frames(args.uart, args.rate, args.duration, show_telemetry=args.show_telemetry))
