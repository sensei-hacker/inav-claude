#!/usr/bin/env python3
"""Capture and identify CRSF telemetry frame types"""

import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
sock.connect(('127.0.0.1', 5761))

print('Connected to SITL UART2 (port 5761), capturing frames...')
print()

frames_seen = {}  # type -> count
data_buffer = b''
total_frames = 0

for i in range(200):  # Capture up to 200 iterations
    try:
        data = sock.recv(2048)
        if not data:
            break
        data_buffer += data

        # Parse CRSF frames: 0xC8 (address) + length + type + payload + CRC
        while len(data_buffer) >= 3:
            if data_buffer[0] == 0xC8:
                frame_len = data_buffer[1]
                if frame_len >= 2 and len(data_buffer) >= frame_len + 2:
                    frame_type = data_buffer[2]

                    # Track frame types
                    frames_seen[frame_type] = frames_seen.get(frame_type, 0) + 1
                    total_frames += 1

                    # Print first occurrence of each frame type
                    if frames_seen[frame_type] == 1:
                        print(f'✓ NEW FRAME: 0x{frame_type:02X} (len={frame_len})')

                    # Move to next frame
                    data_buffer = data_buffer[frame_len + 2:]
                else:
                    break  # Need more data
            else:
                # Resync - skip invalid byte
                data_buffer = data_buffer[1:]

        time.sleep(0.01)  # 10ms delay

    except socket.timeout:
        break

sock.close()

print()
print('=' * 70)
print(f'CAPTURED {total_frames} total frames')
print('=' * 70)
print()
print('Frame types detected (with counts):')
for frame_type in sorted(frames_seen.keys()):
    count = frames_seen[frame_type]
    type_name = {
        0x02: 'GPS',
        0x07: 'VARIO',
        0x08: 'BATTERY',
        0x09: 'BAROMETER',
        0x0A: 'AIRSPEED',
        0x0C: 'RPM',
        0x0D: 'TEMPERATURE',
        0x1E: 'ATTITUDE',
    }.get(frame_type, 'UNKNOWN')
    print(f'  0x{frame_type:02X} {type_name:12s} - {count:4d} frames')

print()
print('PR #11025 Target Frames:')
pr11025_frames = {0x09: 'BAROMETER', 0x0A: 'AIRSPEED', 0x0C: 'RPM', 0x0D: 'TEMPERATURE'}
for frame_type, name in pr11025_frames.items():
    if frame_type in frames_seen:
        print(f'  ✅ 0x{frame_type:02X} {name} - FOUND ({frames_seen[frame_type]} frames)')
    else:
        print(f'  ❌ 0x{frame_type:02X} {name} - MISSING')
