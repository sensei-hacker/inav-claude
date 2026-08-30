#!/usr/bin/env python3
"""
Test the sticky sbuf overrun check added to fc_msp.c for:
  - MSP2_INAV_SET_AUX_RC (0x2230)
  - MSP_OSD_CHAR_WRITE (87)

Connects to SITL over raw TCP (MSPv2 native framing implemented by hand so
we can precisely distinguish "success" ('>') vs "error" ('!') response
frames vs a hung/dead connection (timeout), which matters for this test).

Usage: python3 test_sbuf_overrun.py [host] [port]
Default: localhost 5760
"""
import socket
import struct
import sys
import threading
import time

MSP_SET_RAW_RC = 200
MSP_RC = 105
MSP_RX_CONFIG = 44
MSP_SET_RX_CONFIG = 45
MSP_REBOOT = 68
MSP_EEPROM_WRITE = 250
MSP_API_VERSION = 1
MSP2_INAV_SET_AUX_RC = 0x2230
MSP_OSD_CHAR_WRITE = 87

RX_TYPE_MSP = 2

fail_count = 0
pass_count = 0


def ok(msg):
    global pass_count
    pass_count += 1
    print(f"  ✓ PASS: {msg}")


def bad(msg):
    global fail_count
    fail_count += 1
    print(f"  ✗ FAIL: {msg}")


def crc8_dvb_s2(crc, byte):
    crc ^= byte
    for _ in range(8):
        if crc & 0x80:
            crc = ((crc << 1) ^ 0xD5) & 0xFF
        else:
            crc = (crc << 1) & 0xFF
    return crc


def crc8_dvb_s2_buf(crc, data):
    for b in data:
        crc = crc8_dvb_s2(crc, b)
    return crc


def build_v2_frame(code, payload=b""):
    flags = 0
    hdr = struct.pack("<BHH", flags, code, len(payload))
    crc = crc8_dvb_s2_buf(0, hdr)
    crc = crc8_dvb_s2_buf(crc, payload)
    return b"$X<" + hdr + payload + bytes([crc])


class MSPConn:
    """Minimal, careful raw MSPv2-native client with explicit error/timeout handling."""

    def __init__(self, host, port, timeout=2.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.buf = b""
        self.lock = threading.Lock()

    def connect(self):
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            self.sock.settimeout(self.timeout)
        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            print(f"FATAL: Could not connect to {self.host}:{self.port}: {e}")
            print("  Note: If running in sandbox, /dev/ttyACM*, /dev/ttyUSB*, and localhost")
            print("  are allowlisted; if access is still blocked, ask the user rather than")
            print("  disabling the sandbox.")
            raise

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None

    def _recv_more(self, timeout):
        self.sock.settimeout(timeout)
        try:
            chunk = self.sock.recv(4096)
        except socket.timeout:
            return False
        if not chunk:
            raise ConnectionError("Peer closed connection")
        self.buf += chunk
        return True

    def read_frame(self, timeout):
        """Read one MSPv2-native frame from the stream (any code).
        Returns dict(direction, code, payload) or None on timeout."""
        deadline = time.monotonic() + timeout
        while True:
            # try to parse a frame out of self.buf
            idx = self.buf.find(b"$X")
            if idx != -1 and len(self.buf) >= idx + 3:
                direction = chr(self.buf[idx + 2])
                if direction in (">", "<", "!"):
                    if len(self.buf) >= idx + 3 + 5:
                        flags, code, size = struct.unpack("<BHH", self.buf[idx + 3: idx + 3 + 5])
                        frame_len = 3 + 5 + size + 1
                        if len(self.buf) >= idx + frame_len:
                            payload = self.buf[idx + 8: idx + 8 + size]
                            self.buf = self.buf[idx + frame_len:]
                            return {"direction": direction, "code": code, "payload": payload}
                else:
                    # false '$X' match not followed by valid dir byte; drop 2 bytes and retry
                    self.buf = self.buf[idx + 2:]
                    continue
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            if not self._recv_more(min(remaining, 0.2)):
                if time.monotonic() >= deadline:
                    return None

    def send_raw(self, code, payload=b""):
        frame = build_v2_frame(code, payload)
        with self.lock:
            n = self.sock.sendall(frame)  # sendall returns None on success
        return len(frame)

    def request(self, code, payload=b"", timeout=1.0, expect_code=None):
        """Send request, wait for the matching response code.
        Returns dict(direction, code, payload). Raises TimeoutError if none arrives."""
        want = expect_code if expect_code is not None else code
        self.send_raw(code, payload)
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"No response to code {code} within {timeout}s")
            frame = self.read_frame(remaining)
            if frame is None:
                raise TimeoutError(f"No response to code {code} within {timeout}s")
            if frame["code"] == want:
                return frame
            # else: some unrelated frame (e.g. leftover), keep waiting


class RCSender:
    """Continuous MSP_SET_RAW_RC sender at 50Hz to keep RX_TYPE_MSP link alive."""

    def __init__(self, conn):
        self.conn = conn
        self.running = False
        self.thread = None

    def _loop(self):
        # IMPORTANT: only send 4 channels (RPYT). rx.c's aux-overlay logic
        # skips channels covered by the last MSP_SET_RAW_RC frame width
        # (rxMspGetLastChannelCount()) when receiverType==MSP, so sending
        # a wide RC frame here would mask out the very aux channels
        # (index 12+) that MSP2_INAV_SET_AUX_RC is supposed to control.
        channels = [1500, 1500, 1000, 1500]
        data = struct.pack("<4H", *channels)
        while self.running:
            try:
                self.conn.send_raw(MSP_SET_RAW_RC, data)
            except OSError:
                pass
            time.sleep(0.02)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)


def verify_connection(conn):
    """Pre-test sanity check: confirm FC actually responds to MSP."""
    try:
        frame = conn.request(MSP_API_VERSION, b"", timeout=2.0)
    except TimeoutError as e:
        print(f"FATAL: FC did not respond to MSP_API_VERSION: {e}")
        print("  The FC may be in CLI mode from a previous test (send 'exit\\n' or reboot),")
        print("  or SITL may not be fully started yet.")
        return False
    if frame["direction"] != ">":
        print(f"FATAL: MSP_API_VERSION returned error/unexpected direction={frame['direction']!r}")
        return False
    print(f"  ✓ Connected and FC responds to MSP (API version payload: {list(frame['payload'])})")
    return True


def set_receiver_type_msp(conn):
    frame = conn.request(MSP_RX_CONFIG, b"", timeout=2.0)
    data = bytearray(frame["payload"])
    if len(data) < 24:
        print(f"  WARNING: MSP_RX_CONFIG payload only {len(data)} bytes, expected >=24")
        return False
    current_type = data[23]
    print(f"  Current receiverType byte: {current_type}")
    if current_type == RX_TYPE_MSP:
        print("  receiverType already MSP, no reboot needed")
        return False
    data[23] = RX_TYPE_MSP
    conn.request(MSP_SET_RX_CONFIG, bytes(data), timeout=2.0)
    conn.request(MSP_EEPROM_WRITE, b"", timeout=2.0)
    print("  Set receiverType=MSP and saved to EEPROM; reboot required")
    return True


def reboot_and_wait(conn, host, port):
    conn.send_raw(MSP_REBOOT, b"")
    conn.close()
    print("  Reboot sent, waiting for SITL to come back...")
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        time.sleep(1)
        try:
            s = socket.create_connection((host, port), timeout=1.0)
            s.close()
            time.sleep(1.0)  # give the MSP stack a moment after port opens
            return True
        except OSError:
            continue
    return False


def get_rc_channels(conn, num=32):
    frame = conn.request(MSP_RC, b"", timeout=2.0)
    n = len(frame["payload"]) // 2
    vals = struct.unpack(f"<{n}H", frame["payload"])
    return list(vals)


def send_aux_rc(conn, start_channel, resolution_mode, data_bytes, timeout=1.0):
    """Send MSP2_INAV_SET_AUX_RC frame. Returns ('ok'|'error'|'timeout', frame_or_None)."""
    def_byte = ((start_channel & 0x1F) << 3) | (resolution_mode & 0x07)
    payload = bytes([def_byte]) + bytes(data_bytes)
    try:
        frame = conn.request(MSP2_INAV_SET_AUX_RC, payload, timeout=timeout)
    except TimeoutError:
        return "timeout", None
    if frame["direction"] == "!":
        return "error", frame
    elif frame["direction"] == ">":
        return "ok", frame
    else:
        return "unknown:" + frame["direction"], frame


def send_osd_char_write(conn, addr_bytes, char_data, timeout=1.0):
    payload = addr_bytes + char_data
    try:
        frame = conn.request(MSP_OSD_CHAR_WRITE, payload, timeout=timeout)
    except TimeoutError:
        return "timeout", None
    if frame["direction"] == "!":
        return "error", frame
    elif frame["direction"] == ">":
        return "ok", frame
    else:
        return "unknown:" + frame["direction"], frame


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5760

    print(f"Connecting to SITL MSP at {host}:{port} ...")
    conn = MSPConn(host, port)
    try:
        conn.connect()
    except Exception:
        return 1

    if not verify_connection(conn):
        conn.close()
        return 1

    print("\n[Setup] Ensuring receiverType = MSP (needed for MSP_RC readback of 32 channels)...")
    rebooted = set_receiver_type_msp(conn)
    if rebooted:
        if not reboot_and_wait(conn, host, port):
            print("FATAL: SITL did not come back up after reboot")
            return 1
        conn = MSPConn(host, port)
        conn.connect()
        if not verify_connection(conn):
            return 1

    rc_sender = RCSender(conn)
    rc_sender.start()
    time.sleep(1.0)  # let RC link establish

    try:
        # confirm RC channel readback width
        rc = get_rc_channels(conn)
        print(f"  MSP_RC reports {len(rc)} channels (need >=32 for our test channel indices)")
        if len(rc) < 32:
            bad(f"MSP_RC only reports {len(rc)} channels; cannot verify channels 12-31")
        else:
            ok(f"MSP_RC reports {len(rc)} channels")

        # =========================================================
        # TEST 1: Baseline correctness - well formed frame per mode
        # =========================================================
        print("\n=== TEST 1: Baseline correctness (well-formed frames, all 4 resolution modes) ===")

        # Mode 0: 2-bit, startChannel=12, 1 data byte -> 4 channels (12,13,14,15)
        print("\n-- Mode 0 (2-bit) --")
        byte0 = (0b01 << 6) | (0b10 << 4) | (0b11 << 2) | (0b01 << 0)  # ch0=1,ch1=2,ch2=3,ch3=1
        status, frame = send_aux_rc(conn, start_channel=12, resolution_mode=0, data_bytes=[byte0])
        print(f"  Send result: {status}")
        expected = {12: 1000, 13: 1500, 14: 2000, 15: 1000}
        if status == "ok":
            ok("MSP2_INAV_SET_AUX_RC (2-bit) accepted (direction '>')")
        else:
            bad(f"MSP2_INAV_SET_AUX_RC (2-bit) well-formed frame rejected/timed out: {status}")
        time.sleep(0.3)
        rc = get_rc_channels(conn)
        for idx, exp in expected.items():
            got = rc[idx] if idx < len(rc) else None
            if got == exp:
                ok(f"channel[{idx}] = {got} (expected {exp})")
            else:
                bad(f"channel[{idx}] = {got}, expected {exp}")

        # Mode 1: 4-bit, startChannel=16, 1 data byte -> 2 channels (16,17)
        print("\n-- Mode 1 (4-bit) --")
        byte1 = (5 << 4) | 10  # ch0=5, ch1=10
        status, frame = send_aux_rc(conn, start_channel=16, resolution_mode=1, data_bytes=[byte1])
        print(f"  Send result: {status}")
        expected = {16: 1000 + ((5 - 1) * 1000) // 14, 17: 1000 + ((10 - 1) * 1000) // 14}
        if status == "ok":
            ok("MSP2_INAV_SET_AUX_RC (4-bit) accepted (direction '>')")
        else:
            bad(f"MSP2_INAV_SET_AUX_RC (4-bit) well-formed frame rejected/timed out: {status}")
        time.sleep(0.3)
        rc = get_rc_channels(conn)
        for idx, exp in expected.items():
            got = rc[idx] if idx < len(rc) else None
            if got == exp:
                ok(f"channel[{idx}] = {got} (expected {exp})")
            else:
                bad(f"channel[{idx}] = {got}, expected {exp}")

        # Mode 2: 8-bit, startChannel=20, 3 data bytes -> 3 channels (20,21,22)
        print("\n-- Mode 2 (8-bit) --")
        raws = [1, 128, 255]
        status, frame = send_aux_rc(conn, start_channel=20, resolution_mode=2, data_bytes=raws)
        print(f"  Send result: {status}")

        def pwm8(r):
            return 1000 + ((r - 1) * 1000) // 254

        expected = {20 + i: pwm8(r) for i, r in enumerate(raws)}
        if status == "ok":
            ok("MSP2_INAV_SET_AUX_RC (8-bit) accepted (direction '>')")
        else:
            bad(f"MSP2_INAV_SET_AUX_RC (8-bit) well-formed frame rejected/timed out: {status}")
        time.sleep(0.3)
        rc = get_rc_channels(conn)
        for idx, exp in expected.items():
            got = rc[idx] if idx < len(rc) else None
            if got == exp:
                ok(f"channel[{idx}] = {got} (expected {exp})")
            else:
                bad(f"channel[{idx}] = {got}, expected {exp}")

        # Mode 2 bonus: raw=0 means "skip" (no update), verify previous value retained
        print("\n-- Mode 2 (8-bit) skip semantics --")
        status, frame = send_aux_rc(conn, start_channel=20, resolution_mode=2, data_bytes=[0, 200, 0])
        print(f"  Send result: {status}")
        time.sleep(0.3)
        rc2 = get_rc_channels(conn)
        if status == "ok":
            ok("skip-frame accepted")
        else:
            bad(f"skip-frame rejected/timed out: {status}")
        if rc2[20] == expected[20]:
            ok(f"channel[20] unchanged at {rc2[20]} (raw=0 -> skip honored)")
        else:
            bad(f"channel[20] = {rc2[20]}, expected unchanged {expected[20]} (raw=0 should skip)")
        if rc2[22] == expected[22]:
            ok(f"channel[22] unchanged at {rc2[22]} (raw=0 -> skip honored)")
        else:
            bad(f"channel[22] = {rc2[22]}, expected unchanged {expected[22]}")
        exp21 = pwm8(200)
        if rc2[21] == exp21:
            ok(f"channel[21] updated to {rc2[21]} (expected {exp21})")
        else:
            bad(f"channel[21] = {rc2[21]}, expected {exp21}")

        # Mode 3: 16-bit, startChannel=24, 8 data bytes -> 4 channels (24,25,26,27)
        print("\n-- Mode 3 (16-bit) --")
        raws16 = [100, 3000, 1000, 2200]  # first two exercise constrain() clamping
        data3 = b"".join(struct.pack("<H", r) for r in raws16)
        status, frame = send_aux_rc(conn, start_channel=24, resolution_mode=3, data_bytes=data3)
        print(f"  Send result: {status}")

        def clamp16(r):
            return max(750, min(2250, r))

        expected = {24 + i: clamp16(r) for i, r in enumerate(raws16)}
        if status == "ok":
            ok("MSP2_INAV_SET_AUX_RC (16-bit) accepted (direction '>')")
        else:
            bad(f"MSP2_INAV_SET_AUX_RC (16-bit) well-formed frame rejected/timed out: {status}")
        time.sleep(0.3)
        rc = get_rc_channels(conn)
        for idx, exp in expected.items():
            got = rc[idx] if idx < len(rc) else None
            if got == exp:
                ok(f"channel[{idx}] = {got} (expected {exp}, clamp check)")
            else:
                bad(f"channel[{idx}] = {got}, expected {exp}")

        # =========================================================
        # TEST 2: Truncated / malformed frames per resolution mode
        # =========================================================
        print("\n=== TEST 2: dataSize-vs-actual-layout edge cases per mode ===")
        print("(Handler's own dataSize bounds checks were already confirmed correct in prior")
        print(" audit; goal here is to confirm nothing crashes/hangs and behavior is sane.)")

        # 2a: dataSize=1 (only defByte, no data) -> dataSize<2 explicit reject in handler
        print("\n-- dataSize=1 (defByte only, no payload data) --")
        status, frame = send_aux_rc(conn, start_channel=12, resolution_mode=2, data_bytes=[])
        print(f"  Send result: {status}")
        if status == "error":
            ok("Correctly rejected (dataSize<2 check)")
        elif status == "timeout":
            bad("TIMEOUT sending dataSize=1 frame - possible hang/crash regression!")
        else:
            bad(f"Unexpected result for dataSize=1: {status}")

        # 2b: mode 3 (16-bit) with odd dataBytes (5 bytes -> not multiple of 2)
        print("\n-- Mode 3 (16-bit) with odd dataBytes=5 --")
        status, frame = send_aux_rc(conn, start_channel=12, resolution_mode=3, data_bytes=[1, 2, 3, 4, 5])
        print(f"  Send result: {status}")
        if status == "error":
            ok("Correctly rejected (dataBytes %% 2 != 0 check)")
        elif status == "timeout":
            bad("TIMEOUT sending odd-length 16-bit frame - possible hang/crash regression!")
        else:
            bad(f"Unexpected result for odd 16-bit dataBytes: {status}")

        # 2c: startChannel + channelCount > 32 (mode2, startChannel=30, 5 bytes -> would need ch30-34)
        print("\n-- Mode 2 (8-bit) startChannel=30 with 5 channels (overflows ch index 32) --")
        status, frame = send_aux_rc(conn, start_channel=30, resolution_mode=2, data_bytes=[1, 2, 3, 4, 5])
        print(f"  Send result: {status}")
        if status == "error":
            ok("Correctly rejected (startChannel+channelCount>32 check)")
        elif status == "timeout":
            bad("TIMEOUT - possible hang/crash regression!")
        else:
            bad(f"Unexpected result: {status}")

        # 2d: max valid payload size (dataSize=49) still works and doesn't hang
        print("\n-- Max valid payload (dataSize=49, mode2 8-bit, 48 channels worth but capped by 32-startChannel) --")
        # startChannel=12 -> max channelCount = 32-12=20 for mode2 (8-bit, 1 byte/channel)
        # dataBytes=20 -> dataSize=21 (well within <=49 cap, but exercises a bigger buffer)
        raws_big = [((i % 254) + 1) for i in range(20)]
        status, frame = send_aux_rc(conn, start_channel=12, resolution_mode=2, data_bytes=raws_big)
        print(f"  Send result: {status}")
        if status == "ok":
            ok("Large well-formed 8-bit frame (20 channels) accepted")
        elif status == "timeout":
            bad("TIMEOUT on large well-formed frame - possible hang/crash regression!")
        else:
            bad(f"Large well-formed frame unexpectedly rejected: {status}")

        # 2e: verify connection still alive / FC still responsive after all the above
        print("\n-- Post-test connection liveness check --")
        try:
            frame = conn.request(MSP_API_VERSION, b"", timeout=2.0)
            if frame["direction"] == ">":
                ok("FC still responsive to MSP_API_VERSION after all AUX_RC tests")
            else:
                bad(f"FC responded with unexpected direction {frame['direction']!r}")
        except TimeoutError:
            bad("FC NOT RESPONSIVE after AUX_RC tests - possible crash/hang!")

        # =========================================================
        # TEST 3 (optional): MSP_OSD_CHAR_WRITE sanity (no real OSD hw)
        # =========================================================
        print("\n=== TEST 3: MSP_OSD_CHAR_WRITE sanity (SITL has USE_OSD but no attached display) ===")
        # 8-bit addr + full char (54 bytes metadata+visible) -> dataSize = 1 + 54 = 55
        # OSD_CHAR_BYTES is typically 54 (per-glyph data incl. metadata bytes); dataSize>=55 required
        char_data = bytes(range(54))  # 54 bytes of dummy glyph data
        payload = bytes([5]) + char_data  # addr=5 (8-bit)
        print(f"  dataSize being sent: {len(payload)}")
        status, frame = send_osd_char_write(conn, bytes([5]), char_data)
        print(f"  Send result: {status}")
        if status == "ok":
            ok("MSP_OSD_CHAR_WRITE well-formed frame accepted even with no OSD display attached")
        elif status == "error":
            print("  NOTE: rejected - could be expected if no display or dataSize edge; not necessarily a bug")
            bad(f"MSP_OSD_CHAR_WRITE well-formed frame was rejected: {status}")
        else:
            bad(f"MSP_OSD_CHAR_WRITE TIMEOUT - possible hang/crash: {status}")

        # final liveness check
        try:
            frame = conn.request(MSP_API_VERSION, b"", timeout=2.0)
            if frame["direction"] == ">":
                ok("FC still responsive after OSD_CHAR_WRITE test")
            else:
                bad(f"FC responded with unexpected direction after OSD test: {frame['direction']!r}")
        except TimeoutError:
            bad("FC NOT RESPONSIVE after OSD_CHAR_WRITE test - possible crash/hang!")

        # =========================================================
        # TEST 4: Wire-size accept/reject equivalence (Phase 4) --
        # the sticky overrun check must not change accept/reject for
        # ANY dataSize vs the pre-PR contract:
        #   AUX_RC: 2..49 accepted (length drives channel count)
        #   OSD_CHAR_WRITE: >= 55 accepted, < 55 rejected
        # Longer messages from newer senders must be accepted with
        # trailing bytes ignored; shorter-but-valid AUX_RC messages
        # (the normal case) must be accepted.
        # =========================================================
        print("\n=== TEST 4: wire-size accept/reject equivalence (longer/exact/shorter) ===")

        # 4a: AUX_RC min valid (dataSize=2: defByte + 1 data byte) -> accepted
        print("\n-- AUX_RC dataSize=2 (min valid) --")
        status, frame = send_aux_rc(conn, start_channel=12, resolution_mode=0, data_bytes=[0b01010101])
        print(f"  Send result: {status}")
        if status == "ok":
            ok("AUX_RC dataSize=2 accepted (shorter-but-valid is the normal case)")
        elif status == "timeout":
            bad("TIMEOUT on AUX_RC dataSize=2 - possible hang/crash regression!")
        else:
            bad(f"AUX_RC dataSize=2 unexpectedly rejected: {status}")

        # 4b: AUX_RC max valid (dataSize=41: defByte + 40 bytes, 16-bit, 20 channels
        #     from startChannel=12 -> 12+20=32, exactly the cap) -> accepted
        print("\n-- AUX_RC dataSize=41 (max valid: 20ch x 16-bit from ch12) --")
        data41 = b"".join(struct.pack("<H", 1000 + 50 * i) for i in range(20))
        status, frame = send_aux_rc(conn, start_channel=12, resolution_mode=3, data_bytes=data41)
        print(f"  Send result: {status}")
        if status == "ok":
            ok("AUX_RC dataSize=41 accepted (max valid frame)")
        elif status == "timeout":
            bad("TIMEOUT on AUX_RC dataSize=41 - possible hang/crash regression!")
        else:
            bad(f"AUX_RC dataSize=41 unexpectedly rejected: {status}")
        time.sleep(0.3)
        rc = get_rc_channels(conn)
        if len(rc) > 31 and rc[12] == 1000:
            ok(f"channel[12] = {rc[12]} (expected 1000 from 41-byte frame)")
        else:
            bad(f"channel[12] = {rc[12] if len(rc) > 12 else 'N/A'}, expected 1000")

        # 4c: AUX_RC dataSize=49 (gate allows 2..49, but 16-bit 24ch from ch12 would
        #     overflow 12+24=36>32 -> channel-count check rejects; pre-PR identical)
        print("\n-- AUX_RC dataSize=49 (within gate, exceeds channel bounds) --")
        data49 = b"".join(struct.pack("<H", 1500) for _ in range(24))
        status, frame = send_aux_rc(conn, start_channel=12, resolution_mode=3, data_bytes=data49)
        print(f"  Send result: {status}")
        if status == "error":
            ok("AUX_RC dataSize=49 rejected (startChannel+channelCount>32 check, matches pre-PR)")
        elif status == "timeout":
            bad("TIMEOUT on AUX_RC dataSize=49 - possible hang/crash regression!")
        else:
            bad(f"AUX_RC dataSize=49 unexpected result: {status}")

        # 4d: AUX_RC dataSize=50 (beyond gate 2..49) -> rejected
        print("\n-- AUX_RC dataSize=50 (beyond gate 2..49) --")
        data50 = bytes([1]) * 49  # 8-bit mode, 49 data bytes -> dataSize = 1 + 49 = 50
        status, frame = send_aux_rc(conn, start_channel=12, resolution_mode=2, data_bytes=data50)
        print(f"  Send result: {status}")
        if status == "error":
            ok("AUX_RC dataSize=50 rejected (dataSize>49 gate, matches pre-PR)")
        elif status == "timeout":
            bad("TIMEOUT on AUX_RC dataSize=50 - possible hang/crash regression!")
        else:
            bad(f"AUX_RC dataSize=50 unexpected result: {status}")

        # 4e: OSD_CHAR_WRITE dataSize=54 (shorter than gate 55) -> rejected
        print("\n-- OSD_CHAR_WRITE dataSize=54 (shorter than >=55 gate) --")
        status, frame = send_osd_char_write(conn, bytes([5]), bytes(range(53)))
        print(f"  Send result: {status}")
        if status == "error":
            ok("OSD_CHAR_WRITE dataSize=54 rejected (matches pre-PR gate)")
        elif status == "timeout":
            bad("TIMEOUT on OSD_CHAR_WRITE dataSize=54 - possible hang/crash regression!")
        else:
            bad(f"OSD_CHAR_WRITE dataSize=54 unexpected result: {status}")

        # 4f: OSD_CHAR_WRITE dataSize=56 (16-bit addr + 54 visible bytes) -> accepted
        print("\n-- OSD_CHAR_WRITE dataSize=56 (16-bit addr + visible char) --")
        status, frame = send_osd_char_write(conn, struct.pack("<H", 5), bytes(range(54)))
        print(f"  Send result: {status}")
        if status == "ok":
            ok("OSD_CHAR_WRITE dataSize=56 accepted (16-bit addr layout)")
        elif status == "timeout":
            bad("TIMEOUT on OSD_CHAR_WRITE dataSize=56 - possible hang/crash regression!")
        else:
            bad(f"OSD_CHAR_WRITE dataSize=56 unexpected result: {status}")

        # 4g: OSD_CHAR_WRITE dataSize=66 (16-bit addr + 64 full char) -> accepted
        print("\n-- OSD_CHAR_WRITE dataSize=66 (16-bit addr + full 64-byte char) --")
        status, frame = send_osd_char_write(conn, struct.pack("<H", 5), bytes(range(64)))
        print(f"  Send result: {status}")
        if status == "ok":
            ok("OSD_CHAR_WRITE dataSize=66 accepted (full-char layout)")
        elif status == "timeout":
            bad("TIMEOUT on OSD_CHAR_WRITE dataSize=66 - possible hang/crash regression!")
        else:
            bad(f"OSD_CHAR_WRITE dataSize=66 unexpected result: {status}")

        # 4h: OSD_CHAR_WRITE dataSize=67 (LONGER than any layout needs: 16-bit addr +
        #     64 full char + 1 trailing byte) -> accepted, trailing ignored
        print("\n-- OSD_CHAR_WRITE dataSize=67 (longer than layout, trailing byte ignored) --")
        status, frame = send_osd_char_write(conn, struct.pack("<H", 5), bytes(range(65)))
        print(f"  Send result: {status}")
        if status == "ok":
            ok("OSD_CHAR_WRITE dataSize=67 accepted (longer message from newer sender, trailing ignored)")
        elif status == "timeout":
            bad("TIMEOUT on OSD_CHAR_WRITE dataSize=67 - possible hang/crash regression!")
        else:
            bad(f"OSD_CHAR_WRITE dataSize=67 unexpected result: {status}")

        # 4i: sbufSwitchToReader reset -- a rejected message must not poison the
        #     next message's overrun state. Send an AUX_RC max-valid frame right
        #     after a rejected one; it must still be accepted.
        print("\n-- overrun state does not leak across messages --")
        status, frame = send_aux_rc(conn, start_channel=12, resolution_mode=2, data_bytes=[1, 2, 3])
        print(f"  Send result (after rejected frames): {status}")
        if status == "ok":
            ok("AUX_RC accepted right after rejected frames (no overrun leak / switch-to-reader reset)")
        elif status == "timeout":
            bad("TIMEOUT - possible hang/crash regression!")
        else:
            bad(f"AUX_RC after rejected frames unexpectedly rejected: {status}")

        # final liveness check
        try:
            frame = conn.request(MSP_API_VERSION, b"", timeout=2.0)
            if frame["direction"] == ">":
                ok("FC still responsive after Phase-4 wire-size tests")
            else:
                bad(f"FC responded with unexpected direction after Phase-4 tests: {frame['direction']!r}")
        except TimeoutError:
            bad("FC NOT RESPONSIVE after Phase-4 tests - possible crash/hang!")

    finally:
        rc_sender.stop()
        conn.close()

    print(f"\n=== SUMMARY: {pass_count} passed, {fail_count} failed ===")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
