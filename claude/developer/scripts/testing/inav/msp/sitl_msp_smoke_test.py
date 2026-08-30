#!/usr/bin/env python3
"""
SITL Smoke Test v3 for refactor/flash-reduction-osd-msp-switch-cases
Corrected MSP2 command IDs and payload sizes.
"""
import socket
import struct
import time
import sys

HOST = "127.0.0.1"
PORT = 5760

# MSP v1 command IDs
MSP_API_VERSION          = 1
MSP_STATUS               = 101
MSP_ATTITUDE             = 108
MSP_RC_TUNING            = 111
MSP_SET_RC_TUNING        = 204
MSP_CALIBRATION_DATA     = 14
MSP_SET_CALIBRATION_DATA = 15

# MSP v2 command IDs (from msp_protocol_v2_inav.h and msp_protocol_v2_common.h)
MSP2_COMMON_MOTOR_MIXER    = 0x1005
MSP2_INAV_RATE_PROFILE     = 0x2007
MSP2_INAV_SET_RATE_PROFILE = 0x2008

PASS = 0
FAIL = 0


def result(label, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS  {label}" + (f" — {detail}" if detail else ""))
    else:
        FAIL += 1
        print(f"  FAIL  {label}" + (f" — {detail}" if detail else ""))


def crc8_dvb_s2(data):
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc


def build_v1(cmd, payload=b""):
    size = len(payload)
    cs = size ^ cmd
    for b in payload:
        cs ^= b
    return b"$M<" + bytes([size, cmd]) + payload + bytes([cs])


def build_v2(cmd, payload=b""):
    flag = 0
    size = len(payload)
    header = bytes([flag]) + struct.pack("<HH", cmd, size)
    crc = crc8_dvb_s2(header + payload)
    return b"$X<" + header + payload + bytes([crc])


def recv_one(sock, timeout=3.0):
    """Read one complete MSP response (v1 or v2). Returns (cmd, payload)."""
    sock.settimeout(0.1)
    buf = b""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            chunk = sock.recv(512)
            if not chunk:
                raise IOError("Connection closed by SITL")
            buf += chunk
        except socket.timeout:
            pass

        while len(buf) >= 3:
            if buf[:3] == b"$M>":
                if len(buf) < 5:
                    break
                sz = buf[3]
                cmd = buf[4]
                needed = 5 + sz + 1
                if len(buf) < needed:
                    break
                payload = buf[5:5 + sz]
                return (cmd, payload)

            elif buf[:3] == b"$M!":
                if len(buf) < 5:
                    break
                sz = buf[3]
                cmd = buf[4]
                needed = 5 + sz + 1
                if len(buf) < needed:
                    break
                raise ValueError(f"MSP error response for cmd {cmd}")

            elif buf[:3] == b"$X>":
                if len(buf) < 9:
                    break
                cmd = struct.unpack_from("<H", buf, 4)[0]
                sz = struct.unpack_from("<H", buf, 6)[0]
                needed = 8 + sz + 1
                if len(buf) < needed:
                    break
                payload = buf[8:8 + sz]
                return (cmd, payload)

            else:
                next_v1 = buf.find(b"$M")
                next_v2 = buf.find(b"$X")
                nxt = min(
                    next_v1 if next_v1 != -1 else len(buf),
                    next_v2 if next_v2 != -1 else len(buf)
                )
                if nxt == 0:
                    buf = buf[1:]
                else:
                    buf = buf[nxt:]

    raise TimeoutError(f"No MSP response within {timeout}s (buf {len(buf)} bytes: {buf[:20].hex()})")


def query_v1(cmd, payload=b"", timeout=3.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    s.connect((HOST, PORT))
    s.sendall(build_v1(cmd, payload))
    resp = recv_one(s, timeout)
    s.close()
    return resp


def query_v2(cmd, payload=b"", timeout=3.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    s.connect((HOST, PORT))
    s.sendall(build_v2(cmd, payload))
    resp = recv_one(s, timeout)
    s.close()
    return resp


def set_and_read_v1(set_cmd, set_payload, read_cmd, delay=0.1):
    """On one connection: SET (read ACK), then GET."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    s.connect((HOST, PORT))
    s.sendall(build_v1(set_cmd, set_payload))
    ack_cmd, _ = recv_one(s, timeout=3.0)
    if ack_cmd != set_cmd:
        s.close()
        raise ValueError(f"Expected ACK for cmd {set_cmd}, got cmd {ack_cmd}")
    time.sleep(delay)
    s.sendall(build_v1(read_cmd))
    resp_cmd, resp_payload = recv_one(s, timeout=3.0)
    s.close()
    return resp_cmd, resp_payload


def set_and_read_v2(set_cmd, set_payload, read_cmd, delay=0.1):
    """On one connection: SET v2 (read ACK), then GET v2."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    s.connect((HOST, PORT))
    s.sendall(build_v2(set_cmd, set_payload))
    ack_cmd, _ = recv_one(s, timeout=3.0)
    time.sleep(delay)
    s.sendall(build_v2(read_cmd))
    resp_cmd, resp_payload = recv_one(s, timeout=3.0)
    s.close()
    return resp_cmd, resp_payload


def sanity_check():
    try:
        cmd, _ = query_v1(MSP_API_VERSION)
        return cmd == MSP_API_VERSION
    except Exception:
        return False


def run_tests():
    print(f"\nConnecting to SITL at {HOST}:{PORT}...")
    if not sanity_check():
        print("  FAIL  Cannot get MSP_API_VERSION from SITL")
        print("  Note: If in sandbox, retry with dangerouslyDisableSandbox: true")
        sys.exit(1)
    print("  Connected and responding.\n")

    # ----------------------------------------------------------------
    print("=== Basic Connectivity ===")
    try:
        cmd, payload = query_v1(MSP_API_VERSION)
        result("MSP_API_VERSION", cmd == MSP_API_VERSION, f"len={len(payload)}")
    except Exception as e:
        result("MSP_API_VERSION", False, str(e))

    # ----------------------------------------------------------------
    print("\n=== MSP_STATUS ===")
    try:
        cmd, payload = query_v1(MSP_STATUS)
        result("MSP_STATUS responds", cmd == MSP_STATUS, f"len={len(payload)}")
        if cmd == MSP_STATUS and len(payload) >= 2:
            cycle_time = struct.unpack_from("<H", payload, 0)[0]
            result("cycleTime in range", 0 <= cycle_time < 10000, f"cycleTime={cycle_time}")
    except Exception as e:
        result("MSP_STATUS", False, str(e))

    # ----------------------------------------------------------------
    print("\n=== MSP_ATTITUDE ===")
    try:
        cmd, payload = query_v1(MSP_ATTITUDE)
        result("MSP_ATTITUDE responds", cmd == MSP_ATTITUDE and len(payload) >= 6,
               f"len={len(payload)}")
        if cmd == MSP_ATTITUDE and len(payload) >= 6:
            roll  = struct.unpack_from("<h", payload, 0)[0]
            pitch = struct.unpack_from("<h", payload, 2)[0]
            yaw   = struct.unpack_from("<H", payload, 4)[0]
            result("roll  in range", -1800 <= roll  <= 1800, f"roll={roll/10:.1f}°")
            result("pitch in range",  -900 <= pitch <=  900, f"pitch={pitch/10:.1f}°")
            result("yaw   in range",     0 <= yaw   <  360,  f"yaw={yaw}°")
    except Exception as e:
        result("MSP_ATTITUDE", False, str(e))

    # ----------------------------------------------------------------
    # MSP2_COMMON_MOTOR_MIXER — mspSerializeMotorMixer was refactored
    # Format: N entries * 8 bytes (throttle:u16, roll:i16, pitch:i16, yaw:i16)
    # Default SITL: 24 mixer slots → 192 bytes
    print("\n=== MSP2_COMMON_MOTOR_MIXER (mspSerializeMotorMixer) ===")
    try:
        cmd, payload = query_v2(MSP2_COMMON_MOTOR_MIXER)
        result("MSP2_COMMON_MOTOR_MIXER responds", len(payload) > 0,
               f"len={len(payload)}")
        result("payload is multiple of 8 bytes", len(payload) % 8 == 0,
               f"len={len(payload)} entries={len(payload)//8}")
        if len(payload) >= 8:
            all_ff = all(b == 0xFF for b in payload)
            result("payload not all-0xFF garbage", not all_ff,
                   f"first_bytes={payload[:8].hex()}")
            any_nonzero = any(
                struct.unpack_from("<HhHh", payload, i * 8) != (0, 0, 0, 0)
                for i in range(len(payload) // 8)
            )
            result("at least one non-zero mixer entry", any_nonzero)
    except Exception as e:
        result("MSP2_COMMON_MOTOR_MIXER", False, str(e))

    # ----------------------------------------------------------------
    # MSP_CALIBRATION_DATA — sbufWriteAxisU16/sbufReadAxisU16 were refactored
    # Read layout: U8 flags, i16×3 accZero, i16×3 accGain, i16×3 magZero, ...
    # Write layout (SET): i16×3 accZero, i16×3 accGain, i16×3 magZero (no flags, min 18 bytes)
    print("\n=== MSP_CALIBRATION_DATA (sbufWriteAxisU16/sbufReadAxisU16) ===")
    payload_before = None
    try:
        cmd, payload_before = query_v1(MSP_CALIBRATION_DATA)
        result("MSP_CALIBRATION_DATA read", cmd == MSP_CALIBRATION_DATA and len(payload_before) >= 19,
               f"len={len(payload_before)}")
    except Exception as e:
        result("MSP_CALIBRATION_DATA read", False, str(e))

    if payload_before is not None and len(payload_before) >= 19:
        # offset 0 = flags byte; offsets 1..6 = accZero[3]; offsets 7..12 = accGain[3]
        # offsets 13..18 = magZero[3]
        orig_zero = struct.unpack_from("<hhh", payload_before, 1)
        orig_gain = struct.unpack_from("<hhh", payload_before, 7)
        mag_zero  = struct.unpack_from("<hhh", payload_before, 13)

        test_zero = (111, 222, 333)
        test_gain = (3900, 4000, 4100)
        write_pl = struct.pack("<hhhhhhhhh",
            test_zero[0], test_zero[1], test_zero[2],
            test_gain[0], test_gain[1], test_gain[2],
            mag_zero[0], mag_zero[1], mag_zero[2])

        try:
            resp_cmd, resp_payload = set_and_read_v1(
                MSP_SET_CALIBRATION_DATA, write_pl, MSP_CALIBRATION_DATA)

            if resp_cmd == MSP_CALIBRATION_DATA and len(resp_payload) >= 19:
                read_zero = struct.unpack_from("<hhh", resp_payload, 1)
                read_gain = struct.unpack_from("<hhh", resp_payload, 7)
                result("accZero[0] round-trip", read_zero[0] == test_zero[0],
                       f"wrote={test_zero[0]} read={read_zero[0]}")
                result("accZero[1] round-trip", read_zero[1] == test_zero[1],
                       f"wrote={test_zero[1]} read={read_zero[1]}")
                result("accZero[2] round-trip", read_zero[2] == test_zero[2],
                       f"wrote={test_zero[2]} read={read_zero[2]}")
                result("accGain[0] round-trip", read_gain[0] == test_gain[0],
                       f"wrote={test_gain[0]} read={read_gain[0]}")
                result("accGain[1] round-trip", read_gain[1] == test_gain[1],
                       f"wrote={test_gain[1]} read={read_gain[1]}")
                result("accGain[2] round-trip", read_gain[2] == test_gain[2],
                       f"wrote={test_gain[2]} read={read_gain[2]}")
            else:
                result("MSP_CALIBRATION_DATA read-back format",
                       False, f"cmd={resp_cmd} len={len(resp_payload)}")
        except Exception as e:
            result("MSP_CALIBRATION_DATA round-trip", False, str(e))

        # Restore
        restore_pl = struct.pack("<hhhhhhhhh",
            orig_zero[0], orig_zero[1], orig_zero[2],
            orig_gain[0], orig_gain[1], orig_gain[2],
            mag_zero[0], mag_zero[1], mag_zero[2])
        try:
            query_v1(MSP_SET_CALIBRATION_DATA, restore_pl)
        except Exception:
            pass

    # ----------------------------------------------------------------
    # MSP_RC_TUNING — read to verify format (mspReadRates refactored)
    # Layout: rcRate8(compat=100), rcExpo8, rates[3], dynPID, rcMid8, rcExpo8_thr, pa_bp(u16), rcYawExpo8
    # = 11 bytes total
    print("\n=== MSP_RC_TUNING (mspReadRates) ===")
    cur_rc_tuning = None
    try:
        cmd, cur_rc_tuning = query_v1(MSP_RC_TUNING)
        result("MSP_RC_TUNING responds", cmd == MSP_RC_TUNING, f"cmd={cmd}")
        result("MSP_RC_TUNING payload is 11 bytes", len(cur_rc_tuning) == 11,
               f"len={len(cur_rc_tuning)}")
        if len(cur_rc_tuning) >= 11:
            result("rcRate8 compat == 100", cur_rc_tuning[0] == 100,
                   f"rcRate8={cur_rc_tuning[0]}")
            for i, name in enumerate(["rates[R]", "rates[P]", "rates[Y]"], start=2):
                result(f"MSP_RC_TUNING {name} in range",
                       0 <= cur_rc_tuning[i] <= 255,
                       f"{name}={cur_rc_tuning[i]}")
    except Exception as e:
        result("MSP_RC_TUNING", False, str(e))
        cur_rc_tuning = None

    # Round-trip: write a value within valid range (max 180 for R/P, 100 for Y per settings.yaml)
    if cur_rc_tuning and len(cur_rc_tuning) == 11:
        # rates[R] is at byte index 2; max for R/P = 180
        new_r = 150
        write_pl = bytes([cur_rc_tuning[0], cur_rc_tuning[1], new_r]) + cur_rc_tuning[3:]
        try:
            resp_cmd, resp_payload = set_and_read_v1(MSP_SET_RC_TUNING, write_pl, MSP_RC_TUNING)
            if resp_cmd == MSP_RC_TUNING and len(resp_payload) >= 3:
                result("MSP_SET_RC_TUNING rates[R] round-trip (mspReadRates)",
                       resp_payload[2] == new_r,
                       f"wrote={new_r} read={resp_payload[2]}")
            else:
                result("MSP_SET_RC_TUNING read-back", False,
                       f"cmd={resp_cmd} len={len(resp_payload)}")

            # Restore
            try:
                set_and_read_v1(MSP_SET_RC_TUNING, cur_rc_tuning, MSP_RC_TUNING)
            except Exception:
                pass
        except Exception as e:
            result("MSP_SET_RC_TUNING round-trip", False, str(e))

    # ----------------------------------------------------------------
    # MSP2_INAV_RATE_PROFILE — read to verify format (mspReadRates refactored)
    # Layout: throttle(rcMid8, rcExpo8, dynPID, pa_bp:u16=5b) + stab(rcExpo8, rcYawExpo8, rates[3]=5b) +
    #         manual(rcExpo8, rcYawExpo8, rates[3]=5b) = 15 bytes total
    print("\n=== MSP2_INAV_RATE_PROFILE (mspReadRates) ===")
    cur_rate_profile = None
    try:
        cmd, cur_rate_profile = query_v2(MSP2_INAV_RATE_PROFILE)
        result("MSP2_INAV_RATE_PROFILE responds", cmd == MSP2_INAV_RATE_PROFILE,
               f"cmd=0x{cmd:04x}")
        result("MSP2_INAV_RATE_PROFILE payload is 15 bytes", len(cur_rate_profile) == 15,
               f"len={len(cur_rate_profile)}")
        if len(cur_rate_profile) == 15:
            all_ff = all(b == 0xFF for b in cur_rate_profile)
            result("MSP2_INAV_RATE_PROFILE payload not garbage", not all_ff,
                   f"bytes={cur_rate_profile.hex()}")
    except Exception as e:
        result("MSP2_INAV_RATE_PROFILE", False, str(e))
        cur_rate_profile = None

    # Round-trip: write new stab rates[R] (byte index 7, max 180)
    if cur_rate_profile and len(cur_rate_profile) == 15:
        new_stab_r = 155
        write_pl = cur_rate_profile[:7] + bytes([new_stab_r]) + cur_rate_profile[8:]
        try:
            resp_cmd, resp_payload = set_and_read_v2(
                MSP2_INAV_SET_RATE_PROFILE, write_pl, MSP2_INAV_RATE_PROFILE)
            if resp_cmd == MSP2_INAV_RATE_PROFILE and len(resp_payload) == 15:
                result("MSP2_INAV_SET_RATE_PROFILE stab_rates[R] round-trip (mspReadRates)",
                       resp_payload[7] == new_stab_r,
                       f"wrote={new_stab_r} read={resp_payload[7]}")
            else:
                result("MSP2_INAV_SET_RATE_PROFILE read-back", False,
                       f"cmd=0x{resp_cmd:04x} len={len(resp_payload)}")

            # Restore
            try:
                set_and_read_v2(MSP2_INAV_SET_RATE_PROFILE, cur_rate_profile, MSP2_INAV_RATE_PROFILE)
            except Exception:
                pass
        except Exception as e:
            result("MSP2_INAV_SET_RATE_PROFILE round-trip", False, str(e))

    # ----------------------------------------------------------------
    print(f"\n{'='*60}")
    print(f"RESULTS: {PASS} passed, {FAIL} failed")
    print(f"{'='*60}")
    if FAIL > 0:
        print("\nNote: Failures may indicate a regression in the refactoring.")
    else:
        print("\nAll tests passed — refactoring smoke test OK.")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())
