#!/usr/bin/env python3
"""
Test servo mixer logic condition by varying CH10 input while toggling CH6.
Expected: Servo 0 should follow CH10 only when CH6 > 1700.
"""
import sys
sys.path.insert(0, '/home/raymorris/Documents/planes/inavflight/mspapi2')

from mspapi2 import MSPApi, InavMSP
import time
import struct

def send_rc(ch6_value, ch10_value):
    """Send RC with specified CH6 and CH10 values"""
    with MSPApi(tcp_endpoint="localhost:5760") as api:
        rc_channels = [1500, 1500, 1500, 1000,  # RPYT (0-3)
                      1500, ch6_value,           # AUX1, AUX2/CH6 (4-5)
                      1500, 1500, 1500, ch10_value,  # CH7-CH10 (6-9)
                      1500, 1500, 1500, 1500, 1500, 1500]
        rc_data = struct.pack('<' + 'H' * len(rc_channels), *rc_channels)
        api._request(InavMSP.MSP_SET_RAW_RC, rc_data)

def read_servo():
    """Read servo 0 value"""
    with MSPApi(tcp_endpoint="localhost:5760") as api:
        reply = api._request(InavMSP.MSP_SERVO, b'')
        if isinstance(reply, dict) and 'servoOutputs' in reply:
            return reply['servoOutputs'][0]
    return None

print("Testing servo mixer logic condition with CH10 input...")
print("=" * 70)

# Test 1: CH6 LOW (condition FALSE), vary CH10 - servo should NOT follow
print("\nTest 1: CH6 LOW (1200) - Logic condition FALSE")
print("Varying CH10 - servo should stay at neutral (1500), NOT follow CH10")
for ch10 in [1200, 1500, 1800]:
    send_rc(1200, ch10)
    time.sleep(0.1)
    servo = read_servo()
    print(f"  CH10={ch10} → Servo 0={servo} (expect ~1500)")

# Test 2: CH6 HIGH (condition TRUE), vary CH10 - servo SHOULD follow
print("\nTest 2: CH6 HIGH (1800) - Logic condition TRUE")
print("Varying CH10 - servo SHOULD follow CH10 values")
for ch10 in [1200, 1500, 1800]:
    send_rc(1800, ch10)
    time.sleep(0.1)
    servo = read_servo()
    print(f"  CH10={ch10} → Servo 0={servo} (expect ~{ch10})")

# Test 3: CRITICAL - Set CH10 HIGH with CH6 HIGH, then drop CH6 LOW
print("\nTest 3: CRITICAL BUG TEST")
print("Step 1: Set CH6 HIGH + CH10 HIGH - servo should activate")
send_rc(1800, 1800)
time.sleep(0.2)
servo = read_servo()
print(f"  CH6=1800, CH10=1800 → Servo 0={servo} (expect ~1800)")

print("\nStep 2: Set CH6 LOW - observe if servo immediately stops or decays")
send_rc(1200, 1800)  # CH6 LOW, but CH10 still HIGH

# Read servo multiple times to observe decay
delays = [0.0, 0.1, 0.2, 0.5, 1.0, 2.0]
for i, total_delay in enumerate(delays):
    if i > 0:
        time.sleep(total_delay - delays[i-1])
    servo = read_servo()
    print(f"  After {total_delay:.1f}s: Servo 0={servo}")

print("\n" + "=" * 70)
print("BUG ANALYSIS:")
print("- If servo immediately dropped to ~1500: NO BUG (working correctly)")
print("- If servo gradually decayed from 1800 to 1500: BUG CONFIRMED")
print("=" * 70)
