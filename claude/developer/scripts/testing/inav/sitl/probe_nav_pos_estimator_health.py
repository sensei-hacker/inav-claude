#!/usr/bin/env python3
"""
Diagnostic probe for INAV's navigation position estimator health on SITL,
using ONLY existing MSP surface (no firmware source changes required).

WHY THIS EXISTS
----------------
Any test that needs a GPS-based nav mode (BOXNAVWP / BOXNAVRTH /
BOXNAVPOSHOLD) to actually engage requires navigationPositionEstimateIsHealthy()
(src/main/navigation/navigation.c) to become true:
    posControl.flags.estPosStatus >= EST_USABLE
    && posControl.flags.estAltStatus >= EST_USABLE
    && STATE(GPS_FIX_HOME)
...and GPS_FIX_HOME only latches once, while DISARMED, the first time
estPosStatus reaches EST_USABLE. If the position estimator never converges,
arming with a nav-capable BOX mode configured hangs forever with
ARMING_DISABLED_SENSORS_CALIBRATING | ARMING_DISABLED_NAVIGATION_UNSAFE,
even while feeding a perfectly valid MSP_SET_RAW_GPS fix -- and this can
happen for reasons that have NOTHING to do with GPS at all (see below).

This script polls two things every 0.5s so you can see exactly what's
stuck, without needing to add temporary firmware instrumentation:
  - MSP2_INAV_STATUS (0x2000): live arming-disable flags, decoded by name.
  - MSP2_INAV_DEBUG (0x2019) with debug_mode=POS_EST (20): slot 7 already
    packs posEstimator.flags (EST_GPS_XY_VALID/EST_GPS_Z_VALID/EST_BARO_VALID/
    EST_XY_VALID/EST_Z_VALID) plus eph/epv (clamped to 0-1000 by the
    firmware's own DEBUG_SET call) -- see navigation_pos_estimator.c
    publishEstimatedTopic(). This exists in mainline already; no rebuild
    needed.

KNOWN GOTCHA THIS SCRIPT WAS BUILT TO DIAGNOSE (2026-09-21)
------------------------------------------------------------
gyroUpdate() (src/main/sensors/gyro.c) permanently no-ops for as long as
ARMING_FLAG(SIMULATOR_MODE_HITL) is set -- it assumes the caller will feed
gyro samples itself via the FULL MSP_SIMULATOR sensor payload
(readMspSimulatorValues()). If you use the "minimal" HITL pattern (send
ONE MSP_SIMULATOR frame with just HITL_ENABLE, no sensor bytes, to bypass
sensor calibration -- see sitl_arm_test.py) and you enable it before gyro
calibration (a fixed 2000ms window, CALIBRATING_GYRO_TIME_MS, from
gyro-driver init) has finished, gyroIsCalibrationComplete() can NEVER
become true afterward. That freezes isImuReady() (flight/imu.c) at false
forever, which makes updateEstimatedTopic() early-return with
posEstimator.flags=0 and eph/epv pinned at the invalid ceiling FOREVER --
so the whole GPS position estimator chain above is permanently blocked,
with NO error message pointing at gyro calibration at all (CLI `status`
just says "WAITING FOR GPS FIX").

Plain (non-nav) arming is NOT affected and misleadingly looks fine: the
top-level ARMING_DISABLED_SENSORS_CALIBRATING flag is cleared by
areSensorsCalibrating() (fc_core.c), which checks baro/mag/pitot/acc
calibration but never checks gyroIsCalibrationComplete() at all.

FIX: wait comfortably longer than CALIBRATING_GYRO_TIME_MS (2000ms) after
a post-reboot reconnect, and BEFORE sending the MSP_SIMULATOR HITL-enable
frame. See --hitl-delay below (default 3.0s, known-good).

USAGE
-----
    python3 probe_nav_pos_estimator_health.py [--port 5760] [--hitl-delay 3.0]
                                               [--duration 30] [--no-hitl]

Provisions a minimal AIRPLANE + MSP-RX + GPS-feature setup with all three
nav-capable BOX mode ranges configured (matching
test_fw_wp_turn_mode_gate.py's provision()), reboots, waits --hitl-delay
seconds, enables minimal HITL, then feeds RC+GPS continuously while
printing arming flags and pos-estimator health every 0.5s for --duration
seconds. Use --hitl-delay 0 to reproduce the frozen-forever bug on demand
(useful for regression-checking this exact failure mode).

Note: if running in a sandbox, localhost TCP ports are normally
allowlisted for SITL; if connection is still blocked, ask the user rather
than disabling the sandbox.
"""
from __future__ import annotations

import argparse
import socket
import struct
import sys
import threading
import time

MSP_API_VERSION = 1
MSP_RX_CONFIG = 44
MSP_SET_RX_CONFIG = 45
MSP_SET_RAW_RC = 200
MSP_SET_RAW_GPS = 201
MSP_EEPROM_WRITE = 250
MSP_REBOOT = 68
MSP_FEATURE = 36
MSP_SET_FEATURE = 37
MSP_SET_MODE_RANGE = 35
MSP_SIMULATOR = 0x201F
MSP2_INAV_STATUS = 0x2000
MSP2_INAV_DEBUG = 0x2019
MSP2_COMMON_SET_SETTING = 0x1004

RX_TYPE_MSP = 2
FEATURE_GPS = 1 << 7
HITL_ENABLE = 1 << 0
DEBUG_MODE_POS_EST = 20  # index into debug_modes settings.yaml list

PERM_ARM, PERM_ANGLE, PERM_NAV_RTH, PERM_NAV_POSHOLD, PERM_NAV_WP = 0, 1, 10, 11, 28
RC_LOW, RC_MID, RC_HIGH = 1000, 1500, 2000
CH_ROLL, CH_PITCH, CH_THROTTLE, CH_YAW = 0, 1, 2, 3
CH_ARM, CH_ANGLE, CH_WP, CH_AUX4 = 4, 5, 6, 7

LAT0, LON0 = 47.0, 8.5
MISSION_ALT_CM = 5000
MISSION_ALT_M = MISSION_ALT_CM // 100  # MSP_SET_RAW_GPS altitude field is METERS, not cm

# navPositionEstimationFlags_e (navigation_pos_estimator_private.h)
EST_GPS_XY_VALID = 1 << 0
EST_GPS_Z_VALID = 1 << 1
EST_BARO_VALID = 1 << 2
EST_FLOW_VALID = 1 << 4
EST_XY_VALID = 1 << 5
EST_Z_VALID = 1 << 6

ARMING_FLAG_NAMES = [
    (6, "GEOZONE"), (7, "FAILSAFE_SYS"), (8, "NOT_LEVEL"), (9, "SENSORS_CALIB"),
    (10, "SYS_OVERLOAD"), (11, "NAV_UNSAFE"), (12, "COMPASS_UNCAL"),
    (13, "ACC_UNCAL"), (14, "ARM_SWITCH"), (15, "HW_FAIL"), (16, "BOXFAILSAFE"),
    (18, "RC_LINK"), (19, "THROTTLE"), (20, "CLI"),
]


def crc8_dvb_s2(data: bytes, crc: int = 0) -> int:
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


class MspClient:
    def __init__(self, host="127.0.0.1", port=5760, timeout=3.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._rx = b""
        self._lock = threading.Lock()

    def close(self):
        self.sock.close()

    def send(self, cmd, payload=b""):
        body = struct.pack("<BHH", 0, cmd, len(payload)) + payload
        self.sock.sendall(b"$X<" + body + bytes([crc8_dvb_s2(body)]))

    def _read_exact(self, n):
        while len(self._rx) < n:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("SITL closed connection")
            self._rx += chunk
        out, self._rx = self._rx[:n], self._rx[n:]
        return out

    def recv(self):
        while True:
            if self._read_exact(1) != b"$":
                continue
            if self._read_exact(1) != b"X":
                continue
            direction = self._read_exact(1)
            hdr = self._read_exact(5)
            _flag, cmd, size = struct.unpack("<BHH", hdr)
            payload = self._read_exact(size)
            crc = self._read_exact(1)[0]
            if crc8_dvb_s2(hdr + payload) != crc:
                raise IOError(f"MSP CRC mismatch on cmd {cmd}")
            return cmd, payload, direction == b"!"

    def request(self, cmd, payload=b"", retries=3):
        with self._lock:
            for _ in range(retries):
                self.send(cmd, payload)
                rcmd, rpayload, err = self.recv()
                if rcmd == cmd:
                    if err:
                        raise IOError(f"MSP error reply for cmd 0x{cmd:X}")
                    return rpayload
            raise IOError(f"no matching reply for cmd 0x{cmd:X}")

    def api_version(self):
        p = self.request(MSP_API_VERSION)
        return p[0], p[1], p[2]

    def set_setting(self, name, raw_value):
        self.request(MSP2_COMMON_SET_SETTING, name.encode() + b"\x00" + raw_value)

    def set_mode_range(self, index, box_permanent_id, aux_channel, start_pwm, end_pwm):
        payload = struct.pack("<BBBBB", index, box_permanent_id, aux_channel,
                               (start_pwm - 900) // 25, (end_pwm - 900) // 25)
        self.request(MSP_SET_MODE_RANGE, payload)

    def enable_feature(self, bit):
        mask = struct.unpack("<I", self.request(MSP_FEATURE))[0]
        self.request(MSP_SET_FEATURE, struct.pack("<I", mask | bit))

    def save_eeprom(self):
        self.request(MSP_EEPROM_WRITE)

    def set_rx_type_msp(self):
        data = list(self.request(MSP_RX_CONFIG))
        data[23] = RX_TYPE_MSP
        self.request(MSP_SET_RX_CONFIG, bytes(data[:24]))

    def enable_hitl_minimal(self):
        """Matches sitl_arm_test.py's proven pattern: version=2,
        flags=HITL_ENABLE only, no sensor payload. Bypasses sensor
        calibration gates using SITL's own static fake readings -- but see
        module docstring: this permanently freezes gyroUpdate() from this
        point on, so gyro calibration must already be complete."""
        self.request(MSP_SIMULATOR, struct.pack("<BH", 2, HITL_ENABLE))

    def send_rc(self, channels):
        data = b"".join(struct.pack("<H", c) for c in channels)
        self.request(MSP_SET_RAW_RC, data)

    def send_gps(self, lat_e7, lon_e7, alt_m, speed_cms, fix=2, sats=12):
        # MSP_SET_RAW_GPS altitude field is METERS (u16); firmware does
        # `gpsSol.llh.alt = 100 * sbufReadU16(src)` to convert to cm itself.
        payload = struct.pack("<BBiiHH", fix, sats, lat_e7, lon_e7, alt_m, speed_cms)
        self.request(MSP_SET_RAW_GPS, payload)

    def arming_flags(self):
        p = self.request(MSP2_INAV_STATUS)
        return struct.unpack_from("<I", p, 9)[0]

    def pos_est_debug(self):
        """Requires debug_mode=POS_EST (set via provision()). Returns the
        posEstimator.flags/eph/epv already packed by the firmware's own
        DEBUG_SET(DEBUG_POS_EST, 7, ...) call -- no firmware change needed."""
        p = self.request(MSP2_INAV_DEBUG)
        vals = struct.unpack_from("<8i", p, 0)
        slot7 = vals[7]
        flags = (slot7 >> 20) & 0x7F
        eph = (slot7 >> 10) & 0x3FF
        epv = slot7 & 0x3FF
        return dict(flags=flags, eph=eph, epv=epv, raw=vals)


def check_connection(port=5760):
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=3.0)
        s.close()
    except OSError as e:
        print(f"XXXX FAILED to connect to SITL on tcp:127.0.0.1:{port}: {e}")
        print("    Check: is SITL.elf running? (build_sitl/bin/SITL.elf)")
        print("    Note: if running in a sandbox, localhost ports are normally")
        print("    allowlisted; if still blocked, ask the user rather than")
        print("    disabling the sandbox.")
        sys.exit(1)
    print("OK: TCP connection to SITL verified")


def connect_with_retry(timeout=15.0):
    t_end = time.monotonic() + timeout
    last = None
    while time.monotonic() < t_end:
        try:
            c = MspClient()
            c.api_version()
            return c
        except (ConnectionRefusedError, ConnectionError, OSError, IOError) as e:
            last = e
            time.sleep(0.3)
    raise TimeoutError(f"SITL did not come back up within {timeout}s: {last}")


def flags_str(f):
    names = [name for bit, name in ARMING_FLAG_NAMES if f & (1 << bit)]
    return "|".join(names) if names else "(none)"


def pos_est_flags_str(fl):
    names = []
    if fl & EST_GPS_XY_VALID:
        names.append("GPS_XY")
    if fl & EST_GPS_Z_VALID:
        names.append("GPS_Z")
    if fl & EST_BARO_VALID:
        names.append("BARO")
    if fl & EST_FLOW_VALID:
        names.append("FLOW")
    if fl & EST_XY_VALID:
        names.append("XY_VALID")
    if fl & EST_Z_VALID:
        names.append("Z_VALID")
    return ",".join(names) if names else "none"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=5760, help="SITL MSP TCP port (default 5760)")
    ap.add_argument("--hitl-delay", type=float, default=3.0,
                     help="Seconds to wait after post-reboot reconnect before enabling HITL "
                          "(default 3.0, safely > CALIBRATING_GYRO_TIME_MS=2000ms; use 0 to "
                          "reproduce the frozen-isImuReady bug on demand)")
    ap.add_argument("--duration", type=float, default=30.0, help="Seconds to poll and print (default 30)")
    args = ap.parse_args()

    check_connection(args.port)
    msp = MspClient(port=args.port)
    print(f"API version: {msp.api_version()}")
    msp.set_setting("platform_type", struct.pack("<B", 1))  # AIRPLANE
    msp.set_setting("small_angle", struct.pack("<B", 180))
    msp.set_rx_type_msp()
    msp.enable_feature(FEATURE_GPS)
    msp.set_setting("gps_provider", struct.pack("<B", 1))  # MSP
    msp.set_setting("nav_wp_radius", struct.pack("<H", 3000))
    msp.set_setting("nav_wp_max_safe_distance", struct.pack("<H", 0))
    msp.set_setting("nav_fw_wp_turn_mode", struct.pack("<B", 0))
    msp.set_setting("debug_mode", struct.pack("<B", DEBUG_MODE_POS_EST))

    msp.set_mode_range(0, PERM_ARM, CH_ARM - 4, 1700, 2100)
    msp.set_mode_range(1, PERM_ANGLE, CH_ANGLE - 4, 1700, 2100)
    msp.set_mode_range(2, PERM_NAV_WP, CH_WP - 4, 1700, 2100)
    msp.set_mode_range(3, PERM_NAV_RTH, CH_AUX4 - 4, 1300, 1700)
    msp.set_mode_range(4, PERM_NAV_POSHOLD, CH_AUX4 - 4, 1700, 2100)

    msp.save_eeprom()
    try:
        msp.request(MSP_REBOOT)
    except (IOError, ConnectionError, OSError):
        pass
    print("OK: provisioned, rebooting")
    msp.close()

    msp = connect_with_retry()
    print("OK: reconnected after reboot")
    if args.hitl_delay > 0:
        print(f"  waiting {args.hitl_delay:.1f}s for natural (pre-HITL) gyro calibration to complete...")
        time.sleep(args.hitl_delay)
    else:
        print("  --hitl-delay 0: enabling HITL immediately (reproduces the frozen-isImuReady bug)")
    msp.enable_hitl_minimal()

    rc = [RC_MID] * 8
    rc[CH_THROTTLE] = RC_LOW
    rc[CH_ARM] = RC_LOW
    rc[CH_ANGLE] = RC_LOW
    rc[CH_WP] = RC_LOW
    rc[CH_AUX4] = RC_LOW

    running = True

    def feeder():
        lat_e7 = int(round(LAT0 * 1e7))
        lon_e7 = int(round(LON0 * 1e7))
        while running:
            try:
                msp.send_rc(rc)
                msp.send_gps(lat_e7, lon_e7, MISSION_ALT_M, 0)
            except (IOError, ConnectionError, OSError) as e:
                print(f"  [feeder] send failed: {e}")
            time.sleep(0.02)

    feeder_thread = threading.Thread(target=feeder, daemon=True)
    feeder_thread.start()

    print(f"{'t':>6s}  {'armflags':>10s} {'blocked_by':<30s} {'posestflags':>28s} {'eph':>5s} {'epv':>5s}")
    t0 = time.monotonic()
    try:
        while time.monotonic() - t0 < args.duration:
            time.sleep(0.5)
            elapsed = time.monotonic() - t0
            af = msp.arming_flags()
            pe = msp.pos_est_debug()
            fl = pe["flags"]
            print(f"{elapsed:6.1f}  0x{af:08X} {flags_str(af):<30s} "
                  f"0x{fl:02X}({pos_est_flags_str(fl)}){'':<8s} {pe['eph']:5d} {pe['epv']:5d}")
    finally:
        running = False
        feeder_thread.join(timeout=1.0)
        msp.close()


if __name__ == "__main__":
    main()
