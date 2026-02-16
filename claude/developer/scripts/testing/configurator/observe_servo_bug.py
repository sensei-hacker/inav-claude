#!/usr/bin/env python3
"""
Actually observe the servo mixer logic condition bug by reading servo values.
"""
import sys
sys.path.insert(0, '/home/raymorris/Documents/planes/inavflight/mspapi2')

from mspapi2 import MSPApi, InavMSP
import time
import struct

def send_rc(aux2_value):
    """Send RC with specified AUX2 value"""
    with MSPApi(tcp_endpoint="localhost:5760") as api:
        rc_channels = [1500, 1500, 1500, 1000,  # RPYT
                      1500, aux2_value,          # AUX1, AUX2
                      1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]
        rc_data = struct.pack('<' + 'H' * len(rc_channels), *rc_channels)
        api._request(InavMSP.MSP_SET_RAW_RC, rc_data)

def read_servo():
    """Read servo 0 value"""
    with MSPApi(tcp_endpoint="localhost:5760") as api:
        try:
            reply = api._request(InavMSP.MSP_SERVO, b'')
            # mspapi2 returns a dict with servo data
            if isinstance(reply, dict):
                # Check if servo data is in the dict
                if 'servoOutputs' in reply and len(reply['servoOutputs']) > 0:
                    return reply['servoOutputs'][0]
                else:
                    print(f"   DEBUG: Unexpected reply structure: {reply}")
            else:
                print(f"   DEBUG: Unexpected reply type={type(reply)}")
        except Exception as e:
            import traceback
            print(f"   DEBUG: Error reading servo: {e}")
            traceback.print_exc()
    return None

print("Testing servo mixer logic condition bug...")
print("=" * 60)

# Test 1: Set AUX2 LOW (condition FALSE) - servo should be at neutral
print("\n1. Setting AUX2 LOW (1200) - Logic condition FALSE")
send_rc(1200)
time.sleep(0.2)
servo_value = read_servo()
print(f"   Servo 0 value: {servo_value}")

# Test 2: Set AUX2 HIGH (condition TRUE) - servo should activate
print("\n2. Setting AUX2 HIGH (1800) - Logic condition TRUE")
send_rc(1800)
time.sleep(0.2)
servo_value = read_servo()
print(f"   Servo 0 value: {servo_value}")

# Test 3: Set AUX2 LOW again - THIS IS WHERE WE OBSERVE THE BUG
print("\n3. Setting AUX2 LOW (1200) - Logic condition FALSE")
print("   Observing if servo immediately stops or slowly decays...")
send_rc(1200)

# Read servo value multiple times to see if it decays gradually
for i, delay in enumerate([0.0, 0.1, 0.3, 0.6, 1.0, 2.0]):
    time.sleep(delay if i == 0 else delay - sum([0.0, 0.1, 0.3, 0.6, 1.0][:i]))
    servo_value = read_servo()
    print(f"   After {delay:0.1f}s: Servo 0 = {servo_value}")

print("\n" + "=" * 60)
print("BUG ANALYSIS:")
print("- If servo immediately dropped to ~1500: NO BUG (fixed)")
print("- If servo gradually decayed over time: BUG CONFIRMED")
print("=" * 60)
