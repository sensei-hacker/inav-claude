#!/usr/bin/env python3
"""
Reusable library for driving a real INAV flight controller (USB VCP serial,
NOT SITL) via the MSP_SIMULATOR / SIMULATOR_MODE_HITL facility -- i.e.
"HITL on real hardware": the FC's gyro/accel/baro/GPS are entirely
overridden by injected sensor data over MSP, letting you exercise
arming/nav-mode logic on a bench FC with no props/motors/battery attached,
exactly like SITL but on the actual target firmware/hardware.

Extracted from claude/developer/workspace/investigate-fw-inflight-detection-dead-reckoning/
hw_test_launch_mode_emerg_rearm.py (issue #11644 testing), where it was
built, debugged, and verified end-to-end against a real AEDROXH7 board.
See that script for a full usage example (three test scenarios built on
top of this library), and see the "test-engineer" agent's lessons file
(.claude/agents/test-engineer.md) for the debugging story behind each of
the real-hardware quirks handled here. Summary of what this library gets
right that a naive implementation will not:

1. USE_SIMULATOR / MSP_SIMULATOR is compiled into most real targets by
   default (src/main/target/common.h), not just SITL -- check the specific
   target's target.h for an `#undef USE_SIMULATOR` before assuming a
   physical-motion-only test is required.
2. Real MSP-over-USB-serial has enough round-trip latency variance to
   produce stale/orphaned replies even in a single-threaded, one-request-
   at-a-time client. MspSerialClient.request() drains extra frames instead
   of blindly resending on a cmd mismatch -- resending is what causes an
   ever-growing backlog, not what fixes it.
3. Exactly ONE thread must ever touch the serial port. HitlSender is that
   owner: it sends MSP_SIMULATOR + MSP_SET_RAW_RC every tick and caches
   MSP2_INAV_STATUS/MSP_STATUS_EX polls a few times a second; everything
   else reads those cached values via get_arming_flags()/
   get_flight_mode_flags() instead of issuing a second concurrent request.
4. gyroIsCalibrationComplete() is a one-shot ~2000ms timer that freezes
   forever if SIMULATOR_MODE_HITL is enabled before it completes (real
   gyroUpdate() stops running once that ARMING_FLAG is set). Always wait
   >2000ms of real wall-clock time after a (re)boot, with NO HITL traffic,
   before the first MSP_SIMULATOR frame.
5. MSP_STATUS_EX/MSP2_INAV_STATUS's 4-byte "box mode flags" field is NOT
   the flightModeFlags_e enum bit numbering -- it's fc_msp_box.c's
   packBoxModeFlags() output, ordered by position in the dynamically-built
   activeBoxIds[] list (depends on platform type / features / sensors).
   To find a specific box's bit reliably, query MSP_BOXIDS (cmd 119) and
   find the index of that box's permanentId -- see
   MspSerialClient.find_box_bit().
6. On cleanup, disarm THROUGH the still-running sender and confirm ARMED
   clears before calling sender.stop() -- stopping first means nothing is
   left to transmit the "disarm" RC values you just staged, so the FC
   stays armed into whatever runs next (and e.g. MSP_EEPROM_WRITE refuses
   outright while ARMED). See safe_shutdown().

None of this needs firmware changes -- it's all standard, already-shipped
MSP surface. Safety: never point this at a FC with props, motors, ESCs, or
a battery attached; the whole point is that HITL substitutes for real
sensors, but PWM/DShot outputs are still computed and driven by whatever
flight mode logic runs, based on nothing more than injected sensor values.
"""
from __future__ import annotations

import glob
import math
import struct
import sys
import threading
import time

try:
    import serial
except ImportError:
    print("XXXX FAILED: pyserial not installed (pip install pyserial)")
    sys.exit(1)

MSP_API_VERSION = 1
MSP_STATUS_EX = 150
MSP_SET_RAW_RC = 200
MSP_RX_CONFIG = 44
MSP_SET_MODE_RANGE = 35
MSP_FEATURE = 36
MSP_SET_FEATURE = 37
MSP_EEPROM_WRITE = 250
MSP_REBOOT = 68
MSP_SIMULATOR = 0x201F
MSP2_INAV_STATUS = 0x2000
MSP2_COMMON_SET_SETTING = 0x1004
MSP_BOXIDS = 119

FEATURE_GPS = 1 << 7

# HITL flags (MSP_SIMULATOR, fc_msp.c / runtime_config.h)
HITL_ENABLE = 1 << 0
HITL_HAS_NEW_GPS_DATA = 1 << 4

SIMULATOR_MSP_VERSION = 2

PERM_ARM, PERM_NAV_LAUNCH = 0, 36
RC_LOW, RC_MID, RC_HIGH = 1000, 1500, 2000
CH_ROLL, CH_PITCH, CH_THROTTLE, CH_YAW = 0, 1, 2, 3
CH_ARM, CH_LAUNCH = 4, 5

FLAG_ARMED = 1 << 2
GRAVITY_MG = 1000  # 1G in the packet's milli-g units

# IMPORTANT (real-hardware lesson -- this bit position is NOT a fixed
# flightModeFlags_e constant): MSP_STATUS_EX / MSP2_INAV_STATUS's 4-byte
# "box mode flags" field is built by fc_msp_box.c's packBoxModeFlags(),
# which packs bits in activeBoxIds[] order -- a dynamically built list that
# depends on the current config (platform type, enabled features/sensors).
# It is NOT the same bit numbering as the flightModeFlags_e enum in
# runtime_config.h (NAV_LAUNCH_MODE == 1<<7 there is a DIFFERENT, unrelated
# number space). serializeBoxReply() (MSP_BOXIDS) iterates that exact same
# activeBoxIds[] array in the exact same order, writing each box's
# permanentId -- so the correct way to find "which bit is NAV_LAUNCH for
# THIS boot" is to request MSP_BOXIDS and find the index of permanentId 36
# (PERM_NAV_LAUNCH) in the returned byte list. That index can change across
# reboots/configs (e.g. it shifts if FEATURE_FW_LAUNCH is on, since then
# BOXNAVLAUNCH is not added to activeBoxIds at all -- see
# fc_msp_box.c:286-288), so re-resolve it after every reboot, never
# hard-code it.

LAT0, LON0 = 47.0, 8.5


# ---------------------------------------------------------------------------
# MSP transport (serial, MSPv2 "$X<" framing -- confirmed present/parsed by
# this firmware's serial MSP handler, same wire format as the TCP one used
# for SITL)
# ---------------------------------------------------------------------------

def crc8_dvb_s2(data: bytes, crc: int = 0) -> int:
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


class MspSerialClient:
    def __init__(self, port, baud=115200, timeout=3.0):
        self.port_name = port
        self.timeout = timeout
        try:
            self.ser = serial.Serial(port, baud, timeout=timeout)
        except serial.SerialException as e:
            print(f"XXXX FAILED to open serial port {port}: {e}")
            print("    Check: is the FC plugged in? Is another program (Configurator,")
            print("    another test script) holding the port open?")
            print("    If running in a sandbox: /dev/ttyACM*/ttyUSB* are normally")
            print("    allowlisted; if still blocked, ask the user rather than")
            print("    disabling the sandbox.")
            raise
        time.sleep(0.3)
        self.ser.reset_input_buffer()
        self._lock = threading.Lock()

    def close(self):
        try:
            self.ser.close()
        except Exception:
            pass

    def send(self, cmd, payload=b""):
        body = struct.pack("<BHH", 0, cmd, len(payload)) + payload
        frame = b"$X<" + body + bytes([crc8_dvb_s2(body)])
        n = self.ser.write(frame)
        if n != len(frame):
            raise IOError(f"short write: {n}/{len(frame)} bytes for cmd 0x{cmd:X}")

    def _read_exact(self, n, deadline):
        buf = b""
        while len(buf) < n:
            if time.monotonic() > deadline:
                raise TimeoutError(f"timed out waiting for {n - len(buf)} more bytes")
            chunk = self.ser.read(n - len(buf))
            if not chunk:
                continue
            buf += chunk
        return buf

    def recv(self, timeout=None):
        deadline = time.monotonic() + (timeout if timeout is not None else self.timeout)
        while True:
            if self._read_exact(1, deadline) != b"$":
                continue
            if self._read_exact(1, deadline) != b"X":
                continue
            direction = self._read_exact(1, deadline)
            if direction not in (b">", b"!"):
                continue
            hdr = self._read_exact(5, deadline)
            _flag, cmd, size = struct.unpack("<BHH", hdr)
            payload = self._read_exact(size, deadline)
            crc = self._read_exact(1, deadline)[0]
            if crc8_dvb_s2(hdr + payload) != crc:
                raise IOError(f"MSP CRC mismatch on cmd {cmd}")
            return cmd, payload, direction == b"!"

    def request(self, cmd, payload=b"", retries=3, timeout=None):
        """Send one request, then read frames until we see the matching
        reply -- WITHOUT resending on a mismatch.

        Real-hardware lesson (discovered while writing this test): the
        real MSP-over-USB-serial round trip occasionally delivers a reply
        late enough that it's still in flight when a *later* request's
        recv() starts waiting, so that later call ends up reading a stale/
        orphaned frame for an earlier cmd (valid CRC, just the wrong cmd
        id -- SITL's near-instant TCP loopback never showed this). The
        original version of this method treated any mismatch as reason to
        immediately re-send, which only made it worse: each blind resend
        adds one more in-flight request to the pipe, so the backlog of
        orphaned replies grows monotonically instead of draining. Fix:
        on a mismatch, keep reading (never resend) until the real match
        shows up or the deadline elapses -- this drains exactly the stale
        backlog that caused the mismatch in the first place."""
        eff_timeout = timeout if timeout is not None else self.timeout
        with self._lock:
            for attempt in range(retries):
                self.send(cmd, payload)
                deadline = time.monotonic() + eff_timeout
                while time.monotonic() < deadline:
                    try:
                        rcmd, rpayload, err = self.recv(timeout=deadline - time.monotonic())
                    except TimeoutError:
                        break  # nothing arrived at all within the budget -- fall through to resend
                    if rcmd == cmd:
                        if err:
                            raise IOError(f"MSP error reply for cmd 0x{cmd:X}")
                        return rpayload
                    # else: stale/orphaned reply to an earlier command -- discard, keep draining
                if attempt == retries - 1:
                    raise IOError(f"no matching reply for cmd 0x{cmd:X} after {retries} tries "
                                   "(genuine timeout, no reply of any kind arrived)")

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
        self.request(MSP_EEPROM_WRITE, timeout=5.0)

    def send_rc(self, channels):
        data = b"".join(struct.pack("<H", c) for c in channels)
        self.request(MSP_SET_RAW_RC, data)

    def arming_flags(self):
        p = self.request(MSP2_INAV_STATUS)
        return struct.unpack_from("<I", p, 9)[0]

    def flight_mode_flags(self):
        """Raw 4-byte box-mode-flags bitmask (packBoxModeFlags() order --
        see NAV_LAUNCH bit-index note above; do NOT compare this directly
        against flightModeFlags_e constants)."""
        p = self.request(MSP_STATUS_EX)
        return struct.unpack_from("<I", p, 6)[0]

    def box_permanent_ids(self):
        """MSP_BOXIDS: permanentId of each active box, in packBoxModeFlags()
        bit order (index i here == bit i of flight_mode_flags())."""
        p = self.request(MSP_BOXIDS)
        return list(p)

    def find_box_bit(self, permanent_id):
        ids = self.box_permanent_ids()
        if permanent_id not in ids:
            return None
        return 1 << ids.index(permanent_id)

    def simulator(self, payload):
        return self.request(MSP_SIMULATOR, payload)


def find_acm_port(preferred):
    if preferred and glob.glob(preferred):
        return preferred
    candidates = sorted(glob.glob("/dev/ttyACM*"))
    if candidates:
        return candidates[0]
    return preferred


def exit_cli_if_stuck(port_name, baud=115200):
    """Lesson learned (test-engineer agent notes): a prior session may have
    left the FC in CLI mode, which blocks all MSP traffic. Send 'exit' just
    in case, then give it time to drop back to MSP mode."""
    try:
        s = serial.Serial(port_name, baud, timeout=0.5)
        time.sleep(0.2)
        s.reset_input_buffer()
        s.write(b"#\r\n")
        time.sleep(0.1)
        s.write(b"exit\r\n")
        time.sleep(0.3)
        s.close()
        time.sleep(0.3)
    except serial.SerialException:
        pass


def check_connection(port):
    port = find_acm_port(port)
    if not port:
        print("XXXX FAILED: no /dev/ttyACM* device found")
        print("    Check: is the FC plugged in via USB?")
        print("    If running in a sandbox: /dev/ttyACM* is normally allowlisted;")
        print("    if still blocked, ask the user rather than disabling the sandbox.")
        sys.exit(1)
    exit_cli_if_stuck(port)
    try:
        c = MspSerialClient(port)
        ver = c.api_version()
        print(f"OK: MSP connection verified on {port}, API version {ver}")
        c.close()
    except Exception as e:
        print(f"XXXX FAILED to get a valid MSP reply on {port}: {e}")
        print("    Check: is the FC actually running firmware (not stuck in a")
        print("    bootloader)? Is another program (Configurator, another test")
        print("    script) holding the port open? Is it stuck in CLI mode?")
        sys.exit(1)
    return port


def connect_with_retry(port_hint, timeout=25.0):
    t_end = time.monotonic() + timeout
    last = None
    while time.monotonic() < t_end:
        port = find_acm_port(port_hint)
        if port:
            try:
                c = MspSerialClient(port, timeout=2.0)
                c.api_version()
                return c
            except (serial.SerialException, ConnectionError, OSError, IOError, TimeoutError) as e:
                last = e
        time.sleep(0.3)
    raise TimeoutError(f"FC did not come back up on {port_hint} within {timeout}s: {last}")


# ---------------------------------------------------------------------------
# HITL packet builder (MSP_SIMULATOR v2, full sensor payload) -- identical
# wire format to the SITL version; layout re-confirmed against THIS
# checkout's fc_msp.c readMspSimulatorValues() before use.
# ---------------------------------------------------------------------------

def build_hitl_v2(flags, gps_fix, gps_sats, lat_e7, lon_e7, alt_cm,
                   speed_cms, course_dd, vel_n_cms, vel_e_cms, vel_d_cms,
                   roll_dd, pitch_dd, yaw_dd,
                   acc_x_mg, acc_y_mg, acc_z_mg,
                   gyro_x_16dps, gyro_y_16dps, gyro_z_16dps,
                   baro_pa=101325, mag=(230, 5, -410)):
    return struct.pack(
        "<BB" "BBiiIHH" "hhh" "hhh" "hhh" "hhh" "I" "hhh",
        SIMULATOR_MSP_VERSION, flags,
        gps_fix, gps_sats, lat_e7, lon_e7, alt_cm, speed_cms, course_dd,
        vel_n_cms, vel_e_cms, vel_d_cms,
        roll_dd, pitch_dd, yaw_dd,
        acc_x_mg, acc_y_mg, acc_z_mg,
        gyro_x_16dps, gyro_y_16dps, gyro_z_16dps,
        baro_pa,
        mag[0], mag[1], mag[2],
    )


def latlon_from_ne(x_north_m, y_east_m):
    lat = LAT0 + x_north_m / 111320.0
    lon = LON0 + y_east_m / (111320.0 * math.cos(math.radians(LAT0)))
    return int(round(lat * 1e7)), int(round(lon * 1e7))


class HitlState:
    def __init__(self):
        self.lock = threading.Lock()
        self.rc = [RC_MID] * 8
        self.rc[CH_THROTTLE] = RC_LOW
        self.rc[CH_ARM] = RC_LOW
        self.rc[CH_LAUNCH] = RC_LOW

        self.gps_fix = 2
        self.gps_sats = 12
        self.speed_cms = 0
        self.course_dd = 0
        self.x_m = 0.0
        self.y_m = 0.0
        self.alt_cm = 5000
        self.climb_rate_cms = 0.0

        self.roll_dd = 0
        self.pitch_dd = 0
        self.yaw_dd = 0

        self.acc_x_mg = 0
        self.acc_y_mg = 0
        self.acc_z_mg = GRAVITY_MG

        self.gyro_x_16 = 0
        self.gyro_y_16 = 0
        self.gyro_z_16 = 0

    def set(self, **kw):
        with self.lock:
            for k, v in kw.items():
                setattr(self, k, v)

    def set_rc(self, ch, val):
        with self.lock:
            self.rc[ch] = val

    def snapshot(self):
        with self.lock:
            return dict(self.__dict__)


class HitlSender:
    """Sends MSP_SIMULATOR + MSP_SET_RAW_RC at ~50Hz over the serial link.

    IMPORTANT (real-hardware lesson, discovered while writing this test):
    the FC's real MSP-over-serial round trip has enough latency variance
    (unlike SITL's near-instant TCP loopback) that a second thread issuing
    its own concurrent MSP requests on the SAME MspSerialClient can race: a
    reply that arrives late (after ITS OWN request()'s timeout gave up)
    lands in the RX stream just before a *different*, unrelated request's
    reply -- read_exact()/recv() then happily parses that orphaned frame
    (valid CRC, just the wrong cmd id) and every retry keeps re-consuming
    more orphaned frames instead of the real answer, so the second thread's
    request() eventually raises "no matching reply" with no actual
    IOError/timeout ever having fired. Confirmed the exact failure signature
    on this real board (control_trivial_launch()'s wait_armable() call was
    the second, colliding thread). Fix: exactly ONE thread ever touches the
    serial port after start() -- this sender polls MSP2_INAV_STATUS /
    MSP_STATUS_EX itself every few ticks and caches the results; everything
    else in this script reads those cached values instead of issuing its
    own concurrent request.
    """

    STATUS_POLL_EVERY_N_TICKS = 5  # ~4Hz status polling at the 20ms tick rate

    def __init__(self, msp: MspSerialClient, state: HitlState):
        self.msp = msp
        self.state = state
        self.running = False
        self.thread = None
        self.fail_count = 0
        self.tick_count = 0
        self.last_exc = None
        self._status_lock = threading.Lock()
        self._arming_flags = 0
        self._flight_mode_flags = 0
        self._have_status = False

    def get_arming_flags(self):
        with self._status_lock:
            return self._arming_flags

    def get_flight_mode_flags(self):
        with self._status_lock:
            return self._flight_mode_flags

    def wait_for_status(self, timeout=5.0):
        """Block until at least one status poll has succeeded."""
        t_end = time.monotonic() + timeout
        while time.monotonic() < t_end:
            with self._status_lock:
                if self._have_status:
                    return
            time.sleep(0.05)
        raise TimeoutError("sender never received a status reply "
                            f"(fail_count={self.fail_count}, last_exc={self.last_exc})")

    def _loop(self):
        dt = 0.02
        flags = HITL_ENABLE | HITL_HAS_NEW_GPS_DATA
        while self.running:
            t0 = time.perf_counter()
            s = self.state.snapshot()

            course_rad = math.radians(s["course_dd"] / 10.0)
            dist = s["speed_cms"] / 100.0 * dt
            with self.state.lock:
                self.state.x_m += dist * math.cos(course_rad)
                self.state.y_m += dist * math.sin(course_rad)
                x_m, y_m = self.state.x_m, self.state.y_m
                self.state.alt_cm += s["climb_rate_cms"] * dt
                alt_cm = int(self.state.alt_cm)
            lat_e7, lon_e7 = latlon_from_ne(x_m, y_m)
            vel_n = int(s["speed_cms"] * math.cos(course_rad))
            vel_e = int(s["speed_cms"] * math.sin(course_rad))

            payload = build_hitl_v2(
                flags,
                s["gps_fix"], s["gps_sats"],
                lat_e7, lon_e7, alt_cm,
                s["speed_cms"], s["course_dd"],
                vel_n, vel_e, 0,
                s["roll_dd"], s["pitch_dd"], s["yaw_dd"],
                s["acc_x_mg"], s["acc_y_mg"], s["acc_z_mg"],
                s["gyro_x_16"], s["gyro_y_16"], s["gyro_z_16"],
            )
            try:
                self.msp.simulator(payload)
                self.msp.send_rc(s["rc"])
                self.tick_count += 1

                if self.tick_count % self.STATUS_POLL_EVERY_N_TICKS == 0:
                    af = self.msp.arming_flags()
                    mf = self.msp.flight_mode_flags()
                    with self._status_lock:
                        self._arming_flags = af
                        self._flight_mode_flags = mf
                        self._have_status = True
            except (IOError, ConnectionError, OSError, TimeoutError) as e:
                self.fail_count += 1
                self.last_exc = e

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


# ---------------------------------------------------------------------------
# Provisioning / reboot helpers
# ---------------------------------------------------------------------------

def force_disarm_before_provision(msp: MspSerialClient):
    channels = [RC_MID] * 8
    channels[CH_THROTTLE] = RC_LOW
    channels[CH_ARM] = RC_LOW
    data = b"".join(struct.pack("<H", c) for c in channels)
    for _ in range(10):
        try:
            msp.request(MSP_SET_RAW_RC, data)
        except (IOError, ConnectionError, OSError, TimeoutError):
            pass
        time.sleep(0.05)
    time.sleep(0.5)


def provision(msp: MspSerialClient):
    force_disarm_before_provision(msp)
    print(f"  API version: {msp.api_version()}")
    msp.set_setting("platform_type", struct.pack("<B", 1))     # AIRPLANE
    msp.set_setting("small_angle", struct.pack("<B", 180))     # never SMALL_ANGLE-block arming
    msp.set_setting("receiver_type", struct.pack("<B", 2))     # MSP (rxReceiverType_e index 2)
    msp.enable_feature(FEATURE_GPS)
    msp.set_setting("gps_provider", struct.pack("<B", 1))      # MSP

    msp.set_mode_range(0, PERM_ARM, CH_ARM - 4, 1700, 2100)
    msp.set_mode_range(1, PERM_NAV_LAUNCH, CH_LAUNCH - 4, 1700, 2100)

    msp.save_eeprom()
    try:
        msp.request(MSP_REBOOT, timeout=2.0)
    except (IOError, ConnectionError, OSError, TimeoutError):
        pass
    print("  OK: provisioned, rebooting")


def reboot_and_reconnect(port_hint) -> MspSerialClient:
    time.sleep(3.0)  # real USB re-enumeration takes longer than SITL's execvp
    new_msp = connect_with_retry(port_hint)
    print("  OK: reconnected after reboot")
    return new_msp


def wait_for_gyro_calibration(seconds: float = 3.0):
    # Same lesson as the SITL test: enabling ARMING_FLAG(SIMULATOR_MODE_HITL)
    # stops real gyroUpdate() from running (gyro.c:678 gates on this flag on
    # ANY target, not just SITL). gyroIsCalibrationComplete() is a one-shot
    # ~2000ms timer that must complete BEFORE the first MSP_SIMULATOR frame,
    # or it freezes forever. Must be a real wall-clock wait, no HITL traffic.
    print(f"  Waiting {seconds:.1f}s for boot gyro calibration (no HITL traffic yet)...")
    time.sleep(seconds)


def wait_armable(sender: "HitlSender", timeout: float = 20.0) -> int:
    """Polls the sender's cached status (NOT a direct concurrent MSP
    request -- see HitlSender docstring for why that races on real hw)."""
    sender.wait_for_status()
    NON_BLOCKING = FLAG_ARMED | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 14)
    t_end = time.monotonic() + timeout
    last = 0
    while time.monotonic() < t_end:
        last = sender.get_arming_flags()
        if (last & ~NON_BLOCKING & 0xFFFFFFFF) == 0:
            return last
        time.sleep(0.2)
    raise TimeoutError(f"never became armable, last arming_flags=0x{last:08X}")


def arm(state: HitlState, sender: "HitlSender", timeout: float = 10.0) -> None:
    state.set_rc(CH_ARM, RC_LOW)
    time.sleep(0.3)
    state.set_rc(CH_ARM, RC_HIGH)
    t_end = time.monotonic() + timeout
    while time.monotonic() < t_end:
        f = sender.get_arming_flags()
        if f & FLAG_ARMED:
            return
        time.sleep(0.2)
    raise RuntimeError(f"failed to arm, arming_flags=0x{sender.get_arming_flags():08X}")


def safe_shutdown(sender: "HitlSender", state: HitlState, timeout: float = 5.0):
    """Disarm THROUGH the still-running sender and confirm it before
    stopping it.

    Real-hardware lesson: the original cleanup did `sender.stop()` then
    `state.set_rc(CH_ARM, RC_LOW)` -- but state.set_rc() only ever staged a
    value for the sender's _loop() to transmit on its next tick, and by
    then the sender thread was already dead, so the "disarm" was silently
    never sent. The FC stayed ARMED into the next scenario's provision()
    call, whose force_disarm_before_provision() sends direct low-ARM RC
    frames too, but that alone still wasn't sufficient (the FC had also
    gone this whole time with zero fresh MSP_SIMULATOR/RC frames once the
    sender died, which is its own untested state) -- the net effect was
    MSP_EEPROM_WRITE failing with MSP_RESULT_ERROR (it refuses outright
    while ARMED, fc_msp.c:3143). Always disarm via the live sender and
    confirm ARMED clears BEFORE calling sender.stop().
    """
    state.set_rc(CH_THROTTLE, RC_LOW)
    state.set_rc(CH_ARM, RC_LOW)
    state.set_rc(CH_LAUNCH, RC_LOW)
    t_end = time.monotonic() + timeout
    while time.monotonic() < t_end:
        if not (sender.get_arming_flags() & FLAG_ARMED):
            break
        time.sleep(0.1)
    else:
        print(f"  WARNING: still armed after {timeout:.1f}s disarm-on-cleanup "
              f"attempt, flags=0x{sender.get_arming_flags():08X}")
    sender.stop()


PASS, FAIL, BLOCKED = "PASS", "FAIL", "BLOCKED"
RESULTS = []


def log_result(label, status, detail=""):
    icon = {"PASS": "+", "FAIL": "x", "BLOCKED": "?"}[status]
    print(f"  [{icon}] {label}: {status}" + (f" -- {detail}" if detail else ""))
    RESULTS.append((label, status, detail))
