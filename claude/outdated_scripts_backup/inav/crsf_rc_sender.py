#!/usr/bin/env python3
"""
CRSF RC Frame Sender - Sends RC channel data to SITL CRSF RX

This simulates a CRSF transmitter sending RC channel data to the flight controller,
which triggers CRSF telemetry responses.
"""

import socket
import struct
import time
import sys

# CRSF Constants
CRSF_ADDRESS_FLIGHT_CONTROLLER = 0xC8
CRSF_FRAMETYPE_RC_CHANNELS_PACKED = 0x16
CRSF_FRAME_RC_CHANNELS_PAYLOAD_SIZE = 22  # 11 bits per channel * 16 channels = 22 bytes

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

def send_rc_frames(uart_num=2, rate_hz=50, duration_sec=None):
    """
    Send CRSF RC frames to SITL.

    Args:
        uart_num: UART number (default 2)
        rate_hz: Frame rate in Hz (default 50 - standard CRSF rate)
        duration_sec: Duration to send (None = infinite)
    """
    port = 5760 + (uart_num - 1)
    print(f"=== CRSF RC Frame Sender ===")
    print(f"Connecting to SITL UART{uart_num} on port {port}...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)

    try:
        sock.connect(('127.0.0.1', port))
        print(f"✓ Connected to 127.0.0.1:{port}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return 1

    print(f"\nSending RC frames at {rate_hz}Hz...")
    print("Channels: All at 1500us (midpoint)")
    if duration_sec:
        print(f"Duration: {duration_sec} seconds")
    else:
        print("Duration: Infinite (press Ctrl+C to stop)")
    print()

    # Default channels - all at midpoint (1500us)
    channels = [1500] * 16

    frame_interval = 1.0 / rate_hz
    frame_count = 0
    start_time = time.time()

    try:
        while True:
            # Create and send frame
            frame = create_rc_frame(channels)
            sock.sendall(frame)
            frame_count += 1

            # Status update every 50 frames
            if frame_count % 50 == 0:
                elapsed = time.time() - start_time
                actual_rate = frame_count / elapsed if elapsed > 0 else 0
                print(f"Sent {frame_count} frames ({actual_rate:.1f} Hz actual)")

            # Check duration
            if duration_sec and (time.time() - start_time) >= duration_sec:
                break

            # Sleep for next frame
            time.sleep(frame_interval)

    except KeyboardInterrupt:
        print("\n\n✓ Stopped by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1
    finally:
        sock.close()

    elapsed = time.time() - start_time
    print(f"\nSent {frame_count} frames in {elapsed:.1f} seconds")
    print(f"Average rate: {frame_count/elapsed:.1f} Hz")

    return 0

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Send CRSF RC frames to SITL')
    parser.add_argument('uart', type=int, nargs='?', default=2,
                       help='UART number (default: 2)')
    parser.add_argument('--rate', type=int, default=50,
                       help='Frame rate in Hz (default: 50)')
    parser.add_argument('--duration', type=int, default=None,
                       help='Duration in seconds (default: infinite)')

    args = parser.parse_args()

    sys.exit(send_rc_frames(args.uart, args.rate, args.duration))
