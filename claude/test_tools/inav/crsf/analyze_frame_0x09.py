#!/usr/bin/env python3
"""
CRSF Frame 0x09 Analyzer - Decode Barometer/Vario Data

Decodes frame 0x09 (CRSF_FRAMETYPE_BAROMETER_ALTITUDE_VARIO_SENSOR) to verify:
1. Altitude data is valid (not 0, not garbage)
2. Vario data is reasonable
3. Data changes over time (not frozen/stale)

Frame 0x09 Format:
- uint16_t altitude_packed (decimeters - 10000, with special encoding)
- int8_t vario_packed (logarithmic vertical speed)
"""

import struct
import math

# Constants from crsf.c
ALT_MIN_DM = 10000
ALT_THRESHOLD_DM = 0x8000 - ALT_MIN_DM
ALT_MAX_DM = 0x7ffe * 10 - 5
VARIO_KL = 100.0
VARIO_KR = 0.026

def decode_altitude(altitude_packed):
    """
    Decode CRSF packed altitude to meters.

    From crsf.c:285-297:
    if (altitude_dm < -ALT_MIN_DM):
        altitude_packed = 0
    elif (altitude_dm > ALT_MAX_DM):
        altitude_packed = 0xfffe
    elif (altitude_dm < ALT_THRESHOLD_DM):
        altitude_packed = altitude_dm + ALT_MIN_DM
    else:
        altitude_packed = ((altitude_dm + 5) / 10) | 0x8000
    """
    if altitude_packed == 0:
        return "UNDERFLOW (< -1000m)"
    elif altitude_packed == 0xfffe:
        return "OVERFLOW (> 32766.5m)"
    elif altitude_packed & 0x8000:
        # High precision mode OFF, low precision (1m resolution)
        altitude_dm = ((altitude_packed & 0x7fff) * 10)
        return f"{altitude_dm / 10:.1f}m (1m res)"
    else:
        # High precision mode ON (0.1m resolution)
        altitude_dm = altitude_packed - ALT_MIN_DM
        return f"{altitude_dm / 10:.1f}m (0.1m res)"

def decode_vario(vario_packed):
    """
    Decode CRSF packed vario to m/s.

    From crsf.c:299-301:
    float vario_sm = getEstimatedActualVelocity(Z);
    int8_t sign = vario_sm < 0 ? -1 : ( vario_sm > 0 ? 1 : 0 );
    int8_t vario_packed = constrain(lrintf(log(ABS(vario_sm) / VARIO_KL + 1) / VARIO_KR * sign), SCHAR_MIN, SCHAR_MAX);

    Reverse:
    vario_sm = sign * VARIO_KL * (exp(vario_packed * VARIO_KR) - 1)
    """
    if vario_packed == 0:
        return "0.0 m/s"

    # Convert from int8 to signed
    if vario_packed > 127:
        vario_packed = vario_packed - 256

    sign = 1 if vario_packed > 0 else -1
    abs_packed = abs(vario_packed)

    # Reverse the logarithmic encoding
    vario_ms = sign * VARIO_KL * (math.exp(abs_packed * VARIO_KR) - 1)

    return f"{vario_ms:+.2f} m/s"

def analyze_frame_0x09(frame_bytes):
    """
    Analyze a complete frame 0x09.

    Expected format:
    [SYNC] [LEN] [TYPE=0x09] [ALT_H] [ALT_L] [VARIO] [CRC]
    """
    if len(frame_bytes) < 7:
        return "ERROR: Frame too short"

    frame_type = frame_bytes[2]
    if frame_type != 0x09:
        return f"ERROR: Not frame 0x09 (got 0x{frame_type:02x})"

    # Extract altitude (uint16, big-endian)
    altitude_packed = (frame_bytes[3] << 8) | frame_bytes[4]

    # Extract vario (int8)
    vario_packed = frame_bytes[5]

    # Decode
    altitude_str = decode_altitude(altitude_packed)
    vario_str = decode_vario(vario_packed)

    return f"Alt: {altitude_str}, Vario: {vario_str} (raw: 0x{altitude_packed:04x}, 0x{vario_packed:02x})"

def check_for_issues(frames_0x09):
    """
    Check for common issues:
    1. All altitude values are 0 (uninitialized)
    2. All altitude values are same (frozen)
    3. Altitude values are suspiciously wrong
    """
    if not frames_0x09:
        return ["No frame 0x09 data received"]

    issues = []

    # Extract all altitude values
    altitudes = []
    for frame in frames_0x09:
        if len(frame) >= 7:
            altitude_packed = (frame[3] << 8) | frame[4]
            altitudes.append(altitude_packed)

    # Check for all zeros
    if all(alt == 0 for alt in altitudes):
        issues.append("CRITICAL: All altitude values are 0 (UNDERFLOW - likely uninitialized)")

    # Check for all same value (frozen)
    if len(set(altitudes)) == 1 and len(altitudes) > 10:
        issues.append(f"WARNING: All altitude values are identical (0x{altitudes[0]:04x}) - possible stale data")

    # Check for suspiciously high values
    if any(alt == 0xfffe for alt in altitudes):
        issues.append("WARNING: Altitude OVERFLOW detected (> 32766.5m)")

    return issues if issues else ["No obvious issues detected"]

if __name__ == "__main__":
    # Test cases
    print("=== Frame 0x09 Decoder Test Cases ===\n")

    # Test 1: Normal altitude at sea level (0m)
    test1 = bytes([0xC8, 0x06, 0x09, 0x27, 0x10, 0x00, 0xFF])  # 10000 - 10000 = 0dm = 0m
    print(f"Test 1 (0m alt, 0 vario): {analyze_frame_0x09(test1)}")

    # Test 2: 100m altitude, +1 m/s climb
    test2 = bytes([0xC8, 0x06, 0x09, 0x27, 0xF4, 0x26, 0xFF])  # 11000 - 10000 = 1000dm = 100m
    print(f"Test 2 (100m alt, +1m/s): {analyze_frame_0x09(test2)}")

    # Test 3: Underflow (uninitialized)
    test3 = bytes([0xC8, 0x06, 0x09, 0x00, 0x00, 0x00, 0xFF])
    print(f"Test 3 (UNDERFLOW): {analyze_frame_0x09(test3)}")

    # Test 4: Overflow
    test4 = bytes([0xC8, 0x06, 0x09, 0xFF, 0xFE, 0x00, 0xFF])
    print(f"Test 4 (OVERFLOW): {analyze_frame_0x09(test4)}")

    print("\n=== Usage ===")
    print("This decoder will be integrated into crsf_rc_sender.py for real-time analysis")
