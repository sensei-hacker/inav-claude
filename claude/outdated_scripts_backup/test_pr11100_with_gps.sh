#!/bin/bash
#
# PR #11100 CRSF Telemetry Test with GPS Altitude Motion
#
# This script tests the BAROMETER_ALT_VARIO frame (0x09) from PR #11100
# with simulated GPS altitude changes to verify altitude tracking.
#
# Usage:
#   ./test_pr11100_with_gps.sh [gps_profile]
#
# Parameters:
#   gps_profile  - GPS motion profile: climb, descent, hover, sine (default: climb)

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GPS_SCRIPT="$SCRIPT_DIR/../gps/inject_gps_altitude.py"
BUILD_DIR="build_sitl_pr11100"
INAV_ROOT="/home/raymorris/Documents/planes/inavflight/inav"
SITL_BIN="$INAV_ROOT/$BUILD_DIR/bin/SITL.elf"
SITL_LOG="/tmp/sitl_pr11100_gps.log"
RC_SENDER_SCRIPT="$SCRIPT_DIR/crsf_rc_sender.py"
GPS_PROFILE="${1:-climb}"
TEST_DURATION=30

echo "======================================================================"
echo "PR #11100 CRSF Telemetry Test with GPS Motion"
echo "======================================================================"
echo ""
echo "Configuration:"
echo "  Build Dir:   $BUILD_DIR"
echo "  GPS Profile: $GPS_PROFILE"
echo "  Duration:    ${TEST_DURATION}s"
echo ""

# Step 1: Verify binaries exist
echo "[1/8] Verifying prerequisites..."
if [ ! -f "$SITL_BIN" ]; then
    echo "ERROR: SITL binary not found: $SITL_BIN"
    exit 1
fi
if [ ! -f "$GPS_SCRIPT" ]; then
    echo "ERROR: GPS injection script not found: $GPS_SCRIPT"
    exit 1
fi
echo "OK SITL binary and GPS script found"

# Step 2: Cleanup
echo ""
echo "[2/8] Cleaning up existing processes..."
pkill -9 SITL.elf 2>/dev/null || true
pkill -9 -f crsf_rc_sender 2>/dev/null || true
pkill -9 -f inject_gps 2>/dev/null || true
sleep 2
echo "OK Cleanup complete"

# Step 3: Start SITL
echo ""
echo "[3/8] Starting SITL..."
cd "$INAV_ROOT/$BUILD_DIR"
# rm -f eeprom.bin
./bin/SITL.elf > "$SITL_LOG" 2>&1 &
# ( ./bin/SITL.elf 2>&1 | egrep -v 'Program word' > $SITL_LOG ) &
SITL_PID=$!
sleep 4

if ! pgrep -x SITL.elf > /dev/null; then
    echo "ERROR: SITL failed to start"
    tail -20 "$SITL_LOG"
    exit 1
fi
echo "OK SITL started"

# Step 4: Configure CRSF and TELEMETRY
echo ""
echo "[4/8] Configuring CRSF and TELEMETRY..."
python3 "$SCRIPT_DIR/configure_sitl_crsf.py" --no-reboot
if [ $? -ne 0 ]; then
    echo "ERROR: Configuration failed"
    pkill -9 SITL.elf
    exit 1
fi

# Step 5: Start RC sender BEFORE reboot (brief, just for init)
echo ""
echo "[5/8] Starting RC sender briefly for CRSF init..."
python3 "$RC_SENDER_SCRIPT" 2 --rate 50 --duration 3 > /tmp/rc_sender_gps_test.log 2>&1 &
RC_PID=$!
sleep 2

if ! pgrep -f crsf_rc_sender > /dev/null; then
    echo "WARNING: RC sender may have already completed"
fi
echo "OK RC sender started (PID: $RC_PID)"

# Step 6: Reboot SITL
echo ""
echo "[6/8] Rebooting SITL..."
python3 "$SCRIPT_DIR/reboot_sitl.py"
sleep 8

if ! pgrep -x SITL.elf > /dev/null; then
    echo "ERROR: SITL died after reboot"
    pkill -9 SITL.elf
    exit 1
fi

# Verify UART2 is bound
if ! grep -q "Bind TCP.*5761" "$SITL_LOG"; then
    echo "ERROR: UART2 not bound"
    tail -30 "$SITL_LOG"
    pkill -9 SITL.elf
    exit 1
fi
echo "OK SITL rebooted (UART2 on port 5761)"

# Step 6b: Enable HITL mode (must be done after every boot)
echo ""
echo "[6b/8] Enabling HITL mode for arming..."
python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from configure_sitl_crsf import enable_hitl_mode
enable_hitl_mode(5760)
"
if [ $? -ne 0 ]; then
    echo "WARNING: HITL mode may not have been enabled"
fi

# Step 7: Start GPS altitude injection
echo ""
echo "[7/8] Starting GPS altitude injection ($GPS_PROFILE profile)..."
python3 "$GPS_SCRIPT" --profile "$GPS_PROFILE" --duration "$TEST_DURATION" > /tmp/gps_injection.log 2>&1 &
GPS_PID=$!
sleep 2

if ! pgrep -f inject_gps > /dev/null; then
    echo "WARNING: GPS injection may have failed"
    cat /tmp/gps_injection.log
fi
echo "OK GPS injection running (PID: $GPS_PID)"

# Step 8: Capture and analyze telemetry (with RC sending for arming)
echo ""
echo "[8/8] Capturing CRSF telemetry for ${TEST_DURATION}s..."
echo "      (with RC sender for arming sequence)"
echo ""

python3 << 'EOF'
import socket
import time
import struct
import select

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

# CRSF RC frame constants
CRSF_ADDRESS_FC = 0xC8
CRSF_FRAMETYPE_RC = 0x16
CRSF_RC_PAYLOAD_SIZE = 22

def crc8_dvb_s2(crc, data):
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0xD5) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc

def pack_rc_channels(channels):
    """Pack 16 RC channels (11 bits each) into 22 bytes."""
    packed = []
    for ch in channels:
        value = int((ch - 1000) * 1.639 + 172)
        value = max(172, min(1811, value))
        packed.append(value)

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
    if bit_count > 0:
        result.append(bits & 0xFF)
    return bytes(result[:22])

def create_rc_frame(channels):
    """Create a CRSF RC channels frame."""
    payload = pack_rc_channels(channels)
    frame = bytearray()
    frame.append(CRSF_ADDRESS_FC)
    frame.append(CRSF_RC_PAYLOAD_SIZE + 2)
    frame.append(CRSF_FRAMETYPE_RC)
    frame.extend(payload)
    crc = crc8_dvb_s2(0, bytes(frame[2:]))
    frame.append(crc)
    return bytes(frame)

TEST_DURATION = 30

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(0.5)
sock.connect(('127.0.0.1', 5761))
sock.setblocking(False)

frames_seen = {}
frame_0x09_data = []  # Store all 0x09 frame data for analysis
flight_modes_seen = set()  # Store unique flight mode strings
data_buffer = b''
start = time.time()

# RC frame timing
RC_RATE_HZ = 50
frame_interval = 1.0 / RC_RATE_HZ
next_rc_time = start
rc_frames_sent = 0

# Channel values (16 channels)
channels = [1500] * 16  # All mid-stick initially

print("Sending RC frames + capturing telemetry...")
print("  Arming sequence: throttle low -> ARM -> throttle up")
print("")

while time.time() - start < TEST_DURATION:
    current_time = time.time()
    elapsed = current_time - start

    # Update channel values for arming sequence
    # 0-3s: throttle low, disarmed
    # 3-4s: throttle low, ARM high (arming)
    # 4s+: throttle up, ARM high (flying)
    if elapsed > 4:
        channels[2] = 1600   # Throttle up
        channels[4] = 2000   # ARM high
    elif elapsed > 3:
        channels[2] = 1000   # Throttle low
        channels[4] = 2000   # ARM high - arm here
    else:
        channels[2] = 1000   # Throttle low
        channels[4] = 1000   # ARM low

    # Send RC frame if it's time
    if current_time >= next_rc_time:
        try:
            rc_frame = create_rc_frame(channels)
            sock.sendall(rc_frame)
            rc_frames_sent += 1
            next_rc_time += frame_interval
        except:
            pass

    # Read telemetry (non-blocking)
    try:
        readable, _, _ = select.select([sock], [], [], 0.001)
        if readable:
            data = sock.recv(2048)
            if data:
                data_buffer += data

                while len(data_buffer) >= 3:
                    if data_buffer[0] == 0xC8:
                        frame_len = data_buffer[1]
                        if frame_len >= 2 and len(data_buffer) >= frame_len + 2:
                            frame_type = data_buffer[2]

                            # Count frames
                            frames_seen[frame_type] = frames_seen.get(frame_type, 0) + 1

                            # Store 0x09 frame data
                            if frame_type == 0x09 and len(data_buffer) >= 7:
                                altitude_packed = (data_buffer[3] << 8) | data_buffer[4]
                                vario_packed = data_buffer[5]
                                timestamp = time.time() - start
                                frame_0x09_data.append({
                                    'time': timestamp,
                                    'alt_packed': altitude_packed,
                                    'vario_packed': vario_packed
                                })

                            # Store 0x21 FLIGHT_MODE data (null-terminated string)
                            if frame_type == 0x21 and frame_len > 2:
                                # Frame payload starts at byte 3, ends before CRC
                                payload_len = frame_len - 2  # exclude type and CRC
                                if len(data_buffer) >= 3 + payload_len:
                                    payload = data_buffer[3:3 + payload_len]
                                    # Find null terminator or use whole payload
                                    null_pos = payload.find(b'\x00')
                                    if null_pos > 0:
                                        mode_str = payload[:null_pos].decode('ascii', errors='replace')
                                    else:
                                        mode_str = payload.rstrip(b'\x00').decode('ascii', errors='replace')
                                    if mode_str:
                                        flight_modes_seen.add(mode_str)

                            data_buffer = data_buffer[frame_len + 2:]
                        else:
                            break
                    else:
                        data_buffer = data_buffer[1:]
    except:
        pass

sock.close()
print(f"Sent {rc_frames_sent} RC frames")

# Print results
print("=" * 70)
print("PR #11100 Telemetry Results with GPS Motion")
print("=" * 70)
print(f"{len(frames_seen)} unique frame types received:")
print("")

for ft in sorted(frames_seen.keys()):
    name = FRAME_NAMES.get(ft, f'UNKNOWN')
    marker = '*' if ft == 0x09 else ' '
    print(f"{marker} 0x{ft:02X} {name:24s} x{frames_seen[ft]}")

# Show FLIGHT_MODE analysis first
print("")
print("=" * 70)
print("FLIGHT_MODE (0x21) Analysis")
print("=" * 70)
if flight_modes_seen:
    print(f"Flight modes seen: {', '.join(sorted(flight_modes_seen))}")
    is_armed = any('ARM' in m.upper() for m in flight_modes_seen)
    if is_armed:
        print("  STATUS: ARMED")
    else:
        print("  STATUS: NOT ARMED (altitude telemetry may not update)")
else:
    print("  No FLIGHT_MODE frames decoded")
    is_armed = False

print("")
print("=" * 70)
print("BAROMETER_ALT_VARIO (0x09) Analysis")
print("=" * 70)

if 0x09 in frames_seen:
    print(f"Total 0x09 frames: {frames_seen[0x09]}")
    print("")

    if len(frame_0x09_data) > 0:
        # Sample first, middle, and last frames
        samples = [
            ("First", frame_0x09_data[0]),
            ("Middle", frame_0x09_data[len(frame_0x09_data)//2]),
            ("Last", frame_0x09_data[-1])
        ]

        print("Sample frames:")
        for label, data in samples:
            # Decode altitude: packed value is altitude in 0.5m units, offset by 10000
            # actual_altitude = (packed - 10000) * 0.5
            alt_m = (data['alt_packed'] - 10000) * 0.5

            # Decode vario: signed 8-bit, 0.1 m/s resolution
            vario_raw = data['vario_packed']
            if vario_raw > 127:
                vario_raw = vario_raw - 256
            vario_ms = vario_raw * 0.1

            print(f"  {label:7s} @ {data['time']:5.1f}s: alt={alt_m:6.1f}m, vario={vario_ms:+5.1f}m/s (packed: 0x{data['alt_packed']:04X}, 0x{data['vario_packed']:02X})")

        # Calculate altitude range
        alt_values = [(d['alt_packed'] - 10000) * 0.5 for d in frame_0x09_data]
        alt_min = min(alt_values)
        alt_max = max(alt_values)
        alt_range = alt_max - alt_min

        print("")
        print("Altitude statistics:")
        print(f"  Min altitude: {alt_min:.1f}m")
        print(f"  Max altitude: {alt_max:.1f}m")
        print(f"  Range:        {alt_range:.1f}m")

        print("")
        if alt_range > 1.0:
            print("SUCCESS: Altitude is changing - GPS injection working!")
            exit(0)
        else:
            print("WARNING: Altitude range < 1m - GPS injection may not be affecting telemetry")
            exit(1)
    else:
        print("ERROR: No 0x09 frame data captured")
        exit(1)
else:
    print("ERROR: No BAROMETER_ALT_VARIO (0x09) frames received!")
    exit(1)
EOF

TEST_RESULT=$?

# Cleanup
echo ""
echo "Cleanup..."
pkill -9 -f crsf_rc_sender 2>/dev/null || true
pkill -9 -f inject_gps 2>/dev/null || true
pkill -9 SITL.elf 2>/dev/null || true
echo "OK Processes stopped"

# Show GPS injection log
echo ""
echo "GPS Injection Log:"
cat /tmp/gps_injection.log 2>/dev/null | head -20

echo ""
echo "======================================================================"
if [ $TEST_RESULT -eq 0 ]; then
    echo "TEST PASSED: PR #11100 altitude tracking verified!"
else
    echo "TEST INCOMPLETE: Altitude tracking needs verification"
fi
echo "======================================================================"

exit $TEST_RESULT
