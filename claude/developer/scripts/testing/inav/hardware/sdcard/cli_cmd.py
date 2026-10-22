#!/usr/bin/env python3
"""Run CLI commands on a real FC and ALWAYS exit CLI (exit reboots the FC). Usage: cli_cmd.py 'status' ['get blackbox' ...]"""
import serial, sys, time
s = serial.Serial('/dev/ttyACM0', 115200, timeout=0.2)
s.write(b'#'); time.sleep(0.5); s.read(8192)
try:
    for c in sys.argv[1:]:
        s.write(c.encode() + b'\r\n'); time.sleep(0.8)
        print(s.read(65536).decode('latin1'))
finally:
    s.write(b'exit\r\n'); time.sleep(0.5); s.close()
