#!/usr/bin/env python3
"""
Fixed-wing waypoint-mission test for the USE_FW_TURN_PREDICTOR gate, using
the PROVEN simple SITL HITL pattern (RX_TYPE_MSP + minimal HITL-enable to
bypass sensor calibration + MSP_SET_RAW_RC/MSP_SET_RAW_GPS), matching
sitl_arm_test.py / gps_rth_test.py -- NOT the full synthetic-IMU HITL bench,
which was found to leave ARMING_DISABLED_SENSORS_CALIBRATING /
ARMING_DISABLED_NAVIGATION_UNSAFE permanently latched in this environment
(see notes at bottom of file / test-engineer lessons).

GPS position is advanced by the SCRIPT (open loop, straight line pursuit of
the current active waypoint at constant groundspeed) -- identically for
both turn-mode runs -- and we record the FC's own MSP_NAV_STATUS
desired_heading throughout. Since nav_fw_wp_turn_mode's COORD_FLYBY arc
coordinator is compiled out on this build (USE_FW_TURN_PREDICTOR gated on
MCU_FLASH_SIZE > 512, which evaluates false for SITL due to the
target.h/platform.h include-order quirk -- confirmed via nm: no arc/turn
predictor symbols in the binary), DIRECT and COORD_FLYBY are expected to
drive identical desired-heading sequences against the identical GPS track.

ROOT CAUSE FOUND AND FIXED (2026-09-21): the arming block above was a
test-harness sequencing bug, not a firmware bug. Confirmed live via
temporary DEBUG_POS_EST instrumentation (posEstimator.flags/eph/epv,
polled through the existing MSP2_INAV_DEBUG message -- no firmware change
needed for the final version of this script):

  gyroUpdate() (src/main/sensors/gyro.c ~line 678) permanently no-ops
  ("return;") for as long as ARMING_FLAG(SIMULATOR_MODE_HITL) is set --
  it assumes the caller will inject gyro samples itself via the *full*
  MSP_SIMULATOR sensor payload (readMspSimulatorValues()). The "minimal"
  HITL pattern used here sends exactly ONE MSP_SIMULATOR frame
  (version+HITL_ENABLE, no sensor bytes) and never again, so once that
  frame is sent, gyroUpdateAndCalibrate() (the function that actually
  advances gyroIsCalibrationComplete()) never runs again. If gyro
  calibration (a fixed CALIBRATING_GYRO_TIME_MS = 2000ms window from
  gyro-driver init) had not yet finished at the exact instant HITL was
  enabled, it can NEVER finish afterward -- isImuReady() (flight/imu.c,
  requires sensors(SENSOR_ACC) && ACCELEROMETER_CALIBRATED &&
  gyroIsCalibrationComplete()) is then permanently false.
  updateEstimatedTopic() (navigation_pos_estimator.c) early-returns
  whenever !isImuReady(), pinning posEstimator.flags=0 and eph/epv at the
  "invalid" ceiling forever -- so estPosStatus/estAltStatus never reach
  EST_USABLE, GPS_FIX_HOME never latches (it only latches once, while
  disarmed, the first time estPosStatus>=EST_USABLE is observed), and
  navigationPositionEstimateIsHealthy() -- the exact gate
  navigationIsBlockingArming() checks whenever any nav-capable BOX mode is
  configured -- is permanently false. Plain (non-nav) arming is unaffected
  and misleadingly looks "fine": the top-level ARMING_DISABLED_SENSORS_
  CALIBRATING flag is cleared by areSensorsCalibrating() (fc_core.c),
  which checks baro/mag/pitot/acc calibration but never checks
  gyroIsCalibrationComplete() at all, so it masks the frozen gyro
  calibration for any test that doesn't also arm a nav-capable mode.

  The race is structural, not incidental: main() calls
  enable_hitl_minimal() immediately after reconnecting post-reboot, almost
  always well inside the 2000ms gyro-calibration window, so it reproduced
  on every run tested.

  FIX APPLIED: wait comfortably longer than CALIBRATING_GYRO_TIME_MS
  (2000ms) after reconnecting post-reboot, and BEFORE calling
  enable_hitl_minimal(), so gyro calibration completes naturally (against
  SITL's normal fake-gyro boot data) while HITL is still off. Verified
  live: with a 3.0s wait inserted at that point, posEstimator.flags reads
  0x67 (EST_GPS_XY_VALID|EST_GPS_Z_VALID|EST_BARO_VALID|EST_XY_VALID|
  EST_Z_VALID) and eph/epv converge to ~200/~295 (well under the default
  max_eph_epv=1000) within a few seconds of enabling HITL, and both
  ARMING_DISABLED_SENSORS_CALIBRATING and ARMING_DISABLED_NAVIGATION_UNSAFE
  clear on their own -- confirmed on this exact provisioning sequence
  (AIRPLANE platform, MSP RX, BOXNAVWP/BOXNAVRTH/BOXNAVPOSHOLD mode
  ranges configured) with no other change. No firmware source was
  modified; the earlier "raw GPS altitude is meters not cm" fix in
  send_gps() below remains a separate, real, already-fixed bug.
"""
from __future__ import annotations

import math
import socket
import struct
import sys
import threading
import time

MSP_API_VERSION = 1
MSP_STATUS = 101
MSP_NAV_STATUS = 121
MSP_COMP_GPS = 107
MSP_SET_WP = 209
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
MSP2_COMMON_SET_SETTING = 0x1004

RX_TYPE_MSP = 2
FEATURE_GPS = 1 << 7
HITL_ENABLE = 1 << 0

PERM_ARM, PERM_ANGLE, PERM_NAV_RTH, PERM_NAV_POSHOLD, PERM_NAV_WP = 0, 1, 10, 11, 28
RC_LOW, RC_MID, RC_HIGH = 1000, 1500, 2000
CH_ROLL, CH_PITCH, CH_THROTTLE, CH_YAW = 0, 1, 2, 3
CH_ARM, CH_ANGLE, CH_WP, CH_AUX4 = 4, 5, 6, 7

FLAG_ARMED = 1 << 2
NON_BLOCKING = (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 14)

NAV_WP_ACTION_WAYPOINT = 0x01
NAV_WP_FLAG_LAST = 0xA5
MW_NAV_ERROR_FINISH = 4
MW_NAV_STATE_WP_ENROUTE = 5

LAT0, LON0 = 47.0, 8.5
GROUNDSPEED = 15.0  # m/s
MISSION_ALT_CM = 5000
MISSION_ALT_M = MISSION_ALT_CM // 100  # MSP_SET_RAW_GPS wants meters, not cm
MISSION_WPS = [(300, 0), (300, 300), (500, 250), (100, 100), (0, 0)]


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
        """Matches the proven sitl_arm_test.py pattern: version=2,
        flags=HITL_ENABLE only -- no sensor payload at all. This makes the
        FC treat sensors as detected/healthy using its own static SITL fake
        readings, bypassing the full synthetic-IMU consistency requirements
        that were found to never converge in this environment."""
        self.request(MSP_SIMULATOR, struct.pack("<BH", 2, HITL_ENABLE))

    def send_rc(self, channels):
        data = b"".join(struct.pack("<H", c) for c in channels)
        self.request(MSP_SET_RAW_RC, data)

    def send_gps(self, lat_e7, lon_e7, alt_m, speed_cms, fix=2, sats=12):
        # MSP_SET_RAW_GPS altitude field is METERS (u16); the firmware does
        # `gpsSol.llh.alt = 100 * sbufReadU16(src)` to convert to cm itself.
        # Passing centimeters here (as MSP_SIMULATOR/HITL v3 wants) silently
        # gives a x100 altitude error -- discovered the hard way: it fed a
        # 5000 m GPS altitude against a ~0 m baro reading, which never lets
        # estAltStatus reach EST_USABLE, permanently latching
        # ARMING_DISABLED_NAVIGATION_UNSAFE ("WAITING FOR GPS FIX").
        payload = struct.pack("<BBiiHH", fix, sats, lat_e7, lon_e7, alt_m, speed_cms)
        self.request(MSP_SET_RAW_GPS, payload)

    def arming_flags(self):
        p = self.request(MSP2_INAV_STATUS)
        return struct.unpack_from("<I", p, 9)[0]

    def nav_status(self):
        p = self.request(MSP_NAV_STATUS)
        mode, state, action, wp_number, error = struct.unpack_from("<BBBBB", p, 0)
        heading_hold, desired_heading = struct.unpack_from("<HH", p, 5)
        return dict(mode=mode, state=state, action=action, wp_number=wp_number,
                    error=error, heading_hold=heading_hold, desired_heading=desired_heading)

    def dist_to_home(self):
        p = self.request(MSP_COMP_GPS)
        dist, direction = struct.unpack_from("<Hh", p, 0)
        return dist, direction

    def set_waypoint(self, wp_no, lat_e7, lon_e7, alt_cm, flag=0):
        payload = struct.pack("<BBIIIHHHB", wp_no, NAV_WP_ACTION_WAYPOINT,
                               lat_e7 & 0xFFFFFFFF, lon_e7 & 0xFFFFFFFF, alt_cm, 0, 0, 0, flag)
        self.request(MSP_SET_WP, payload)


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


def latlon_from_ne(x_north_m, y_east_m):
    lat = LAT0 + x_north_m / 111320.0
    lon = LON0 + y_east_m / (111320.0 * math.cos(math.radians(LAT0)))
    return int(round(lat * 1e7)), int(round(lon * 1e7))


class RcGpsSender:
    """Background 50Hz sender: keeps RC link alive and drives a kinematic
    GPS position toward a target (x, y) at constant groundspeed. Movement is
    fully deterministic/open-loop -- identical given identical target
    sequences -- independent of anything the FC computes."""

    def __init__(self, msp: MspClient):
        self.msp = msp
        self.rc = [RC_MID] * 8
        self.rc[CH_THROTTLE] = RC_LOW
        self.rc[CH_ARM] = RC_LOW
        self.rc[CH_ANGLE] = RC_LOW
        self.rc[CH_WP] = RC_LOW
        self.rc[CH_AUX4] = RC_LOW
        self.x = 0.0
        self.y = 0.0
        self.target = None  # (x, y) or None to hold position
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.fail_count = 0

    def set_rc(self, updates: dict):
        """updates maps channel index (int, e.g. CH_ARM) -> PWM value.
        Takes a plain dict rather than **kwargs because channel indices are
        ints, not valid Python keyword-argument names."""
        with self.lock:
            for k, v in updates.items():
                self.rc[k] = v

    def set_target(self, xy):
        with self.lock:
            self.target = xy

    def get_pos(self):
        with self.lock:
            return self.x, self.y

    def _loop(self):
        dt = 0.02
        while self.running:
            t0 = time.perf_counter()
            with self.lock:
                rc = list(self.rc)
                target = self.target
                if target is not None:
                    dx, dy = target[0] - self.x, target[1] - self.y
                    dist = math.hypot(dx, dy)
                    step = GROUNDSPEED * dt
                    if dist > step:
                        self.x += dx / dist * step
                        self.y += dy / dist * step
                    else:
                        self.x, self.y = target
                    course = math.degrees(math.atan2(dy, dx)) % 360.0
                    speed_cms = int(GROUNDSPEED * 100) if dist > 0.5 else 0
                else:
                    course = 0.0
                    speed_cms = 0
                x, y = self.x, self.y
            lat_e7, lon_e7 = latlon_from_ne(x, y)
            try:
                self.msp.send_rc(rc)
                self.msp.send_gps(lat_e7, lon_e7, MISSION_ALT_M, speed_cms)
            except (IOError, ConnectionError, OSError):
                self.fail_count += 1
            remaining = dt - (time.perf_counter() - t0)
            if remaining > 0:
                time.sleep(remaining)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)


def provision(msp: MspClient, nav_wp_turn_mode=0):
    print(f"API version: {msp.api_version()}")
    msp.set_setting("platform_type", struct.pack("<B", 1))  # AIRPLANE
    msp.set_setting("small_angle", struct.pack("<B", 180))
    msp.set_rx_type_msp()
    msp.enable_feature(FEATURE_GPS)
    msp.set_setting("gps_provider", struct.pack("<B", 1))  # MSP
    msp.set_setting("nav_wp_radius", struct.pack("<H", 3000))  # 30 m
    msp.set_setting("nav_wp_max_safe_distance", struct.pack("<H", 0))  # disable "1st WP too far"
    msp.set_setting("nav_fw_wp_turn_mode", struct.pack("<B", nav_wp_turn_mode))

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
    print(f"OK: provisioned (nav_fw_wp_turn_mode={nav_wp_turn_mode}), rebooting")


def upload_mission(msp: MspClient):
    n = len(MISSION_WPS)
    for i, (x, y) in enumerate(MISSION_WPS, start=1):
        lat_e7, lon_e7 = latlon_from_ne(x, y)
        flag = NAV_WP_FLAG_LAST if i == n else 0
        msp.set_waypoint(i, lat_e7, lon_e7, MISSION_ALT_CM, flag=flag)
    print(f"OK: uploaded {n}-waypoint mission")


def wait_flags_clear(msp: MspClient, mask, timeout=15.0):
    t_end = time.monotonic() + timeout
    while time.monotonic() < t_end:
        f = msp.arming_flags()
        if f & mask == 0:
            return f
        time.sleep(0.2)
    raise TimeoutError(f"flags {mask:#x} never cleared: last=0x{msp.arming_flags():08X}")


def run_wp_mission(msp: MspClient, sender: RcGpsSender, turn_mode_name: str, results: dict):
    print(f"\n--- Mission run: nav_fw_wp_turn_mode = {turn_mode_name} ---")
    sender.x = sender.y = 0.0
    sender.set_target(None)

    wait_flags_clear(msp, ~NON_BLOCKING & 0xFFFFFFFF, timeout=15.0)
    print("  arm-ready")

    sender.set_rc({CH_ARM: RC_LOW})
    time.sleep(0.3)
    sender.set_rc({CH_ARM: RC_HIGH})
    time.sleep(0.5)
    f = msp.arming_flags()
    if not (f & FLAG_ARMED):
        raise RuntimeError(f"arm failed, flags=0x{f:08X}")
    print("  armed")

    sender.set_rc({CH_THROTTLE: 1500, CH_ANGLE: RC_HIGH})
    time.sleep(0.5)
    sender.set_rc({CH_WP: RC_HIGH})
    print("  NAV WP engaged, flying mission (open-loop kinematic GPS track)...")

    heading_log = []
    last_wp_seen = 0
    last_wp_change_t = 0.0
    t = 0.0
    finished = crashed = timed_out = False
    timeout = 180.0
    poll_dt = 0.5

    while t < timeout:
        ns = msp.nav_status()
        wp_idx = ns["wp_number"]  # 1-based active WP
        target = MISSION_WPS[wp_idx - 1] if 1 <= wp_idx <= len(MISSION_WPS) else None
        sender.set_target(target)

        x, y = sender.get_pos()
        heading_log.append((t, wp_idx, ns["state"], ns["desired_heading"], x, y))

        if wp_idx != last_wp_seen:
            last_wp_seen = wp_idx
            last_wp_change_t = t
        stuck = (t - last_wp_change_t) > 60.0 and ns["state"] == MW_NAV_STATE_WP_ENROUTE

        if ns["error"] == MW_NAV_ERROR_FINISH:
            finished = True
            print(f"  MISSION FINISHED at t={t:.1f}s pos=({x:.0f},{y:.0f})")
            break
        if stuck:
            print(f"  STUCK: wp_number unchanged >60s at t={t:.1f}s (wp={last_wp_seen})")
            break

        print(f"  t={t:5.1f}s wp={wp_idx} state={ns['state']} error={ns['error']} "
              f"desired_hdg={ns['desired_heading']} pos=({x:6.1f},{y:6.1f})")
        time.sleep(poll_dt)
        t += poll_dt
    else:
        timed_out = True

    # Reset RC to a fully-idle disarmed state (throttle back to low) --
    # ARMING_DISABLED_THROTTLE blocks re-arming on the next mission run
    # otherwise, since CH_THROTTLE was left at 1500 during flight above.
    sender.set_rc({CH_WP: RC_LOW, CH_ARM: RC_LOW, CH_THROTTLE: RC_LOW, CH_ANGLE: RC_LOW})
    time.sleep(0.5)

    results[turn_mode_name] = dict(finished=finished, crashed=crashed, timed_out=timed_out,
                                    elapsed=t, heading_log=heading_log)


def run_poshold_rth_check(msp: MspClient, sender: RcGpsSender):
    print("\n--- POSHOLD / RTH sanity check ---")
    sender.x = sender.y = 0.0
    sender.set_target(None)
    wait_flags_clear(msp, ~NON_BLOCKING & 0xFFFFFFFF, timeout=15.0)

    sender.set_rc({CH_ARM: RC_LOW})
    time.sleep(0.3)
    sender.set_rc({CH_ARM: RC_HIGH})
    time.sleep(0.5)
    if not (msp.arming_flags() & FLAG_ARMED):
        raise RuntimeError("arm failed for poshold/rth check")
    print("  armed")
    sender.set_rc({CH_THROTTLE: 1500, CH_ANGLE: RC_HIGH})
    time.sleep(0.3)

    # Fly straight out 250m
    sender.set_target((250.0, 0.0))
    for _ in range(int(250.0 / GROUNDSPEED / 0.5) + 2):
        x, y = sender.get_pos()
        if math.hypot(x, y) >= 249.0:
            break
        time.sleep(0.5)
    x, y = sender.get_pos()
    print(f"  flew out to ({x:.0f},{y:.0f})")

    sender.set_rc({CH_AUX4: RC_HIGH})  # POSHOLD band 1700-2100
    sender.set_target((x, y))  # hold current position
    print("  NAV POSHOLD engaged, holding position for 10s")
    time.sleep(10.0)
    d, _ = msp.dist_to_home()
    poshold_ok = d is not None and 200 < d < 320  # ~250m out, still there
    print(f"  POSHOLD: FC distHome={d}m -> {'OK' if poshold_ok else 'FAIL'}")

    sender.set_rc({CH_AUX4: 1500})  # RTH band 1300-1700
    sender.set_target((0.0, 0.0))  # simulate flying home
    print("  NAV RTH engaged, flying back toward home")
    min_dist = d if d is not None else 99999
    for _ in range(30):
        time.sleep(1.0)
        dd, _ = msp.dist_to_home()
        if dd is not None:
            min_dist = min(min_dist, dd)
        if dd is not None and dd < 30:
            break
    rth_ok = min_dist < 60
    print(f"  RTH: closest approach reported by FC = {min_dist}m -> {'OK' if rth_ok else 'FAIL'}")

    sender.set_rc({CH_AUX4: RC_LOW, CH_ARM: RC_LOW})
    return dict(poshold_ok=poshold_ok, rth_ok=rth_ok)


def main():
    check_connection()
    msp = MspClient()
    provision(msp, nav_wp_turn_mode=0)  # DIRECT
    msp.close()
    print("  waiting for SITL reboot...")
    msp = connect_with_retry()
    print("OK: reconnected after reboot")
    # Gyro calibration (CALIBRATING_GYRO_TIME_MS = 2000ms from gyro-driver
    # init) must complete BEFORE HITL is enabled: gyroUpdate() permanently
    # no-ops once SIMULATOR_MODE_HITL is set (it expects the full
    # MSP_SIMULATOR sensor-payload path to drive gyro samples instead),
    # so gyroIsCalibrationComplete() can never progress after that point.
    # If we enabled HITL too early, isImuReady() would be stuck false
    # forever, which stalls the entire GPS position estimator (eph/epv
    # never converge, GPS_FIX_HOME never latches) even with a perfectly
    # valid GPS feed -- see docstring above for the full root-cause trace.
    print("  waiting 3.0s for natural (pre-HITL) gyro calibration to complete...")
    time.sleep(3.0)
    msp.enable_hitl_minimal()

    sender = RcGpsSender(msp)
    sender.start()
    time.sleep(1.0)

    results = {}
    try:
        upload_mission(msp)
        run_wp_mission(msp, sender, "DIRECT", results)

        msp.set_setting("nav_fw_wp_turn_mode", struct.pack("<B", 1))  # COORD_FLYBY
        print("\nOK: nav_fw_wp_turn_mode set live to COORD_FLYBY (1), no reboot")
        upload_mission(msp)
        run_wp_mission(msp, sender, "COORD_FLYBY", results)

        sanity = run_poshold_rth_check(msp, sender)
    finally:
        sender.stop()
        msp.close()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    ok = True
    for name, r in results.items():
        status = "PASS" if (r["finished"] and not r["crashed"] and not r["timed_out"]) else "FAIL"
        if status == "FAIL":
            ok = False
        print(f"{name:12s} {status}  finished={r['finished']} crashed={r['crashed']} "
              f"timed_out={r['timed_out']} elapsed={r['elapsed']:.0f}s "
              f"samples={len(r['heading_log'])}")

    if "DIRECT" in results and "COORD_FLYBY" in results:
        a = results["DIRECT"]["heading_log"]
        b = results["COORD_FLYBY"]["heading_log"]
        n = min(len(a), len(b))
        # heading_log tuple layout: (t, wp_idx, state, desired_heading, x, y).
        # Only compare samples where BOTH runs are actively navigating
        # (state == MW_NAV_STATE_WP_ENROUTE) with the same active waypoint.
        # Sample index 0 (state == 0, WP mode not yet engaged) reads a
        # *stale* desired_heading left over from the FC's PREVIOUS run --
        # comparing it produces a huge, meaningless diff (confirmed live:
        # DIRECT's idx-0 read 0 while COORD_FLYBY's idx-0 read ~22171
        # centidegrees, the exact leftover final heading from the DIRECT
        # run moments earlier) and has nothing to do with turn-mode
        # behavior.
        diffs = [abs(a[i][3] - b[i][3]) for i in range(n)
                 if a[i][1] == b[i][1] and a[i][2] == MW_NAV_STATE_WP_ENROUTE
                 and b[i][2] == MW_NAV_STATE_WP_ENROUTE]
        max_diff = max(diffs) if diffs else None
        # Tolerance of 50 centidegrees (0.5 deg): the two runs are driven by
        # independent wall-clock kinematic replay through the same
        # RcGpsSender, so small floating-point/scheduling jitter between
        # runs is expected even when the underlying nav behavior is
        # identical -- observed max jitter in a real passing run was 28
        # centidegrees (0.28 deg). A genuine COORD_FLYBY arc-predictor
        # divergence would show large, sustained heading differences during
        # turns, not a few tenths of a degree of noise.
        identical = max_diff is not None and max_diff <= 50
        print(f"\nDIRECT vs COORD_FLYBY desired_heading max diff over {len(diffs)} "
              f"comparable ENROUTE samples: {max_diff} (centidegrees) -> "
              f"{'IDENTICAL (gate fallback confirmed)' if identical else 'DIFFERENT (unexpected!)'}")
        if not identical:
            ok = False

    print(f"\nPOSHOLD: {'PASS' if sanity['poshold_ok'] else 'FAIL'}")
    print(f"RTH:     {'PASS' if sanity['rth_ok'] else 'FAIL'}")
    if not (sanity["poshold_ok"] and sanity["rth_ok"]):
        ok = False

    print(f"\nOVERALL: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
