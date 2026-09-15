#!/usr/bin/env python3
"""
ESC passthrough emulator — replay esc-configurator's MSP handshake and the 4-way
DeviceInitFlash against a flight controller, and hex-dump exactly what comes back.

Purpose: diagnose why esc-configurator (Bluejay tool) fails against INAV:
  (1) confirm the MSP_STATUS response length (INAV returns 11 bytes; esc-configurator's
      Msp.js reads a uint16 at offset 11 -> RangeError), and
  (2) test the SiLabs device-ID fix by issuing the 4-way cmd_DeviceInitFlash and reading
      ACK (0x00 = detected/OK, nonzero = rejected).

Usage:
    python3 esc_emulator.py [PORT [BAUD]]
    # e.g. python3 esc_emulator.py /dev/ttyACM0 115200

Run this OUTSIDE the DSH sandbox (it needs access to the serial device). Requires pyserial.
"""

import sys
import time

try:
    import serial
except ImportError:
    sys.exit("pyserial not installed: pip install pyserial")

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

# ---- MSP framing (esc-configurator's encodeV1: "$M<" + len(1) + cmd(1) + payload + XOR) ----
def msp_v1_frame(command: int, payload: bytes = b"") -> bytes:
    assert 0 <= command <= 0xFF
    body = bytearray()
    body.append(0x24)  # '$'
    body.append(0x4D)  # 'M'
    body.append(0x3C)  # '<'
    body.append(len(payload))
    body.append(command)
    body.extend(payload)
    checksum = body[3] ^ body[4]
    for b in payload:
        checksum ^= b
    body.append(checksum & 0xFF)
    return bytes(body)

# ---- 4-way framing (esc-configurator FourWay.js createMessage) ----
def crc16_xmodem(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc

def fourway_frame(command: int, params: bytes = b"", address: int = 0) -> bytes:
    if len(params) == 0:
        params = b"\x00"
    if len(params) > 256:
        raise ValueError("too many params")
    body = bytearray()
    body.append(0x2F)                    # '/' cmd_Local_Escape
    body.append(command)
    body.append((address >> 8) & 0xFF)
    body.append(address & 0xFF)
    body.append(len(params) if len(params) != 256 else 0)
    body.extend(params)
    crc = crc16_xmodem(bytes(body))
    body.append((crc >> 8) & 0xFF)
    body.append(crc & 0xFF)
    return bytes(body)


def hexdump(label: str, data: bytes):
    print(f"{label} ({len(data)} bytes):")
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hexstr = " ".join(f"{b:02X}" for b in chunk)
        asciistr = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {i:04X}  {hexstr:<47}  {asciistr}")


def read_frame(ser: serial.Serial, timeout_s: float = 2.0) -> bytes:
    """Read one MSP $M> frame (or raw bytes if framing is unexpected)."""
    ser.timeout = timeout_s
    raw = bytearray()
    # Wait for '$'
    start = ser.read(1)
    if not start:
        return b""
    raw.extend(start)
    if start != b"$":
        # Read whatever else is available and return raw
        raw.extend(ser.read(64))
        return bytes(raw)
    header = ser.read(2)  # 'M' and direction
    raw.extend(header)
    if header[:1] != b"M":
        return bytes(raw)
    length = ser.read(1)
    raw.extend(length)
    if not length:
        return bytes(raw)
    n = length[0]
    body = ser.read(n + 1)  # payload + checksum
    raw.extend(body)
    return bytes(raw)


def msp_request(ser, name, command, payload=b""):
    frame = msp_v1_frame(command, payload)
    print(f"\n>>> {name} (cmd {command}) -> {frame.hex(' ')}")
    ser.reset_input_buffer()
    ser.write(frame)
    resp = read_frame(ser)
    if not resp:
        print("<<< (no response)")
        return b""
    hexdump(f"<<< {name} response", resp)
    # Parse $M> len/cmd
    if len(resp) >= 5 and resp[0] == 0x24 and resp[1] == 0x4D:
        rlen, rcmd = resp[3], resp[4]
        print(f"    parsed: cmd={rcmd} payload_len={rlen}")
    return resp


def read_fourway_response(ser: serial.Serial, timeout_s: float = 2.0) -> bytes:
    """Read one 4-way response frame: '.' + cmd(1) + addr(2) + o_len(1) + params + ack(1) + crc(2)."""
    ser.timeout = timeout_s
    raw = bytearray()
    b = ser.read(1)
    if not b:
        return b""
    raw.extend(b)
    if b != b"\x2e":  # '.' cmd_Remote_Escape
        raw.extend(ser.read(64))
        return bytes(raw)
    header = ser.read(4)  # cmd(1) + addr_hi(1) + addr_lo(1) + o_len(1)
    raw.extend(header)
    if len(header) < 4:
        return bytes(raw)
    o_len = header[3]
    rest = ser.read(o_len + 1 + 2)  # params(o_len) + ack(1) + crc(2)
    raw.extend(rest)
    return bytes(raw)


def main():
    print(f"Opening {PORT} @ {BAUD} ...")
    ser = serial.Serial(PORT, BAUD, timeout=2.0)
    time.sleep(0.3)
    ser.reset_input_buffer()

    # 1) MSP handshake — same commands esc-configurator's Msp.js sends
    msp_request(ser, "MSP_API_VERSION", 1)
    msp_request(ser, "MSP_FC_VARIANT", 2)
    msp_request(ser, "MSP_FC_VERSION", 3)
    msp_request(ser, "MSP_STATUS", 101)          # <-- esc-configurator chokes on this (11 bytes vs 16)
    msp_request(ser, "MSP_STATUS_EX", 150)       # INAV's extended variant (16 bytes) for comparison

    # 2) Enter ESC 4-way passthrough (esc-configurator's set4WayIf(): empty payload)
    resp = msp_request(ser, "MSP_SET_PASSTHROUGH", 245)
    # $M> len(1)=1 cmd(1)=245 payload[0]=esc_count checksum
    esc_count = resp[5] if len(resp) >= 6 and resp[0] == 0x24 and resp[3] >= 1 else 0
    print(f"\n=== FC reported ESC count: {esc_count} ===")

    # 3) 4-way: cmd_DeviceInitFlash (0x37) for each ESC -> triggers firmware Connect()
    #    ACK 0x00 = detected/OK, nonzero = rejected (e.g. unknown SiLabs device ID)
    if esc_count:
        for esc in range(min(esc_count, 8)):
            frame = fourway_frame(0x37, params=b"\x00", address=esc)  # cmd_DeviceInitFlash, ESC index
            print(f"\n>>> 4way cmd_DeviceInitFlash ESC[{esc}] -> {frame.hex(' ')}")
            ser.reset_input_buffer()
            ser.write(frame)
            time.sleep(0.1)
            resp = read_fourway_response(ser)
            hexdump(f"<<< 4way response ESC[{esc}]", resp)
            # Response: '.' cmd addr_hi addr_lo o_len(=4) DeviceInfo[4] ack crc_hi crc_lo
            #   DeviceInfo.bytes = [sig_lo, sig_hi, boot_ver_byte, interface_mode]
            if len(resp) >= 10 and resp[0] == 0x2E and resp[4] == 4:
                sig = resp[5] | (resp[6] << 8)
                iface = resp[8]
                iface_name = {0: "none", 1: "SiLabs (BLHeli_S/Bluejay)", 2: "Atmel AVR",
                              3: "SimonK", 4: "ARM (BLHeli32/AM32)"}.get(iface, f"unknown({iface})")
                ack = resp[9]
                verdict = "OK (detected)" if ack == 0x00 else f"ERROR/rejected (ack={ack:#04x})"
                print(f"    ESC[{esc}] signature=0x{sig:04X}  interface={iface_name}  ack={ack:#04x} -> {verdict}")
            elif len(resp) >= 7 and resp[0] == 0x2E:
                ack = resp[5 + resp[4]]  # fallback: skip '.' cmd addr(2) o_len(1) + o_len params
                verdict = "OK (detected)" if ack == 0x00 else f"ERROR/rejected (ack={ack:#04x})"
                print(f"    ESC[{esc}] ack={ack:#04x} -> {verdict}")
            else:
                print("    (could not parse 4-way response)")

    ser.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
