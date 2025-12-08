#!/usr/bin/env python3
"""
CRSF Telemetry Motion Simulator

This script simulates altitude changes by injecting GPS data via MSP while
simultaneously sending CRSF RC frames and monitoring telemetry responses.

Purpose:
- Test PR #11100's frame 0x09 (barometer/vario telemetry) with changing altitude
- Verify altitude and vario data encoding correctness
- Detect any issues with sensor data when values change

Usage:
    python3 simulate_altitude_motion.py [--duration SECS] [--profile PROFILE]

Profiles:
    climb       - Simulate steady climb from 0m to 100m at 5 m/s
    descent     - Simulate steady descent from 100m to 0m at -3 m/s
    hover       - Simulate hovering at 50m (stationary)
    sine        - Simulate sinusoidal altitude variation
"""

import sys
import time
import socket
import struct
import select
import argparse
import math

# Add uNAVlib to path (relative to this script's location)
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))))
unavlib_path = os.path.join(project_root, 'uNAVlib')
sys.path.insert(0, unavlib_path)
from unavlib.main import MSPy
from unavlib.enums.msp_codes import MSPCodes

# CRSF protocol constants
CRSF_SYNC = 0xC8
CRSF_FRAMETYPE_RC_CHANNELS_PACKED = 0x16

# CRSF frame names
FRAME_NAMES = {
    0x02: 'GPS',
    0x07: 'VARIO',
    0x08: 'BATTERY',
    0x09: 'BARO_ALT',
    0x0A: 'AIRSPEED',
    0x0C: 'RPM',
    0x0D: 'TEMPERATURE',
    0x1E: 'ATTITUDE',
    0x21: 'FLIGHT_MODE'
}

# Altitude encoding constants (from PR #11100)
ALT_MIN_DM = 10000  # -1000m offset in decimeters
ALT_MAX_DM = 22766  # Maximum altitude before switching to low-res mode
VARIO_KL = 0.001525902  # Logarithmic vario constants
VARIO_KR = 0.1677923


def crc8_dvb_s2(data):
    """Calculate CRC8 DVB-S2"""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0xD5
            else:
                crc = crc << 1
            crc &= 0xFF
    return crc


def encode_rc_frame(channels):
    """
    Encode CRSF RC channels frame

    Args:
        channels: List of 16 channel values (0-2047, midpoint=1024)

    Returns:
        bytes: Complete CRSF RC frame with sync, length, type, data, and CRC
    """
    # Pack 16 channels into 11-bit values (22 bytes total)
    packed = bytearray()
    bits = 0
    bit_count = 0

    for ch in channels:
        # Clamp to 11-bit range
        val = max(0, min(2047, ch))
        bits |= (val << bit_count)
        bit_count += 11

        while bit_count >= 8:
            packed.append(bits & 0xFF)
            bits >>= 8
            bit_count -= 8

    # Build frame: sync + length + type + data + CRC
    frame = bytearray([CRSF_SYNC])
    payload = bytearray([CRSF_FRAMETYPE_RC_CHANNELS_PACKED]) + packed
    frame.append(len(payload) + 1)  # +1 for CRC
    frame.extend(payload)
    frame.append(crc8_dvb_s2(payload))

    return bytes(frame)


def decode_altitude(altitude_packed):
    """Decode CRSF packed altitude to meters"""
    if altitude_packed == 0:
        return None, "UNDERFLOW"
    elif altitude_packed == 0xfffe:
        return None, "OVERFLOW"
    elif altitude_packed & 0x8000:
        # Low precision (1m resolution)
        altitude_dm = ((altitude_packed & 0x7fff) * 10)
        return altitude_dm / 10.0, "1m_res"
    else:
        # High precision (0.1m resolution)
        altitude_dm = altitude_packed - ALT_MIN_DM
        return altitude_dm / 10.0, "0.1m_res"


def decode_vario(vario_packed):
    """Decode CRSF packed vario to m/s"""
    if vario_packed == 0:
        return 0.0

    # Handle signed byte
    if vario_packed > 127:
        vario_packed = vario_packed - 256

    sign = 1 if vario_packed > 0 else -1
    abs_packed = abs(vario_packed)

    # Inverse of logarithmic encoding: v = sign * KL * (exp(packed * KR) - 1)
    vario_ms = sign * VARIO_KL * (math.exp(abs_packed * VARIO_KR) - 1)
    return vario_ms


def inject_gps_altitude(board, altitude_cm, lat=0, lon=0, fix_type=3, num_sats=10):
    """
    Inject simulated GPS altitude via MSP_SET_RAW_GPS

    Args:
        board: MSPy board connection
        altitude_cm: Altitude in centimeters
        lat: Latitude (degrees * 1e7), default 0
        lon: Longitude (degrees * 1e7), default 0
        fix_type: GPS fix type (0=no fix, 3=3D fix), default 3
        num_sats: Number of satellites, default 10

    MSP_SET_RAW_GPS format (14 bytes):
        - fixType (uint8)
        - numSat (uint8)
        - lat (int32) - degrees * 1e7
        - lon (int32) - degrees * 1e7
        - alt (uint16) - meters (will be converted to cm internally)
        - groundSpeed (uint16) - cm/s
    """
    # Convert altitude from cm to meters for MSP message
    altitude_m = altitude_cm // 100

    # Pack GPS data
    data = struct.pack('<BBiiHH',
                       fix_type,
                       num_sats,
                       lat,
                       lon,
                       altitude_m,  # MSP wants meters, INAV converts to cm
                       0)  # groundSpeed (cm/s)

    # Send MSP command
    if board.send_RAW_msg(MSPCodes['MSP_SET_RAW_GPS'], data=list(data)):
        # Don't wait for response - SET commands typically don't respond
        pass


def simulate_motion(profile='climb', duration_sec=30, port=5761):
    """
    Simulate altitude motion while monitoring CRSF telemetry

    Args:
        profile: Motion profile (climb, descent, hover, sine)
        duration_sec: Test duration in seconds
        port: CRSF UART port (5761 for UART2)
    """
    print("=" * 70)
    print("CRSF Telemetry Motion Simulator")
    print("=" * 70)
    print(f"\nProfile: {profile}")
    print(f"Duration: {duration_sec}s")
    print(f"CRSF Port: {port}")
    print()

    # Connect to MSP (UART1 port 5760)
    print("Connecting to SITL MSP (port 5760)...")
    board = None
    try:
        board = MSPy(device="5760", use_tcp=True, loglevel='WARNING')
        if board == 1:
            print("✗ MSP connection failed")
            return
        print("✓ MSP connected")
        # Wait for SITL to be fully ready before sending commands
        print("Waiting for SITL to initialize...")
        time.sleep(3)
    except Exception as e:
        print(f"✗ MSP connection error: {e}")
        return

    # Connect to CRSF (UART2)
    print(f"Connecting to SITL CRSF (port {port})...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('127.0.0.1', port))
        sock.setblocking(False)  # Non-blocking for select()
        print("✓ CRSF connected")
    except Exception as e:
        print(f"✗ CRSF connection error: {e}")
        board.disconnect()
        return

    print()
    print("Starting motion simulation...")
    print()

    # RC frame: all channels at midpoint (1024)
    channels = [1024] * 16
    rc_frame = encode_rc_frame(channels)

    # Motion parameters
    start_time = time.time()
    frame_count = 0
    telemetry_frames = {}
    frame_0x09_samples = []

    # RC sending rate
    rc_interval = 1.0 / 50  # 50 Hz
    last_rc_time = 0

    # MSP altitude injection rate
    msp_interval = 1.0 / 10  # 10 Hz
    last_msp_time = 0

    # Telemetry frame buffer
    telemetry_buffer = b''

    try:
        while (time.time() - start_time) < duration_sec:
            current_time = time.time() - start_time

            # Calculate altitude based on profile
            if profile == 'climb':
                altitude_m = min(100, current_time * 5)  # 5 m/s climb to 100m
            elif profile == 'descent':
                altitude_m = max(0, 100 - current_time * 3)  # 3 m/s descent from 100m
            elif profile == 'hover':
                altitude_m = 50  # Stationary at 50m
            elif profile == 'sine':
                altitude_m = 50 + 30 * math.sin(current_time * 0.5)  # ±30m around 50m
            else:
                altitude_m = 0

            # Inject GPS altitude via MSP at 10 Hz
            if time.time() - last_msp_time >= msp_interval:
                inject_gps_altitude(board, int(altitude_m * 100))  # Convert m to cm
                last_msp_time = time.time()

            # Send RC frame at 50 Hz
            if time.time() - last_rc_time >= rc_interval:
                sock.sendall(rc_frame)
                frame_count += 1
                last_rc_time = time.time()

            # Read telemetry (non-blocking)
            readable, _, _ = select.select([sock], [], [], 0)
            if readable:
                try:
                    chunk = sock.recv(256)
                    telemetry_buffer += chunk

                    # Parse CRSF frames
                    while len(telemetry_buffer) >= 3:
                        if telemetry_buffer[0] == CRSF_SYNC:
                            frame_len = telemetry_buffer[1]
                            if frame_len >= 2 and len(telemetry_buffer) >= frame_len + 2:
                                frame_type = telemetry_buffer[2]
                                frame_data = bytes(telemetry_buffer[:frame_len + 2])

                                # Count frames
                                telemetry_frames[frame_type] = telemetry_frames.get(frame_type, 0) + 1

                                # Decode frame 0x09 (barometer/vario)
                                if frame_type == 0x09 and len(frame_data) >= 7:
                                    altitude_packed = (frame_data[3] << 8) | frame_data[4]
                                    vario_packed = frame_data[5]

                                    altitude_decoded, res = decode_altitude(altitude_packed)
                                    vario_decoded = decode_vario(vario_packed)

                                    frame_0x09_samples.append({
                                        'time': current_time,
                                        'injected_alt': altitude_m,
                                        'decoded_alt': altitude_decoded,
                                        'decoded_vario': vario_decoded,
                                        'resolution': res
                                    })

                                    # Print sample every 2 seconds
                                    if len(frame_0x09_samples) % 20 == 0:
                                        print(f"[{current_time:5.1f}s] Injected: {altitude_m:6.1f}m | "
                                              f"Telemetry: {altitude_decoded:6.1f}m, {vario_decoded:+6.2f} m/s")

                                telemetry_buffer = telemetry_buffer[frame_len + 2:]
                            else:
                                break
                        else:
                            telemetry_buffer = telemetry_buffer[1:]
                except socket.error:
                    pass

            # Small sleep to prevent busy-wait
            time.sleep(0.001)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        sock.close()
        if board is not None:
            try:
                board.reboot()  # Cleanly disconnect by rebooting
            except:
                pass  # Ignore errors during cleanup

    # Print results
    print()
    print("=" * 70)
    print("Test Results")
    print("=" * 70)
    print(f"\nRC frames sent: {frame_count}")
    print(f"Telemetry frames received: {sum(telemetry_frames.values())}")
    print()
    print("Frame distribution:")
    for ft in sorted(telemetry_frames.keys()):
        name = FRAME_NAMES.get(ft, f'UNKNOWN')
        print(f"  0x{ft:02X} {name:16s}: {telemetry_frames[ft]} frames")

    if frame_0x09_samples:
        print()
        print(f"Frame 0x09 (BARO_ALT) samples: {len(frame_0x09_samples)}")
        print()
        print("Sample data:")
        print("  Time    | Injected Alt | Decoded Alt | Vario    | Resolution")
        print("  --------|--------------|-------------|----------|------------")
        for sample in frame_0x09_samples[::10]:  # Every 10th sample
            print(f"  {sample['time']:5.1f}s | {sample['injected_alt']:11.1f}m | "
                  f"{sample['decoded_alt']:10.1f}m | {sample['decoded_vario']:+7.2f} | "
                  f"{sample['resolution']}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simulate altitude motion for CRSF telemetry testing')
    parser.add_argument('--duration', type=int, default=30, help='Test duration in seconds (default: 30)')
    parser.add_argument('--profile', choices=['climb', 'descent', 'hover', 'sine'],
                        default='climb', help='Motion profile (default: climb)')
    parser.add_argument('--port', type=int, default=5761, help='CRSF UART port (default: 5761 for UART2)')

    args = parser.parse_args()

    simulate_motion(profile=args.profile, duration_sec=args.duration, port=args.port)
