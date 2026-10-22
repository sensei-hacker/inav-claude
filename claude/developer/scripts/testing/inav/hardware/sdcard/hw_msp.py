#!/usr/bin/env python3
"""Minimal single-threaded MSP v1/v2 serial client for a real FC (drains mismatched replies, never resends on mismatch).
Note: if the port cannot be opened, it may be a sandbox restriction (ttyACM* is allowlisted; ask the user otherwise),
or the FC may be in CLI/MSC mode, or Configurator may hold the port."""
import serial, struct, time

def crc8(crc, b):
    crc ^= b
    for _ in range(8):
        crc = ((crc << 1) ^ 0xD5) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc

class Msp:
    def __init__(self, port='/dev/ttyACM0', baud=115200):
        self.s = serial.Serial(port, baud, timeout=0.01)
        self.buf = b''
    def close(self): self.s.close()
    def send(self, cmd, payload=b''):
        if cmd > 255 or True:
            hdr = struct.pack('<BHH', 0, cmd, len(payload))
            c = 0
            for b in hdr + payload: c = crc8(c, b)
            pkt = b'$X<' + hdr + payload + bytes([c])
        n = self.s.write(pkt)
        if n != len(pkt): raise IOError('short write')
    def _parse(self):
        while True:
            i = self.buf.find(b'$X>')
            j = self.buf.find(b'$X!')
            if i < 0 and j < 0:
                self.buf = self.buf[-2:]; return None
            k = i if j < 0 or (0 <= i < j) else j
            err = (k == j and j >= 0 and not (0 <= i < j))
            self.buf = self.buf[k:]
            if len(self.buf) < 8: return None
            flag, cmd, ln = struct.unpack_from('<BHH', self.buf, 3)
            if len(self.buf) < 8 + ln + 0: return None
            if len(self.buf) < 9 + ln: return None
            body = self.buf[3:8 + ln]; c = 0
            for b in body: c = crc8(c, b)
            if c != self.buf[8 + ln]:
                self.buf = self.buf[1:]; continue
            pl = self.buf[8:8 + ln]; self.buf = self.buf[9 + ln:]
            return cmd, pl, err
    def request(self, cmd, payload=b'', timeout=1.0, retries=2):
        for _ in range(retries + 1):
            self.send(cmd, payload)
            end = time.time() + timeout
            while time.time() < end:
                d = self.s.read(4096)
                if d: self.buf += d
                while True:
                    r = self._parse()
                    if r is None: break
                    if r[0] == cmd:
                        if r[2]: return None
                        return r[1]
        return None
    def pump(self, ms=0):
        d = self.s.read(4096)
        if d: self.buf += d
        while self._parse(): pass
